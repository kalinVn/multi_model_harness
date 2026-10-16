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

    def create_model_messages(
        self,
        session_messages: list[Message],
        parsed_command: ParsedCommand | None,
        command_service: CommandService,
        include_tools: bool = True,
    ) -> list[Message]:
        """Добавя системно съобщение само за текущия ход, което указва на модела как да форматира
        финалния отговор при команда. Това съобщение не се записва в историята на сесията и важи
        само за конкретното извикване.
        Може да добавим – например, при команда за създаване на файл, инструктираме модела
        финалният отговор да е JSON с полета answer и command_summary. Това важи само за този ход
        и не променя историята.
        """
        response_format_instruction: list[Message] = []
        command_message = None

        # Добавяме системно съобщение само за текущия ход, което указва на модела как да форматира
        # финалния отговор при команда. Това съобщение не се записва в историята на сесията и важи
        # само за конкретното извикване.
        # Може да добавим – например, при команда за създаване на файл, инструктираме модела
        # финалният отговор да е JSON с полета answer и command_summary. Това важи само за този ход
        # и не променя историята.
        if parsed_command is not None:
            response_format_instruction.append(
                build_command_response_format_context()
            )
            command_message = command_service.prepare_command_context(
                parsed_command
            )

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

        model_messages = self.compose_model_messages(
            messages_for_model + response_format_instruction
        )
        if command_message is not None:
            model_messages.append(command_message)

        return model_messages

    def compose_model_messages(self, messages: list[Message]) -> list[Message]:
        """Обхожда всички съобщения и подготвя контекста за модела.

        За съобщенията с tool_results използва summary, ако съществува,
        или пълния output, ако липсва.
        Събира ID-тата на tool results без summary и добавя
        инструкции към модела за тяхното обобщаване.
        Не променя оригиналните съобщения от сесията.
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
        """Обновява само контекстите с изрично поискани пълни tool outputs.

        Оригиналните съобщения от сесията остават непроменени.
        """
        if not tool_result_output_requests:
            return model_messages

        updated_model_messages: list[Message] = []
        model_messages_updated = False

        for message in model_messages:

            if  not message.has_tool_results() or not message.has_requested_tool_results(tool_result_output_requests):
               
                updated_model_messages.append(message)
                continue

            updated_content = build_tool_results_context(list(message.tool_results), tool_result_output_requests)

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
        """Обхожда всички съобщения и проверява дали съдържат tool_results.

        Ако има tool_results, обхожда всеки ToolResult.
        Ако ToolResult има валидно summary, използва него вместо пълния output.
        Ако няма summary, използва пълния output и добавя result.id
        в tool_result_ids_to_summarize за последващо обобщаване.
        Добавя обработеното съобщение в model_messages.
        Ако съобщението няма tool_results, го добавя без промяна.
        Не променя оригиналните съобщения от сесията.
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
        """Проверява дали има ToolResult ID-та, които трябва да бъдат обобщени.

        Използва вече събраните ID-та в tool_result_ids_to_summarize.
        Ако има такива ID-та, добавя към model_messages инструкция,
        която указва на модела за кои ToolResult-и трябва да генерира summary.
        Не обхожда повторно всички съобщения и не обработва tool output.
        Не променя оригиналните съобщения в сесията.
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
