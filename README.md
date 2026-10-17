# AI Harness

AI Harness is a terminal-based AI agent runner for working with a local project.
It keeps the conversation in a persistent in-memory session, sends requests to a
configured model provider, executes registered tools, and feeds their results back
to the model until a final response is produced.

The project provides:

- a shared `ModelClient` interface for Google Gemini, OpenAI, and Groq;
- a `MainOrchestrator` that manages conversation history and tool-call cycles;
- built-in tools for shell commands and reading or writing project files;
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

To use Groq:

```env
MODEL_PROVIDER=groq
GROQ_API_KEY=<your-key>
GROQ_MODEL=qwen/qwen3.8-27b
```

Both Groq variables are required. Select a model available to your account that
supports function calling and JSON replies. Restart the CLI after changing `.env`.
Groq uses the existing OpenAI SDK with `https://api.groq.com/openai/v1`; no new
dependency is needed. See [Groq compatibility](https://console.groq.com/docs/openai)
and [tool use](https://console.groq.com/docs/tool-use/overview).

Use `MODEL_PROVIDER=gemini` (or `google`) for Google Gemini and
`MODEL_PROVIDER=openai` for OpenAI.

## Groq implementation notes

Groq-specific tool conversion lives in `harness.mappers.groq_mapper`. The current
provider interface carries the tool catalog as system text from
`build_tools_schema`; the adapter converts that catalog into native function
definitions. Current tool arguments are required strings. If the shared catalog
format or argument types change, this conversion needs updating.

Native calls are converted to the existing `ToolCall` objects. The adapter does
not execute tools. Tool history/results keep the harness's existing text format
and original result IDs; native provider call IDs are not persisted. Replies and
summaries use the existing strict response parser. When native tools are supplied,
the response envelope is prompted and validated locally rather than using strict
JSON-schema output, which Groq does not combine with tool use.

The current orchestrator executes one batch of tools per user turn and returns
the initial response text. Automatic follow-up generation is not added by this
provider replacement.

## Test commands

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
