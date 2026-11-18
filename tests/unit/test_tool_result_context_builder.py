import unittest
from copy import deepcopy

from harness.builder.tool_result_context_builder import (
    TOOL_RESULTS_CONTEXT_FOOTER,
    TOOL_RESULTS_CONTEXT_HEADER,
    build_tool_results_context,
)
from harness.config.model_context_config import MAX_TOOL_RESULT_CHARS
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

    def test_default_limit_preserves_outputs_at_or_below_maximum(self):
        for output_length in (MAX_TOOL_RESULT_CHARS - 1, MAX_TOOL_RESULT_CHARS):
            with self.subTest(output_length=output_length):
                result = ToolResult("bash", "x" * output_length, id="boundary-result")
                original = deepcopy(result)

                context = build_tool_results_context([result])

                self.assertIn("Output:\n" + result.output, context)
                self.assertNotIn("tool result truncated", context)
                self.assertEqual(result, original)

    def test_default_limit_truncates_only_context_above_maximum(self):
        result = ToolResult("bash", "x" * (MAX_TOOL_RESULT_CHARS + 803), id="large-result")
        original = deepcopy(result)

        context = build_tool_results_context([result])

        self.assertIn("Output:\n" + "x" * MAX_TOOL_RESULT_CHARS, context)
        self.assertIn("[tool result truncated: 803 characters omitted]", context)
        self.assertNotIn(result.output, context)
        self.assertEqual(result, original)

    def test_existing_summary_is_not_limited_by_output_maximum(self):
        result = ToolResult(
            "bash",
            "complete original output",
            "s" * (MAX_TOOL_RESULT_CHARS + 1),
            id="summarized-result"
        )
        original = deepcopy(result)

        context = build_tool_results_context([result])

        self.assertIn("Summary:\n" + result.summary, context)
        self.assertNotIn("tool result truncated", context)
        self.assertNotIn(result.output, context)
        self.assertEqual(result, original)

    def test_requested_full_output_uses_default_limit_without_overwriting_summary(self):
        result = ToolResult(
            "bash",
            "x" * (MAX_TOOL_RESULT_CHARS + 5),
            "Saved summary.",
            id="requested-result"
        )
        original = deepcopy(result)

        context = build_tool_results_context(
            [result],
            tool_result_output_requests=[result.id]
        )

        self.assertIn("Output:\n" + "x" * MAX_TOOL_RESULT_CHARS, context)
        self.assertIn("[tool result truncated: 5 characters omitted]", context)
        self.assertNotIn(result.summary, context)
        self.assertEqual(result, original)

    def test_repeated_context_builds_are_identical_and_limit_each_result_independently(self):
        results = [
            ToolResult("bash", "a" * 30_000, id="first-result"),
            ToolResult("bash", "b" * 30_000, id="second-result")
        ]
        original = deepcopy(results)

        first_context = build_tool_results_context(results)
        second_context = build_tool_results_context(results)

        self.assertEqual(first_context, second_context)
        self.assertIn(results[0].output, first_context)
        self.assertIn(results[1].output, first_context)
        self.assertNotIn("tool result truncated", first_context)
        self.assertEqual(results, original)

    def test_tool_result_output_is_truncated_with_an_explicit_marker(self):
        result = ToolResult("git", "x" * 100, id="large-result")

        context = build_tool_results_context([result], max_output_chars=20)

        self.assertIn("Output:\n" + "x" * 20, context)
        self.assertIn("[tool result truncated: 80 characters omitted]", context)
        self.assertNotIn("x" * 21, context)


if __name__ == "__main__":
    unittest.main()
