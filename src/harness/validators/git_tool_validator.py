import json
import re
from pathlib import Path
from typing import Any

from harness.config.git_tool_config import (
    GIT_OPERATION_DEFINITIONS,
    GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE,
    GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE,
    MAX_COUNT,
    MAX_MESSAGE_LENGTH,
    MAX_PATHS,
    MAX_STASH_INDEX,
    READ_OPERATIONS,
    REMOTE_OPERATIONS,
    RESET_MODE_VALUES,
    SAFE_REMOTE_NAME_PATTERN,
    SAFE_REVISION_PATTERN,
    SUPPORTED_OPERATIONS,
    TOP_LEVEL_ARGUMENTS,
    WRITE_OPERATIONS,
)
from harness.service.git_tool_service import GitToolService


class GitToolValidator:
    """Validate Git tool permissions and operation arguments."""

    READ_OPERATIONS = READ_OPERATIONS
    WRITE_OPERATIONS = WRITE_OPERATIONS
    REMOTE_OPERATIONS = REMOTE_OPERATIONS
    OPERATIONS = SUPPORTED_OPERATIONS

    def __init__(
        self,
        working_directory: Path,
        allow_write_operations: bool,
        allow_remote_operations: bool,
        service: GitToolService,
    ) -> None:
        self._working_directory = working_directory
        self._allow_write_operations = allow_write_operations
        self._allow_remote_operations = allow_remote_operations
        self._service = service

    def validate(self, arguments: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        if not isinstance(arguments, dict):
            raise ValueError("git arguments must be an object.")

        unexpected_arguments = set(arguments) - TOP_LEVEL_ARGUMENTS
        if unexpected_arguments:
            names = ", ".join(sorted(unexpected_arguments))
            raise ValueError(f"git received unexpected arguments: {names}")

        operation = arguments.get("operation")
        if not isinstance(operation, str) or operation not in self.OPERATIONS:
            allowed = ", ".join(sorted(self.OPERATIONS))
            raise ValueError(f"git operation must be one of: {allowed}")

        if operation in self.WRITE_OPERATIONS and not self._allow_write_operations:
            raise PermissionError(
                "Git write operations are disabled. Set "
                f"{GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE}=true to enable them."
            )
        if operation in self.REMOTE_OPERATIONS and not self._allow_remote_operations:
            raise PermissionError(
                "Git remote operations are disabled. Set "
                f"{GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE}=true to enable them."
            )

        operation_arguments = self._parse_operation_arguments(arguments.get("args"))
        self._ensure_project_repository()
        return operation, operation_arguments

    def require_arguments(
        self,
        arguments: dict[str, Any],
        operation: str,
    ) -> None:
        operation_definition = GIT_OPERATION_DEFINITIONS[operation]
        allowed = operation_definition["allowed_arguments"]
        required = operation_definition["required_arguments"]

        unexpected = set(arguments) - allowed
        if unexpected:
            names = ", ".join(sorted(unexpected))
            raise ValueError(f"git {operation} received unexpected args: {names}")

        missing = required - set(arguments)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"git {operation} is missing required args: {names}")

    def validate_path(self, value: Any, operation: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"git {operation} path must be a non-empty string.")
        if "\0" in value or value.startswith(("-", ":")):
            raise ValueError(f"git {operation} path contains a forbidden value.")

        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = self._working_directory / candidate
        resolved_path = candidate.resolve()

        try:
            relative_path = resolved_path.relative_to(self._working_directory)
        except ValueError as error:
            raise ValueError(
                f"git {operation} path must remain inside the project repository."
            ) from error

        if relative_path.parts and relative_path.parts[0] == ".git":
            raise ValueError(f"git {operation} cannot operate on Git metadata.")

        return relative_path.as_posix() or "."

    def validate_file_path(self, value: Any, operation: str) -> str:
        path = self.validate_path(value, operation)
        if path == ".":
            raise ValueError(f"git {operation} args.path must identify a file.")
        return path

    def validate_paths(self, value: Any, operation: str) -> list[str]:
        if not isinstance(value, list) or not value:
            raise ValueError(f"git {operation} args.paths must be a non-empty array.")
        if len(value) > MAX_PATHS:
            raise ValueError(
                f"git {operation} accepts at most {MAX_PATHS} paths at a time."
            )
        return [self.validate_path(path, operation) for path in value]

    def validate_max_count(self, value: Any, operation: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"git {operation} args.max_count must be an integer.")
        if not 1 <= value <= MAX_COUNT:
            raise ValueError(
                f"git {operation} args.max_count must be between 1 and {MAX_COUNT}."
            )
        return value

    def validate_revision(self, value: Any) -> str:
        if not isinstance(value, str) or not re.fullmatch(
            SAFE_REVISION_PATTERN,
            value,
        ):
            raise ValueError("Git revision must be a non-empty safe revision.")
        return value

    def validate_branch_name(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git branch name must be a non-empty safe string.")

        try:
            self._service.run(
                ["check-ref-format", "--branch", value],
                failure_prefix="Invalid Git branch name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error

        return value

    def validate_tag_name(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git tag name must be a non-empty safe string.")

        try:
            self._service.run(
                ["check-ref-format", f"refs/tags/{value}"],
                failure_prefix="Invalid Git tag name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error

        return value

    def validate_remote_name(self, value: Any) -> str:
        if not isinstance(value, str) or not re.fullmatch(
            SAFE_REMOTE_NAME_PATTERN,
            value,
        ):
            raise ValueError("Git remote name must be a non-empty safe string.")

        remote_names = self._service.run(["remote"]).splitlines()
        if value not in remote_names:
            raise ValueError(f"Unknown Git remote: {value}")
        return value

    def validate_diff_staged(self, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError("git diff args.staged must be a boolean.")
        return value

    def validate_stash_include_untracked(self, value: Any) -> bool:
        if not isinstance(value, bool):
            raise ValueError(
                "git stash args.include_untracked must be a boolean."
            )
        return value

    def validate_message(self, value: Any, operation: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"git {operation} args.message must be a non-empty string."
            )
        if len(value) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"git {operation} args.message must not exceed "
                f"{MAX_MESSAGE_LENGTH} characters."
            )
        return value

    def validate_restore_staged(self, value: Any) -> None:
        if value is not True:
            raise ValueError("git restore only supports the safe staged=true variant.")

    def validate_reset_mode(self, value: Any) -> str:
        if value not in RESET_MODE_VALUES:
            raise ValueError("git reset args.mode must be 'soft' or 'mixed'.")
        return value

    def validate_stash_index(self, value: Any) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= MAX_STASH_INDEX
        ):
            raise ValueError(
                "git stash_pop args.index must be between 0 and "
                f"{MAX_STASH_INDEX}."
            )
        return value

    def _parse_operation_arguments(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise ValueError("git args must contain a valid JSON object.") from error

        if not isinstance(value, dict):
            raise ValueError("git args must be an object or a JSON-encoded object.")
        return value

    def _ensure_project_repository(self) -> None:
        if not self._working_directory.is_dir():
            raise ValueError(
                f"Git working directory does not exist: {self._working_directory}"
            )

        repository_root = self._service.run(
            ["rev-parse", "--show-toplevel"],
            failure_prefix="Not a Git repository",
        )
        if Path(repository_root).resolve() != self._working_directory:
            raise ValueError(
                "Git operations require the configured working directory to be "
                "the repository root."
            )
