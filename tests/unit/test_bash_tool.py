import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.config.bash_tool_config import BASH_ALLOWED_ENVIRONMENT_VARIABLES
from harness.tools.bash_tool import BashTool


class BashToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.working_directory = Path(self.temporary_directory.name)
        self.tool = BashTool(working_directory=self.working_directory)

    def test_execute_passes_only_allowlisted_environment_variables(self):
        completed_process = subprocess.CompletedProcess(
            args="printf safe",
            returncode=0,
            stdout="safe",
            stderr="",
        )
        parent_environment = {
            "PATH": "/usr/bin",
            "HOME": "/home/harness",
            "USER": "harness",
            "LOGNAME": "harness",
            "LANG": "en_US.UTF-8",
            "SSH_AUTH_SOCK": "/tmp/ssh-agent.sock",
            "VIRTUAL_ENV": "/project/.venv",
            "OPENAI_API_KEY": "openai-secret-value",
            "GEMINI_API_KEY": "gemini-secret-value",
            "GROQ_API_KEY": "groq-secret-value",
            "SERVICE_TOKEN": "service-secret-value",
            "DATABASE_PASSWORD": "database-secret-value",
            "UNRELATED_SETTING": "unrelated-value",
        }

        with (
            patch.dict("os.environ", parent_environment, clear=True),
            patch(
                "harness.tools.bash_tool.subprocess.run",
                return_value=completed_process,
            ) as run_bash,
        ):
            output = self.tool.execute({"command": "printf safe"})

        self.assertIn("Output:\nsafe", output)
        child_environment = run_bash.call_args.kwargs["env"]
        self.assertEqual(
            set(child_environment),
            set(parent_environment) & BASH_ALLOWED_ENVIRONMENT_VARIABLES,
        )
        for name in (
            "PATH",
            "HOME",
            "USER",
            "LOGNAME",
            "LANG",
            "SSH_AUTH_SOCK",
            "VIRTUAL_ENV",
        ):
            with self.subTest(name=name):
                self.assertEqual(child_environment[name], parent_environment[name])

        for name in (
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "GROQ_API_KEY",
            "SERVICE_TOKEN",
            "DATABASE_PASSWORD",
            "UNRELATED_SETTING",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, child_environment)

    def test_execute_retains_shell_functionality(self):
        output = self.tool.execute({"command": "printf '%s' \"$PWD\""})

        self.assertIn(f"Output:\n{self.working_directory}", output)


if __name__ == "__main__":
    unittest.main()
