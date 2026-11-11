import math
import unittest

from harness.validators.model_response_validator import ModelResponseValidator


class ModelResponseValidatorTest(unittest.TestCase):
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
            "tool_result_summaries",
        )

    def test_response_fields_accept_unrecognized_fields(self):
        ModelResponseValidator.validate_response_fields({
            "text": "",
            "tool_calls": [],
            "tool_result_summaries": [],
            "metadata": {"provider": "test"}
        })

    def test_nested_fields_error_is_preserved(self):
        with self.assertRaises(ValueError) as raised:
            ModelResponseValidator.validate_fields({}, ("tool", "arguments"), "tool_calls[0]")

        self.assertEqual(
            str(raised.exception),
            "tool_calls[0] must be an object containing: tool, arguments",
        )

    def test_nested_fields_accept_unrecognized_fields(self):
        ModelResponseValidator.validate_fields(
            {"tool": "read_file", "arguments": {}, "metadata": {}},
            ("tool", "arguments"),
            "tool_calls[0]"
        )
