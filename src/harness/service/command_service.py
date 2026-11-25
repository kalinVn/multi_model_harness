import json
import re
from pathlib import Path

from harness.domain.message import Message
from harness.loader.command_context_loader import get_command_message_obj
from harness.loader.command_loader import CommandLoader
from harness.parser.command_parser import ParsedCommand
from harness.resolver.command_resolver import CommandResolver
from harness.tools.tool_registry import ToolRegistry


class CommandService:
    """Prepare command-specific messages."""

    def __init__(
        self,
        command_resolver: CommandResolver,
        command_loader: CommandLoader,
        tool_registry: ToolRegistry,
    ) -> None:
        self._command_resolver = command_resolver
        self._command_loader = command_loader
        self._tool_registry = tool_registry

    def prepare_command_context(
        self,
        parsed_command: ParsedCommand,
    ) -> Message:
        """Build the model context for a parsed command."""
        return get_command_message_obj(
            parsed_command.name,
            command_resolver=self._command_resolver,
            tool_registry=self._tool_registry,
            command_loader=self._command_loader,
        )

    def get_dependency_roots(self, parsed_command: ParsedCommand, project_root: Path) -> list[str]:
        """Return the command file and validated concrete file inputs."""

        command_path = self._command_resolver.resolve(parsed_command.name)
        output = json.loads(self._tool_registry.execute("read_file", {"paths": [str(command_path)]}))
        result = output["results"][0]
        if not result["success"]:
            raise RuntimeError(result["error"])

        command = self._command_loader.get_command_object(result["content"])
        arguments = self._parse_named_arguments(parsed_command.arguments)
        required_paths = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*_path)=<[^>]+>", command.sections.get("Invocation", ""))
        roots = [self._normalize_file_path(command_path, project_root, "command file")]

        for name in required_paths:
            if name not in arguments:
                raise ValueError(f"Required command input is missing: {name}")

        for name, value in arguments.items():
            if not name.endswith("_path"):
                continue
            roots.append(self._validate_file_input(name, value, project_root))

        return list(dict.fromkeys(roots))

    @staticmethod
    def _parse_named_arguments(arguments: list[str]) -> dict[str, str]:
        named_arguments = {}
        for argument in arguments:
            if "=" not in argument:
                continue
            name, value = argument.split("=", 1)
            if name in named_arguments:
                raise ValueError(f"Duplicate command input: {name}")
            named_arguments[name] = value
        return named_arguments

    @staticmethod
    def _validate_file_input(name: str, value: str, project_root: Path) -> str:
        if not value or "<" in value or ">" in value:
            raise ValueError(f"Command input must be a concrete repository-relative file: {name}")

        path = Path(value.replace("\\", "/"))
        if path.is_absolute():
            raise ValueError(f"Command input must be repository-root-relative: {name}")

        resolved_root = project_root.resolve()
        resolved = (resolved_root / path).resolve()
        if not resolved.is_relative_to(resolved_root):
            raise ValueError(f"Command input escapes the repository root: {name}")
        if not resolved.is_file():
            raise FileNotFoundError(f"Command input file does not exist: {name}={value}")
        try:
            resolved.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"Command input file is unreadable: {name}={value}: {error}") from error
        return resolved.relative_to(resolved_root).as_posix()

    @staticmethod
    def _normalize_file_path(path: Path, project_root: Path, label: str) -> str:
        resolved_root = project_root.resolve()
        resolved = path.resolve()
        if not resolved.is_relative_to(resolved_root):
            raise ValueError(f"{label.capitalize()} escapes the repository root: {path}")
        return resolved.relative_to(resolved_root).as_posix()
