"""Строго и независимо от доставчика декодиране на JSON отговор."""
import json

from harness.domain.tool_call import ToolCall
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary
from harness.validators.model_response_validator import ModelResponseValidator
from harness.validators.string_validator import StringValidator


def _parse_tool_calls(data) -> list[ToolCall]:
    """
    Разборира и валидира извикванията на инструменти от данните на отговора на модела.

    Пример (валиден):
        {"tool_calls": [{"tool": "bash", "arguments": {"command": "ls"}}]}

    Пример (невалиден):
        {"tool_calls": [{"tool": 123, "arguments": {}}]}

    Връща:
        Списък с валидирани ToolCall обекти.
    """
    tool_calls = []
    for index, call in enumerate(data["tool_calls"]):
        path = f"tool_calls[{index}]"
        name = StringValidator.validate_string(call["tool"], f"{path}.tool", nonempty=True)
        ModelResponseValidator.validate_fields(call, ("tool", "arguments"), path)
        
        ModelResponseValidator.validate_call_arguments(call["arguments"], path)
        tool_calls.append(ToolCall(name=name, arguments=call["arguments"]))

    return tool_calls


def _parse_tool_result_summaries(data) -> list[ToolResultSummary]:
    """
    Разборира и валидира обобщенията на резултатите от инструменти от данните на отговора на модела.

    Пример (валиден):
        {"tool_result_summaries": [{"id": "call_1", "summary": "Командата приключи"}]}

    Пример (невалиден):
        {"tool_result_summaries": [{"id": 123, "summary": "Командата приключи"}]}

    Връща:
        Списък с валидирани ToolResultSummary обекти.
    """
    summaries = []
    for index, summary in enumerate(data["tool_result_summaries"]):
        path = f"tool_result_summaries[{index}]"
        ModelResponseValidator.validate_fields(summary, ("id", "summary"), path)
        summaries.append(ToolResultSummary(
            id=StringValidator.validate_string(summary["id"], f"{path}.id", nonempty=True),
            summary=StringValidator.validate_string(summary["summary"], f"{path}.summary"),
        ))

    return summaries


def _get_output_requests(data):
    """
    Прочита и валидира ID на заявките за изход от резултати на инструменти от данните на отговора на модела.

    Пример (валиден):
        {"tool_result_output_requests": ["result_1"]}

    Пример (невалиден):
        {"tool_result_output_requests": "result_1"}

    Връща:
        Списък с валидирани ID на резултати.
    """
    output_requests_data = data.get("tool_result_output_requests", [])
    ModelResponseValidator.validate_output_request_data(output_requests_data)

    output_requests = [
        StringValidator.validate_string(result_id, f"tool_result_output_requests[{index}]", nonempty=True)
        for index, result_id in enumerate(output_requests_data)
    ]

    return output_requests


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

    ModelResponseValidator.validate(text)

    # Разборираме JSON отговора до Python обект (речник).
    #
    # Пример за валиден JSON:
    # {"text": "Здравей", "tool_calls": [], "tool_result_summaries": []}
    # Резултат: Python речник с достъпни полета.
    #
    # Пример за дублирани JSON полета:
    # {"text": "Здравей", "text": "Свят"}
    # Резултат: ValueError("Duplicate JSON field: text")
    #
    # Пример за невалидни числови константи:
    # {"text": "Здравей", "value": NaN}
    # Резултат: ValueError("Invalid JSON constant: NaN")
    #
    # Отхвърляме дублирани полета и невалидни числови константи
    # като NaN, Infinity и -Infinity.

    try:
        data = json.loads(text, object_pairs_hook=ModelResponseValidator.validate_json_object_pairs, parse_constant=ModelResponseValidator.validate_json_constant)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Malformed model response JSON: {error.msg} "
            f"at line {error.lineno}, column {error.colno} (char {error.pos})"
        ) from error
    
    ModelResponseValidator.validate_finite_numbers_data(data)
    ModelResponseValidator.validate_response_fields(data)
    ModelResponseValidator.validate_response_list_fields(data)
    StringValidator.validate_string(data["text"], "text")
   
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
