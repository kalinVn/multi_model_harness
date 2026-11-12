from typing import Protocol

from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition


class ModelClient(Protocol):
    def count_tokens(self, messages: list[Message], tools: list[ToolDefinition]) -> int:
        """Return the complete provider input size in tokens."""

        ...

    def get_context_limits(self) -> ModelContextLimits:
        """Return the selected model's input and output token limits."""

        ...

    def generate(self, messages: list[Message], tools: list[ToolDefinition] | None = None) -> ModelResponse:
        """Generate a response for the prepared messages and permitted tools."""

        ...
