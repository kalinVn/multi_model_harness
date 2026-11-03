import os

import httpx
from google import genai
from google.genai.errors import ClientError, ServerError

from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.mappers.google_mapper import (
    get_tool_object,
    map_messages,
    map_response,
)
from harness.validators.gemini_error_validator import GeminiErrorValidator
from harness.validators.messages_validator import MessagesValidator


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

    def generate(self, messages: list[Message], tools: list[ToolDefinition] | None = None) -> ModelResponse:
        MessagesValidator.validate(messages)
        contents, system_instruction = map_messages(messages)

        config: dict[str, object] = {
            "system_instruction": system_instruction,
            "tools": get_tool_object(tools or []) or None,
        }

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=contents,
                config=config
            )
        except (ClientError, ServerError, httpx.HTTPError) as error:
            GeminiErrorValidator.validate(error, self._model)

        return map_response(response, tools)
