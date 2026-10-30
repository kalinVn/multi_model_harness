import os
from collections.abc import Callable
from pathlib import Path
from harness.builder.command_response_format_context_builder import (
    build_command_response_retry_context,
)
from harness.domain.loop_state import LoopState
from harness.parser.command_response_parser import parse_command_response
from harness.loader.command_loader import (
    CommandLoader,
)
from harness.parser.command_parser import (
    ParsedCommand,
    parse_command,
)
from harness.resolver.command_resolver import (
    CommandResolver,
)
from harness.session_manager import (
    SessionManager,
)
from harness.models.request import Request
from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_result import ToolResult
from harness.service.command_service import CommandService
from harness.service.tool_service import ToolService
from harness.tools.tool_registry import (
    ToolRegistry,
)
from harness.tools.register_tools import (
    register_tools,
)
from harness.builder.model_message_builder import ModelMessageBuilder
from harness.builder.tool_parameters_builder import (
    build_tool_parameters,
)
from harness.models.model_client import (
    ModelClient,
)
from harness.models.response import ModelResponse


class MainOrchestrator:
    MAX_TOOL_STEPS = 20
    MAX_COMMAND_RESPONSE_RETRIES = 2
    MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS = 3
    def __init__(
        self,
        model_client: ModelClient,
        project_root: Path | None = None,
        on_tool_result: Callable[[ToolResult], None] | None = None,
        max_tool_steps: int | None = None,
        max_command_response_retries: int | None = None,
        max_tool_result_output_request_steps: int | None = None,
    ) -> None:
        self.MAX_TOOL_STEPS = self._read_non_negative_limit(
            "HARNESS_MAX_TOOL_STEPS",
            max_tool_steps,
            type(self).MAX_TOOL_STEPS,
        )
        self.MAX_COMMAND_RESPONSE_RETRIES = self._read_non_negative_limit(
            "HARNESS_MAX_COMMAND_RESPONSE_RETRIES",
            max_command_response_retries,
            type(self).MAX_COMMAND_RESPONSE_RETRIES,
        )
        self.MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS = self._read_non_negative_limit(
            "HARNESS_MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS",
            max_tool_result_output_request_steps,
            type(self).MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS,
        )
        self._model_client = model_client
        self._model_messages_builder = ModelMessageBuilder()
        self._on_tool_result = on_tool_result
        self._project_root = (
            project_root or Path.cwd()
        )
        commands_directory = (
            self._project_root
            / ".caisa"
            / "commands"
        )
        self._command_resolver = CommandResolver(commands_directory)
        self._command_loader = CommandLoader()
        self._tool_registry = ToolRegistry()

        register_tools(self._tool_registry, working_directory=self._project_root)
        self._tool_parameters = build_tool_parameters(
            self._tool_registry.list_tools()
        )

        self._command_service = CommandService(
            command_resolver=self._command_resolver,
            command_loader=self._command_loader,
            tool_registry=self._tool_registry,
        )
        self._tool_service = ToolService(
            tool_registry=self._tool_registry,
            model_message_builder=self._model_messages_builder,
            on_tool_result=self._on_tool_result,
        )
        self._session_manager = SessionManager(
            project_root=self._project_root,
            tool_registry=self._tool_registry,
        )
        self._session_manager.create_session()

    @staticmethod
    def _read_non_negative_limit(
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
            raise ValueError(
                f"{environment_name} must be a non-negative integer."
            ) from error
        if value < 0:
            raise ValueError(f"{environment_name} must be a non-negative integer.")
        return value

    def handle(
        self,
        request: Request,
    ) -> str:
        state = LoopState()

        if not request.message.strip():
            return "Please enter a message."
        
        session = self._session_manager.current_session
        user_message = Message(role="user", content=request.message)
        session.add_message(user_message)
        state.parsed_command = parse_command(request.message)

      
        state.model_messages = self._model_messages_builder.create_model_messages(
            session.messages,
            state.parsed_command,
            self._command_service,
        )

        return self._loop(state, session)
   

    def _loop(self, state, session):

        tools = self._tool_service.get_available_tools(self._tool_parameters, state.model_messages)
        
        state.response = self._model_client.generate(state.model_messages, tools=tools)
                    
        session.apply_tool_result_summaries(state.response.tool_result_summaries)
        requested_tool_result_ids = self._tool_service.get_requested_tool_result_ids(
            session,
            state.response,
        )

        if not state.response.tool_calls: 
            return self._handle_no_tool_calls(state, session, requested_tool_result_ids)
        else:
            return self._handle_tool_calls(state, session, requested_tool_result_ids)


    def _handle_no_tool_calls(self, state, session ,requested_tool_result_ids):
            updated_model_messages = (
                self._tool_service.update_model_messages_by_requested_tool_result_ids(
                    state.model_messages,
                    requested_tool_result_ids,
                )
            )

            if updated_model_messages != state.model_messages:
                if state.tool_result_output_request_steps >= self.MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS:
                    message = (
                        "Maximum tool result output request steps "
                        "exceeded."
                    )
                    session.add_message(Message(role="assistant", content=message))

                    return message

                state.tool_result_output_request_steps += 1
                state.model_messages = updated_model_messages

                return self._loop(state, session)
                


            result = self._handle_response_without_tool_calls(
                session,
                state.response,
                state.parsed_command,
                state,
            )

            if isinstance(result, str):
                return result
            
            state.command_response_retries += 1
            state.model_messages = result

            return self._loop(state, session)

            
    def _handle_tool_calls(self, state, session, requested_tool_result_ids):

        if state.tool_steps >= self.MAX_TOOL_STEPS:

            message = "Maximum tool execution steps exceeded."
            session.add_message(Message(role="assistant", content=message))

            return message
        
        tool_call_message = self._tool_service.prepare_tool_call_message(state.response.tool_calls,)
        session.add_message(tool_call_message)

        tool_results = self._tool_service.execute_tool_calls(state.response.tool_calls)

        tool_result_message = self._tool_service.prepare_tool_result_message(
            tool_results,
        )
        session.add_message(tool_result_message)

        state.tool_steps += 1
        
        state.model_messages = self._model_messages_builder.create_model_messages(
            session.messages,
            state.parsed_command,
            self._command_service,
        )

        state.model_messages = (
            self._tool_service.update_model_messages_by_requested_tool_result_ids(
                state.model_messages,
                requested_tool_result_ids,
            )
        )

        return self._loop(state, session)

    def _handle_response_without_tool_calls(
        self,
        session: Session,
        response: ModelResponse,
        parsed_command: ParsedCommand | None,
        state,
    ) -> str | list[Message]:
        """Return the final response or model context for a retry.

        str: The final response to the user, such as "The file was read
        successfully."
        list[Message]: New context containing an instruction to fix the JSON;
        it is sent to the model during the next iteration.
        """
        # If there is no parsed command, save and return the response text
        # without any command-specific processing.
        if parsed_command is None:
            session.add_message(Message(role="assistant", content=response.text))
            return response.text

        # Parse the response and verify that it has the expected structure.
        # For example, if the response is JSON with status: "ok", verify that
        # status is exactly "ok" rather than "error".
        parsed_response = parse_command_response(response.text)

        # A non-None parsed response is valid and can be saved to the session.
        if parsed_response is not None:

            answer, command_summary = parsed_response

            # Save command_summary as a system message.
            command_summary_message = (
                self._command_service.prepare_command_summary_message(
                    parsed_command,
                    command_summary,
                )
            )
            session.add_message(command_summary_message)
            session.add_message(Message(role="assistant", content=answer))

            # Return the final text intended for the user.
            return answer

        # Once all response-correction attempts are exhausted, save the error
        # message in the session history and return it to the user.
        if state.command_response_retries >= self.MAX_COMMAND_RESPONSE_RETRIES:
            message = (
                "Command response remained invalid after "
                f"{self.MAX_COMMAND_RESPONSE_RETRIES} retries."
            )

            session.add_message(Message(role="assistant", content=message))

            return message


        model_messages = self._model_messages_builder.create_model_messages(
            session.messages,
            state.parsed_command,
            self._command_service,
            include_tools=False,
        )
        model_messages.append(build_command_response_retry_context())

        return model_messages
