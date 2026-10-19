import math


class ModelResponseValidator:
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
