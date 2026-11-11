from dataclasses import dataclass
from typing import Literal

from harness.domain.tool_result import ToolResult


MessageRole = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class Message:
    role: MessageRole
    content: str
    tool_results: tuple[ToolResult, ...] = ()
    tool_result_output_requests: tuple[str, ...] = ()
    available_tool_names: tuple[str, ...] | None = None

    def has_tool_results(self) -> bool:
        return bool(self.tool_results)

    def has_requested_tool_results(
        self,
        request_ids: list[str],
    ) -> bool:
        return any(tool_result.id in request_ids for tool_result in self.tool_results)
