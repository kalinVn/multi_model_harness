from pathlib import Path

from markdown_it import MarkdownIt


class MarkdownLoader:
    @staticmethod
    def load(markdown_path: Path) -> dict[str, str]:
        content = markdown_path.read_text(encoding="utf-8")

        return MarkdownLoader.parse(content)

    @staticmethod
    def parse(content: str) -> dict[str, str]:
        lines = content.splitlines(keepends=True)
        tokens = MarkdownIt("commonmark").parse(content)
        headings = []

        for index, token in enumerate(tokens):
            if token.type != "heading_open" or token.tag != "h1" or token.level != 0 or token.map is None:
                continue

            name = tokens[index + 1].content.strip()

            if not name:
                raise ValueError("Empty Markdown section name.")

            if any(heading_name == name for heading_name, _, _ in headings):
                raise ValueError(f"Duplicate Markdown section: {name}")

            headings.append((name, token.map[0], token.map[1]))

        sections = {}

        for index, (name, _, content_start) in enumerate(headings):
            content_end = headings[index + 1][1] if index + 1 < len(headings) else len(lines)
            section_lines = lines[content_start:content_end]

            while section_lines and not section_lines[0].strip():
                section_lines.pop(0)

            while section_lines and not section_lines[-1].strip():
                section_lines.pop()

            sections[name] = "".join(section_lines).rstrip("\r\n")

        return sections
