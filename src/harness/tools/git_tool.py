import os
import re
import subprocess
from pathlib import Path
from typing import Any

from harness.validators.git_tool_validator import GitToolValidator


class GitTool:
    READ_OPERATIONS = GitToolValidator.READ_OPERATIONS
    WRITE_OPERATIONS = GitToolValidator.WRITE_OPERATIONS
    REMOTE_OPERATIONS = GitToolValidator.REMOTE_OPERATIONS
    OPERATIONS = GitToolValidator.OPERATIONS

    def __init__(
        self,
        working_directory: Path | None = None,
        allow_write_operations: bool = False,
        allow_remote_operations: bool = False,
        timeout_seconds: int = 30,
    ) -> None:
        self._working_directory = (working_directory or Path.cwd()).resolve()
        self._timeout_seconds = timeout_seconds
        self._validator = GitToolValidator(
            working_directory=self._working_directory,
            allow_write_operations=allow_write_operations,
            allow_remote_operations=allow_remote_operations,
            run_git=lambda arguments, **options: self._run_git(
                arguments,
                **options,
            ),
        )

    @property
    def name(self) -> str:
        return "git"

    @property
    def description(self) -> str:
        return (
            "Runs allowlisted Git operations in the project repository. "
            "Read, local write, and remote operations are separately restricted. "
            "Destructive and force variants are unavailable."
        )

    @property
    def arguments_schema(self) -> dict[str, str | dict[str, Any]]:
        return {
            "operation": {
                "type": "string",
                "enum": sorted(self.OPERATIONS),
                "description": "The allowlisted Git operation to execute.",
            },
            "args": {
                "type": "object",
                "description": (
                    "Operation-specific arguments. For add, paths is required. "
                    "For commit, message is required. Use an empty object when "
                    "the selected operation takes no arguments."
                ),
                "properties": {
                    "branch": {"type": "string"},
                    "include_untracked": {"type": "boolean"},
                    "index": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "max_count": {"type": "integer", "minimum": 1, "maximum": 100},
                    "message": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 1000,
                        "description": "Required for commit; the commit message.",
                    },
                    "mode": {"type": "string", "enum": ["soft", "mixed"]},
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "old_name": {"type": "string"},
                    "path": {"type": "string"},
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "maxItems": 100,
                        "description": "Required for add; repository-relative paths to stage.",
                    },
                    "remote": {"type": "string"},
                    "revision": {"type": "string"},
                    "staged": {"type": "boolean"},
                },
                "additionalProperties": False,
                "x-required": False,
            },
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        operation, operation_arguments = self._validator.validate(arguments)
        
        command = getattr(self, f"_build_{operation}_command")(operation_arguments)
        return self._run_git(command)

    def _build_status_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, set(), "status")
        return ["status", "--short", "--branch", "--untracked-files=all"]

    def _build_diff_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"staged", "path"}, "diff")
        staged = self._validator.validate_boolean(
            arguments.get("staged", False),
            "git diff args.staged must be a boolean.",
        )

        command = ["diff", "--no-ext-diff", "--no-textconv", "--no-color"]
        if staged:
            command.append("--cached")

        command.append("--")
        path = arguments.get("path")
        if path is not None:
            command.append(self._validator.validate_path(path, "diff"))

        return command

    def _build_log_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"max_count"}, "log")
        max_count = self._validator.validate_max_count(
            arguments.get("max_count", 20),
            "log",
        )
        return ["log", "--oneline", "--no-decorate", f"--max-count={max_count}"]

    def _build_branch_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, set(), "branch_list")
        return ["branch", "--list", "--no-color"]

    def _build_show_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"revision", "path"}, "show")
        revision = self._validator.validate_revision(
            arguments.get("revision", "HEAD")
        )
        path = arguments.get("path")

        if path is not None:
            relative_path = self._validator.validate_file_path(path, "show")
            return [
                "show",
                "--no-ext-diff",
                "--no-textconv",
                "--no-color",
                f"{revision}:{relative_path}",
            ]

        return [
            "show",
            "--no-ext-diff",
            "--no-textconv",
            "--no-color",
            "--format=fuller",
            revision,
            "--",
        ]

    def _build_tag_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, set(), "tag_list")
        return ["tag", "--list", "--sort=refname"]

    def _build_remote_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, set(), "remote_list")
        return ["remote"]

    def _build_blame_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"path", "revision"},
            "blame",
            required={"path"},
        )
        revision = self._validator.validate_revision(
            arguments.get("revision", "HEAD")
        )
        path = self._validator.validate_file_path(arguments["path"], "blame")

        return ["blame", "--date=short", revision, "--", path]

    def _build_rev_parse_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"revision"}, "rev_parse")
        revision = self._validator.validate_revision(
            arguments.get("revision", "HEAD")
        )
        return ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{object}}"]

    def _build_reflog_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"max_count"}, "reflog")
        max_count = self._validator.validate_max_count(
            arguments.get("max_count", 20),
            "reflog",
        )
        return ["reflog", "--oneline", f"--max-count={max_count}"]

    def _build_ls_files_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"path"}, "ls_files")
        command = ["ls-files", "--"]
        path = arguments.get("path")
        if path is not None:
            command.append(self._validator.validate_path(path, "ls_files"))
        return command

    def _build_stash_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, set(), "stash_list")
        return ["stash", "list"]

    def _build_add_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"paths"},
            "add",
            required={"paths"},
        )
        paths = self._validator.validate_paths(arguments["paths"], "add")
        return ["add", "--", *paths]

    def _build_commit_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"message"},
            "commit",
            required={"message"},
        )
        message = self._validator.validate_message(arguments["message"], "commit")

        return ["commit", "--no-verify", "--no-gpg-sign", "-m", message]

    def _build_branch_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"name"},
            "branch_create",
            required={"name"},
        )
        branch_name = self._validator.validate_branch_name(arguments["name"])
        return ["branch", "--no-track", branch_name]

    def _build_branch_rename_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"old_name", "new_name"},
            "branch_rename",
            required={"old_name", "new_name"},
        )
        old_name = self._validator.validate_branch_name(arguments["old_name"])
        new_name = self._validator.validate_branch_name(arguments["new_name"])
        return ["branch", "-m", old_name, new_name]

    def _build_branch_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"name"},
            "branch_delete",
            required={"name"},
        )
        branch_name = self._validator.validate_branch_name(arguments["name"])
        return ["branch", "-d", branch_name]

    def _build_switch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"branch"},
            "switch",
            required={"branch"},
        )
        branch_name = self._validator.validate_branch_name(arguments["branch"])
        return ["switch", "--no-guess", branch_name]

    def _build_merge_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"branch"},
            "merge",
            required={"branch"},
        )
        branch_name = self._validator.validate_branch_name(arguments["branch"])
        return ["merge", "--no-edit", "--no-gpg-sign", branch_name]

    def _build_cherry_pick_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"revision"},
            "cherry_pick",
            required={"revision"},
        )
        revision = self._validator.validate_revision(arguments["revision"])
        return ["cherry-pick", "--no-gpg-sign", revision]

    def _build_restore_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"paths", "staged"},
            "restore",
            required={"paths", "staged"},
        )
        self._validator.validate_restore_staged(arguments["staged"])
        paths = self._validator.validate_paths(arguments["paths"], "restore")
        return ["restore", "--staged", "--", *paths]

    def _build_reset_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"mode", "revision"},
            "reset",
            required={"mode"},
        )
        mode = self._validator.validate_reset_mode(arguments["mode"])
        revision = self._validator.validate_revision(
            arguments.get("revision", "HEAD")
        )
        return ["reset", f"--{mode}", revision]

    def _build_stash_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"include_untracked", "message"},
            "stash",
        )
        include_untracked = self._validator.validate_boolean(
            arguments.get("include_untracked", False),
            "git stash args.include_untracked must be a boolean.",
        )

        command = ["stash", "push"]
        if include_untracked:
            command.append("--include-untracked")

        message = arguments.get("message")
        if message is not None:
            message = self._validator.validate_message(message, "stash")
            command.extend(["--message", message])

        command.append("--")
        return command

    def _build_stash_pop_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, {"index"}, "stash_pop")
        index = self._validator.validate_stash_index(arguments.get("index", 0))
        return ["stash", "pop", f"stash@{{{index}}}"]

    def _build_tag_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"name", "revision"},
            "tag_create",
            required={"name"},
        )
        tag_name = self._validator.validate_tag_name(arguments["name"])
        revision = self._validator.validate_revision(
            arguments.get("revision", "HEAD")
        )
        return ["tag", tag_name, revision]

    def _build_tag_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"name"},
            "tag_delete",
            required={"name"},
        )
        return [
            "tag",
            "-d",
            self._validator.validate_tag_name(arguments["name"]),
        ]

    def _build_fetch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"remote"},
            "fetch",
            required={"remote"},
        )
        return [
            "fetch",
            "--no-tags",
            self._validator.validate_remote_name(arguments["remote"]),
        ]

    def _build_pull_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"branch", "remote"},
            "pull",
            required={"branch", "remote"},
        )
        remote = self._validator.validate_remote_name(arguments["remote"])
        branch = self._validator.validate_branch_name(arguments["branch"])
        return ["pull", "--ff-only", "--no-rebase", remote, branch]

    def _build_push_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(
            arguments,
            {"branch", "remote"},
            "push",
            required={"branch", "remote"},
        )
        remote = self._validator.validate_remote_name(arguments["remote"])
        branch = self._validator.validate_branch_name(arguments["branch"])
        refspec = f"refs/heads/{branch}:refs/heads/{branch}"
        return ["push", "--porcelain", "--no-verify", remote, refspec]

    def _run_git(
        self,
        arguments: list[str],
        failure_prefix: str = "Git command failed",
    ) -> str:
        environment = os.environ.copy()
        environment.update(
            {
                "GIT_PAGER": "cat",
                "GIT_TERMINAL_PROMPT": "0",
                "LC_ALL": "C",
                "PAGER": "cat",
            }
        )

        try:
            completed_process = subprocess.run(
                ["git", "-c", "core.hooksPath=/dev/null", *arguments],
                cwd=self._working_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except FileNotFoundError as error:
            raise RuntimeError("Git executable was not found.") from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                f"Git command timed out after {self._timeout_seconds} seconds."
            ) from error

        stdout = self._redact_sensitive_output(
            completed_process.stdout.strip(),
            environment,
        )
        stderr = self._redact_sensitive_output(
            completed_process.stderr.strip(),
            environment,
        )
        if completed_process.returncode != 0:
            details = stderr or stdout or f"exit code {completed_process.returncode}"
            raise RuntimeError(f"{failure_prefix}: {details}")

        output = "\n".join(part for part in (stdout, stderr) if part)
        return output or "Git command completed successfully."

    def _redact_sensitive_output(
        self,
        output: str,
        environment: dict[str, str],
    ) -> str:
        output = re.sub(
            r"(https?://)[^/@\s]+@",
            r"\1<redacted>@",
            output,
        )
        sensitive_markers = ("KEY", "PASSWORD", "SECRET", "TOKEN")
        for name, value in environment.items():
            if (
                value
                and len(value) >= 8
                and any(marker in name.upper() for marker in sensitive_markers)
            ):
                output = output.replace(value, "<redacted>")
        return output
