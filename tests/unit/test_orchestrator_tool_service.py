import unittest
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.config.response.command_response_config import COMMAND_RESPONSE_FORMAT_INSTRUCTIONS
from harness.config.tool_usage_config import TOOL_USAGE_INSTRUCTIONS
from harness.domain.context import ModelContextLimits
from harness.domain.loop_state import LoopState
from harness.domain.message import Message
from harness.domain.session import Session
from harness.domain.tool_call import ToolCall
from harness.models.context_memory_summary import ContextMemorySummary
from harness.models.errors import ContextWindowExceeded
from harness.models.request import Request
from harness.models.response import ModelResponse
from harness.session_manager import SessionManager
from tests.unit.model_client_mock import allow_context


class MainOrchestratorToolServiceIntegrationTest(unittest.TestCase):
    def create_orchestrator(self, client: Mock, on_tool_result=None) -> MainOrchestrator:
        with patch.object(
            SessionManager,
            "_load_system_prompt",
            return_value="Instructions"
        ):
            return MainOrchestrator(allow_context(client), on_tool_result=on_tool_result)

    def test_tool_service_reuses_orchestrator_dependencies(self):
        callback = Mock()
        runner = self.create_orchestrator(Mock(), callback)

        self.assertIs(runner._tool_service._tool_registry, runner._tool_registry)
        self.assertIs(
            runner._tool_service._model_message_builder,
            runner._model_messages_builder,
        )
        self.assertIs(runner._tool_service._on_tool_result, callback)

    def test_session_starts_with_combined_system_message(self):
        runner = self.create_orchestrator(Mock())

        messages = runner._session_manager.current_session.messages

        self.assertEqual(len(messages), 1)
        system_instruction = messages[0]
        self.assertEqual(system_instruction.role, "system")
        self.assertEqual(system_instruction.type, "system_instruction")
        self.assertEqual(
            system_instruction.content,
            f"Instructions\n\n{TOOL_USAGE_INSTRUCTIONS}\n\n{COMMAND_RESPONSE_FORMAT_INSTRUCTIONS}"
        )

    def test_normal_response_is_added_to_session_and_returned(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text="Hello")
        runner = self.create_orchestrator(client)

        result = runner.handle(Request.create("Hi"))

        self.assertEqual(result, "Hello")
        self.assertTrue(client.generate.call_args.kwargs["tools"])
        self.assertEqual(
            runner._session_manager.current_session.messages[-2].type,
            "user_message"
        )
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content="Hello", type="assistant_message")
        )

    def test_context_validation_uses_each_generated_request(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})]),
            ModelResponse(text="Done")
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(return_value="contents")

        self.assertEqual(runner.handle(Request.create("Read README.md")), "Done")

        self.assertEqual(client.count_tokens.call_count, client.generate.call_count)
        self.assertEqual(client.get_context_limits.call_count, client.generate.call_count)
        for count_call, generate_call in zip(client.count_tokens.call_args_list, client.generate.call_args_list):
            self.assertEqual(count_call.args[0], generate_call.args[0])
            self.assertEqual(count_call.args[1], generate_call.kwargs["tools"])

    def test_context_validation_rejects_request_before_generation(self):
        client = Mock()
        runner = self.create_orchestrator(client)
        client.count_tokens.return_value = 901
        client.get_context_limits.return_value = ModelContextLimits("test-model", 1_000, 100)

        with self.assertRaises(ContextWindowExceeded):
            runner.handle(Request.create("Continue"))

        client.generate.assert_not_called()

    def test_unknown_command_returns_message_without_calling_model(self):
        client = Mock()
        runner = self.create_orchestrator(client)

        result = runner.handle(Request.create("execute command missing-command"))

        self.assertEqual(result, "Unknown command: missing-command")
        client.generate.assert_not_called()
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )

    def test_command_answer_is_stored_without_summary_message(self):
        client = Mock()
        client.generate.return_value = ModelResponse(
            text='{"answer": "Done"}'
        )
        runner = self.create_orchestrator(client)

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=Message(role="system", content="Command instructions"),
        ):
            result = runner.handle(Request.create("execute command review"))

        self.assertEqual(result, "Done")
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content="Done", type="assistant_message")
        )

    def test_command_without_declared_tools_disables_tool_calls(self):
        client = Mock()
        client.generate.return_value = ModelResponse(
            text='{"answer": "Hello"}'
        )
        runner = self.create_orchestrator(client)
        command_context = Message(
            role="system",
            content="Hello command instructions",
            available_tool_names=()
        )

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context
        ):
            result = runner.handle(Request.create("execute command hello"))

        self.assertEqual(result, "Hello")
        self.assertEqual(client.generate.call_args.kwargs["tools"], [])

    def test_command_retry_permissions_do_not_leak_to_next_request(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(text='{"answer": "Hello"}'),
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})]),
            ModelResponse(text="Done")
        ]
        runner = self.create_orchestrator(client)
        command_context = Message(
            role="system",
            content="Command instructions",
            available_tool_names=("read_file",)
        )

        with patch(
            "harness.service.command_service.get_command_message_obj",
            return_value=command_context
        ):
            self.assertEqual(runner.handle(Request.create("execute command hello")), "Hello")

        runner._tool_registry.execute = Mock(return_value="contents")

        self.assertEqual(runner.handle(Request.create("Read README.md")), "Done")
        self.assertEqual(
            [tool["name"] for tool in client.generate.call_args_list[0].kwargs["tools"]],
            ["read_file"]
        )
        self.assertEqual(client.generate.call_args_list[1].kwargs["tools"], [])
        self.assertTrue(client.generate.call_args_list[2].kwargs["tools"])
        runner._tool_registry.execute.assert_called_once_with(
            "read_file",
            {"paths": ["README.md"]}
        )

    def test_tool_messages_keep_execution_order_and_final_response(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[
                    ToolCall("read_file", {"paths": ["first.txt"]}),
                    ToolCall("bash", {"commands": ["pwd"]}),
                ]
            ),
            ModelResponse(text="Done"),
        ]
        callback = Mock()
        runner = self.create_orchestrator(client, callback)
        session = runner._session_manager.current_session

        def execute(name, _arguments):
            self.assertTrue(session.messages[-1].content.startswith("Raw tool calls:"))
            self.assertFalse(session.messages[-1].tool_results)
            return f"{name} output"

        runner._tool_registry.execute = Mock(side_effect=execute)

        result = runner.handle(Request.create("Inspect the project"))

        self.assertEqual(result, "Done")
        self.assertEqual(runner._tool_registry.execute.call_count, 2)
        self.assertEqual(callback.call_count, 2)
        tool_call_index = next(
            index
            for index, message in enumerate(session.messages)
            if message.content.startswith("Raw tool calls:")
        )
        tool_result_index = next(
            index
            for index, message in enumerate(session.messages)
            if message.tool_results
        )
        self.assertLess(tool_call_index, tool_result_index)
        self.assertEqual(len(session.messages[tool_result_index].tool_results), 2)
        self.assertEqual(
            session.messages[-1],
            Message(role="assistant", content="Done", type="assistant_message")
        )

    def test_sequential_tool_calls_update_model_context_incrementally(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["first.txt"]})]),
            ModelResponse(tool_calls=[ToolCall("bash", {"commands": ["pwd"]})]),
            ModelResponse(text="Done")
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(side_effect=["first output", "second output"])
        builder = runner._model_messages_builder
        builder.create_model_messages = Mock(wraps=builder.create_model_messages)
        builder.prepare_new_messages = Mock(wraps=builder.prepare_new_messages)

        result = runner.handle(Request.create("Inspect sequentially"))

        self.assertEqual(result, "Done")
        builder.create_model_messages.assert_called_once()
        self.assertEqual(builder.prepare_new_messages.call_count, 3)
        final_context = client.generate.call_args_list[2].args[0]
        self.assertEqual(sum(message.type == "user_message" for message in final_context), 1)
        self.assertEqual(sum(message.type == "tool_call" for message in final_context), 2)
        self.assertEqual(sum(message.type == "tool_result" for message in final_context), 2)
        self.assertIn("first output", next(
            message.content
            for message in final_context
            if message.tool_results and message.tool_results[0].name == "read_file"
        ))
        self.assertIn("second output", next(
            message.content
            for message in final_context
            if message.tool_results and message.tool_results[0].name == "bash"
        ))

    def test_previous_tool_result_can_be_requested_by_id(self):
        client = Mock()
        generated_requests = []

        def generate(messages, tools=None):
            generated_requests.append(messages)
            if len(generated_requests) == 1:
                return ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["large.txt"]})])

            result = next(result for message in messages for result in message.tool_results)
            if len(generated_requests) == 2:
                self.assertIn("[tool result truncated:", next(
                    message.content for message in messages if message.tool_results
                ))
                return ModelResponse(tool_result_output_requests=[result.id])

            self.assertIn("abcdefghij", next(message.content for message in messages if message.tool_results))

            return ModelResponse(text="Done")

        client.generate.side_effect = generate
        runner = self.create_orchestrator(client)
        runner._model_messages_builder._max_tool_result_chars = 5
        runner._tool_registry.execute = Mock(return_value="abcdefghij")

        result = runner.handle(Request.create("Read the complete result"))

        self.assertEqual(result, "Done")
        self.assertEqual(client.generate.call_count, 3)
        stored_result = next(
            result
            for message in runner._session_manager.current_session.messages
            for result in message.tool_results
        )
        self.assertEqual(stored_result.output, "abcdefghij")

    def test_tool_execution_limit_is_preserved(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file")]),
            ModelResponse(tool_calls=[ToolCall("read_file")]),
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(return_value="output")

        with patch.object(MainOrchestrator, "MAX_TOOL_STEPS", 1):
            result = runner.handle(Request.create("Continue"))

        self.assertEqual(result, "Maximum tool execution steps exceeded.")
        runner._tool_registry.execute.assert_called_once_with("read_file", {})
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )

    def test_registered_tool_unavailable_for_request_is_rejected_before_execution(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(tool_calls=[ToolCall("read_file")]),
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock()

        with (
            patch(
                "harness.service.command_service.get_command_message_obj",
                return_value=Message(role="system", content="Command instructions")
            ),
            self.assertRaisesRegex(ValueError, "Model returned an unavailable tool")
        ):
            runner.handle(Request.create("execute command review"))

        self.assertTrue(client.generate.call_args_list[0].kwargs["tools"])
        self.assertEqual(client.generate.call_args_list[1].kwargs["tools"], [])
        runner._tool_registry.execute.assert_not_called()

    def test_command_response_retry_limit_and_final_result_are_preserved(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="invalid"),
            ModelResponse(text="still invalid"),
        ]
        runner = self.create_orchestrator(client)
        builder = runner._model_messages_builder
        builder.create_model_messages = Mock(wraps=builder.create_model_messages)

        with (
            patch.object(MainOrchestrator, "MAX_COMMAND_RESPONSE_RETRIES", 1),
            patch(
                "harness.service.command_service.get_command_message_obj",
                return_value=Message(role="system", content="Command instructions")
            )
        ):
            result = runner.handle(Request.create("execute command review"))

        self.assertEqual(result, "Command response remained invalid after 1 retries.")
        self.assertEqual(client.generate.call_count, 2)
        builder.create_model_messages.assert_called_once()
        self.assertFalse(any(
            "previous command response" in message.content.lower()
            for message in runner._session_manager.current_session.messages
        ))
        self.assertEqual(
            runner._session_manager.current_session.messages[-1],
            Message(role="assistant", content=result, type="error")
        )

    def test_completed_task_without_tools_updates_memory_once(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text="Done", task_status="completed")
        runner = self.create_orchestrator(client)
        session = runner._session_manager.current_session
        summary = ContextMemorySummary.empty(session.id)
        memory_agent = Mock()
        memory_agent.create_summary.return_value = summary
        runner._context_memory_agent = memory_agent

        result = runner.handle(Request.create("Complete the task"))

        self.assertEqual(result, "Done")
        memory_agent.create_summary.assert_called_once()
        memory_agent.update_summary.assert_not_called()
        task_messages = memory_agent.create_summary.call_args.args[1]
        self.assertEqual(task_messages[0].content, "Complete the task")
        self.assertEqual(task_messages[-1].content, "Done")
        self.assertIs(session.context_memory_summary, summary)
        self.assertTrue(session.memory_update_completed)
        self.assertIsNone(session.active_task_start_index)

        runner._update_context_memory(session)
        memory_agent.create_summary.assert_called_once()

    def test_in_progress_task_continues_across_handle_calls(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="I need the filename.", task_status="in_progress"),
            ModelResponse(text="Done", task_status="completed")
        ]
        runner = self.create_orchestrator(client)
        session = runner._session_manager.current_session
        memory_agent = Mock()
        memory_agent.create_summary.return_value = ContextMemorySummary.empty(session.id)
        runner._context_memory_agent = memory_agent

        first_result = runner.handle(Request.create("Read a file"))

        self.assertEqual(first_result, "I need the filename.")
        memory_agent.create_summary.assert_not_called()
        task_start = session.active_task_start_index

        second_result = runner.handle(Request.create("Use README.md"))

        self.assertEqual(second_result, "Done")
        self.assertEqual(memory_agent.create_summary.call_count, 1)
        self.assertEqual(memory_agent.create_summary.call_args.args[1], session.messages[task_start:])
        second_context = client.generate.call_args_list[1].args[0]
        self.assertTrue(any(message.content == "I need the filename." for message in second_context))
        self.assertTrue(any(message.content == "Use README.md" for message in second_context))

    def test_blocked_and_missing_status_do_not_update_memory(self):
        for response in (
            ModelResponse(text="Need permission", task_status="blocked"),
            ModelResponse(text="Status missing")
        ):
            with self.subTest(task_status=response.task_status):
                client = Mock()
                client.generate.return_value = response
                runner = self.create_orchestrator(client)
                memory_agent = Mock()
                runner._context_memory_agent = memory_agent

                runner.handle(Request.create("Continue"))

                memory_agent.create_summary.assert_not_called()
                memory_agent.update_summary.assert_not_called()
                session = runner._session_manager.current_session
                self.assertIsNotNone(session.active_task_start_index)
                self.assertFalse(session.memory_update_completed)

    def test_completed_status_with_pending_tool_calls_is_not_confirmed(self):
        state = LoopState(
            execution_finished=True,
            response=ModelResponse(
                tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})],
                task_status="completed"
            )
        )
        session = Session(messages=[Message(role="user", type="user_message", content="Read file")])
        session.active_task_start_index = 0

        self.assertFalse(MainOrchestrator._is_task_completed(state, session))

    def test_contradicted_completed_status_keeps_task_active_and_records_uncertainty(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(
                tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})],
                task_status="completed"
            ),
            ModelResponse(
                tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})],
                task_status="completed"
            )
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(return_value="contents")
        memory_agent = Mock()
        runner._context_memory_agent = memory_agent

        with patch.object(MainOrchestrator, "MAX_TOOL_STEPS", 1):
            result = runner.handle(Request.create("Read until complete"))

        session = runner._session_manager.current_session
        self.assertEqual(result, "Maximum tool execution steps exceeded.")
        self.assertEqual(session.task_status, "in_progress")
        self.assertIsNotNone(session.completion_uncertainty)
        self.assertIsNotNone(session.active_task_start_index)
        memory_agent.create_summary.assert_not_called()

    def test_blocked_tool_failure_preserves_original_result_without_memory_update(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall("read_file", {"paths": ["missing.txt"]})]),
            ModelResponse(text="The file is unavailable.", task_status="blocked")
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(side_effect=RuntimeError("missing file"))
        memory_agent = Mock()
        runner._context_memory_agent = memory_agent

        result = runner.handle(Request.create("Read missing.txt"))

        self.assertEqual(result, "The file is unavailable.")
        memory_agent.create_summary.assert_not_called()
        stored_result = next(
            result
            for message in runner._session_manager.current_session.messages
            for result in message.tool_results
        )
        self.assertFalse(stored_result.success)
        self.assertEqual(stored_result.output, "missing file")
        self.assertTrue(stored_result.id)

    def test_completed_task_with_multiple_tools_passes_original_results_to_memory(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[
                ToolCall("read_file", {"paths": ["first.txt"]}),
                ToolCall("bash", {"commands": ["pwd"]})
            ]),
            ModelResponse(text="Done", task_status="completed")
        ]
        runner = self.create_orchestrator(client)
        runner._tool_registry.execute = Mock(side_effect=["first output", "second output"])
        session = runner._session_manager.current_session
        memory_agent = Mock()
        memory_agent.create_summary.return_value = ContextMemorySummary.empty(session.id)
        runner._context_memory_agent = memory_agent

        runner.handle(Request.create("Inspect the project"))

        task_messages = memory_agent.create_summary.call_args.args[1]
        task_results = [result for message in task_messages for result in message.tool_results]
        self.assertEqual([result.output for result in task_results], ["first output", "second output"])
        self.assertEqual(len({result.id for result in task_results}), 2)
        for result in task_results:
            self.assertIs(session.get_tool_result_by_id(result.id), result)

    def test_existing_memory_and_active_plan_use_incremental_update(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text="Plan completed", task_status="completed")
        runner = self.create_orchestrator(client)
        session = runner._session_manager.current_session
        previous = ContextMemorySummary(
            summary_id="summary-1",
            session_id=session.id,
            version=1,
            active_plan_id="plan-1"
        )
        updated = ContextMemorySummary(
            summary_id="summary-1",
            session_id=session.id,
            version=2,
            conversation_summary="Plan completed"
        )
        session.context_memory_summary = previous
        memory_agent = Mock()
        memory_agent.update_summary.return_value = updated
        runner._context_memory_agent = memory_agent

        runner.handle(Request.create("Finish the active plan"))

        memory_agent.create_summary.assert_not_called()
        memory_agent.update_summary.assert_called_once()
        self.assertIs(memory_agent.update_summary.call_args.args[0], previous)
        self.assertIs(session.context_memory_summary, updated)

    def test_completed_history_is_replaced_by_memory_in_next_model_context(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(text="First done", task_status="completed"),
            ModelResponse(text="Working", task_status="in_progress")
        ]
        runner = self.create_orchestrator(client)
        session = runner._session_manager.current_session
        summary = ContextMemorySummary(
            summary_id="summary-1",
            session_id=session.id,
            version=1,
            conversation_summary="The first task was completed."
        )
        memory_agent = Mock()
        memory_agent.create_summary.return_value = summary
        runner._context_memory_agent = memory_agent

        runner.handle(Request.create("First raw task"))
        runner.handle(Request.create("Second task"))

        second_context = client.generate.call_args_list[1].args[0]
        self.assertTrue(any(message.type == "context_memory" for message in second_context))
        self.assertFalse(any(message.content == "First raw task" for message in second_context))
        self.assertFalse(any(message.content == "First done" for message in second_context))
        self.assertTrue(any(message.content == "Second task" for message in second_context))

    def test_memory_failure_preserves_response_and_unsummarized_task(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text="Done", task_status="completed")
        runner = self.create_orchestrator(client)
        session = runner._session_manager.current_session
        memory_agent = Mock()
        memory_agent.create_summary.side_effect = ValueError("invalid memory response")
        runner._context_memory_agent = memory_agent

        result = runner.handle(Request.create("Complete the task"))

        self.assertEqual(result, "Done")
        self.assertIsNone(session.context_memory_summary)
        self.assertIsNotNone(session.active_task_start_index)
        self.assertFalse(session.memory_update_completed)
        self.assertEqual(session.memory_update_error, "invalid memory response")
        self.assertTrue(any(message.content == "Complete the task" for message in session.messages))
        self.assertTrue(any(message.content == "Done" for message in session.messages))


if __name__ == "__main__":
    unittest.main()
