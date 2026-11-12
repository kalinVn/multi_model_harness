import os
from dataclasses import replace

from harness.builder.tool_result_context_builder import (
    build_tool_results_context,
    has_tool_result_summary,
)
from harness.domain.message import Message
from harness.parser.command_parser import ParsedCommand
from harness.service.command_service import CommandService


class ModelMessageBuilder:
    DEFAULT_MAX_TOOL_RESULT_CHARS = 12_000

    def __init__(self, max_tool_result_chars: int | None = None) -> None:
        self._max_tool_result_chars = self._read_positive_limit(
            "HARNESS_MAX_TOOL_RESULT_CHARS",
            max_tool_result_chars,
            self.DEFAULT_MAX_TOOL_RESULT_CHARS
        )

    def create_model_messages(
        self,
        session_messages: list[Message],
        parsed_command: ParsedCommand | None,
        command_service: CommandService
    ) -> list[Message]:
        """Build model context without modifying the session history."""

        command_message = None

        if parsed_command is not None:
            command_message = command_service.prepare_command_context(parsed_command)

        model_messages = self.compose_model_messages(session_messages)

        if command_message is not None:
            model_messages.append(command_message)

        return model_messages

    def compose_model_messages(self, messages: list[Message]) -> list[Message]:
        """Process all messages and prepare the model context.

        For messages with tool_results, use the summary when one exists or the
        full output otherwise. Collect the IDs of tool results without a
        summary and add instructions asking the model to summarize them. The
        original session messages are not modified.
        """

        model_messages: list[Message] = []

        tool_result_ids_to_summarize = self._add_tool_results_to_model_messages(
            messages,
            model_messages
        )

        self._add_tool_result_summary_instructions_to_model_messages(
            model_messages,
            tool_result_ids_to_summarize
        )

        return model_messages

    def update_model_messages_by_tool_result_output_requests_ids(
        self,
        model_messages: list[Message],
        tool_result_output_requests: list[str]
    ) -> list[Message]:
        """Update only contexts with explicitly requested full tool outputs.

        The original session messages remain unchanged.
        """

        if not tool_result_output_requests:
            return model_messages

        updated_model_messages: list[Message] = []
        model_messages_updated = False

        for message in model_messages:
            if not message.has_tool_results() or not message.has_requested_tool_results(tool_result_output_requests):
                updated_model_messages.append(message)
                continue

            updated_content = build_tool_results_context(
                list(message.tool_results),
                tool_result_output_requests,
                max_output_chars=self._max_tool_result_chars
            )

            if updated_content == message.content:
                updated_model_messages.append(message)
                continue

            updated_model_messages.append(replace(message, content=updated_content))
            model_messages_updated = True

        if not model_messages_updated:
            return model_messages

        return updated_model_messages

    def _add_tool_results_to_model_messages(
        self,
        messages: list[Message],
        model_messages: list[Message]
    ) -> list[str]:
        """Process all messages and check whether they contain tool_results.

        For messages with tool_results, inspect each ToolResult. Use a valid
        summary instead of the full output when available. Otherwise, use the
        full output and add result.id to tool_result_ids_to_summarize for later
        summarization. Add the processed message to model_messages. Messages
        without tool_results are added unchanged. The original session
        messages are not modified.
        """

        tool_result_ids_to_summarize: list[str] = []

        for message in messages:
            if message.has_tool_results():
                for tool_result in message.tool_results:
                    if not has_tool_result_summary(tool_result):
                        tool_result_ids_to_summarize.append(tool_result.id)

                model_messages.append(
                    replace(
                        message,
                        content=build_tool_results_context(
                            list(message.tool_results),
                            max_output_chars=self._max_tool_result_chars
                        )
                    )
                )
            else:
                model_messages.append(message)

        return tool_result_ids_to_summarize

    def _add_tool_result_summary_instructions_to_model_messages(
        self,
        model_messages: list[Message],
        tool_result_ids_to_summarize: list[str]
    ) -> None:
        """Check whether any ToolResult IDs need to be summarized.

        Use the IDs already collected in tool_result_ids_to_summarize. If any
        exist, append an instruction to model_messages that tells the model
        which ToolResults require summaries. Do not iterate over every message
        again or process tool output. The original session messages are not
        modified.
        """

        if not tool_result_ids_to_summarize:
            return

        instruction = (
            "While continuing the main task, return a concise semantic summary "
            "for each of these tool result IDs, identifying each summary by its ID: "
            + ", ".join(tool_result_ids_to_summarize)
            + ". Aim for 100 to 200 tokens per summary, at most about 250 tokens; "
            "use fewer tokens for simple results."
        )

        model_messages.append(
            Message(role="system", type="tool_result_summary", content=instruction)
        )

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
