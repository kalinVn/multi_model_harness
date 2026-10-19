import os

from openai import OpenAI

from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.tool_schema import ToolSchema
from harness.parser.response_parser import prepare_model_response
from harness.mappers.openai_mapper import (
    map_messages,
)


class OpenAIClient:
    def __init__(self) -> None:
        self._client = OpenAI()

        self._model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    def generate(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
    ) -> ModelResponse:

        if not messages:
            raise ValueError("Cannot generate response with empty conversation.")

        input_messages = map_messages(messages, tools)

        response = self._client.responses.create(
            model=self._model,
            input=input_messages,
        )

        return prepare_model_response(response.output_text)
