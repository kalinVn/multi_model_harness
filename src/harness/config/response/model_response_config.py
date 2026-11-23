MODEL_RESPONSE_INSTRUCTION = """
Always respond with a valid JSON object containing
these three required fields:

{
  "text": "",
  "tool_calls": [],
  "task_status": "in_progress"
}

You may also include this optional field:

{
  "tool_result_output_requests": []
}

Rules:
1. Put your user-facing answer in "text".

2. Put requested tool calls in "tool_calls".
   Each call must contain a nonempty string "tool" and an object "arguments".

3. Never invent tool result IDs or claim that
   an unexecuted tool has completed.

4. Set "task_status" to exactly one of:
   - "in_progress" when the user task still requires work or a follow-up execution.
   - "completed" only when the entire user task is finished, not merely the current response.
   - "blocked" when progress requires user information, permission, or external intervention.
   A tool-free response does not by itself mean the task is completed.

5. To request the complete output for a previous tool
   result, put its original ID in
   "tool_result_output_requests". Omit this optional field
   when no complete outputs are needed.

6. Use an empty array when there are no tool calls.

7. Return JSON only, without Markdown code fences
   or explanatory text outside the JSON.
""".strip()


# Compatibility name for callers using the previous instruction constant.
TOOL_CALL_INSTRUCTION = MODEL_RESPONSE_INSTRUCTION
