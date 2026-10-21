class ModelRateLimitError(RuntimeError):
    """Raised when a model provider temporarily rejects requests."""


class ModelConnectionError(RuntimeError):
    """Raised when a model provider cannot be reached."""


class ModelResponseFormatError(ValueError):
    """Raised when a provider repeatedly returns an unusable response."""
