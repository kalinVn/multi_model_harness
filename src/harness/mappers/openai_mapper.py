from harness.builder.tool_parameters_builder import (
    TOOLS_CONTEXT_HEADER,
)
from harness.converter.tool_converter_facade import ToolConverterFacade
from harness.domain.message import Message
from harness.models.response_instruction import MODEL_RESPONSE_INSTRUCTION
from harness.models.tool_definition import ToolDefinition


def map_messages(
    messages: list[Message],
    tools: list[ToolDefinition] | None = None,
) -> list[dict[str, str]]:
    mapped_messages: list[dict[str, str]] = []
    tools_context_mapped = False

    for message in messages:
        content = message.content
        if (
            tools
            and message.role == "system"
            and content.startswith(TOOLS_CONTEXT_HEADER)
        ):
            content = ToolConverterFacade().convert_tools("openai", tools)
            tools_context_mapped = True
        mapped_messages.append({"role": message.role, "content": content})

    if tools and not tools_context_mapped:
        mapped_messages.append(
            {
                "role": "system",
                "content": ToolConverterFacade().convert_tools(
                    "openai",
                    tools,
                ),
            }
        )

    mapped_messages.append(
        {"role": "system", "content": MODEL_RESPONSE_INSTRUCTION}
    )
    return mapped_messages
