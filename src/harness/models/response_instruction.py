from harness.config.response.model_response_config import MODEL_RESPONSE_INSTRUCTION, TOOL_CALL_INSTRUCTION


MODEL_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {"type": "string"},
                    "arguments": {"type": "object"}
                },
                "required": ["tool", "arguments"]
            }
        },
        "tool_result_output_requests": {
            "type": "array",
            "items": {"type": "string"}
        },
        "task_status": {
            "type": "string",
            "enum": ["in_progress", "completed", "blocked"]
        }
    },
    "required": ["text", "tool_calls", "task_status"]
}
