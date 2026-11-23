import json


class CommandResponseValidator:
    """Validate the structured response returned for a command."""

    def validate(self, response_text: str) -> bool:
        """
        Validate that command JSON has exactly one string answer field.

        Example (valid): '{"answer": "Done"}'.
        Example (invalid): '{"answer": 1}'.
        Result: False for invalid data; this method does not raise validation errors.
        """
        try:
            payload = json.loads(response_text)
        except (json.JSONDecodeError, TypeError):
            return False

        if not isinstance(payload, dict):
            return False

        if set(payload) != {"answer"}:
            return False

        return isinstance(payload["answer"], str) and bool(payload["answer"].strip())
