import json
import unittest
from pathlib import Path
from unittest.mock import Mock

from harness.domain.command import Command
from harness.domain.message import Message
from harness.domain.session import Session
from harness.parser.command_parser import ParsedCommand
from harness.service.command_service import CommandService


class CommandServiceTest(unittest.TestCase):
    def create_service(
        self,
        command_resolver: Mock | None = None,
        command_loader: Mock | None = None,
        tool_registry: Mock | None = None,
    ) -> CommandService:
        return CommandService(
            command_resolver=command_resolver or Mock(),
            command_loader=command_loader or Mock(),
            tool_registry=tool_registry or Mock(),
        )

    def test_prepare_command_summary_message_has_no_session_side_effect(self):
        service = self.create_service()
        session = Session()

        message = service.prepare_command_summary_message(
            ParsedCommand(name="review", arguments=[]),
            "Reviewed the project.",
        )

        self.assertEqual(
            message,
            Message(
                role="system",
                content=(
                    "Command execution summary: review was executed. Result: "
                    "Reviewed the project."
                ),
            ),
        )
        self.assertEqual(session.messages, [])

    def test_prepare_command_context_reuses_existing_dependencies(self):
        command_path = Path("/project/.caisa/commands/review.md")
        command_resolver = Mock()
        command_resolver.resolve.return_value = command_path
        command_loader = Mock()
        command_loader.get_command_object.return_value = Command(
            name="review",
            description="Review the project.",
            sections={},
        )
        tool_registry = Mock()
        tool_registry.execute.return_value = json.dumps(
            {
                "results": [
                    {
                        "path": str(command_path),
                        "success": True,
                        "content": "command file content",
                    }
                ]
            }
        )
        service = self.create_service(command_resolver, command_loader, tool_registry)

        message = service.prepare_command_context(
            ParsedCommand(name="review", arguments=[]),
        )

        command_resolver.resolve.assert_called_once_with("review")
        tool_registry.execute.assert_called_once_with(
            "read_file",
            {"paths": [str(command_path)]},
        )
        command_loader.get_command_object.assert_called_once_with(
            "command file content"
        )
        self.assertEqual(message.role, "system")
        self.assertIn("Executing command: review", message.content)


if __name__ == "__main__":
    unittest.main()
