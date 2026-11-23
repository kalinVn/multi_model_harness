from dataclasses import dataclass
from typing import Literal

from harness.domain.tool_result import ToolResult


MessageRole = Literal["user", "assistant", "system"]
MessageType = Literal[
    "user_message",
    "assistant_message",
    "system_instruction",
    "context_memory",
    "tools_instruction",
    "command_instruction",
    "tool_call",
    "tool_result",
    "error"
]


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str
    tool_results: tuple[ToolResult, ...] = ()
    tool_result_output_requests: tuple[str, ...] = ()
    available_tool_names: tuple[str, ...] | None = None
    type: MessageType | None = None

    def has_tool_results(self) -> bool:
        return bool(self.tool_results)

    def has_requested_tool_results(
        self,
        request_ids: list[str],
    ) -> bool:
        for tool_result in self.tool_results:
            if tool_result.id in request_ids:
                return True

        return False

    @staticmethod
    def contains_non_system_message(messages: list["Message"]) -> bool:
        for message in messages:
            if message.role != "system":
                return True

        return False

    @staticmethod
    def get_last_available_tool_names(messages: list["Message"]) -> tuple[str, ...] | None:
        for message in reversed(messages):
            if message.available_tool_names is not None:
                return message.available_tool_names

        return None
