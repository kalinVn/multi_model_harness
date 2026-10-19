"""Groq conversions at the existing text-only provider boundary."""
import json
from copy import deepcopy

from harness.config.response.groq_response_instruction import GROQ_RESPONSE_INSTRUCTION

from harness.domain.message import Message
from harness.models.groq_tool_type import GroqToolType
from harness.models.response import ModelResponse
from harness.models.tool_schema import ToolSchema
from harness.parser.response_parser import prepare_model_response
from harness.validators.model_response_validator import ModelResponseValidator
from harness.validators.tools_validator import ToolsValidator
# Groq API requires a specific tool format, so we convert our
# provider-independent Harness tool definitions into Groq function definitions.
# The "type": "function" field identifies the tool type,
# while "function" contains its name, description, and parameters.


def prepare_groq_tools(tools: list[ToolSchema]) -> list[GroqToolType]:
    """
        Convert Harness tool definitions into the Groq API function format.

        Groq API requires a specific tool format, so we convert our
        provider-independent Harness tool definitions into Groq function definitions.
        The "type": "function" field identifies the tool type,
        while "function" contains its name, description, and parameters.

        Example input:
            [
                {
                    "name": "read_file",
                    "description": "Reads a file",
                    "parameters": {}
                }
            ]

        Example output:
            [
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "description": "Reads a file",
                        "parameters": {}
                    }
                }
            ]
            
    """

    ToolsValidator.validate(tools)


    formatted_grok_tools = [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": deepcopy(tool["parameters"]),
            },
        }
        
        for tool in tools
    ]

    return formatted_grok_tools



def prepare_groq_messages(
    model_messages: list[Message],
) -> list[dict[str, str]]:
    """
    Convert a list of Harness Message objects into Groq-compatible dictionaries.
    Each Message is converted to a dictionary containing "role" and "content".
    Append the Groq system response instruction to the messages.

    Example input:
        [Message(role="user", content="Hello")]

    Example output:
        [
            {"role": "user", "content": "Hello"},
            {"role": "system", "content": GROQ_RESPONSE_INSTRUCTION}
        ]
    """
    
    groq_messages = [
        {"role": message.role, "content": message.content}
        for message in model_messages
    ]

    groq_messages.append({"role": "system", "content": GROQ_RESPONSE_INSTRUCTION})

    return groq_messages


def _get_tool_call_response_json(tool_call) -> str:
    """
    Build the model-response JSON string for a native Groq tool call.

    Parameters:
        tool_call: A Groq tool call containing a function name and JSON arguments.
    Example input:
        function.name = "bash"
        function.arguments = '{"command":"ls -la"}'
    Example output:
        '{"text":"","tool_calls":[{"tool":"bash","arguments":{"command":"ls -la"}}],"tool_result_summaries":[]}'
    Returns:
        The complete tool-call response JSON string.
    """
    return (
        '{"text":"","tool_calls":[{"tool":'
        + json.dumps(tool_call.function.name)
        + ',"arguments":' + tool_call.function.arguments
        + '}],"tool_result_summaries":[]}'
    )


def _parse_groq_tool_calls(tool_calls, available_tool_names):
    """
    Validate and parse native Groq tool calls into Harness ToolCall objects.

    Description:
        Preserve each call's validation, JSON conversion, parsing, and collection order.
    Parameters:
        tool_calls: The native tool calls returned by Groq.
        available_tool_names: The names of tools available to the model.
    Example input:
        ([SimpleNamespace(type="function", function=SimpleNamespace(
            name="bash", arguments='{"command":"ls"}'))], {"bash"})
    Example output:
        [ToolCall(name="bash", arguments={"command": "ls"})]
    Returns:
        A list of parsed ToolCall objects in the original order.
    Raises:
        ValueError: If a tool name, arguments, JSON payload, or envelope is invalid.
    """
    prepared_tool_calls = []

    for tool_call in tool_calls:
        ToolsValidator.validate_groq_tool_call(tool_call, available_tool_names)
        ToolsValidator.validate_groq_tool_arguments(tool_call.function.arguments)

        tool_call_response_json = _get_tool_call_response_json(tool_call)

        prepared_tool_call_response = prepare_model_response(tool_call_response_json)

        ToolsValidator.validate_groq_tool_call_response(
            prepared_tool_call_response,
            tool_call.function.name,
        )

        prepared_tool_calls.extend(prepared_tool_call_response.tool_calls)

    return prepared_tool_calls


def prepare_groq_response(message, tools: list[GroqToolType]) -> ModelResponse:
    """
    Convert Groq message content and native tool calls into a ModelResponse.

    Description:
        Parse structured text content, validate native Groq tool calls, and combine
        both sources into the provider-independent response model.
    Example input:
        message = SimpleNamespace(
            content='{"text":"Hello","tool_calls":[],"tool_result_summaries":[]}',
            tool_calls=None,
        )
        tools = []
    Example output:
        ModelResponse(
            text="Hello",
            tool_calls=[],
            tool_result_summaries=[],
            tool_result_output_requests=[],
        )
    Native tool-call example input:
        message.tool_calls = [
            SimpleNamespace(
                type="function",
                function=SimpleNamespace(
                    name="bash",
                    arguments='{"command":"ls -la"}',
                ),
            )
        ]
        tools = [
            {"type": "function", "function": {"name": "bash"}}
        ]
    Native tool-call example output:
        ModelResponse(
            text="",
            tool_calls=[ToolCall(name="bash", arguments={"command": "ls -la"})],
            tool_result_summaries=[],
            tool_result_output_requests=[],
        )
    Returns:
        A ModelResponse containing parsed text, tool calls, and result metadata.
    Raises:
        ValueError: If the message content or native tool calls are invalid.
    """

    tool_calls = message.tool_calls or []

    has_response_content = ModelResponseValidator.has_response_content(
        message.content
    )

    if has_response_content:
        response = prepare_model_response(message.content)
    else:
        response = ModelResponse()

    ModelResponseValidator.validate_prepare_groq_response(
        message.content,
        tool_calls,
        response,
    )

    available_tool_names = {tool["function"]["name"] for tool in tools}
    prepared_tool_calls = _parse_groq_tool_calls(
        tool_calls,
        available_tool_names,
    )

    return ModelResponse(
        text=response.text,
        tool_calls=prepared_tool_calls,
        tool_result_summaries=response.tool_result_summaries,
        tool_result_output_requests=response.tool_result_output_requests,
    )
