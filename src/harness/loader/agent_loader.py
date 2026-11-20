from pathlib import Path

from harness.domain.agent import Agent
from harness.domain.message import Message
from harness.loader.markdown_loader import MarkdownLoader
from harness.validators.agent_validator import AgentValidator


class AgentLoader:
    def load(self, agent_path: Path) -> Agent | Message:
        sections = MarkdownLoader.load(agent_path)
        name = sections.get("Name", "").strip()
        description = sections.get("Description", "").strip()
        instructions = sections.get("Instructions", "").strip()
        error_message = AgentValidator.validate(name, description, instructions)

        if error_message is not None:
            return error_message

        allowed_tools = self._parse_tools(sections.get("Tools", ""))
        allowed_skills = self._parse_skills(sections.get("Skills", ""))
        max_steps = self._parse_max_steps(sections.get("Max Steps", "10"))

        return Agent(
            name=name,
            description=description,
            instructions=instructions,
            allowed_tools=allowed_tools,
            allowed_skills=allowed_skills,
            max_steps=max_steps
        )

    @staticmethod
    def _parse_tools(content: str) -> tuple[str, ...]:
        tools = tuple(
            line.strip().removeprefix("-").strip()
            for line in content.splitlines()
            if line.strip()
        )

        if any(not tool for tool in tools):
            raise ValueError("Agent contains an empty tool name.")

        if len(tools) != len(set(tools)):
            raise ValueError("Agent contains duplicate tools.")

        return tools

    @staticmethod
    def _parse_skills(content: str) -> tuple[str, ...]:
        skills = tuple(
            line.strip().removeprefix("-").strip()
            for line in content.splitlines()
            if line.strip()
        )

        if any(not skill for skill in skills):
            raise ValueError("Agent contains an empty skill name.")

        if len(skills) != len(set(skills)):
            raise ValueError("Agent contains duplicate skills.")

        return skills

    @staticmethod
    def _parse_max_steps(content: str) -> int:
        try:
            max_steps = int(content.strip())
        except ValueError as error:
            raise ValueError("Agent Max Steps must be an integer.") from error

        if max_steps < 1:
            raise ValueError("Agent Max Steps must be greater than zero.")

        return max_steps
