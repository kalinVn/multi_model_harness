import json
import os
from copy import deepcopy
from typing import Any

import httpx
from google import genai
from google.genai.errors import ClientError, ServerError

from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.response_instruction import MODEL_RESPONSE_SCHEMA
from harness.models.tool_definition import ToolDefinition
from harness.mappers.google_mapper import map_messages
from harness.parser.response_parser import prepare_model_response
from harness.validators.gemini_error_validator import GeminiErrorValidator
from harness.validators.messages_validator import MessagesValidator


def _prepare_response_schema(value: Any) -> Any:
    """Remove JSON Schema fields unsupported by Gemini structured output."""

    if isinstance(value, dict):
        return {
            key: _prepare_response_schema(nested_value)
            for key, nested_value in value.items()
            if key not in {"minLength", "maxLength"}
        }
    if isinstance(value, list):
        return [_prepare_response_schema(item) for item in value]

    return deepcopy(value)


def _build_response_schema(tools: list[ToolDefinition] | None) -> dict[str, object]:
    response_schema = deepcopy(MODEL_RESPONSE_SCHEMA)
    tool_calls_schema = response_schema["properties"]["tool_calls"]
    if tools:
        tool_calls_schema["items"] = {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "string", "enum": [tool["name"]]},
                        "arguments": _prepare_response_schema(tool["parameters"])
                    },
                    "required": ["tool", "arguments"]
                }
                for tool in tools
            ]
        }
    else:
        tool_calls_schema["maxItems"] = 0

    return response_schema


class GeminiClient:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY")

        timeout_seconds = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

        self._client = genai.Client(
            api_key=api_key,
            http_options={
                "timeout": timeout_seconds * 1000,
                "retry_options": {
                    "attempts": 4,
                    "initial_delay": 1.0,
                    "max_delay": 8.0,
                    "exp_base": 2.0,
                    "jitter": 1.0,
                    "http_status_codes": [500, 502, 503, 504],
                },
            },
        )

        self._model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def count_tokens(self, messages: list[Message], tools: list[ToolDefinition]) -> int:
        MessagesValidator.validate(messages)
        contents, system_instruction = map_messages(messages, tools)
        response_schema = json.dumps(_build_response_schema(tools), ensure_ascii=False, separators=(",", ":"))
        hidden_context = (
            f"System instruction:\n{system_instruction}\n\n"
            f"Structured response schema:\n{response_schema}"
        )
        contents_for_count = [
            {"role": "user", "parts": [{"text": hidden_context}]},
            *contents
        ]

        try:
            response = self._client.models.count_tokens(
                model=self._model,
                contents=contents_for_count
            )
        except (ClientError, ServerError, httpx.HTTPError) as error:
            GeminiErrorValidator.validate(error, self._model)

        if not isinstance(response.total_tokens, int):
            raise ValueError(f"Gemini did not return a token count for model '{self._model}'.")

        return response.total_tokens

    def get_context_limits(self) -> ModelContextLimits:
        try:
            metadata = self._client.models.get(model=self._model)
        except (ClientError, ServerError, httpx.HTTPError) as error:
            GeminiErrorValidator.validate(error, self._model)

        input_token_limit = metadata.input_token_limit
        output_token_limit = metadata.output_token_limit
        if not isinstance(input_token_limit, int) or not isinstance(output_token_limit, int):
            raise ValueError(f"Gemini model '{self._model}' did not provide token limits.")

        return ModelContextLimits(
            model=self._model,
            context_window=input_token_limit,
            reserved_output_tokens=output_token_limit,
            input_token_limit=input_token_limit
        )

    def generate(self, messages: list[Message], tools: list[ToolDefinition] | None = None) -> ModelResponse:
        MessagesValidator.validate(messages)
        contents, system_instruction = map_messages(messages, tools)

        config: dict[str, object] = {
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": _build_response_schema(tools)
        }

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config
            )
        except (ClientError, ServerError, httpx.HTTPError) as error:
            GeminiErrorValidator.validate(error, self._model)

        return prepare_model_response(response.text)
