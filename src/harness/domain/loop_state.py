from dataclasses import dataclass, field

from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.parser.command_parser import ParsedCommand


@dataclass
class LoopState:
    """Execution state for a single request to MainOrchestrator."""

    tool_steps: int = 0
    command_response_retries: int = 0
    tool_result_output_request_steps: int = 0
    tool_result_summary_retries: int = 0
    model_messages: list[Message] = field(default_factory=list)
    response: ModelResponse | None = None
    parsed_command: ParsedCommand | None = None
