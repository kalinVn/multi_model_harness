from harness.domain.command import Command

# Взима създадения Command обект с полетата name, description и sections.
# Изгражда от тях текстов контекст, който се подава към LLM модела.
#
# Пример за входен Command обект:
# name = "write_file"
# description = "Creates a new file"
# sections = {"Usage": "write_file path content"}
#
# Резултатът е един форматиран текст:
# Name: write_file
# Description: Creates a new file
# Usage: write_file path content

def create_context_from_command_obj(command_obj: Command) -> str:
    parts = [
        (
            "Harness command definition follows. The command name selects this "
            "definition; it is not a shell command and must never be passed to "
            "the bash tool. Follow the Instructions section exactly. For bash, "
            "execute only the shell command explicitly stated in Instructions. "
            "If a matching tool result is already present, do not repeat the "
            "tool call; use that result to finish the command."
        ),
        f"Executing command: {command_obj.name}",
        f"Description:\n{command_obj.description}",
    ]

    for section_name, section_content in command_obj.sections.items():
        parts.append(
            f"{section_name}:\n"
            f"{section_content}"
        )

    return "\n\n".join(parts)
