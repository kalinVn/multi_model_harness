import unittest
from copy import deepcopy
from unittest.mock import Mock

from harness.builder.tools_schema_builder import (
    build_tools_context,
    build_tools_schema,
)
from harness.config.git_tool_config import GIT_TOOL_ARGUMENTS_SCHEMA
from harness.tools.git_tool import GitTool


class ToolsSchemaBuilderTest(unittest.TestCase):
    def test_builds_structured_schema_with_complete_constraints(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.arguments_schema = {
            "mode": {
                "type": "string",
                "description": "Execution mode.",
                "enum": ["safe", "fast"],
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "minLength": 1},
                    },
                    "required": ["name"],
                    "additionalProperties": False,
                },
                "minItems": 1,
                "maxItems": 5,
                "x-required": False,
            },
        }
        original = deepcopy(tool.arguments_schema)

        schemas = build_tools_schema([tool])

        self.assertEqual(tool.arguments_schema, original)
        self.assertEqual(schemas[0]["name"], "example")
        parameters = schemas[0]["parameters"]
        self.assertEqual(parameters["required"], ["mode"])
        self.assertEqual(
            parameters["properties"]["mode"]["enum"],
            ["safe", "fast"],
        )
        self.assertEqual(
            parameters["properties"]["items"]["items"]["properties"]
            ["name"]["minLength"],
            1,
        )
        self.assertNotIn(
            "x-required",
            parameters["properties"]["items"],
        )
        self.assertFalse(parameters["additionalProperties"])

    def test_git_schema_is_preserved(self):
        tool = GitTool()

        schema = build_tools_schema([tool])[0]

        self.assertEqual(
            schema["parameters"]["properties"],
            GIT_TOOL_ARGUMENTS_SCHEMA,
        )
        self.assertEqual(
            schema["parameters"]["required"],
            ["command_name", "command"],
        )

    def test_tool_usage_context_contains_no_tool_definitions(self):
        tool = Mock()
        tool.name = "secret_tool_name"

        context = build_tools_context([tool])

        self.assertNotIn(tool.name, context)
        self.assertNotIn("Tool:", context)
        self.assertNotIn("Arguments:", context)


if __name__ == "__main__":
    unittest.main()
