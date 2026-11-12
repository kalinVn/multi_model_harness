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
        "tool_result_summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "summary": {"type": "string"}
                },
                "required": ["id", "summary"]
            }
        },
        "tool_result_output_requests": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["text", "tool_calls", "tool_result_summaries"]
}
