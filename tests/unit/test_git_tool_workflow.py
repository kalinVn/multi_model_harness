import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from harness.agents.main_orchestrator import MainOrchestrator
from harness.domain.tool_call import ToolCall
from harness.models.request import Request
from harness.models.response import ModelResponse


class GitToolWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.project_root = Path(self.temporary_directory.name)
        caisa_directory = self.project_root / ".caisa"
        caisa_directory.mkdir()
        (caisa_directory / "CAISA.md").write_text(
            "You are a project assistant.",
            encoding="utf-8",
        )
        (self.project_root / "tracked.txt").write_text("initial\n", encoding="utf-8")
        self._git("init")
        self._git("config", "user.name", "Harness Test")
        self._git("config", "user.email", "harness@example.test")
        self._git("add", ".")
        self._git("commit", "-m", "Initial commit")
        (self.project_root / "tracked.txt").write_text("changed\n", encoding="utf-8")

    def _git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def _create_orchestrator(self, responses: list[ModelResponse]):
        client = Mock()
        client.generate.side_effect = responses
        environment = patch.dict(
            os.environ,
            {
                "HARNESS_ENABLE_GIT_WRITE_OPERATIONS": "true",
                "HARNESS_ENABLE_GIT_REMOTE_OPERATIONS": "false",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        return MainOrchestrator(client, project_root=self.project_root), client

    def test_status_add_commit_status_workflow(self):
        runner, client = self._create_orchestrator([
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "add",
                    "command": ["add", "--", "tracked.txt"],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "commit",
                    "command": [
                        "commit",
                        "--no-verify",
                        "--no-gpg-sign",
                        "-m",
                        "Update tracked file",
                    ],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
            ModelResponse(text="Changes were committed and the repository is clean."),
        ])

        result = runner.handle(Request.create("add and commit changes"))

        self.assertEqual(
            result,
            "Changes were committed and the repository is clean.",
        )
        self.assertEqual(client.generate.call_count, 5)
        self.assertEqual(self._git("log", "-1", "--pretty=%s"), "Update tracked file")
        self.assertEqual(self._git("status", "--porcelain"), "")
        for call_index in range(1, 5):
            messages = client.generate.call_args_list[call_index].args[0]
            self.assertTrue(
                any(
                    message.tool_results
                    and "Success: True" in message.content
                    for message in messages
                )
            )

    def test_invalid_add_arguments_are_returned_and_model_can_recover(self):
        runner, client = self._create_orchestrator([
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {"command_name": "add", "command": ["add", "--"]},
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "add",
                    "command": ["add", "--", "tracked.txt"],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "commit",
                    "command": [
                        "commit",
                        "--no-verify",
                        "--no-gpg-sign",
                        "-m",
                        "Recovered commit",
                    ],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
            ModelResponse(text="Recovered from the invalid add call and committed the changes."),
        ])

        result = runner.handle(Request.create("add and commit changes"))

        self.assertEqual(
            result,
            "Recovered from the invalid add call and committed the changes.",
        )
        self.assertEqual(client.generate.call_count, 6)
        recovery_messages = client.generate.call_args_list[2].args[0]
        self.assertTrue(any(
            "Success: False" in message.content
            and "command does not match the supported structure" in message.content
            for message in recovery_messages
        ))
        self.assertEqual(self._git("log", "-1", "--pretty=%s"), "Recovered commit")
        self.assertEqual(self._git("status", "--porcelain"), "")

    def test_tool_iteration_limit_is_configurable(self):
        client = Mock()
        client.generate.side_effect = [
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
            ModelResponse(tool_calls=[ToolCall(
                "git",
                {
                    "command_name": "status",
                    "command": [
                        "status",
                        "--short",
                        "--branch",
                        "--untracked-files=all",
                    ],
                },
            )]),
        ]
        with patch.dict(
            os.environ,
            {
                "HARNESS_ENABLE_GIT_WRITE_OPERATIONS": "true",
                "HARNESS_MAX_TOOL_STEPS": "1",
            },
        ):
            runner = MainOrchestrator(client, project_root=self.project_root)

        result = runner.handle(Request.create("check twice"))

        self.assertEqual(result, "Maximum tool execution steps exceeded.")
        self.assertEqual(client.generate.call_count, 2)


if __name__ == "__main__":
    unittest.main()
