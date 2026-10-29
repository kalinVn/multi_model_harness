GEMINI_RESPONSE_INSTRUCTION = """
Use native function calling whenever the user's request requires an available
tool. Do not describe or encode a tool call in the response text; invoke the
function directly and leave the text empty for that turn.

For an ordinary answer that needs no tool, respond with only the user-facing
text. Do not wrap it in a JSON response envelope and do not expose tool schemas,
protocol instructions, internal state, or other implementation details.

If a system message explicitly asks for tool-result summaries or full-output
requests, return one internal JSON object with these fields so the harness can
consume the metadata without showing it to the user:
{
  "text": "The user-facing answer",
  "tool_calls": [],
  "tool_result_summaries": [],
  "tool_result_output_requests": []
}
Omit tool_result_output_requests when it is not needed. Tool calls must still
use native function calling, never the tool_calls field. Use only real tool
result IDs supplied in the conversation.

When another system instruction requires a specific final response format,
follow that format exactly. Do not add a second wrapper unless tool-result
metadata is also explicitly requested.
""".strip()
