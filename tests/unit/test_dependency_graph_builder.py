import tempfile
import unittest
from pathlib import Path

from harness.builder.dependency_graph_builder import DependencyGraphBuilder


class DependencyGraphBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.builder = DependencyGraphBuilder(self.root)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write(self, path: str, content: str = "") -> Path:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_builds_single_node_without_dependencies(self):
        self.write("root.md", "No dependencies.")

        result = self.builder.build("root.md")

        self.assertEqual(result.roots, ["root.md"])
        self.assertEqual(result.files, ["root.md"])
        self.assertEqual(result.nodes["root.md"].dependencies, [])
        self.assertEqual(result.cycles, [])
        self.assertEqual(result.unresolved, [])

    def test_discovers_one_direct_dependency(self):
        self.write("root.md", "Read `docs/child.md`.")
        self.write("docs/child.md")

        result = self.builder.build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, ["docs/child.md"])
        self.assertEqual(result.files, ["root.md", "docs/child.md"])

    def test_preserves_first_discovery_order_for_multiple_dependencies(self):
        self.write("root.md", "Read `b.md`, then `a.md`.")
        self.write("a.md")
        self.write("b.md")

        result = self.builder.build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, ["b.md", "a.md"])
        self.assertEqual(result.files, ["root.md", "b.md", "a.md"])

    def test_deduplicates_repeated_dependency_edges(self):
        self.write("root.md", "Read `child.md`, then follow `child.md`.")
        self.write("child.md")

        result = self.builder.build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, ["child.md"])

    def test_discovers_nested_dependencies(self):
        self.write("a.md", "Read `b.md`.")
        self.write("b.md", "Read `c.md`.")
        self.write("c.md")

        result = self.builder.build("a.md")

        self.assertEqual(result.files, ["a.md", "b.md", "c.md"])
        self.assertEqual(result.nodes["b.md"].dependencies, ["c.md"])

    def test_supports_shared_dependencies(self):
        self.write("a.md", "Read `shared.md`.")
        self.write("b.md", "Read `shared.md`.")
        self.write("shared.md")

        result = self.builder.build(["a.md", "b.md"])

        self.assertEqual(result.files, ["a.md", "shared.md", "b.md"])
        self.assertEqual(result.nodes["a.md"].dependencies, ["shared.md"])
        self.assertEqual(result.nodes["b.md"].dependencies, ["shared.md"])

    def test_detects_child_reference_to_ancestor(self):
        self.write("a.md", "Read `b.md`.")
        self.write("b.md", "Return to `a.md`.")

        result = self.builder.build("a.md")

        self.assertEqual(result.nodes["b.md"].dependencies, ["a.md"])
        self.assertEqual(result.cycles, [["a.md", "b.md", "a.md"]])

    def test_detects_longer_cycle_without_duplicate_nodes(self):
        self.write("a.md", "Read `b.md`.")
        self.write("b.md", "Read `c.md`.")
        self.write("c.md", "Read `a.md`.")

        result = self.builder.build("a.md")

        self.assertEqual(result.files, ["a.md", "b.md", "c.md"])
        self.assertEqual(result.cycles, [["a.md", "b.md", "c.md", "a.md"]])

    def test_supports_multiple_unique_roots(self):
        self.write("one.md")
        self.write("two.md")

        result = self.builder.build(["one.md", "two.md", "one.md"])

        self.assertEqual(result.roots, ["one.md", "two.md"])
        self.assertEqual(result.files, ["one.md", "two.md"])

    def test_supports_multiple_dots_and_hidden_directories(self):
        self.write("root.md", "Use `.caisa/rules/v1.2.rules.md`.")
        self.write(".caisa/rules/v1.2.rules.md")

        result = self.builder.build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, [".caisa/rules/v1.2.rules.md"])

    def test_ignores_non_file_inline_code_and_fenced_code(self):
        self.write("root.md", "Run `npm install` with `NODE_ENV=production`.\n\n```md\n`hidden.md`\n```")
        self.write("hidden.md")

        result = self.builder.build("root.md")

        self.assertEqual(result.files, ["root.md"])
        self.assertEqual(result.unresolved, [])

    def test_records_missing_reference_with_source_location(self):
        self.write("root.md", "First line.\nRead `missing.md`.")

        result = self.builder.build("root.md")

        self.assertEqual(len(result.unresolved), 1)
        self.assertEqual(result.unresolved[0].source, "root.md")
        self.assertEqual(result.unresolved[0].reference, "missing.md")
        self.assertEqual(result.unresolved[0].line, 2)
        self.assertEqual(result.unresolved[0].column, 7)
        self.assertEqual(result.unresolved[0].reason, "referenced file does not exist")

    def test_records_runtime_placeholder_without_fake_node(self):
        self.write("root.md", "Use `specification_path=<repository-relative path>`.")

        result = self.builder.build("root.md")

        self.assertEqual(result.files, ["root.md"])
        self.assertEqual(result.unresolved[0].reason, "runtime placeholder")

    def test_records_reference_that_escapes_repository(self):
        self.write("nested/root.md", "Read `../../outside.md`.")

        result = self.builder.build("nested/root.md")

        self.assertEqual(result.unresolved[0].reason, "path escapes the repository root")

    def test_rejects_invalid_initial_paths(self):
        self.write("directory/child.md")

        with self.assertRaisesRegex(ValueError, "repository-root-relative"):
            self.builder.build(self.root / "directory/child.md")
        with self.assertRaisesRegex(ValueError, "cannot escape"):
            self.builder.build("../outside.md")
        with self.assertRaisesRegex(FileNotFoundError, "does not exist"):
            self.builder.build("missing.md")
        with self.assertRaisesRegex(FileNotFoundError, "regular file"):
            self.builder.build("directory")

    def test_rejects_unreadable_initial_content(self):
        target = self.root / "invalid.md"
        target.write_bytes(b"\xff")

        with self.assertRaisesRegex(ValueError, "unreadable"):
            self.builder.build("invalid.md")

    def test_discovers_supported_text_dependency(self):
        self.write("root.md", "Read `notes/context.txt`.")
        self.write("notes/context.txt", "Text context")

        result = self.builder.build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, ["notes/context.txt"])
        self.assertIn("notes/context.txt", result.nodes)

    def test_normalizes_legacy_relative_reference_from_source_directory(self):
        self.write("docs/commands/root.md", "Read `../../shared/context.md`.")
        self.write("shared/context.md")

        result = self.builder.build("docs/commands/root.md")

        self.assertEqual(result.nodes["docs/commands/root.md"].dependencies, ["shared/context.md"])

    def test_normalizes_path_separators(self):
        self.write("docs/root.md", "Read `docs\\child.md`.")
        self.write("docs/child.md")

        result = self.builder.build("docs\\root.md")

        self.assertEqual(result.roots, ["docs/root.md"])
        self.assertEqual(result.nodes["docs/root.md"].dependencies, ["docs/child.md"])

    def test_supports_configurable_extensions(self):
        self.write("root.md", "Read `notes/context.rst` and ignore `data.json`.")
        self.write("notes/context.rst")
        self.write("data.json")

        result = DependencyGraphBuilder(self.root, supported_extensions=("md", "rst")).build("root.md")

        self.assertEqual(result.nodes["root.md"].dependencies, ["notes/context.rst"])
        self.assertNotIn("data.json", result.nodes)

    def test_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside_directory:
            outside = Path(outside_directory) / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            (self.root / "escape.md").symlink_to(outside)
            self.write("root.md", "Read `escape.md`.")

            result = self.builder.build("root.md")

        self.assertEqual(result.files, ["root.md"])
        self.assertEqual(result.unresolved[0].reason, "path escapes the repository root")


class DependencyGraphBuilderIntegrationTests(unittest.TestCase):
    def test_build_frontend_discovers_recursive_workflow_context(self):
        project_root = Path(__file__).resolve().parents[2]

        result = DependencyGraphBuilder(project_root).build(".caisa/commands/build_frontend.md")

        self.assertIn(".caisa/commands/build_frontend.md", result.nodes)
        self.assertIn(".caisa/agents/new-frontend-orchestrator.md", result.nodes)
        self.assertIn(".caisa/skills/workflow-new-frontend.md", result.nodes)
        self.assertEqual(
            result.nodes[".caisa/agents/new-frontend-orchestrator.md"].dependencies,
            [".caisa/skills/workflow-new-frontend.md"]
        )


if __name__ == "__main__":
    unittest.main()
