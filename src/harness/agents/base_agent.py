from harness.domain.agent import Agent
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.model_client import ModelClient
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.service.tool_service import ToolService
from harness.skills.skill_registry import SkillRegistry


class BaseAgent:
    def __init__(
        self,
        agent: Agent,
        model_client: ModelClient,
        tool_service: ToolService,
        tool_definitions: list[ToolDefinition],
        skill_registry: SkillRegistry
    ) -> None:
        self._agent = agent
        self._model_client = model_client
        self._tool_service = tool_service
        self._tool_definitions = tool_definitions
        self._skill_registry = skill_registry

    @property
    def name(self) -> str:
        return self._agent.name

    @property
    def description(self) -> str:
        return self._agent.description

    def observe(self, messages: list[Message]) -> list[Message]:
        return messages

    def think(self, messages: list[Message], available_tools: list[ToolDefinition]) -> ModelResponse:
        return self._model_client.generate(messages, tools=available_tools)

    @staticmethod
    def decide(response: ModelResponse) -> list[ToolCall]:
        return response.tool_calls

    def action(
        self,
        messages: list[Message],
        tool_calls: list[ToolCall],
        available_tools: list[ToolDefinition]
    ) -> None:
        tool_results = self._tool_service.execute_tool_calls(tool_calls, available_tools)
        tool_call_message, tool_result_message = self._tool_service.prepare_tool_response_messages(
            tool_calls,
            tool_results
        )

        messages.extend([tool_call_message, tool_result_message])

    def plan(self, task: str | None) -> Message:
        return self.loop(task)

    def loop(self, task: str | None) -> Message:
        if task is None:
            return Message(role="assistant", type="error", content="Task is required.")

        if not task.strip():
            return Message(role="assistant", type="error", content="Task cannot be empty.")

        instructions = self._agent.instructions
        skill_instructions = self._skill_registry.get_instructions(self._agent.allowed_skills)

        if skill_instructions:
            instructions = f"{instructions}\n\n{skill_instructions}"

        system_message = Message(role="system", type="system_instruction", content=instructions)
        user_message = Message(role="user", type="user_message", content=task)
        messages = [system_message, user_message]
        available_tools = self._tool_service.get_available_tools_by_names(self._tool_definitions, self._agent.allowed_tools)

        for _ in range(self._agent.max_steps):
            messages = self.observe(messages)
            response = self.think(messages, available_tools)
            tool_calls = self.decide(response)

            if not tool_calls:
                return Message(role="assistant", type="assistant_message", content=response.text)

            self.action(messages, tool_calls, available_tools)

        content = f"Agent {self._agent.name!r} reached its maximum number of steps."

        return Message(role="assistant", type="error", content=content)
