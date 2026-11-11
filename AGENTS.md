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
