from dataclasses import dataclass
from harness.models.response import ModelResponse
from harness.parser.command_parser import  ParsedCommand


@dataclass
class LoopState:
    """Състояние на изпълнението за една заявка към MainOrchestrator."""

    tool_steps: int = 0
    command_response_retries: int = 0
    tool_result_output_request_steps: int = 0
    response: ModelResponse | None = None
    parsed_command: ParsedCommand | None = None
