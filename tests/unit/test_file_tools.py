import json
import tempfile
import unittest
from pathlib import Path

from harness.tools.read_file_tool import ReadFileTool
from harness.tools.tool_registry import ToolRegistry
from harness.tools.write_file_tool import WriteFileTool


class FileToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)

    def test_reads_multiple_files_and_reports_partial_failures(self):
        first = self.root / "first.txt"
        third = self.root / "third.txt"
        missing = self.root / "missing.txt"
        first.write_text("first", encoding="utf-8")
        third.write_text("third", encoding="utf-8")

        output = json.loads(
            ReadFileTool().execute(
                {"paths": [str(first), str(missing), str(third)]}
            )
        )

        results = output["results"]
        self.assertFalse(output["success"])
        self.assertEqual(
            [result["path"] for result in results],
            [str(first), str(missing), str(third)],
        )
        self.assertEqual([result["success"] for result in results], [True, False, True])
        self.assertEqual(results[0]["content"], "first")
        self.assertIn("File not found", results[1]["error"])
        self.assertEqual(results[2]["content"], "third")

    def test_writes_multiple_files_and_reports_partial_failures(self):
        first = self.root / "first.txt"
        blocker = self.root / "blocker"
        blocked = blocker / "blocked.txt"
        third = self.root / "third.txt"
        blocker.write_text("not a directory", encoding="utf-8")

        output = json.loads(
            WriteFileTool().execute(
                {
                    "files": [
                        {"path": str(first), "content": "first"},
                        {"path": str(blocked), "content": "blocked"},
                        {"path": str(third), "content": "third"},
                    ]
                }
            )
        )

        results = output["results"]
        self.assertFalse(output["success"])
        self.assertEqual([result["success"] for result in results], [True, False, True])
        self.assertEqual(first.read_text(encoding="utf-8"), "first")
        self.assertFalse(blocked.exists())
        self.assertEqual(third.read_text(encoding="utf-8"), "third")

    def test_registry_rejects_undeclared_top_level_and_nested_arguments(self):
        registry = ToolRegistry()
        registry.register(WriteFileTool())
        file_definition = {
            "path": str(self.root / "file.txt"),
            "content": "content",
        }

        with self.assertRaisesRegex(ValueError, "undeclared parameters: mode"):
            registry.execute(
                "write_file",
                {"files": [file_definition], "mode": "append"},
            )

        with self.assertRaisesRegex(ValueError, "undeclared parameters: mode"):
            registry.execute(
                "write_file",
                {"files": [{**file_definition, "mode": "append"}]},
            )

    def test_registry_rejects_undeclared_read_arguments(self):
        registry = ToolRegistry()
        registry.register(ReadFileTool())

        with self.assertRaisesRegex(ValueError, "undeclared parameters: mode"):
            registry.execute(
                "read_file",
                {"paths": [str(self.root / "file.txt")], "mode": "binary"}
            )


if __name__ == "__main__":
    unittest.main()
