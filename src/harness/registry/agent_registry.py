from harness.agents.base_agent import BaseAgent
from harness.domain.agent import Agent
from harness.factory.agents_factory import AgentFactory
from harness.models.model_client import ModelClient
from harness.models.tool_definition import ToolDefinition
from harness.service.tool_service import ToolService
from harness.skills.skill_registry import SkillRegistry


class AgentRegistry:
    def __init__(
        self,
        model_client: ModelClient | None = None,
        tool_service: ToolService | None = None,
        tool_definitions: list[ToolDefinition] | None = None,
        skill_registry: SkillRegistry | None = None,
        agent_definitions: list[Agent] | None = None
    ) -> None:
        self._agents: dict[str, BaseAgent] = {}

        if model_client is None:
            return

        if tool_service is None or skill_registry is None:
            raise ValueError("Legacy registry initialization requires all agent dependencies.")

        factory = AgentFactory(model_client, tool_service, tool_definitions or [], skill_registry)
        agents = [factory.create_planner(), factory.create_context_memory()]
        agents.extend(factory.create(definition) for definition in agent_definitions or [])

        names: set[str] = set()
        for agent in agents:
            if agent.name in names:
                raise ValueError(f"Agent already registered: {agent.name}")

            names.add(agent.name)
            self.register(agent)

    def register(self, agent: BaseAgent) -> None:
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent already registered: {agent.agent_id}")

        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> BaseAgent:
        agent = self._agents.get(agent_id)

        if agent is not None:
            return agent

        matches = self.get_by_type(agent_id)
        if len(matches) == 1:
            return matches[0]

        raise ValueError(f"Unknown agent: {agent_id}")

    def get_by_type(self, agent_type: str) -> list[BaseAgent]:
        return [agent for agent in self._agents.values() if agent.agent_type == agent_type]

    def list_agents(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def unregister(self, agent_id: str) -> None:
        if agent_id not in self._agents:
            raise ValueError(f"Unknown agent: {agent_id}")

        del self._agents[agent_id]
