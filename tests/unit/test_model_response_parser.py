import json
import unittest

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.parser.response_parser import prepare_model_response


class ModelResponseParserTest(unittest.TestCase):
    def test_parses_text_tool_calls_and_output_requests(self):
        response = prepare_model_response(json.dumps({
            "text": "Continue",
            "tool_calls": [{"tool": "read_file", "arguments": {"paths": ["README.md"]}}],
            "tool_result_output_requests": ["result-1"]
        }))

        self.assertEqual(response, ModelResponse(
            text="Continue",
            tool_calls=[ToolCall("read_file", {"paths": ["README.md"]})],
            tool_result_output_requests=["result-1"]
        ))

    def test_output_requests_are_optional(self):
        response = prepare_model_response('{"text":"Done","tool_calls":[]}')

        self.assertEqual(response, ModelResponse(text="Done"))

    def test_parses_supported_task_status_values(self):
        for task_status in ("in_progress", "completed", "blocked"):
            with self.subTest(task_status=task_status):
                response = prepare_model_response(json.dumps({
                    "text": "Status",
                    "tool_calls": [],
                    "task_status": task_status
                }))

                self.assertEqual(response.task_status, task_status)

    def test_missing_task_status_remains_unknown_and_invalid_status_is_rejected(self):
        response = prepare_model_response('{"text":"Done","tool_calls":[]}')

        self.assertIsNone(response.task_status)

        for task_status in ("finished", 1, []):
            with self.subTest(task_status=task_status), self.assertRaisesRegex(ValueError, "task_status"):
                prepare_model_response(json.dumps({
                    "text": "Done",
                    "tool_calls": [],
                    "task_status": task_status
                }))

    def test_invalid_json_and_fields_are_rejected(self):
        invalid_responses = [
            "",
            "not-json",
            '{"text":"Done"}',
            '{"text":"Done","tool_calls":"none"}',
            '{"text":"Done","tool_calls":[],"tool_result_output_requests":"result-1"}',
            '{"text":"Done","tool_calls":[{"tool":"read_file"}]}',
            '{"text":"Done","tool_calls":[{"tool":"read_file","arguments":{"x":NaN}}]}'
        ]

        for response in invalid_responses:
            with self.subTest(response=response), self.assertRaises(ValueError):
                prepare_model_response(response)

    def test_unrecognized_fields_are_ignored(self):
        response = prepare_model_response('{"text":"Done","tool_calls":[],"extra":true}')

        self.assertEqual(response, ModelResponse(text="Done"))


if __name__ == "__main__":
    unittest.main()
