import unittest

from harness.validators.string_validator import StringValidator


class StringValidatorTest(unittest.TestCase):
    def test_validated_string_is_returned(self):
        self.assertEqual(StringValidator.validate_string("value", "field"), "value")

    def test_string_errors_are_preserved(self):
        cases = (
            (1, False, "field must be a string"),
            (" \n", True, "field must be a nonempty string"),
        )
        for value, nonempty, expected in cases:
            with self.subTest(value=value, nonempty=nonempty), self.assertRaises(ValueError) as raised:
                StringValidator.validate_string(value, "field", nonempty=nonempty)

            self.assertEqual(str(raised.exception), expected)
