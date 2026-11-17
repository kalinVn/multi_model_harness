from dataclasses import dataclass, field
from uuid import uuid4

from harness.domain.message import Message
from harness.domain.tool_result import ToolResult
from harness.models.tool_result_summary import ToolResultSummary


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def get_tool_result_by_id(
        self,
        result_id: str,
    ) -> ToolResult | None:
        for message in self.messages:
            for tool_result in message.tool_results:
                if tool_result.id == result_id:
                    return tool_result

        return None

    def get_missing_tool_result_summary_ids(self) -> list[str]:
        """Return IDs for stored tool results that do not have a summary."""

        return [
            result.id
            for message in self.messages
            for result in message.tool_results
            if not result.summary.strip()
        ]

    def apply_tool_result_summaries(
        self,
        summaries: list[ToolResultSummary],
    ) -> None:
        """Attach result summaries so they can replace full output later."""
        for summary in summaries:
            for message in self.messages:
                for result in message.tool_results:
                    if result.id == summary.id and not result.summary.strip() and summary.summary.strip():
                        result.summary = summary.summary
