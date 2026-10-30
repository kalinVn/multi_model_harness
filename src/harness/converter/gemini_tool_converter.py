from copy import deepcopy
from typing import Any

from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_validator import ToolValidator


class GeminiToolConverter:
    """Convert shared tool definitions to Gemini declaration dictionaries."""

    def convert_tools(
        self,
        tools: list[ToolDefinition],
    ) -> list[dict[str, Any]]:
        ToolValidator.validate_tool_names(tools)

        tools_obj: list[dict[str, Any]] = []

        for tool in tools:
            tools_obj.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": self._prepare_schema_value(tool["parameters"]),
                }
            )

        if not tools_obj:
            return []

        return [{"function_declarations": tools_obj}]

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
