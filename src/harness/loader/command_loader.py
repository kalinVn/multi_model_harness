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

        # Извличаме всички секции с изключение на "Name" и "Description".
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
        """TODO: Добавяне на поддръжка за вложени Markdown секции.

        В момента само "# " създава нова секция.
        Заглавия като "## " и "### " се третират като обикновено съдържание.
        В бъдеще да се поддържат йерархични секции според нивата на заглавията,
        като се запазват връзките родител–дете.
        """
        return self._parse_sections(content)

    def _parse_sections(
        self,
        content: str,
    ) -> dict[str, str]:
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        # Разделяме текста на отделни редове чрез splitlines().
        # Пример:
        # content = "ябълка\nбанан"
        # content.splitlines() -> ["ябълка", "банан"]
        file_lines = content.splitlines()

        # Премахваме празните низове и низовете само с интервали от списъка. Например
        # ["ябълка", "", "банан", "  "] става ["ябълка", "банан"].
        file_lines = [line for line in file_lines if line.strip()]

        for line in file_lines:
            # Ред, започващ с "# ", например "# name", започва нова
            # секция с име "name".
            if line.startswith("# "):
                current_section = line[2:].strip()
                sections[current_section] = []
                continue

            # Ако редът не започва с "# ", го добавяме към текущата
            # секция. Например, ако current_section = "name":
            # sections['name'].append('test-write-file')
            if current_section is not None:
                sections[current_section].append(line)

        return {
            section_name: "\n".join(lines).strip()
            for section_name, lines in sections.items()
        }
