import unittest
from copy import deepcopy
from unittest.mock import Mock

from harness.builder.gemini_schema_builder import GeminiSchemaBuilder
from harness.builder.tool_parameters_builder import build_tool_parameters


class GeminiSchemaBuilderTest(unittest.TestCase):
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
        self.schemas = build_tool_parameters([tool])

    def test_gemini_builder_preserves_semantics_and_removes_unsupported_fields(self):
        original = deepcopy(self.schemas)

        tools = GeminiSchemaBuilder().build_schema(self.schemas)

        self.assertEqual(self.schemas, original)
        declaration = tools[0].function_declarations[0]
        parameters = declaration.parameters
        serialized = parameters.model_dump(by_alias=True, exclude_none=True)
        self.assertEqual(declaration.name, "example")
        self.assertEqual(parameters.required, ["mode"])
        self.assertEqual(parameters.properties["mode"].enum, ["safe", "fast"])
        self.assertEqual(parameters.properties["items"].min_items, 1)
        self.assertEqual(
            parameters.properties["items"].items.required,
            ["name"],
        )
        self.assertNotIn("additionalProperties", str(serialized))
        self.assertNotIn("additional_properties", str(serialized))


if __name__ == "__main__":
    unittest.main()
