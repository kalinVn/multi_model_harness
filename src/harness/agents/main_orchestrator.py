from collections.abc import Callable
from pathlib import Path

from harness.builder.command_response_format_context_builder import (
    build_command_response_retry_context,
)
from harness.builder.model_message_builder import ModelMessageBuilder
from harness.builder.tool_parameters_builder import build_tool_parameters
from harness.domain.loop_state import LoopState
from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_result import ToolResult
from harness.loader.agent_loader import AgentLoader
from harness.loader.command_loader import CommandLoader
from harness.loader.skill_loader import SkillLoader
from harness.models.errors import UnknownCommandError
from harness.models.model_client import ModelClient
from harness.models.request import Request
from harness.models.response import ModelResponse
from harness.models.tool_definition import ToolDefinition
from harness.parser.command_parser import ParsedCommand, parse_command
from harness.parser.command_response_parser import parse_command_response
from harness.resolver.command_resolver import CommandResolver
from harness.registry.agent_registry import AgentRegistry
from harness.service.command_service import CommandService
from harness.service.context_manager import ContextManager
from harness.service.tool_service import ToolService
from harness.session_manager import SessionManager
from harness.skills.skill_registry import SkillRegistry
from harness.tools.register_tools import register_tools
from harness.tools.tool_registry import ToolRegistry
from harness.validators.tool_call_validator import ToolCallValidator


