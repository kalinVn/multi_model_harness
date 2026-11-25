## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- .caisa/commands/frontend_debug_component_builder.md

# Name
frontend-debug-component-builder

# Description
Plan and independently validate a new frontend, then build only components selected by component-specific debug descriptions and verify them in the isolated Vite workspace.

# Instructions

## Migrated contract

## Frontend Debug Component Builder

Execute [frontend_debug_component_builder](.caisa/commands/frontend_debug_component_builder.md) with the user's explicit `specification_path`.

The command owns planning and validation coordination. Frontend Component Builder Debug owns component selection and implementation. Vite Dev Environment owns dependency, test, build, preview, health, and URL verification.

Do not substitute a default specification path or broaden the workflow into production frontend implementation.
