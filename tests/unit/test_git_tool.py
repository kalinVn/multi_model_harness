import json
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
    GIT_TOOL_ARGUMENTS_SCHEMA,
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

    def test_status_reports_repository_changes(self):
        (self.repository / "untracked.txt").write_text("new\n", encoding="utf-8")

        output = self.read_tool.execute({"operation": "status"})

        self.assertIn("## main", output)
        self.assertIn("?? untracked.txt", output)

    def test_execute_delegates_validation_to_git_tool_validator(self):
        arguments = {"unexpected": "value"}
        with (
            patch.object(
                self.read_tool._validator,
                "validate",
                return_value=("status", {}),
            ) as validate,
            patch.object(
                self.read_tool._service,
                "run",
                return_value="status output",
            ) as run_git,
        ):
            output = self.read_tool.execute(arguments)

        self.assertEqual(output, "status output")
        validate.assert_called_once_with(arguments)
        run_git.assert_called_once_with(
            ["status", "--short", "--branch", "--untracked-files=all"]
        )

    def test_validator_uses_git_tool_service(self):
        self.assertIs(self.read_tool._validator._service, self.read_tool._service)

    def test_uses_shared_git_tool_configuration(self):
        self.assertEqual(self.read_tool.description, GIT_TOOL_DESCRIPTION)
        self.assertEqual(self.read_tool.arguments_schema, GIT_TOOL_ARGUMENTS_SCHEMA)
        self.assertIsNot(self.read_tool.arguments_schema, GIT_TOOL_ARGUMENTS_SCHEMA)
        self.assertIs(GitTool.READ_OPERATIONS, READ_OPERATIONS)
        self.assertIs(GitTool.WRITE_OPERATIONS, WRITE_OPERATIONS)
        self.assertIs(GitTool.REMOTE_OPERATIONS, REMOTE_OPERATIONS)
        self.assertIs(GitTool.OPERATIONS, SUPPORTED_OPERATIONS)

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

    def test_command_builder_dynamically_dispatches_operation(self):
        with patch.object(
            self.read_tool._command_builder,
            "_build_status_command",
            return_value=["status-command"],
        ) as build_status:
            command = self.read_tool._command_builder.build("status", {})

        self.assertEqual(command, ["status-command"])
        build_status.assert_called_once_with({})

    def test_diff_supports_worktree_and_staged_changes(self):
        (self.repository / "tracked.txt").write_text("changed\n", encoding="utf-8")

        worktree_output = self.read_tool.execute(
            {"operation": "diff", "args": {"path": "tracked.txt"}}
        )
        self.assertIn("+changed", worktree_output)

        self._git("add", "tracked.txt")
        staged_output = self.read_tool.execute(
            {"operation": "diff", "args": {"staged": True}}
        )
        self.assertIn("+changed", staged_output)

    def test_log_limits_results(self):
        output = self.read_tool.execute(
            {"operation": "log", "args": {"max_count": 1}}
        )

        self.assertIn("Initial commit", output)
        self.assertEqual(len(output.splitlines()), 1)

    def test_branch_list_marks_current_branch(self):
        output = self.read_tool.execute({"operation": "branch_list"})

        self.assertIn("* main", output)

    def test_show_returns_commit_and_file_content(self):
        commit_output = self.read_tool.execute(
            {"operation": "show", "args": {"revision": "HEAD"}}
        )
        file_output = self.read_tool.execute(
            {
                "operation": "show",
                "args": {"revision": "HEAD", "path": "tracked.txt"},
            }
        )

        self.assertIn("Initial commit", commit_output)
        self.assertEqual(file_output, "initial")

    def test_tag_list_reports_local_tags(self):
        self._git("tag", "v1.0.0")

        output = self.read_tool.execute({"operation": "tag_list"})

        self.assertEqual(output, "v1.0.0")

    def test_remote_list_reports_names_without_urls(self):
        remote = self._create_bare_remote()

        output = self.read_tool.execute({"operation": "remote_list"})

        self.assertEqual(output, "origin")
        self.assertNotIn(str(remote), output)

    def test_blame_reports_file_history(self):
        output = self.read_tool.execute(
            {"operation": "blame", "args": {"path": "tracked.txt"}}
        )

        self.assertIn("Harness Tests", output)
        self.assertIn("initial", output)

    def test_rev_parse_resolves_revision(self):
        output = self.read_tool.execute(
            {"operation": "rev_parse", "args": {"revision": "HEAD"}}
        )

        self.assertEqual(output, self._git("rev-parse", "HEAD"))

    def test_reflog_limits_results(self):
        output = self.read_tool.execute(
            {"operation": "reflog", "args": {"max_count": 1}}
        )

        self.assertIn("commit (initial): Initial commit", output)
        self.assertEqual(len(output.splitlines()), 1)

    def test_ls_files_lists_tracked_paths(self):
        output = self.read_tool.execute({"operation": "ls_files"})

        self.assertEqual(output, "tracked.txt")

    def test_add_stages_only_valid_repository_paths(self):
        (self.repository / "new.txt").write_text("new\n", encoding="utf-8")

        self.write_tool.execute(
            {"operation": "add", "args": {"paths": ["new.txt"]}}
        )

        self.assertIn("A  new.txt", self._git("status", "--short"))

    def test_commit_creates_local_commit(self):
        (self.repository / "new.txt").write_text("new\n", encoding="utf-8")
        self.write_tool.execute(
            {"operation": "add", "args": {"paths": ["new.txt"]}}
        )

        output = self.write_tool.execute(
            {"operation": "commit", "args": {"message": "Add new file"}}
        )

        self.assertIn("Add new file", output)
        self.assertEqual(self._git("log", "-1", "--pretty=%s"), "Add new file")

    def test_branch_create_and_switch(self):
        self.write_tool.execute(
            {"operation": "branch_create", "args": {"name": "feature/test"}}
        )
        self.assertIn("feature/test", self._git("branch", "--list"))

        output = self.write_tool.execute(
            {"operation": "switch", "args": {"branch": "feature/test"}}
        )

        self.assertIn("Switched to branch 'feature/test'", output)
        self.assertEqual(self._git("branch", "--show-current"), "feature/test")

    def test_branch_rename_and_safe_delete(self):
        self._git("branch", "old-name")

        self.write_tool.execute(
            {
                "operation": "branch_rename",
                "args": {"old_name": "old-name", "new_name": "new-name"},
            }
        )
        self.assertIn("new-name", self._git("branch", "--list"))

        self.write_tool.execute(
            {"operation": "branch_delete", "args": {"name": "new-name"}}
        )
        self.assertNotIn("new-name", self._git("branch", "--list"))

    def test_branch_delete_rejects_unmerged_branch(self):
        self._git("switch", "-c", "unmerged")
        self._commit_file("unmerged.txt", "unmerged\n", "Unmerged commit")
        self._git("switch", "main")

        with self.assertRaisesRegex(RuntimeError, "not fully merged"):
            self.write_tool.execute(
                {"operation": "branch_delete", "args": {"name": "unmerged"}}
            )

        self.assertIn("unmerged", self._git("branch", "--list"))

    def test_merge_integrates_branch(self):
        self._git("switch", "-c", "feature")
        self._commit_file("feature.txt", "feature\n", "Feature commit")
        self._git("switch", "main")

        output = self.write_tool.execute(
            {"operation": "merge", "args": {"branch": "feature"}}
        )

        self.assertTrue((self.repository / "feature.txt").is_file())
        self.assertIn("Fast-forward", output)

    def test_merge_conflict_is_reported(self):
        self._git("switch", "-c", "conflicting")
        self._commit_file("tracked.txt", "branch change\n", "Branch change")
        self._git("switch", "main")
        self._commit_file("tracked.txt", "main change\n", "Main change")

        with self.assertRaisesRegex(RuntimeError, "Git command failed"):
            self.write_tool.execute(
                {"operation": "merge", "args": {"branch": "conflicting"}}
            )

        contents = (self.repository / "tracked.txt").read_text(encoding="utf-8")
        self.assertIn("<<<<<<<", contents)

    def test_cherry_pick_applies_commit(self):
        self._git("switch", "-c", "feature")
        revision = self._commit_file("picked.txt", "picked\n", "Picked commit")
        self._git("switch", "main")

        self.write_tool.execute(
            {"operation": "cherry_pick", "args": {"revision": revision}}
        )

        self.assertEqual(
            (self.repository / "picked.txt").read_text(encoding="utf-8"),
            "picked\n",
        )

    def test_restore_only_unstages_paths(self):
        (self.repository / "tracked.txt").write_text("changed\n", encoding="utf-8")
        self._git("add", "tracked.txt")

        self.write_tool.execute(
            {
                "operation": "restore",
                "args": {"paths": ["tracked.txt"], "staged": True},
            }
        )

        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")
        self.assertEqual(self._git("diff", "--name-only"), "tracked.txt")

    def test_reset_supports_only_soft_and_mixed_modes(self):
        self._commit_file("second.txt", "second\n", "Second commit")

        self.write_tool.execute(
            {"operation": "reset", "args": {"mode": "soft", "revision": "HEAD~1"}}
        )
        self.assertIn("second.txt", self._git("diff", "--cached", "--name-only"))

        self._git("commit", "-m", "Second commit again")
        self.write_tool.execute(
            {"operation": "reset", "args": {"mode": "mixed", "revision": "HEAD~1"}}
        )
        self.assertEqual(self._git("diff", "--cached", "--name-only"), "")
        self.assertIn("?? second.txt", self._git("status", "--short"))

    def test_stash_list_and_pop_round_trip_changes(self):
        (self.repository / "tracked.txt").write_text("stashed\n", encoding="utf-8")

        self.write_tool.execute(
            {"operation": "stash", "args": {"message": "Harness stash"}}
        )
        self.assertEqual(
            (self.repository / "tracked.txt").read_text(encoding="utf-8"),
            "initial\n",
        )
        self.assertIn(
            "Harness stash",
            self.read_tool.execute({"operation": "stash_list"}),
        )

        self.write_tool.execute({"operation": "stash_pop", "args": {"index": 0}})
        self.assertEqual(
            (self.repository / "tracked.txt").read_text(encoding="utf-8"),
            "stashed\n",
        )

    def test_tag_create_and_delete(self):
        self.write_tool.execute(
            {"operation": "tag_create", "args": {"name": "v2.0.0"}}
        )
        self.assertIn("v2.0.0", self._git("tag", "--list"))

        self.write_tool.execute(
            {"operation": "tag_delete", "args": {"name": "v2.0.0"}}
        )
        self.assertNotIn("v2.0.0", self._git("tag", "--list"))

    def test_accepts_json_encoded_operation_arguments(self):
        output = self.read_tool.execute(
            {
                "operation": "log",
                "args": json.dumps({"max_count": 1}),
            }
        )

        self.assertIn("Initial commit", output)

    def test_fetch_updates_remote_tracking_references(self):
        self._create_bare_remote()
        self._git("push", "origin", "main")

        self.remote_tool.execute(
            {"operation": "fetch", "args": {"remote": "origin"}}
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

        self.remote_tool.execute(
            {
                "operation": "pull",
                "args": {"remote": "origin", "branch": "main"},
            }
        )

        self.assertEqual(
            (self.repository / "remote.txt").read_text(encoding="utf-8"),
            "remote\n",
        )

    def test_push_uses_same_branch_and_never_force_pushes(self):
        remote = self._create_bare_remote()

        output = self.remote_tool.execute(
            {
                "operation": "push",
                "args": {"remote": "origin", "branch": "main"},
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
            {"operation": "rebase"},
            {"operation": "status", "unexpected": "value"},
            {"operation": "status", "args": []},
            {"operation": "status", "args": "not-json"},
            {"operation": "status", "args": {"extra": True}},
            {"operation": "diff", "args": {"staged": "yes"}},
            {"operation": "log", "args": {"max_count": 0}},
            {"operation": "show", "args": {"revision": "--help"}},
            {"operation": "add", "args": {"paths": []}},
            {"operation": "commit", "args": {"message": " "}},
            {"operation": "branch_create", "args": {"name": "--help"}},
        ]

        for arguments in invalid_calls:
            if arguments.get("operation") in GitTool.WRITE_OPERATIONS:
                tool = self.write_tool
            else:
                tool = self.read_tool
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                tool.execute(arguments)

    def test_rejects_invalid_arguments_for_extended_operations(self):
        invalid_calls = [
            (self.read_tool, {"operation": "tag_list", "args": {"pattern": "*"}}),
            (self.read_tool, {"operation": "blame", "args": {"path": "."}}),
            (self.read_tool, {"operation": "rev_parse", "args": {"revision": "--all"}}),
            (self.read_tool, {"operation": "reflog", "args": {"max_count": 101}}),
            (self.write_tool, {"operation": "branch_rename", "args": {"old_name": "main"}}),
            (self.write_tool, {"operation": "branch_delete", "args": {"name": "--force"}}),
            (self.write_tool, {"operation": "merge", "args": {"branch": "--abort"}}),
            (self.write_tool, {"operation": "cherry_pick", "args": {"revision": "--abort"}}),
            (
                self.write_tool,
                {
                    "operation": "restore",
                    "args": {"paths": ["tracked.txt"], "staged": False},
                },
            ),
            (self.write_tool, {"operation": "reset", "args": {"mode": "hard"}}),
            (self.write_tool, {"operation": "stash", "args": {"include_untracked": "yes"}}),
            (self.write_tool, {"operation": "stash_pop", "args": {"index": -1}}),
            (self.write_tool, {"operation": "tag_create", "args": {"name": "--force"}}),
            (self.remote_tool, {"operation": "fetch", "args": {"remote": "missing"}}),
            (self.remote_tool, {"operation": "pull", "args": {"remote": "origin"}}),
            (
                self.remote_tool,
                {
                    "operation": "push",
                    "args": {"remote": "origin", "branch": "--force"},
                },
            ),
        ]

        for tool, arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                tool.execute(arguments)

    def test_rejects_paths_outside_repository_and_git_metadata(self):
        outside_path = self.root / "outside.txt"
        outside_path.write_text("outside\n", encoding="utf-8")

        for path in ("../outside.txt", str(outside_path), ".git/config", ":(top)*"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.write_tool.execute(
                    {"operation": "add", "args": {"paths": [path]}}
                )

    def test_rejects_working_directory_that_is_not_repository_root(self):
        subdirectory = self.repository / "nested"
        subdirectory.mkdir()

        with self.assertRaisesRegex(ValueError, "repository root"):
            GitTool(working_directory=subdirectory).execute({"operation": "status"})

        outside_directory = self.root / "not-a-repository"
        outside_directory.mkdir()
        with self.assertRaisesRegex(RuntimeError, "Not a Git repository"):
            GitTool(working_directory=outside_directory).execute({"operation": "status"})

    def test_surfaces_git_command_failures(self):
        with self.assertRaisesRegex(RuntimeError, "Git command failed"):
            self.write_tool.execute(
                {"operation": "switch", "args": {"branch": "missing-branch"}}
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
            "GROQ_API_KEY": "groq-secret-value",
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
            "GROQ_API_KEY",
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
                "environment-secret, groq-secret-value, and tiny"
            ),
        )
        with (
            patch.dict(
                "os.environ",
                {
                    "GROQ_API_KEY": "groq-secret-value",
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
        self.assertNotIn("groq-secret-value", message)
        self.assertNotIn("tiny", message)
        self.assertIn("<redacted>", message)
        self.assertNotIn("GROQ_API_KEY", run_git.call_args.kwargs["env"])
        self.assertNotIn("SERVICE_TOKEN", run_git.call_args.kwargs["env"])
        self.assertNotIn("SHORT_TOKEN", run_git.call_args.kwargs["env"])

    def test_write_operations_are_disabled_by_default(self):
        calls = [
            {"operation": "add", "args": {"paths": ["tracked.txt"]}},
            {"operation": "commit", "args": {"message": "Message"}},
            {"operation": "branch_create", "args": {"name": "feature"}},
            {
                "operation": "branch_rename",
                "args": {"old_name": "main", "new_name": "renamed"},
            },
            {"operation": "branch_delete", "args": {"name": "feature"}},
            {"operation": "switch", "args": {"branch": "main"}},
            {"operation": "merge", "args": {"branch": "main"}},
            {"operation": "cherry_pick", "args": {"revision": "HEAD"}},
            {
                "operation": "restore",
                "args": {"paths": ["tracked.txt"], "staged": True},
            },
            {"operation": "reset", "args": {"mode": "mixed"}},
            {"operation": "stash"},
            {"operation": "stash_pop"},
            {"operation": "tag_create", "args": {"name": "v1"}},
            {"operation": "tag_delete", "args": {"name": "v1"}},
        ]

        for arguments in calls:
            with self.subTest(operation=arguments["operation"]):
                with self.assertRaisesRegex(PermissionError, "disabled"):
                    self.read_tool.execute(arguments)

    def test_remote_operations_are_disabled_separately(self):
        calls = [
            {"operation": "fetch", "args": {"remote": "origin"}},
            {
                "operation": "pull",
                "args": {"remote": "origin", "branch": "main"},
            },
            {
                "operation": "push",
                "args": {"remote": "origin", "branch": "main"},
            },
        ]

        for arguments in calls:
            with self.subTest(operation=arguments["operation"]):
                with self.assertRaisesRegex(PermissionError, "remote operations"):
                    self.read_tool.execute(arguments)

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

        git_tool = registry.get("git")
        git_tool.execute(
            {"operation": "branch_create", "args": {"name": "registered"}}
        )

        self.assertIn("registered", self._git("branch", "--list"))

        self._create_bare_remote()
        self._git("push", "origin", "main")
        git_tool.execute(
            {"operation": "fetch", "args": {"remote": "origin"}}
        )


if __name__ == "__main__":
    unittest.main()
