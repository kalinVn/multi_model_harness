from typing import Protocol

from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.tool_schema import ToolSchema


class ModelClient(Protocol):

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
    ) -> ModelResponse:
        ...
