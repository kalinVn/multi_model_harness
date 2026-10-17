from pathlib import Path
from typing import Any


class ReadFileTool:
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads text content from a file."

    @property
    def arguments_schema(self) -> dict[str, str]:
        return {
            "path": "Path of the file to read.",
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        path_value = arguments.get("path")

        if not isinstance(path_value, str):
            raise ValueError("read_file requires a string 'path'.")

        path = Path(path_value)

        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        return path.read_text(encoding="utf-8")
