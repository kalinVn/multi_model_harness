# Project Structure Documentation

This document outlines the architecture of the AI Harness project based on the contents of `src/harness`.

## Core Responsibilities

- **`agents/`**: Contains orchestrators that manage the conversation loop, tool-call cycles, and interaction with model providers.
- **`app/`**: Implements the CLI interface for user interaction.
- **`builder/`**: Responsible for constructing tool schemas, model messages, and command contexts.
- **`config/`**: Stores configuration for various tools and sensitive data redaction.
- **`contracts/`**: Defines abstract base classes or interfaces for tools.
- **`domain/`**: Houses core domain models like `Message`, `Session`, `ToolCall`, and `ToolResult`.
- **`factory/`**: Creates model client instances.
- **`loader/`**: Handles loading of commands and command contexts.
- **`mappers/`**: Maps between provider-specific formats (Gemini and OpenAI).
- **`models/`**: Defines shared data structures and API models.
- **`parser/`**: Parses model responses, commands, and tool calls.
- **`providers/`**: Implements concrete clients for supported AI model providers.
- **`resolver/`**: Resolves commands to their implementations.
- **`service/`**: Contains high-level services for command execution, tool management, and data protection.
- **`tools/`**: Implements specific tools like `bash`, `git`, file I/O.
- **`validators/`**: Validates responses, messages, and tool definitions.

## Workflow

1. **Initialization**: The CLI (`app/`) initializes the `Session` and `MainOrchestrator` (`agents/`).
2. **Input**: User input is received through the CLI.
3. **Orchestration**: The `MainOrchestrator` manages the interaction flow:
    - Prepares the request using `builder/`.
    - Sends the request to the chosen `provider` (`providers/`).
    - Receives a response, which is parsed by `parser/`.
4. **Tool Execution**: If the model requests a tool call:
    - The `ToolService` (`service/`) identifies and executes the tool from `tools/`.
    - Results are validated (`validators/`) and fed back into the `Session`.
5. **Cycle**: This continues until a final response is generated.
