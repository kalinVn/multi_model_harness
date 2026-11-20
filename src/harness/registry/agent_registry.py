from harness.agents.base_agent import BaseAgent
from harness.config.agents import context_memory_instructions, planner_instructions
from harness.domain.agent import Agent
from harness.models.model_client import ModelClient
from harness.models.tool_definition import ToolDefinition
from harness.service.tool_service import ToolService
from harness.skills.skill_registry import SkillRegistry


class AgentRegistry:
    def __init__(
        self,
        model_client: ModelClient,
        tool_service: ToolService,
        tool_definitions: list[ToolDefinition],
        skill_registry: SkillRegistry
    ) -> None:
        self._agents: dict[str, BaseAgent] = {}
        planner = Agent(
            name="planner",
            description="Create an execution plan for a specific task.",
            instructions=planner_instructions.INSTRUCTIONS,
            allowed_tools=("list_directory", "read_file", "write_file"),
            max_steps=5
        )
        context_memory = Agent(
            name="context-memory",
            description="Summarize the important context for a specific task.",
            instructions=context_memory_instructions.INSTRUCTIONS,
            max_steps=1
        )
        planner_agent = BaseAgent(planner, model_client, tool_service, tool_definitions, skill_registry)
        context_memory_agent = BaseAgent(context_memory, model_client, tool_service, tool_definitions, skill_registry)

        self.register(planner_agent)
        self.register(context_memory_agent)

    def register(self, agent: BaseAgent) -> None:
        if agent.name in self._agents:
            raise ValueError(f"Agent already registered: {agent.name}")

        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        agent = self._agents.get(name)

        if agent is None:
            raise ValueError(f"Unknown agent: {name}")

        return agent

    def list_agents(self) -> list[BaseAgent]:
        return list(self._agents.values())
