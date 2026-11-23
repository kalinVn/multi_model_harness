INSTRUCTIONS = """Create or incrementally update a structured context memory summary.

Preserve important user goals, decisions, architectural constraints, completed work, unfinished work,
and significant information from tool results. Keep important tool findings concise and reference the
original tool execution ID when one is supplied. Do not include complete tool result output in the
summary. Preserve relevant information from the previous summary, remove duplication, and correctly
replace decisions that the new context explicitly supersedes. Never silently discard unresolved tasks
or important constraints.

Do not call tools or modify files. Do not invent events, tool results, execution IDs, files, decisions,
or completed actions. Use only the supplied previous summary, messages, and tool results.

Put exactly one JSON object in the ModelResponse text field with these fields:
{
  "current_goal": "string or null",
  "conversation_summary": "string",
  "decisions": ["string"],
  "constraints": ["string"],
  "important_tool_findings": [
    {
      "tool_execution_id": "existing ID or null",
      "tool_name": "string",
      "agent_id": "string or null",
      "finding": "concise string"
    }
  ],
  "important_files": ["string"],
  "current_state": "string",
  "pending_steps": ["string"],
  "active_plan_id": "string or null"
}

Return every field with the specified type and no additional fields.
"""
