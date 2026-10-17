from typing import Any, Protocol


class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    @property
    def arguments_schema(self) -> dict[str, str | dict[str, Any]]:
        ...

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        ...
