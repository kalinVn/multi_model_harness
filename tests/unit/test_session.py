import unittest

from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_result import ToolResult
from harness.models.tool_result_summary import ToolResultSummary


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

    def test_get_missing_tool_result_summary_ids_returns_only_unsummarized_results(self):
        missing = ToolResult("read_file", "first output", id="missing-id")
        whitespace = ToolResult("bash", "second output", summary="   ", id="whitespace-id")
        summarized = ToolResult("read_file", "third output", summary="Saved summary.", id="summarized-id")
        session = Session(messages=[
            Message(role="user", content="Stored results", tool_results=(missing, whitespace, summarized))
        ])

        result_ids = session.get_missing_tool_result_summary_ids()

        self.assertEqual(result_ids, ["missing-id", "whitespace-id"])

    def test_apply_tool_result_summaries_ignores_unknown_empty_and_existing_summaries(self):
        result = ToolResult("bash", "complete output", id="result-id")
        session = Session(messages=[Message(role="user", content="Stored result", tool_results=(result,))])

        session.apply_tool_result_summaries([
            ToolResultSummary("unknown-id", "Unknown summary."),
            ToolResultSummary(result.id, "   ")
        ])

        self.assertEqual(result.summary, "")

        session.apply_tool_result_summaries([ToolResultSummary(result.id, "Saved summary.")])
        session.apply_tool_result_summaries([ToolResultSummary(result.id, "Replacement summary.")])

        self.assertEqual(result.summary, "Saved summary.")
        self.assertEqual(result.output, "complete output")


if __name__ == "__main__":
    unittest.main()
