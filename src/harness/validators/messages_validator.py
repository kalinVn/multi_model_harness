from harness.domain.message import Message


class MessagesValidator:
    """Validate that model messages contain conversation content."""

    @staticmethod
    def validate(messages: list[Message]) -> None:
        """
        Validate that messages include at least one non-system message.

        Example (valid): [Message(role="user", content="Hello")].
        Example (invalid): [Message(role="system", content="Rules")].
        Result: ValueError because the conversation has no non-system message.
        """
        if not Message.contains_non_system_message(messages):
            raise ValueError("Cannot generate response with empty conversation.")
