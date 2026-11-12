import json
from copy import deepcopy

from harness.contracts.tool import Tool
from harness.models.tool_definition import ToolDefinition
from harness.validators.tool_validator import ToolValidator


def build_tool_parameters(
    tools: list[Tool],
) -> list[ToolDefinition]:
    """Build provider-independent parameters for registered tools."""

    ToolValidator.validate(tools)
    tool_parameters_objects: list[ToolDefinition] = []

    for tool in tools:
        parameter_object = tool.get_parameter_object()
        ToolValidator.validate_parameter_object(tool.name, parameter_object)

        tool_parameters_objects.append(
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": deepcopy(parameter_object),
            }
        )

    return tool_parameters_objects


def build_text_tools_context(tool_definitions: list[ToolDefinition]) -> str:
    """Render structured schemas for text-only provider compatibility."""
    if not tool_definitions:
        return "No tools are currently available."

    parts = ["Available tools:", ""]

    for tool_definition in tool_definitions:
        parts.append(f"Tool: {tool_definition['name']}")
        parts.append(f"Description: {tool_definition['description']}")
        properties = tool_definition["parameters"]["properties"]

        if properties:
            parts.append("Arguments:")
            for parameter_name, property_schema in properties.items():
                parts.append(
                    f"- {parameter_name}: "
                    + json.dumps(
                        property_schema,
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                )
        else:
            parts.append("Arguments: none")

        parts.append("")

    return "\n".join(parts).strip()
