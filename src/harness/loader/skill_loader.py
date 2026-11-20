from pathlib import Path

from harness.domain.skill import Skill
from harness.loader.markdown_loader import MarkdownLoader


class SkillLoader:
    def load_directory(self, skills_directory: Path) -> list[Skill]:
        if not skills_directory.is_dir():
            return []

        return [self.load(skill_path) for skill_path in sorted(skills_directory.glob("*.md"))]

    def load(self, skill_path: Path) -> Skill:
        sections = MarkdownLoader.load(skill_path)
        name = sections.get("Name", "").strip()
        description = sections.get("Description", "").strip()
        instructions = sections.get("Instructions", "").strip()

        if not name:
            raise ValueError("Skill must contain a '# Name' section.")

        if not description:
            raise ValueError("Skill must contain a '# Description' section.")

        if not instructions:
            raise ValueError("Skill must contain an '# Instructions' section.")

        return Skill(name=name, description=description, instructions=instructions)
