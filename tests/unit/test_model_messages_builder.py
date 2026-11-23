import unittest
from unittest.mock import Mock

from harness.builder.model_message_builder import ModelMessageBuilder
from harness.domain.message import Message
from harness.domain.tool_result import ToolResult


class ModelMessageBuilderTest(unittest.TestCase):
    def setUp(self):
        self.command_service = Mock()

    def test_preserves_history_and_renders_tool_results_without_mutation(self):
        result = ToolResult("read_file", "contents", id="result-1")
        tool_message = Message(
            role="user",
            type="tool_result",
            content="original content",
            tool_results=(result,)
        )
        messages = [Message(role="user", content="Read file"), tool_message]

        model_messages = ModelMessageBuilder().create_model_messages(messages, None, self.command_service)

        self.assertIs(model_messages[0], messages[0])
        self.assertIsNot(model_messages[1], tool_message)
        self.assertEqual(tool_message.content, "original content")
        self.assertIn("Tool result ID: result-1", model_messages[1].content)
        self.assertIn("contents", model_messages[1].content)

    def test_default_context_truncates_large_results(self):
        result = ToolResult("bash", "abcdefghij", id="result-1")
        message = Message(role="user", content="result", tool_results=(result,), type="tool_result")

        model_messages = ModelMessageBuilder(max_tool_result_chars=5).create_model_messages(
            [message],
            None,
            self.command_service
        )

        self.assertIn("[tool result truncated: 5 characters omitted]", model_messages[0].content)
        self.assertEqual(result.output, "abcdefghij")

    def test_prepare_new_messages_renders_only_new_tool_results(self):
        tool_call = Message(role="assistant", type="tool_call", content="Tool call")
        result = ToolResult("bash", "abcdefghij", id="result-1")
        tool_result = Message(
            role="user",
            type="tool_result",
            content="original result",
            tool_results=(result,)
        )

        prepared = ModelMessageBuilder(max_tool_result_chars=5).prepare_new_messages(
            [tool_call, tool_result]
        )

        self.assertIs(prepared[0], tool_call)
        self.assertIsNot(prepared[1], tool_result)
        self.assertEqual(tool_result.content, "original result")
        self.assertIn("[tool result truncated: 5 characters omitted]", prepared[1].content)

    def test_requested_previous_result_exposes_complete_output(self):
        result = ToolResult("bash", "abcdefghij", id="result-1")
        message = Message(role="user", content="result", tool_results=(result,), type="tool_result")
        builder = ModelMessageBuilder(max_tool_result_chars=5)
        model_messages = builder.create_model_messages([message], None, self.command_service)

        updated = builder.update_model_messages_by_tool_result_output_requests_ids(
            model_messages,
            ["result-1"]
        )

        self.assertIn("abcdefghij", updated[0].content)
        self.assertNotIn("truncated", updated[0].content)
        self.assertEqual(updated[0].tool_results, (result,))

    def test_empty_and_unknown_output_requests_leave_context_unchanged(self):
        result = ToolResult("bash", "output", id="result-1")
        message = Message(role="user", content="result", tool_results=(result,), type="tool_result")
        builder = ModelMessageBuilder()
        model_messages = builder.create_model_messages([message], None, self.command_service)

        self.assertIs(
            builder.update_model_messages_by_tool_result_output_requests_ids(model_messages, []),
            model_messages
        )
        self.assertIs(
            builder.update_model_messages_by_tool_result_output_requests_ids(model_messages, ["unknown"]),
            model_messages
        )

    def test_command_context_is_appended_after_conversation(self):
        parsed_command = Mock()
        command_message = Message(role="system", type="command_instruction", content="Command")
        self.command_service.prepare_command_context.return_value = command_message
        conversation = [Message(role="user", content="Run command")]

        model_messages = ModelMessageBuilder().create_model_messages(
            conversation,
            parsed_command,
            self.command_service
        )

        self.assertEqual(model_messages, [*conversation, command_message])
        self.command_service.prepare_command_context.assert_called_once_with(parsed_command)

    def test_invalid_configured_limit_is_rejected(self):
        for value in (0, -1, "invalid"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ModelMessageBuilder(max_tool_result_chars=value)


if __name__ == "__main__":
    unittest.main()
