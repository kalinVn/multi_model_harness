import json
from pathlib import Path
from typing import Any

class ReadFileTool:
    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return (
            "Reads text content from one or more files sequentially. "
            "Returns one result per path and continues after read failures."
        )

    def get_parameter_object(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "description": "Paths of the files to read in order.",
                },
            },
            "required": ["paths"],
            "additionalProperties": False,
        }

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        paths = arguments["paths"]

        results: list[dict[str, Any]] = []
        for path_value in paths:
            path = Path(path_value)
            result: dict[str, Any] = {"path": path_value}

            try:
                if not path.is_file():
                    raise FileNotFoundError(f"File not found: {path}")
                result.update(
                    success=True,
                    content=path.read_text(encoding="utf-8"),
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
