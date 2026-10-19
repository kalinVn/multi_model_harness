import json
import unittest

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.parser.response_parser import prepare_model_response

IDS = ("bc950638-61a9-4662-a330-76c77c43225d", "99f97142-ae4f-404f-a0f5-81a998a42df6")


class ModelResponseParserTest(unittest.TestCase):
    def test_empty_response_has_specific_error(self):
        for raw in ("", " \n\t"):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "response is empty"):
                prepare_model_response(raw)

    def test_final_response(self):
        self.assertEqual(prepare_model_response(json.dumps(dict(
            text="Finished.", tool_calls=[], tool_result_summaries=[]
        ))), ModelResponse(text="Finished."))

    def test_optional_tool_result_output_requests(self):
        parsed = prepare_model_response(json.dumps(dict(
            text="",
            tool_calls=[],
            tool_result_summaries=[],
            tool_result_output_requests=list(IDS),
        )))

        self.assertEqual(parsed.tool_result_output_requests, list(IDS))

    def test_one_and_multiple_calls_with_empty_text_and_summaries(self):
        calls = [dict(tool="read_file", arguments={"path": "a.py"}),
                 dict(tool="bash", arguments={"command": "pwd", "nested": [None, True, {"x": 1}]})]
        summaries = [dict(id=id_, summary=f"Result {i}") for i, id_ in enumerate(IDS)]
        for count in (1, 2):
            with self.subTest(count=count):
                parsed = prepare_model_response(json.dumps(dict(
                    text="", tool_calls=calls[:count], tool_result_summaries=summaries)))
                self.assertEqual(parsed.text, "")
                self.assertEqual(parsed.tool_calls, [ToolCall(c["tool"], c["arguments"]) for c in calls[:count]])
                self.assertEqual(parsed.tool_result_summaries,
                                 [ToolResultSummary(s["id"], s["summary"]) for s in summaries])

    def test_malformed_json_is_rejected(self):
        for raw in ("", "plain answer", "{", '{} trailing', '```json\n{}\n```',
                    '{"text":"a","text":"b"}',
                    '{"text":"","tool_calls":[{"tool":"x","arguments":{"x":NaN}}],"tool_result_summaries":[]}',
                    '{"text":"","tool_calls":[{"tool":"x","arguments":{"x":1e999}}],"tool_result_summaries":[]}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                prepare_model_response(raw)

    def test_invalid_fields_and_nested_types_are_rejected(self):
        valid = dict(text="", tool_calls=[], tool_result_summaries=[])
        invalid = [None, [], 1, {}, {**valid, "extra": 1}]
        for field in valid:
            invalid.append({k: v for k, v in valid.items() if k != field})
        for value in (None, 1, True, [], {}):
            invalid.append({**valid, "text": value})
        for field in ("tool_calls", "tool_result_summaries"):
            for value in (None, "", {}, True, 1):
                invalid.append({**valid, field: value})
        for value in (None, "", {}, True, 1, [None], [1], [""]):
            invalid.append({**valid, "tool_result_output_requests": value})
        for call in (None, [], "x", {}, {"tool": "x"},
                     {"tool": 1, "arguments": {}}, {"tool": " ", "arguments": {}},
                     *({"tool": "x", "arguments": x} for x in (None, [], "", 1, True))):
            invalid.append({**valid, "tool_calls": [call]})
        for summary in (None, [], "x", {}, {"id": IDS[0]},
                        *({"id": x, "summary": "ok"} for x in (None, 1, True, [], {}, "")),
                        *({"id": IDS[0], "summary": x} for x in (None, 1, True, [], {}))):
            invalid.append({**valid, "tool_result_summaries": [summary]})
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                prepare_model_response(json.dumps(value))
        with self.assertRaises(ValueError):
            prepare_model_response(None)
