import unittest

from harness.builder.tool_result_context_builder import build_tool_results_context
from harness.domain.tool_result import ToolResult


class ToolResultContextBuilderTest(unittest.TestCase):
    def test_context_contains_complete_result_metadata_and_output(self):
        result = ToolResult("read_file", "file contents", success=True, id="result-1")

        context = build_tool_results_context([result])

        self.assertIn("Tool result ID: result-1", context)
        self.assertIn("Tool: read_file", context)
        self.assertIn("Success: True", context)
        self.assertIn("Output:\nfile contents", context)

    def test_default_context_truncates_without_modifying_stored_output(self):
        result = ToolResult("bash", "abcdefghij", id="result-1")

        context = build_tool_results_context([result], max_output_chars=5)

        self.assertIn("abcde", context)
        self.assertIn("[tool result truncated: 5 characters omitted]", context)
        self.assertEqual(result.output, "abcdefghij")

    def test_requested_result_uses_complete_stored_output(self):
        result = ToolResult("bash", "abcdefghij", id="result-1")

        context = build_tool_results_context([result], ["result-1"], max_output_chars=5)

        self.assertIn("abcdefghij", context)
        self.assertNotIn("truncated", context)

    def test_multiple_results_keep_execution_order(self):
        first = ToolResult("read_file", "first output", id="first")
        second = ToolResult("bash", "second output", success=False, id="second")

        context = build_tool_results_context([first, second])

        self.assertLess(context.index("first output"), context.index("second output"))
        self.assertEqual(context.count("Tool result ID:"), 2)


if __name__ == "__main__":
    unittest.main()
