import json
from pathlib import Path
from typing import Any


class ListDirectoryTool:
    def __init__(self, working_directory: Path | None = None) -> None:
        self._working_directory = (working_directory or Path.cwd()).resolve()

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "Lists the direct children of a project directory without modifying files."

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Project-relative directory path to list."
                }
            },
            "required": ["path"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        path_value = arguments["path"]
        path = (self._working_directory / path_value).resolve()

        try:
            if not path.is_relative_to(self._working_directory):
                raise PermissionError("Directory path must stay inside the project.")

            if not path.is_dir():
                raise FileNotFoundError(f"Directory not found: {path_value}")

            entries = sorted(item.name for item in path.iterdir())
            result = {"success": True, "path": path_value, "entries": entries}
        except Exception as error:
            result = {"success": False, "path": path_value, "error": str(error)}

        return json.dumps(result, ensure_ascii=False)
