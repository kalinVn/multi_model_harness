import json
from typing import Any

from harness.config.response.gemini_response_instruction import GEMINI_RESPONSE_INSTRUCTION
from harness.converter.tool_converter_facade import ToolConverterFacade
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.parser.response_parser import prepare_model_response
from harness.validators.gemini_response_validator import GeminiResponseValidator
from harness.validators.tool_call_validator import ToolCallValidator


def get_tool_object(tool_definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Convert shared definitions to Gemini declaration dictionaries."""

    return ToolConverterFacade().convert_tools("gemini", tool_definitions)


def map_messages(
    messages: list[Message],
) -> tuple[list[dict[str, object]], str]:
    """Map Harness history to the dictionary format accepted by Gemini.

    Tool calls and tool results are already rendered into Message.content by
    the shared Harness message builders, so their history remains unchanged.
    """
    contents: list[dict[str, object]] = []
    system_messages: list[str] = []

    for message in messages:
        if message.role == "system":
            system_messages.append(message.content)
            continue

        role = (
            "model"
            if message.role == "assistant"
            else "user"
        )

        contents.append({
            "role": role,
            "parts": [{"text": message.content}],
        })

    system_messages.append(GEMINI_RESPONSE_INSTRUCTION)

    system_instruction = "\n\n".join(system_messages)

    return contents, system_instruction


class GeminiResponseMapper:
    """Convert Gemini responses into the shared model response contract."""

    def map_response(self, response: Any) -> ModelResponse:
        """Map user-facing Gemini text and native calls to the shared response.

        Gemini normally returns plain text. The legacy internal response envelope
        is decoded only when all of its protocol fields are present, which keeps
        JSON answers and command-specific JSON as ordinary user-facing content.
        """
        candidates = response.candidates or []
        response_text = ""
        native_calls: list[ToolCall] = []

        for candidate in candidates:
            parts = (candidate.content.parts if candidate.content else []) or []
            for part in parts:
                if part.text:
                    response_text += part.text

                function_call = part.function_call
                if function_call is None:
                    continue

                native_calls.append(ToolCall(
                    name=function_call.name,
                    arguments=function_call.args or {}
                ))

        GeminiResponseValidator.validate(response, response_text, bool(native_calls))

        try:
            ToolCallValidator.validate_arguments(native_calls, "Gemini")
            parsed_response = self._map_text_response(response_text) if response_text.strip() else ModelResponse()
            ToolCallValidator.validate_native_tool_calls(parsed_response.tool_calls, "Gemini")
        except ValueError as error:
            raise ValueError(f"Gemini returned an invalid model response: {error}") from error

        return ModelResponse(
            text=parsed_response.text,
            tool_calls=native_calls,
            tool_result_summaries=parsed_response.tool_result_summaries,
            tool_result_output_requests=parsed_response.tool_result_output_requests
        )

    def _map_text_response(self, response_text: str) -> ModelResponse:
        """Decode a harness metadata envelope, otherwise preserve Gemini text."""

        try:
            data = json.loads(response_text)

        except (json.JSONDecodeError, TypeError):
            return ModelResponse(text=response_text)

        required_metadata_fields = {"text", "tool_result_summaries"}
        allowed_metadata_fields = required_metadata_fields | {
            "tool_calls",
            "tool_result_output_requests"
        }

        if (
            not isinstance(data, dict)
            or not required_metadata_fields.issubset(data)
            or not set(data).issubset(allowed_metadata_fields)
        ):
            return ModelResponse(text=response_text)

        if "tool_calls" not in data:
            data["tool_calls"] = []
            response_text = json.dumps(data, ensure_ascii=False)

        return prepare_model_response(response_text)
