from harness.domain.skill import Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill already registered: {skill.name}")

        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        skill = self._skills.get(name)

        if skill is None:
            raise ValueError(f"Unknown skill: {name}")

        return skill

    def get_instructions(self, names: tuple[str, ...]) -> str:
        instructions = [self.get(name).instructions for name in names]

        return "\n\n".join(instructions)

    def list_skills(self) -> list[Skill]:
        return list(self._skills.values())
