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
                    "parameters_json_schema": tool["parameters"],
                }
            )

        if not tools_obj:
            return []

        return [{"function_declarations": tools_obj}]
