import json
from copy import deepcopy
from typing import Any

from harness.contracts.tool import Tool
from harness.models.tool_schema import ToolSchema


TOOLS_CONTEXT_HEADER = "Tool usage:"


def build_tools_schema(
    tools: list[Tool],
) -> list[ToolSchema]:
    """Build provider-independent structured schemas for registered tools."""
    schemas: list[ToolSchema] = []
    names: set[str] = set()

    for tool in tools:
        if tool.name in names:
            raise ValueError(f"Duplicate tool schema: {tool.name}")
        names.add(tool.name)

        properties: dict[str, dict[str, Any]] = {}
        required: list[str] = []

        for argument_name, argument_schema in tool.arguments_schema.items():
            if isinstance(argument_schema, str):
                property_schema: dict[str, Any] = {
                    "type": "string",
                    "description": argument_schema,
                }
                is_required = True
            elif isinstance(argument_schema, dict):
                property_schema = deepcopy(argument_schema)
                is_required = property_schema.pop("x-required", True)
                if not isinstance(property_schema.get("type"), str):
                    raise ValueError(
                        f"Tool argument schema must define a type: "
                        f"{tool.name}.{argument_name}"
                    )
                if not isinstance(is_required, bool):
                    raise ValueError(
                        f"Tool argument required marker must be a boolean: "
                        f"{tool.name}.{argument_name}"
                    )
            else:
                raise ValueError(
                    f"Invalid tool argument schema: {tool.name}.{argument_name}"
                )

            properties[argument_name] = property_schema
            if is_required:
                required.append(argument_name)

        schemas.append(
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            }
        )

    return schemas


def build_tools_context(tools: list[Tool]) -> str:
    """Build provider-independent tool usage instructions without schemas."""
    if not tools:
        return "No tools are currently available."

    parts = [
        TOOLS_CONTEXT_HEADER,
        "",
        "Use a tool only when it is necessary "
        "to fulfill the user's explicit request.",
        "",
        "Do not use tools for greetings, "
        "casual conversation, acknowledgements, "
        "or questions that can be answered directly.",
        "",
        "Do not inspect files or execute commands "
        "unless the user's request requires it.",
        "",
        "Do not claim that a tool succeeded "
        "unless it was actually executed.",
    ]

    return "\n".join(parts).strip()


def build_text_tools_context(tool_schemas: list[ToolSchema]) -> str:
    """Render structured schemas for text-only provider compatibility."""
    if not tool_schemas:
        return "No tools are currently available."

    parts = ["Available tools:", ""]

    for tool_schema in tool_schemas:
        parts.append(f"Tool: {tool_schema['name']}")
        parts.append(f"Description: {tool_schema['description']}")
        properties = tool_schema["parameters"]["properties"]

        if properties:
            parts.append("Arguments:")
            for argument_name, property_schema in properties.items():
                parts.append(
                    f"- {argument_name}: "
                    + json.dumps(
                        property_schema,
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                )
        else:
            parts.append("Arguments: none")

        parts.append("")

    parts.extend(
        [
            "Tool call format:",
            "",
            "When you need to use a tool, respond only with valid JSON.",
            "",
            "{",
            '  "tool": "<tool_name>",',
            '  "arguments": {',
            '    "<argument_name>": "<argument_value>"',
            "  }",
            "}",
            "",
            "Do not wrap the JSON in Markdown.",
            "Do not include explanatory text before or after the JSON.",
        ]
    )

    return "\n".join(parts).strip()
