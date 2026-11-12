from harness.domain.context import ContextUsage
from harness.domain.message import Message
from harness.models.errors import ContextWindowExceeded
from harness.models.model_client import ModelClient
from harness.models.tool_definition import ToolDefinition


class ContextManager:
    def validate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition],
        model_client: ModelClient
    ) -> ContextUsage:
        """Validate the complete provider request against its input budget."""

        input_tokens = model_client.count_tokens(messages, tools)
        limits = model_client.get_context_limits()

        if not isinstance(input_tokens, int) or isinstance(input_tokens, bool):
            raise ValueError("Model input token count must be an integer.")
        if input_tokens < 0:
            raise ValueError("Model input token count cannot be negative.")
        if not isinstance(limits.context_window, int) or isinstance(limits.context_window, bool):
            raise ValueError("Model context window must be an integer.")
        if limits.context_window < 1:
            raise ValueError("Model context window must be a positive integer.")
        if not isinstance(limits.reserved_output_tokens, int) or isinstance(limits.reserved_output_tokens, bool):
            raise ValueError("Reserved output tokens must be an integer.")
        if limits.reserved_output_tokens < 0:
            raise ValueError("Reserved output tokens cannot be negative.")

        available_input_tokens = limits.input_token_limit
        if available_input_tokens is None:
            available_input_tokens = limits.context_window - limits.reserved_output_tokens
        if not isinstance(available_input_tokens, int) or isinstance(available_input_tokens, bool):
            raise ValueError("Available model input budget must be an integer.")
        if available_input_tokens < 1:
            raise ValueError("Available model input budget must be a positive integer.")

        remaining_tokens = available_input_tokens - input_tokens
        usage = ContextUsage(
            input_tokens=input_tokens,
            context_window=limits.context_window,
            reserved_output_tokens=limits.reserved_output_tokens,
            available_input_tokens=available_input_tokens,
            remaining_tokens=remaining_tokens
        )

        if remaining_tokens < 0:
            raise ContextWindowExceeded(
                model=limits.model,
                input_tokens=input_tokens,
                available_input_tokens=available_input_tokens
            )

        return usage
