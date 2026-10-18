from harness.domain.message import Message


class MessagesValidator:
    """Validate that model messages contain conversation content."""

    @staticmethod
    def validate(messages: list[Message]) -> None:
        if not messages or not any(
            message.role != "system"
            for message in messages
        ):
            raise ValueError("Cannot generate response with empty conversation.")
