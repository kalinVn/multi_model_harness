import unittest
from copy import deepcopy

from harness.builder.tool_result_context_builder import (
    TOOL_RESULTS_CONTEXT_FOOTER,
    TOOL_RESULTS_CONTEXT_HEADER,
    build_tool_results_context,
)
from harness.domain.tool_result import ToolResult


class ToolResultContextBuilderTest(unittest.TestCase):
    def test_append_unsummarized_result_includes_complete_result(self):
        result = ToolResult("read_file", "full file contents", id="unsummarized-id")
        context = build_tool_results_context([result])

        self.assertIn("Tool result ID: unsummarized-id", context)
        self.assertIn("Tool: read_file", context)
        self.assertIn("Success: True", context)
        self.assertIn("Output:\nfull file contents", context)

    def test_append_valid_summary_includes_id_and_omits_full_output(self):
        result = ToolResult(
            "read_file",
            "full file contents",
            "Concise file summary.",
            id="summarized-id",
        )
        original = deepcopy(result)
        context = build_tool_results_context([result])

        self.assertIn("Tool result ID: summarized-id", context)
        self.assertIn("Tool: read_file", context)
        self.assertIn("Success: True", context)
        self.assertIn("Summary:\nConcise file summary.", context)
        self.assertNotIn(result.output, context)
        self.assertEqual(result, original)

    def test_empty_and_whitespace_summaries_use_full_output_without_mutation(self):
        for summary in ("", "  \n\t"):
            with self.subTest(summary=summary):
                result = ToolResult(
                    "bash",
                    "complete command output",
                    summary,
                    success=False,
                    id="empty-summary-id",
                )
                original = deepcopy(result)
                context = build_tool_results_context([result])

                self.assertIn("Tool result ID: empty-summary-id", context)
                self.assertIn("Success: False", context)
                self.assertIn(result.output, context)
                self.assertEqual(result, original)

    def test_summary_aware_context_handles_mixed_results_once(self):
        summarized = ToolResult(
            "read_file",
            "raw configuration",
            "Configuration summary.",
            id="first-id",
        )
        unsummarized = ToolResult("bash", "raw command output", id="second-id")

        context = build_tool_results_context([summarized, unsummarized])

        self.assertEqual(context.count(TOOL_RESULTS_CONTEXT_HEADER), 1)
        self.assertEqual(context.count(TOOL_RESULTS_CONTEXT_FOOTER), 1)
        self.assertEqual(context.count("Tool result ID: first-id"), 1)
        self.assertEqual(context.count("Tool result ID: second-id"), 1)
        self.assertIn(summarized.summary, context)
        self.assertNotIn(summarized.output, context)
        self.assertIn(unsummarized.output, context)

    def test_context_uses_summary_when_summary_exists(self):
        result = ToolResult(
            "read_file",
            "initial full output",
            "Summary already present.",
            id="initial-id",
        )

        context = build_tool_results_context([result])

        self.assertIn("Tool result ID: initial-id", context)
        self.assertNotIn(result.output, context)
        self.assertIn(result.summary, context)

    def test_requested_full_output_replaces_existing_summary(self):
        result = ToolResult(
            "read_file",
            "complete requested output",
            "Existing summary.",
            id="requested-id",
        )

        context = build_tool_results_context(
            [result],
            tool_result_output_requests=["requested-id"],
        )

        self.assertIn(result.output, context)
        self.assertNotIn(result.summary, context)


if __name__ == "__main__":
    unittest.main()
