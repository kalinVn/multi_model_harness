import re
from typing import Any

from harness.contracts.tool import Tool
from harness.models.tool_definition import ToolDefinition


class ToolValidator:
    """Validate provider-independent tool definitions before schema building."""

    TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")

    @classmethod
    def validate(cls, tools: list[Tool]) -> None:
        if not isinstance(tools, list):
            raise ValueError("Tools must be provided as a list.")

        cls._validate_names([getattr(tool, "name", None) for tool in tools])

        for tool in tools:
            name = tool.name

            description = getattr(tool, "description", None)
            if not isinstance(description, str):
                raise ValueError(f"Tool description must be a string: {name}")

            get_parameter_object = getattr(tool, "get_parameter_object", None)
            if not callable(get_parameter_object):
                raise ValueError(
                    f"Tool must define get_parameter_object(): {name}"
                )

    @classmethod
    def validate_tool_names(cls, tools: list[ToolDefinition]) -> None:
        cls._validate_names([tool["name"] for tool in tools])

    @classmethod
    def _validate_names(cls, names: list[Any]) -> None:
        seen_names: set[str] = set()
        for name in names:
            cls._validate_tool_name(name)
            if name in seen_names:
                raise ValueError(f"Duplicate tool schema: {name}")
            seen_names.add(name)

    @classmethod
    def validate_parameter_object(
        cls,
        tool_name: str,
        parameter_object: Any,
    ) -> None:
        if not isinstance(parameter_object, dict):
            raise ValueError(
                f"Tool parameter object must be an object: {tool_name}"
            )

        required_fields = {
            "type",
            "properties",
            "required",
        }
        if not required_fields.issubset(parameter_object):
            raise ValueError(
                f"Tool parameter object is missing required fields: {tool_name}"
            )
        if parameter_object["type"] != "object":
            raise ValueError(
                f"Tool parameter object must define type object: {tool_name}"
            )
        if (
            "additionalProperties" in parameter_object
            and not isinstance(parameter_object["additionalProperties"], bool)
        ):
            raise ValueError(
                "Tool parameter object must define additionalProperties "
                "as a boolean: "
                f"{tool_name}"
            )

        cls._validate_object_schema(
            parameter_object,
            tool_name,
            require_descriptions=True,
        )

    @classmethod
    def validate_arguments(
        cls,
        tool_name: str,
        parameter_object: dict[str, Any],
        arguments: Any,
    ) -> None:
        """Validate runtime arguments against the declared tool schema."""
        cls._validate_argument_value(
            arguments,
            parameter_object,
            f"{tool_name} arguments",
        )

    @classmethod
    def _validate_tool_name(cls, name: Any) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tool name must be a nonempty string.")
        if cls.TOOL_NAME_PATTERN.fullmatch(name) is None:
            raise ValueError(f"Invalid tool name: {name}")

    @classmethod
    def _validate_json_schema(
        cls,
        schema: dict[str, Any],
        path: str,
        require_description: bool = False,
    ) -> None:
        schema_type = schema.get("type")
        if not isinstance(schema_type, str) or not schema_type:
            raise ValueError(f"Tool parameter schema must define a type: {path}")
        if require_description and (
            not isinstance(schema.get("description"), str)
            or not schema["description"].strip()
        ):
            raise ValueError(
                f"Tool parameter schema must define a description: {path}"
            )

        if "properties" in schema and schema_type != "object":
            raise ValueError(
                f"Conflicting tool parameter schema definitions: {path}"
            )
        if "required" in schema and schema_type != "object":
            raise ValueError(
                f"Conflicting tool parameter schema definitions: {path}"
            )
        if "items" in schema and schema_type != "array":
            raise ValueError(
                f"Conflicting tool parameter schema definitions: {path}"
            )

        if schema_type == "object":
            cls._validate_object_schema(schema, path)
        elif schema_type == "array" and "items" in schema:
            items = schema["items"]
            if not isinstance(items, dict):
                raise ValueError(f"Invalid tool parameter schema: {path}.items")
            cls._validate_json_schema(items, f"{path}.items")

    @classmethod
    def _validate_object_schema(
        cls,
        schema: dict[str, Any],
        path: str,
        require_descriptions: bool = False,
    ) -> None:
        if (
            "additionalProperties" in schema
            and not isinstance(schema["additionalProperties"], bool)
        ):
            raise ValueError(
                "Tool parameter object must define additionalProperties "
                f"as a boolean: {path}"
            )

        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError(f"Invalid tool parameter schema: {path}.properties")

        for property_name, property_schema in properties.items():
            if not isinstance(property_name, str) or not property_name.strip():
                raise ValueError(
                    f"Tool parameter name must be a nonempty string: {path}"
                )
            if not isinstance(property_schema, dict):
                raise ValueError(
                    f"Invalid tool parameter schema: {path}.{property_name}"
                )
            cls._validate_json_schema(
                property_schema,
                f"{path}.{property_name}",
                require_description=require_descriptions,
            )

        required = schema.get("required", [])
        if not isinstance(required, list) or any(
            not isinstance(name, str) or not name
            for name in required
        ):
            raise ValueError(f"Invalid tool parameter schema: {path}.required")
        has_duplicates = len(required) != len(set(required))
        has_unknown_names = not set(required).issubset(properties)
        if has_duplicates or has_unknown_names:
            raise ValueError(
                f"Conflicting tool parameter schema definitions: {path}"
            )

    @classmethod
    def _validate_argument_value(
        cls,
        value: Any,
        schema: dict[str, Any],
        path: str,
    ) -> None:
        schema_type = schema["type"]

        if schema_type == "object":
            if not isinstance(value, dict):
                raise ValueError(f"{path} must be an object.")

            properties = schema.get("properties", {})
            unexpected = set(value) - set(properties)
            if unexpected and schema.get("additionalProperties", True) is False:
                names = ", ".join(sorted(unexpected))
                raise ValueError(
                    f"{path} contains undeclared parameters: {names}"
                )

            missing = set(schema.get("required", [])) - set(value)
            if missing:
                names = ", ".join(sorted(missing))
                raise ValueError(
                    f"{path} is missing required parameters: {names}"
                )

            for name, nested_value in value.items():
                if name not in properties:
                    continue
                cls._validate_argument_value(
                    nested_value,
                    properties[name],
                    f"{path}.{name}",
                )
            return

        if schema_type == "array":
            if not isinstance(value, list):
                raise ValueError(f"{path} must be an array.")
            if len(value) < schema.get("minItems", 0):
                raise ValueError(f"{path} contains too few items.")
            max_items = schema.get("maxItems")
            if max_items is not None and len(value) > max_items:
                raise ValueError(f"{path} contains too many items.")
            items = schema.get("items")
            if items is not None:
                for index, item in enumerate(value):
                    cls._validate_argument_value(
                        item,
                        items,
                        f"{path}[{index}]",
                    )
            return

        expected_types = {
            "string": str,
            "boolean": bool,
            "integer": int,
            "number": (int, float),
        }
        expected_type = expected_types.get(schema_type)
        if expected_type is None:
            return
        if isinstance(value, bool) and schema_type in {"integer", "number"}:
            raise ValueError(f"{path} must be a {schema_type}.")
        if not isinstance(value, expected_type):
            raise ValueError(f"{path} must be a {schema_type}.")

        if "enum" in schema and value not in schema["enum"]:
            raise ValueError(f"{path} contains an unsupported value.")
