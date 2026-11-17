from dataclasses import replace
from unittest.mock import Mock

from harness.domain.context import ModelContextLimits
from harness.domain.message import Message
from harness.models.response import ModelResponse
from harness.models.tool_result_summary import ToolResultSummary


def allow_context(client: Mock) -> Mock:
    client.count_tokens.return_value = 1
    client.get_context_limits.return_value = ModelContextLimits(
        model="test-model",
        context_window=1_000,
        reserved_output_tokens=100
    )

    return client


def add_tool_result_summaries(response: ModelResponse, messages: list[Message]) -> ModelResponse:
    summaries = list(response.tool_result_summaries)
    summarized_ids = {summary.id for summary in summaries}

    for message in messages:
        for result in message.tool_results:
            if not result.summary.strip() and result.id not in summarized_ids:
                outcome = "succeeded" if result.success else "failed"
                summaries.append(ToolResultSummary(result.id, f"{result.name} {outcome}."))

    return replace(response, tool_result_summaries=summaries)
