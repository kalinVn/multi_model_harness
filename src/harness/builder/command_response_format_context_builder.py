from harness.domain.message import Message


def build_command_response_retry_context() -> Message:
    return Message(
        role="system",
        type="command_instruction",
        content=(
            "The previous command response was empty or did not follow the "
            "required format. Return the final command response now. The outer "
            "response `text` must be nonempty and contain a JSON-encoded object "
            "with exactly one nonempty string field: `answer`. "
            "For example: `{\"answer\":\"Done\"}`. "
            "Do not wrap the inner JSON in Markdown."
        ),
    )