class MainOrchestrator:
    MAX_TOOL_STEPS = 60
    MAX_COMMAND_RESPONSE_RETRIES = 2
    MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS = 3

    def __init__(
        self,
        model_client: ModelClient,
        project_root: Path | None = None,
        on_tool_result: Callable[[ToolResult], None] | None = None
    ) -> None:
        self._model_client = model_client
        self._context_manager = ContextManager()
        self._model_messages_builder = ModelMessageBuilder()
        self._on_tool_result = on_tool_result
        self._project_root = project_root or Path.cwd()
        commands_directory = self._project_root / ".caisa" / "commands"
        agents_directory = self._project_root / ".caisa" / "agents"
        skills_directory = self._project_root / ".caisa" / "skills"
        self._command_resolver = CommandResolver(commands_directory)
        self._command_loader = CommandLoader()
        self._tool_registry = ToolRegistry()

        register_tools(self._tool_registry, working_directory=self._project_root)
        self._tool_parameters = build_tool_parameters(self._tool_registry.list_tools())

        self._command_service = CommandService(
            command_resolver=self._command_resolver,
            command_loader=self._command_loader,
            tool_registry=self._tool_registry
        )
        self._tool_service = ToolService(
            tool_registry=self._tool_registry,
            model_message_builder=self._model_messages_builder,
            on_tool_result=self._on_tool_result
        )
        self._skill_registry = SkillRegistry()
        skills = SkillLoader().load_directory(skills_directory)

        for skill in skills:
            self._skill_registry.register(skill)

        agents = AgentLoader().load_directory(agents_directory)
        self._agent_registry = AgentRegistry(
            model_client=self._model_client,
            tool_service=self._tool_service,
            tool_definitions=self._tool_parameters,
            skill_registry=self._skill_registry,
            agent_definitions=agents,
            project_root=self._project_root
        )
        self._planner = self._agent_registry.get("planner")
        self._context_memory_agent = self._agent_registry.get("context_memory")
        self._session_manager = SessionManager(
            project_root=self._project_root,
            tool_registry=self._tool_registry
        )
        self._session_manager.create_session()

    def handle(self, request: Request) -> str:
        state = LoopState()

        if not request.message.strip():
            return "Please enter a message."

        session = self._session_manager.current_session
        session.begin_or_resume_task()
        user_message = Message(role="user", type="user_message", content=request.message)
        session.add_message(user_message)
        state.parsed_command = parse_command(request.message)

        try:
            state.model_messages = self._model_messages_builder.create_model_messages(
                session.get_model_context_messages(),
                state.parsed_command,
                self._command_service
            )
        except UnknownCommandError as error:
            message = str(error)
            session.add_message(Message(role="assistant", type="error", content=message))

            return message

        result = self._loop(state, session)
        state.execution_finished = True
        session.task_status = state.response.task_status if state.response is not None else None

        if self._is_task_completed(state, session):
            self._update_context_memory(session)
        elif session.task_status == "completed":
            session.task_status = "in_progress"
            session.completion_uncertainty = "Reported completion conflicts with active execution evidence."
        else:
            session.completion_uncertainty = None

        return result

    @staticmethod
    def _is_task_completed(state: LoopState, session: Session) -> bool:
        if not state.execution_finished or state.response is None:
            return False

        if state.response.task_status != "completed" or state.response.tool_calls:
            return False

        task_messages = session.get_active_task_messages()
        if not task_messages:
            return False

        final_message = task_messages[-1]
        if final_message.type != "assistant_message" or not final_message.content.strip():
            return False

        return True

    def _update_context_memory(self, session: Session) -> None:
        if session.memory_update_completed:
            return

        task_messages = session.get_active_task_messages()
        tool_results = [
            tool_result
            for message in task_messages
            for tool_result in message.tool_results
        ]

        try:
            if session.context_memory_summary is None:
                summary = self._context_memory_agent.create_summary(session.id, task_messages)
            else:
                summary = self._context_memory_agent.update_summary(
                    session.context_memory_summary,
                    task_messages,
                    tool_results
                )
        except Exception as error:
            session.memory_update_error = str(error)
            session.memory_update_completed = False

            return

        session.mark_memory_updated(summary)

    def _loop(self, state: LoopState, session: Session, available_tools: list[ToolDefinition] | None = None) -> str:
        if available_tools is None:
            available_tools = self._tool_service.get_available_tools(
                self._tool_parameters,
                state.model_messages
            )

        self._context_manager.validate(
            messages=state.model_messages,
            tools=available_tools,
            model_client=self._model_client
        )

        state.response = self._model_client.generate(
            state.model_messages,
            tools=available_tools
        )

        ToolCallValidator.validate(state.response.tool_calls, available_tools)

        requested_tool_result_ids = self._tool_service.get_requested_tool_result_ids(session, state.response)

        if not state.response.tool_calls:
            return self._handle_no_tool_calls(
                state,
                session,
                requested_tool_result_ids,
                available_tools
            )

        return self._handle_tool_calls(
            state,
            session,
            requested_tool_result_ids,
            available_tools
        )

    def _handle_no_tool_calls(
        self,
        state: LoopState,
        session: Session,
        requested_tool_result_ids: list[str],
        available_tools: list[ToolDefinition]
    ) -> str:
        updated_model_messages = self._tool_service.update_model_messages_by_requested_tool_result_ids(
            state.model_messages,
            requested_tool_result_ids
        )

        if updated_model_messages != state.model_messages:
            if state.tool_result_output_request_steps >= self.MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS:
                message = "Maximum tool result output request steps exceeded."
                session.add_message(Message(role="assistant", type="error", content=message))

                return message

            state.tool_result_output_request_steps += 1
            state.model_messages = updated_model_messages

            return self._loop(state, session, available_tools)

        result = self._process_response(
            session,
            state.response,
            state.parsed_command,
            state
        )

        if isinstance(result, str):
            return result

        state.command_response_retries += 1
        state.model_messages = result

        return self._loop(state, session, available_tools=[])

    def _handle_tool_calls(
        self,
        state: LoopState,
        session: Session,
        requested_tool_result_ids: list[str],
        available_tools: list[ToolDefinition]
    ) -> str:
        if state.tool_steps >= self.MAX_TOOL_STEPS:
            message = "Maximum tool execution steps exceeded."
            session.add_message(Message(role="assistant", type="error", content=message))

            return message

        tool_call_message = self._tool_service.prepare_tool_call_message(state.response.tool_calls)
        session.add_message(tool_call_message)

        tool_results = self._tool_service.execute_tool_calls(state.response.tool_calls, available_tools)
        tool_result_message = self._tool_service.prepare_tool_result_message(tool_results)

        session.add_message(tool_result_message)
        state.tool_steps += 1

        new_model_messages = self._model_messages_builder.prepare_new_messages(
            [tool_call_message, tool_result_message]
        )
        state.model_messages.extend(new_model_messages)

        state.model_messages = self._tool_service.update_model_messages_by_requested_tool_result_ids(
            state.model_messages,
            requested_tool_result_ids
        )

        return self._loop(state, session, available_tools)

    def _process_response(
        self,
        session: Session,
        response: ModelResponse,
        parsed_command: ParsedCommand | None,
        state: LoopState
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
            session.add_message(Message(role="assistant", type="assistant_message", content=response.text))

            return response.text

        # Parse the response and verify that it has the expected structure.
        # For example, if the response is JSON with status: "ok", verify that
        # status is exactly "ok" rather than "error".
        parsed_response = parse_command_response(response.text)

        # A non-None parsed response is valid and can be saved to the session.
        if parsed_response is not None:
            session.add_message(Message(role="assistant", type="assistant_message", content=parsed_response))

            # Return the final text intended for the user.
            return parsed_response

        # Once all response-correction attempts are exhausted, save the error
        # message in the session history and return it to the user.
        if state.command_response_retries >= self.MAX_COMMAND_RESPONSE_RETRIES:
            message = (
                "Command response remained invalid after "
                f"{self.MAX_COMMAND_RESPONSE_RETRIES} retries."
            )

            session.add_message(Message(role="assistant", type="error", content=message))

            return message

        model_messages = list(state.model_messages)
        model_messages.append(build_command_response_retry_context())

        return model_messages
