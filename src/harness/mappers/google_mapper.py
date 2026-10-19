from copy import deepcopy

from google.genai import types

from harness.config.response.gemini_response_instruction import (
    GEMINI_RESPONSE_INSTRUCTION,
)
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.response_instruction import (
    MODEL_RESPONSE_INSTRUCTION,
    TOOL_CALL_INSTRUCTION,  # Местоположение за импорт с обратна съвместимост.
)
from harness.models.tool_schema import ToolSchema
from harness.parser.response_parser import prepare_model_response


def map_tool_schemas(tool_schemas: list[ToolSchema]) -> list[types.Tool]:
    """Преобразува споделените схеми във валидирани декларации на Gemini функции."""
    names = [tool_schema["name"] for tool_schema in tool_schemas]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate harness tool definitions for Gemini")

    declarations: list[types.FunctionDeclaration] = []
    for tool_schema in tool_schemas:
        try:
            parameters = types.Schema.model_validate(
                deepcopy(tool_schema["parameters"])
            )
        except ValueError as error:
            raise ValueError(
                f"Gemini does not support the schema for tool "
                f"'{tool_schema['name']}': {error}"
            ) from error

        declarations.append(
            types.FunctionDeclaration(
                name=tool_schema["name"],
                description=tool_schema["description"],
                parameters=parameters,
            )
        )

    if not declarations:
        return []
    return [types.Tool(function_declarations=declarations)]


def map_messages(
    messages: list[Message],
    use_native_tools: bool = False,
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

    response_instruction = (
        GEMINI_RESPONSE_INSTRUCTION
        if use_native_tools
        else MODEL_RESPONSE_INSTRUCTION
    )
    system_messages.append(response_instruction)

    system_instruction = "\n\n".join(system_messages)

    return contents, system_instruction


def get_response_text(response: types.GenerateContentResponse) -> str:
    """Събира текстовите части, без да допуска, че нативното извикване има текст."""
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
    tool_schemas: list[ToolSchema] | None = None,
) -> ModelResponse:
    """Преобразува Gemini текст и нативни извиквания на функции към споделения отговор."""
    allowed_names = {
        tool_schema["name"]
        for tool_schema in tool_schemas or []
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
        parsed_response = prepare_model_response(response_text)
    elif native_calls:
        parsed_response = ModelResponse()
    else:
        raise ValueError("Gemini returned no response text or tool calls")

    if native_calls and parsed_response.tool_calls:
        raise ValueError("Gemini must return tool calls as native function calls")

    return ModelResponse(
        text=parsed_response.text,
        tool_calls=native_calls or parsed_response.tool_calls,
        tool_result_summaries=parsed_response.tool_result_summaries,
        tool_result_output_requests=(
            parsed_response.tool_result_output_requests
        ),
    )
