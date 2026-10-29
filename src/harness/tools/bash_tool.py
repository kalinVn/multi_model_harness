import os
import subprocess
from pathlib import Path
from typing import Any

from harness.config.bash_tool_config import BASH_ALLOWED_ENVIRONMENT_VARIABLES


class BashTool:
    def __init__(
        self,
        working_directory: Path | None = None,
        timeout_seconds: int = 30,
    ) -> None:
        self._working_directory = (working_directory or Path.cwd()).resolve()

        self._timeout_seconds = timeout_seconds

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return (
            "Executes a Bash command in the project "
            "working directory."
        )

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to execute.",
                },
            },
            "required": ["command"],
            "additionalProperties": False,
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        command = arguments.get("command")

        if not isinstance(command, str):
            raise ValueError("bash requires a string 'command'.")

        if not command.strip():
            raise ValueError("bash requires a non-empty 'command'.")

        environment = {
            name: os.environ[name]
            for name in BASH_ALLOWED_ENVIRONMENT_VARIABLES
            if name in os.environ
        }

        try:
            completed_process = subprocess.run(
                command,
                cwd=self._working_directory,
                env=environment,
                shell=True,
                executable="/bin/bash",
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )

        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Bash command timed out after "
                f"{self._timeout_seconds} seconds."
            ) from error

        parts = [
            f"Exit code: {completed_process.returncode}"
        ]

        stdout = completed_process.stdout.strip()
        stderr = completed_process.stderr.strip()

        if stdout:
            parts.append(f"Output:\n{stdout}")

        if stderr:
            parts.append(f"Errors:\n{stderr}")

        if not stdout and not stderr:
            parts.append("No output.")

        return "\n\n".join(parts)
