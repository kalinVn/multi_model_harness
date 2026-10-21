import json
import math
import re

from harness.parser.command_response_parser import parse_command_response
from harness.models.errors import ModelResponseFormatError
from harness.validators.string_validator import StringValidator


class ModelResponseValidator:
    @staticmethod
    def validate_prepare_model_response(text: str) -> None:
        """
        Validate JSON text before it is converted into a ModelResponse.

        Description:
            Decode the JSON securely and validate all response and nested fields.
        Parameters:
            text: The model response JSON string to validate.
        Example input: '{"text":"Hello","tool_calls":[],"tool_result_summaries":[]}'
        Example output: None
        Returns: None when the complete model response is valid.
        Raises: ValueError when the JSON or any response field is invalid.
        """
        ModelResponseValidator.validate(text)

        try:
            data = json.loads(
                text,
                object_pairs_hook=ModelResponseValidator.validate_json_object_pairs,
                parse_constant=ModelResponseValidator.validate_json_constant,
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Malformed model response JSON: {error.msg} "
                f"at line {error.lineno}, column {error.colno} (char {error.pos})"
            ) from error

        ModelResponseValidator.validate_finite_numbers_data(data)
        ModelResponseValidator.validate_response_fields(data)
        ModelResponseValidator.validate_response_list_fields(data)
        StringValidator.validate_string(data["text"], "text")

        for index, call in enumerate(data["tool_calls"]):
            path = f"tool_calls[{index}]"
            ModelResponseValidator.validate_fields(call, ("tool", "arguments"), path)
            StringValidator.validate_string(call["tool"], f"{path}.tool", nonempty=True)
            ModelResponseValidator.validate_call_arguments(call["arguments"], path)

        for index, summary in enumerate(data["tool_result_summaries"]):
            path = f"tool_result_summaries[{index}]"
            ModelResponseValidator.validate_fields(summary, ("id", "summary"), path)
            StringValidator.validate_string(summary["id"], f"{path}.id", nonempty=True)
            StringValidator.validate_string(summary["summary"], f"{path}.summary")

        output_requests_data = data.get("tool_result_output_requests", [])
        ModelResponseValidator.validate_output_request_data(output_requests_data)
        for index, result_id in enumerate(output_requests_data):
            StringValidator.validate_string(
                result_id,
                f"tool_result_output_requests[{index}]",
                nonempty=True,
            )

    @staticmethod
    def is_plain_text_response(
        command_response_required,
        native_tool_calls,
        response_text,
    ) -> bool:
        """
        Check whether an invalid structured response can be accepted as plain text.

        Parameters:
            command_response_required: Whether a structured command response is required.
            native_tool_calls: Native tool calls included in the Groq response.
            response_text: The response content to evaluate.
        Example input: (False, None, "Hello")
        Example output: True
        Returns: True only for nonempty, non-JSON plain text without native tool calls.

        Command formatting belongs to the orchestrator. The provider accepts
        plain text here so the orchestrator can request the command envelope
        itself instead of failing inside the provider retry loop.
        """
        return bool(
            not native_tool_calls
            and isinstance(response_text, str)
            and response_text.strip()
            and not response_text.lstrip().startswith(("{", "[", "```"))
        )

    @staticmethod
    def unwrap_json_code_fence(response_text) -> str | None:
        """Return JSON contained in one complete Markdown fence, if present."""
        if not isinstance(response_text, str):
            return None

        match = re.fullmatch(
            r"\s*```(?:json)?\s*(.*?)\s*```\s*",
            response_text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return None

        unwrapped = match.group(1).strip()
        return unwrapped or None

    @staticmethod
    def is_valid_command_response(
        command_response_required,
        native_tool_calls,
        response_text,
    ) -> bool:
        """
        Check whether the content is a valid required command response.

        Parameters:
            command_response_required: Whether a structured command response is required.
            native_tool_calls: Native tool calls included in the Groq response.
            response_text: The command response content to evaluate.
        Example input: (True, None, '{"answer":"Done","command_summary":"Complete"}')
        Example output: True
        Returns: True when a required command response parses successfully without tool calls.
        """
        return (
            command_response_required
            and not native_tool_calls
            and parse_command_response(response_text) is not None
        )

    @staticmethod
    def is_acceptable_text_response(
        command_response_required,
        native_tool_calls,
        response_text,
    ) -> bool:
        """
        Check whether response text is acceptable as plain text or command JSON.

        Parameters:
            command_response_required: Whether a structured command response is required.
            native_tool_calls: Native tool calls included in the Groq response.
            response_text: The response content to evaluate.
        Example input: (False, None, "Hello")
        Example output: True
        Returns: True when either supported text-response validation succeeds.
        """
        return (
            ModelResponseValidator.is_plain_text_response(
                command_response_required,
                native_tool_calls,
                response_text,
            )
            or ModelResponseValidator.is_valid_command_response(
                command_response_required,
                native_tool_calls,
                response_text,
            )
        )

    @staticmethod
    def has_exhausted_retries(retry_attempt, maximum_retries) -> bool:
        """
        Check whether the current retry attempt reached the allowed limit.

        Parameters:
            retry_attempt: The zero-based current retry attempt.
            maximum_retries: The maximum number of allowed retries.
        Example input: (2, 2)
        Example output: True
        Returns: True when retry_attempt is greater than or equal to maximum_retries.
        """
        return retry_attempt >= maximum_retries

    @staticmethod
    def validate_retry_limit(
        retry_attempt,
        maximum_retries,
        error,
        response_text=None,
    ) -> None:
        """
        Validate that another invalid-response retry is still allowed.

        Parameters:
            retry_attempt: The zero-based current retry attempt.
            maximum_retries: The maximum number of allowed retries.
            error: The validation error raised for the invalid model response.
        Example input: (1, 2, ValueError("invalid response"))
        Example output: None
        Returns: None while the retry limit has not been reached.
        Raises: ModelResponseFormatError with the original error chained when
            the limit is reached.
        """
        if ModelResponseValidator.has_exhausted_retries(
            retry_attempt,
            maximum_retries,
        ):
            if response_text is None:
                response_preview = "<none>"
            else:
                response_preview = repr(str(response_text)[:300])

            raise ModelResponseFormatError(
                "Groq returned an invalid model response after "
                f"{maximum_retries} retries: {error}. "
                f"Response preview: {response_preview}"
            ) from error

    @staticmethod
    def has_response_content(response_content) -> bool:
        """
        Check whether Groq response content contains nonempty text.

        Description:
            Treat missing, empty, and whitespace-only content as unavailable.
        Parameters:
            response_content: The text content returned by Groq.
        Example input: "  Hello  "
        Example output: True
        Returns: True when response_content contains non-whitespace text.
        """
        return bool(
            response_content
            and response_content.strip()
        )

    @staticmethod
    def validate_prepare_groq_response(
        response_content,
        native_tool_calls,
        response,
    ) -> None:
        """
        Validate that a Groq message contains text or native tool calls.

        Description:
            Reject an empty response and validate already parsed structured text.
        Parameters:
            response_content: The text content returned by Groq.
            native_tool_calls: The native tool calls returned by Groq.
            response: The already parsed ModelResponse.
        Example input: ('{"text":"Hello"}', None, ModelResponse(text="Hello"))
        Example output: None
        Returns: None when the Groq response is valid.
        Raises: ValueError when the response is missing or contains embedded tool calls.
        """
        has_response_content = ModelResponseValidator.has_response_content(
            response_content
        )
        if not has_response_content and not native_tool_calls:
            raise ValueError("Groq returned no response text or tool calls")

        if has_response_content:
            ModelResponseValidator.validate_groq_response(response)

    @staticmethod
    def validate_groq_response(response) -> None:
        """
        Validate that parsed Groq text does not contain embedded tool calls.

        Description:
            Require tool calls to use Groq's native function-call representation.
        Parameters:
            response: The already parsed ModelResponse.
        Example input: ModelResponse(text="Hello", tool_calls=[])
        Example output: None
        Returns: None when the parsed response contains no tool calls.
        Raises: ValueError when structured text contains tool calls.
        """
        if response.tool_calls:
            raise ValueError("Groq must return tool calls as native function calls")

    @staticmethod
    def validate_json_object_pairs(pairs):
        """
        Validate JSON object pairs and reject duplicate field names.

        Example (valid): [("text", "Hello")] -> {"text": "Hello"}.
        Example (invalid): [("text", "Hello"), ("text", "Again")].
        Result: ValueError because "text" is duplicated.
        """

        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON field: {key}")
            result[key] = value

        return result

    @staticmethod
    def validate_json_constant(value):
        """
        Validate that a non-standard JSON numeric constant is rejected.

        Example (valid): 1 is parsed normally without invoking this hook.
        Example (invalid): NaN.
        Result: ValueError because NaN is not a valid JSON constant.
        """
        raise ValueError(f"Invalid JSON constant: {value}")

    @staticmethod
    def validate_response_choice(response) -> None:
        """
        Validate that Groq returned a choice with a complete finish reason.

        Example (valid): choices[0].finish_reason == "stop".
        Example (invalid): choices == [] or finish_reason == "length".
        Result: ValueError because no complete response choice is available.
        """
        if not response.choices:
            raise ValueError("Groq returned no response choices")
        if response.choices[0].finish_reason not in {"stop", "tool_calls"}:
            raise ValueError(
                "Groq returned an incomplete response: "
                f"{response.choices[0].finish_reason}"
            )

    @staticmethod
    def validate(text: str) -> None:
        """
        Validate that the model response is a non-empty string.

        Example (valid): "{}".
        Example (invalid): "   ".
        Result: ValueError because the response is empty after trimming.
        """
        if not isinstance(text, str):
            raise ValueError("Model response must be a JSON string")
        if not text.strip():
            raise ValueError("Model response is empty; expected a JSON object")

        

    @staticmethod
    def validate_finite_numbers_data(value) -> None:
        """
        Validate that all nested floating-point values are finite.

        Example (valid): {"values": [1, 2.5]}.
        Example (invalid): {"value": float("inf")}.
        Result: ValueError because Infinity is not finite.
        """
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("JSON numbers must be finite")
        if isinstance(value, dict):
            for item in value.values():
                ModelResponseValidator.validate_finite_numbers_data(item)
        elif isinstance(value, list):
            for item in value:
                ModelResponseValidator.validate_finite_numbers_data(item)



    @staticmethod
    def validate_response_fields(data) -> None:
        """
        Validate that a response has exactly the required and optional fields.

        Example (valid): {"text": "Hello", "tool_calls": [], "tool_result_summaries": []}.
        Example (invalid): {"text": "Hello", "tool_result_summaries": []}.
        Result: ValueError because "tool_calls" is missing.
        """
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
        
    @staticmethod
    def validate_response_list_fields(data) -> None:
        """
        Validate that tool_calls and tool_result_summaries are lists.

        Example (valid): {"tool_calls": [], "tool_result_summaries": []}.
        Example (invalid): {"tool_calls": "none", "tool_result_summaries": []}.
        Result: ValueError because "tool_calls" is not an array.
        """
        for field in ("tool_calls", "tool_result_summaries"):
            if not isinstance(data[field], list):
                raise ValueError(f"{field} must be an array")

    @staticmethod
    def validate_call_arguments(arguments, path) -> None:
        """
        Validate that a tool call's arguments are a JSON object.

        Example (valid): {"path": "README.md"}.
        Example (invalid): ["README.md"].
        Result: ValueError because the arguments are not an object.
        """
        if not isinstance(arguments, dict):
            raise ValueError(f"{path}.arguments must be an object")

    @staticmethod
    def validate_output_request_data(output_request_data) -> None:
        """
        Validate that tool result output requests are provided as a list.

        Example (valid): ["result-1"].
        Example (invalid): "result-1".
        Result: ValueError because the value is not an array.
        """
        if not isinstance(output_request_data, list):
            raise ValueError("tool_result_output_requests must be an array")

    @staticmethod
    def validate_fields(value, expected, path) -> None:
        """
        Validate that an object contains exactly the expected fields.

        Example (valid): {"tool": "read_file", "arguments": {}}.
        Example (invalid): {"tool": "read_file"}.
        Result: ValueError because an expected field is missing.
        """
        if not isinstance(value, dict) or set(value) != set(expected):
            raise ValueError(f"{path} must be an object with exactly: {', '.join(expected)}")
