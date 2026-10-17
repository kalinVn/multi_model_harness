from typing import Any

from harness.contracts.tool import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        tool: Tool,
    ) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(
        self,
        name: str,
    ) -> Tool:
        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"Unknown tool: {name}")

        return tool

    def execute(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        tool = self.get(name)

        return tool.execute(arguments)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())
