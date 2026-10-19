import math

from harness.parser.command_response_parser import parse_command_response


class ModelResponseValidator:
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
        """
        return bool(
            not command_response_required
            and not native_tool_calls
            and isinstance(response_text, str)
            and response_text.strip()
            and not response_text.lstrip().startswith(("{", "[", "```"))
        )

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
    def validate_retry_limit(retry_attempt, maximum_retries, error) -> None:
        """
        Validate that another invalid-response retry is still allowed.

        Parameters:
            retry_attempt: The zero-based current retry attempt.
            maximum_retries: The maximum number of allowed retries.
            error: The validation error raised for the invalid model response.
        Example input: (1, 2, ValueError("invalid response"))
        Example output: None
        Returns: None while the retry limit has not been reached.
        Raises: ValueError with the original error chained when the limit is reached.
        """
        if ModelResponseValidator.has_exhausted_retries(
            retry_attempt,
            maximum_retries,
        ):
            raise ValueError(
                "Groq returned an invalid model response after "
                f"{maximum_retries} retries: {error}"
            ) from error

    @staticmethod
    def validate_json_object_pairs(pairs):
        """
        Валидира двойките на JSON обект и отхвърля дублирани имена на полета.

        Пример (валиден): [("text", "Здравей")] -> {"text": "Здравей"}.
        Пример (невалиден): [("text", "Здравей"), ("text", "Отново")].
        Резултат: ValueError, защото "text" се дублира.
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
        Валидира, че нестандартна числова JSON константа се отхвърля.

        Пример (валиден): 1 се разборира нормално, без да се извиква този hook.
        Пример (невалиден): NaN.
        Резултат: ValueError, защото NaN не е валидна JSON константа.
        """
        raise ValueError(f"Invalid JSON constant: {value}")

    @staticmethod
    def validate_response_choice(response) -> None:
        """
        Валидира, че Groq е върнал избор със завършена причина за приключване.

        Пример (валиден): choices[0].finish_reason == "stop".
        Пример (невалиден): choices == [] or finish_reason == "length".
        Резултат: ValueError, защото няма наличен завършен избор на отговор.
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
        Валидира, че отговорът на модела е непразен низ.

        Пример (валиден): "{}".
        Пример (невалиден): "   ".
        Резултат: ValueError, защото отговорът е празен след изчистване на интервалите.
        """
        if not isinstance(text, str):
            raise ValueError("Model response must be a JSON string")
        if not text.strip():
            raise ValueError("Model response is empty; expected a JSON object")

        

    @staticmethod
    def validate_finite_numbers_data(value) -> None:
        """
        Валидира, че всички вложени стойности с плаваща запетая са крайни.

        Пример (валиден): {"values": [1, 2.5]}.
        Пример (невалиден): {"value": float("inf")}.
        Резултат: ValueError, защото Infinity не е крайно число.
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
        Валидира, че отговорът има точно задължителните и незадължителните полета.

        Пример (валиден): {"text": "Здравей", "tool_calls": [], "tool_result_summaries": []}.
        Пример (невалиден): {"text": "Здравей", "tool_result_summaries": []}.
        Резултат: ValueError, защото "tool_calls" липсва.
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
        Валидира, че tool_calls и tool_result_summaries са списъци.

        Пример (валиден): {"tool_calls": [], "tool_result_summaries": []}.
        Пример (невалиден): {"tool_calls": "none", "tool_result_summaries": []}.
        Резултат: ValueError, защото "tool_calls" не е масив.
        """
        for field in ("tool_calls", "tool_result_summaries"):
            if not isinstance(data[field], list):
                raise ValueError(f"{field} must be an array")

    @staticmethod
    def validate_call_arguments(arguments, path) -> None:
        """
        Валидира, че аргументите на извикване на инструмент са JSON обект.

        Пример (валиден): {"path": "README.md"}.
        Пример (невалиден): ["README.md"].
        Резултат: ValueError, защото аргументите не са обект.
        """
        if not isinstance(arguments, dict):
            raise ValueError(f"{path}.arguments must be an object")

    @staticmethod
    def validate_output_request_data(output_request_data) -> None:
        """
        Валидира, че заявките за изход от резултати на инструменти са подадени като списък.

        Пример (валиден): ["result-1"].
        Пример (невалиден): "result-1".
        Резултат: ValueError, защото стойността не е масив.
        """
        if not isinstance(output_request_data, list):
            raise ValueError("tool_result_output_requests must be an array")

    @staticmethod
    def validate_fields(value, expected, path) -> None:
        """
        Валидира, че обектът съдържа точно очакваните полета.

        Пример (валиден): {"tool": "read_file", "arguments": {}}.
        Пример (невалиден): {"tool": "read_file"}.
        Резултат: ValueError, защото липсва очаквано поле.
        """
        if not isinstance(value, dict) or set(value) != set(expected):
            raise ValueError(f"{path} must be an object with exactly: {', '.join(expected)}")
