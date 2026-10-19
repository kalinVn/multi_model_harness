"""Groq conversions at the existing text-only provider boundary."""
import json
from copy import deepcopy

from harness.config.response.groq_response_instruction import GROQ_RESPONSE_INSTRUCTION

from harness.domain.message import Message
from harness.models.groq_tool_type import GroqToolType
from harness.models.response import ModelResponse
from harness.models.tool_schema import ToolSchema
from harness.parser.response_parser import prepare_model_response
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

    groq_messages.append(
        {"role": "system", "content": GROQ_RESPONSE_INSTRUCTION}
    )

    return groq_messages


def prepare_groq_response(message, tools: list[GroqToolType]) -> ModelResponse:

    tool_calls = message.tool_calls or []

    if message.content and message.content.strip():
        response = prepare_model_response(message.content)
    elif tool_calls:
        response = ModelResponse()
    else:
        raise ValueError("Groq returned no response text or tool calls")
    
    if response.tool_calls:
        raise ValueError("Groq must return tool calls as native function calls")

    available_tool_names = {tool["function"]["name"] for tool in tools}
    prepared_tool_calls = []
    
    for tool_call in tool_calls:
        ToolsValidator.validate_groq_tool_call(tool_call, available_tool_names)
        ToolsValidator.validate_groq_tool_arguments(tool_call.function.arguments)
        
        raw = (
            '{"text":"","tool_calls":[{"tool":'
            + json.dumps(tool_call.function.name)
            + ',"arguments":' + tool_call.function.arguments
            + '}],"tool_result_summaries":[]}'
        )

        prepared_tool_call_response = prepare_model_response(raw)

        if (
            len(prepared_tool_call_response.tool_calls) != 1
            or prepared_tool_call_response.tool_calls[0].name
            != tool_call.function.name
        ):
            raise ValueError("Groq tool arguments contain an invalid call envelope")
        
        prepared_tool_calls.extend(prepared_tool_call_response.tool_calls)

    return ModelResponse(
        text=response.text,
        tool_calls=prepared_tool_calls,
        tool_result_summaries=response.tool_result_summaries,
        tool_result_output_requests=response.tool_result_output_requests,
    )
