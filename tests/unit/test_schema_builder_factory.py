import unittest
from copy import deepcopy
from unittest.mock import Mock

from harness.builder.gemini_schema_builder import GeminiSchemaBuilder
from harness.builder.tools_schema_builder import build_tools_schema


class GeminiSchemaBuilderTest(unittest.TestCase):
    def setUp(self) -> None:
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.arguments_schema = {
            "mode": {
                "type": "string",
                "enum": ["safe", "fast"],
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
                "minItems": 1,
                "x-required": False,
            },
        }
        self.schemas = build_tools_schema([tool])

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
