import unittest

from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_result import ToolResult


class SessionTest(unittest.TestCase):
    def test_get_tool_result_by_id_returns_original_result(self):
        first = ToolResult("read_file", "first output", id="first-id")
        second = ToolResult("bash", "second output", id="second-id")
        first_message = Message(
            role="user",
            content="Stored first result",
            tool_results=(first,),
        )
        second_message = Message(
            role="user",
            content="Stored second result",
            tool_results=(second,),
        )
        messages = [
            Message(role="assistant", content="Unrelated message"),
            first_message,
            second_message,
        ]
        session = Session(messages=messages)

        result = session.get_tool_result_by_id("second-id")

        self.assertIs(result, second)
        self.assertEqual(session.messages, messages)

    def test_get_tool_result_by_id_returns_none_for_unknown_id(self):
        result = ToolResult("read_file", "output", id="known-id")
        message = Message(role="user", content="Stored result", tool_results=(result,))
        session = Session(messages=[message])

        self.assertIsNone(session.get_tool_result_by_id("unknown-id"))
        self.assertEqual(session.messages, [message])


if __name__ == "__main__":
    unittest.main()
