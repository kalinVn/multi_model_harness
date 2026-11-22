from uuid import uuid4

from harness.agents.base_agent import BaseAgent
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
        skill_registry: SkillRegistry
    ) -> None:
        self._model_client = model_client
        self._tool_service = tool_service
        self._tool_definitions = tool_definitions
        self._skill_registry = skill_registry

    def create(self, agent: Agent) -> BaseAgent:
        return BaseAgent(
            agent,
            self._model_client,
            self._tool_service,
            self._tool_definitions,
            self._skill_registry,
            agent_id=str(uuid4())
        )

    def create_planner(self) -> BaseAgent:
        planner = Agent(
            name="planner",
            description="Create an execution plan for a specific task.",
            instructions=planner_instructions.INSTRUCTIONS,
            allowed_tools=("list_directory", "read_file", "write_file"),
            max_steps=5
        )

        return self.create(planner)

    def create_context_memory(self) -> BaseAgent:
        context_memory = Agent(
            name="context-memory",
            description="Summarize the important context for a specific task.",
            instructions=context_memory_instructions.INSTRUCTIONS,
            max_steps=1
        )

        return self.create(context_memory)
