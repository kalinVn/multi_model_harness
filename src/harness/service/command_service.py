from harness.domain.message import Message
from harness.loader.command_context_loader import get_command_message_obj
from harness.loader.command_loader import CommandLoader
from harness.parser.command_parser import ParsedCommand
from harness.resolver.command_resolver import CommandResolver
from harness.tools.tool_registry import ToolRegistry


class CommandService:
    """Prepare command-specific messages."""

    def __init__(
        self,
        command_resolver: CommandResolver,
        command_loader: CommandLoader,
        tool_registry: ToolRegistry,
    ) -> None:
        self._command_resolver = command_resolver
        self._command_loader = command_loader
        self._tool_registry = tool_registry

    def prepare_command_context(
        self,
        parsed_command: ParsedCommand,
    ) -> Message:
        """Build the model context for a parsed command."""
        return get_command_message_obj(
            parsed_command.name,
            command_resolver=self._command_resolver,
            tool_registry=self._tool_registry,
            command_loader=self._command_loader,
        )

    def prepare_command_summary_message(
        self,
        parsed_command: ParsedCommand,
        command_summary: str,
    ) -> Message:
        """Build the system message that summarizes a completed command."""
        return Message(
            role="system",
            content=(
                "Command execution summary: "
                f"{parsed_command.name} was executed. Result: "
                f"{command_summary}"
            ),
        )
