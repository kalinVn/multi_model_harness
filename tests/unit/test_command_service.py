import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from harness.domain.command import Command
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

    def test_get_dependency_roots_validates_required_file_input(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            command_path = project_root / ".caisa" / "commands" / "build.md"
            specification_path = project_root / "docs" / "spec.md"
            specification_path.parent.mkdir(parents=True)
            specification_path.write_text("Specification", encoding="utf-8")
            command_resolver = Mock()
            command_resolver.resolve.return_value = command_path
            command_loader = Mock()
            command_loader.get_command_object.return_value = Command(
                name="build",
                description="Build.",
                sections={"Invocation": "execute command build specification_path=<repository-relative path>"}
            )
            tool_registry = Mock()
            tool_registry.execute.return_value = json.dumps({
                "results": [{"success": True, "content": "command"}]
            })
            service = self.create_service(command_resolver, command_loader, tool_registry)

            roots = service.get_dependency_roots(
                ParsedCommand(name="build", arguments=["specification_path=docs/spec.md"]),
                project_root
            )

        self.assertEqual(roots, [".caisa/commands/build.md", "docs/spec.md"])

    def test_get_dependency_roots_rejects_missing_required_input(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            command_path = project_root / ".caisa" / "commands" / "build.md"
            command_resolver = Mock()
            command_resolver.resolve.return_value = command_path
            command_loader = Mock()
            command_loader.get_command_object.return_value = Command(
                name="build",
                description="Build.",
                sections={"Invocation": "execute command build specification_path=<repository-relative path>"}
            )
            tool_registry = Mock()
            tool_registry.execute.return_value = json.dumps({
                "results": [{"success": True, "content": "command"}]
            })
            service = self.create_service(command_resolver, command_loader, tool_registry)

            with self.assertRaisesRegex(ValueError, "Required command input is missing: specification_path"):
                service.get_dependency_roots(ParsedCommand(name="build", arguments=[]), project_root)


if __name__ == "__main__":
    unittest.main()
