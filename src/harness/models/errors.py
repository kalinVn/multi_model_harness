class ModelRateLimitError(RuntimeError):
    """Генерира се, когато доставчик на модел временно отхвърля заявки."""


class ModelConnectionError(RuntimeError):
    """Генерира се, когато доставчикът на модел не може да бъде достигнат."""
