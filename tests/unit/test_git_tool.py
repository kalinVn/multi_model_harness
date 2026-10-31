import json
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness.builder.git_command_builder import GitCommandBuilder
from harness.config.git_tool_config import (
    GIT_ARGUMENT_PROPERTIES,
    GIT_ALLOWED_ENVIRONMENT_VARIABLES,
    GIT_ENVIRONMENT_OVERRIDES,
    GIT_OPERATION_DEFINITIONS,
    GIT_TOOL_PARAMETER_OBJECT,
    GIT_TOOL_DESCRIPTION,
    READ_OPERATIONS,
    REMOTE_OPERATIONS,
    SUPPORTED_OPERATIONS,
    WRITE_OPERATIONS,
)
from harness.tools.git_tool import GitTool
from harness.tools.register_tools import register_tools
from harness.tools.tool_registry import ToolRegistry


class GitToolTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()

        self._git("init", "-b", "main")
        self._git("config", "user.name", "Harness Tests")
        self._git("config", "user.email", "harness@example.test")
        (self.repository / "tracked.txt").write_text("initial\n", encoding="utf-8")
        self._git("add", "tracked.txt")
        self._git("commit", "-m", "Initial commit")

        self.read_tool = GitTool(working_directory=self.repository)
        self.write_tool = GitTool(
            working_directory=self.repository,
            allow_write_operations=True,
        )
        self.remote_tool = GitTool(
            working_directory=self.repository,
            allow_remote_operations=True,
        )

    def _git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repository,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def _create_bare_remote(self) -> Path:
        remote = self.root / "remote.git"
        subprocess.run(
            ["git", "init", "--bare", str(remote)],
            capture_output=True,
            text=True,
            check=True,
        )
        self._git("remote", "add", "origin", str(remote))
        return remote

    def _commit_file(self, path: str, content: str, message: str) -> str:
        (self.repository / path).write_text(content, encoding="utf-8")
        self._git("add", path)
        self._git("commit", "-m", message)
        return self._git("rev-parse", "HEAD")

    def _execute(self, tool: GitTool, arguments: dict) -> str:
        """Run one command through the batch API for focused behavior tests."""
        batch_arguments = dict(arguments)
        command = batch_arguments.pop("tokens", None)
        batch_arguments.pop("expected_operation", None)

        if command is not None:
            if isinstance(command, list) and all(
                isinstance(token, str) for token in command
            ):
                batch_arguments["commands"] = (
                    [shlex.join(command)] if command else []
                )
            else:
                batch_arguments["commands"] = command

        output = json.loads(tool.execute(batch_arguments))
        result = output["results"][0]
        if not result["success"]:
            raise RuntimeError(result["error"])
        return result["output"]

    def test_status_reports_repository_changes(self):
        (self.repository / "untracked.txt").write_text("new\n", encoding="utf-8")

        output = self._execute(self.read_tool,
            {
                "expected_operation": "status",
                "tokens": [
                    "status",
                    "--short",
                    "--branch",
                    "--untracked-files=all",
                ],
            }
        )

        self.assertIn("## main", output)
        self.assertIn("?? untracked.txt", output)

    def test_executes_multiple_commands_and_continues_after_failure(self):
        output = json.loads(
            self.write_tool.execute(
                {
                    "commands": [
                        "status --short --branch --untracked-files=all",
                        "branch -d missing-branch",
                        "log --oneline --no-decorate --max-count=1",
                    ]
                }
            )
        )

        results = output["results"]
        self.assertFalse(output["success"])
        self.assertEqual(
            [result["operation"] for result in results],
            ["status", "branch_delete", "log"],
        )
        self.assertEqual(
            [result["success"] for result in results],
            [True, False, True],
        )
        self.assertIn("Initial commit", results[2]["output"])

    def test_validates_every_command_before_executing_batch(self):
        new_file = self.repository / "new.txt"
        new_file.write_text("new\n", encoding="utf-8")

        with self.assertRaises(ValueError):
            self.write_tool.execute(
                {
                    "commands": [
                        "add -- new.txt",
                        "reset --hard HEAD",
                    ]
                }
            )

        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")

    def test_execute_delegates_validation_to_git_tool_validator(self):
        command = ["status", "--short", "--branch", "--untracked-files=all"]
        command_text = shlex.join(command)
        arguments = {"commands": [command_text]}
        with (
            patch.object(
                self.read_tool._validator,
                "prepare_commands",
                return_value=[(command_text, "status", command)],
            ) as prepare_commands,
            patch.object(
                self.read_tool._service,
                "run",
                return_value="status output",
            ) as run_git,
        ):
            output = self._execute(self.read_tool, arguments)

        self.assertEqual(output, "status output")
        prepare_commands.assert_called_once_with(arguments)
        run_git.assert_called_once_with(command)

    def test_validator_methods_return_none_for_valid_commands(self):
        arguments = {
            "expected_operation": "status",
            "tokens": [
                "status",
                "--short",
                "--branch",
                "--untracked-files=all",
            ],
        }

        self.assertIsNone(
            self.read_tool._validator.validate_command(
                arguments["expected_operation"],
                arguments["tokens"],
            )
        )
        batch_arguments = {"commands": [shlex.join(arguments["tokens"])]}
        self.assertIsNone(self.read_tool._validator.validate(batch_arguments))

    def test_validator_uses_git_tool_service(self):
        self.assertIs(self.read_tool._validator._service, self.read_tool._service)

    def test_uses_shared_git_tool_configuration(self):
        self.assertEqual(self.read_tool.description, GIT_TOOL_DESCRIPTION)
        parameter_object = self.read_tool.get_parameter_object()
        self.assertEqual(parameter_object, GIT_TOOL_PARAMETER_OBJECT)
        self.assertIsNot(parameter_object, GIT_TOOL_PARAMETER_OBJECT)
        self.assertIs(GitTool.READ_OPERATIONS, READ_OPERATIONS)
        self.assertIs(GitTool.WRITE_OPERATIONS, WRITE_OPERATIONS)
        self.assertIs(GitTool.REMOTE_OPERATIONS, REMOTE_OPERATIONS)
        self.assertIs(GitTool.OPERATIONS, SUPPORTED_OPERATIONS)
        self.assertEqual(
            set(parameter_object["properties"]),
            {"commands"},
        )
        self.assertFalse(parameter_object["additionalProperties"])

        self.assertEqual(set(GIT_OPERATION_DEFINITIONS), SUPPORTED_OPERATIONS)
        for operation, definition in GIT_OPERATION_DEFINITIONS.items():
            with self.subTest(operation=operation):
                self.assertTrue(
                    definition["required_arguments"]
                    <= definition["allowed_arguments"]
                )
                self.assertTrue(
                    definition["allowed_arguments"]
                    <= set(GIT_ARGUMENT_PROPERTIES)
                )
                self.assertTrue(
                    hasattr(GitCommandBuilder, f"_build_{operation}_command")
                )
                self.assertTrue(
                    hasattr(
                        self.read_tool._validator,
                        f"_validate_{operation}_command",
                    )
                )

        self.assertFalse(hasattr(self.read_tool, "_command_builder"))

    def test_command_builder_dynamically_dispatches_operation(self):
        command_builder = GitCommandBuilder(self.read_tool._validator)
        with patch.object(
            command_builder,
            "_build_status_command",
            return_value=["status-command"],
        ) as build_status:
            command = command_builder.build("status", {})

        self.assertEqual(command, ["status-command"])
        build_status.assert_called_once_with({})

    def test_diff_supports_worktree_and_staged_changes(self):
        (self.repository / "tracked.txt").write_text("changed\n", encoding="utf-8")

        worktree_output = self._execute(self.read_tool,
            {
                "expected_operation": "diff",
                "tokens": [
                    "diff",
                    "--no-ext-diff",
                    "--no-textconv",
                    "--no-color",
                    "--",
                    "tracked.txt",
                ],
            }
        )
        self.assertIn("+changed", worktree_output)

        self._git("add", "tracked.txt")
        staged_output = self._execute(self.read_tool,
            {
                "expected_operation": "diff",
                "tokens": [
                    "diff",
                    "--no-ext-diff",
                    "--no-textconv",
                    "--no-color",
                    "--cached",
                    "--",
                ],
            }
        )
        self.assertIn("+changed", staged_output)

    def test_log_limits_results(self):
        output = self._execute(self.read_tool,
            {
                "expected_operation": "log",
                "tokens": ["log", "--oneline", "--no-decorate", "--max-count=1"],
            }
        )

        self.assertIn("Initial commit", output)
        self.assertEqual(len(output.splitlines()), 1)

    def test_branch_list_marks_current_branch(self):
        output = self._execute(self.read_tool,
            {
                "expected_operation": "branch_list",
                "tokens": ["branch", "--list", "--no-color"],
            }
        )

        self.assertIn("* main", output)

    def test_show_returns_commit_and_file_content(self):
        commit_output = self._execute(self.read_tool,
            {
                "expected_operation": "show",
                "tokens": [
                    "show",
                    "--no-ext-diff",
                    "--no-textconv",
                    "--no-color",
                    "--format=fuller",
                    "HEAD",
                    "--",
                ],
            }
        )
        file_output = self._execute(self.read_tool,
            {
                "expected_operation": "show",
                "tokens": [
                    "show",
                    "--no-ext-diff",
                    "--no-textconv",
                    "--no-color",
                    "HEAD:tracked.txt",
                ],
            }
        )

        self.assertIn("Initial commit", commit_output)
        self.assertEqual(file_output, "initial")

    def test_tag_list_reports_local_tags(self):
        self._git("tag", "v1.0.0")

        output = self._execute(self.read_tool,
            {
                "expected_operation": "tag_list",
                "tokens": ["tag", "--list", "--sort=refname"],
            }
        )

        self.assertEqual(output, "v1.0.0")

    def test_remote_list_reports_names_without_urls(self):
        remote = self._create_bare_remote()

        output = self._execute(self.read_tool,
            {"expected_operation": "remote_list", "tokens": ["remote"]}
        )

        self.assertEqual(output, "origin")
        self.assertNotIn(str(remote), output)

    def test_blame_reports_file_history(self):
        output = self._execute(self.read_tool,
            {
                "expected_operation": "blame",
                "tokens": ["blame", "--date=short", "HEAD", "--", "tracked.txt"],
            }
        )

        self.assertIn("Harness Tests", output)
        self.assertIn("initial", output)

    def test_rev_parse_resolves_revision(self):
        output = self._execute(self.read_tool,
            {
                "expected_operation": "rev_parse",
                "tokens": [
                    "rev-parse",
                    "--verify",
                    "--end-of-options",
                    "HEAD^{object}",
                ],
            }
        )

        self.assertEqual(output, self._git("rev-parse", "HEAD"))

    def test_reflog_limits_results(self):
        output = self._execute(self.read_tool,
            {
                "expected_operation": "reflog",
                "tokens": ["reflog", "--oneline", "--max-count=1"],
            }
        )

        self.assertIn("commit (initial): Initial commit", output)
        self.assertEqual(len(output.splitlines()), 1)

    def test_ls_files_lists_tracked_paths(self):
        output = self._execute(self.read_tool,
            {"expected_operation": "ls_files", "tokens": ["ls-files", "--"]}
        )

        self.assertEqual(output, "tracked.txt")

    def test_add_stages_only_valid_repository_paths(self):
        (self.repository / "new.txt").write_text("new\n", encoding="utf-8")

        self._execute(self.write_tool,
            {"expected_operation": "add", "tokens": ["add", "--", "new.txt"]}
        )

        self.assertIn("A  new.txt", self._git("status", "--short"))

    def test_add_accepts_standard_git_path_syntax(self):
        (self.repository / "first.txt").write_text("first\n", encoding="utf-8")
        (self.repository / "second.txt").write_text("second\n", encoding="utf-8")

        self._execute(self.write_tool,
            {
                "expected_operation": "add",
                "tokens": ["add", "first.txt", "second.txt"],
            }
        )

        status = self._git("status", "--short")
        self.assertIn("A  first.txt", status)
        self.assertIn("A  second.txt", status)

    def test_commit_creates_local_commit(self):
        (self.repository / "new.txt").write_text("new\n", encoding="utf-8")
        self._execute(self.write_tool,
            {"expected_operation": "add", "tokens": ["add", "--", "new.txt"]}
        )

        output = self._execute(self.write_tool,
            {
                "expected_operation": "commit",
                "tokens": [
                    "commit",
                    "--no-verify",
                    "--no-gpg-sign",
                    "-m",
                    "Add new file",
                ],
            }
        )

        self.assertIn("Add new file", output)
        self.assertEqual(self._git("log", "-1", "--pretty=%s"), "Add new file")

    def test_commit_accepts_standard_message_syntax(self):
        (self.repository / "standard.txt").write_text("new\n", encoding="utf-8")
        self._execute(self.write_tool,
            {"expected_operation": "add", "tokens": ["add", "standard.txt"]}
        )

        output = self._execute(self.write_tool,
            {
                "expected_operation": "commit",
                "tokens": ["commit", "-m", "Use standard syntax"],
            }
        )

        self.assertIn("Use standard syntax", output)
        self.assertEqual(
            self._git("log", "-1", "--pretty=%s"),
            "Use standard syntax",
        )

    def test_branch_create_and_switch(self):
        self._execute(self.write_tool,
            {
                "expected_operation": "branch_create",
                "tokens": ["branch", "--no-track", "feature/test"],
            }
        )
        self.assertIn("feature/test", self._git("branch", "--list"))

        output = self._execute(self.write_tool,
            {
                "expected_operation": "switch",
                "tokens": ["switch", "--no-guess", "feature/test"],
            }
        )

        self.assertIn("Switched to branch 'feature/test'", output)
        self.assertEqual(self._git("branch", "--show-current"), "feature/test")

    def test_branch_rename_and_safe_delete(self):
        self._git("branch", "old-name")

        self._execute(self.write_tool,
            {
                "expected_operation": "branch_rename",
                "tokens": ["branch", "-m", "old-name", "new-name"],
            }
        )
        self.assertIn("new-name", self._git("branch", "--list"))

        self._execute(self.write_tool,
            {
                "expected_operation": "branch_delete",
                "tokens": ["branch", "-d", "new-name"],
            }
        )
        self.assertNotIn("new-name", self._git("branch", "--list"))

    def test_branch_delete_rejects_unmerged_branch(self):
        self._git("switch", "-c", "unmerged")
        self._commit_file("unmerged.txt", "unmerged\n", "Unmerged commit")
        self._git("switch", "main")

        with self.assertRaisesRegex(RuntimeError, "not fully merged"):
            self._execute(self.write_tool,
                {
                    "expected_operation": "branch_delete",
                    "tokens": ["branch", "-d", "unmerged"],
                }
            )

        self.assertIn("unmerged", self._git("branch", "--list"))

    def test_merge_integrates_branch(self):
        self._git("switch", "-c", "feature")
        self._commit_file("feature.txt", "feature\n", "Feature commit")
        self._git("switch", "main")

        output = self._execute(self.write_tool,
            {
                "expected_operation": "merge",
                "tokens": ["merge", "--no-edit", "--no-gpg-sign", "feature"],
            }
        )

        self.assertTrue((self.repository / "feature.txt").is_file())
        self.assertIn("Fast-forward", output)

    def test_merge_conflict_is_reported(self):
        self._git("switch", "-c", "conflicting")
        self._commit_file("tracked.txt", "branch change\n", "Branch change")
        self._git("switch", "main")
        self._commit_file("tracked.txt", "main change\n", "Main change")

        with self.assertRaisesRegex(RuntimeError, "Git command failed"):
            self._execute(self.write_tool,
                {
                    "expected_operation": "merge",
                    "tokens": [
                        "merge",
                        "--no-edit",
                        "--no-gpg-sign",
                        "conflicting",
                    ],
                }
            )

        contents = (self.repository / "tracked.txt").read_text(encoding="utf-8")
        self.assertIn("<<<<<<<", contents)

    def test_cherry_pick_applies_commit(self):
        self._git("switch", "-c", "feature")
        revision = self._commit_file("picked.txt", "picked\n", "Picked commit")
        self._git("switch", "main")

        self._execute(self.write_tool,
            {
                "expected_operation": "cherry_pick",
                "tokens": ["cherry-pick", "--no-gpg-sign", revision],
            }
        )

        self.assertEqual(
            (self.repository / "picked.txt").read_text(encoding="utf-8"),
            "picked\n",
        )

    def test_restore_only_unstages_paths(self):
        (self.repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
        self._git("add", "tracked.txt")

        self._execute(self.write_tool,
            {
                "expected_operation": "restore",
                "tokens": ["restore", "--staged", "--", "tracked.txt"],
            }
        )

        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")
        self.assertEqual(self._git("diff", "--name-only"), "tracked.txt")

    def test_reset_supports_only_soft_and_mixed_modes(self):
        self._commit_file("second.txt", "second\n", "Second commit")

        self._execute(self.write_tool,
            {
                "expected_operation": "reset",
                "tokens": ["reset", "--soft", "HEAD~1"],
            }
        )
        self.assertIn("second.txt", self._git("diff", "--cached", "--name-only"))

        self._git("commit", "-m", "Second commit again")
        self._execute(self.write_tool,
            {
                "expected_operation": "reset",
                "tokens": ["reset", "--mixed", "HEAD~1"],
            }
        )
        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")
        self.assertIn("?? second.txt", self._git("status", "--short"))

    def test_stash_list_and_pop_round_trip_changes(self):
        (self.repository / "tracked.txt").write_text("stashed\n", encoding="utf-8")

        self._execute(self.write_tool,
            {
                "expected_operation": "stash",
                "tokens": ["stash", "push", "--message", "Harness stash", "--"],
            }
        )
        self.assertEqual(
            (self.repository / "tracked.txt").read_text(encoding="utf-8"),
            "initial\n",
        )
        self.assertIn(
            "Harness stash",
            self._execute(self.read_tool,
                {"expected_operation": "stash_list", "tokens": ["stash", "list"]}
            ),
        )

        self._execute(self.write_tool,
            {
                "expected_operation": "stash_pop",
                "tokens": ["stash", "pop", "stash@{0}"],
            }
        )
        self.assertEqual(
            (self.repository / "tracked.txt").read_text(encoding="utf-8"),
            "stashed\n",
        )

    def test_tag_create_and_delete(self):
        self._execute(self.write_tool,
            {
                "expected_operation": "tag_create",
                "tokens": ["tag", "v2.0.0", "HEAD"],
            }
        )
        self.assertIn("v2.0.0", self._git("tag", "--list"))

        self._execute(self.write_tool,
            {
                "expected_operation": "tag_delete",
                "tokens": ["tag", "-d", "v2.0.0"],
            }
        )
        self.assertNotIn("v2.0.0", self._git("tag", "--list"))

    def test_rejects_json_encoded_command(self):
        with self.assertRaisesRegex(ValueError, "must be an array"):
            self._execute(self.read_tool,
                {
                    "expected_operation": "log",
                    "tokens": json.dumps(
                        ["log", "--oneline", "--no-decorate", "--max-count=1"]
                    ),
                }
            )

    def test_fetch_updates_remote_tracking_references(self):
        self._create_bare_remote()
        self._git("push", "origin", "main")

        self._execute(self.remote_tool,
            {
                "expected_operation": "fetch",
                "tokens": ["fetch", "--no-tags", "origin"],
            }
        )

        self.assertEqual(
            self._git("rev-parse", "refs/remotes/origin/main"),
            self._git("rev-parse", "main"),
        )

    def test_pull_allows_only_fast_forward_integration(self):
        remote = self._create_bare_remote()
        self._git("push", "origin", "main")
        contributor = self.root / "contributor"
        subprocess.run(
            ["git", "clone", "--branch", "main", str(remote), str(contributor)],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Contributor"],
            cwd=contributor,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "contributor@example.test"],
            cwd=contributor,
            check=True,
        )
        (contributor / "remote.txt").write_text("remote\n", encoding="utf-8")
        subprocess.run(["git", "add", "remote.txt"], cwd=contributor, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Remote commit"],
            cwd=contributor,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=contributor,
            capture_output=True,
            check=True,
        )

        self._execute(self.remote_tool,
            {
                "expected_operation": "pull",
                "tokens": [
                    "pull",
                    "--ff-only",
                    "--no-rebase",
                    "origin",
                    "main",
                ],
            }
        )

        self.assertEqual(
            (self.repository / "remote.txt").read_text(encoding="utf-8"),
            "remote\n",
        )

    def test_push_uses_same_branch_and_never_force_pushes(self):
        remote = self._create_bare_remote()

        output = self._execute(self.remote_tool,
            {
                "expected_operation": "push",
                "tokens": [
                    "push",
                    "--porcelain",
                    "--no-verify",
                    "origin",
                    "refs/heads/main:refs/heads/main",
                ],
            }
        )

        remote_revision = subprocess.run(
            ["git", "--git-dir", str(remote), "rev-parse", "refs/heads/main"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertIn("refs/heads/main:refs/heads/main", output)
        self.assertEqual(remote_revision, self._git("rev-parse", "main"))

    def test_rejects_invalid_operations_and_arguments(self):
        invalid_calls = [
            {},
            {"expected_operation": "rebase", "tokens": ["rebase", "main"]},
            {
                "expected_operation": "status",
                "tokens": ["status"],
                "unexpected": "value",
            },
            {"expected_operation": "status", "tokens": []},
            {"expected_operation": "status", "tokens": "status"},
            {"expected_operation": "status", "tokens": ["status", "--porcelain"]},
            {"expected_operation": "status", "tokens": ["-c", "alias.status=!sh"]},
            {"expected_operation": "status", "tokens": ["status", "&&", "push"]},
            {"expected_operation": "status", "tokens": ["status", 1]},
            {"expected_operation": "status", "tokens": ["status\0"]},
            {
                "expected_operation": "commit",
                "tokens": ["commit", "--no-verify", "--no-gpg-sign", "-m", " "],
            },
        ]

        for arguments in invalid_calls:
            if arguments.get("expected_operation") in GitTool.WRITE_OPERATIONS:
                tool = self.write_tool
            else:
                tool = self.read_tool
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self._execute(tool, arguments)

    def test_rejects_invalid_arguments_for_extended_operations(self):
        invalid_calls = [
            (
                self.read_tool,
                {
                    "expected_operation": "tag_list",
                    "tokens": ["tag", "--list", "--sort=refname", "*"],
                },
            ),
            (
                self.read_tool,
                {
                    "expected_operation": "blame",
                    "tokens": ["blame", "--date=short", "HEAD", "--", "."],
                },
            ),
            (
                self.read_tool,
                {
                    "expected_operation": "rev_parse",
                    "tokens": [
                        "rev-parse",
                        "--verify",
                        "--end-of-options",
                        "--all^{object}",
                    ],
                },
            ),
            (
                self.read_tool,
                {
                    "expected_operation": "reflog",
                    "tokens": ["reflog", "--oneline", "--max-count=101"],
                },
            ),
            (
                self.write_tool,
                {"expected_operation": "branch_rename", "tokens": ["branch", "-m", "main"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "branch_delete", "tokens": ["branch", "-D", "main"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "merge", "tokens": ["merge", "--abort"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "cherry_pick", "tokens": ["cherry-pick", "--abort"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "restore", "tokens": ["restore", "tracked.txt"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "reset", "tokens": ["reset", "--hard", "HEAD"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "stash", "tokens": ["stash", "push", "--all", "--"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "stash_pop", "tokens": ["stash", "pop", "stash@{-1}"]},
            ),
            (
                self.write_tool,
                {"expected_operation": "tag_create", "tokens": ["tag", "--force", "HEAD"]},
            ),
            (
                self.remote_tool,
                {"expected_operation": "fetch", "tokens": ["fetch", "--no-tags", "missing"]},
            ),
            (
                self.remote_tool,
                {
                    "expected_operation": "fetch",
                    "tokens": ["fetch", "--no-tags", "https://example.test/repo"],
                },
            ),
            (
                self.remote_tool,
                {"expected_operation": "pull", "tokens": ["pull", "origin", "main"]},
            ),
            (
                self.remote_tool,
                {
                    "expected_operation": "push",
                    "tokens": [
                        "push",
                        "--force",
                        "origin",
                        "refs/heads/main:refs/heads/main",
                    ],
                },
            ),
            (
                self.remote_tool,
                {
                    "expected_operation": "push",
                    "tokens": [
                        "push",
                        "--porcelain",
                        "--no-verify",
                        "origin",
                        "refs/heads/main:refs/heads/other",
                    ],
                },
            ),
        ]

        for tool, arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self._execute(tool, arguments)

    def test_rejects_paths_outside_repository_and_git_metadata(self):
        outside_path = self.root / "outside.txt"
        outside_path.write_text("outside\n", encoding="utf-8")

        for path in ("../outside.txt", str(outside_path), ".git/config", ":(top)*"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self._execute(self.write_tool,
                    {"expected_operation": "add", "tokens": ["add", "--", path]}
                )

    def test_rejects_working_directory_that_is_not_repository_root(self):
        subdirectory = self.repository / "nested"
        subdirectory.mkdir()

        with self.assertRaisesRegex(ValueError, "repository root"):
            GitTool(working_directory=subdirectory).execute(
                {
                    "commands": [
                        "status --short --branch --untracked-files=all"
                    ],
                }
            )

        outside_directory = self.root / "not-a-repository"
        outside_directory.mkdir()
        with self.assertRaisesRegex(RuntimeError, "Not a Git repository"):
            GitTool(working_directory=outside_directory).execute(
                {
                    "commands": [
                        "status --short --branch --untracked-files=all"
                    ],
                }
            )

    def test_surfaces_git_command_failures(self):
        with self.assertRaisesRegex(RuntimeError, "Git command failed"):
            self._execute(self.write_tool,
                {
                    "expected_operation": "switch",
                    "tokens": ["switch", "--no-guess", "missing-branch"],
                }
            )

    def test_git_service_passes_only_allowlisted_environment_variables(self):
        completed_process = subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=0,
            stdout="status output",
            stderr="",
        )
        parent_environment = {
            "PATH": "/usr/bin",
            "HOME": "/home/harness",
            "USER": "harness",
            "LOGNAME": "harness",
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
            "SSH_AUTH_SOCK": "/tmp/ssh-agent.sock",
            "XDG_CONFIG_HOME": "/home/harness/.config",
            "OPENAI_API_KEY": "openai-secret-value",
            "GEMINI_API_KEY": "gemini-secret-value",
            "SERVICE_PASSWORD": "service-secret-value",
            "UNRELATED_SETTING": "unrelated-value",
        }

        with (
            patch.dict("os.environ", parent_environment, clear=True),
            patch(
                "harness.service.git_tool_service.subprocess.run",
                return_value=completed_process,
            ) as run_git,
        ):
            output = self.read_tool._service.run(["status"])

        self.assertEqual(output, "status output")
        self.assertNotIn("shell", run_git.call_args.kwargs)
        child_environment = run_git.call_args.kwargs["env"]
        for name in (
            "PATH",
            "HOME",
            "USER",
            "LOGNAME",
            "LANG",
            "SSH_AUTH_SOCK",
            "XDG_CONFIG_HOME",
        ):
            with self.subTest(name=name):
                self.assertEqual(child_environment[name], parent_environment[name])

        self.assertEqual(child_environment["LC_ALL"], "C")
        self.assertEqual(
            set(child_environment),
            (
                set(parent_environment) & GIT_ALLOWED_ENVIRONMENT_VARIABLES
            )
            | set(GIT_ENVIRONMENT_OVERRIDES),
        )
        for name in (
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "SERVICE_PASSWORD",
            "UNRELATED_SETTING",
        ):
            with self.subTest(name=name):
                self.assertNotIn(name, child_environment)

    def test_redacts_credentials_from_git_output(self):
        completed_process = subprocess.CompletedProcess(
            args=["git", "fetch"],
            returncode=1,
            stdout="",
            stderr=(
                "failed for https://user:password@example.test/ and "
                "environment-secret, provider-secret-value, and tiny"
            ),
        )
        with (
            patch.dict(
                "os.environ",
                {
                    "PROVIDER_API_KEY": "provider-secret-value",
                    "SERVICE_TOKEN": "environment-secret",
                    "SHORT_TOKEN": "tiny",
                },
                clear=True,
            ),
            patch(
                "harness.service.git_tool_service.subprocess.run",
                return_value=completed_process,
            ) as run_git,
        ):
            with self.assertRaises(RuntimeError) as caught:
                self.read_tool._service.run(["fetch"])

        message = str(caught.exception)
        self.assertNotIn("password", message)
        self.assertNotIn("environment-secret", message)
        self.assertNotIn("provider-secret-value", message)
        self.assertNotIn("tiny", message)
        self.assertIn("<redacted>", message)
        self.assertNotIn("PROVIDER_API_KEY", run_git.call_args.kwargs["env"])
        self.assertNotIn("SERVICE_TOKEN", run_git.call_args.kwargs["env"])
        self.assertNotIn("SHORT_TOKEN", run_git.call_args.kwargs["env"])

    def test_write_operations_are_disabled_by_default(self):
        calls = [
            {"expected_operation": "add", "tokens": ["add", "--", "tracked.txt"]},
            {
                "expected_operation": "commit",
                "tokens": [
                    "commit",
                    "--no-verify",
                    "--no-gpg-sign",
                    "-m",
                    "Message",
                ],
            },
            {
                "expected_operation": "branch_create",
                "tokens": ["branch", "--no-track", "feature"],
            },
            {"expected_operation": "branch_rename", "tokens": ["branch", "-m", "main", "renamed"]},
            {"expected_operation": "branch_delete", "tokens": ["branch", "-d", "feature"]},
            {"expected_operation": "switch", "tokens": ["switch", "--no-guess", "main"]},
            {
                "expected_operation": "merge",
                "tokens": ["merge", "--no-edit", "--no-gpg-sign", "main"],
            },
            {
                "expected_operation": "cherry_pick",
                "tokens": ["cherry-pick", "--no-gpg-sign", "HEAD"],
            },
            {
                "expected_operation": "restore",
                "tokens": ["restore", "--staged", "--", "tracked.txt"],
            },
            {"expected_operation": "reset", "tokens": ["reset", "--mixed", "HEAD"]},
            {"expected_operation": "stash", "tokens": ["stash", "push", "--"]},
            {"expected_operation": "stash_pop", "tokens": ["stash", "pop", "stash@{0}"]},
            {"expected_operation": "tag_create", "tokens": ["tag", "v1", "HEAD"]},
            {"expected_operation": "tag_delete", "tokens": ["tag", "-d", "v1"]},
        ]

        for arguments in calls:
            with self.subTest(operation=arguments["expected_operation"]):
                with self.assertRaisesRegex(PermissionError, "disabled"):
                    self._execute(self.read_tool, arguments)

    def test_remote_operations_are_disabled_separately(self):
        calls = [
            {
                "expected_operation": "fetch",
                "tokens": ["fetch", "--no-tags", "origin"],
            },
            {
                "expected_operation": "pull",
                "tokens": ["pull", "--ff-only", "--no-rebase", "origin", "main"],
            },
            {
                "expected_operation": "push",
                "tokens": [
                    "push",
                    "--porcelain",
                    "--no-verify",
                    "origin",
                    "refs/heads/main:refs/heads/main",
                ],
            },
        ]

        for arguments in calls:
            with self.subTest(operation=arguments["expected_operation"]):
                with self.assertRaisesRegex(PermissionError, "remote operations"):
                    self._execute(self.read_tool, arguments)

    def test_register_tools_honors_git_write_and_remote_settings(self):
        registry = ToolRegistry()
        with patch.dict(
            "os.environ",
            {
                "HARNESS_ENABLE_GIT_REMOTE_OPERATIONS": "true",
                "HARNESS_ENABLE_GIT_WRITE_OPERATIONS": "true",
            },
        ):
            register_tools(registry, working_directory=self.repository)

        registry.execute(
            "git",
            {"commands": ["branch --no-track registered"]},
        )

        self.assertIn("registered", self._git("branch", "--list"))

        self._create_bare_remote()
        self._git("push", "origin", "main")
        registry.execute(
            "git",
            {"commands": ["fetch --no-tags origin"]},
        )


if __name__ == "__main__":
    unittest.main()
