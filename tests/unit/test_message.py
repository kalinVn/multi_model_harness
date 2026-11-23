import unittest
from typing import get_args

from harness.domain.message import Message, MessageType
from harness.domain.tool_result import ToolResult


class MessageTest(unittest.TestCase):
    def test_message_type_supports_all_structured_values(self):
        self.assertEqual(
            set(get_args(MessageType)),
            {
                "user_message",
                "assistant_message",
                "system_instruction",
                "tools_instruction",
                "command_instruction",
                "tool_call",
                "tool_result",
                "tool_result_summary",
                "error"
            }
        )

    def test_type_is_optional_and_preserves_positional_compatibility(self):
        result = ToolResult("read_file", "output", id="result-id")
        message = Message("user", "Stored result", (result,), ("result-id",), ("read_file",))

        self.assertIsNone(message.type)
        self.assertEqual(message.tool_results, (result,))
        self.assertEqual(message.tool_result_output_requests, ("result-id",))
        self.assertEqual(message.available_tool_names, ("read_file",))

    def test_message_accepts_explicit_type(self):
        message = Message(role="user", content="Hello", type="user_message")

        self.assertEqual(message.type, "user_message")

    def test_has_tool_results(self):
        without_results = Message(role="user", content="No results")
        with_results = Message(
            role="user",
            content="Stored result",
            tool_results=(ToolResult("read_file", "output", id="result-id"),),
        )

        self.assertFalse(without_results.has_tool_results())
        self.assertTrue(with_results.has_tool_results())

    def test_has_requested_tool_results(self):
        message = Message(
            role="user",
            content="Stored results",
            tool_results=(
                ToolResult("read_file", "first output", id="first-id"),
                ToolResult("bash", "second output", id="second-id"),
            ),
        )

        self.assertTrue(message.has_requested_tool_results(["second-id"]))
        self.assertFalse(message.has_requested_tool_results(["unknown-id"]))
        self.assertFalse(message.has_requested_tool_results([]))

    def test_contains_type(self):
        messages = [
            Message(role="user", content="Task", type="user_message"),
            Message(role="system", content="Summarize", type="tool_result_summary")
        ]

        self.assertTrue(Message.contains_type(messages, "tool_result_summary"))
        self.assertFalse(Message.contains_type(messages, "error"))
        self.assertFalse(Message.contains_type([], "tool_result_summary"))

    def test_contains_non_system_message(self):
        system_messages = [Message(role="system", content="Rules")]
        conversation = [Message(role="system", content="Rules"), Message(role="user", content="Task")]

        self.assertFalse(Message.contains_non_system_message(system_messages))
        self.assertFalse(Message.contains_non_system_message([]))
        self.assertTrue(Message.contains_non_system_message(conversation))

    def test_get_last_available_tool_names(self):
        messages = [
            Message(role="system", content="First", available_tool_names=("read_file",)),
            Message(role="user", content="Task"),
            Message(role="system", content="Second", available_tool_names=("bash",))
        ]

        self.assertEqual(Message.get_last_available_tool_names(messages), ("bash",))
        self.assertIsNone(Message.get_last_available_tool_names([Message(role="user", content="Task")]))
        self.assertIsNone(Message.get_last_available_tool_names([]))


if __name__ == "__main__":
    unittest.main()
