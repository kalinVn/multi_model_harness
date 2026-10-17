import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from harness.service.git_tool_service import GitToolService


class GitToolServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.working_directory = Path(self.temporary_directory.name)
        self.redaction_service = Mock()
        self.redaction_service.redact.side_effect = lambda output: output
        self.service = GitToolService(
            working_directory=self.working_directory,
            timeout_seconds=17,
            redaction_service=self.redaction_service,
        )

    def test_run_executes_git_and_processes_stdout_and_stderr(self):
        completed_process = subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=0,
            stdout="private output\n",
            stderr="private warning\n",
        )
        self.redaction_service.redact.side_effect = (
            lambda output: output.replace("private", "<redacted>")
        )
        with patch(
            "harness.service.git_tool_service.subprocess.run",
            return_value=completed_process,
        ) as run_git:
            output = self.service.run(["status"])

        self.assertEqual(output, "<redacted> output\n<redacted> warning")
        run_git.assert_called_once()
        call = run_git.call_args
        self.assertEqual(
            call.args[0],
            ["git", "-c", "core.hooksPath=/dev/null", "status"],
        )
        self.assertEqual(call.kwargs["cwd"], self.working_directory)
        self.assertEqual(call.kwargs["timeout"], 17)
        self.assertFalse(call.kwargs["check"])
        self.redaction_service.redact.assert_any_call("private output")
        self.redaction_service.redact.assert_any_call("private warning")

    def test_run_raises_sanitized_git_error(self):
        completed_process = subprocess.CompletedProcess(
            args=["git", "fetch"],
            returncode=1,
            stdout="",
            stderr="private failure\n",
        )
        self.redaction_service.redact.side_effect = (
            lambda output: output.replace("private", "<redacted>")
        )

        with (
            patch(
                "harness.service.git_tool_service.subprocess.run",
                return_value=completed_process,
            ),
            self.assertRaisesRegex(
                RuntimeError,
                "Git command failed: <redacted> failure",
            ),
        ):
            self.service.run(["fetch"])

    def test_run_reports_timeout(self):
        with (
            patch(
                "harness.service.git_tool_service.subprocess.run",
                side_effect=subprocess.TimeoutExpired("git", 17),
            ),
            self.assertRaisesRegex(
                RuntimeError,
                "Git command timed out after 17 seconds",
            ),
        ):
            self.service.run(["status"])

    def test_run_reports_missing_git_executable(self):
        with (
            patch(
                "harness.service.git_tool_service.subprocess.run",
                side_effect=FileNotFoundError,
            ),
            self.assertRaisesRegex(RuntimeError, "Git executable was not found"),
        ):
            self.service.run(["status"])


if __name__ == "__main__":
    unittest.main()
