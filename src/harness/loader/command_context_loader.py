from harness.builder.command_context_builder import create_context_from_command_obj
from harness.domain.message import Message
from harness.loader.command_loader import CommandLoader
from harness.resolver.command_resolver import CommandResolver
from harness.tools.tool_registry import ToolRegistry


def get_command_message_obj(
    command_name: str,
    command_resolver: CommandResolver,
    tool_registry: ToolRegistry,
    command_loader: CommandLoader,
) -> Message:

    # Find the command file path by command name. For example, the input
    # "test_write_file" resolves to the path of "test_write_file.md". Raise
    # an error if no match is found.
    command_path = command_resolver.resolve(command_name)

    args = {
        "path": str(command_path),
    }

    # Read the command Markdown file, such as test_write_file.md.
    read_file_content = tool_registry.execute("read_file", args)

    command_obj = command_loader.get_command_object(read_file_content)

    command_context = create_context_from_command_obj(command_obj)

    return Message(
        role="system",
        content=command_context,
    )
