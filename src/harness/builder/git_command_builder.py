from typing import Any

from harness.config.git_tool_config import (
    DEFAULT_MAX_COUNT,
    DEFAULT_REVISION,
    DEFAULT_STASH_INDEX,
)
from harness.validators.git_tool_validator import GitToolValidator


class GitCommandBuilder:
    """Build validated argument lists for supported Git operations."""

    def __init__(self, validator: GitToolValidator) -> None:
        self._validator = validator

    def build(
        self,
        operation: str,
        arguments: dict[str, Any],
    ) -> list[str]:
        self._validator.require_arguments(arguments, "status")
        return getattr(self, f"_build_{operation}_command")(arguments)

    def _build_status_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "status")
        return ["status", "--short", "--branch", "--untracked-files=all"]

    def _build_diff_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "diff")
        staged = self._validator.validate_diff_staged(
            arguments.get("staged", False)
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
        self._validator.require_arguments(arguments, "log")
        max_count = self._validator.validate_max_count(
            arguments.get("max_count", DEFAULT_MAX_COUNT),
            "log",
        )
        return ["log", "--oneline", "--no-decorate", f"--max-count={max_count}"]

    def _build_branch_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "branch_list")
        return ["branch", "--list", "--no-color"]

    def _build_show_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "show")
        revision = self._validator.validate_revision(
            arguments.get("revision", DEFAULT_REVISION)
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
        self._validator.require_arguments(arguments, "tag_list")
        return ["tag", "--list", "--sort=refname"]

    def _build_remote_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "remote_list")
        return ["remote"]

    def _build_blame_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "blame")
        revision = self._validator.validate_revision(
            arguments.get("revision", DEFAULT_REVISION)
        )
        path = self._validator.validate_file_path(arguments["path"], "blame")
        return ["blame", "--date=short", revision, "--", path]

    def _build_rev_parse_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "rev_parse")
        revision = self._validator.validate_revision(
            arguments.get("revision", DEFAULT_REVISION)
        )
        return ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{object}}"]

    def _build_reflog_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "reflog")
        max_count = self._validator.validate_max_count(
            arguments.get("max_count", DEFAULT_MAX_COUNT),
            "reflog",
        )
        return ["reflog", "--oneline", f"--max-count={max_count}"]

    def _build_ls_files_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "ls_files")
        command = ["ls-files", "--"]
        path = arguments.get("path")
        if path is not None:
            command.append(self._validator.validate_path(path, "ls_files"))
        return command

    def _build_stash_list_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "stash_list")
        return ["stash", "list"]

    def _build_add_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "add")
        paths = self._validator.validate_paths(arguments["paths"], "add")
        return ["add", "--", *paths]

    def _build_commit_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "commit")
        message = self._validator.validate_message(arguments["message"], "commit")
        return ["commit", "--no-verify", "--no-gpg-sign", "-m", message]

    def _build_branch_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "branch_create")
        branch_name = self._validator.validate_branch_name(arguments["name"])
        return ["branch", "--no-track", branch_name]

    def _build_branch_rename_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "branch_rename")
        old_name = self._validator.validate_branch_name(arguments["old_name"])
        new_name = self._validator.validate_branch_name(arguments["new_name"])
        return ["branch", "-m", old_name, new_name]

    def _build_branch_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "branch_delete")
        branch_name = self._validator.validate_branch_name(arguments["name"])
        return ["branch", "-d", branch_name]

    def _build_switch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "switch")
        branch_name = self._validator.validate_branch_name(arguments["branch"])
        return ["switch", "--no-guess", branch_name]

    def _build_merge_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "merge")
        branch_name = self._validator.validate_branch_name(arguments["branch"])
        return ["merge", "--no-edit", "--no-gpg-sign", branch_name]

    def _build_cherry_pick_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "cherry_pick")
        revision = self._validator.validate_revision(arguments["revision"])
        return ["cherry-pick", "--no-gpg-sign", revision]

    def _build_restore_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "restore")
        self._validator.validate_restore_staged(arguments["staged"])
        paths = self._validator.validate_paths(arguments["paths"], "restore")
        return ["restore", "--staged", "--", *paths]

    def _build_reset_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "reset")
        mode = self._validator.validate_reset_mode(arguments["mode"])
        revision = self._validator.validate_revision(
            arguments.get("revision", DEFAULT_REVISION)
        )
        return ["reset", f"--{mode}", revision]

    def _build_stash_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "stash")
        include_untracked = self._validator.validate_stash_include_untracked(
            arguments.get("include_untracked", False)
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
        self._validator.require_arguments(arguments, "stash_pop")
        index = self._validator.validate_stash_index(
            arguments.get("index", DEFAULT_STASH_INDEX)
        )
        return ["stash", "pop", f"stash@{{{index}}}"]

    def _build_tag_create_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "tag_create")
        tag_name = self._validator.validate_tag_name(arguments["name"])
        revision = self._validator.validate_revision(
            arguments.get("revision", DEFAULT_REVISION)
        )
        return ["tag", tag_name, revision]

    def _build_tag_delete_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "tag_delete")
        return [
            "tag",
            "-d",
            self._validator.validate_tag_name(arguments["name"]),
        ]

    def _build_fetch_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "fetch")
        return [
            "fetch",
            "--no-tags",
            self._validator.validate_remote_name(arguments["remote"]),
        ]

    def _build_pull_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "pull")
        remote = self._validator.validate_remote_name(arguments["remote"])
        branch = self._validator.validate_branch_name(arguments["branch"])
        return ["pull", "--ff-only", "--no-rebase", remote, branch]

    def _build_push_command(self, arguments: dict[str, Any]) -> list[str]:
        self._validator.require_arguments(arguments, "push")
        remote = self._validator.validate_remote_name(arguments["remote"])
        branch = self._validator.validate_branch_name(arguments["branch"])
        refspec = f"refs/heads/{branch}:refs/heads/{branch}"
        return ["push", "--porcelain", "--no-verify", remote, refspec]
