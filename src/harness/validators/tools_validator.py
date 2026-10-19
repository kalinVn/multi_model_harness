from harness.models.tool_schema import ToolSchema


class ToolsValidator:
    @staticmethod
    def validate(tools: list[ToolSchema]) -> None:
        """
        Валидира, че дефинициите на Harness инструменти имат уникални имена.

        Пример (валиден): [{"name": "read_file"}].
        Пример (невалиден): две дефиниции с име "read_file".
        Резултат: ValueError, защото дублирани имена на инструменти не са разрешени.
        """
        # Извличаме имената на всички инструменти
        tool_names = [tool["name"] for tool in tools]

        if len(tool_names) != len(set(tool_names)):
            raise ValueError("Duplicate harness tool definitions for Groq")

    @staticmethod
    def validate_groq_tool_call(tool_call, available_tool_names: set[str]) -> None:
        """
        Валидира, че Groq е върнал извикване на наличен функционален инструмент.

        Пример (валиден): type="function", function.name="read_file".
        Пример (невалиден): function.name="unknown".
        Резултат: ValueError, защото инструментът не е наличен.
        """
        if tool_call.type != "function" or tool_call.function.name not in available_tool_names:
            raise ValueError("Groq returned an unavailable tool")

    @staticmethod
    def validate_groq_tool_arguments(arguments) -> None:
        """
        Валидира, че аргументите на Groq инструмента са кодирани като JSON низ.

        Пример (валиден): '{"path": "README.md"}'.
        Пример (невалиден): {"path": "README.md"}.
        Резултат: ValueError, защото аргументите не са низ.
        """
        if not isinstance(arguments, str):
            raise ValueError("Groq tool arguments must be a JSON string")

    @staticmethod
    def validate_groq_tool_call_response(
        prepared_tool_call_response,
        expected_tool_name,
    ) -> None:
        """
        Validate that a parsed Groq response contains the expected single tool call.

        Parameters:
            prepared_tool_call_response: The parsed ModelResponse to validate.
            expected_tool_name: The native Groq function name expected in the response.
        Example input:
            (ModelResponse(tool_calls=[ToolCall(name="bash")]), "bash")
        Example output:
            None
        Returns:
            None when exactly one tool call has the expected name.
        Raises:
            ValueError: If the parsed response has an invalid call envelope.
        """
        if (
            len(prepared_tool_call_response.tool_calls) != 1
            or prepared_tool_call_response.tool_calls[0].name
            != expected_tool_name
        ):
            raise ValueError("Groq tool arguments contain an invalid call envelope")
