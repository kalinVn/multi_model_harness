import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from harness.builder.tool_parameters_builder import (
    build_tools_context,
    build_tool_parameters,
)
from harness.config.git_tool_config import GIT_TOOL_PARAMETER_OBJECT
from harness.tools.bash_tool import BashTool
from harness.tools.git_tool import GitTool
from harness.tools.read_file_tool import ReadFileTool
from harness.tools.write_file_tool import WriteFileTool


class ToolParametersBuilderTest(unittest.TestCase):
    def test_validates_tools_before_building_schemas(self):
        tool = Mock()
        tool.name = "example"
        tool.description = "Example tool."
        tool.get_parameter_object.return_value = {
            "type": "object",
            "properties": {},
            "required": [],
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
                    },
                    "minItems": 1,
                    "maxItems": 5,
                },
            },
            "required": ["mode"],
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
        self.assertNotIn("additionalProperties", parameters)

    def test_git_schema_is_preserved(self):
        tool = GitTool()

        schema = build_tool_parameters([tool])[0]

        self.assertEqual(
            schema["parameters"],
            GIT_TOOL_PARAMETER_OBJECT,
        )
        self.assertEqual(
            schema["parameters"]["required"],
            ["commands"],
        )

    def test_batch_tool_schemas_use_declared_arrays_without_additional_properties(self):
        schemas = {
            schema["name"]: schema["parameters"]
            for schema in build_tool_parameters(
                [ReadFileTool(), WriteFileTool(), BashTool(), GitTool()]
            )
        }

        self.assertEqual(schemas["read_file"]["required"], ["paths"])
        self.assertEqual(schemas["write_file"]["required"], ["files"])
        self.assertEqual(schemas["bash"]["required"], ["commands"])
        self.assertEqual(schemas["git"]["required"], ["commands"])
        self.assertEqual(
            schemas["write_file"]["properties"]["files"]["items"][
                "required"
            ],
            ["path", "content"],
        )
        for schema in schemas.values():
            self.assertFalse(schema["additionalProperties"])
        self.assertFalse(
            schemas["write_file"]["properties"]["files"]["items"][
                "additionalProperties"
            ]
        )

    def test_tool_usage_context_contains_no_tool_definitions(self):
        tool = Mock()
        tool.name = "secret_tool_name"

        context = build_tools_context([tool])

        self.assertNotIn(tool.name, context)
        self.assertNotIn("Tool:", context)
        self.assertNotIn("Arguments:", context)
        self.assertIn("only when its schema explicitly allows", context)


if __name__ == "__main__":
    unittest.main()
