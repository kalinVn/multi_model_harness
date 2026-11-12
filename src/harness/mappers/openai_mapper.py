from harness.config.response.model_response_config import MODEL_RESPONSE_INSTRUCTION
from harness.converter.tool_converter_facade import ToolConverterFacade
from harness.domain.message import Message
from harness.models.tool_definition import ToolDefinition


def map_messages(messages: list[Message], tools: list[ToolDefinition] | None = None) -> list[dict[str, str]]:
    mapped_messages = [{"role": message.role, "content": message.content} for message in messages]

    if tools:
        mapped_messages.append({
            "role": "system",
            "content": ToolConverterFacade().convert_tools("openai", tools)
        })

    mapped_messages.append({"role": "system", "content": MODEL_RESPONSE_INSTRUCTION})

    return mapped_messages
