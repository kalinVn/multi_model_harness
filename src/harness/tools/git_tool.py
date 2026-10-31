import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from harness.config.git_tool_config import (
    DEFAULT_ALLOW_REMOTE_OPERATIONS,
    DEFAULT_ALLOW_WRITE_OPERATIONS,
    DEFAULT_TIMEOUT_SECONDS,
    GIT_TOOL_PARAMETER_OBJECT,
    GIT_TOOL_DESCRIPTION,
    GIT_TOOL_NAME,
    READ_OPERATIONS,
    REMOTE_OPERATIONS,
    SUPPORTED_OPERATIONS,
    WRITE_OPERATIONS,
)
from harness.service.git_tool_service import GitToolService
from harness.validators.git_tool_validator import GitToolValidator


class GitTool:
    READ_OPERATIONS = READ_OPERATIONS
    WRITE_OPERATIONS = WRITE_OPERATIONS
    REMOTE_OPERATIONS = REMOTE_OPERATIONS
    OPERATIONS = SUPPORTED_OPERATIONS

    def __init__(
        self,
        working_directory: Path | None = None,
        allow_write_operations: bool = DEFAULT_ALLOW_WRITE_OPERATIONS,
        allow_remote_operations: bool = DEFAULT_ALLOW_REMOTE_OPERATIONS,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._working_directory = (working_directory or Path.cwd()).resolve()
        self._service = GitToolService(
            working_directory=self._working_directory,
            timeout_seconds=timeout_seconds,
        )
        self._validator = GitToolValidator(
            working_directory=self._working_directory,
            allow_write_operations=allow_write_operations,
            allow_remote_operations=allow_remote_operations,
            service=self._service,
        )

    @property
    def name(self) -> str:
        return GIT_TOOL_NAME

    @property
    def description(self) -> str:
        return GIT_TOOL_DESCRIPTION

    def get_parameter_object(self) -> dict[str, Any]:
        return deepcopy(GIT_TOOL_PARAMETER_OBJECT)

    def execute(self, arguments: dict[str, Any]) -> str:
        commands = self._validator.prepare_commands(arguments)
        results: list[dict[str, Any]] = []

        for command_text, command_name, command in commands:
            result: dict[str, Any] = {
                "command": command_text,
                "operation": command_name,
            }
            try:
                result.update(success=True, output=self._service.run(command))
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

