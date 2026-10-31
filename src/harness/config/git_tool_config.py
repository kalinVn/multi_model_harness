from typing import Any

from harness.config.sensitive_data_redaction_config import (
    CREDENTIAL_URL_PATTERN,
    SENSITIVE_ENVIRONMENT_MARKERS,
)


GIT_TOOL_NAME = "git"
GIT_TOOL_DESCRIPTION = (
    "Runs one or more allowlisted Git commands sequentially in the project "
    "repository. Provide each command as a shell-style string without the "
    "git executable. "
    "Read, local write, and remote operations are separately restricted. "
    "Destructive and force variants are unavailable. All commands are "
    "validated before execution; runtime failures do not stop later commands."
)

GIT_WRITE_OPERATIONS_ENVIRONMENT_VARIABLE = (
    "HARNESS_ENABLE_GIT_WRITE_OPERATIONS"
)
GIT_REMOTE_OPERATIONS_ENVIRONMENT_VARIABLE = (
    "HARNESS_ENABLE_GIT_REMOTE_OPERATIONS"
)
DEFAULT_ALLOW_WRITE_OPERATIONS = False
DEFAULT_ALLOW_REMOTE_OPERATIONS = False
DEFAULT_TIMEOUT_SECONDS = 30
GIT_COMMAND_FAILURE_PREFIX = "Git command failed"

GIT_COMMAND_PREFIX = ("git", "-c", "core.hooksPath=/dev/null")
GIT_ALLOWED_ENVIRONMENT_VARIABLES = frozenset(
    {
        "HOME",
        "LANG",
        "LANGUAGE",
        "LC_ALL",
        "LC_CTYPE",
        "LOGNAME",
        "PATH",
        "SSH_AUTH_SOCK",
        "TEMP",
        "TMP",
        "TMPDIR",
        "USER",
        "XDG_CONFIG_HOME",
    }
)
GIT_ENVIRONMENT_OVERRIDES = {
    "GIT_PAGER": "cat",
    "GIT_TERMINAL_PROMPT": "0",
    "LC_ALL": "C",
}
SAFE_REVISION_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._/@{}~^+\-]*"
SAFE_REMOTE_NAME_PATTERN = r"[A-Za-z0-9][A-Za-z0-9._/\-]*"

READ_OPERATION_TYPE = "read"
WRITE_OPERATION_TYPE = "write"
REMOTE_OPERATION_TYPE = "remote"

