import json
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
            "Executes one or more Bash commands sequentially in the project "
            "working directory. Returns one result per command and continues "
            "after command failures."
        )

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "commands": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Bash commands to execute in order.",
                },
            },
            "required": ["commands"],
            "additionalProperties": False,
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        commands = arguments["commands"]

        if any(not command.strip() for command in commands):
            raise ValueError("bash commands must be non-empty.")

        environment = {
            name: os.environ[name]
            for name in BASH_ALLOWED_ENVIRONMENT_VARIABLES
            if name in os.environ
        }

        results: list[dict[str, Any]] = []
        for command in commands:
            result: dict[str, Any] = {"command": command}

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
                result.update(
                    success=completed_process.returncode == 0,
                    exit_code=completed_process.returncode,
                    stdout=completed_process.stdout.strip(),
                    stderr=completed_process.stderr.strip(),
                )
            except subprocess.TimeoutExpired:
                result.update(
                    success=False,
                    error=(
                        "Bash command timed out after "
                        f"{self._timeout_seconds} seconds."
                    ),
                )
            except Exception as error:
                result.update(success=False, error=str(error))

            results.append(result)

        return json.dumps(
            {
                "success": all(result["success"] for result in results),
                "results": results,
            },
            ensure_ascii=False,
        )
