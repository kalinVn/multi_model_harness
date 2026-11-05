from harness.domain.tool_call import ToolCall
from harness.models.tool_definition import ToolDefinition


class ToolCallValidator:
    """Validate model tool calls against the tools available for the request."""

    @staticmethod
    def validate_arguments(tool_calls: list[ToolCall], provider_name: str) -> None:
        for tool_call in tool_calls:
            if not isinstance(tool_call.arguments, dict):
                raise ValueError(f"{provider_name} tool arguments must be an object")

    @staticmethod
    def validate_native_tool_calls(tool_calls: list[ToolCall], provider_name: str) -> None:
        if tool_calls:
            raise ValueError(f"{provider_name} must return tool calls as native function calls")

    @staticmethod
    def validate(tool_calls: list[ToolCall], available_tools: list[ToolDefinition]) -> None:
        allowed_names = {tool["name"] for tool in available_tools}

        if any(not tool_call.name or tool_call.name not in allowed_names for tool_call in tool_calls):
            raise ValueError("Model returned an unavailable tool")
