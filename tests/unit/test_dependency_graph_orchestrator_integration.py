import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.builder.dependency_graph_builder import DependencyGraphBuilder
from harness.models.request import Request
from harness.models.response import ModelResponse
from harness.session_manager import SessionManager
from tests.unit.model_client_mock import allow_context


class DependencyGraphOrchestratorIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[2]

    def create_orchestrator(self, client: Mock, dependency_graph_builder=None) -> MainOrchestrator:
        with patch.object(SessionManager, "_load_system_prompt", return_value="Instructions"):
            return MainOrchestrator(
                allow_context(client),
                project_root=self.project_root,
                dependency_graph_builder=dependency_graph_builder
            )

    def test_build_frontend_stores_recursive_dependencies_before_execution(self):
        client = Mock()
        builder = Mock(wraps=DependencyGraphBuilder(self.project_root))
        runner = self.create_orchestrator(client, builder)
        captured_state = None

        def capture_state(state, session):
            nonlocal captured_state
            captured_state = state
            return "prepared"

        runner._loop = Mock(side_effect=capture_state)

        result = runner.handle(Request.create(
            "execute command build_frontend specification_path=docs/frontend/frontend.md"
        ))

        self.assertEqual(result, "prepared")
        builder.build.assert_called_once_with([
            ".caisa/commands/build_frontend.md",
            "docs/frontend/frontend.md"
        ])
        self.assertIsNotNone(captured_state.dependency_graph)
        self.assertIn(".caisa/agents/new-frontend-orchestrator.md", captured_state.dependency_graph.nodes)
        self.assertIn(".caisa/skills/workflow-new-frontend.md", captured_state.dependency_graph.nodes)
        self.assertEqual(len(captured_state.dependency_graph.files), len(set(captured_state.dependency_graph.files)))
        client.generate.assert_not_called()

    def test_missing_required_input_does_not_invoke_builder_or_model(self):
        client = Mock()
        builder = Mock()
        runner = self.create_orchestrator(client, builder)

        with self.assertRaisesRegex(ValueError, "Required command input is missing: specification_path"):
            runner.handle(Request.create("execute command build_frontend"))

        builder.build.assert_not_called()
        client.generate.assert_not_called()

    def test_builder_error_is_propagated_before_model_execution(self):
        client = Mock()
        builder = Mock()
        builder.build.side_effect = RuntimeError("dependency discovery failed")
        runner = self.create_orchestrator(client, builder)

        with self.assertRaisesRegex(RuntimeError, "dependency discovery failed"):
            runner.handle(Request.create(
                "execute command build_frontend specification_path=docs/frontend/frontend.md"
            ))

        client.generate.assert_not_called()

    def test_existing_llm_flow_continues_after_dependency_discovery(self):
        client = Mock()
        client.generate.return_value = ModelResponse(text='{"answer": "Done"}')
        builder = Mock(wraps=DependencyGraphBuilder(self.project_root))
        runner = self.create_orchestrator(client, builder)

        result = runner.handle(Request.create(
            "execute command build_frontend specification_path=docs/frontend/frontend.md"
        ))

        self.assertEqual(result, "Done")
        builder.build.assert_called_once()
        client.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
