from typing import Any, TypedDict


class ToolSchema(TypedDict):
    """Независима от доставчика структурирана дефиниция на един Harness инструмент."""

    name: str
    description: str
    parameters: dict[str, Any]
