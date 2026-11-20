from harness.domain.message import Message


class AgentValidator:
    @staticmethod
    def validate(name: str, description: str, instructions: str) -> Message | None:
        if not name:
            return Message(role="assistant", type="error", content="Agent must contain a '# Name' section.")

        if not description:
            return Message(role="assistant", type="error", content="Agent must contain a '# Description' section.")

        if not instructions:
            return Message(role="assistant", type="error", content="Agent must contain an '# Instructions' section.")

        return None
