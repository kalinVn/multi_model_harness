from collections.abc import Callable

from harness.builder.model_message_builder import ModelMessageBuilder
from harness.builder.tool_call_context_builder import build_tool_calls_context
from harness.builder.tool_result_context_builder import build_tool_results_context
from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.models.response import ModelResponse
from harness.tools.tool_registry import ToolRegistry


class ToolService:
    """Provide tool execution and tool-message preparation operations."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
        model_message_builder: ModelMessageBuilder,
        on_tool_result: Callable[[ToolResult], None] | None = None,
    ) -> None:
        self._tool_registry = tool_registry
        self._model_message_builder = model_message_builder
        self._on_tool_result = on_tool_result

    def execute_tool_calls(
        self,
        tool_calls: list[ToolCall],
    ) -> list[ToolResult]:
        """Execute tool calls and return their results in the same order."""
        tool_results: list[ToolResult] = []

        for tool_call in tool_calls:
            try:
                output = self._tool_registry.execute(
                    tool_call.name,
                    tool_call.arguments,
                )
                tool_result = ToolResult(name=tool_call.name, output=output)
            except Exception as error:
                tool_result = ToolResult(
                    name=tool_call.name,
                    output=str(error),
                    success=False,
                )

            tool_results.append(tool_result)
            if self._on_tool_result is not None:
                self._on_tool_result(tool_result)

        return tool_results

    def get_requested_tool_result_ids(
        self,
        session: Session,
        response: ModelResponse,
    ) -> list[str]:
        """Return requested tool-result IDs that exist in the session."""
        requested_tool_result_ids: list[str] = []

        for result_id in response.tool_result_output_requests:
            tool_result = session.get_tool_result_by_id(result_id)
            if tool_result is not None:
                requested_tool_result_ids.append(tool_result.id)

        return requested_tool_result_ids

    def update_model_messages_by_requested_tool_result_ids(
        self,
        model_messages: list[Message],
        requested_tool_result_ids: list[str],
    ) -> list[Message]:
        """Expose full output for explicitly requested tool results."""
        if not requested_tool_result_ids:
            return model_messages

        return (
            self._model_message_builder
            .update_model_messages_by_tool_result_output_requests_ids(
                model_messages=model_messages,
                tool_result_output_requests=requested_tool_result_ids,
            )
        )

    def prepare_tool_response_messages(
        self,
        tool_calls: list[ToolCall],
        tool_results: list[ToolResult],
    ) -> tuple[Message, Message]:
        """Build session messages for tool calls and their existing results."""
        return (
            self.prepare_tool_call_message(tool_calls),
            self.prepare_tool_result_message(tool_results),
        )

    def prepare_tool_call_message(
        self,
        tool_calls: list[ToolCall],
    ) -> Message:
        """Build the assistant message that describes tool calls."""
        return Message(role="assistant", content=build_tool_calls_context(tool_calls))

    def prepare_tool_result_message(
        self,
        tool_results: list[ToolResult],
    ) -> Message:
        """Build the user message that contains existing tool results."""
        return Message(
            role="user",
            content=build_tool_results_context(tool_results),
            tool_results=tuple(tool_results),
        )
