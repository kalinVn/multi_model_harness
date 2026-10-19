import os
import subprocess
from pathlib import Path

from harness.config.git_tool_config import (
    GIT_ALLOWED_ENVIRONMENT_VARIABLES,
    GIT_COMMAND_FAILURE_PREFIX,
    GIT_COMMAND_PREFIX,
    GIT_ENVIRONMENT_OVERRIDES,
)
from harness.service.sensitive_data_redaction_service import (
    SensitiveDataRedactionService,
)


class GitToolService:
    """Изпълнява Git команди с конфигурираните ограничения за сигурност."""

    def __init__(
        self,
        working_directory: Path,
        timeout_seconds: int,
        redaction_service: SensitiveDataRedactionService | None = None,
    ) -> None:
        self._working_directory = working_directory
        self._timeout_seconds = timeout_seconds
        self._redaction_service = (
            redaction_service
            if redaction_service is not None
            else SensitiveDataRedactionService()
        )

    def run(
        self,
        arguments: list[str],
        failure_prefix: str = GIT_COMMAND_FAILURE_PREFIX,
    ) -> str:
        environment = self._build_environment()

        try:
            completed_process = subprocess.run(
                [*GIT_COMMAND_PREFIX, *arguments],
                cwd=self._working_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError("Git executable was not found.") from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                f"Git command timed out after {self._timeout_seconds} seconds."
            ) from error

        stdout = self._redaction_service.redact(completed_process.stdout.strip())
        stderr = self._redaction_service.redact(completed_process.stderr.strip())

        if completed_process.returncode != 0:
            details = stderr or stdout or f"exit code {completed_process.returncode}"
            raise RuntimeError(f"{failure_prefix}: {details}")

        output = "\n".join(part for part in (stdout, stderr) if part)
        return output or "Git command completed successfully."

    @staticmethod
    def _build_environment() -> dict[str, str]:
        environment = {
            name: os.environ[name]
            for name in GIT_ALLOWED_ENVIRONMENT_VARIABLES
            if name in os.environ
        }
        environment.update(GIT_ENVIRONMENT_OVERRIDES)
        return environment
