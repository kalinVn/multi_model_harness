import unittest

from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_result import ToolResult
from harness.models.context_memory_summary import ContextMemorySummary


class SessionTest(unittest.TestCase):
    def test_get_tool_result_by_id_returns_original_complete_result(self):
        result = ToolResult("read_file", "complete output", id="result-1")
        session = Session(messages=[Message(
            role="user",
            type="tool_result",
            content="Rendered output",
            tool_results=(result,)
        )])

        self.assertIs(session.get_tool_result_by_id("result-1"), result)
        self.assertEqual(session.get_tool_result_by_id("result-1").output, "complete output")
        self.assertIsNone(session.get_tool_result_by_id("unknown"))

    def test_task_and_memory_state_is_isolated_between_sessions(self):
        first = Session()
        second = Session()
        first.begin_or_resume_task()
        first.context_memory_summary = ContextMemorySummary.empty(first.id)

        self.assertIsNotNone(first.active_task_start_index)
        self.assertIsNone(second.active_task_start_index)
        self.assertIsNotNone(first.context_memory_summary)
        self.assertIsNone(second.context_memory_summary)
        self.assertNotEqual(first.id, second.id)


if __name__ == "__main__":
    unittest.main()
