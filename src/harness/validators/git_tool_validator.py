import re
from pathlib import Path
from typing import Any

from harness.config.git_tool_config import (
    GIT_OPERATION_DEFINITIONS,
    GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE,
    GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE,
    MAX_COMMAND_TOKENS,
    MAX_COUNT,
    MAX_MESSAGE_LENGTH,
    MAX_PATHS,
    MAX_STASH_INDEX,
    READ_OPERATIONS,
    REMOTE_OPERATIONS,
    RESET_MODE_VALUES,
    SAFE_REMOTE_NAME_PATTERN,
    SAFE_REVISION_PATTERN,
    SUPPORTED_OPERATIONS,
    TOP_LEVEL_ARGUMENTS,
    WRITE_OPERATIONS,
)
from harness.service.git_tool_service import GitToolService


class GitToolValidator:
    """Validate Git tool permissions and complete command arguments."""

    READ_OPERATIONS = READ_OPERATIONS
    WRITE_OPERATIONS = WRITE_OPERATIONS
    REMOTE_OPERATIONS = REMOTE_OPERATIONS
    OPERATIONS = SUPPORTED_OPERATIONS

    def __init__(
        self,
        working_directory: Path,
        allow_write_operations: bool,
        allow_remote_operations: bool,
        service: GitToolService,
    ) -> None:
        self._working_directory = working_directory
        self._allow_write_operations = allow_write_operations
        self._allow_remote_operations = allow_remote_operations
        self._service = service

    def validate(self, arguments: dict[str, Any]) -> None:
        """
        Validate the top-level Git arguments and repository context.

        Example (valid): {"command_name": "status", "command": ["status", "--short", "--branch", "--untracked-files=all"]}.
        Example (invalid): {"command_name": "status"}.
        Result: ValueError because a required argument is missing.
        """
        if not isinstance(arguments, dict):
            raise ValueError("git arguments must be an object.")

        unexpected_arguments = set(arguments) - TOP_LEVEL_ARGUMENTS
        if unexpected_arguments:
            names = ", ".join(sorted(unexpected_arguments))
            raise ValueError(f"git received unexpected arguments: {names}")

        missing_arguments = TOP_LEVEL_ARGUMENTS - set(arguments)
        if missing_arguments:
            names = ", ".join(sorted(missing_arguments))
            raise ValueError(f"git is missing required arguments: {names}")

        self.validate_command(
            arguments["command_name"],
            arguments["command"],
        )
        self._ensure_project_repository()

    def validate_command(
        self,
        command_name: str,
        command: list[str],
    ) -> None:
        """
        Validate a supported Git command's tokens, permission, and structure.

        Example (valid): command_name="status" with the canonical status tokens.
        Example (invalid): command_name="unknown".
        Result: ValueError, or PermissionError when the operation is disabled.
        """
        if not isinstance(command_name, str) or command_name not in self.OPERATIONS:
            allowed = ", ".join(sorted(self.OPERATIONS))
            raise ValueError(f"git command_name must be one of: {allowed}")
        if not isinstance(command, list) or not command:
            raise ValueError("git command must be a non-empty array.")
        if len(command) > MAX_COMMAND_TOKENS:
            raise ValueError(
                f"git command accepts at most {MAX_COMMAND_TOKENS} tokens."
            )
        if any(not isinstance(token, str) for token in command):
            raise ValueError("git command tokens must be strings.")
        if any("\0" in token for token in command):
            raise ValueError("git command tokens cannot contain NUL bytes.")

        command = self.normalize_safe_command(command_name, command)
        self._validate_operation_permission(command_name)
        validator = getattr(self, f"_validate_{command_name}_command")
        validator(command)

    @staticmethod
    def normalize_safe_command(
        command_name: str,
        command: list[str],
    ) -> list[str]:
        """Convert familiar safe Git syntax to the canonical internal form."""
        if command_name == "add" and command[0] == "add":
            if len(command) >= 2 and command[1] != "--":
                return ["add", "--", *command[1:]]

        if command_name == "commit" and command[0] == "commit":
            if len(command) == 3 and command[1] in {"-m", "--message"}:
                return [
                    "commit",
                    "--no-verify",
                    "--no-gpg-sign",
                    "-m",
                    command[2],
                ]

        return command

    def _validate_operation_permission(self, command_name: str) -> None:
        """
        Validate that the requested Git operation is enabled.

        Example (valid): "status" when read operations are allowed.
        Example (invalid): "commit" when write operations are disabled.
        Result: PermissionError because the operation is not enabled.
        """
        if command_name in self.WRITE_OPERATIONS and not self._allow_write_operations:
            raise PermissionError(
                "Git write operations are disabled. Set "
                f"{GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE}=true to enable them."
            )
        if command_name in self.REMOTE_OPERATIONS and not self._allow_remote_operations:
            raise PermissionError(
                "Git remote operations are disabled. Set "
                f"{GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE}=true to enable them."
            )

    def _validate_status_command(self, command: list[str]) -> None:
        """
        Validate the exact canonical Git status command.

        Example (valid): ["status", "--short", "--branch", "--untracked-files=all"].
        Example (invalid): ["status"].
        Result: ValueError because the command structure is unsupported.
        """
        self._require_exact_command(
            "status",
            command,
            ["status", "--short", "--branch", "--untracked-files=all"],
        )

    def _validate_diff_command(self, command: list[str]) -> None:
        """
        Validate the safe canonical Git diff command and optional path.

        Example (valid): ["diff", "--no-ext-diff", "--no-textconv", "--no-color", "--"].
        Example (invalid): ["diff", "README.md"].
        Result: ValueError because the command structure is unsupported.
        """
        prefix = ["diff", "--no-ext-diff", "--no-textconv", "--no-color"]
        if command[:4] != prefix:
            self._raise_invalid_command("diff")

        index = 4
        canonical_command = list(prefix)
        if index < len(command) and command[index] == "--cached":
            canonical_command.append("--cached")
            index += 1
        if index >= len(command) or command[index] != "--":
            self._raise_invalid_command("diff")

        canonical_command.append("--")
        remaining = command[index + 1 :]
        if len(remaining) > 1:
            self._raise_invalid_command("diff")
        if remaining:
            canonical_command.append(self.validate_path(remaining[0], "diff"))
        self._require_exact_command("diff", command, canonical_command)

    def _validate_log_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git log command and bounded max count.

        Example (valid): ["log", "--oneline", "--no-decorate", "--max-count=10"].
        Example (invalid): ["log", "--oneline"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 4 or command[:3] != [
            "log",
            "--oneline",
            "--no-decorate",
        ]:
            self._raise_invalid_command("log")
        max_count = self._validate_count_option(command[3], "log")
        self._require_exact_command(
            "log",
            command,
            ["log", "--oneline", "--no-decorate", f"--max-count={max_count}"],
        )

    def _validate_branch_list_command(self, command: list[str]) -> None:
        """
        Validate the exact canonical Git branch-list command.

        Example (valid): ["branch", "--list", "--no-color"].
        Example (invalid): ["branch", "--all"].
        Result: ValueError because the command structure is unsupported.
        """
        self._require_exact_command(
            "branch_list",
            command,
            ["branch", "--list", "--no-color"],
        )

    def _validate_show_command(self, command: list[str]) -> None:
        """
        Validate a safe Git show command for a revision or revision path.

        Example (valid): ["show", "--no-ext-diff", "--no-textconv", "--no-color", "HEAD:README.md"].
        Example (invalid): ["show", "HEAD"].
        Result: ValueError because the command structure is unsupported.
        """
        prefix = ["show", "--no-ext-diff", "--no-textconv", "--no-color"]
        if command[:4] != prefix:
            self._raise_invalid_command("show")

        remaining = command[4:]
        if (
            len(remaining) == 3
            and remaining[0] == "--format=fuller"
            and remaining[2] == "--"
        ):
            revision = self.validate_revision(remaining[1])
            self._require_exact_command(
                "show",
                command,
                [*prefix, "--format=fuller", revision, "--"],
            )
            return
        if len(remaining) == 1:
            revision, separator, path = remaining[0].partition(":")
            if not separator:
                self._raise_invalid_command("show")
            revision = self.validate_revision(revision)
            path = self.validate_file_path(path, "show")
            self._require_exact_command(
                "show",
                command,
                [*prefix, f"{revision}:{path}"],
            )
            return

        self._raise_invalid_command("show")

    def _validate_tag_list_command(self, command: list[str]) -> None:
        """
        Validate the exact canonical Git tag-list command.

        Example (valid): ["tag", "--list", "--sort=refname"].
        Example (invalid): ["tag", "--list"].
        Result: ValueError because the command structure is unsupported.
        """
        self._require_exact_command(
            "tag_list",
            command,
            ["tag", "--list", "--sort=refname"],
        )

    def _validate_remote_list_command(self, command: list[str]) -> None:
        """
        Validate the exact canonical Git remote-list command.

        Example (valid): ["remote"].
        Example (invalid): ["remote", "-v"].
        Result: ValueError because the command structure is unsupported.
        """
        self._require_exact_command("remote_list", command, ["remote"])

    def _validate_blame_command(self, command: list[str]) -> None:
        """
        Validate a canonical Git blame command with safe revision and file path.

        Example (valid): ["blame", "--date=short", "HEAD", "--", "README.md"].
        Example (invalid): ["blame", "README.md"].
        Result: ValueError because the command structure is unsupported.
        """
        if (
            len(command) != 5
            or command[:2] != ["blame", "--date=short"]
            or command[3] != "--"
        ):
            self._raise_invalid_command("blame")
        revision = self.validate_revision(command[2])
        path = self.validate_file_path(command[4], "blame")
        self._require_exact_command(
            "blame",
            command,
            ["blame", "--date=short", revision, "--", path],
        )

    def _validate_rev_parse_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git rev-parse object verification command.

        Example (valid): ["rev-parse", "--verify", "--end-of-options", "HEAD^{object}"].
        Example (invalid): ["rev-parse", "HEAD"].
        Result: ValueError because the command structure is unsupported.
        """
        suffix = "^{object}"
        if len(command) != 4 or command[:3] != [
            "rev-parse",
            "--verify",
            "--end-of-options",
        ] or not command[3].endswith(suffix):
            self._raise_invalid_command("rev_parse")
        revision = self.validate_revision(command[3][: -len(suffix)])
        self._require_exact_command(
            "rev_parse",
            command,
            ["rev-parse", "--verify", "--end-of-options", f"{revision}{suffix}"],
        )

    def _validate_reflog_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git reflog command and bounded max count.

        Example (valid): ["reflog", "--oneline", "--max-count=10"].
        Example (invalid): ["reflog", "--oneline"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["reflog", "--oneline"]:
            self._raise_invalid_command("reflog")
        max_count = self._validate_count_option(command[2], "reflog")
        self._require_exact_command(
            "reflog",
            command,
            ["reflog", "--oneline", f"--max-count={max_count}"],
        )

    def _validate_ls_files_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git ls-files command and optional path.

        Example (valid): ["ls-files", "--", "src"].
        Example (invalid): ["ls-files", "src"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) not in {2, 3} or command[:2] != ["ls-files", "--"]:
            self._raise_invalid_command("ls_files")
        canonical_command = ["ls-files", "--"]
        if len(command) == 3:
            canonical_command.append(self.validate_path(command[2], "ls_files"))
        self._require_exact_command("ls_files", command, canonical_command)

    def _validate_stash_list_command(self, command: list[str]) -> None:
        """
        Validate the exact canonical Git stash-list command.

        Example (valid): ["stash", "list"].
        Example (invalid): ["stash"].
        Result: ValueError because the command structure is unsupported.
        """
        self._require_exact_command(
            "stash_list",
            command,
            ["stash", "list"],
        )

    def _validate_add_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git add command with one or more safe paths.

        Example (valid): ["add", "--", "README.md"].
        The standard ["add", "README.md"] form is normalized before this
        canonical validation step.
        """
        if len(command) < 3 or command[:2] != ["add", "--"]:
            self._raise_invalid_command("add")
        paths = self.validate_paths(command[2:], "add")
        self._require_exact_command("add", command, ["add", "--", *paths])

    def _validate_commit_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git commit command and commit message.

        Example (valid): ["commit", "--no-verify", "--no-gpg-sign", "-m", "Update docs"].
        Example (invalid): ["commit", "-m", "Update docs"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 5 or command[:4] != [
            "commit",
            "--no-verify",
            "--no-gpg-sign",
            "-m",
        ]:
            self._raise_invalid_command("commit")
        message = self.validate_message(command[4], "commit")
        self._require_exact_command(
            "commit",
            command,
            ["commit", "--no-verify", "--no-gpg-sign", "-m", message],
        )

    def _validate_branch_create_command(self, command: list[str]) -> None:
        """
        Validate the canonical command for creating a safe branch name.

        Example (valid): ["branch", "--no-track", "feature/docs"].
        Example (invalid): ["branch", "feature/docs"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["branch", "--no-track"]:
            self._raise_invalid_command("branch_create")
        name = self.validate_branch_name(command[2])
        self._require_exact_command(
            "branch_create",
            command,
            ["branch", "--no-track", name],
        )

    def _validate_branch_rename_command(self, command: list[str]) -> None:
        """
        Validate the canonical command for renaming safe branch names.

        Example (valid): ["branch", "-m", "old-name", "new-name"].
        Example (invalid): ["branch", "-m", "new-name"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 4 or command[:2] != ["branch", "-m"]:
            self._raise_invalid_command("branch_rename")
        old_name = self.validate_branch_name(command[2])
        new_name = self.validate_branch_name(command[3])
        self._require_exact_command(
            "branch_rename",
            command,
            ["branch", "-m", old_name, new_name],
        )

    def _validate_branch_delete_command(self, command: list[str]) -> None:
        """
        Validate the canonical command for deleting a safe branch name.

        Example (valid): ["branch", "-d", "feature/docs"].
        Example (invalid): ["branch", "-D", "feature/docs"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["branch", "-d"]:
            self._raise_invalid_command("branch_delete")
        name = self.validate_branch_name(command[2])
        self._require_exact_command(
            "branch_delete",
            command,
            ["branch", "-d", name],
        )

    def _validate_switch_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git switch command and safe branch name.

        Example (valid): ["switch", "--no-guess", "main"].
        Example (invalid): ["switch", "main"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["switch", "--no-guess"]:
            self._raise_invalid_command("switch")
        branch = self.validate_branch_name(command[2])
        self._require_exact_command(
            "switch",
            command,
            ["switch", "--no-guess", branch],
        )

    def _validate_merge_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git merge command and safe branch name.

        Example (valid): ["merge", "--no-edit", "--no-gpg-sign", "feature/docs"].
        Example (invalid): ["merge", "feature/docs"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 4 or command[:3] != [
            "merge",
            "--no-edit",
            "--no-gpg-sign",
        ]:
            self._raise_invalid_command("merge")
        branch = self.validate_branch_name(command[3])
        self._require_exact_command(
            "merge",
            command,
            ["merge", "--no-edit", "--no-gpg-sign", branch],
        )

    def _validate_cherry_pick_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git cherry-pick command and safe revision.

        Example (valid): ["cherry-pick", "--no-gpg-sign", "abc123"].
        Example (invalid): ["cherry-pick", "abc123"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["cherry-pick", "--no-gpg-sign"]:
            self._raise_invalid_command("cherry_pick")
        revision = self.validate_revision(command[2])
        self._require_exact_command(
            "cherry_pick",
            command,
            ["cherry-pick", "--no-gpg-sign", revision],
        )

    def _validate_restore_command(self, command: list[str]) -> None:
        """
        Validate the canonical staged Git restore command and safe paths.

        Example (valid): ["restore", "--staged", "--", "README.md"].
        Example (invalid): ["restore", "README.md"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) < 4 or command[:3] != ["restore", "--staged", "--"]:
            self._raise_invalid_command("restore")
        paths = self.validate_paths(command[3:], "restore")
        self._require_exact_command(
            "restore",
            command,
            ["restore", "--staged", "--", *paths],
        )

    def _validate_reset_command(self, command: list[str]) -> None:
        """
        Validate a safe Git reset command with allowed mode and revision.

        Example (valid): ["reset", "--soft", "HEAD~1"].
        Example (invalid): ["reset", "--hard", "HEAD"].
        Result: ValueError because the mode or command structure is unsupported.
        """
        if len(command) != 3 or not command[1].startswith("--"):
            self._raise_invalid_command("reset")
        mode = self.validate_reset_mode(command[1][2:])
        revision = self.validate_revision(command[2])
        self._require_exact_command(
            "reset",
            command,
            ["reset", f"--{mode}", revision],
        )

    def _validate_stash_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git stash-push command and optional safe values.

        Example (valid): ["stash", "push", "--message", "Work", "--"].
        Example (invalid): ["stash", "push"].
        Result: ValueError because the command structure is unsupported.
        """
        if command[:2] != ["stash", "push"]:
            self._raise_invalid_command("stash")

        index = 2
        canonical_command = ["stash", "push"]
        if index < len(command) and command[index] == "--include-untracked":
            canonical_command.append("--include-untracked")
            index += 1
        if index < len(command) and command[index] == "--message":
            if index + 1 >= len(command):
                self._raise_invalid_command("stash")
            message = self.validate_message(command[index + 1], "stash")
            canonical_command.extend(["--message", message])
            index += 2
        if command[index:] != ["--"]:
            self._raise_invalid_command("stash")
        canonical_command.append("--")
        self._require_exact_command("stash", command, canonical_command)

    def _validate_stash_pop_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git stash-pop command and bounded stash index.

        Example (valid): ["stash", "pop", "stash@{0}"].
        Example (invalid): ["stash", "pop", "0"].
        Result: ValueError because the stash reference is unsupported.
        """
        if len(command) != 3 or command[:2] != ["stash", "pop"]:
            self._raise_invalid_command("stash_pop")
        match = re.fullmatch(r"stash@\{([0-9]+)\}", command[2])
        if match is None:
            self._raise_invalid_command("stash_pop")
        index = self.validate_stash_index(int(match.group(1)))
        self._require_exact_command(
            "stash_pop",
            command,
            ["stash", "pop", f"stash@{{{index}}}"],
        )

    def _validate_tag_create_command(self, command: list[str]) -> None:
        """
        Validate the canonical command for creating a safe Git tag.

        Example (valid): ["tag", "v1.0.0", "HEAD"].
        Example (invalid): ["tag", "v1.0.0"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[0] != "tag":
            self._raise_invalid_command("tag_create")
        name = self.validate_tag_name(command[1])
        revision = self.validate_revision(command[2])
        self._require_exact_command(
            "tag_create",
            command,
            ["tag", name, revision],
        )

    def _validate_tag_delete_command(self, command: list[str]) -> None:
        """
        Validate the canonical command for deleting a safe Git tag.

        Example (valid): ["tag", "-d", "v1.0.0"].
        Example (invalid): ["tag", "--delete", "v1.0.0"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["tag", "-d"]:
            self._raise_invalid_command("tag_delete")
        name = self.validate_tag_name(command[2])
        self._require_exact_command(
            "tag_delete",
            command,
            ["tag", "-d", name],
        )

    def _validate_fetch_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git fetch command and known remote name.

        Example (valid): ["fetch", "--no-tags", "origin"].
        Example (invalid): ["fetch", "origin"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 3 or command[:2] != ["fetch", "--no-tags"]:
            self._raise_invalid_command("fetch")
        remote = self.validate_remote_name(command[2])
        self._require_exact_command(
            "fetch",
            command,
            ["fetch", "--no-tags", remote],
        )

    def _validate_pull_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git pull command, remote, and branch.

        Example (valid): ["pull", "--ff-only", "--no-rebase", "origin", "main"].
        Example (invalid): ["pull", "origin", "main"].
        Result: ValueError because the command structure is unsupported.
        """
        if len(command) != 5 or command[:3] != [
            "pull",
            "--ff-only",
            "--no-rebase",
        ]:
            self._raise_invalid_command("pull")
        remote = self.validate_remote_name(command[3])
        branch = self.validate_branch_name(command[4])
        self._require_exact_command(
            "pull",
            command,
            ["pull", "--ff-only", "--no-rebase", remote, branch],
        )

    def _validate_push_command(self, command: list[str]) -> None:
        """
        Validate the canonical Git push command and matching branch refspec.

        Example (valid): ["push", "--porcelain", "--no-verify", "origin", "refs/heads/main:refs/heads/main"].
        Example (invalid): a refspec with different source and destination branches.
        Result: ValueError because the refspec or command structure is unsupported.
        """
        if len(command) != 5 or command[:3] != [
            "push",
            "--porcelain",
            "--no-verify",
        ]:
            self._raise_invalid_command("push")
        remote = self.validate_remote_name(command[3])
        refspec = command[4]
        prefix = "refs/heads/"
        source, separator, destination = refspec.partition(":")
        if (
            not separator
            or not source.startswith(prefix)
            or not destination.startswith(prefix)
        ):
            self._raise_invalid_command("push")
        branch = self.validate_branch_name(source.removeprefix(prefix))
        expected_refspec = f"{prefix}{branch}:{prefix}{branch}"
        if refspec != expected_refspec:
            self._raise_invalid_command("push")
        self._require_exact_command(
            "push",
            command,
            ["push", "--porcelain", "--no-verify", remote, expected_refspec],
        )

    def require_arguments(
        self,
        arguments: dict[str, Any],
        operation: str,
    ) -> None:
        """
        Validate an operation's allowed and required argument names.

        Example (valid): all required arguments with no unsupported keys.
        Example (invalid): an argument named "unknown".
        Result: ValueError because the argument is unexpected or required data is missing.
        """
        operation_definition = GIT_OPERATION_DEFINITIONS[operation]
        allowed = operation_definition["allowed_arguments"]
        required = operation_definition["required_arguments"]

        unexpected = set(arguments) - allowed
        if unexpected:
            names = ", ".join(sorted(unexpected))
            raise ValueError(f"git {operation} received unexpected args: {names}")

        missing = required - set(arguments)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"git {operation} is missing required args: {names}")

    def validate_path(self, value: Any, operation: str) -> str:
        """
        Validate and normalize a path contained within the project repository.

        Example (valid): "src/main.py" -> "src/main.py".
        Example (invalid): "../outside.txt".
        Result: ValueError because the path escapes the repository.
        """
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

    def validate_file_path(self, value: Any, operation: str) -> str:
        """
        Validate a repository path that identifies a file rather than its root.

        Example (valid): "README.md".
        Example (invalid): ".".
        Result: ValueError because the repository root is not a file path.
        """
        path = self.validate_path(value, operation)
        if path == ".":
            raise ValueError(f"git {operation} args.path must identify a file.")
        return path

    def validate_paths(self, value: Any, operation: str) -> list[str]:
        """
        Validate a non-empty bounded list of repository paths.

        Example (valid): ["README.md", "src/main.py"].
        Example (invalid): [].
        Result: ValueError because at least one path is required.
        """
        if not isinstance(value, list) or not value:
            raise ValueError(f"git {operation} args.paths must be a non-empty array.")
        if len(value) > MAX_PATHS:
            raise ValueError(
                f"git {operation} accepts at most {MAX_PATHS} paths at a time."
            )
        return [self.validate_path(path, operation) for path in value]

    def validate_max_count(self, value: Any, operation: str) -> int:
        """
        Validate an integer result count within the configured bounds.

        Example (valid): 10.
        Example (invalid): 0.
        Result: ValueError because the count is outside the allowed range.
        """
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"git {operation} args.max_count must be an integer.")
        if not 1 <= value <= MAX_COUNT:
            raise ValueError(
                f"git {operation} args.max_count must be between 1 and {MAX_COUNT}."
            )
        return value

    def validate_revision(self, value: Any) -> str:
        """
        Validate a non-empty Git revision matching the safe revision pattern.

        Example (valid): "HEAD~1".
        Example (invalid): "--help".
        Result: ValueError because the revision is unsafe.
        """
        if not isinstance(value, str) or not re.fullmatch(
            SAFE_REVISION_PATTERN,
            value,
        ):
            raise ValueError("Git revision must be a non-empty safe revision.")
        return value

    def validate_branch_name(self, value: Any) -> str:
        """
        Validate a non-empty branch name accepted by Git's ref checker.

        Example (valid): "feature/docs".
        Example (invalid): "-dangerous".
        Result: ValueError because the branch name is unsafe or invalid.
        """
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git branch name must be a non-empty safe string.")

        try:
            self._service.run(
                ["check-ref-format", "--branch", value],
                failure_prefix="Invalid Git branch name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error
        return value

    def validate_tag_name(self, value: Any) -> str:
        """
        Validate a non-empty tag name accepted by Git's ref checker.

        Example (valid): "v1.0.0".
        Example (invalid): "-dangerous".
        Result: ValueError because the tag name is unsafe or invalid.
        """
        if not isinstance(value, str) or not value.strip() or value.startswith("-"):
            raise ValueError("Git tag name must be a non-empty safe string.")

        try:
            self._service.run(
                ["check-ref-format", f"refs/tags/{value}"],
                failure_prefix="Invalid Git tag name",
            )
        except RuntimeError as error:
            raise ValueError(str(error)) from error
        return value

    def validate_remote_name(self, value: Any) -> str:
        """
        Validate a safe remote name that exists in the repository.

        Example (valid): "origin" when that remote exists.
        Example (invalid): "unknown" when no such remote exists.
        Result: ValueError because the remote name is unsafe or unknown.
        """
        if not isinstance(value, str) or not re.fullmatch(
            SAFE_REMOTE_NAME_PATTERN,
            value,
        ):
            raise ValueError("Git remote name must be a non-empty safe string.")

        remote_names = self._service.run(["remote"]).splitlines()
        if value not in remote_names:
            raise ValueError(f"Unknown Git remote: {value}")
        return value

    def validate_diff_staged(self, value: Any) -> bool:
        """
        Validate that the Git diff staged flag is boolean.

        Example (valid): True.
        Example (invalid): "true".
        Result: ValueError because the flag is not boolean.
        """
        if not isinstance(value, bool):
            raise ValueError("git diff args.staged must be a boolean.")
        return value

    def validate_stash_include_untracked(self, value: Any) -> bool:
        """
        Validate that the stash include-untracked flag is boolean.

        Example (valid): False.
        Example (invalid): 1.
        Result: ValueError because the flag is not boolean.
        """
        if not isinstance(value, bool):
            raise ValueError("git stash args.include_untracked must be a boolean.")
        return value

    def validate_message(self, value: Any, operation: str) -> str:
        """
        Validate a non-empty Git message within the configured length limit.

        Example (valid): "Update documentation".
        Example (invalid): "   ".
        Result: ValueError because the message is empty or too long.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"git {operation} args.message must be a non-empty string."
            )
        if len(value) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"git {operation} args.message must not exceed "
                f"{MAX_MESSAGE_LENGTH} characters."
            )
        return value

    def validate_restore_staged(self, value: Any) -> None:
        """
        Validate that restore uses only the safe staged=true variant.

        Example (valid): True.
        Example (invalid): False.
        Result: ValueError because unstaged restore is unsupported.
        """
        if value is not True:
            raise ValueError("git restore only supports the safe staged=true variant.")

    def validate_reset_mode(self, value: Any) -> str:
        """
        Validate that reset mode is limited to soft or mixed.

        Example (valid): "soft".
        Example (invalid): "hard".
        Result: ValueError because the reset mode is unsafe.
        """
        if value not in RESET_MODE_VALUES:
            raise ValueError("git reset args.mode must be 'soft' or 'mixed'.")
        return value

    def validate_stash_index(self, value: Any) -> int:
        """
        Validate an integer stash index within the configured bounds.

        Example (valid): 0.
        Example (invalid): -1.
        Result: ValueError because the stash index is outside the allowed range.
        """
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= MAX_STASH_INDEX
        ):
            raise ValueError(
                "git stash_pop args.index must be between 0 and "
                f"{MAX_STASH_INDEX}."
            )
        return value

    def _validate_count_option(self, token: str, operation: str) -> int:
        """
        Validate and parse a canonical --max-count option token.

        Example (valid): "--max-count=10" -> 10.
        Example (invalid): "--max-count=all".
        Result: ValueError because the option is malformed or out of range.
        """
        prefix = "--max-count="
        if not token.startswith(prefix) or not token.removeprefix(prefix).isdigit():
            self._raise_invalid_command(operation)
        value = int(token.removeprefix(prefix))
        return self.validate_max_count(value, operation)

    @staticmethod
    def _require_exact_command(
        operation: str,
        command: list[str],
        expected: list[str],
    ) -> None:
        """
        Validate that a Git command exactly matches its canonical token list.

        Example (valid): command == expected.
        Example (invalid): command contains an extra token.
        Result: ValueError because the command structure differs.
        """
        if command != expected:
            raise ValueError(
                f"git {operation} command does not match the supported structure."
            )

    @staticmethod
    def _raise_invalid_command(operation: str) -> None:
        """
        Reject an unsupported Git command structure for an operation.

        Example (valid): canonical commands do not invoke this method.
        Example (invalid): an unsupported command reaches this method.
        Result: ValueError describing the required supported structure.
        """
        raise ValueError(
            f"git {operation} command does not match the supported structure."
        )

    def _ensure_project_repository(self) -> None:
        """
        Validate that the working directory is the root of a Git repository.

        Example (valid): a configured path equal to git rev-parse --show-toplevel.
        Example (invalid): a missing directory or nested repository path.
        Result: ValueError, or the service's repository error when Git lookup fails.
        """
        if not self._working_directory.is_dir():
            raise ValueError(
                f"Git working directory does not exist: {self._working_directory}"
            )

        repository_root = self._service.run(
            ["rev-parse", "--show-toplevel"],
            failure_prefix="Not a Git repository",
        )
        if Path(repository_root).resolve() != self._working_directory:
            raise ValueError(
                "Git operations require the configured working directory to be "
                "the repository root."
            )
