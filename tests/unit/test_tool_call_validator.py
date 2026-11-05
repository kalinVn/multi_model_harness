import unittest

from harness.domain.tool_call import ToolCall
from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_call_validator import ToolCallValidator


class ToolCallValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.available_tools: list[ToolDefinition] = [
            {
                "name": "read_file",
                "description": "Reads a file.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False
                }
            }
        ]

    def test_accepts_calls_to_tools_available_for_request(self):
        ToolCallValidator.validate([ToolCall("read_file")], self.available_tools)

    def test_rejects_calls_to_tools_unavailable_for_request(self):
        for tool_call in (ToolCall("bash"), ToolCall("")):
            with self.subTest(tool=tool_call.name):
                with self.assertRaisesRegex(ValueError, "Model returned an unavailable tool"):
                    ToolCallValidator.validate([tool_call], self.available_tools)

    def test_rejects_tool_calls_when_request_has_no_tools(self):
        with self.assertRaisesRegex(ValueError, "Model returned an unavailable tool"):
            ToolCallValidator.validate([ToolCall("read_file")], [])

    def test_validates_provider_tool_call_arguments(self):
        ToolCallValidator.validate_arguments([ToolCall("read_file")], "Gemini")

        with self.assertRaisesRegex(ValueError, "Gemini tool arguments must be an object"):
            ToolCallValidator.validate_arguments([ToolCall("read_file", ["README.md"])], "Gemini")

    def test_rejects_text_encoded_calls_for_native_tool_providers(self):
        with self.assertRaisesRegex(
            ValueError,
            "Gemini must return tool calls as native function calls"
        ):
            ToolCallValidator.validate_native_tool_calls([ToolCall("read_file")], "Gemini")


if __name__ == "__main__":
    unittest.main()
