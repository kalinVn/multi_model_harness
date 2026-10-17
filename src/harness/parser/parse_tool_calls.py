import json

from harness.domain.tool_call import ToolCall


def parse_tool_calls(text: str) -> list[ToolCall]:
    cleaned = text.strip()

    if not cleaned:
        return []

    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()

    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, dict):
        return []

    tool_name = data.get("tool")
    arguments = data.get("arguments", {})

    if not isinstance(tool_name, str):
        return []

    if not isinstance(arguments, dict):
        return []

    return [ToolCall(name=tool_name, arguments=arguments)]
