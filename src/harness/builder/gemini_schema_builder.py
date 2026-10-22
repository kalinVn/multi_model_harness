from copy import deepcopy
from typing import Any

from google.genai import types

from harness.models.tool_schema import ToolSchema


class GeminiSchemaBuilder:
    """Build native Gemini declarations from shared tool schemas."""

    def build_schema(self, tools: list[ToolSchema]) -> list[types.Tool]:
        names = [tool["name"] for tool in tools]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate harness tool definitions for Gemini")

        declarations: list[types.FunctionDeclaration] = []
        for tool in tools:
            parameters_data = self._prepare_schema_value(tool["parameters"])

            try:
                parameters = types.Schema.model_validate(parameters_data)
            except ValueError as error:
                raise ValueError(
                    f"Gemini does not support the schema for tool "
                    f"'{tool['name']}': {error}"
                ) from error

            declarations.append(
                types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=parameters,
                )
            )

        if not declarations:
            return []
        return [types.Tool(function_declarations=declarations)]

    def _prepare_schema_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: self._prepare_schema_value(nested_value)
                for key, nested_value in value.items()
                if key != "additionalProperties"
            }
        if isinstance(value, list):
            return [self._prepare_schema_value(item) for item in value]
        return deepcopy(value)
