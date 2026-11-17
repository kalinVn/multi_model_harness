import unittest
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.config.response.command_response_config import COMMAND_RESPONSE_FORMAT_INSTRUCTIONS
from harness.config.tool_usage_config import TOOL_USAGE_INSTRUCTIONS
from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.models.errors import ContextWindowExceeded
from harness.models.request import Request
from harness.models.response import ModelResponse
from harness.session_manager import SessionManager
from tests.unit.model_client_mock import add_tool_result_summaries, allow_context


class MainOrchestratorToolServiceIntegrationTest(unittest.TestCase):
    def create_orchestrator(self, client: Mock, on_tool_result=None) -> MainOrchestrator:
        side_effect = client.generate.side_effect
        if side_effect is not None and not callable(side_effect):
            def generate(messages, tools=None):
                response = next(side_effect)
                if not response.tool_calls:
                    response = add_tool_result_summaries(response, messages)

                return response

            client.generate.side_effect = generate

        with patch.object(
            SessionManager,
            "_load_system_prompt",
            return_value="Instructions"
        ):
            return MainOrchestrator(allow_context(client), on_tool_result=on_tool_result)

    def test_tool_service_reuses_orchestrator_dependencies(self):
        callback = Mock()
        runner = self.create_orchestrator(Mock(), callback)

        self.assertIs(runner._tool_service._tool_registry, runner._tool_registry)
        self.assertIs(
            runner._tool_service._model_message_builder,
            runner._model_messages_builder,
        )
        self.assertIs(runner._tool_service._on_tool_result, callback)

    def test_session_starts_with_combined_system_message(self):
        runner = self.create_orchestrator(Mock())

        messages = runner._session_manager.current_session.messages

        self.assertEqual(len(messages), 1)
        system_instruction = messages[0]
        self.assertEqual(system_instruction.role, "system")
        self.assertEqual(system_instruction.type, "system_instruction")
        self.assertEqual(
            system_instruction.content,
            f"Instructions\n\n{TOOL_USAGE_INSTRUCTIONS}\n\n{COMMAND_RESPONSE_FORMAT_INSTRUCTIONS}"
        )

    def test_normal_response_is_added_to_session_and_returned(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text="Hello")
        runner = self.create_orchestrator(client)

        result = runner.handle(Request.create("Hi"))

        self.assertEqual(result, "Hello")
        self.assertTrue(client.generate.call_args.kwargs["tools"])
        self.assertEqual(
            runner._session_manager.current_session.messages[-2].type,
            "user_message"
        )
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content="Hello", type="assistant_message")
        )

    def test_context_validation_uses_each_generated_request(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})]),
            ModelResponse(text="Done")
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(return_value="contents")

        self.assertEqual(runner.handle(Request.create("Read README.md")), "Done")

        self.assertEqual(client.count_tokens.call_count, client.generate.call_count)
        self.assertEqual(client.get_context_limits.call_count, client.generate.call_count)
        for count_call, generate_call in zip(client.count_tokens.call_args_list, client.generate.call_args_list):
            self.assertEqual(count_call.args[0], generate_call.args[0])
            self.assertEqual(count_call.args[1], generate_call.kwargs["tools"])

    def test_context_validation_rejects_request_before_generation(self):
        client = Mock()
        runner = self.create_orchestrator(client)
        client.count_tokens.return_value = 901
        client.get_context_limits.return_value = ModelContextLimits("test-model", 1_000, 100)

        with self.assertRaises(ContextWindowExceeded):
            runner.handle(Request.create("Continue"))

        client.generate.assert_not_called()

    def test_unknown_command_returns_message_without_calling_model(self):
        client = Mock()
        runner = self.create_orchestrator(client)

        result = runner.handle(Request.create("execute command missing-command"))

        self.assertEqual(result, "Unknown command: missing-command")
        client.generate.assert_not_called()
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )

    def test_command_summary_precedes_final_answer(self):
        client = Mock()
        client.generate.return_value = ModelResponse(
            text=(
                '{"answer": "Done", '
                '"command_summary": "Reviewed the project."}'
            )
        )
        runner = self.create_orchestrator(client)

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=Message(role="system", content="Command instructions"),
        ):
            result = runner.handle(Request.create("execute command review"))

        self.assertEqual(result, "Done")
        self.assertEqual(
            runner._session_manager.current_session.messages[-2:],
            [
                Message(
                    role="system",
                    content=(
                        "Command execution summary: review was executed. Result: "
                        "Reviewed the project."
                    ),
                    type="command_instruction"
                ),
                Message(role="assistant", content="Done", type="assistant_message")
            ],
        )

    def test_command_without_declared_tools_disables_tool_calls(self):
        client = Mock()
        client.generate.return_value = ModelResponse(
            text=(
                '{"answer": "Hello", '
                '"command_summary": "The hello command was acknowledged."}'
            )
        )
        runner = self.create_orchestrator(client)
        command_context = Message(
            role="system",
            content="Hello command instructions",
            available_tool_names=()
        )

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context
        ):
            result = runner.handle(Request.create("execute command hello"))

        self.assertEqual(result, "Hello")
        self.assertEqual(client.generate.call_args.kwargs["tools"], [])

    def test_command_retry_permissions_do_not_leak_to_next_request(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(
                text=(
                    '{"answer": "Hello", '
                    '"command_summary": "The command completed."}'
                )
            ),
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})]),
            ModelResponse(text="Done")
        ]
        runner = self.create_orchestrator(client)
        command_context = Message(
            role="system",
            content="Command instructions",
            available_tool_names=("read_file",)
        )

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context
        ):
            self.assertEqual(runner.handle(Request.create("execute command hello")), "Hello")

        runner._tool_registry.execute = Mock(return_value="contents")

        self.assertEqual(runner.handle(Request.create("Read README.md")), "Done")
        self.assertEqual(
            [tool["name"] for tool in client.generate.call_args_list[0].kwargs["tools"]],
            ["read_file"]
        )
        self.assertEqual(client.generate.call_args_list[1].kwargs["tools"], [])
        self.assertTrue(client.generate.call_args_list[2].kwargs["tools"])
        runner._tool_registry.execute.assert_called_once_with(
            "read_file",
            {"paths": ["README.md"]}
        )

    def test_tool_messages_keep_execution_order_and_final_response(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[
                    ToolCall("read_file", {"paths": ["first.txt"]}),
                    ToolCall("bash", {"commands": ["pwd"]}),
                ]
            ),
            ModelResponse(text="Done"),
        ]
        callback = Mock()
        runner = self.create_orchestrator(client, callback)
        session = runner._session_manager.current_session

        def execute(name, _arguments):
            self.assertTrue(session.messages[-1].content.startswith("Raw tool calls:"))
            self.assertFalse(session.messages[-1].tool_results)
            return f"{name} output"

        runner._tool_registry.execute = Mock(side_effect=execute)

        result = runner.handle(Request.create("Inspect the project"))

        self.assertEqual(result, "Done")
        self.assertEqual(runner._tool_registry.execute.call_count, 2)
        self.assertEqual(callback.call_count, 2)
        tool_call_index = next(
            index
            for index, message in enumerate(session.messages)
            if message.content.startswith("Raw tool calls:")
        )
        tool_result_index = next(
            index
            for index, message in enumerate(session.messages)
            if message.tool_results
        )
        self.assertLess(tool_call_index, tool_result_index)
        self.assertEqual(len(session.messages[tool_result_index].tool_results), 2)
        self.assertEqual(
            session.messages[-1],
            Message(role="assistant", content="Done", type="assistant_message")
        )

    def test_tool_execution_limit_is_preserved(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file")]),
            ModelResponse(tool_calls=[ToolCall("read_file")]),
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(return_value="output")

        with patch.object(MainOrchestrator, "MAX_TOOL_STEPS", 1):
            result = runner.handle(Request.create("Continue"))

        self.assertEqual(result, "Maximum tool execution steps exceeded.")
        runner._tool_registry.execute.assert_called_once_with("read_file", {})
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )

    def test_registered_tool_unavailable_for_request_is_rejected_before_execution(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(tool_calls=[ToolCall("read_file")]),
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock()

        with (
            patch(
                "harness.service.command_service.get_command_message_obj",
                return_value=Message(role="system", content="Command instructions")
            ),
            self.assertRaisesRegex(ValueError, "Model returned an unavailable tool")
        ):
            runner.handle(Request.create("execute command review"))

        self.assertTrue(client.generate.call_args_list[0].kwargs["tools"])
        self.assertEqual(client.generate.call_args_list[1].kwargs["tools"], [])
        runner._tool_registry.execute.assert_not_called()

    def test_command_response_retry_limit_and_final_result_are_preserved(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(text="still invalid"),
        ]
        runner = self.create_orchestrator(client)

        with (
            patch.object(MainOrchestrator, "MAX_COMMAND_RESPONSE_RETRIES", 1),
            patch(
                "harness.service.command_service.get_command_message_obj",
                return_value=Message(role="system", content="Command instructions")
            )
        ):
            result = runner.handle(Request.create("execute command review"))

        self.assertEqual(result, "Command response remained invalid after 1 retries.")
        self.assertEqual(client.generate.call_count, 2)
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )


if __name__ == "__main__":
    unittest.main()
