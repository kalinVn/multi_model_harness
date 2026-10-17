import unittest
from copy import deepcopy
from unittest.mock import Mock, patch
from uuid import UUID

from harness.builder.model_message_builder import ModelMessageBuilder
from harness.builder.tool_result_context_builder import (
    TOOL_RESULTS_CONTEXT_FOOTER,
    TOOL_RESULTS_CONTEXT_HEADER,
)
from harness.builder.tools_schema_builder import TOOLS_CONTEXT_HEADER
from harness.domain.message import Message
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.models.request import Request
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.agents.main_orchestrator import MainOrchestrator
from harness.parser.command_parser import ParsedCommand
from harness.session_manager import SessionManager


class ModelMessageBuilderTest(unittest.TestCase):
    def test_create_model_messages_limits_history_and_preserves_initial_system_messages(self):
        messages = [
            Message(role="system", content="Instructions"),
            Message(role="system", content=f"{TOOLS_CONTEXT_HEADER}\nTools"),
            Message(role="user", content="old request"),
            Message(role="assistant", content="old response"),
            Message(role="user", content="current request"),
        ]

        model_messages = ModelMessageBuilder(
            max_history_messages=2,
        ).create_model_messages(messages, None, Mock())

        self.assertEqual(model_messages, messages[:2] + messages[-2:])

    def test_history_limit_keeps_request_during_long_tool_call_sequence(self):
        request = Message(role="user", content="add and commit changes")
        messages = [Message(role="system", content="Instructions"), request]
        for index in range(3):
            messages.extend([
                Message(role="assistant", content=f"tool call {index}"),
                Message(
                    role="user",
                    content=f"tool result {index}",
                    tool_results=(ToolResult("git", f"output {index}"),),
                ),
            ])

        model_messages = ModelMessageBuilder(
            max_history_messages=3,
        ).create_model_messages(messages, None, Mock())

        self.assertIs(model_messages[1], request)
        self.assertEqual(len(model_messages), 5)
        self.assertTrue(any("output 2" in message.content for message in model_messages))

    def test_compose_limits_tool_result_content_including_errors(self):
        result = ToolResult(
            "git",
            "failure-" + "x" * 100,
            success=False,
            id="failed-result",
        )

        model_messages = ModelMessageBuilder(
            max_tool_result_chars=16,
        ).compose_model_messages([
            Message(role="user", content="raw", tool_results=(result,)),
        ])

        self.assertIn("Success: False", model_messages[0].content)
        self.assertIn("failure-xxxxxxxx", model_messages[0].content)
        self.assertIn("tool result truncated", model_messages[0].content)
        self.assertNotIn(result.output, model_messages[0].content)

    def test_create_model_messages_adds_command_instructions_in_order(self):
        messages = [
            Message(role="system", content="Instructions"),
            Message(role="user", content="execute command review"),
        ]
        original = deepcopy(messages)
        command_context = Message(role="system", content="Command context")
        command_service = Mock()
        command_service.prepare_command_context.return_value = command_context

        model_messages = ModelMessageBuilder().create_model_messages(
            messages,
            ParsedCommand(name="review", arguments=[]),
            command_service,
        )

        command_service.prepare_command_context.assert_called_once_with(
            ParsedCommand(name="review", arguments=[]),
        )
        self.assertEqual(model_messages[:2], messages)
        self.assertIn("`command_summary`", model_messages[-2].content)
        self.assertEqual(model_messages[-1], command_context)
        self.assertEqual(messages, original)

    def test_create_model_messages_filters_tools_when_disabled(self):
        messages = [
            Message(role="system", content=f"{TOOLS_CONTEXT_HEADER}\nTools"),
            Message(role="user", content="Continue"),
        ]
        command_service = Mock()

        model_messages = ModelMessageBuilder().create_model_messages(
            messages,
            None,
            command_service,
            include_tools=False,
        )

        self.assertEqual(model_messages, [Message(role="user", content="Continue")])
        command_service.prepare_command_context.assert_not_called()

    def test_tool_results_generate_unique_ids_and_allow_summary_assignment(self):
        first = ToolResult("read_file", "contents")
        second = ToolResult("read_file", "contents")

        self.assertNotEqual(first.id, second.id)
        self.assertEqual(UUID(first.id).version, 4)
        self.assertEqual(UUID(second.id).version, 4)
        first.summary = "Read configuration."
        self.assertEqual(first.summary, "Read configuration.")

    def test_compose_preserves_history_and_replaces_only_tool_results(self):
        results = (
            ToolResult("read_file", "full file contents", "Read config.py successfully."),
            ToolResult("bash", "full error output", "bash failed.", success=False),
        )
        messages = [
            Message(role="system", content="Instructions"),
            Message(role="user", content="Read config.py"),
            Message(role="assistant", content="Reading config.py"),
            Message(role="user", content="full raw tool results", tool_results=results),
        ]
        original = deepcopy(messages)

        model_messages = ModelMessageBuilder().compose_model_messages(messages)

        self.assertIsNot(model_messages, messages)
        self.assertEqual(len(model_messages), len(messages))
        self.assertEqual(messages, original)
        self.assertEqual(model_messages[:3], messages[:3])
        self.assertEqual(model_messages[3].role, "user")
        self.assertEqual(model_messages[3].tool_results, results)
        self.assertIs(model_messages[3].tool_results[0], results[0])
        self.assertIs(model_messages[3].tool_results[1], results[1])
        self.assertIn(results[0].summary, model_messages[3].content)
        self.assertIn(results[1].summary, model_messages[3].content)
        self.assertIn(results[0].id, model_messages[3].content)
        self.assertIn(results[1].id, model_messages[3].content)
        self.assertNotIn(messages[3].content, model_messages[3].content)
        for result in results:
            self.assertNotIn(result.output, model_messages[3].content)
        self.assertEqual(messages[3].tool_results, results)
        self.assertEqual(model_messages[3].content.count(TOOL_RESULTS_CONTEXT_HEADER), 1)
        self.assertEqual(model_messages[3].content.count(TOOL_RESULTS_CONTEXT_FOOTER), 1)

    def test_compose_handles_summarized_and_unsummarized_results_without_mutation(self):
        summarized = ToolResult("read_file", "already summarized output", "Read configuration.")
        unsummarized = ToolResult("bash", "complete command output")
        another_result = ToolResult("read_file", "another full output")
        message = Message(role="user", content="Original history", tool_results=(summarized, unsummarized))
        another_message = Message(role="user", content="More history", tool_results=(another_result,))
        messages = [message, another_message, Message(role="assistant", content="Continuing")]
        original = deepcopy(messages)

        model_messages = ModelMessageBuilder().compose_model_messages(messages)

        content = model_messages[0].content
        self.assertIn(summarized.summary, content)
        self.assertNotIn(summarized.output, content)
        self.assertIn(unsummarized.output, content)
        self.assertIn(unsummarized.id, content)
        self.assertIn(another_result.output, model_messages[1].content)
        self.assertIn(another_result.id, model_messages[1].content)
        self.assertEqual(len(model_messages), len(messages) + 1)
        self.assertEqual(model_messages[-2], messages[-1])
        instruction = model_messages[-1]
        self.assertEqual(instruction.role, "system")
        self.assertIn(unsummarized.id, instruction.content)
        self.assertIn(another_result.id, instruction.content)
        self.assertNotIn(summarized.id, instruction.content)
        self.assertEqual(sum("concise semantic summary" in item.content for item in model_messages), 1)
        self.assertIn("continuing the main task", instruction.content)
        self.assertIn("100 to 200 tokens", instruction.content)
        self.assertIn("250 tokens", instruction.content)
        self.assertIn("fewer tokens for simple results", instruction.content)
        self.assertEqual(messages, original)
        self.assertEqual(message.content, "Original history")
        self.assertEqual(unsummarized.summary, "")
        self.assertEqual(model_messages[0].tool_results, message.tool_results)

    def test_whitespace_summary_is_treated_as_missing_and_preserved(self):
        result = ToolResult(
            "bash",
            "complete command output",
            "  \n\t",
            id="whitespace-summary-id",
        )
        message = Message(role="user", content="Original history", tool_results=(result,))

        model_messages = ModelMessageBuilder().compose_model_messages([message])

        self.assertEqual(len(model_messages), 2)
        self.assertIn(result.output, model_messages[0].content)
        self.assertIn(result.id, model_messages[0].content)
        self.assertIn(result.id, model_messages[1].content)
        self.assertEqual(result.summary, "  \n\t")
        self.assertEqual(message.content, "Original history")
        self.assertIs(message.tool_results[0], result)

    def test_update_model_messages_replaces_only_requested_summary(self):
        requested = ToolResult(
            "read_file",
            "complete requested output",
            "Requested summary.",
            id="requested-id",
        )
        untouched = ToolResult(
            "read_file",
            "complete untouched output",
            "Untouched summary.",
            id="untouched-id",
        )
        unsummarized = ToolResult(
            "bash",
            "complete unsummarized output",
            id="unsummarized-id",
        )
        unrelated = Message(role="assistant", content="Continue the task")
        source = Message(
            role="user",
            content="Original tool results",
            tool_results=(requested, untouched, unsummarized),
        )
        builder = ModelMessageBuilder()
        model_messages = builder.compose_model_messages([unrelated, source])
        original = deepcopy(model_messages)

        updated = builder.update_model_messages_by_tool_result_output_requests_ids(
            model_messages=model_messages,
            tool_result_output_requests=[requested.id],
        )

        content = updated[1].content
        self.assertEqual(model_messages, original)
        self.assertIs(updated[0], unrelated)
        self.assertIn(requested.output, content)
        self.assertNotIn(requested.summary, content)
        self.assertIn(untouched.summary, content)
        self.assertNotIn(untouched.output, content)
        self.assertIn(unsummarized.output, content)
        self.assertEqual(content.count(requested.id), 1)
        self.assertEqual(content.count(untouched.id), 1)
        self.assertEqual(content.count(unsummarized.id), 1)
        self.assertEqual(content.count(TOOL_RESULTS_CONTEXT_HEADER), 1)
        self.assertEqual(content.count(TOOL_RESULTS_CONTEXT_FOOTER), 1)
        self.assertEqual(len(updated), len(model_messages))

    def test_update_model_messages_handles_empty_and_unknown_requests(self):
        result = ToolResult(
            "read_file",
            "complete output",
            "Existing summary.",
            id="known-id",
        )
        builder = ModelMessageBuilder()
        model_messages = builder.compose_model_messages([
            Message(role="user", content="Original", tool_results=(result,)),
        ])

        empty_update = builder.update_model_messages_by_tool_result_output_requests_ids(
            model_messages=model_messages,
            tool_result_output_requests=[],
        )
        unknown_update = builder.update_model_messages_by_tool_result_output_requests_ids(
            model_messages=model_messages,
            tool_result_output_requests=["unknown-id"],
        )

        self.assertIs(empty_update, model_messages)
        self.assertEqual(unknown_update, model_messages)
        self.assertIs(unknown_update, model_messages)
        self.assertIs(unknown_update[0], model_messages[0])

    def test_update_model_messages_handles_multiple_requested_ids(self):
        first = ToolResult(
            "read_file",
            "first complete output",
            "First summary.",
            id="first-id",
        )
        second = ToolResult(
            "bash",
            "second complete output",
            "Second summary.",
            id="second-id",
        )
        builder = ModelMessageBuilder()
        model_messages = builder.compose_model_messages([
            Message(role="user", content="First", tool_results=(first,)),
            Message(role="user", content="Second", tool_results=(second,)),
        ])

        updated = builder.update_model_messages_by_tool_result_output_requests_ids(
            model_messages=model_messages,
            tool_result_output_requests=[first.id, second.id],
        )

        self.assertIn(first.output, updated[0].content)
        self.assertNotIn(first.summary, updated[0].content)
        self.assertIn(second.output, updated[1].content)
        self.assertNotIn(second.summary, updated[1].content)
        self.assertEqual(len(updated), len(model_messages))

    def test_runner_keeps_and_sends_unsummarized_results_across_turns(self):
        for success in (True, False):
            with self.subTest(success=success):
                client = Mock()
                client.generate.side_effect = [
                    ModelResponse(tool_calls=[ToolCall("read_file", {"path": "config.py"})]),
                    ModelResponse(text="Done"),
                    ModelResponse(text="Next answer"),
                ]
                with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
                    runner = MainOrchestrator(client)

                raw_output = "large raw output or error details"
                runner._tool_registry.execute = Mock(return_value=raw_output)
                if not success:
                    runner._tool_registry.execute.side_effect = ValueError(raw_output)

                self.assertEqual(runner.handle(Request.create("Read config.py")), "Done")
                session = runner._session_manager.current_session
                stored = next(message for message in session.messages if message.tool_results)
                result = stored.tool_results[0]
                self.assertEqual(result.output, raw_output)
                self.assertEqual(result.success, success)
                self.assertEqual(result.summary, "")
                self.assertIn(raw_output, stored.content)
                self.assertTrue(any("Raw tool calls:" in message.content for message in session.messages))
                self.assertEqual(session.messages[-1], Message(role="assistant", content="Done"))
                runner._tool_registry.execute.assert_called_once_with("read_file", {"path": "config.py"})

                self.assertEqual(runner.handle(Request.create("Continue")), "Next answer")
                for call in client.generate.call_args_list[1:]:
                    model_messages = call.args[0]
                    self.assertEqual(sum(raw_output in message.content for message in model_messages), 1)
                    self.assertTrue(any("concise semantic summary" in message.content for message in model_messages))
                    self.assertEqual(
                        sum(bool(message.tool_results) for message in model_messages),
                        1,
                    )
                self.assertEqual(stored.tool_results[0].output, raw_output)

    def test_runner_reinvokes_model_for_requested_previous_output(self):
        previous = ToolResult(
            "read_file",
            "complete previous output",
            "Previous summary.",
            id="previous-id",
        )
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_result_output_requests=[previous.id]),
            ModelResponse(text="Done"),
        ]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        session = runner._session_manager.current_session
        stored_message = Message(
            role="user",
            content="Stored previous output",
            tool_results=(previous,),
        )
        session.add_message(stored_message)
        message_count_before_handle = len(session.messages)
        runner._tool_registry.execute = Mock()

        self.assertEqual(runner.handle(Request.create("Continue")), "Done")

        first_messages = client.generate.call_args_list[0].args[0]
        next_messages = client.generate.call_args_list[1].args[0]
        self.assertTrue(any(previous.summary in message.content for message in first_messages))
        self.assertFalse(any(previous.output in message.content for message in first_messages))
        self.assertTrue(any(previous.output in message.content for message in next_messages))
        self.assertFalse(any(previous.summary in message.content for message in next_messages))
        self.assertEqual(
            sum(message.content.count(previous.id) for message in next_messages),
            1,
        )
        self.assertEqual(len(session.messages), message_count_before_handle + 2)
        self.assertFalse(
            any(message.tool_result_output_requests for message in session.messages)
        )
        stored_messages = [
            message
            for message in session.messages
            if message.tool_results
        ]
        self.assertEqual(len(stored_messages), 1)
        self.assertIs(stored_messages[0], stored_message)
        self.assertEqual(stored_message.content, "Stored previous output")
        self.assertIs(stored_message.tool_results[0], previous)
        runner._tool_registry.execute.assert_not_called()

    def test_runner_limits_requested_previous_output_retries(self):
        previous_results = [
            ToolResult(
                "read_file",
                f"complete output {index}",
                f"Summary {index}.",
                id=f"result-{index}",
            )
            for index in range(
                MainOrchestrator.MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS + 1
            )
        ]
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_result_output_requests=[result.id])
            for result in previous_results
        ]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        session = runner._session_manager.current_session
        session.add_message(
            Message(
                role="user",
                content="Stored previous outputs",
                tool_results=tuple(previous_results),
            )
        )

        result = runner.handle(Request.create("Continue"))

        self.assertEqual(result, "Maximum tool result output request steps exceeded.")
        self.assertEqual(
            client.generate.call_count,
            MainOrchestrator.MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS + 1,
        )
        self.assertEqual(
            session.messages[-1],
            Message(role="assistant", content=result),
        )

    def test_runner_sends_requested_previous_output_on_next_model_call(self):
        previous = ToolResult(
            "read_file",
            "complete previous output",
            "Previous summary.",
            id="previous-id",
        )
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[ToolCall("read_file", {"path": "next.py"})],
                tool_result_output_requests=[previous.id],
            ),
            ModelResponse(text="Done"),
        ]
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        session = runner._session_manager.current_session
        session.add_message(
            Message(
                role="user",
                content="Stored previous output",
                tool_results=(previous,),
            )
        )
        message_count_before_handle = len(session.messages)
        runner._tool_registry.execute = Mock(return_value="new tool output")

        self.assertEqual(runner.handle(Request.create("Continue")), "Done")

        first_messages = client.generate.call_args_list[0].args[0]
        next_messages = client.generate.call_args_list[1].args[0]
        self.assertTrue(any(previous.summary in message.content for message in first_messages))
        self.assertFalse(any(previous.output in message.content for message in first_messages))
        self.assertTrue(any(previous.output in message.content for message in next_messages))
        self.assertFalse(any(previous.summary in message.content for message in next_messages))
        self.assertEqual(
            sum(message.content.count(previous.id) for message in next_messages),
            1,
        )
        self.assertEqual(
            sum(message.content.count("new tool output") for message in next_messages),
            1,
        )
        self.assertEqual(len(session.messages), message_count_before_handle + 4)
        self.assertFalse(
            any(message.tool_result_output_requests for message in session.messages)
        )
        runner._tool_registry.execute.assert_called_once_with(
            "read_file",
            {"path": "next.py"},
        )

    def test_runner_publishes_multiple_tool_results_once_in_execution_order(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[
                    ToolCall("bash", {"command": "printf 'first\\nsecond\\n'"}),
                    ToolCall("read_file", {"path": "missing.txt"}),
                ]
            ),
            ModelResponse(text="Done"),
        ]
        listener = Mock()
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client, on_tool_result=listener)

        runner._tool_registry.execute = Mock(
            side_effect=["first\nsecond", ValueError("missing file")]
        )

        self.assertEqual(runner.handle(Request.create("Inspect the project")), "Done")

        session = runner._session_manager.current_session
        stored_message = next(message for message in session.messages if message.tool_results)
        first, second = stored_message.tool_results

        self.assertEqual(listener.call_count, 2)
        self.assertIs(listener.call_args_list[0].args[0], first)
        self.assertIs(listener.call_args_list[1].args[0], second)
        self.assertEqual(first.output, "first\nsecond")
        self.assertTrue(first.success)
        self.assertEqual(second.output, "missing file")
        self.assertFalse(second.success)
        self.assertEqual(first.summary, "")
        self.assertEqual(second.summary, "")

    def test_runner_publishes_each_result_before_executing_the_next_tool(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[
                    ToolCall("bash", {"command": "first"}),
                    ToolCall("bash", {"command": "second"}),
                ]
            ),
            ModelResponse(text="Done"),
        ]
        listener = Mock()
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client, on_tool_result=listener)

        def execute(_name, arguments):
            if arguments["command"] == "second":
                self.assertEqual(listener.call_count, 1)
                self.assertEqual(listener.call_args.args[0].output, "first output")
            return f"{arguments['command']} output"

        runner._tool_registry.execute = Mock(side_effect=execute)

        self.assertEqual(runner.handle(Request.create("Run both")), "Done")
        self.assertEqual(listener.call_count, 2)

    def test_command_context_and_final_response_are_preserved(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file", {"path": "config.py"})]),
            ModelResponse(text='{"answer": "Done", "command_summary": "Read configuration."}'),
        ]
        command_context = Message(role="system", content="Command instructions")
        listener = Mock()
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client, on_tool_result=listener)
        runner._tool_registry.execute = Mock(return_value="full configuration")

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context,
        ):
            self.assertEqual(runner.handle(Request.create("execute command review")), "Done")

        first_messages = client.generate.call_args_list[0].args[0]
        second_messages = client.generate.call_args_list[1].args[0]
        self.assertIn(command_context, first_messages)
        self.assertIn(command_context, second_messages)
        for messages in (first_messages, second_messages):
            self.assertTrue(any("`command_summary`" in message.content for message in messages))
        session = runner._session_manager.current_session
        self.assertEqual(session.messages[-1], Message(role="assistant", content="Done"))
        self.assertIn("Read configuration.", session.messages[-2].content)
        published_result = listener.call_args.args[0]
        self.assertEqual(listener.call_count, 1)
        self.assertEqual(published_result.name, "read_file")
        self.assertEqual(published_result.output, "full configuration")

    def test_invalid_command_response_is_retried_without_entering_history(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text=""),
            ModelResponse(
                text=(
                    '{"answer": "Done", '
                    '"command_summary": "Command completed."}'
                )
            ),
        ]
        command_context = Message(role="system", content="Command instructions")
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context,
        ):
            self.assertEqual(runner.handle(Request.create("execute command review")), "Done")

        self.assertEqual(client.generate.call_count, 2)
        retry_messages = client.generate.call_args_list[1].args[0]
        self.assertIn(command_context, retry_messages)
        self.assertFalse(
            any(
                message.content.startswith(TOOLS_CONTEXT_HEADER)
                for message in retry_messages
            )
        )
        self.assertTrue(
            any("previous command response" in message.content for message in retry_messages)
        )
        session = runner._session_manager.current_session
        self.assertFalse(any(message.content == "" for message in session.messages))
        self.assertEqual(session.messages[-1], Message(role="assistant", content="Done"))

    def test_summary_only_command_response_is_retried_for_final_answer(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("write_file", {"path": "result.txt"})]),
            ModelResponse(
                tool_result_summaries=[
                    ToolResultSummary("result-id", "The file was created.")
                ]
            ),
            ModelResponse(
                text=(
                    '{"answer": "Created result.txt", '
                    '"command_summary": "Created the requested file."}'
                )
            ),
        ]
        command_context = Message(role="system", content="Command instructions")
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            runner = MainOrchestrator(client)
        runner._tool_registry.execute = Mock(return_value="full write output")

        with (
            patch(
                "harness.service.command_service.get_command_message_obj",
                return_value=command_context,
            ),
            patch("harness.domain.tool_result.uuid4", return_value="result-id"),
        ):
            result = runner.handle(Request.create("execute command review"))

        self.assertEqual(result, "Created result.txt")
        self.assertEqual(client.generate.call_count, 3)
        final_messages = client.generate.call_args_list[2].args[0]
        self.assertTrue(
            any("The file was created." in message.content for message in final_messages)
        )
        self.assertFalse(
            any("full write output" in message.content for message in final_messages)
        )


if __name__ == "__main__":
    unittest.main()
