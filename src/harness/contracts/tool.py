from typing import Any, Protocol


class Tool(Protocol):
    @property
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        ...

    def get_parameter_object(self) -> dict[str, Any]:
        ...

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        ...
