class ModelRateLimitError(RuntimeError):
    """Raised when a model provider temporarily rejects requests."""


class ModelConnectionError(RuntimeError):
    """Raised when a model provider cannot be reached."""


class UnknownCommandError(ValueError):
    """Raised when a requested Harness command does not exist."""


class ContextWindowExceeded(Exception):
    def __init__(self, model: str, input_tokens: int, available_input_tokens: int) -> None:
        self.model = model
        self.input_tokens = input_tokens
        self.available_input_tokens = available_input_tokens
        self.exceeded_tokens = input_tokens - available_input_tokens
        super().__init__(
            "Context window exceeded.\n"
            f"Model: {model}\n"
            f"Input tokens: {input_tokens}\n"
            f"Available input budget: {available_input_tokens}\n"
            f"Exceeded by: {self.exceeded_tokens} tokens"
        )
