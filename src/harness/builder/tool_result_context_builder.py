from harness.domain.tool_result import ToolResult


TOOL_RESULTS_CONTEXT_HEADER = "The requested tools have finished."
TOOL_RESULTS_CONTEXT_FOOTER = (
    "Use these results to continue the task. "
    "If no more tools are needed, respond normally."
)


def has_tool_result_summary(tool_result: ToolResult) -> bool:
    return bool(tool_result.summary and tool_result.summary.strip())


def _add_tool_result_output_to_context_paragraphs(
    context_paragraphs: list[str],
    tool_result: ToolResult,
    max_content_chars: int | None = None,
) -> None:
    output = _truncate_tool_result_content(tool_result.output, max_content_chars)
    context_paragraphs.append(
        "\n".join(
            [
                f"Tool result ID: {tool_result.id}",
                f"Tool: {tool_result.name}",
                f"Success: {tool_result.success}",
                "Output:",
                output,
            ]
        )
    )


def _add_tool_result_summary_to_context_paragraphs(
    context_paragraphs: list[str],
    tool_result: ToolResult,
    max_content_chars: int | None = None,
) -> None:
    summary = _truncate_tool_result_content(tool_result.summary, max_content_chars)
    context_paragraphs.append(
        "\n".join(
            [
                f"Tool result ID: {tool_result.id}",
                f"Tool: {tool_result.name}",
                f"Success: {tool_result.success}",
                "Summary:",
                summary,
            ]
        )
    )


def _truncate_tool_result_content(content: str, max_chars: int | None) -> str:
    if max_chars is None or len(content) <= max_chars:
        return content

    omitted_chars = len(content) - max_chars
    return (
        content[:max_chars]
        + f"\n[tool result truncated: {omitted_chars} characters omitted]"
    )


def build_tool_results_context(
    tool_results: list[ToolResult],
    tool_result_output_requests: list[str] | None = None,
    max_output_chars: int | None = None,
) -> str:
    context_paragraphs = [TOOL_RESULTS_CONTEXT_HEADER]
    requested_output_ids = set(tool_result_output_requests or [])
    max_content_chars = None
    if max_output_chars is not None:
        max_content_chars = max(1, max_output_chars // max(1, len(tool_results)))

    for tool_result in tool_results:
        model_requested_full_output = tool_result.id in requested_output_ids
        

        if model_requested_full_output:
            _add_tool_result_output_to_context_paragraphs(
                context_paragraphs,
                tool_result,
                max_content_chars,
            )

            continue

        if has_tool_result_summary(tool_result):
            _add_tool_result_summary_to_context_paragraphs(
                context_paragraphs,
                tool_result,
                max_content_chars,
            )
            
            continue

        _add_tool_result_output_to_context_paragraphs(
            context_paragraphs,
            tool_result,
            max_content_chars,
        )

    context_paragraphs.append(TOOL_RESULTS_CONTEXT_FOOTER)

    return "\n\n".join(context_paragraphs)
