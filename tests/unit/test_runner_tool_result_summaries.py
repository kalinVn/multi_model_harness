import unittest
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.session_manager import SessionManager
from harness.models.request import Request
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from tests.unit.model_client_mock import allow_context


class MainOrchestratorToolResultSummariesTest(unittest.TestCase):
    def test_bash_summary_is_saved_and_reused_across_later_requests(self):
        result_id = "81cdfd23-c5ec-4ae7-902e-2cfb83eec76f"
        output = "project/\n  src/\n    harness/\n  tests/"
        summary = "The project contains src/harness and tests directories."
        client = allow_context(Mock())
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("bash", {"commands": ["ls -R"]})]),
            ModelResponse(
                text="Listed the project tree.",
                tool_result_summaries=[ToolResultSummary(result_id, summary)]
            ),
            ModelResponse(text="Continued with the saved context.")
        ]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        runner._tool_registry.execute = Mock(return_value=output)

        with patch("harness.domain.tool_result.uuid4", return_value=result_id):
            self.assertEqual(runner.handle(Request.create("Run ls -R with Bash")), "Listed the project tree.")

        session = runner._session_manager.current_session
        stored_result = session.messages[3].tool_results[0]
        self.assertEqual(stored_result.id, result_id)
        self.assertEqual(stored_result.summary, summary)
        self.assertEqual(stored_result.output, output)
        summary_request = client.generate.call_args_list[1].args[0]
        self.assertTrue(any(result_id in message.content for message in summary_request))

        self.assertEqual(runner.handle(Request.create("Continue")), "Continued with the saved context.")

        later_context = client.generate.call_args_list[2].args[0]
        self.assertEqual(stored_result.summary, summary)
        self.assertEqual(stored_result.output, output)
        self.assertTrue(any(summary in message.content for message in later_context))
        self.assertFalse(any(output in message.content for message in later_context))
        self.assertFalse(any(message.type == "tool_result_summary" for message in later_context))

    def test_retries_missing_and_mismatched_tool_result_summaries(self):
        for returned_summaries in (
            [],
            [ToolResultSummary("unknown-id", "Summary for a different result.")]
        ):
            with self.subTest(returned_summaries=returned_summaries):
                result_id = "bash-result-id"
                summary = "The root directory was listed successfully."
                client = allow_context(Mock())
                client.generate.side_effect = [
                    ModelResponse(tool_calls=[ToolCall("bash", {"commands": ["ls -R"]})]),
                    ModelResponse(text="Premature response", tool_result_summaries=returned_summaries),
                    ModelResponse(
                        text="Done",
                        tool_result_summaries=[ToolResultSummary(result_id, summary)]
                    )
                ]
                with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
                    runner = MainOrchestrator(client)
                runner._tool_registry.execute = Mock(return_value="complete directory tree")

                with patch("harness.domain.tool_result.uuid4", return_value=result_id):
                    self.assertEqual(runner.handle(Request.create("Run ls -R")), "Done")

                stored_result = runner._session_manager.current_session.messages[3].tool_results[0]
                self.assertEqual(stored_result.summary, summary)
                self.assertEqual(stored_result.output, "complete directory tree")
                self.assertEqual(client.generate.call_count, 3)
                runner._tool_registry.execute.assert_called_once_with("bash", {"commands": ["ls -R"]})
                retry_context = client.generate.call_args_list[2].args[0]
                self.assertTrue(any(result_id in message.content for message in retry_context))
                self.assertTrue(any("complete directory tree" in message.content for message in retry_context))
                self.assertTrue(
                    any(
                        "Please add the missing summaries" in message.content
                        for message in retry_context
                    )
                )

    def test_continues_after_repeated_missing_tool_result_summaries(self):
        result_id = "missing-summary-id"
        client = allow_context(Mock())
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("bash", {"commands": ["ls -R"]})]),
            *[
                ModelResponse(text="Response without the requested summary")
                for _ in range(MainOrchestrator.MAX_TOOL_RESULT_SUMMARY_RETRIES + 1)
            ]
        ]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        runner._tool_registry.execute = Mock(return_value="complete directory tree")

        with patch("harness.domain.tool_result.uuid4", return_value=result_id):
            response = runner.handle(Request.create("Run ls -R"))

        self.assertEqual(response, "Response without the requested summary")
        self.assertEqual(
            client.generate.call_count,
            MainOrchestrator.MAX_TOOL_RESULT_SUMMARY_RETRIES + 2
        )
        result = runner._session_manager.current_session.messages[3].tool_results[0]
        self.assertEqual(result.summary, "")
        self.assertEqual(result.output, "complete directory tree")
        self.assertEqual(runner._session_manager.current_session.messages[-1].type, "assistant_message")
        runner._tool_registry.execute.assert_called_once_with("bash", {"commands": ["ls -R"]})

    def test_applies_summaries_before_final_response_or_new_tool_execution(self):
        for has_tool_calls in (False, True):
            with self.subTest(has_tool_calls=has_tool_calls):
                result = ToolResult("read_file", "full original contents")
                summary = "Contains the main orchestration loop."
                client = allow_context(Mock())
                client.generate.side_effect = [
                    ModelResponse(
                        text="Done",
                        tool_calls=[ToolCall("read_file", {"paths": ["next.py"]})] if has_tool_calls else [],
                        tool_result_summaries=[
                            ToolResultSummary(result.id, summary),
                            ToolResultSummary("unknown-id", "Ignore this summary."),
                        ],
                    ),
                    ModelResponse(
                        text="Done",
                        tool_result_summaries=[
                            ToolResultSummary("new-result-id", "Read the next file.")
                        ]
                    ),
                ]
                with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
                    runner = MainOrchestrator(client)
                session = runner._session_manager.current_session
                stored_message = Message(role="user", content=result.output, tool_results=(result,))
                session.add_message(stored_message)

                def execute(name, arguments):
                    self.assertEqual(result.summary, summary)
                    return "new tool output"

                runner._tool_registry.execute = Mock(side_effect=execute)

                with patch("harness.domain.tool_result.uuid4", return_value="new-result-id"):
                    self.assertEqual(runner.handle(Request.create("Continue")), "Done")

                self.assertIs(session.messages[1], stored_message)
                self.assertIs(stored_message.tool_results[0], result)
                self.assertEqual(result.summary, summary)
                self.assertEqual(result.output, "full original contents")
                self.assertEqual(stored_message.content, "full original contents")
                stored_results = [item for message in session.messages for item in message.tool_results]
                self.assertEqual(len(stored_results), 2 if has_tool_calls else 1)
                self.assertEqual(client.generate.call_count, 2 if has_tool_calls else 1)
                if has_tool_calls:
                    runner._tool_registry.execute.assert_called_once_with(
                        "read_file",
                        {"paths": ["next.py"]},
                    )
                    next_messages = client.generate.call_args_list[1].args[0]
                    self.assertTrue(any(summary in message.content for message in next_messages))
                    self.assertFalse(any(result.output in message.content for message in next_messages))
                else:
                    runner._tool_registry.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
