from pathlib import Path
from uuid import uuid4

from harness.agents.base_agent import BaseAgent
from harness.agents.context_memory_agent import ContextMemoryAgent
from harness.agents.planner_agent import PlannerAgent
from harness.config.agents import context_memory_instructions, planner_instructions
from harness.domain.agent import Agent
from harness.models.model_client import ModelClient
from harness.models.tool_definition import ToolDefinition
from harness.service.tool_service import ToolService
from harness.skills.skill_registry import SkillRegistry


class AgentFactory:
    def __init__(
        self,
        model_client: ModelClient,
        tool_service: ToolService,
        tool_definitions: list[ToolDefinition],
        skill_registry: SkillRegistry,
        project_root: Path | None = None
    ) -> None:
        self._model_client = model_client
        self._tool_service = tool_service
        self._tool_definitions = tool_definitions
        self._skill_registry = skill_registry
        self._project_root = project_root or Path.cwd()

    def create(self, agent: Agent) -> BaseAgent:
        return BaseAgent(
            agent,
            self._model_client,
            self._tool_service,
            self._tool_definitions,
            self._skill_registry,
            agent_id=str(uuid4())
        )

    def create_planner(self) -> PlannerAgent:
        planner = Agent(
            name="planner",
            description="Create an execution plan for a specific task.",
            instructions=planner_instructions.INSTRUCTIONS,
            allowed_tools=("list_directory", "read_file", "write_file"),
            max_steps=5
        )

        return PlannerAgent(
            planner,
            self._model_client,
            self._tool_service,
            self._tool_definitions,
            self._skill_registry,
            agent_id=str(uuid4())
        )

    def create_context_memory(self) -> ContextMemoryAgent:
        context_memory = Agent(
            name="context_memory",
            description="Create and incrementally update structured conversation memory.",
            instructions=context_memory_instructions.INSTRUCTIONS,
            max_steps=1
        )

        global_instructions_path = self._project_root / ".caisa" / "CAISA.md"
        global_instructions = global_instructions_path.read_text(encoding="utf-8")

        return ContextMemoryAgent(
            context_memory,
            self._model_client,
            self._tool_service,
            self._tool_definitions,
            self._skill_registry,
            agent_id=str(uuid4()),
            global_instructions=global_instructions
        )
