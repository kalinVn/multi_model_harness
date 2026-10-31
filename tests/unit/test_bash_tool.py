import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.config.bash_tool_config import BASH_ALLOWED_ENVIRONMENT_VARIABLES
from harness.tools.bash_tool import BashTool
from harness.tools.tool_registry import ToolRegistry


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
            output = json.loads(
                self.tool.execute({"commands": ["printf safe"]})
            )

        self.assertEqual(output["results"][0]["stdout"], "safe")
        self.assertTrue(output["results"][0]["success"])
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
            "SERVICE_TOKEN",
            "DATABASE_PASSWORD",
            "UNRELATED_SETTING",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, child_environment)

    def test_execute_retains_shell_functionality(self):
        output = json.loads(
            self.tool.execute({"commands": ["printf '%s' \"$PWD\""]})
        )

        self.assertEqual(
            output["results"][0]["stdout"],
            str(self.working_directory),
        )

    def test_executes_multiple_commands_and_continues_after_failure(self):
        output = json.loads(
            self.tool.execute(
                {
                    "commands": [
                        "printf first",
                        "printf failure >&2; exit 7",
                        "printf third",
                    ]
                }
            )
        )

        results = output["results"]
        self.assertFalse(output["success"])
        self.assertEqual([result["stdout"] for result in results], ["first", "", "third"])
        self.assertEqual([result["success"] for result in results], [True, False, True])
        self.assertEqual(results[1]["exit_code"], 7)
        self.assertEqual(results[1]["stderr"], "failure")

    def test_rejects_undeclared_arguments(self):
        registry = ToolRegistry()
        registry.register(self.tool)

        with self.assertRaisesRegex(ValueError, "undeclared parameters: shell"):
            registry.execute(
                "bash",
                {"commands": ["pwd"], "shell": "/bin/sh"}
            )


if __name__ == "__main__":
    unittest.main()
