class ModelRateLimitError(RuntimeError):
    """Raised when a model provider temporarily rejects requests."""


class ModelConnectionError(RuntimeError):
    """Raised when a model provider cannot be reached."""


class UnknownCommandError(ValueError):
    """Raised when a requested Harness command does not exist."""
