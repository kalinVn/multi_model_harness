from pathlib import Path
from typing import Iterable

from markdown_it import MarkdownIt

from harness.domain.dependency_graph import DependencyGraph, DependencyGraphNode, UnresolvedDependency


class DependencyGraphBuilder:
    """Build a deterministic graph of file references found in Markdown inline code."""

    def __init__(self, project_root: Path, supported_extensions: Iterable[str] = (".md", ".txt")) -> None:
        self._project_root = project_root.resolve()
        self._supported_extensions = self._normalize_extensions(supported_extensions)
        self._markdown = MarkdownIt("commonmark")

    def build(self, initial_paths: str | Path | Iterable[str | Path]) -> DependencyGraph:
        nodes: dict[str, DependencyGraphNode] = {}
        files: list[str] = []
        cycles: list[list[str]] = []
        unresolved: list[UnresolvedDependency] = []
        states: dict[str, str] = {}
        stack: list[str] = []
        contents: dict[str, str] = {}
        roots = self._normalize_roots(initial_paths, contents)

        for root in roots:
            self._visit(root, nodes, files, cycles, unresolved, states, stack, contents)

        return DependencyGraph(roots=roots, nodes=nodes, files=files, cycles=cycles, unresolved=unresolved)

    def _visit(
        self,
        relative_path: str,
        nodes: dict[str, DependencyGraphNode],
        files: list[str],
        cycles: list[list[str]],
        unresolved: list[UnresolvedDependency],
        states: dict[str, str],
        stack: list[str],
        contents: dict[str, str]
    ) -> None:
        state = states.get(relative_path)
        if state == "visited":
            return
        if state == "visiting":
            cycle = stack[stack.index(relative_path):] + [relative_path]
            if cycle not in cycles:
                cycles.append(cycle)
            return

        states[relative_path] = "visiting"
        stack.append(relative_path)
        nodes[relative_path] = DependencyGraphNode()
        files.append(relative_path)
        content = contents[relative_path]
        dependencies = nodes[relative_path].dependencies

        for reference, line, column in self._extract_references(content):
            candidate, reason = self._resolve_reference(relative_path, reference, contents)
            if candidate is None:
                if reason:
                    unresolved.append(UnresolvedDependency(
                        source=relative_path,
                        reference=reference,
                        line=line,
                        column=column,
                        reason=reason
                    ))
                continue
            if candidate not in dependencies:
                dependencies.append(candidate)
            self._visit(candidate, nodes, files, cycles, unresolved, states, stack, contents)

        stack.pop()
        states[relative_path] = "visited"

    def _normalize_roots(self, initial_paths: str | Path | Iterable[str | Path], contents: dict[str, str]) -> list[str]:
        values = [initial_paths] if isinstance(initial_paths, (str, Path)) else list(initial_paths)
        if not values:
            raise ValueError("At least one initial file path is required.")

        roots = []
        for value in values:
            root = self._resolve_initial_path(value, contents)
            if root not in roots:
                roots.append(root)
        return roots

    def _resolve_initial_path(self, value: str | Path, contents: dict[str, str]) -> str:
        path = Path(str(value).replace("\\", "/"))
        if path.is_absolute():
            raise ValueError(f"Initial path must be repository-root-relative: {value}")
        if ".." in path.parts:
            raise ValueError(f"Initial path cannot escape the repository root: {value}")

        candidate = (self._project_root / path).resolve()
        self._require_inside_root(candidate, str(value))
        if not candidate.is_file():
            raise FileNotFoundError(f"Initial file does not exist or is not a regular file: {value}")

        relative_path = candidate.relative_to(self._project_root).as_posix()
        if relative_path in contents:
            return relative_path
        try:
            contents[relative_path] = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"Initial file is unreadable: {relative_path}: {error}") from error
        return relative_path

    def _extract_references(self, content: str) -> list[tuple[str, int, int]]:
        references = []
        lines = content.splitlines()

        for token in self._markdown.parse(content):
            if token.type != "inline" or token.map is None:
                continue
            search_line = token.map[0]
            search_start = 0
            for child in token.children or []:
                if child.type != "code_inline":
                    continue
                line, column = self._find_source_location(lines, child.content, search_line, search_start, token.map[1])
                search_line = line - 1
                search_start = column - 1 + len(child.content)
                references.append((child.content.strip(), line, column))
        return references

    @staticmethod
    def _find_source_location(lines: list[str], content: str, start_line: int, start_column: int, end_line: int) -> tuple[int, int]:
        for line_index in range(start_line, min(end_line, len(lines))):
            column_index = lines[line_index].find(content, start_column if line_index == start_line else 0)
            if column_index >= 0:
                return line_index + 1, column_index + 1
        return start_line + 1, 1

    def _resolve_reference(self, source: str, reference: str, contents: dict[str, str]) -> tuple[str | None, str | None]:
        if self._is_runtime_placeholder(reference):
            return None, "runtime placeholder"

        path_text = reference.split("#", 1)[0].replace("\\", "/")
        path = Path(path_text)
        if path.suffix.lower() not in self._supported_extensions:
            return None, None
        if path.is_absolute():
            return None, "absolute paths are not allowed"

        candidates = [self._project_root / path]
        if path.parts and path.parts[0] in {".", ".."}:
            candidates = [self._project_root / Path(source).parent / path]
        elif len(path.parts) == 1:
            candidates.append(self._project_root / Path(source).parent / path)

        escaped = False
        for candidate in candidates:
            resolved = candidate.resolve()
            if not resolved.is_relative_to(self._project_root):
                escaped = True
                continue
            if resolved.is_file():
                relative_path = resolved.relative_to(self._project_root).as_posix()
                if relative_path not in contents:
                    try:
                        contents[relative_path] = resolved.read_text(encoding="utf-8")
                    except (OSError, UnicodeError):
                        return None, "referenced file is unreadable"
                return relative_path, None

        if escaped:
            return None, "path escapes the repository root"
        return None, "referenced file does not exist"

    def _require_inside_root(self, path: Path, original: str) -> None:
        if not path.is_relative_to(self._project_root):
            raise ValueError(f"Path escapes the repository root: {original}")

    @staticmethod
    def _normalize_extensions(extensions: Iterable[str]) -> frozenset[str]:
        normalized = frozenset(extension.lower() if extension.startswith(".") else f".{extension.lower()}" for extension in extensions)
        if not normalized:
            raise ValueError("At least one supported file extension is required.")
        return normalized

    @staticmethod
    def _is_runtime_placeholder(reference: str) -> bool:
        return "<" in reference and ">" in reference or "_path=" in reference
