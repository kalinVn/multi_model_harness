# src/harness/loader/command_loader.py

from harness.domain.command import Command


class CommandLoader:

    def get_command_object(self, file_command_content: str) -> Command:
        file_command_sections = self._parse_file_command_content(file_command_content)

        name = file_command_sections.get("Name")
        description = file_command_sections.get("Description")

        if not name:
            raise ValueError("Command must contain a '# Name' section.")

        if not description:
            raise ValueError("Command must contain a '# Description' section.")

        # Extract all sections except "Name" and "Description".
        extra_sections = {
            key: value
            for key, value in file_command_sections.items()
            if key not in {"Name", "Description"}
        }

        return Command(name=name, description=description, sections=extra_sections)

    def _parse_file_command_content(
        self,
        content: str,
    ) -> dict[str, str]:
        """TODO: Add support for nested Markdown sections.

        Currently, only "# " creates a new section.
        Headings like "## " and "### " are treated as plain content.
        In the future, support hierarchical sections based on heading levels,
        while preserving the parent-child relationships.
        """
        return self._parse_sections(content)

    def _parse_sections(
        self,
        content: str,
    ) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        # Split the text into individual lines with splitlines().
        # Example:
        # content = "apple\nbanana"
        # content.splitlines() -> ["apple", "banana"]
        file_lines = content.splitlines()

        # Remove empty or whitespace-only strings from the list. For example,
        # ["apple", "", "banana", "  "] becomes ["apple", "banana"].
        file_lines = [line for line in file_lines if line.strip()]

        for line in file_lines:
            # A line beginning with "# ", such as "# name", starts a new
            # section named "name".
            if line.startswith("# "):
                current_section = line[2:].strip()
                sections[current_section] = []
                continue

            # If a line does not begin with "# ", append it to the current
            # section. For example, if current_section = "name":
            # sections['name'].append('test-write-file')
            if current_section is not None:
                sections[current_section].append(line)

        return {
            section_name: "\n".join(lines).strip()
            for section_name, lines in sections.items()
        }
