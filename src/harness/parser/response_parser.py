"""Строго и независимо от доставчика декодиране на JSON отговор."""
import json

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.validators.model_response_validator import ModelResponseValidator


def _parse_tool_calls(data) -> list[ToolCall]:
    """
    Construct tool calls from validated model response data.

    Example input:
        {"tool_calls": [{"tool": "bash", "arguments": {"command": "ls"}}]}

    Returns:
        A list of ToolCall objects.
    """
    tool_calls = []
    for call in data["tool_calls"]:
        tool_calls.append(ToolCall(name=call["tool"], arguments=call["arguments"]))

    return tool_calls


def _parse_tool_result_summaries(data) -> list[ToolResultSummary]:
    """
    Construct tool result summaries from validated model response data.

    Example input:
        {"tool_result_summaries": [{"id": "call_1", "summary": "Completed"}]}

    Returns:
        A list of ToolResultSummary objects.
    """
    summaries = []
    for summary in data["tool_result_summaries"]:
        summaries.append(ToolResultSummary(
            id=summary["id"],
            summary=summary["summary"],
        ))

    return summaries


def _get_output_requests(data):
    """
    Read output request IDs from validated model response data.

    Example input:
        {"tool_result_output_requests": ["result_1"]}

    Returns:
        A list of validated result IDs.
    """
    return data.get("tool_result_output_requests", [])


def prepare_model_response(text: str) -> ModelResponse:
    """Декодира пълния отговор или генерира ValueError; никога не предполага изпълнение на инструмент.

    ID на резултатите от инструменти са непрозрачни и се запазват дословно. Runner ги проверява
    спрямо изпълнените резултати. Схемите на аргументите на инструментите се валидират при изпълнение.
      Разборира и валидира JSON отговор на модела.

    Аргументи:
        text: JSON низ, съдържащ отговора на модела.

    Пример (вход):
        '{"text": "Здравей", "tool_calls": [], "tool_result_summaries": []}'

    Пример (изход):
        ModelResponse(
            text="Здравей",
            tool_calls=[],
            tool_result_summaries=[],
            tool_result_output_requests=[]
        )

    Връща:
        ModelResponse: Разборираният и валидиран отговор на модела.

    Генерира:
        ValueError: Ако JSON или данните на отговора са невалидни.
    """

    ModelResponseValidator.validate_prepare_model_response(text)

    data = json.loads(
        text,
        object_pairs_hook=ModelResponseValidator.validate_json_object_pairs,
        parse_constant=ModelResponseValidator.validate_json_constant,
    )

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
