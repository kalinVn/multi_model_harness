from harness.models.tool_schema import ToolSchema


class ToolsValidator:
    @staticmethod
    def validate(tools: list[ToolSchema]) -> None:
        """
        Validate that Harness tool definitions have unique names.

        Example (valid): [{"name": "read_file"}].
        Example (invalid): two definitions named "read_file".
        Result: ValueError because duplicate tool names are not allowed.
        """
        # Extract the names of all tools
        tool_names = [tool["name"] for tool in tools]

        if len(tool_names) != len(set(tool_names)):
            raise ValueError("Duplicate harness tool definitions for Groq")

    @staticmethod
    def validate_groq_tool_call(tool_call, available_tool_names: set[str]) -> None:
        """
        Validate that Groq returned an available function tool call.

        Example (valid): type="function", function.name="read_file".
        Example (invalid): function.name="unknown".
        Result: ValueError because the tool is unavailable.
        """
        if tool_call.type != "function" or tool_call.function.name not in available_tool_names:
            raise ValueError("Groq returned an unavailable tool")

    @staticmethod
    def validate_groq_tool_arguments(arguments) -> None:
        """
        Validate that Groq tool arguments are encoded as a JSON string.

        Example (valid): '{"path": "README.md"}'.
        Example (invalid): {"path": "README.md"}.
        Result: ValueError because the arguments are not a string.
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
