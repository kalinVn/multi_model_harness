# CAISA.md

# Tennis AI Coach

## Purpose

Tennis AI Coach is a commercial subscription-based platform that observes a tennis player through a camera and provides low-latency coaching through headphones.

caisa must:
1. Read this file before significant work.
2. Inspect existing code before modifying it.
3. Load only documentation relevant to the current task.
4. Use specialized agents when appropriate.
5. Preserve existing architecture unless change is justified.

Detailed knowledge belongs in `docs/`, `.caisa/agents/`, `.caisa/rules/`, and `.caisa/skills/`.

---

## Architecture

Core realtime pipeline:

```text
Camera
→ Vision Engine
→ Structured State
→ Coach Engine
→ Instruction
→ Audio
```

Vision answers: **What is happening?**

Coach Engine answers: **What should the player do?**

Keep perception and coaching logic separate.

Major domains:

- Client
- Admin
- API / Auth / Payments
- Realtime
- Vision
- Coach Engine
- Training
- Analysis
- Audio

---

## Technology

Frontend:
- Vue 3
- ES6
- Vue Router
- Vite
- `vite.config.ts` — development server and build configuration
- Pinia — state management
- HTML5
- CSS3 / SCSS
- HTML5 Canvas API — video overlays, pose landmarks, trajectories and visual feedback
- pixi.js
- MediaDevices API — camera access
- ESLint — static code analysis and code-quality rules
- Prettier — code formatting
- Vitest — unit and component tests
- Playwright — end-to-end and browser testing

Backend:
- Python
- FastAPI
- Pydantic

Data:
- PostgreSQL
- SQLAlchemy + Alembic
- Redis
- S3-compatible object storage

Platform:
- WebSockets
- Stripe
- Docker + Docker Compose
- kubernetes
- aws
- github action

Authentication:
- Email/password
- Google
- Apple
- 2FA



Do not replace core technologies without justification.

---

## Docker


Docker configuration belongs in:

`infrastructure/docker/`

Detailed instructions:

`docs/infrastructure/docker.md`

---

## Realtime & AI

Latency is a first-class requirement.

Use lightweight ML models primarily for perception:

- pose
- ball
- racket
- court

Prefer deterministic algorithms where practical for:

- tracking
- geometry
- trajectory
- rally state
- stroke state
- coaching decisions

Do not put an LLM in the per-frame realtime path.

Never fabricate vision data or coaching decisions when confidence is insufficient.

---

## Security & Data

Never commit secrets or expose credentials.

Never store plaintext passwords.

Authorization must be enforced server-side.

Stripe webhooks must be verified and idempotent.

PostgreSQL is the persistent source of truth.

Redis is for cache and temporary/realtime state.

Large videos and binary files belong in object storage.

---

## Agents

Agents live in `.caisa/agents/`.

Use the appropriate specialized agent for each task.

Core agents cover:

- architecture
- frontend
- backend
- auth
- database
- payments
- admin
- vision
- realtime
- tennis coaching
- training
- analysis
- audio
- security
- testing
- performance
- devops
- kubernetes
- ci/cd

Infrastructure agents:
- Testing Infrastructure Agent
- Verification Infrastructure Agent
- Code Review Infrastructure Agent


Agents must respect domain boundaries and shared contracts.

---

## Commands

Commands live in `.caisa/commands/`.

Primary commands:

- `/build-up`
- `/update-app`
- `/analyze-project`
- `/code-review`
- `/refactor`
- `/fix-errors`
- `/run-tests`
/

`/build-up` orchestrates major implementation work.

`/update-app` applies changes to the existing application.
- `/setup-infrastructure`
- `/setup-production`
---

## Context

Load context progressively:

```text
caisa.md
→ Task
→ Relevant Agent
→ Relevant Rules / Skills
→ Relevant Docs
→ Relevant Code
```

Never load the entire documentation tree unnecessarily.

---

## Development Rules

Before implementation:

- understand the task
- inspect existing code
- identify affected domains
- load relevant context

After implementation:

- validate contracts
- run relevant tests
- check security
- check realtime performance when applicable
- update affected documentation

Never rewrite unrelated working code.

Never disable tests just to make a build pass.

Fix root causes.

---

## Priorities

Prioritize:

**Correctness → Security → Latency → Reliability → Maintainability → Scalability → Cost**

Prefer:

**simple → measurable → tested → improved**

Build a production system, not a demo.

# Migrated Repository Instructions

The existing artist-application context above remains authoritative. The Codex configuration also contains Tennis/frontend contracts whose referenced `claude/` and `docs/frontend/` sources are absent from this repository. Those contracts are available as Caisa commands, agents, and skills, but must stop with a clear blocker when their required source files are missing; they do not override the project context above.

## Repository Python Rules

# Python Coding Style

