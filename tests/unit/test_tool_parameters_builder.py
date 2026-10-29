import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from harness.builder.tool_parameters_builder import (
    build_tools_context,
    build_tool_parameters,
)
from harness.config.git_tool_config import GIT_TOOL_PARAMETER_OBJECT
from harness.tools.git_tool import GitTool


class ToolParametersBuilderTest(unittest.TestCase):
    def test_validates_tools_before_building_schemas(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        with patch(
            "harness.builder.tool_parameters_builder.ToolValidator.validate"
        ) as validate:
            schemas = build_tool_parameters([tool])

        validate.assert_called_once_with([tool])
        tool.get_parameter_object.assert_called_once_with()
        self.assertEqual(schemas[0]["name"], "example")

    def test_builds_structured_schema_with_complete_constraints(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        parameter_object = {
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
                            "name": {"type": "string", "minLength": 1},
                        },
                        "required": ["name"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                    "maxItems": 5,
                },
            },
            "required": ["mode"],
            "additionalProperties": False,
        }
        tool.get_parameter_object.return_value = parameter_object
        original = deepcopy(parameter_object)

        schemas = build_tool_parameters([tool])

        self.assertEqual(parameter_object, original)
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
        self.assertFalse(parameters["additionalProperties"])

    def test_git_schema_is_preserved(self):
        tool = GitTool()

        schema = build_tool_parameters([tool])[0]

        self.assertEqual(
            schema["parameters"],
            GIT_TOOL_PARAMETER_OBJECT,
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
