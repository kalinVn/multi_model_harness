from pathlib import Path
from typing import Any


class ReadFileTool:
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Reads text content from a file."

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file to read.",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
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
