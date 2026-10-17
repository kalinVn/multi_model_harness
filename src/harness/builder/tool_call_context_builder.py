import json

from harness.domain.tool_call import ToolCall


def build_tool_calls_context(
    tool_calls: list[ToolCall],
) -> str:
    raw_calls = [
        {
            "tool": tool_call.name,
            "arguments": tool_call.arguments,
        }
        for tool_call in tool_calls
    ]

    return "Raw tool calls:\n" + json.dumps(raw_calls, ensure_ascii=False, default=str)
