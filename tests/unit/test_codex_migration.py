import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from harness.agents.main_orchestrator import MainOrchestrator
from harness.domain.agent import Agent
from harness.loader.agent_loader import AgentLoader
from harness.loader.command_loader import CommandLoader
from harness.loader.markdown_loader import MarkdownLoader
from harness.loader.skill_loader import SkillLoader
from harness.models.response import ModelResponse
from harness.registry.agent_registry import AgentRegistry
from harness.skills.skill_registry import SkillRegistry
from scripts.migrate_codex_markdown import adapt_references, demote_top_level_headings, read_frontmatter


class CodexMigrationTests(unittest.TestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.caisa_root = self.project_root / ".caisa"

    def test_frontmatter_conversion_inputs_are_extracted(self):
        metadata, body = read_frontmatter(
            "---\nname: example\ndescription: Example skill.\n---\n\n# Instructions\nUse it.\n"
        )

        self.assertEqual(metadata, {"name": "example", "description": "Example skill."})
        self.assertEqual(body, "\n# Instructions\nUse it.\n")

    def test_heading_demotion_preserves_fenced_hashes_and_nested_content(self):
        content = """# Contract

- Parent
  - Child

```markdown
# Literal heading
```
"""

        converted = demote_top_level_headings(content)

        self.assertTrue(converted.startswith("## Contract"))
        self.assertIn("  - Child", converted)
        self.assertIn("```markdown\n# Literal heading\n```", converted)

    def test_relative_caisa_references_are_adapted(self):
        content = "Read `.codex/workflows/new-frontend.md` and `.codex/skills/plan-new-frontend.md`."

        self.assertEqual(
            adapt_references(content),
            "Read `.caisa/skills/workflow-new-frontend.md` and `.caisa/skills/plan-new-frontend.md`."
        )

    def test_all_migrated_definitions_load_with_real_loaders(self):
        agents = AgentLoader().load_directory(self.caisa_root / "agents")
        skills = SkillLoader().load_directory(self.caisa_root / "skills")
        commands = [
            CommandLoader().get_command_object(path.read_text(encoding="utf-8"))
            for path in sorted((self.caisa_root / "commands").glob("*.md"))
        ]

        self.assertEqual(len(agents), 7)
        self.assertEqual(len(skills), 43)
        self.assertEqual(len(commands), 12)
        self.assertEqual(len({agent.name for agent in agents}), len(agents))
        self.assertEqual(len({skill.name for skill in skills}), len(skills))
        self.assertTrue(agents[0].allowed_skills[0].startswith("workflow-"))
        self.assertIn("Instructions", commands[0].sections)

    def test_agent_directory_reports_missing_required_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.md"
            path.write_text("# Name\ninvalid\n# Instructions\nWork.", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "# Description"):
                AgentLoader().load_directory(Path(directory))

    def test_duplicate_agent_names_are_rejected_by_registry(self):
        duplicate = Agent(name="planner", description="Duplicate", instructions="Do work.")

        with self.assertRaisesRegex(ValueError, "Agent already registered: planner"):
            AgentRegistry(Mock(), Mock(), [], SkillRegistry(), [duplicate])

    def test_invalid_heading_syntax_is_not_corrected(self):
        sections = MarkdownLoader.parse("#Name\ninvalid\n# Description\nValid description")

        self.assertNotIn("Name", sections)

    def test_orchestrator_discovers_migrated_agents_and_skills(self):
        model_client = Mock()
        orchestrator = MainOrchestrator(model_client, project_root=self.project_root)
        agent_names = {agent.name for agent in orchestrator._agent_registry.list_agents()}
        skill_names = {skill.name for skill in orchestrator._skill_registry.list_skills()}

        self.assertIn("planner", agent_names)
        self.assertIn("new-frontend-orchestrator", agent_names)
        self.assertIn("plan-new-frontend", skill_names)
        self.assertIn("workflow-new-frontend", skill_names)

        model_client.generate.return_value = ModelResponse(text="Plan blocked because the specification is missing.")
        result = orchestrator._agent_registry.get("new-frontend-orchestrator").plan("Plan the frontend.")
        system_prompt = model_client.generate.call_args.args[0][0].content

        self.assertEqual(result.content, "Plan blocked because the specification is missing.")
        self.assertIn("New Frontend Orchestrator Role", system_prompt)
        self.assertIn("New Frontend Workflow", system_prompt)

    def test_migration_report_covers_every_repository_local_codex_source(self):
        report = (self.caisa_root / "MIGRATION.md").read_text(encoding="utf-8")
        sources = sorted(
            path.relative_to(self.project_root).as_posix()
            for path in (self.project_root / ".codex").rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml"}
        )

        missing = [source for source in sources if f"`{source}`" not in report]

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
