import re
from typing import Any

from harness.contracts.tool import Tool


class ToolValidator:
    """Validate provider-independent tool definitions before schema building."""

    TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,63}$")

    @classmethod
    def validate(cls, tools: list[Tool]) -> None:
        if not isinstance(tools, list):
            raise ValueError("Tools must be provided as a list.")

        names: set[str] = set()
        for tool in tools:
            name = getattr(tool, "name", None)
            cls._validate_tool_name(name)
            if name in names:
                raise ValueError(f"Duplicate tool schema: {name}")
            names.add(name)

            description = getattr(tool, "description", None)
            if not isinstance(description, str):
                raise ValueError(f"Tool description must be a string: {name}")

            get_parameter_object = getattr(tool, "get_parameter_object", None)
            if not callable(get_parameter_object):
                raise ValueError(
                    f"Tool must define get_parameter_object(): {name}"
                )

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
            "additionalProperties",
        }
        if not required_fields.issubset(parameter_object):
            raise ValueError(
                f"Tool parameter object is missing required fields: {tool_name}"
            )
        if parameter_object["type"] != "object":
            raise ValueError(
                f"Tool parameter object must define type object: {tool_name}"
            )
        if parameter_object["additionalProperties"] is not False:
            raise ValueError(
                "Tool parameter object must disable additional properties: "
                f"{tool_name}"
            )

        cls._validate_object_schema(
            parameter_object,
            tool_name,
            require_descriptions=True,
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
