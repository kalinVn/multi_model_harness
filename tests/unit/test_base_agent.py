import json
import unittest
from unittest.mock import Mock, call

from harness.agents.base_agent import BaseAgent
from harness.agents.planner_agent import PlannerAgent
from harness.domain.agent import Agent
from harness.domain.message import Message
from harness.domain.skill import Skill
from harness.domain.tool_call import ToolCall
from harness.domain.tool_result import ToolResult
from harness.models.response import ModelResponse
from harness.skills.skill_registry import SkillRegistry


class BaseAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent_definition = Agent(
            name="worker",
            description="Worker agent",
            instructions="Base instructions",
            allowed_tools=("read_file",),
            allowed_skills=("review",),
            max_steps=2
        )
        self.model_client = Mock()
        self.tool_service = Mock()
        self.tool_definitions = [{
            "name": "read_file",
            "description": "Read files",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }]
        self.skill_registry = SkillRegistry()
        self.skill_registry.register(Skill("review", "Review", "Skill instructions"))
        self.agent = BaseAgent(
            self.agent_definition,
            self.model_client,
            self.tool_service,
            self.tool_definitions,
            self.skill_registry
        )

    def test_observe_hook_is_removed(self):
        self.assertFalse(hasattr(self.agent, "observe"))

    def test_think_receives_prepared_messages_and_allowed_tools(self):
        available_tools = [self.tool_definitions[0]]
        self.tool_service.get_available_tools_by_names.return_value = available_tools
        self.model_client.generate.return_value = ModelResponse(text="Done")

        result = self.agent.loop("Complete the task")

        expected_messages = [
            Message(
                role="system",
                type="system_instruction",
                content="Base instructions\n\nSkill instructions"
            ),
            Message(role="user", type="user_message", content="Complete the task")
        ]
        self.model_client.generate.assert_called_once_with(expected_messages, tools=available_tools)
        self.tool_service.get_available_tools_by_names.assert_called_once_with(
            self.tool_definitions,
            ("read_file",)
        )
        self.assertEqual(result, Message(role="assistant", type="assistant_message", content="Done"))

    def test_decide_returns_model_tool_calls(self):
        tool_calls = [ToolCall("read_file", {"paths": ["README.md"]})]

        self.assertIs(self.agent.decide(ModelResponse(tool_calls=tool_calls)), tool_calls)

    def test_action_executes_tools_and_appends_response_messages(self):
        messages = [Message(role="user", content="Read")]
        tool_calls = [ToolCall("read_file", {"paths": ["README.md"]})]
        available_tools = [self.tool_definitions[0]]
        tool_results = [ToolResult("read_file", "contents")]
        tool_call_message = Message(role="assistant", type="tool_call", content="call")
        tool_result_message = Message(role="system", type="tool_result", content="result")
        self.tool_service.execute_tool_calls.return_value = tool_results
        self.tool_service.prepare_tool_response_messages.return_value = (tool_call_message, tool_result_message)

        self.agent.action(messages, tool_calls, available_tools)

        self.tool_service.execute_tool_calls.assert_called_once_with(tool_calls, available_tools)
        self.tool_service.prepare_tool_response_messages.assert_called_once_with(tool_calls, tool_results)
        self.assertEqual(messages[-2:], [tool_call_message, tool_result_message])

    def test_next_think_iteration_receives_previous_tool_results(self):
        tool_call = ToolCall("read_file", {"paths": ["README.md"]})
        tool_call_message = Message(role="assistant", type="tool_call", content="call")
        tool_result_message = Message(role="system", type="tool_result", content="result")
        available_tools = [self.tool_definitions[0]]
        self.tool_service.get_available_tools_by_names.return_value = available_tools
        self.tool_service.execute_tool_calls.return_value = [ToolResult("read_file", "contents")]
        self.tool_service.prepare_tool_response_messages.return_value = (tool_call_message, tool_result_message)
        self.model_client.generate.side_effect = [
            ModelResponse(tool_calls=[tool_call]),
            ModelResponse(text="Finished")
        ]

        result = self.agent.loop("Read the file")

        first_messages = self.model_client.generate.call_args_list[0].args[0]
        second_messages = self.model_client.generate.call_args_list[1].args[0]
        self.assertIs(first_messages, second_messages)
        self.assertEqual(second_messages[-2:], [tool_call_message, tool_result_message])
        self.assertEqual(result.content, "Finished")

    def test_maximum_step_limit_is_preserved(self):
        tool_call = ToolCall("read_file")
        available_tools = [self.tool_definitions[0]]
        self.tool_service.get_available_tools_by_names.return_value = available_tools
        self.tool_service.execute_tool_calls.return_value = []
        self.tool_service.prepare_tool_response_messages.return_value = (
            Message(role="assistant", type="tool_call", content="call"),
            Message(role="system", type="tool_result", content="result")
        )
        self.model_client.generate.return_value = ModelResponse(tool_calls=[tool_call])

        result = self.agent.loop("Keep working")

        self.assertEqual(self.model_client.generate.call_count, 2)
        self.assertEqual(self.tool_service.execute_tool_calls.call_count, 2)
        self.assertEqual(result.type, "error")
        self.assertEqual(result.content, "Agent 'worker' reached its maximum number of steps.")

    def test_invalid_tasks_return_existing_errors_without_model_calls(self):
        self.assertEqual(
            self.agent.loop(None),
            Message(role="assistant", type="error", content="Task is required.")
        )
        self.assertEqual(
            self.agent.loop("  "),
            Message(role="assistant", type="error", content="Task cannot be empty.")
        )
        self.model_client.generate.assert_not_called()
        self.tool_service.get_available_tools_by_names.assert_not_called()

    def test_planner_subclass_continues_through_base_loop(self):
        planner = PlannerAgent(
            self.agent_definition,
            self.model_client,
            self.tool_service,
            self.tool_definitions,
            self.skill_registry
        )
        available_tools = [self.tool_definitions[0]]
        self.tool_service.get_available_tools_by_names.return_value = available_tools
        self.model_client.generate.side_effect = [
            ModelResponse(text=json.dumps({"requires_plan": True})),
            ModelResponse(text="Plan complete")
        ]

        result = planner.plan("Plan this task")

        self.assertEqual(result.content, "Plan complete")
        self.assertEqual(
            self.model_client.generate.call_args_list,
            [
                call(unittest.mock.ANY, tools=[]),
                call(unittest.mock.ANY, tools=available_tools)
            ]
        )


if __name__ == "__main__":
    unittest.main()
