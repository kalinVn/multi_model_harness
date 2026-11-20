from harness.domain.command import Command
from harness.loader.markdown_loader import MarkdownLoader


class CommandLoader:
    def get_command_object(self, file_command_content: str) -> Command:
        file_command_sections = MarkdownLoader.parse(file_command_content)

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
