from harness.builder.tool_parameters_builder import TOOLS_CONTEXT_HEADER, build_text_tools_context
from harness.domain.message import Message
from harness.models.response_instruction import MODEL_RESPONSE_INSTRUCTION
from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_validator import ToolValidator


def map_messages(messages: list[Message], tools: list[ToolDefinition] | None = None) -> tuple[list[dict[str, object]], str]:
    """Map Harness history to the dictionary format accepted by Gemini.

    Tool calls and tool results are already rendered into Message.content by
    the shared Harness message builders, so their history remains unchanged.
    """
    contents: list[dict[str, object]] = []
    system_messages: list[str] = []
    tools_context_mapped = False

    for message in messages:
        if message.role == "system":
            content = message.content
            if tools and content.startswith(TOOLS_CONTEXT_HEADER):
                ToolValidator.validate_tool_names(tools)
                content = build_text_tools_context(tools)
                tools_context_mapped = True
            system_messages.append(content)
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

    if tools and not tools_context_mapped:
        ToolValidator.validate_tool_names(tools)
        system_messages.append(build_text_tools_context(tools))

    system_messages.append(MODEL_RESPONSE_INSTRUCTION)

    return contents, "\n\n".join(system_messages)
