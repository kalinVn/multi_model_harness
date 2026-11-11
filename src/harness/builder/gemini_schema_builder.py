from typing import Any

from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_validator import ToolValidator


class GeminiSchemaBuilder:
    """Build Gemini declaration dictionaries from shared tool schemas."""

    def build_schema(
        self,
        tools: list[ToolDefinition],
    ) -> list[dict[str, Any]]:

        ToolValidator.validate_tool_names(tools)

        declarations: list[dict[str, Any]] = []

        for tool in tools:
            declarations.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            )

        if not declarations:
            return []

        return [{"function_declarations": declarations}]
