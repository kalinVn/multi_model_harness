from harness.builder.tools_schema_builder import (
    TOOLS_CONTEXT_HEADER,
    build_text_tools_context,
)
from harness.domain.message import Message
from harness.models.response_instruction import MODEL_RESPONSE_INSTRUCTION
from harness.models.tool_schema import ToolSchema


def map_messages(
    messages: list[Message],
    tools: list[ToolSchema] | None = None,
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
            content = build_text_tools_context(tools)
            tools_context_mapped = True
        mapped_messages.append({"role": message.role, "content": content})

    if tools and not tools_context_mapped:
        mapped_messages.append(
            {
                "role": "system",
                "content": build_text_tools_context(tools),
            }
        )

    mapped_messages.append(
        {"role": "system", "content": MODEL_RESPONSE_INSTRUCTION}
    )
    return mapped_messages
