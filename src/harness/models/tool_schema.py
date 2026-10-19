from typing import Any, TypedDict


class ToolSchema(TypedDict):
    """Provider-independent structured definition of one Harness tool."""

    name: str
    description: str
    parameters: dict[str, Any]
