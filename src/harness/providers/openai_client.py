import os

from openai import OpenAI

from harness.config.model_context_config import OPENAI_MODEL_CONTEXT_LIMITS
from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.mappers.openai_mapper import map_messages
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.parser.response_parser import prepare_model_response


class OpenAIClient:
    def __init__(self) -> None:
        self._client = OpenAI()

        self._model = os.getenv("OPENAI_MODEL", "gpt-5.5")

    def count_tokens(self, messages: list[Message], tools: list[ToolDefinition]) -> int:
        if not messages:
            raise ValueError("Cannot count tokens for an empty conversation.")

        input_messages = map_messages(messages, tools)
        response = self._client.responses.input_tokens.count(
            model=self._model,
            input=input_messages
        )
        if not isinstance(response.input_tokens, int):
            raise ValueError(f"OpenAI did not return a token count for model '{self._model}'.")

        return response.input_tokens

    def get_context_limits(self) -> ModelContextLimits:
        configured_limits = OPENAI_MODEL_CONTEXT_LIMITS.get(self._model)
        context_window_value = os.getenv("OPENAI_CONTEXT_WINDOW")
        reserved_output_value = os.getenv("OPENAI_RESERVED_OUTPUT_TOKENS")

        if configured_limits is None and (
            context_window_value is None or reserved_output_value is None
        ):
            raise ValueError(
                f"Missing context window metadata for OpenAI model '{self._model}'. "
                "Set OPENAI_CONTEXT_WINDOW and OPENAI_RESERVED_OUTPUT_TOKENS."
            )

        default_context_window, default_reserved_output = configured_limits or (None, None)
        context_window_raw = context_window_value if context_window_value is not None else default_context_window
        reserved_output_raw = reserved_output_value if reserved_output_value is not None else default_reserved_output
        try:
            context_window = int(context_window_raw)
            reserved_output_tokens = int(reserved_output_raw)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "OPENAI_CONTEXT_WINDOW and OPENAI_RESERVED_OUTPUT_TOKENS must be integers."
            ) from error

        if context_window < 1:
            raise ValueError("OPENAI_CONTEXT_WINDOW must be a positive integer.")
        if reserved_output_tokens < 0:
            raise ValueError("OPENAI_RESERVED_OUTPUT_TOKENS cannot be negative.")

        return ModelContextLimits(
            model=self._model,
            context_window=context_window,
            reserved_output_tokens=reserved_output_tokens
        )

    def generate(self, messages: list[Message], tools: list[ToolDefinition] | None = None) -> ModelResponse:
        if not messages:
            raise ValueError("Cannot generate response with empty conversation.")

        input_messages = map_messages(messages, tools)

        response = self._client.responses.create(
            model=self._model,
            input=input_messages
        )

        return prepare_model_response(response.output_text)
