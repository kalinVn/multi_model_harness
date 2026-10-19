from harness.domain.message import Message


class MessagesValidator:
    """Валидира, че съобщенията към модела съдържат разговорно съдържание."""

    @staticmethod
    def validate(messages: list[Message]) -> None:
        """
        Валидира, че съобщенията включват поне едно несистемно съобщение.

        Пример (валиден): [Message(role="user", content="Здравей")].
        Пример (невалиден): [Message(role="system", content="Правила")].
        Резултат: ValueError, защото разговорът няма несистемно съобщение.
        """
        if not messages or not any(
            message.role != "system"
            for message in messages
        ):
            raise ValueError("Cannot generate response with empty conversation.")
