# AI Harness

AI Harness is a terminal-based AI agent runner for working with a local project.
It keeps the conversation in a persistent in-memory session, sends requests to a
configured model provider, executes registered tools, and feeds their results back
to the model until a final response is produced.

The project provides:

- a shared `ModelClient` interface for Google Gemini and OpenAI;
- a `MainOrchestrator` that manages conversation history and tool-call cycles;
- built-in tools for shell commands, Git, and reading or writing project files;
- reusable Markdown commands stored in `.caisa/commands`;
- compact summaries of tool results to keep longer sessions manageable;
- an interactive CLI that preserves the session until `exit` or `quit`.

## Quick start

Install the project and configure the model provider in `.env`:

```bash
pip install -e .
python main.py
```

The package entry point remains available with
`python -m harness.app.cli.main`.

## Model providers

Use `MODEL_PROVIDER=gemini` (or `google`) for Google Gemini and
`MODEL_PROVIDER=openai` for OpenAI.

The orchestrator sends each batch of results, including failures, back to the
model and continues until the model returns a final response or the configured
iteration limit is reached.

## Git tool

The `git` tool provides a restricted interface to the Git repository configured
as the harness working directory. It is registered alongside `read_file`,
`write_file`, and `bash` by `register_tools`, so it uses the existing
`ToolRegistry` and `ToolService` execution lifecycle.

The tool accepts an `operation` and operation-specific `args`. Its provider
schema exposes `args` as a typed object, including an array of `paths` for
`add` and a string `message` for `commit`. Runtime validation remains the final
authority, and direct Python callers may also pass legacy JSON-encoded `args`.

| Operation | Type | Arguments |
| --- | --- | --- |
| `status` | Read | None |
| `diff` | Read | Optional `staged` boolean and repository-relative `path` |
| `log` | Read | Optional `max_count` integer from 1 to 100 |
| `branch_list` | Read | None |
| `show` | Read | Optional `revision` and repository-relative `path` |
| `tag_list` | Read | None |
| `remote_list` | Read | None; returns names without URLs |
| `blame` | Read | Required `path`; optional `revision` |
| `rev_parse` | Read | Optional `revision`, defaulting to `HEAD` |
| `reflog` | Read | Optional `max_count` integer from 1 to 100 |
| `ls_files` | Read | Optional repository-relative `path` |
| `stash_list` | Read | None |
| `add` | Write | Non-empty `paths` array |
| `commit` | Write | Non-empty `message` |
| `branch_create` | Write | New branch `name` |
| `branch_rename` | Write | Required `old_name` and `new_name` |
| `branch_delete` | Write | Branch `name`; uses safe `-d` deletion |
| `switch` | Write | Existing `branch` name |
| `merge` | Write | Existing `branch` name |
| `cherry_pick` | Write | Required `revision` |
| `restore` | Write | Required `paths` and `staged: true`; only unstages |
| `reset` | Write | Required `mode` (`soft` or `mixed`); optional `revision` |
| `stash` | Write | Optional `message` and `include_untracked` boolean |
| `stash_pop` | Write | Optional stash `index`, defaulting to `0` |
| `tag_create` | Write | Required tag `name`; optional `revision` |
| `tag_delete` | Write | Required tag `name` |
| `fetch` | Remote | Required configured `remote` name |
| `pull` | Remote | Required `remote` and `branch`; fast-forward only |
| `push` | Remote | Required `remote` and `branch`; never forced |

Example tool calls:

```json
{
  "tool": "git",
  "arguments": {
    "operation": "status",
    "args": {}
  }
}
```

```json
{
  "tool": "git",
  "arguments": {
    "operation": "merge",
    "args": {"branch": "master"}
  }
}
```

```json
{
  "tool": "git",
  "arguments": {
    "operation": "stash",
    "args": {}
  }
}
```

Read operations are enabled by default. Write operations are disabled by
default because the harness has no interactive approval mechanism. Enable them
only for a trusted local repository by adding this setting to `.env` and
restarting the CLI:

```env
HARNESS_ENABLE_GIT_WRITE_OPERATIONS=true
```

Remote operations are independently disabled by default. Enable them only when
the configured remotes and credentials are trusted:

```env
HARNESS_ENABLE_GIT_REMOTE_OPERATIONS=true
```

The tool only permits its documented operations, invokes Git with argument
lists instead of a shell, disables repository hooks, rejects option-like and
out-of-repository paths, and does not implement destructive variants such as
hard reset, clean, force push, forced branch deletion, or remote deletion.
`pull` is restricted to fast-forward integration, `restore` can only unstage,
and `remote_list` omits URLs to avoid exposing embedded credentials. Git output
also redacts HTTP(S) URL credentials and sensitive environment values.

## Execution and context limits

The following optional `.env` settings bound model retries and request size:

```env
HARNESS_MAX_TOOL_STEPS=20
HARNESS_MAX_COMMAND_RESPONSE_RETRIES=2
HARNESS_MAX_TOOL_RESULT_OUTPUT_REQUEST_STEPS=3
HARNESS_MAX_HISTORY_MESSAGES=40
HARNESS_MAX_TOOL_RESULT_CHARS=12000
```

Initial system/tool instructions are retained while only the newest configured
number of conversation messages are sent. Tool outputs are truncated with an
explicit marker before they are sent to a provider. These limits reduce the
risk of HTTP 413 responses.

## Test commands

Run the unit suite with:

```bash
python -m unittest discover -s tests
```

Start the interactive CLI:

```bash
python main.py
```

Then enter any of the following commands at the prompt:

```text
execute command hello
execute command test_bash
execute command test_write_file
```

- `hello` verifies that a command can be loaded and executed.
- `test_bash` runs `ls` through the Bash tool.
- `test_write_file` creates `tool-test.txt` containing
  `Hello from AI Harness!` through the file-writing tool.


  



