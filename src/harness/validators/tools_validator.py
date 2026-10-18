from harness.models.tool_schema import ToolSchema


class ToolsValidator:
    @staticmethod
    def validate(tools: list[ToolSchema]) -> None:
        # Extract the names of all tools
        tool_names = [tool["name"] for tool in tools]

        if len(tool_names) != len(set(tool_names)):
            raise ValueError("Duplicate harness tool definitions for Groq")
