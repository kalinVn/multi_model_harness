COMMAND_RESPONSE_FORMAT_INSTRUCTIONS = """
COMMAND RESPONSE FORMAT:

These instructions apply only when completing a command, not during normal conversation.

When a command is complete and no more tools are needed, put a JSON-encoded
object in the `text` string of the standard model response envelope.
This inner object has exactly one string field: `answer`, containing the normal
user-facing response.
Do not wrap the JSON in Markdown.
Keep the outer `text` and `tool_calls` fields.
This format applies only to the final response; tool-call responses must continue to use the tool protocol.
A valid outer `text` value looks like:
`{"answer":"Done"}`.
Never leave `text` empty in the final command response.
""".strip()
