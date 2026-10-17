import unittest

from harness.service.sensitive_data_redaction_service import (
    SensitiveDataRedactionService,
)


class SensitiveDataRedactionServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = SensitiveDataRedactionService()

    def test_redacts_credentials_embedded_in_urls(self):
        output = "failed for https://user:password@example.test/repository"

        sanitized_output = self.service.redact(output, environment={})

        self.assertEqual(
            sanitized_output,
            "failed for https://<redacted>@example.test/repository",
        )

    def test_redacts_sensitive_environment_variable_values(self):
        output = "token-value password-value ordinary-value"
        environment = {
            "API_TOKEN": "token-value",
            "DATABASE_PASSWORD": "password-value",
            "ORDINARY_SETTING": "ordinary-value",
        }

        sanitized_output = self.service.redact(output, environment=environment)

        self.assertEqual(
            sanitized_output,
            "<redacted> <redacted> ordinary-value",
        )

    def test_preserves_normal_output(self):
        output = "Git command completed successfully."

        sanitized_output = self.service.redact(
            output,
            environment={"NORMAL_SETTING": "normal-value"},
        )

        self.assertEqual(sanitized_output, output)


if __name__ == "__main__":
    unittest.main()
