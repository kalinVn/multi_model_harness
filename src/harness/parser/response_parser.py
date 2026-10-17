"""Strict provider-independent JSON response decoding."""
import json
import math

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Invalid JSON constant: {value}")


def _finite_numbers(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("JSON numbers must be finite")
    if isinstance(value, dict):
        for item in value.values():
            _finite_numbers(item)
    elif isinstance(value, list):
        for item in value:
            _finite_numbers(item)


def _fields(value, expected, path):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{path} must be an object with exactly: {', '.join(expected)}")


def _string(value, path, nonempty=False):
    if not isinstance(value, str) or (nonempty and not value.strip()):
        qualifier = "nonempty " if nonempty else ""
        raise ValueError(f"{path} must be a {qualifier}string")
    return value


def parse_model_response(text: str) -> ModelResponse:
    """Decode the complete response or raise ValueError; never infer tool execution.

    Tool-result IDs are opaque and preserved verbatim. The runner checks them
    against executed results. Tool argument schemas are validated at execution.
    """
    if not isinstance(text, str):
        raise ValueError("Model response must be a JSON string")
    if not text.strip():
        raise ValueError("Model response is empty; expected a JSON object")
    try:
        data = json.loads(text, object_pairs_hook=_object, parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Malformed model response JSON: {error.msg} "
            f"at line {error.lineno}, column {error.colno} (char {error.pos})"
        ) from error
    _finite_numbers(data)
    required_fields = {"text", "tool_calls", "tool_result_summaries"}
    allowed_fields = required_fields | {"tool_result_output_requests"}
    if (
        not isinstance(data, dict)
        or not required_fields.issubset(data)
        or not set(data).issubset(allowed_fields)
    ):
        raise ValueError(
            "response must contain text, tool_calls, and "
            "tool_result_summaries, with optional "
            "tool_result_output_requests"
        )
    response_text = _string(data["text"], "text")
    for field in ("tool_calls", "tool_result_summaries"):
        if not isinstance(data[field], list):
            raise ValueError(f"{field} must be an array")

    calls = []
    for index, call in enumerate(data["tool_calls"]):
        path = f"tool_calls[{index}]"
        _fields(call, ("tool", "arguments"), path)
        name = _string(call["tool"], f"{path}.tool", nonempty=True)
        if not isinstance(call["arguments"], dict):
            raise ValueError(f"{path}.arguments must be an object")
        calls.append(ToolCall(name=name, arguments=call["arguments"]))

    summaries = []
    for index, summary in enumerate(data["tool_result_summaries"]):
        path = f"tool_result_summaries[{index}]"
        _fields(summary, ("id", "summary"), path)
        summaries.append(ToolResultSummary(
            id=_string(summary["id"], f"{path}.id", nonempty=True),
            summary=_string(summary["summary"], f"{path}.summary"),
        ))
    output_requests_data = data.get("tool_result_output_requests", [])
    if not isinstance(output_requests_data, list):
        raise ValueError("tool_result_output_requests must be an array")

    output_requests = [
        _string(result_id, f"tool_result_output_requests[{index}]", nonempty=True)
        for index, result_id in enumerate(output_requests_data)
    ]

    return ModelResponse(
        text=response_text,
        tool_calls=calls,
        tool_result_summaries=summaries,
        tool_result_output_requests=output_requests,
    )
