"""Groq conversions at the existing text-only provider boundary."""
import json
import re

from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.parser.response_parser import parse_model_response


GROQ_RESPONSE_INSTRUCTION = """
Use native function calling when the user's request requires an available tool.
Do not describe a function call in text or JSON content. Invoke the function.
When invoking a function, leave message content empty.

When answering the user without a function call, return only this JSON object:
{"text":"Your actual answer","tool_calls":[],"tool_result_summaries":[]}
All three fields are required. The optional tool_result_output_requests field
is an array of original tool result ID strings whose complete outputs you need.
No other fields or Markdown fences are allowed.
The text field is a string. The tool_calls field in content is always empty.
When no native function call is emitted, the text field must not be empty.
If an earlier command instruction requires answer and command_summary, encode
that two-field JSON object inside text exactly as instructed.
The tool_result_summaries array contains objects with exactly id and summary,
both strings. Use only original IDs from actual previously executed results.
If there are no results to summarize, use an empty array. Never invent results.
This JSON object is message content, not a function call. There is no json tool.
Past tool calls and results are supplied as conversation text by the harness.
Messages saying "The requested tools have finished" contain completed results.
Use their Output as the result of the preceding call; do not repeat that call.
"Tool result ID" is an opaque identifier for summaries, never a file path.
After a successful read, answer from the provided Output and summarize that
result using its exact ID. Request another tool only if more work is necessary.
Answer the latest user request; use tools only when that request requires them.
""".strip()


def _tool_definitions(content: str) -> list[dict]:
    """Decode build_tools_schema output without changing the shared Tool contract.

    Current tools describe required string arguments as name -> description.
    Only the dedicated system tool catalog is interpreted as definitions.
    """
    catalog, separator, _ = content.removeprefix("Available tools:\n\n").partition(
        "\n\nUse a tool only when"
    )
    if not separator:
        raise ValueError("Invalid harness tool catalog for Groq")
    tools = []
    for block in catalog.split("\n\n"):
        match = re.fullmatch(
            r"Tool: ([\w-]+)\nDescription: ([^\n]+)\nArguments:( none|\n.+)",
            block, re.DOTALL,
        )
        if not match:
            raise ValueError("Invalid harness tool definition for Groq")
        name, description, arguments = match.groups()
        properties = {}
        if arguments != " none":
            for line in arguments.strip().splitlines():
                argument = re.fullmatch(r"- ([\w-]+): (.+)", line)
                if not argument or argument[1] in properties:
                    raise ValueError("Invalid harness tool arguments for Groq")
                properties[argument[1]] = {"type": "string", "description": argument[2]}
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                    "additionalProperties": False,
                },
            },
        })
    return tools


def map_messages(messages: list[Message]) -> tuple[list[dict[str, str]], list[dict]]:
    mapped = []
    tools = []
    for message in messages:
        content = message.content
        if message.role == "system" and content.startswith("Available tools:\n\n"):
            tools.extend(_tool_definitions(content))
            # Drop only the conflicting standalone tool-call output instructions.
            content = content.partition("\n\nTool call format:")[0]
        mapped.append({"role": message.role, "content": content})
    names = [tool["function"]["name"] for tool in tools]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate harness tool definitions for Groq")
    mapped.append({"role": "system", "content": GROQ_RESPONSE_INSTRUCTION})
    return mapped, tools


def map_response(message, tools: list[dict]) -> ModelResponse:
    native_calls = message.tool_calls or []
    if message.content and message.content.strip():
        response = parse_model_response(message.content)
    elif native_calls:
        response = ModelResponse()
    else:
        raise ValueError("Groq returned no response text or tool calls")
    if response.tool_calls:
        raise ValueError("Groq must return tool calls as native function calls")

    allowed = {tool["function"]["name"] for tool in tools}
    calls = []
    for call in native_calls:
        if call.type != "function" or call.function.name not in allowed:
            raise ValueError("Groq returned an unavailable tool")
        # Pass raw argument JSON through the shared strict parser, preserving its
        # duplicate-key/nonfinite-number checks instead of silently normalizing it.
        if not isinstance(call.function.arguments, str):
            raise ValueError("Groq tool arguments must be a JSON string")
        raw = (
            '{"text":"","tool_calls":[{"tool":'
            + json.dumps(call.function.name)
            + ',"arguments":' + call.function.arguments
            + '}],"tool_result_summaries":[]}'
        )
        parsed = parse_model_response(raw)
        if len(parsed.tool_calls) != 1 or parsed.tool_calls[0].name != call.function.name:
            raise ValueError("Groq tool arguments contain an invalid call envelope")
        calls.extend(parsed.tool_calls)
    return ModelResponse(
        text=response.text,
        tool_calls=calls,
        tool_result_summaries=response.tool_result_summaries,
        tool_result_output_requests=response.tool_result_output_requests,
    )