Apply these rules whenever generating, modifying, or refactoring Python code in this project.

## Readability

Write clean, compact, readable Python code.

Avoid unnecessary:

- Parentheses
- Line breaks
- Indentation
- Intermediate variables
- Abstractions
- Helper functions

Keep logically related statements together.

Separate independent operations with blank lines.

## Variable Assignments

Keep short variable assignments and simple expressions on one line.

Do not wrap an assignment in parentheses or split a short path expression across multiple lines.

WRONG:

~~~python
self._project_root = (
    project_root or Path.cwd()
)
commands_directory = (
    self._project_root
    / ".caisa"
    / "commands"
)
~~~

CORRECT:

~~~python
self._project_root = project_root or Path.cwd()
commands_directory = self._project_root / ".caisa" / "commands"
~~~

## Python Function Formatting Conventions

**Important:** Follow these conventions whenever creating or modifying Python code.

### 1. Function Definitions

Keep function declarations on a single line whenever reasonably possible.

Do not split a function signature unnecessarily, especially when it contains only one parameter.

Use 4 spaces for indentation. Never use tabs.

WRONG:

~~~python
def map_tool_definitions(
    tool_definitions: list[ToolDefinition],
) -> list[dict[str, Any]]:
    """Convert shared definitions to Gemini declaration dictionaries."""
    return ToolConverterFacade().convert_tools("gemini", tool_definitions)
~~~

CORRECT:

~~~python
def map_tool_definitions(tool_definitions: list[ToolDefinition]) -> list[dict[str, Any]]:
    """Convert shared definitions to Gemini declaration dictionaries."""

    return ToolConverterFacade().convert_tools("gemini", tool_definitions)
~~~

### 2. Indentation

Follow these rules:

- Function declarations start at the correct scope indentation.
- Function bodies use 4 spaces per indentation level.
- Docstrings are indented inside the function.
- Executable statements are indented inside the function.
- Never put a function body on the same line as its declaration.
- Never put a docstring and executable statement on the same line.

### 3. Docstring Spacing

Insert exactly one blank line after a function docstring before executable statements.

Keep the docstring directly below the function declaration.

### 4. Function Parameters

- Keep parameters on one line whenever readable.
- Do not wrap a single parameter unnecessarily.
- Do not add trailing commas after the final parameter.
- Avoid unnecessary parentheses.
- Split parameters across multiple lines only when genuinely needed for readability.

### 5. Function Calls

Keep short calls on one line.

Keep an assignment and its function call on one line when the method name and arguments remain readable.

WRONG:

~~~python
available_tools = self._tool_service.get_available_tools_by_names(
    self._tool_definitions,
    self._agent.allowed_tools
)
~~~

CORRECT:

~~~python
available_tools = self._tool_service.get_available_tools_by_names(self._tool_definitions, self._agent.allowed_tools)
~~~

Do not put complex expressions, conditional expressions, or large constructor calls directly inside methods such as `append()`.

Prepare or update the value first, then pass the simple value to the method. Prefer a clear `if` statement when the value depends on a condition.

WRONG:

~~~python
messages.append(message if content == message.content else replace(message, content=content))
~~~

CORRECT:

~~~python
if content != message.content:
    message = replace(message, content=content)
messages.append(message)
~~~

WRONG:

~~~python
native_calls.append(
    ToolCall(
        name=function_call.name,
        arguments=arguments
    )
)
~~~

CORRECT:

~~~python
native_calls.append(ToolCall(name=function_call.name, arguments=arguments))
~~~

### 6. Multiline Constructor Calls

When multiple lines are necessary, align parameters consistently.

Do not wrap individual argument values in unnecessary parentheses.

Do not add a trailing comma after the last argument.

WRONG:

~~~python
return ModelResponse(
    text=parsed_response.text,
    tool_calls=native_calls,
    tool_result_summaries=parsed_response.tool_result_summaries,
    tool_result_output_requests=(
        parsed_response.tool_result_output_requests
    ),
)
~~~

CORRECT:

~~~python
return ModelResponse(
    text=parsed_response.text,
    tool_calls=native_calls,
    tool_result_summaries=parsed_response.tool_result_summaries,
    tool_result_output_requests=parsed_response.tool_result_output_requests
)
~~~

### 7. Blank Lines

Follow these conventions:

- Two blank lines between top-level functions.
- One blank line between class methods.
- One blank line after a docstring before executable code.
- One blank line between independent logical blocks when useful.
- Keep related statements together.
- Never insert blank lines that break Python syntax.
- Do not insert blank lines between try/except/finally clauses.
- Separate independent if statements and logical operations with blank lines.
- Add a blank line before a final return when it improves readability.
- Do not add blank lines mechanically after every statement.

Keep related variable assignments together at the beginning of the current function, loop, or conditional block whenever their dependencies allow it.

