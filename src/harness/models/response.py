from dataclasses import dataclass, field
from typing import Literal

from harness.domain.tool_call import ToolCall


TaskStatus = Literal["in_progress", "completed", "blocked"]


@dataclass(frozen=True)
class ModelResponse:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_result_output_requests: list[str] = field(default_factory=list)
    task_status: TaskStatus | None = None
