"""Strict provider-independent JSON response decoding."""
import json

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.validators.model_response_validator import ModelResponseValidator


def _parse_tool_calls(data) -> list[ToolCall]:
    """
    Construct tool calls from validated model response data.

    Example input:
        {"tool_calls": [{"tool": "bash", "arguments": {"command": "ls"}}]}

    Returns:
        A list of ToolCall objects.
    """
    tool_calls = []
    for call in data["tool_calls"]:
        tool_calls.append(ToolCall(name=call["tool"], arguments=call["arguments"]))

    return tool_calls


def _parse_tool_result_summaries(data) -> list[ToolResultSummary]:
    """
    Construct tool result summaries from validated model response data.

    Example input:
        {"tool_result_summaries": [{"id": "call_1", "summary": "Completed"}]}

    Returns:
        A list of ToolResultSummary objects.
    """
    summaries = []
    for summary in data["tool_result_summaries"]:
        summaries.append(ToolResultSummary(
            id=summary["id"],
            summary=summary["summary"],
        ))

    return summaries


def _get_output_requests(data):
    """
    Read output request IDs from validated model response data.

    Example input:
        {"tool_result_output_requests": ["result_1"]}

    Returns:
        A list of validated result IDs.
    """
    return data.get("tool_result_output_requests", [])


def prepare_model_response(text: str) -> ModelResponse:
    """Decode the complete response or raise ValueError; never infer tool execution.

    Tool-result IDs are opaque and preserved verbatim. The runner checks them
    against executed results. Tool argument schemas are validated at execution.
      Parse and validate a JSON model response.

    Args:
        text: JSON string containing the model response.

    Example (input):
        '{"text": "Hello", "tool_calls": [], "tool_result_summaries": []}'

    Example (output):
        ModelResponse(
            text="Hello",
            tool_calls=[],
            tool_result_summaries=[],
            tool_result_output_requests=[]
        )

    Returns:
        ModelResponse: The parsed and validated model response.

    Raises:
        ValueError: If the JSON or response data is invalid.
    """

    ModelResponseValidator.validate_prepare_model_response(text)

    data = json.loads(
        text,
        object_pairs_hook=ModelResponseValidator.validate_json_object_pairs,
        parse_constant=ModelResponseValidator.validate_json_constant,
    )

    response_text = data["text"]

    tool_calls = _parse_tool_calls(data)
    summaries = _parse_tool_result_summaries(data)

    output_requests = _get_output_requests(data)

    return ModelResponse(
        text=response_text,
        tool_calls=tool_calls,
        tool_result_summaries=summaries,
        tool_result_output_requests=output_requests
    )
