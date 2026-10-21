import json
import math
import unittest
from unittest.mock import patch

from harness.validators.model_response_validator import ModelResponseValidator


class ModelResponseValidatorTest(unittest.TestCase):
    def test_plain_text_response_is_valid(self):
        self.assertTrue(
            ModelResponseValidator.is_plain_text_response(
                False,
                None,
                "Hello",
            )
        )

    def test_json_response_is_not_plain_text(self):
        self.assertFalse(
            ModelResponseValidator.is_plain_text_response(
                False,
                None,
                '{"text":"Hello"}',
            )
        )

    def test_empty_response_is_not_plain_text(self):
        for response_text in (None, "", "   "):
            with self.subTest(response_text=response_text):
                self.assertFalse(
                    ModelResponseValidator.is_plain_text_response(
                        False,
                        None,
                        response_text,
                    )
                )

    def test_native_tool_calls_prevent_plain_text_response(self):
        self.assertFalse(
            ModelResponseValidator.is_plain_text_response(
                False,
                [object()],
                "Hello",
            )
        )

    def test_command_plain_text_is_left_for_orchestrator_validation(self):
        self.assertTrue(
            ModelResponseValidator.is_plain_text_response(
                True,
                None,
                "Command completed",
            )
        )

    def test_complete_json_markdown_fence_is_unwrapped(self):
        self.assertEqual(
            ModelResponseValidator.unwrap_json_code_fence(
                '```json\n{"text":"Hello"}\n```'
            ),
            '{"text":"Hello"}',
        )

    def test_non_fenced_or_empty_markdown_is_not_unwrapped(self):
        for response_text in (None, "", '{"text":"Hello"}', "```json\n```"):
            with self.subTest(response_text=response_text):
                self.assertIsNone(
                    ModelResponseValidator.unwrap_json_code_fence(response_text)
                )

    def test_valid_command_response_is_accepted(self):
        response_text = json.dumps(
            {
                "answer": "Done",
                "command_summary": "Command completed.",
            }
        )

        self.assertTrue(
            ModelResponseValidator.is_valid_command_response(
                True,
                None,
                response_text,
            )
        )

    def test_invalid_command_response_is_rejected(self):
        for response_text in (None, "invalid", json.dumps({"answer": "Done"})):
            with self.subTest(response_text=response_text):
                self.assertFalse(
                    ModelResponseValidator.is_valid_command_response(
                        True,
                        None,
                        response_text,
                    )
                )

    def test_native_tool_calls_prevent_command_response(self):
        with patch(
            "harness.validators.model_response_validator.parse_command_response"
        ) as parse_command_response:
            self.assertFalse(
                ModelResponseValidator.is_valid_command_response(
                    True,
                    [object()],
                    None,
                )
            )
            parse_command_response.assert_not_called()

    def test_command_parser_is_skipped_when_command_response_is_not_required(self):
        with patch(
            "harness.validators.model_response_validator.parse_command_response"
        ) as parse_command_response:
            self.assertFalse(
                ModelResponseValidator.is_valid_command_response(
                    False,
                    None,
                    None,
                )
            )
            parse_command_response.assert_not_called()

    def test_retry_limit_reached(self):
        self.assertTrue(ModelResponseValidator.has_exhausted_retries(2, 2))

    def test_retry_limit_not_reached(self):
        self.assertFalse(ModelResponseValidator.has_exhausted_retries(1, 2))

    def test_nested_non_finite_numbers_are_rejected(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaisesRegex(
                ValueError,
                "JSON numbers must be finite",
            ):
                ModelResponseValidator.validate_finite_numbers_data(
                    {"nested": [{"value": value}]}
                )

    def test_response_fields_error_is_preserved(self):
        with self.assertRaises(ValueError) as raised:
            ModelResponseValidator.validate_response_fields({"text": ""})

        self.assertEqual(
            str(raised.exception),
            "response must contain text, tool_calls, and "
            "tool_result_summaries, with optional "
            "tool_result_output_requests",
        )

    def test_exact_fields_error_is_preserved(self):
        with self.assertRaises(ValueError) as raised:
            ModelResponseValidator.validate_fields({}, ("tool", "arguments"), "tool_calls[0]")

        self.assertEqual(
            str(raised.exception),
            "tool_calls[0] must be an object with exactly: tool, arguments",
        )
