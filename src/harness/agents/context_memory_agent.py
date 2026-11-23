import json

from harness.agents.base_agent import BaseAgent
from harness.domain.agent import Agent
from harness.domain.message import Message
from harness.domain.tool_result import ToolResult
from harness.models.context_memory_summary import ContextMemorySummary
from harness.models.model_client import ModelClient
from harness.models.tool_definition import ToolDefinition
from harness.service.tool_service import ToolService
from harness.skills.skill_registry import SkillRegistry
from harness.validators.model_response_validator import ModelResponseValidator


class ContextMemoryAgent(BaseAgent):
    def __init__(
        self,
        agent: Agent,
        model_client: ModelClient,
        tool_service: ToolService,
        tool_definitions: list[ToolDefinition],
        skill_registry: SkillRegistry,
        global_instructions: str,
        agent_id: str | None = None
    ) -> None:
        super().__init__(agent, model_client, tool_service, tool_definitions, skill_registry, agent_id)
        self._global_instructions = global_instructions

    def create_summary(self, session_id: str, conversation_history: list[Message]) -> ContextMemorySummary:
        if not session_id.strip():
            raise ValueError("Session ID is required.")

        if not conversation_history:
            return ContextMemorySummary.empty(session_id)

        payload = {
            "operation": "create_summary",
            "session_id": session_id,
            "conversation_history": self._serialize_messages(conversation_history)
        }
        tool_result_ids = self._get_message_tool_result_ids(conversation_history)

        return self._generate_summary(payload, session_id, 1, allowed_tool_result_ids=tool_result_ids)

    def update_summary(
        self,
        previous_summary: ContextMemorySummary,
        new_messages: list[Message],
        new_tool_results: list[ToolResult] | None = None
    ) -> ContextMemorySummary:
        new_tool_results = new_tool_results or []
        if not new_messages and not new_tool_results:
            return previous_summary

        payload = {
            "operation": "update_summary",
            "previous_summary": previous_summary.to_dict(),
            "new_messages": self._serialize_messages(new_messages),
            "new_tool_results": [self._serialize_tool_result(result) for result in new_tool_results]
        }
        previous_ids = {
            finding.tool_execution_id
            for finding in previous_summary.important_tool_findings
            if finding.tool_execution_id is not None
        }
        message_ids = self._get_message_tool_result_ids(new_messages)
        allowed_ids = previous_ids | message_ids | {result.id for result in new_tool_results}
        allowed_agent_ids = {
            finding.agent_id
            for finding in previous_summary.important_tool_findings
            if finding.agent_id is not None
        }

        return self._generate_summary(
            payload,
            previous_summary.session_id,
            previous_summary.version + 1,
            summary_id=previous_summary.summary_id,
            allowed_tool_result_ids=allowed_ids,
            allowed_agent_ids=allowed_agent_ids
        )

    def _generate_summary(
        self,
        payload: dict,
        session_id: str,
        version: int,
        summary_id: str | None = None,
        allowed_tool_result_ids: set[str] | None = None,
        allowed_agent_ids: set[str] | None = None
    ) -> ContextMemorySummary:
        system_content = f"{self._global_instructions}\n\n{self._agent.instructions}"
        messages = [
            Message(role="system", type="system_instruction", content=system_content),
            Message(role="user", type="user_message", content=json.dumps(payload))
        ]
        response = self._model_client.generate(messages, tools=[])

        if response.tool_calls:
            raise ValueError("Context memory summarization must not call tools.")

        try:
            data = json.loads(
                response.text,
                object_pairs_hook=ModelResponseValidator.validate_json_object_pairs,
                parse_constant=ModelResponseValidator.validate_json_constant
            )
        except json.JSONDecodeError as error:
            raise ValueError("Context memory agent returned invalid JSON.") from error

        ModelResponseValidator.validate_finite_numbers_data(data)
        summary = ContextMemorySummary.from_model_data(data, session_id, version, summary_id)
        allowed_tool_result_ids = allowed_tool_result_ids or set()
        referenced_ids = {
            finding.tool_execution_id
            for finding in summary.important_tool_findings
            if finding.tool_execution_id is not None
        }
        unknown_ids = referenced_ids - allowed_tool_result_ids

        if unknown_ids:
            raise ValueError("Context memory response references unknown tool execution IDs.")

        allowed_agent_ids = allowed_agent_ids or set()
        agent_ids = {finding.agent_id for finding in summary.important_tool_findings if finding.agent_id is not None}
        if agent_ids - allowed_agent_ids:
            raise ValueError("Context memory response references unknown agent IDs.")

        return summary

    @staticmethod
    def _serialize_messages(messages: list[Message]) -> list[dict]:
        return [
            {
                "role": message.role,
                "type": message.type,
                "content": message.content,
                "tool_results": [ContextMemoryAgent._serialize_tool_result(result) for result in message.tool_results]
            }
            for message in messages
        ]

    @staticmethod
    def _serialize_tool_result(result: ToolResult) -> dict:
        return {
            "id": result.id,
            "name": result.name,
            "output": result.output,
            "success": result.success
        }

    @staticmethod
    def _get_message_tool_result_ids(messages: list[Message]) -> set[str]:
        return {result.id for message in messages for result in message.tool_results}
