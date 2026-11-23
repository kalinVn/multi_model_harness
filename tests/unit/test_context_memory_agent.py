import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from harness.agents.context_memory_agent import ContextMemoryAgent
from harness.domain.message import Message
from harness.domain.tool_result import ToolResult
from harness.factory.agents_factory import AgentFactory
from harness.models.context_memory_summary import ContextMemorySummary, ImportantToolFinding
from harness.models.response import ModelResponse
from harness.registry.agent_registry import AgentRegistry
from harness.skills.skill_registry import SkillRegistry


class ContextMemoryAgentTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.project_root = Path(self.directory.name)
        caisa_directory = self.project_root / ".caisa"
        caisa_directory.mkdir()
        (caisa_directory / "CAISA.md").write_text("GLOBAL HARNESS INSTRUCTIONS", encoding="utf-8")
        self.model_client = Mock()
        self.factory = AgentFactory(
            self.model_client,
            Mock(),
            [],
            SkillRegistry(),
            project_root=self.project_root
        )
        self.agent = self.factory.create_context_memory()

    def tearDown(self):
        self.directory.cleanup()

    def test_factory_creates_registered_context_memory_agent(self):
        registry = AgentRegistry()
        registry.register(self.agent)

        self.assertIsInstance(self.agent, ContextMemoryAgent)
        self.assertEqual(self.agent.agent_type, "context_memory")
        self.assertIs(registry.get(self.agent.agent_id), self.agent)
        self.assertEqual(registry.get_by_type("context_memory"), [self.agent])

    def test_empty_history_returns_isolated_summary_without_model_call(self):
        first = self.agent.create_summary("session-1", [])
        second = self.agent.create_summary("session-2", [])

        self.assertEqual(first.session_id, "session-1")
        self.assertEqual(second.session_id, "session-2")
        self.assertNotEqual(first.summary_id, second.summary_id)
        self.assertEqual(first.version, 1)
        self.assertEqual(first.conversation_summary, "")
        self.model_client.generate.assert_not_called()

    def test_initial_summary_uses_global_and_specialized_instructions(self):
        self.model_client.generate.return_value = self._response(
            current_goal="Implement memory",
            conversation_summary="The user requested context memory.",
            decisions=["Use the existing ModelClient."],
            constraints=["Do not modify MainOrchestrator."],
            current_state="Implementation requested.",
            pending_steps=["Implement focused tests."]
        )

        summary = self.agent.create_summary(
            "session-1",
            [Message(role="user", type="user_message", content="Implement context memory.")]
        )

        messages = self.model_client.generate.call_args.args[0]
        self.assertIn("GLOBAL HARNESS INSTRUCTIONS", messages[0].content)
        self.assertIn("incrementally update a structured context memory summary", messages[0].content)
        self.assertEqual(self.model_client.generate.call_args.kwargs["tools"], [])
        self.assertEqual(summary.current_goal, "Implement memory")
        self.assertEqual(summary.decisions, ["Use the existing ModelClient."])
        self.assertEqual(summary.constraints, ["Do not modify MainOrchestrator."])
        self.assertEqual(summary.pending_steps, ["Implement focused tests."])

    def test_initial_summary_preserves_real_tool_execution_reference(self):
        tool_result = ToolResult(name="read_file", output="Authentication service exists.", id="exec-123")
        message = Message(
            role="assistant",
            type="tool_result",
            content="Tool result",
            tool_results=(tool_result,)
        )
        finding = {
            "tool_execution_id": "exec-123",
            "tool_name": "read_file",
            "agent_id": None,
            "finding": "The project has an authentication service."
        }
        self.model_client.generate.return_value = self._response(important_tool_findings=[finding])

        summary = self.agent.create_summary("session-1", [message])

        self.assertEqual(summary.important_tool_findings[0].tool_execution_id, "exec-123")
        self.assertEqual(summary.important_tool_findings[0].finding, finding["finding"])
        payload = json.loads(self.model_client.generate.call_args.args[0][1].content)
        self.assertEqual(payload["conversation_history"][0]["tool_results"][0]["id"], "exec-123")

    def test_incremental_update_preserves_identity_and_uses_only_new_context(self):
        previous = ContextMemorySummary(
            summary_id="summary-1",
            session_id="session-1",
            version=2,
            current_goal="Refactor context management",
            conversation_summary="Initial work started.",
            decisions=["Use AgentFactory."],
            constraints=["Keep sessions isolated."],
            current_state="Agent design complete.",
            pending_steps=["Implement updates."]
        )
        self.model_client.generate.return_value = self._response(
            current_goal="Refactor context management",
            conversation_summary="Initial work and update implementation completed.",
            decisions=["Use AgentFactory."],
            constraints=["Keep sessions isolated."],
            current_state="Update implementation complete.",
            pending_steps=["Run verification."]
        )
        new_message = Message(role="assistant", type="assistant_message", content="Update implementation complete.")

        updated = self.agent.update_summary(previous, [new_message])

        self.assertEqual(updated.summary_id, previous.summary_id)
        self.assertEqual(updated.session_id, previous.session_id)
        self.assertEqual(updated.version, 3)
        self.assertEqual(updated.decisions, previous.decisions)
        self.assertEqual(updated.constraints, previous.constraints)
        self.assertEqual(updated.pending_steps, ["Run verification."])
        payload = json.loads(self.model_client.generate.call_args.args[0][1].content)
        self.assertEqual(payload["operation"], "update_summary")
        self.assertNotIn("conversation_history", payload)
        self.assertEqual(len(payload["new_messages"]), 1)

    def test_incremental_update_accepts_new_tool_results_and_rejects_fake_ids(self):
        previous = ContextMemorySummary.empty("session-1")
        result = ToolResult(name="read_file", output="Uses PostgreSQL.", id="exec-456")
        finding = {
            "tool_execution_id": "exec-456",
            "tool_name": "read_file",
            "agent_id": None,
            "finding": "The application uses PostgreSQL."
        }
        self.model_client.generate.return_value = self._response(important_tool_findings=[finding])

        updated = self.agent.update_summary(previous, [], [result])

        self.assertEqual(updated.important_tool_findings[0], ImportantToolFinding(**finding))

        fake_finding = {**finding, "tool_execution_id": "invented-id"}
        self.model_client.generate.return_value = self._response(important_tool_findings=[fake_finding])
        with self.assertRaisesRegex(ValueError, "unknown tool execution IDs"):
            self.agent.update_summary(previous, [], [result])

    def test_invalid_response_does_not_change_previous_summary(self):
        previous = ContextMemorySummary.empty("session-1")
        self.model_client.generate.return_value = ModelResponse(text="not-json")

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            self.agent.update_summary(
                previous,
                [Message(role="user", type="user_message", content="New request")]
            )

        self.model_client.generate.return_value = ModelResponse(text=json.dumps({"current_goal": "Incomplete"}))
        with self.assertRaisesRegex(ValueError, "invalid fields"):
            self.agent.update_summary(
                previous,
                [Message(role="user", type="user_message", content="New request")]
            )

        self.assertEqual(previous.version, 1)
        self.assertEqual(previous.conversation_summary, "")

    @staticmethod
    def _response(**overrides) -> ModelResponse:
        data = {
            "current_goal": None,
            "conversation_summary": "",
            "decisions": [],
            "constraints": [],
            "important_tool_findings": [],
            "important_files": [],
            "current_state": "",
            "pending_steps": [],
            "active_plan_id": None
        }
        data.update(overrides)

        return ModelResponse(text=json.dumps(data))


if __name__ == "__main__":
    unittest.main()
