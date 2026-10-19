# Use native function calling when the user's request requires an available tool.
# Do not describe a function call in text or JSON content. Invoke the function.
# When invoking a function, leave message content empty.
#
# Example:
# User: "Create a file hello.txt containing Hello World."
#
# {
#   "id": "chatcmpl-example123",
#   "object": "chat.completion",
#   "created": 1792314000,
#   "model": "llama-3.3-70b-versatile",
#   "choices": [
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": null,
#         "tool_calls": [
#           {
#             "id": "call_123",
#             "type": "function",
#             "function": {
#               "name": "write_file",
#               "arguments": "{\"path\":\"hello.txt\",\"content\":\"Hello World\"}"
#             }
#           }
#         ]
#       },
#       "finish_reason": "tool_calls"
#     }
#   ],
#   "usage": {
#     "prompt_tokens": 150,
#     "completion_tokens": 30,
#     "total_tokens": 180
#   }
# }
# The function call is returned in message.tool_calls,
# not as JSON text in message.content.



# ============================================================
# Explanation: tool_result_summaries
# ============================================================
#
# Original instruction:
#
# The tool_result_summaries array contains objects with exactly
# id and summary, both strings.
#
# Meaning:
#
# The model must summarize results from previously executed tools.
#
# Each summary object must contain exactly two string fields:
#
# - id: The original ID assigned to the executed tool result.
# - summary: A concise summary of that tool's output.
#
# The model must never invent result IDs.
# If there are no results to summarize, return an empty array.
#
# ------------------------------------------------------------
# Example
# ------------------------------------------------------------
#
# User request:
# "Read config.py and explain its contents."
#
# The Harness executes:
# read_file(path="config.py")
#
# Example tool result:
#
# Tool result ID: result_123
# Output: The file contains application configuration settings.
#
# Expected model response (message.content):
#
# {
#   "text": "The file config.py contains application configuration settings.",
#   "tool_calls": [],
#   "tool_result_summaries": [
#     {
#       "id": "result_123",
#       "summary": "Successfully read config.py. The file contains application configuration settings."
#     }
#   ]
# }
#
# Important:
#
# - "result_123" must be an actual ID provided by the Harness.
# - "summary" describes the previously executed tool result.
# - "tool_calls" is empty because no new tool is being requested.
# - This JSON is returned in message.content, not message.tool_calls.
# - This is an illustrative example, not an actual model response.
#
# The comments are developer documentation only.
# They must not be included in GROQ_RESPONSE_INSTRUCTION.
# ============================================================.



GROQ_RESPONSE_INSTRUCTION = """
Use native function calling when the user's request requires an available tool.
Do not describe a function call in text or JSON content. Invoke the function.
When invoking a function, leave message content empty.

When answering the user without a function call, return only this JSON object:
{
    "text":"Your actual answer",
    "tool_calls":[],
    "tool_result_summaries":[]
}

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
