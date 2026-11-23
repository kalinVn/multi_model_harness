import unittest

from harness.parser.command_response_parser import parse_command_response
from harness.validators.command_response_validator import CommandResponseValidator


class CommandResponseValidatorTest(unittest.TestCase):
    def test_accepts_nonempty_answer(self):
        self.assertTrue(CommandResponseValidator().validate('{"answer":"Done"}'))
        self.assertEqual(parse_command_response('{"answer":"Done"}'), "Done")

    def test_rejects_invalid_command_responses(self):
        invalid_responses = [
            "",
            "not-json",
            "[]",
            "{}",
            '{"answer":1}',
            '{"answer":""}',
            '{"answer":"   "}',
            '{"answer":"Done","extra":"value"}'
        ]

        for response in invalid_responses:
            with self.subTest(response=response):
                self.assertFalse(CommandResponseValidator().validate(response))
                self.assertIsNone(parse_command_response(response))


if __name__ == "__main__":
    unittest.main()
