import json
from typing import Any

from google.genai import types

from harness.config.response.gemini_response_instruction import (
    GEMINI_RESPONSE_INSTRUCTION,
)
from harness.converter.tool_converter_facade import ToolConverterFacade
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.parser.response_parser import prepare_model_response


def map_tool_definitions(
    tool_definitions: list[ToolDefinition],
) -> list[dict[str, Any]]:
    """Convert shared definitions to Gemini declaration dictionaries."""
    return ToolConverterFacade().convert_tools(
        "gemini",
        tool_definitions,
    )


def map_messages(
    messages: list[Message],
) -> tuple[list[types.Content], str | None]:
    contents: list[types.Content] = []
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

        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=message.content)])
        )

    system_messages.append(GEMINI_RESPONSE_INSTRUCTION)

    system_instruction = "\n\n".join(system_messages)

    return contents, system_instruction


def get_response_text(response: types.GenerateContentResponse) -> str:
    """Collect text parts without assuming that a native call has text."""
    return "".join(
        part.text
        for candidate in response.candidates or []
        for part in (candidate.content.parts if candidate.content else []) or []
        if part.text
    )


def has_function_calls(response: types.GenerateContentResponse) -> bool:
    return any(
        part.function_call is not None
        for candidate in response.candidates or []
        for part in (candidate.content.parts if candidate.content else []) or []
    )


def map_response(
    response: types.GenerateContentResponse,
    tool_definitions: list[ToolDefinition] | None = None,
) -> ModelResponse:
    """Map user-facing Gemini text and native calls to the shared response.

    Gemini normally returns plain text. The legacy internal response envelope
    is decoded only when all of its protocol fields are present, which keeps
    JSON answers and command-specific JSON as ordinary user-facing content.
    """
    allowed_names = {
        tool_definition["name"]
        for tool_definition in tool_definitions or []
    }
    native_calls: list[ToolCall] = []

    for candidate in response.candidates or []:
        for part in (candidate.content.parts if candidate.content else []) or []:
            function_call = part.function_call
            if function_call is None:
                continue
            if not function_call.name or function_call.name not in allowed_names:
                raise ValueError("Gemini returned an unavailable tool")
            arguments = function_call.args or {}
            if not isinstance(arguments, dict):
                raise ValueError("Gemini tool arguments must be an object")
            native_calls.append(
                ToolCall(name=function_call.name, arguments=arguments)
            )

    response_text = get_response_text(response)
    if response_text.strip():
        parsed_response = _map_text_response(response_text)
    elif native_calls:
        parsed_response = ModelResponse()
    else:
        raise ValueError("Gemini returned no response text or tool calls")

    if parsed_response.tool_calls:
        raise ValueError("Gemini must return tool calls as native function calls")

    return ModelResponse(
        text=parsed_response.text,
        tool_calls=native_calls,
        tool_result_summaries=parsed_response.tool_result_summaries,
        tool_result_output_requests=(
            parsed_response.tool_result_output_requests
        ),
    )


def _map_text_response(response_text: str) -> ModelResponse:
    """Decode a harness metadata envelope, otherwise preserve Gemini text."""
    try:
        data = json.loads(response_text)
    except (json.JSONDecodeError, TypeError):
        return ModelResponse(text=response_text)

    required_metadata_fields = {"text", "tool_result_summaries"}
    allowed_metadata_fields = required_metadata_fields | {
        "tool_calls",
        "tool_result_output_requests",
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
