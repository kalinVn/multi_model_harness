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
    """Валидира разрешенията на Git инструмента и пълните аргументи на командата."""

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
        Валидира аргументите от най-горно ниво на Git и контекста на хранилището.

        Пример (валиден): {"command_name": "status", "command": ["status", "--short", "--branch", "--untracked-files=all"]}.
        Пример (невалиден): {"command_name": "status"}.
        Резултат: ValueError, защото липсва задължителен аргумент.
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
        Валидира токените, разрешението и структурата на поддържана Git команда.

        Пример (валиден): command_name="status" с каноничните status токени.
        Пример (невалиден): command_name="unknown".
        Резултат: ValueError или PermissionError, когато операцията е забранена.
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

        self._validate_operation_permission(command_name)
        validator = getattr(self, f"_validate_{command_name}_command")
        validator(command)

    def _validate_operation_permission(self, command_name: str) -> None:
        """
        Валидира, че заявената Git операция е разрешена.

        Пример (валиден): "status", когато операциите за четене са разрешени.
        Пример (невалиден): "commit", когато операциите за запис са забранени.
        Резултат: PermissionError, защото операцията не е разрешена.
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
        Валидира точната канонична Git status команда.

        Пример (валиден): ["status", "--short", "--branch", "--untracked-files=all"].
        Пример (невалиден): ["status"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        self._require_exact_command(
            "status",
            command,
            ["status", "--short", "--branch", "--untracked-files=all"],
        )

    def _validate_diff_command(self, command: list[str]) -> None:
        """
        Валидира безопасната канонична Git diff команда и незадължителния път.

        Пример (валиден): ["diff", "--no-ext-diff", "--no-textconv", "--no-color", "--"].
        Пример (невалиден): ["diff", "README.md"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git log команда и ограничения максимален брой.

        Пример (валиден): ["log", "--oneline", "--no-decorate", "--max-count=10"].
        Пример (невалиден): ["log", "--oneline"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира точната канонична Git команда за изброяване на клонове.

        Пример (валиден): ["branch", "--list", "--no-color"].
        Пример (невалиден): ["branch", "--all"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        self._require_exact_command(
            "branch_list",
            command,
            ["branch", "--list", "--no-color"],
        )

    def _validate_show_command(self, command: list[str]) -> None:
        """
        Валидира безопасна Git show команда за ревизия или път в ревизия.

        Пример (валиден): ["show", "--no-ext-diff", "--no-textconv", "--no-color", "HEAD:README.md"].
        Пример (невалиден): ["show", "HEAD"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира точната канонична Git команда за изброяване на tag-ове.

        Пример (валиден): ["tag", "--list", "--sort=refname"].
        Пример (невалиден): ["tag", "--list"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        self._require_exact_command(
            "tag_list",
            command,
            ["tag", "--list", "--sort=refname"],
        )

    def _validate_remote_list_command(self, command: list[str]) -> None:
        """
        Валидира точната канонична Git команда за изброяване на remote-и.

        Пример (валиден): ["remote"].
        Пример (невалиден): ["remote", "-v"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        self._require_exact_command("remote_list", command, ["remote"])

    def _validate_blame_command(self, command: list[str]) -> None:
        """
        Валидира канонична Git blame команда с безопасна ревизия и път до файл.

        Пример (валиден): ["blame", "--date=short", "HEAD", "--", "README.md"].
        Пример (невалиден): ["blame", "README.md"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git rev-parse команда за проверка на обект.

        Пример (валиден): ["rev-parse", "--verify", "--end-of-options", "HEAD^{object}"].
        Пример (невалиден): ["rev-parse", "HEAD"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git reflog команда и ограничения максимален брой.

        Пример (валиден): ["reflog", "--oneline", "--max-count=10"].
        Пример (невалиден): ["reflog", "--oneline"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git ls-files команда и незадължителния път.

        Пример (валиден): ["ls-files", "--", "src"].
        Пример (невалиден): ["ls-files", "src"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        if len(command) not in {2, 3} or command[:2] != ["ls-files", "--"]:
            self._raise_invalid_command("ls_files")
        canonical_command = ["ls-files", "--"]
        if len(command) == 3:
            canonical_command.append(self.validate_path(command[2], "ls_files"))
        self._require_exact_command("ls_files", command, canonical_command)

    def _validate_stash_list_command(self, command: list[str]) -> None:
        """
        Валидира точната канонична Git stash-list команда.

        Пример (валиден): ["stash", "list"].
        Пример (невалиден): ["stash"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        self._require_exact_command(
            "stash_list",
            command,
            ["stash", "list"],
        )

    def _validate_add_command(self, command: list[str]) -> None:
        """
        Валидира каноничната Git add команда с един или повече безопасни пътища.

        Пример (валиден): ["add", "--", "README.md"].
        Пример (невалиден): ["add", "README.md"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
        """
        if len(command) < 3 or command[:2] != ["add", "--"]:
            self._raise_invalid_command("add")
        paths = self.validate_paths(command[2:], "add")
        self._require_exact_command("add", command, ["add", "--", *paths])

    def _validate_commit_command(self, command: list[str]) -> None:
        """
        Валидира каноничната Git commit команда и commit съобщението.

        Пример (валиден): ["commit", "--no-verify", "--no-gpg-sign", "-m", "Актуализиране на документацията"].
        Пример (невалиден): ["commit", "-m", "Актуализиране на документацията"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната команда за създаване на безопасно име на клон.

        Пример (валиден): ["branch", "--no-track", "feature/docs"].
        Пример (невалиден): ["branch", "feature/docs"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната команда за преименуване на безопасни имена на клонове.

        Пример (валиден): ["branch", "-m", "old-name", "new-name"].
        Пример (невалиден): ["branch", "-m", "new-name"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната команда за изтриване на безопасно име на клон.

        Пример (валиден): ["branch", "-d", "feature/docs"].
        Пример (невалиден): ["branch", "-D", "feature/docs"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git switch команда и безопасното име на клон.

        Пример (валиден): ["switch", "--no-guess", "main"].
        Пример (невалиден): ["switch", "main"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git merge команда и безопасното име на клон.

        Пример (валиден): ["merge", "--no-edit", "--no-gpg-sign", "feature/docs"].
        Пример (невалиден): ["merge", "feature/docs"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git cherry-pick команда и безопасната ревизия.

        Пример (валиден): ["cherry-pick", "--no-gpg-sign", "abc123"].
        Пример (невалиден): ["cherry-pick", "abc123"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната staged Git restore команда и безопасните пътища.

        Пример (валиден): ["restore", "--staged", "--", "README.md"].
        Пример (невалиден): ["restore", "README.md"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира безопасна Git reset команда с разрешени режим и ревизия.

        Пример (валиден): ["reset", "--soft", "HEAD~1"].
        Пример (невалиден): ["reset", "--hard", "HEAD"].
        Резултат: ValueError, защото режимът или структурата на командата не се поддържа.
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
        Валидира каноничната Git stash-push команда и незадължителните безопасни стойности.

        Пример (валиден): ["stash", "push", "--message", "Работа", "--"].
        Пример (невалиден): ["stash", "push"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git stash-pop команда и ограничения stash индекс.

        Пример (валиден): ["stash", "pop", "stash@{0}"].
        Пример (невалиден): ["stash", "pop", "0"].
        Резултат: ValueError, защото референцията към stash не се поддържа.
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
        Валидира каноничната команда за създаване на безопасен Git tag.

        Пример (валиден): ["tag", "v1.0.0", "HEAD"].
        Пример (невалиден): ["tag", "v1.0.0"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната команда за изтриване на безопасен Git tag.

        Пример (валиден): ["tag", "-d", "v1.0.0"].
        Пример (невалиден): ["tag", "--delete", "v1.0.0"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git fetch команда и познатото име на remote.

        Пример (валиден): ["fetch", "--no-tags", "origin"].
        Пример (невалиден): ["fetch", "origin"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git pull команда, remote и клон.

        Пример (валиден): ["pull", "--ff-only", "--no-rebase", "origin", "main"].
        Пример (невалиден): ["pull", "origin", "main"].
        Резултат: ValueError, защото структурата на командата не се поддържа.
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
        Валидира каноничната Git push команда и съответстващия refspec на клона.

        Пример (валиден): ["push", "--porcelain", "--no-verify", "origin", "refs/heads/main:refs/heads/main"].
        Пример (невалиден): refspec с различни изходен и целеви клон.
        Резултат: ValueError, защото refspec или структурата на командата не се поддържа.
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
        Валидира разрешените и задължителните имена на аргументи за операция.

        Пример (валиден): всички задължителни аргументи без неподдържани ключове.
        Пример (невалиден): аргумент с име "unknown".
        Резултат: ValueError, защото аргументът е неочакван или липсват задължителни данни.
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
        Валидира и нормализира път, който остава в хранилището на проекта.

        Пример (валиден): "src/main.py" -> "src/main.py".
        Пример (невалиден): "../outside.txt".
        Резултат: ValueError, защото пътят излиза извън хранилището.
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
        Валидира път в хранилището, който сочи файл, а не неговия корен.

        Пример (валиден): "README.md".
        Пример (невалиден): ".".
        Резултат: ValueError, защото коренът на хранилището не е път до файл.
        """
        path = self.validate_path(value, operation)
        if path == ".":
            raise ValueError(f"git {operation} args.path must identify a file.")
        return path

    def validate_paths(self, value: Any, operation: str) -> list[str]:
        """
        Валидира непразен ограничен списък с пътища в хранилището.

        Пример (валиден): ["README.md", "src/main.py"].
        Пример (невалиден): [].
        Резултат: ValueError, защото се изисква поне един път.
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
        Валидира целочислен брой резултати в конфигурираните граници.

        Пример (валиден): 10.
        Пример (невалиден): 0.
        Резултат: ValueError, защото броят е извън разрешения диапазон.
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
        Валидира непразна Git ревизия, съответстваща на безопасния шаблон.

        Пример (валиден): "HEAD~1".
        Пример (невалиден): "--help".
        Резултат: ValueError, защото ревизията е опасна.
        """
        if not isinstance(value, str) or not re.fullmatch(
            SAFE_REVISION_PATTERN,
            value,
        ):
            raise ValueError("Git revision must be a non-empty safe revision.")
        return value

    def validate_branch_name(self, value: Any) -> str:
        """
        Валидира непразно име на клон, приемано от Git проверката за ref.

        Пример (валиден): "feature/docs".
        Пример (невалиден): "-dangerous".
        Резултат: ValueError, защото името на клона е опасно или невалидно.
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
        Валидира непразно име на tag, приемано от Git проверката за ref.

        Пример (валиден): "v1.0.0".
        Пример (невалиден): "-dangerous".
        Резултат: ValueError, защото името на tag е опасно или невалидно.
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
        Валидира безопасно име на remote, което съществува в хранилището.

        Пример (валиден): "origin", когато този remote съществува.
        Пример (невалиден): "unknown", когато такъв remote не съществува.
        Резултат: ValueError, защото името на remote е опасно или неизвестно.
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
        Валидира, че staged флагът на Git diff е булев.

        Пример (валиден): True.
        Пример (невалиден): "true".
        Резултат: ValueError, защото флагът не е булев.
        """
        if not isinstance(value, bool):
            raise ValueError("git diff args.staged must be a boolean.")
        return value

    def validate_stash_include_untracked(self, value: Any) -> bool:
        """
        Валидира, че флагът include-untracked на stash е булев.

        Пример (валиден): False.
        Пример (невалиден): 1.
        Резултат: ValueError, защото флагът не е булев.
        """
        if not isinstance(value, bool):
            raise ValueError("git stash args.include_untracked must be a boolean.")
        return value

    def validate_message(self, value: Any, operation: str) -> str:
        """
        Валидира непразно Git съобщение в конфигурираното ограничение за дължина.

        Пример (валиден): "Актуализиране на документацията".
        Пример (невалиден): "   ".
        Резултат: ValueError, защото съобщението е празно или твърде дълго.
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
        Валидира, че restore използва само безопасния вариант staged=true.

        Пример (валиден): True.
        Пример (невалиден): False.
        Резултат: ValueError, защото restore без staged не се поддържа.
        """
        if value is not True:
            raise ValueError("git restore only supports the safe staged=true variant.")

    def validate_reset_mode(self, value: Any) -> str:
        """
        Валидира, че режимът за reset е ограничен до soft или mixed.

        Пример (валиден): "soft".
        Пример (невалиден): "hard".
        Резултат: ValueError, защото режимът за reset е опасен.
        """
        if value not in RESET_MODE_VALUES:
            raise ValueError("git reset args.mode must be 'soft' or 'mixed'.")
        return value

    def validate_stash_index(self, value: Any) -> int:
        """
        Валидира целочислен stash индекс в конфигурираните граници.

        Пример (валиден): 0.
        Пример (невалиден): -1.
        Резултат: ValueError, защото индексът на stash е извън разрешения диапазон.
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
        Валидира и разборира каноничен токен на опцията --max-count.

        Пример (валиден): "--max-count=10" -> 10.
        Пример (невалиден): "--max-count=all".
        Резултат: ValueError, защото опцията е неправилно форматирана или извън диапазона.
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
        Валидира, че Git командата съвпада точно с каноничния си списък от токени.

        Пример (валиден): command == expected.
        Пример (невалиден): командата съдържа допълнителен токен.
        Резултат: ValueError, защото структурата на командата се различава.
        """
        if command != expected:
            raise ValueError(
                f"git {operation} command does not match the supported structure."
            )

    @staticmethod
    def _raise_invalid_command(operation: str) -> None:
        """
        Отхвърля неподдържана структура на Git команда за операция.

        Пример (валиден): каноничните команди не извикват този метод.
        Пример (невалиден): неподдържана команда достига до този метод.
        Резултат: ValueError, описващ изискваната поддържана структура.
        """
        raise ValueError(
            f"git {operation} command does not match the supported structure."
        )

    def _ensure_project_repository(self) -> None:
        """
        Валидира, че работната директория е коренът на Git хранилище.

        Пример (валиден): конфигуриран път, равен на git rev-parse --show-toplevel.
        Пример (невалиден): липсваща директория или вложен път в хранилището.
        Резултат: ValueError или грешката на услугата за хранилището при неуспешна Git проверка.
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
