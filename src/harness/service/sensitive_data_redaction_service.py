import os
import re
from collections.abc import Mapping

from harness.config.sensitive_data_redaction_config import (
    CREDENTIAL_URL_PATTERN,
    SENSITIVE_ENVIRONMENT_MARKERS,
)


class SensitiveDataRedactionService:
    """Премахва идентификационни данни и тайни от средата от изхода на процеса."""

    def redact(
        self,
        output: str,
        environment: Mapping[str, str] | None = None,
    ) -> str:
        sanitized_output = re.sub(
            CREDENTIAL_URL_PATTERN,
            r"\1<redacted>@",
            output,
        )
        source_environment = os.environ if environment is None else environment

        for name, value in source_environment.items():
            if value and any(
                marker in name.upper()
                for marker in SENSITIVE_ENVIRONMENT_MARKERS
            ):
                sanitized_output = sanitized_output.replace(value, "<redacted>")

        return sanitized_output
