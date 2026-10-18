from typing import Any, TypedDict


class GroqFunctionType(TypedDict):
    name: str
    description: str
    parameters: dict[str, Any]


class GroqToolType(TypedDict):
    type: str
    function: GroqFunctionType