GIT_OPERATION_DEFINITIONS: dict[str, dict[str, Any]] = {
    "status": {
        "type": READ_OPERATION_TYPE,
        "description": "Show branch and working-tree status.",
        "allowed_arguments": frozenset(),
        "required_arguments": frozenset(),
    },
    "diff": {
        "type": READ_OPERATION_TYPE,
        "description": "Show worktree or staged changes, optionally for one path.",
        "allowed_arguments": frozenset({"staged", "path"}),
        "required_arguments": frozenset(),
    },
    "log": {
        "type": READ_OPERATION_TYPE,
        "description": "Show recent commits with a bounded result count.",
        "allowed_arguments": frozenset({"max_count"}),
        "required_arguments": frozenset(),
    },
    "branch_list": {
        "type": READ_OPERATION_TYPE,
        "description": "List local branches.",
        "allowed_arguments": frozenset(),
        "required_arguments": frozenset(),
    },
    "show": {
        "type": READ_OPERATION_TYPE,
        "description": "Show a revision or a file at a revision.",
        "allowed_arguments": frozenset({"revision", "path"}),
        "required_arguments": frozenset(),
    },
    "tag_list": {
        "type": READ_OPERATION_TYPE,
        "description": "List local tags.",
        "allowed_arguments": frozenset(),
        "required_arguments": frozenset(),
    },
    "remote_list": {
        "type": READ_OPERATION_TYPE,
        "description": "List configured remote names without URLs.",
        "allowed_arguments": frozenset(),
        "required_arguments": frozenset(),
    },
    "blame": {
        "type": READ_OPERATION_TYPE,
        "description": "Show line history for a repository file.",
        "allowed_arguments": frozenset({"path", "revision"}),
        "required_arguments": frozenset({"path"}),
    },
    "rev_parse": {
        "type": READ_OPERATION_TYPE,
        "description": "Resolve and verify a revision.",
        "allowed_arguments": frozenset({"revision"}),
        "required_arguments": frozenset(),
    },
    "reflog": {
        "type": READ_OPERATION_TYPE,
        "description": "Show recent reference-log entries with a bounded count.",
        "allowed_arguments": frozenset({"max_count"}),
        "required_arguments": frozenset(),
    },
    "ls_files": {
        "type": READ_OPERATION_TYPE,
        "description": "List tracked files, optionally under one path.",
        "allowed_arguments": frozenset({"path"}),
        "required_arguments": frozenset(),
    },
    "stash_list": {
        "type": READ_OPERATION_TYPE,
        "description": "List local stash entries.",
        "allowed_arguments": frozenset(),
        "required_arguments": frozenset(),
    },
    "add": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Stage selected repository paths.",
        "allowed_arguments": frozenset({"paths"}),
        "required_arguments": frozenset({"paths"}),
    },
    "commit": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Create a local commit with a message.",
        "allowed_arguments": frozenset({"message"}),
        "required_arguments": frozenset({"message"}),
    },
    "branch_create": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Create a local branch without tracking configuration.",
        "allowed_arguments": frozenset({"name"}),
        "required_arguments": frozenset({"name"}),
    },
    "branch_rename": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Rename a local branch.",
        "allowed_arguments": frozenset({"old_name", "new_name"}),
        "required_arguments": frozenset({"old_name", "new_name"}),
    },
    "branch_delete": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Safely delete a fully merged local branch.",
        "allowed_arguments": frozenset({"name"}),
        "required_arguments": frozenset({"name"}),
    },
    "switch": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Switch to an existing local branch.",
        "allowed_arguments": frozenset({"branch"}),
        "required_arguments": frozenset({"branch"}),
    },
    "merge": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Merge an existing branch into the current branch.",
        "allowed_arguments": frozenset({"branch"}),
        "required_arguments": frozenset({"branch"}),
    },
    "cherry_pick": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Apply one revision to the current branch.",
        "allowed_arguments": frozenset({"revision"}),
        "required_arguments": frozenset({"revision"}),
    },
    "restore": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Unstage selected paths without discarding worktree changes.",
        "allowed_arguments": frozenset({"paths", "staged"}),
        "required_arguments": frozenset({"paths", "staged"}),
    },
    "reset": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Perform a soft or mixed reset to a revision.",
        "allowed_arguments": frozenset({"mode", "revision"}),
        "required_arguments": frozenset({"mode"}),
    },
    "stash": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Stash local changes with optional untracked files and message.",
        "allowed_arguments": frozenset({"include_untracked", "message"}),
        "required_arguments": frozenset(),
    },
    "stash_pop": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Apply and remove a stash entry by index.",
        "allowed_arguments": frozenset({"index"}),
        "required_arguments": frozenset(),
    },
    "tag_create": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Create a local tag at a revision.",
        "allowed_arguments": frozenset({"name", "revision"}),
        "required_arguments": frozenset({"name"}),
    },
    "tag_delete": {
        "type": WRITE_OPERATION_TYPE,
        "description": "Delete a local tag.",
        "allowed_arguments": frozenset({"name"}),
        "required_arguments": frozenset({"name"}),
    },
    "fetch": {
        "type": REMOTE_OPERATION_TYPE,
        "description": "Fetch updates from a configured remote without tags.",
        "allowed_arguments": frozenset({"remote"}),
        "required_arguments": frozenset({"remote"}),
    },
    "pull": {
        "type": REMOTE_OPERATION_TYPE,
        "description": "Fast-forward the current branch from a remote branch.",
        "allowed_arguments": frozenset({"remote", "branch"}),
        "required_arguments": frozenset({"remote", "branch"}),
    },
    "push": {
        "type": REMOTE_OPERATION_TYPE,
        "description": "Push a branch to the same branch name without force.",
        "allowed_arguments": frozenset({"remote", "branch"}),
        "required_arguments": frozenset({"remote", "branch"}),
    },
}

