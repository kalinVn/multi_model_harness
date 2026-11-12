import unittest
from unittest.mock import Mock

from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.models.errors import ContextWindowExceeded
from harness.service.context_manager import ContextManager


class ContextManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.messages = [Message(role="user", content="Continue")]
        self.tools = [{
            "name": "read_file",
            "description": "Reads files.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }]
        self.client = Mock()

    def test_validate_returns_usage_for_complete_request(self):
        self.client.count_tokens.return_value = 250
        self.client.get_context_limits.return_value = ModelContextLimits(
            model="test-model",
            context_window=1_000,
            reserved_output_tokens=100
        )

        usage = ContextManager().validate(self.messages, self.tools, self.client)

        self.assertEqual(usage.input_tokens, 250)
        self.assertEqual(usage.available_input_tokens, 900)
        self.assertEqual(usage.remaining_tokens, 650)
        self.client.count_tokens.assert_called_once_with(self.messages, self.tools)
        self.client.get_context_limits.assert_called_once_with()

    def test_validate_uses_explicit_provider_input_limit(self):
        self.client.count_tokens.return_value = 750
        self.client.get_context_limits.return_value = ModelContextLimits(
            model="gemini-test",
            context_window=800,
            reserved_output_tokens=200,
            input_token_limit=800
        )

        usage = ContextManager().validate(self.messages, self.tools, self.client)

        self.assertEqual(usage.available_input_tokens, 800)
        self.assertEqual(usage.remaining_tokens, 50)

    def test_validate_allows_request_at_exact_input_limit(self):
        self.client.count_tokens.return_value = 900
        self.client.get_context_limits.return_value = ModelContextLimits(
            model="test-model",
            context_window=1_000,
            reserved_output_tokens=100
        )

        usage = ContextManager().validate(self.messages, self.tools, self.client)

        self.assertEqual(usage.remaining_tokens, 0)

    def test_validate_raises_detailed_error_when_input_exceeds_limit(self):
        self.client.count_tokens.return_value = 901
        self.client.get_context_limits.return_value = ModelContextLimits(
            model="test-model",
            context_window=1_000,
            reserved_output_tokens=100
        )

        with self.assertRaises(ContextWindowExceeded) as raised:
            ContextManager().validate(self.messages, self.tools, self.client)

        self.assertEqual(raised.exception.model, "test-model")
        self.assertEqual(raised.exception.input_tokens, 901)
        self.assertEqual(raised.exception.available_input_tokens, 900)
        self.assertEqual(raised.exception.exceeded_tokens, 1)

    def test_validate_rejects_invalid_token_count_and_limits(self):
        invalid_cases = [
            ("invalid", ModelContextLimits("test-model", 1_000, 100), "must be an integer"),
            (-1, ModelContextLimits("test-model", 1_000, 100), "cannot be negative"),
            (1, ModelContextLimits("test-model", 0, 0), "positive integer"),
            (1, ModelContextLimits("test-model", 100, 100), "input budget")
        ]

        for input_tokens, limits, message in invalid_cases:
            with self.subTest(input_tokens=input_tokens, limits=limits):
                self.client.count_tokens.return_value = input_tokens
                self.client.get_context_limits.return_value = limits

                with self.assertRaisesRegex(ValueError, message):
                    ContextManager().validate(self.messages, self.tools, self.client)


if __name__ == "__main__":
    unittest.main()
