import unittest
from types import SimpleNamespace

from harness.validators.tool_validator import ToolValidator


def make_tool(
    name="example",
    description="Example tool.",
    parameter_object=None,
):
    if parameter_object is None:
        parameter_object = {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to use.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        }
    return SimpleNamespace(
        name=name,
        description=description,
        get_parameter_object=lambda: parameter_object,
    )


class ToolValidatorTest(unittest.TestCase):
    def test_accepts_valid_tool_definitions(self):
        ToolValidator.validate([
            make_tool(),
            make_tool(name="batch-tool"),
        ])

    def test_rejects_missing_or_invalid_tool_names(self):
        for name in (None, "", "   ", "1tool", "invalid name", "a" * 65):
            with self.subTest(name=name), self.assertRaises(ValueError):
                ToolValidator.validate([make_tool(name=name)])

    def test_preserves_duplicate_tool_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "Duplicate tool schema: example",
        ):
            ToolValidator.validate([make_tool(), make_tool()])

    def test_rejects_invalid_tool_structure(self):
        missing_method = SimpleNamespace(
            name="example",
            description="Example tool.",
        )
        cases = [
            (make_tool(description=None), "Tool description must be a string"),
            (missing_method, "must define get_parameter_object"),
        ]

        for tool, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(
                ValueError,
                message,
            ):
                ToolValidator.validate([tool])

    def test_rejects_incomplete_parameter_objects(self):
        cases = [
            ([], "parameter object must be an object"),
            ({"type": "object"}, "missing required fields"),
            (
                {
                    "type": "array",
                    "properties": {},
                    "required": [],
                    "additionalProperties": False,
                },
                "must define type object",
            ),
            (
                {
                    "type": "object",
                    "properties": {},
                    "required": [],
                    "additionalProperties": True,
                },
                "must disable additional properties",
            ),
        ]

        for parameter_object, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(
                ValueError,
                message,
            ):
                ToolValidator.validate_parameter_object(
                    "example",
                    parameter_object,
                )

    def test_rejects_parameter_without_type_or_description(self):
        invalid_properties = [
            {"description": "Missing type."},
            {"type": "string"},
        ]

        for property_schema in invalid_properties:
            parameter_object = {
                "type": "object",
                "properties": {"value": property_schema},
                "required": ["value"],
                "additionalProperties": False,
            }
            with self.subTest(schema=property_schema), self.assertRaises(ValueError):
                ToolValidator.validate_parameter_object(
                    "example",
                    parameter_object,
                )

    def test_rejects_conflicting_schema_definitions(self):
        conflicting_schemas = [
            {"type": "string", "properties": {}},
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["missing"],
            },
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name", "name"],
            },
            {"type": "array", "items": "string"},
        ]

        for schema in conflicting_schemas:
            schema.setdefault("description", "Conflicting value.")
            parameter_object = {
                "type": "object",
                "properties": {"value": schema},
                "required": ["value"],
                "additionalProperties": False,
            }
            with self.subTest(schema=schema), self.assertRaises(ValueError):
                ToolValidator.validate_parameter_object(
                    "example",
                    parameter_object,
                )


if __name__ == "__main__":
    unittest.main()
