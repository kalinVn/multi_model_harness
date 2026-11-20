import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from harness.domain.agent import Agent
from harness.domain.message import Message
from harness.domain.skill import Skill
from harness.loader.agent_loader import AgentLoader
from harness.loader.command_context_loader import get_command_message_obj
from harness.loader.command_loader import CommandLoader
from harness.loader.markdown_loader import MarkdownLoader
from harness.loader.skill_loader import SkillLoader


class CommandLoaderTests(unittest.TestCase):
    def test_parse_sections_preserves_boundaries_and_empty_sections(self):
        content = """Ignored preamble
# Name
example
# Empty
# Description
Example description
# Steps
First line

   
Second line
"""

        sections = MarkdownLoader.parse(content)

        self.assertEqual(
            sections,
            {
                "Name": "example",
                "Empty": "",
                "Description": "Example description",
                "Steps": "First line\n\n   \nSecond line"
            }
        )

    def test_parse_preserves_nested_markdown_lists_and_code_blocks(self):
        content = """# Name
example

# Instructions
Intro paragraph
continues here.

## Workflow
1. Analyze
   - Inspect files
     - Preserve nesting
2. Implement

```markdown
# Not a section
- literal list
```

    indented content
"""

        sections = MarkdownLoader.parse(content)

        self.assertEqual(sections["Name"], "example")
        self.assertEqual(
            sections["Instructions"],
            """Intro paragraph
continues here.

## Workflow
1. Analyze
   - Inspect files
     - Preserve nesting
2. Implement

```markdown
# Not a section
- literal list
```

    indented content"""
        )
        self.assertNotIn("Not a section", sections)

    def test_parse_rejects_duplicate_top_level_sections(self):
        with self.assertRaisesRegex(ValueError, "Duplicate Markdown section: Name"):
            MarkdownLoader.parse("# Name\nfirst\n# Name\nsecond")

    def test_parse_does_not_treat_invalid_heading_as_a_section(self):
        sections = MarkdownLoader.parse("#Name\ninvalid\n# Name\nvalid")

        self.assertEqual(sections, {"Name": "valid"})

    def test_command_loader_reports_missing_section_for_invalid_heading(self):
        with self.assertRaisesRegex(ValueError, "# Name"):
            CommandLoader().get_command_object("#Name\nexample\n# Description\nDescription")

    def test_skill_loader_reports_missing_required_section(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "skill.md"
            path.write_text("# Name\nexample\n# Instructions\nDo work.", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "# Description"):
                SkillLoader().load(path)

    def test_agent_and_skill_loaders_preserve_markdown_instructions(self):
        content = """# Name
example
# Description
Example definition
# Tools
- read_file
- write_file
# Skills
- python
- code-review
# Instructions
Use **Markdown**.

## Workflow
1. Inspect.
2. Implement.
"""

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "definition.md"
            path.write_text(content, encoding="utf-8")
            agent = AgentLoader().load(path)
            skill = SkillLoader().load(path)

        self.assertEqual(
            agent,
            Agent(
                name="example",
                description="Example definition",
                instructions="Use **Markdown**.\n\n## Workflow\n1. Inspect.\n2. Implement.",
                allowed_tools=("read_file", "write_file"),
                allowed_skills=("python", "code-review")
            )
        )
        self.assertEqual(
            skill,
            Skill(
                name="example",
                description="Example definition",
                instructions="Use **Markdown**.\n\n## Workflow\n1. Inspect.\n2. Implement."
            )
        )

    def test_get_command_message_obj_reads_through_tool_registry(self):
        command_path = Path("/project/.caisa/commands/example.md")
        command_resolver = Mock()
        command_resolver.resolve.return_value = command_path
        tool_registry = Mock()
        content = "# Name\nexample\n# Description\nExample description"
        tool_registry.execute.return_value = json.dumps(
            {
                "results": [
                    {
                        "path": str(command_path),
                        "success": True,
                        "content": content,
                    }
                ]
            }
        )

        message = get_command_message_obj(
            "example",
            command_resolver=command_resolver,
            tool_registry=tool_registry,
            command_loader=CommandLoader(),
        )

        tool_registry.execute.assert_called_once_with(
            "read_file",
            {"paths": [str(command_path)]},
        )
        self.assertEqual(
            message,
            Message(
                role="system",
                content=(
                    "Harness command definition follows. The command name "
                    "selects this definition; it is not a shell command and "
                    "must never be passed to the bash tool. Follow the "
                    "Instructions section exactly. For bash, execute only the "
                    "shell command explicitly stated in Instructions. If a "
                    "matching tool result is already present, do not repeat "
                    "the tool call; use that result to finish the command.\n\n"
                    "Executing command: example\n\n"
                    "Description:\nExample description"
                ),
                available_tool_names=(),
                type="command_instruction"
            ),
        )

    def test_get_command_message_obj_exposes_declared_tools(self):
        command_path = Path("/project/.caisa/commands/example.md")
        command_resolver = Mock()
        command_resolver.resolve.return_value = command_path
        tool_registry = Mock()
        tool_registry.execute.return_value = json.dumps({
            "results": [{
                "path": str(command_path),
                "success": True,
                "content": (
                    "# Name\nexample\n# Description\nExample description"
                    "\n# Tools\nbash, read_file"
                )
            }]
        })

        message = get_command_message_obj(
            "example",
            command_resolver=command_resolver,
            tool_registry=tool_registry,
            command_loader=CommandLoader()
        )

        self.assertEqual(message.available_tool_names, ("bash", "read_file"))
        self.assertEqual(
            tool_registry.get.call_args_list,
            [unittest.mock.call("bash"), unittest.mock.call("read_file")]
        )


if __name__ == "__main__":
    unittest.main()
