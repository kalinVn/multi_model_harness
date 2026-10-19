import json

from harness.validators.command_response_validator import CommandResponseValidator


def parse_command_response(response_text: str) -> tuple[str, str] | None:
    """Parse a command response after it passes validation."""
    validator = CommandResponseValidator()

    if not validator.validate(response_text):
        return None

    payload = json.loads(response_text)
    answer = payload["answer"]
    command_summary = payload["command_summary"]

    return answer, command_summary.strip()
