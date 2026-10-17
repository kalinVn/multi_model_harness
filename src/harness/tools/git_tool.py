import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


class GitTool:
    READ_OPERATIONS = {
        "blame",
        "branch_list",
        "diff",
        "log",
        "ls_files",
        "reflog",
        "remote_list",
        "rev_parse",
        "show",
        "stash_list",
        "status",
        "tag_list",
    }
    WRITE_OPERATIONS = {
        "add",
        "branch_create",
        "branch_delete",
        "branch_rename",
        "cherry_pick",
        "commit",
        "merge",
        "reset",
        "restore",
        "stash",
        "stash_pop",
        "switch",
        "tag_create",
        "tag_delete",
    }
    REMOTE_OPERATIONS = {"fetch", "pull", "push"}
    OPERATIONS = READ_OPERATIONS | WRITE_OPERATIONS | REMOTE_OPERATIONS

    def __init__(
        self,
        working_directory: Path | None = None,
        allow_write_operations: bool = False,
        allow_remote_operations: bool = False,
        timeout_seconds: int = 30,
    ) -> None:
        self._working_directory = (working_directory or Path.cwd()).resolve()
        self._allow_write_operations = allow_write_operations
        self._allow_remote_operations = allow_remote_operations
        self._timeout_seconds = timeout_seconds

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
        if not isinstance(arguments, dict):
            raise ValueError("git arguments must be an object.")

        unexpected_arguments = set(arguments) - {"operation", "args"}
        if unexpected_arguments:
            names = ", ".join(sorted(unexpected_arguments))
            raise ValueError(f"git received unexpected arguments: {names}")

        operation = arguments.get("operation")
        if not isinstance(operation, str) or operation not in self.OPERATIONS:
            allowed = ", ".join(sorted(self.OPERATIONS))
            raise ValueError(f"git operation must be one of: {allowed}")

        if operation in self.WRITE_OPERATIONS and not self._allow_write_operations:
            raise PermissionError(
                "Git write operations are disabled. Set "
                "HARNESS_ENABLE_GIT_WRITE_OPERATIONS=true to enable them."
            )
        if operation in self.REMOTE_OPERATIONS and not self._allow_remote_operations:
            raise PermissionError(
                "Git remote operations are disabled. Set "
                "HARNESS_ENABLE_GIT_REMOTE_OPERATIONS=true to enable them."
            )

        operation_arguments = self._parse_operation_arguments(arguments.get("args"))
        self._ensure_project_repository()

        command = getattr(self, f"_build_{operation}_command")(operation_arguments)
        return self._run_git(command)

    def _parse_operation_arguments(self, value: Any) -> dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as error:
                raise ValueError("git args must contain a valid JSON object.") from error

        if not isinstance(value, dict):
            raise ValueError("git args must be an object or a JSON-encoded object.")

        return value

    def _ensure_project_repository(self) -> None:
        if not self._working_directory.is_dir():
            raise ValueError(
                f"Git working directory does not exist: {self._working_directory}"
            )

        repository_root = self._run_git(
            ["rev-parse", "--show-toplevel"],
            failure_prefix="Not a Git repository",
        )
        if Path(repository_root).resolve() != self._working_directory:
            raise ValueError(
                "Git operations require the configured working directory to be "
                "the repository root."
            )

    def _build_status_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, set(), "status")
        return ["status", "--short", "--branch", "--untracked-files=all"]

    def _build_diff_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"staged", "path"}, "diff")
        staged = arguments.get("staged", False)
        if not isinstance(staged, bool):
            raise ValueError("git diff args.staged must be a boolean.")

        command = ["diff", "--no-ext-diff", "--no-textconv", "--no-color"]
        if staged:
            command.append("--cached")

        command.append("--")
        path = arguments.get("path")
        if path is not None:
            command.append(self._validate_path(path, "diff"))

        return command

    def _build_log_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"max_count"}, "log")
        max_count = self._validate_max_count(arguments.get("max_count", 20), "log")
        return ["log", "--oneline", "--no-decorate", f"--max-count={max_count}"]

    def _build_branch_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, set(), "branch_list")
        return ["branch", "--list", "--no-color"]

    def _build_show_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"revision", "path"}, "show")
        revision = self._validate_revision(arguments.get("revision", "HEAD"))
        path = arguments.get("path")

        if path is not None:
            relative_path = self._validate_path(path, "show")
            if relative_path == ".":
                raise ValueError("git show args.path must identify a file.")
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
        self._require_arguments(arguments, set(), "tag_list")
        return ["tag", "--list", "--sort=refname"]

    def _build_remote_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, set(), "remote_list")
        return ["remote"]

    def _build_blame_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"path", "revision"},
            "blame",
            required={"path"},
        )
        revision = self._validate_revision(arguments.get("revision", "HEAD"))
        path = self._validate_path(arguments["path"], "blame")
        if path == ".":
            raise ValueError("git blame args.path must identify a file.")

        return ["blame", "--date=short", revision, "--", path]

    def _build_rev_parse_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"revision"}, "rev_parse")
        revision = self._validate_revision(arguments.get("revision", "HEAD"))
        return ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{object}}"]

    def _build_reflog_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"max_count"}, "reflog")
        max_count = self._validate_max_count(arguments.get("max_count", 20), "reflog")
        return ["reflog", "--oneline", f"--max-count={max_count}"]

    def _build_ls_files_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"path"}, "ls_files")
        command = ["ls-files", "--"]
        path = arguments.get("path")
        if path is not None:
            command.append(self._validate_path(path, "ls_files"))
        return command

    def _build_stash_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, set(), "stash_list")
        return ["stash", "list"]

    def _build_add_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"paths"}, "add", required={"paths"})
        paths = self._validate_paths(arguments["paths"], "add")
        return ["add", "--", *paths]

    def _build_commit_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"message"}, "commit", required={"message"})
        message = arguments["message"]
        if not isinstance(message, str) or not message.strip():
            raise ValueError("git commit args.message must be a non-empty string.")
        if len(message) > 1000:
            raise ValueError("git commit args.message must not exceed 1000 characters.")

        return ["commit", "--no-verify", "--no-gpg-sign", "-m", message]

    def _build_branch_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"name"}, "branch_create", required={"name"})
        branch_name = self._validate_branch_name(arguments["name"])
        return ["branch", "--no-track", branch_name]

    def _build_branch_rename_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"old_name", "new_name"},
            "branch_rename",
            required={"old_name", "new_name"},
        )
        old_name = self._validate_branch_name(arguments["old_name"])
        new_name = self._validate_branch_name(arguments["new_name"])
        return ["branch", "-m", old_name, new_name]

    def _build_branch_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"name"},
            "branch_delete",
            required={"name"},
        )
        branch_name = self._validate_branch_name(arguments["name"])
        return ["branch", "-d", branch_name]

    def _build_switch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"branch"}, "switch", required={"branch"})
        branch_name = self._validate_branch_name(arguments["branch"])
        return ["switch", "--no-guess", branch_name]

    def _build_merge_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"branch"}, "merge", required={"branch"})
        branch_name = self._validate_branch_name(arguments["branch"])
        return ["merge", "--no-edit", "--no-gpg-sign", branch_name]

    def _build_cherry_pick_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"revision"},
            "cherry_pick",
            required={"revision"},
        )
        revision = self._validate_revision(arguments["revision"])
        return ["cherry-pick", "--no-gpg-sign", revision]

    def _build_restore_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"paths", "staged"},
            "restore",
            required={"paths", "staged"},
        )
        if arguments["staged"] is not True:
            raise ValueError(
                "git restore only supports the safe staged=true variant."
            )
        paths = self._validate_paths(arguments["paths"], "restore")
        return ["restore", "--staged", "--", *paths]

    def _build_reset_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"mode", "revision"},
            "reset",
            required={"mode"},
        )
        mode = arguments["mode"]
        if mode not in {"soft", "mixed"}:
            raise ValueError("git reset args.mode must be 'soft' or 'mixed'.")
        revision = self._validate_revision(arguments.get("revision", "HEAD"))
        return ["reset", f"--{mode}", revision]

    def _build_stash_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"include_untracked", "message"}, "stash")
        include_untracked = arguments.get("include_untracked", False)
        if not isinstance(include_untracked, bool):
            raise ValueError("git stash args.include_untracked must be a boolean.")

        command = ["stash", "push"]
        if include_untracked:
            command.append("--include-untracked")

        message = arguments.get("message")
        if message is not None:
            if not isinstance(message, str) or not message.strip():
                raise ValueError("git stash args.message must be a non-empty string.")
            if len(message) > 1000:
                raise ValueError(
                    "git stash args.message must not exceed 1000 characters."
                )
            command.extend(["--message", message])

        command.append("--")
        return command

    def _build_stash_pop_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(arguments, {"index"}, "stash_pop")
        index = arguments.get("index", 0)
        if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index <= 1000:
            raise ValueError("git stash_pop args.index must be between 0 and 1000.")
        return ["stash", "pop", f"stash@{{{index}}}"]

    def _build_tag_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"name", "revision"},
            "tag_create",
            required={"name"},
        )
        tag_name = self._validate_tag_name(arguments["name"])
        revision = self._validate_revision(arguments.get("revision", "HEAD"))
        return ["tag", tag_name, revision]

    def _build_tag_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"name"},
            "tag_delete",
            required={"name"},
        )
        return ["tag", "-d", self._validate_tag_name(arguments["name"])]

    def _build_fetch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"remote"},
            "fetch",
            required={"remote"},
        )
        return ["fetch", "--no-tags", self._validate_remote_name(arguments["remote"])]

    def _build_pull_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"branch", "remote"},
            "pull",
            required={"branch", "remote"},
        )
        remote = self._validate_remote_name(arguments["remote"])
        branch = self._validate_branch_name(arguments["branch"])
        return ["pull", "--ff-only", "--no-rebase", remote, branch]

    def _build_push_command(self, arguments: dict[str, Any]) -> list[str]:
        self._require_arguments(
            arguments,
            {"branch", "remote"},
            "push",
            required={"branch", "remote"},
        )
        remote = self._validate_remote_name(arguments["remote"])
        branch = self._validate_branch_name(arguments["branch"])
        refspec = f"refs/heads/{branch}:refs/heads/{branch}"
        return ["push", "--porcelain", "--no-verify", remote, refspec]

    def _require_arguments(
        self,
        arguments: dict[str, Any],
        allowed: set[str],
        operation: str,
        required: set[str] | None = None,
    ) -> None:
        unexpected = set(arguments) - allowed
        if unexpected:
            names = ", ".join(sorted(unexpected))
            raise ValueError(f"git {operation} received unexpected args: {names}")

        missing = (required or set()) - set(arguments)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"git {operation} is missing required args: {names}")

    def _validate_path(self, value: Any, operation: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"git {operation} path must be a non-empty string.")
        if "\0" in value or value.startswith(("-", ":")):
            raise ValueError(f"git {operation} path contains a forbidden value.")

        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = self._working_directory / candidate
        resolved_path = candidate.resolve()

        try:
            relative_path = resolved_path.relative_to(self._working_directory)
        except ValueError as error:
            raise ValueError(
                f"git {operation} path must remain inside the project repository."
            ) from error

        if relative_path.parts and relative_path.parts[0] == ".git":
            raise ValueError(f"git {operation} cannot operate on Git metadata.")

        return relative_path.as_posix() or "."

    def _validate_paths(self, value: Any, operation: str) -> list[str]:
        if not isinstance(value, list) or not value:
            raise ValueError(f"git {operation} args.paths must be a non-empty array.")
        if len(value) > 100:
            raise ValueError(f"git {operation} accepts at most 100 paths at a time.")
        return [self._validate_path(path, operation) for path in value]

    def _validate_max_count(self, value: Any, operation: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"git {operation} args.max_count must be an integer.")
        if not 1 <= value <= 100:
            raise ValueError(
                f"git {operation} args.max_count must be between 1 and 100."
            )
        return value

    def _validate_revision(self, value: Any) -> str:
        if not isinstance(value, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/@{}~^+\-]*",
            value,
        ):
            raise ValueError("Git revision must be a non-empty safe revision.")
        return value

    def _validate_branch_name(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git branch name must be a non-empty safe string.")

        try:
            self._run_git(
                ["check-ref-format", "--branch", value],
                failure_prefix="Invalid Git branch name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error

        return value

    def _validate_tag_name(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git tag name must be a non-empty safe string.")

        try:
            self._run_git(
                ["check-ref-format", f"refs/tags/{value}"],
                failure_prefix="Invalid Git tag name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error

        return value

    def _validate_remote_name(self, value: Any) -> str:
        if not isinstance(value, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/\-]*",
            value,
        ):
            raise ValueError("Git remote name must be a non-empty safe string.")

        remote_names = self._run_git(["remote"]).splitlines()
        if value not in remote_names:
            raise ValueError(f"Unknown Git remote: {value}")

        return value

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
