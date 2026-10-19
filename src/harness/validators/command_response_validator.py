import json


class CommandResponseValidator:
    """Validate the structured response returned for a command."""

    def validate(self, response_text: str) -> bool:
        """
        Validate that command JSON has string answer and non-empty summary fields.

        Example (valid): '{"answer": "Done", "command_summary": "Updated file"}'.
        Example (invalid): '{"answer": "Done", "command_summary": ""}'.
        Result: False for invalid data; this method does not raise validation errors.
        """
        try:
            payload = json.loads(response_text)
        except (json.JSONDecodeError, TypeError):
            return False

        if not isinstance(payload, dict):
            return False

        answer = payload.get("answer")
        command_summary = payload.get("command_summary")

        if not isinstance(answer, str):
            return False

        if not isinstance(command_summary, str) or not command_summary.strip():
            return False

        return True
