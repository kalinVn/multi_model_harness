import json

from harness.contracts.tool import Tool


TOOLS_CONTEXT_HEADER = "Available tools:"


def build_tools_schema(
    tools: list[Tool],
) -> str:
    if not tools:
        return "No tools are currently available."

    parts = [
        TOOLS_CONTEXT_HEADER,
        "",
    ]

    for tool in tools:
        parts.append(f"Tool: {tool.name}")

        parts.append(f"Description: {tool.description}")

        if tool.arguments_schema:
            parts.append("Arguments:")

            for (
                argument_name,
                argument_description,
            ) in tool.arguments_schema.items():
                if isinstance(argument_description, dict):
                    argument_description = json.dumps(
                        argument_description,
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                parts.append(f"- {argument_name}: {argument_description}")
        else:
            parts.append("Arguments: none")

        parts.append("")

    parts.extend(
        [
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
            "Tool call format:",
            "",
            "When you need to use a tool, "
            "respond only with valid JSON.",
            "",
            "{",
            '  "tool": "<tool_name>",',
            '  "arguments": {',
            '    "<argument_name>": "<argument_value>"',
            "  }",
            "}",
            "",
            "Do not wrap the JSON in Markdown.",
            "Do not include explanatory text "
            "before or after the JSON.",
            "Do not claim that a tool succeeded "
            "unless it was actually executed.",
        ]
    )

    return "\n".join(parts).strip()
