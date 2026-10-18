from copy import deepcopy
from pathlib import Path
from typing import Any

from harness.config.git_tool_config import (
    DEFAULT_ALLOW_REMOTE_OPERATIONS,
    DEFAULT_ALLOW_WRITE_OPERATIONS,
    DEFAULT_TIMEOUT_SECONDS,
    GIT_TOOL_ARGUMENTS_SCHEMA,
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

    @property
    def arguments_schema(self) -> dict[str, str | dict[str, Any]]:
        return deepcopy(GIT_TOOL_ARGUMENTS_SCHEMA)

    def execute(self, arguments: dict[str, Any]) -> str:
        self._validator.validate(arguments)
        command = arguments["command"]
        return self._service.run(command)


