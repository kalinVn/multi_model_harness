import json
import math

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
