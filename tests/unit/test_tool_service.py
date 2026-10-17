import unittest
from unittest.mock import Mock

from harness.builder.model_message_builder import ModelMessageBuilder
from harness.builder.tool_call_context_builder import build_tool_calls_context
from harness.builder.tool_result_context_builder import build_tool_results_context
from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.models.response import ModelResponse
from harness.service.tool_service import ToolService
from harness.tools.tool_registry import ToolRegistry


class ToolServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool_registry = Mock(spec=ToolRegistry)
        self.model_message_builder = Mock(spec=ModelMessageBuilder)

    def create_service(
        self,
        on_tool_result=None,
    ) -> ToolService:
        return ToolService(
            tool_registry=self.tool_registry,
            model_message_builder=self.model_message_builder,
            on_tool_result=on_tool_result,
        )

    def test_execute_tool_calls_returns_successful_results_in_order(self):
        self.tool_registry.execute.side_effect = ["first output", "second output"]
        tool_calls = [
            ToolCall("read_file", {"path": "first.txt"}),
            ToolCall("bash", {"command": "pwd"}),
        ]

        results = self.create_service().execute_tool_calls(tool_calls)

        self.assertEqual([result.name for result in results], ["read_file", "bash"])
        self.assertEqual(
            [result.output for result in results],
            ["first output", "second output"],
        )
        self.assertTrue(all(result.success for result in results))
        self.assertEqual(
            self.tool_registry.execute.call_args_list,
            [
                unittest.mock.call("read_file", {"path": "first.txt"}),
                unittest.mock.call("bash", {"command": "pwd"}),
            ],
        )

    def test_execute_tool_calls_converts_exceptions_to_failed_results(self):
        self.tool_registry.execute.side_effect = ValueError("missing file")

        results = self.create_service().execute_tool_calls(
            [ToolCall("read_file", {"path": "missing.txt"})]
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "read_file")
        self.assertEqual(results[0].output, "missing file")
        self.assertFalse(results[0].success)

    def test_execute_tool_calls_invokes_callback_for_each_result(self):
        callback = Mock()
        self.tool_registry.execute.side_effect = ["output", RuntimeError("failed")]

        results = self.create_service(callback).execute_tool_calls(
            [ToolCall("read_file"), ToolCall("bash")]
        )

        self.assertEqual(callback.call_count, 2)
        self.assertIs(callback.call_args_list[0].args[0], results[0])
        self.assertIs(callback.call_args_list[1].args[0], results[1])

    def test_get_requested_tool_result_ids_returns_only_valid_ids(self):
        first = ToolResult("read_file", "first", id="first-id")
        second = ToolResult("bash", "second", id="second-id")
        session = Session(
            messages=[
                Message(
                    role="user",
                    content="Stored results",
                    tool_results=(first, second),
                )
            ]
        )
        original_messages = list(session.messages)
        response = ModelResponse(
            tool_result_output_requests=["second-id", "unknown-id", "first-id"]
        )

        result_ids = self.create_service().get_requested_tool_result_ids(
            session,
            response,
        )

        self.assertEqual(result_ids, ["second-id", "first-id"])
        self.assertEqual(session.messages, original_messages)

    def test_update_model_messages_delegates_to_builder(self):
        model_messages = [Message(role="user", content="Summary")]
        updated_messages = [Message(role="user", content="Full output")]
        self.model_message_builder.update_model_messages_by_tool_result_output_requests_ids.return_value = (
            updated_messages
        )

        result = self.create_service().update_model_messages_by_requested_tool_result_ids(
            model_messages,
            ["result-id"],
        )

        self.assertIs(result, updated_messages)
        self.model_message_builder.update_model_messages_by_tool_result_output_requests_ids.assert_called_once_with(
            model_messages=model_messages,
            tool_result_output_requests=["result-id"],
        )

    def test_update_model_messages_returns_original_when_no_ids_requested(self):
        model_messages = [Message(role="user", content="Unchanged")]

        result = self.create_service().update_model_messages_by_requested_tool_result_ids(
            model_messages,
            [],
        )

        self.assertIs(result, model_messages)
        self.model_message_builder.update_model_messages_by_tool_result_output_requests_ids.assert_not_called()

    def test_prepare_tool_response_messages_does_not_modify_session(self):
        tool_calls = [ToolCall("read_file", {"path": "config.py"})]
        tool_results = [ToolResult("read_file", "configuration", id="result-id")]
        existing_message = Message(role="user", content="Existing history")
        session = Session(messages=[existing_message])

        tool_call_message, tool_result_message = (
            self.create_service().prepare_tool_response_messages(
                tool_calls,
                tool_results,
            )
        )

        self.assertEqual(
            tool_call_message,
            Message(role="assistant", content=build_tool_calls_context(tool_calls)),
        )
        self.assertEqual(tool_result_message.role, "user")
        self.assertEqual(
            tool_result_message.content,
            build_tool_results_context(tool_results),
        )
        self.assertEqual(tool_result_message.tool_results, tuple(tool_results))
        self.assertEqual(session.messages, [existing_message])


if __name__ == "__main__":
    unittest.main()
