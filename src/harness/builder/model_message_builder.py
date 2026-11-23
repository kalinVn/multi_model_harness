import os
from dataclasses import replace

from harness.builder.tool_result_context_builder import build_tool_results_context
from harness.config.model_context_config import MAX_TOOL_RESULT_CHARS
from harness.domain.message import Message
from harness.parser.command_parser import ParsedCommand
from harness.service.command_service import CommandService


class ModelMessageBuilder:
    def __init__(self, max_tool_result_chars: int | None = None) -> None:
        self._max_tool_result_chars = self._read_positive_limit(
            "HARNESS_MAX_TOOL_RESULT_CHARS",
            max_tool_result_chars,
            MAX_TOOL_RESULT_CHARS
        )

    def create_model_messages(
        self,
        session_messages: list[Message],
        parsed_command: ParsedCommand | None,
        command_service: CommandService
    ) -> list[Message]:
        """Build model context without modifying the session history."""

        model_messages = self.prepare_new_messages(session_messages)

        if parsed_command is not None:
            model_messages.append(command_service.prepare_command_context(parsed_command))

        return model_messages

    def prepare_new_messages(self, messages: list[Message]) -> list[Message]:
        """Prepare new session messages for incremental model context."""

        model_messages = []

        for message in messages:
            if message.has_tool_results():
                message = replace(
                    message,
                    content=build_tool_results_context(
                        list(message.tool_results),
                        max_output_chars=self._max_tool_result_chars
                    )
                )
            model_messages.append(message)

        return model_messages

    def update_model_messages_by_tool_result_output_requests_ids(
        self,
        model_messages: list[Message],
        tool_result_output_requests: list[str]
    ) -> list[Message]:
        """Expose complete output for explicitly requested tool results."""

        if not tool_result_output_requests:
            return model_messages

        updated_model_messages = []
        model_messages_updated = False

        for message in model_messages:
            if not message.has_tool_results() or not message.has_requested_tool_results(tool_result_output_requests):
                updated_model_messages.append(message)
                continue

            content = build_tool_results_context(
                list(message.tool_results),
                tool_result_output_requests,
                max_output_chars=self._max_tool_result_chars
            )
            if content != message.content:
                message = replace(message, content=content)
                model_messages_updated = True
            updated_model_messages.append(message)

        if not model_messages_updated:
            return model_messages

        return updated_model_messages

    @staticmethod
    def _read_positive_limit(environment_name: str, configured_value: int | None, default: int) -> int:
        raw_value = configured_value if configured_value is not None else os.getenv(environment_name, str(default))
        try:
            value = int(raw_value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{environment_name} must be a positive integer.") from error

        if value < 1:
            raise ValueError(f"{environment_name} must be a positive integer.")

        return value
