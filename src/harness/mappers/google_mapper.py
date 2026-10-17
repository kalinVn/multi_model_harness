from google.genai import types

from harness.domain.message import Message


from harness.models.response_instruction import (
    MODEL_RESPONSE_INSTRUCTION,
    TOOL_CALL_INSTRUCTION,  # Backward-compatible import location.
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

    system_messages.append(MODEL_RESPONSE_INSTRUCTION)

    system_instruction = "\n\n".join(system_messages)

    return contents, system_instruction
