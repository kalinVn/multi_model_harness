import unittest
from copy import deepcopy
from unittest.mock import Mock

from harness.builder.tool_parameters_builder import build_tool_parameters
from harness.converter.gemini_tool_converter import GeminiToolConverter
from harness.converter.openai_tool_converter import OpenAIToolConverter
from harness.converter.tool_converter_facade import ToolConverterFacade


class ToolConvertersTest(unittest.TestCase):
    def setUp(self) -> None:
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Execution mode.",
                    "enum": ["safe", "fast"],
                },
                "items": {
                    "type": "array",
                    "description": "Items to process.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                },
            },
            "required": ["mode"],
            "additionalProperties": False,
        }
        self.tools = build_tool_parameters([tool])

    def test_gemini_conversion_preserves_json_schema_unchanged(self):
        original = deepcopy(self.tools)

        converted = GeminiToolConverter().convert_tools(self.tools)

        self.assertEqual(self.tools, original)
        declaration = converted[0]["function_declarations"][0]
        parameters = declaration["parameters_json_schema"]
        self.assertEqual(declaration["name"], "example")
        self.assertEqual(declaration["description"], "Example tool.")
        self.assertNotIn("parameters", declaration)
        self.assertIs(parameters, self.tools[0]["parameters"])
        self.assertEqual(parameters["required"], ["mode"])
        self.assertEqual(
            parameters["properties"]["mode"]["enum"],
            ["safe", "fast"],
        )
        self.assertEqual(parameters["properties"]["items"]["minItems"], 1)
        self.assertEqual(
            parameters["properties"]["items"]["items"]["required"],
            ["name"],
        )
        self.assertFalse(parameters["additionalProperties"])
        self.assertFalse(
            parameters["properties"]["items"]["items"][
                "additionalProperties"
            ]
        )

    def test_openai_conversion_uses_text_tool_catalog(self):
        original = deepcopy(self.tools)

        converted = OpenAIToolConverter().convert_tools(self.tools)

        self.assertEqual(self.tools, original)
        self.assertIn("Available tools:", converted)
        self.assertIn("Tool: example", converted)
        self.assertIn("Description: Example tool.", converted)
        self.assertIn("Arguments:", converted)
        self.assertIn('"enum":["safe","fast"]', converted)

    def test_facade_selects_provider_converter(self):
        facade = ToolConverterFacade()

        self.assertEqual(
            facade.convert_tools("gemini", self.tools),
            GeminiToolConverter().convert_tools(self.tools),
        )
        self.assertEqual(
            facade.convert_tools("openai", self.tools),
            OpenAIToolConverter().convert_tools(self.tools),
        )

    def test_facade_rejects_unsupported_provider(self):
        with self.assertRaisesRegex(
            ValueError,
            "Unsupported tool converter provider: anthropic",
        ):
            ToolConverterFacade().convert_tools("anthropic", self.tools)

    def test_converters_handle_empty_tool_lists(self):
        self.assertEqual(GeminiToolConverter().convert_tools([]), [])
        self.assertEqual(
            OpenAIToolConverter().convert_tools([]),
            "No tools are currently available.",
        )
        self.assertEqual(
            ToolConverterFacade().convert_tools("gemini", []),
            [],
        )
        self.assertEqual(
            ToolConverterFacade().convert_tools("openai", []),
            "No tools are currently available.",
        )

    def test_gemini_conversion_rejects_duplicate_tool_names(self):
        duplicate_tools = [self.tools[0], deepcopy(self.tools[0])]

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate tool schema: example",
        ) as caught:
            GeminiToolConverter().convert_tools(duplicate_tools)

        self.assertNotIn("Gemini", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
