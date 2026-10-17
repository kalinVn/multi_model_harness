import json
import os
import re

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from harness.domain.message import Message
from harness.mappers.groq_mapper import map_messages, map_response
from harness.models.errors import ModelConnectionError, ModelRateLimitError
from harness.models.response import ModelResponse
from harness.parser.command_response_parser import parse_command_response


class GroqClient:
    MAX_INVALID_RESPONSE_RETRIES = 2

    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY")
        self._model = os.getenv("GROQ_MODEL", "").strip()
        if not self._model:
            raise ValueError("Missing GROQ_MODEL")
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=60.0,
            max_retries=2,
        )

    def generate(self, messages: list[Message]) -> ModelResponse:
        if not messages or not any(message.role != "system" for message in messages):
            raise ValueError("Cannot generate response with empty conversation.")
        mapped, tools = map_messages(messages)
        options = {"tools": tools, "tool_choice": "auto"} if tools else {
            "response_format": {"type": "json_object"},
        }
        command_response_required = any(
            "`command_summary`" in message.content
            for message in messages
        )
        request_messages = mapped
        request_options = options
        invalid_response_retries = 0

        while True:
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=request_messages,
                    **request_options,
                )
            except RateLimitError as error:
                raise ModelRateLimitError(
                    "Groq request quota exceeded. Retry after the cooldown."
                ) from error
            except APIConnectionError as error:
                raise ModelConnectionError(
                    "Groq could not be reached. Check the connection."
                ) from error
            except APIStatusError as error:
                details = self._format_api_error_details(error)
                size_guidance = ""
                if error.status_code == 413:
                    size_guidance = (
                        " Reduce HARNESS_MAX_HISTORY_MESSAGES and "
                        "HARNESS_MAX_TOOL_RESULT_CHARS."
                    )
                raise ModelConnectionError(
                    f"Groq request failed ({error.status_code}): {details}."
                    f"{size_guidance}"
                ) from error

            if not response.choices:
                raise ValueError("Groq returned no response choices")

            choice = response.choices[0]
            if choice.finish_reason not in {"stop", "tool_calls"}:
                raise ValueError(
                    "Groq returned an incomplete response: "
                    f"{choice.finish_reason}"
                )

            try:
                return map_response(choice.message, tools)
            except ValueError as error:
                response_text = choice.message.content
                if (
                    not command_response_required
                    and not choice.message.tool_calls
                    and isinstance(response_text, str)
                    and response_text.strip()
                    and not response_text.lstrip().startswith(("{", "[", "```"))
                ):
                    return ModelResponse(text=response_text)

                if (
                    command_response_required
                    and not choice.message.tool_calls
                    and parse_command_response(response_text) is not None
                ):
                    return ModelResponse(text=response_text)

                if (
                    invalid_response_retries
                    >= self.MAX_INVALID_RESPONSE_RETRIES
                ):
                    raise ValueError(
                        "Groq returned an invalid model response after "
                        f"{self.MAX_INVALID_RESPONSE_RETRIES} retries: {error}"
                    ) from error

                invalid_response_retries += 1
                if command_response_required:
                    expected_response = (
                        'If the command is complete, return exactly this outer JSON '
                        'shape: {"text":"{\\"answer\\":\\"Done\\",'
                        '\\"command_summary\\":\\"One concise sentence.\\"}",'
                        '"tool_calls":[],"tool_result_summaries":[]}.'
                    )
                else:
                    expected_response = (
                        'If no tool is needed, return exactly this JSON shape: '
                        '{"text":"Your answer","tool_calls":[],'
                        '"tool_result_summaries":[]}.'
                    )

                request_messages = mapped + [
                    {
                        "role": "system",
                        "content": (
                            "The previous response was invalid: "
                            f"{error}. Follow the response protocol exactly. "
                            "If a tool is needed, invoke it as a native function "
                            "call and leave message content empty; never put a tool "
                            "call JSON object in message content. "
                            f"{expected_response} Do not return Markdown or plain "
                            "text outside the outer JSON object."
                        ),
                    }
                ]
                request_options = {
                    **options,
                    "temperature": 0,
                }

    @staticmethod
    def _format_api_error_details(error: APIStatusError) -> str:
        body = getattr(error, "body", None)
        if body is not None:
            details = json.dumps(
                GroqClient._redact_error_value(body),
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )
        else:
            details = getattr(error, "message", None) or str(error)

        details = re.sub(
            r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+",
            r"\1<redacted>",
            str(details),
        )
        if len(details) > 2_000:
            details = details[:2_000] + "... [Groq error details truncated]"
        return details

    @staticmethod
    def _redact_error_value(value):
        if isinstance(value, dict):
            redacted = {}
            for key, nested_value in value.items():
                normalized_key = str(key).lower().replace("-", "_")
                if normalized_key in {"key", "api_key", "apikey"} or any(
                    marker in normalized_key
                    for marker in ("authorization", "password", "secret", "token")
                ):
                    redacted[key] = "<redacted>"
                else:
                    redacted[key] = GroqClient._redact_error_value(nested_value)
            return redacted
        if isinstance(value, list):
            return [GroqClient._redact_error_value(item) for item in value]
        return value
