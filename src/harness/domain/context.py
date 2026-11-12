from dataclasses import dataclass


@dataclass(frozen=True)
class ModelContextLimits:
    model: str
    context_window: int
    reserved_output_tokens: int
    input_token_limit: int | None = None


@dataclass(frozen=True)
class ContextUsage:
    input_tokens: int
    context_window: int
    reserved_output_tokens: int
    available_input_tokens: int
    remaining_tokens: int
