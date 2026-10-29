from pathlib import Path
from typing import Any


class WriteFileTool:
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Writes text content to a file."

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file to create or overwrite.",
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write into the file.",
                },
            },
            "required": ["path", "content"],
            "additionalProperties": False,
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        path_value = arguments.get("path")
        content = arguments.get("content")

        if not isinstance(path_value, str):
            raise ValueError("write_file requires a string 'path'.")

        if not isinstance(content, str):
            raise ValueError("write_file requires a string 'content'.")

        path = Path(path_value)

        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")

        return f"File written successfully: {path}"