READ_OPERATIONS = {
    operation
    for operation, definition in GIT_OPERATION_DEFINITIONS.items()
    if definition["type"] == READ_OPERATION_TYPE
}
WRITE_OPERATIONS = {
    operation
    for operation, definition in GIT_OPERATION_DEFINITIONS.items()
    if definition["type"] == WRITE_OPERATION_TYPE
}
REMOTE_OPERATIONS = {
    operation
    for operation, definition in GIT_OPERATION_DEFINITIONS.items()
    if definition["type"] == REMOTE_OPERATION_TYPE
}
SUPPORTED_OPERATIONS = set(GIT_OPERATION_DEFINITIONS)
TOP_LEVEL_ARGUMENTS = frozenset({"commands"})

DEFAULT_REVISION = "HEAD"
DEFAULT_MAX_COUNT = 20
MAX_COUNT = 100
MAX_PATHS = 100
MAX_MESSAGE_LENGTH = 1000
DEFAULT_STASH_INDEX = 0
MAX_STASH_INDEX = 1000
MAX_COMMAND_TOKENS = MAX_PATHS + 3
MAX_COMMANDS = 20
RESET_MODES = ("soft", "mixed")
RESET_MODE_VALUES = frozenset(RESET_MODES)

GIT_ARGUMENT_PROPERTIES: dict[str, dict[str, Any]] = {
    "branch": {"type": "string"},
    "include_untracked": {"type": "boolean"},
    "index": {"type": "integer", "minimum": 0, "maximum": MAX_STASH_INDEX},
    "max_count": {"type": "integer", "minimum": 1, "maximum": MAX_COUNT},
    "message": {
        "type": "string",
        "minLength": 1,
        "maxLength": MAX_MESSAGE_LENGTH,
        "description": "Required for commit; the commit message.",
    },
    "mode": {"type": "string", "enum": list(RESET_MODES)},
    "name": {"type": "string"},
    "new_name": {"type": "string"},
    "old_name": {"type": "string"},
    "path": {"type": "string"},
    "paths": {
        "type": "array",
        "items": {"type": "string"},
        "minItems": 1,
        "maxItems": MAX_PATHS,
        "description": "Required for add; repository-relative paths to stage.",
    },
    "remote": {"type": "string"},
    "revision": {"type": "string"},
    "staged": {"type": "boolean"},
}

GIT_COMMAND_ARGUMENT_DESCRIPTION = (
    "Safe Git command string, excluding the git executable. Shell quoting is "
    "parsed into arguments, but the command is never executed through a shell. "
    "Familiar add and commit syntax is accepted and normalized. "
    "Use exactly one supported form: status --short --branch "
    "--untracked-files=all; diff --no-ext-diff --no-textconv --no-color "
    "[--cached] -- [path]; log --oneline --no-decorate --max-count=N; "
    "branch --list --no-color; show --no-ext-diff --no-textconv --no-color "
    "--format=fuller REVISION --; show --no-ext-diff --no-textconv --no-color "
    "REVISION:PATH; tag --list --sort=refname; remote; blame --date=short "
    "REVISION -- PATH; rev-parse --verify --end-of-options REVISION^{object}; "
    "reflog --oneline --max-count=N; ls-files -- [path]; stash list; "
    "add [--] PATH...; commit (-m|--message) MESSAGE or commit "
    "--no-verify --no-gpg-sign -m MESSAGE; "
    "branch --no-track NAME; branch -m OLD NEW; branch -d NAME; "
    "switch --no-guess BRANCH; merge --no-edit --no-gpg-sign BRANCH; "
    "cherry-pick --no-gpg-sign REVISION; restore --staged -- PATH...; "
    "reset (--soft|--mixed) REVISION; stash push [--include-untracked] "
    "[--message MESSAGE] --; stash pop stash@{INDEX}; tag NAME REVISION; "
    "tag -d NAME; fetch --no-tags REMOTE; pull --ff-only --no-rebase "
    "REMOTE BRANCH; push --porcelain --no-verify REMOTE "
    "refs/heads/BRANCH:refs/heads/BRANCH."
)

GIT_TOOL_PARAMETER_OBJECT: dict[str, Any] = {
    "type": "object",
    "properties": {
        "commands": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": MAX_COMMANDS,
            "description": (
                "Git commands to execute in order. Each item must match one "
                f"supported safe form. {GIT_COMMAND_ARGUMENT_DESCRIPTION}"
            ),
        },
    },
    "required": ["commands"],
    "additionalProperties": False,
}
