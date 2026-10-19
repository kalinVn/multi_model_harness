"""Strict provider-independent JSON response decoding."""
import json

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.validators.model_response_validator import ModelResponseValidator
from harness.validators.string_validator import StringValidator


def _parse_tool_calls(data) -> list[ToolCall]:
    """
    Parse and validate tool calls from the model response data.

    Example (valid):
        {"tool_calls": [{"tool": "bash", "arguments": {"command": "ls"}}]}

    Example (invalid):
        {"tool_calls": [{"tool": 123, "arguments": {}}]}

    Returns:
        A list of validated ToolCall objects.
    """
    tool_calls = []
    for index, call in enumerate(data["tool_calls"]):
        path = f"tool_calls[{index}]"
        name = StringValidator.validate_string(call["tool"], f"{path}.tool", nonempty=True)
        ModelResponseValidator.validate_fields(call, ("tool", "arguments"), path)
        
        ModelResponseValidator.validate_call_arguments(call["arguments"], path)
        tool_calls.append(ToolCall(name=name, arguments=call["arguments"]))

    return tool_calls


def _parse_tool_result_summaries(data) -> list[ToolResultSummary]:
    """
    Parse and validate tool result summaries from the model response data.

    Example (valid):
        {"tool_result_summaries": [{"id": "call_1", "summary": "Command completed"}]}

    Example (invalid):
        {"tool_result_summaries": [{"id": 123, "summary": "Command completed"}]}

    Returns:
        A list of validated ToolResultSummary objects.
    """
    summaries = []
    for index, summary in enumerate(data["tool_result_summaries"]):
        path = f"tool_result_summaries[{index}]"
        ModelResponseValidator.validate_fields(summary, ("id", "summary"), path)
        summaries.append(ToolResultSummary(
            id=StringValidator.validate_string(summary["id"], f"{path}.id", nonempty=True),
            summary=StringValidator.validate_string(summary["summary"], f"{path}.summary"),
        ))

    return summaries


def _get_output_requests(data):
    """
    Read and validate tool result output request IDs from model response data.

    Example (valid):
        {"tool_result_output_requests": ["result_1"]}

    Example (invalid):
        {"tool_result_output_requests": "result_1"}

    Returns:
        A list of validated result IDs.
    """
    output_requests_data = data.get("tool_result_output_requests", [])
    ModelResponseValidator.validate_output_request_data(output_requests_data)

    output_requests = [
        StringValidator.validate_string(result_id, f"tool_result_output_requests[{index}]", nonempty=True)
        for index, result_id in enumerate(output_requests_data)
    ]

    return output_requests


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

    ModelResponseValidator.validate(text)

    # Parse the JSON response into a Python object (dictionary).
    #
    # Example of valid JSON:
    # {"text": "Hello", "tool_calls": [], "tool_result_summaries": []}
    # Result: Python dictionary with accessible fields.
    #
    # Example of duplicate JSON fields:
    # {"text": "Hello", "text": "World"}
    # Result: ValueError("Duplicate JSON field: text")
    #
    # Example of invalid numeric constants:
    # {"text": "Hello", "value": NaN}
    # Result: ValueError("Invalid JSON constant: NaN")
    #
    # Reject duplicate fields and invalid numeric constants
    # such as NaN, Infinity, and -Infinity.

    try:
        data = json.loads(text, object_pairs_hook=ModelResponseValidator.validate_json_object_pairs, parse_constant=ModelResponseValidator.validate_json_constant)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Malformed model response JSON: {error.msg} "
            f"at line {error.lineno}, column {error.colno} (char {error.pos})"
        ) from error
    
    ModelResponseValidator.validate_finite_numbers_data(data)
    ModelResponseValidator.validate_response_fields(data)
    ModelResponseValidator.validate_response_list_fields(data)
    StringValidator.validate_string(data["text"], "text")
   
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
