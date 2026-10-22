from copy import deepcopy

from harness.models.groq_tool_type import GroqToolType
from harness.models.tool_schema import ToolSchema
from harness.validators.tools_validator import ToolsValidator


class GroqSchemaBuilder:
    """Build native Groq function definitions from shared tool schemas."""

    def build_schema(self, tools: list[ToolSchema]) -> list[GroqToolType]:
        ToolsValidator.validate(tools)

        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": deepcopy(tool["parameters"]),
                },
            }
            for tool in tools
        ]
