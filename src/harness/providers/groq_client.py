import json
import os
import re

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError

from harness.domain.message import Message
from harness.mappers.groq_mapper import prepare_groq_response, prepare_groq_tools, prepare_groq_messages
from harness.models.errors import ModelConnectionError, ModelRateLimitError
from harness.models.groq_tool_type import GroqToolType
from harness.models.response import ModelResponse
from harness.models.tool_schema import ToolSchema
from harness.validators.messages_validator import MessagesValidator
from harness.validators.model_response_validator import ModelResponseValidator


GroqResponseParseResult = ModelResponse | tuple[list[dict[str, str]], dict]


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
        

    def generate(
        self,
        model_messages: list[Message],
        tools: list[ToolSchema] | None = None,
    ) -> ModelResponse:
        MessagesValidator.validate(model_messages)

        tools_list = prepare_groq_tools(tools)
        groq_messages = prepare_groq_messages(model_messages)

        if tools_list:
            groq_options = {
                "tools": tools_list,
                "tool_choice": "auto",
            }
        else:
            groq_options = {
                "response_format": {"type": "json_object"},
            }

        command_response_required = any("`command_summary`" in message.content for message in model_messages)

        request_messages = groq_messages.copy()
        request_options = groq_options.copy()

        for retry_attempt in range(self.MAX_INVALID_RESPONSE_RETRIES + 1):
            choice = self._fetch_groq_response(
                request_messages,
                request_options
            )

            parse_result = self._parse_groq_response(
                choice,
                tools_list,
                command_response_required,
                retry_attempt,
                groq_messages,
                groq_options
            )

            if isinstance(parse_result, ModelResponse):
                return parse_result

            request_messages, request_options = parse_result


    def _fetch_groq_response(
        self,
        request_messages: list[dict[str, str]],
        request_options: dict,
    ):
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

        ModelResponseValidator.validate_response_choice(response)

        choice = response.choices[0]

        return choice

    

    def _parse_groq_response(
        self,
        choice,
        tools_list: list[GroqToolType],
        command_response_required: bool,
        retry_attempt: int,
        groq_messages: list[dict[str, str]],
        groq_options: dict,
    ) -> GroqResponseParseResult:
        try:
            return prepare_groq_response(
                choice.message.content,
                choice.message.tool_calls,
                tools_list,
            )
        except ValueError as error:
            response_text = choice.message.content

            unwrapped_response_text = (
                ModelResponseValidator.unwrap_json_code_fence(response_text)
            )

            if unwrapped_response_text is not None:
                try:
                    return prepare_groq_response(
                        unwrapped_response_text,
                        choice.message.tool_calls,
                        tools_list,
                    )
                except ValueError:
                    if ModelResponseValidator.is_valid_command_response(
                        command_response_required,
                        choice.message.tool_calls,
                        unwrapped_response_text,
                    ):
                        return ModelResponse(text=unwrapped_response_text)

            if ModelResponseValidator.is_acceptable_text_response(
                command_response_required,
                choice.message.tool_calls,
                response_text,
            ):
                return ModelResponse(text=response_text)

            ModelResponseValidator.validate_retry_limit(
                retry_attempt,
                self.MAX_INVALID_RESPONSE_RETRIES,
                error,
                response_text,
            )

            expected_response = self._get_expected_response(command_response_required)

            request_messages = self._get_request_messages(
                groq_messages,
                error,
                expected_response,
                response_text,
            )

            request_options = {**groq_options, "temperature": 0}

            return request_messages, request_options
        

    def _get_expected_response(
        self,
        command_response_required: bool,
    ) -> str:
        r"""
        Return the response-format instruction for the current response type.

        Description:
            Select the exact JSON response example required for a command or a
            regular model response.
        Args:
            command_response_required: Whether command response JSON is required.
        Example input:
            self._get_expected_response(True)
            self._get_expected_response(False)
        Example output:
            'If the command is complete, return exactly this outer JSON shape: {"text":"{\"answer\":\"Done\",\"command_summary\":\"One concise sentence.\"}","tool_calls":[],"tool_result_summaries":[]}.'
            'If no tool is needed, return exactly this JSON shape: {"text":"Your answer","tool_calls":[],"tool_result_summaries":[]}.'
        Returns:
            The exact expected-response instruction string.
        """
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

        return expected_response
    

    def _get_request_messages(
        self,
        groq_messages,
        error,
        expected_response,
        response_text,
    ):
        """
        Append the response-correction instruction to the original Groq messages.

        Description:
            Build a new message list containing the original messages followed by
            the exact system correction instruction for an invalid response.
        Args:
            groq_messages: The original list of Groq message dictionaries.
            error: The validation error produced for the previous response.
            expected_response: The expected-response instruction to append.
        Example input:
            groq_messages = [{"role": "user", "content": "Hello"}]
            error = ValueError("invalid JSON")
            expected_response = "Return valid JSON."
        Example output:
            [
                {"role": "user", "content": "Hello"},
                {
                    "role": "system",
                    "content": "The previous response was invalid: invalid JSON. Follow the response protocol exactly. If a tool is needed, invoke it as a native function call and leave message content empty; never put a tool call JSON object in message content. Return valid JSON. Do not return Markdown or plain text outside the outer JSON object.",
                },
            ]
        Returns:
            A new complete list containing the original and correction messages.
        """
        invalid_response_message = []
        if isinstance(response_text, str) and response_text:
            invalid_response_message.append(
                {"role": "assistant", "content": response_text}
            )

        return groq_messages + invalid_response_message + [
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
