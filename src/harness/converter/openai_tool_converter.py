from harness.builder.tool_parameters_builder import build_text_tools_context
from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_validator import ToolValidator


class OpenAIToolConverter:
    """Convert shared tool definitions to the OpenAI text tool catalog."""

    def convert_tools(self, tools: list[ToolDefinition]) -> str:
        ToolValidator.validate_tool_names(tools)
        return build_text_tools_context(tools)
