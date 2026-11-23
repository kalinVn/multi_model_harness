import json
from dataclasses import dataclass, field
from uuid import uuid4

from harness.domain.message import Message
from harness.domain.tool_result import ToolResult
from harness.models.context_memory_summary import ContextMemorySummary
from harness.models.response import TaskStatus


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[Message] = field(default_factory=list)
    context_memory_summary: ContextMemorySummary | None = None
    active_task_start_index: int | None = None
    task_status: TaskStatus | None = None
    completion_uncertainty: str | None = None
    memory_update_completed: bool = False
    memory_update_error: str | None = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def begin_or_resume_task(self) -> None:
        """Start a task boundary or resume the existing blocked or unfinished task."""

        if self.active_task_start_index is not None:
            return

        self.active_task_start_index = len(self.messages)
        self.task_status = "in_progress"
        self.completion_uncertainty = None
        self.memory_update_completed = False
        self.memory_update_error = None

    def get_active_task_messages(self) -> list[Message]:
        if self.active_task_start_index is None:
            return []

        return self.messages[self.active_task_start_index:]

    def get_model_context_messages(self) -> list[Message]:
        if self.context_memory_summary is None:
            return list(self.messages)

        task_start = self.active_task_start_index
        if task_start is None:
            task_start = len(self.messages)
        system_messages = [
            message
            for message in self.messages[:task_start]
            if message.type == "system_instruction"
        ]
        memory_message = Message(
            role="system",
            type="context_memory",
            content=json.dumps(self.context_memory_summary.to_dict())
        )

        return [*system_messages, memory_message, *self.messages[task_start:]]

    def mark_memory_updated(self, summary: ContextMemorySummary) -> None:
        self.context_memory_summary = summary
        self.active_task_start_index = None
        self.task_status = "completed"
        self.completion_uncertainty = None
        self.memory_update_completed = True
        self.memory_update_error = None

    def get_tool_result_by_id(
        self,
        result_id: str,
    ) -> ToolResult | None:
        for message in self.messages:
            for tool_result in message.tool_results:
                if tool_result.id == result_id:
                    return tool_result

        return None
