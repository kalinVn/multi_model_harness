import os
from dataclasses import replace

from harness.builder.command_response_format_context_builder import (
    build_command_response_format_context,
)
from harness.builder.tool_result_context_builder import (
    build_tool_results_context,
    has_tool_result_summary,
)
from harness.builder.tools_schema_builder import TOOLS_CONTEXT_HEADER
from harness.domain.message import Message
from harness.parser.command_parser import ParsedCommand
from harness.service.command_service import CommandService


class ModelMessageBuilder:
    DEFAULT_MAX_HISTORY_MESSAGES = 40
    DEFAULT_MAX_TOOL_RESULT_CHARS = 12_000

    def __init__(
        self,
        max_history_messages: int | None = None,
        max_tool_result_chars: int | None = None,
    ) -> None:
        self._max_history_messages = self._read_positive_limit(
            "HARNESS_MAX_HISTORY_MESSAGES",
            max_history_messages,
            self.DEFAULT_MAX_HISTORY_MESSAGES,
        )
        self._max_tool_result_chars = self._read_positive_limit(
            "HARNESS_MAX_TOOL_RESULT_CHARS",
            max_tool_result_chars,
            self.DEFAULT_MAX_TOOL_RESULT_CHARS,
        )

    def create_model_messages(
        self,
        session_messages: list[Message],
        parsed_command: ParsedCommand | None,
        command_service: CommandService,
        include_tools: bool = True,
    ) -> list[Message]:
        """Добавя системно съобщение за текущия ход, което указва на модела как
        да форматира крайния отговор за команда. Съобщението не се запазва
        в историята на сесията и важи само за текущото извикване.
        Например при команда за създаване на файл можем да укажем на модела
        да върне крайния отговор като JSON с полета answer и command_summary.
        Това важи само за текущия ход и не променя историята.
        """
        response_format_instruction: list[Message] = []
        command_message = None

        # Добавяме системно съобщение за текущия ход, което указва на модела как
        # да форматира крайния отговор за команда. Съобщението не се запазва
        # в историята на сесията и важи само за това извикване. Например
        # команда за създаване на файл може да изисква JSON с полета answer и
        # command_summary, без да променя историята.
        if parsed_command is not None:
            response_format_instruction.append(build_command_response_format_context())
            command_message = command_service.prepare_command_context(parsed_command)

        messages_for_model = session_messages
        if not include_tools:
            messages_for_model = [
                message
                for message in session_messages
                if not (
                    message.role == "system"
                    and message.content.startswith(TOOLS_CONTEXT_HEADER)
                )
            ]

        messages_for_model = self._limit_history(messages_for_model)
        model_messages = self.compose_model_messages(
            messages_for_model + response_format_instruction
        )
        
        if command_message is not None:
            model_messages.append(command_message)

        return model_messages

    def compose_model_messages(self, messages: list[Message]) -> list[Message]:
        """Обработва всички съобщения и подготвя контекста на модела.

        За съобщения с tool_results използва обобщението, когато съществува,
        или пълния изход в противен случай. Събира ID на резултатите без
        обобщение и добавя инструкции към модела да ги обобщи. Оригиналните
        съобщения на сесията не се променят.
        """
        model_messages: list[Message] = []

        tool_result_ids_to_summarize = self._add_tool_results_to_model_messages(
            messages,
            model_messages,
        )

        self._add_tool_result_summary_instructions_to_model_messages(
            model_messages,
            tool_result_ids_to_summarize,
        )

        return model_messages

    def update_model_messages_by_tool_result_output_requests_ids(
        self,
        model_messages: list[Message],
        tool_result_output_requests: list[str],
    ) -> list[Message]:
        """Актуализира само контекстите с изрично заявен пълен изход от инструменти.

        Оригиналните съобщения на сесията остават непроменени.
        """
        if not tool_result_output_requests:
            return model_messages

        updated_model_messages: list[Message] = []
        model_messages_updated = False

        for message in model_messages:

            if  not message.has_tool_results() or not message.has_requested_tool_results(tool_result_output_requests):
               
                updated_model_messages.append(message)
                continue

            updated_content = build_tool_results_context(
                list(message.tool_results),
                tool_result_output_requests,
                max_output_chars=self._max_tool_result_chars,
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
        model_messages: list[Message],
    ) -> list[str]:
        """Обработва всички съобщения и проверява дали съдържат tool_results.

        За съобщения с tool_results проверява всеки ToolResult. Използва валидно
        обобщение вместо пълния изход, когато е налично. В противен случай използва
        пълния изход и добавя result.id към tool_result_ids_to_summarize за последващо
        обобщаване. Добавя обработеното съобщение към model_messages. Съобщенията
        без tool_results се добавят непроменени. Оригиналните съобщения на сесията
        не се променят.
        """
        tool_result_ids_to_summarize: list[str] = []

        for message in messages:
            if message.has_tool_results():
                for tool_result in message.tool_results:
                    if not has_tool_result_summary(tool_result):
                        tool_result_ids_to_summarize.append(tool_result.id)

                model_messages.append(
                    Message(
                        role=message.role,
                        content=build_tool_results_context(
                            list(message.tool_results),
                            max_output_chars=self._max_tool_result_chars,
                        ),
                        tool_results=message.tool_results,
                    )
                )
            else:
                model_messages.append(message)

        return tool_result_ids_to_summarize

    def _add_tool_result_summary_instructions_to_model_messages(
        self,
        model_messages: list[Message],
        tool_result_ids_to_summarize: list[str],
    ) -> None:
        """Проверява дали има ID на ToolResult, които трябва да бъдат обобщени.

        Използва ID, вече събрани в tool_result_ids_to_summarize. Ако има такива,
        добавя инструкция към model_messages, която указва на модела кои ToolResults
        изискват обобщение. Не обхожда повторно всички съобщения и не обработва
        изхода от инструментите. Оригиналните съобщения на сесията не се променят.
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

        model_messages.append(Message(role="system", content=instruction))

    def _limit_history(self, messages: list[Message]) -> list[Message]:
        initial_system_count = 0
        for message in messages:
            if message.role != "system":
                break
            initial_system_count += 1

        initial_system_messages = messages[:initial_system_count]
        conversation = messages[initial_system_count:]
        if len(conversation) <= self._max_history_messages:
            return list(messages)

        recent_messages = conversation[-self._max_history_messages:]
        latest_user_request = next(
            (
                message
                for message in reversed(conversation)
                if message.role == "user" and not message.has_tool_results()
            ),
            None,
        )
        if self._max_history_messages > 1 and latest_user_request is not None and all(
            message is not latest_user_request for message in recent_messages
        ):
            recent_messages = [latest_user_request] + recent_messages[1:]

        return initial_system_messages + recent_messages

    @staticmethod
    def _read_positive_limit(
        environment_name: str,
        configured_value: int | None,
        default: int,
    ) -> int:
        raw_value: int | str = (
            configured_value
            if configured_value is not None
            else os.getenv(environment_name, str(default))
        )
        try:
            value = int(raw_value)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{environment_name} must be a positive integer.") from error
        if value < 1:
            raise ValueError(f"{environment_name} must be a positive integer.")
        return value
