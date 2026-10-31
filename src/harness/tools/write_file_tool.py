import json
from pathlib import Path
from typing import Any

class WriteFileTool:
    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Writes text content to one or more files sequentially. "
            "Returns one result per file and continues after write failures."
        )

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": (
                                    "Path of the file to create or overwrite."
                                ),
                            },
                            "content": {
                                "type": "string",
                                "description": "Text content to write.",
                            },
                        },
                        "required": ["path", "content"],
                        "additionalProperties": False,
                    },
                    "minItems": 1,
                    "description": "Files to write sequentially.",
                },
            },
            "required": ["files"],
            "additionalProperties": False,
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        files = arguments["files"]

        results: list[dict[str, Any]] = []
        for file_definition in files:
            path_value = file_definition["path"]
            path = Path(path_value)
            result: dict[str, Any] = {"path": path_value}

            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(file_definition["content"], encoding="utf-8")
                result.update(
                    success=True,
                    message=f"File written successfully: {path}",
                )
            except Exception as error:
                result.update(success=False, error=str(error))

            results.append(result)

        return json.dumps(
            {
                "success": all(result["success"] for result in results),
                "results": results,
            },
            ensure_ascii=False,
        )