Insert one blank line after the assignment group before an `if`, `return`, or the next logical step. Separate distinct processing steps with one blank line so the control flow remains visible.

WRONG:

~~~python
for _ in range(agent.max_steps):
    messages = self.observe(messages)
    response = self.think(messages, available_tools)
    tool_calls = self.decide(response)
    if not tool_calls:
        return response.text
    self.action(messages, tool_calls, available_tools)
~~~

CORRECT:

~~~python
for _ in range(agent.max_steps):
    messages = self.observe(messages)
    response = self.think(messages, available_tools)
    tool_calls = self.decide(response)

    if not tool_calls:
        return response.text

    self.action(messages, tool_calls, available_tools)
~~~

### 8. Imports

Prefer single-line imports.

WRONG:

~~~python
from harness.config.response.gemini_response_instruction import (
    GEMINI_RESPONSE_INSTRUCTION,
)
~~~

CORRECT:

~~~python
from harness.config.response.gemini_response_instruction import GEMINI_RESPONSE_INSTRUCTION
~~~

Avoid unnecessary parentheses and line wrapping in imports.

### 9. General Conventions

Follow PEP 8 for:

- Naming conventions
- Indentation
- Import organization
- Function and class separation
- General readability

Use the explicit formatting preferences in this AGENTS.md for:

- Single-line function signatures
- Compact function calls
- Blank lines after docstrings
- No unnecessary parentheses
- No trailing commas in multiline calls

Prioritize readability over automatic formatting conventions, avoid aggressive line wrapping, and prefer compact expressions when they remain understandable.

Respect Python syntax and the project's configured line-length limit. Do not sacrifice readability or valid Python syntax merely to avoid line breaks.

Do not disable required formatters or linters. If a formatter such as Black or Ruff conflicts with these explicit preferences, report the conflict instead of silently changing project configuration.

## Conditional Expressions

Keep simple conditional expressions on one line.

Correct:

~~~python
role = "model" if message.role == "assistant" else "user"
~~~

Incorrect:

~~~python
role = (
    "model"
    if message.role == "assistant"
    else "user"
)
~~~

## Collection Filtering and Predicate Logic

Do not hide domain filtering or lookup logic inside dense one-line `any()`, `all()`, `next()`, `filter()`, `map()`, generator expressions, or lambdas.

When a collection query has domain meaning, expose it through the model that owns that data and implement it with a clear loop and explicit return values.

WRONG:

~~~python
summary_requested = any(message.type == "tool_result_summary" for message in messages)
~~~

CORRECT:

~~~python
summary_requested = Message.contains_type(messages, "tool_result_summary")
~~~

Avoid lambdas in production control flow and domain filtering. Use a named method or an explicit loop so the responsibility and stopping condition are visible.

Simple comprehensions remain acceptable for straightforward data construction when they do not hide domain decisions.

## Type Hints

Use existing Harness contracts.

Prefer our own models:

- Message
- ModelResponse
- ToolDefinition
- ToolCall

Avoid introducing unnecessary SDK-specific types into shared application code.

Do not introduce duplicate models or redundant abstractions.

## Explicit SDK and API Calls

Avoid unnecessary wrapper methods and context managers that hide a single SDK or API call.

BAD:

~~~python
response = self._fetch_response(contents, config)
~~~

BAD:

~~~python
with handle_api_errors(self._model):
    response = self._client.models.generate_content(...)
~~~

PREFERRED:

~~~python
response = self._client.models.generate_content(...)
~~~

Keep API calls explicit and readable.

Delegate error classification to dedicated validators.

Do not introduce unnecessary helper methods, context managers, or abstraction layers.

## Existing Code

When modifying existing code:

- Follow these formatting rules.
- Preserve existing behavior.
- Avoid unrelated refactoring.
- Do not introduce unnecessary complexity.
- Keep the implementation simple and maintainable.

## Codex Project Adapter

# Project Configuration Adapter

Root `.caisa/CAISA.md` is the active Codex instruction source. `claude/CLAUDE.md` remains Claude compatibility configuration and may be consulted for historical/project context, but it does not override active instructions.

Use:

- Vue 3, TypeScript, Vite, Pinia, and Vue Router for the frontend.
- Python, FastAPI, Pydantic, PostgreSQL/SQLAlchemy/Alembic, Redis, object storage, WebSockets, Stripe, Docker/Compose, Kubernetes on AWS, and GitHub Actions as defined by `.caisa/CAISA.md`.
- `docs/frontend/frontend.md` and its declared supporting documents for current frontend product, route, component, integration, and structure contracts.
- `.codex/workflows/` for maintained infrastructure execution, frontend orchestration, and planning-debug execution.

Never infer file existence from `claude/PROJECT_STRUCTURE.md`; verify the repository.
