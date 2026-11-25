# Name
frontend_debug_component_builder

# Description
Plan, validate, build, preview, and test selected frontend components in the isolated debug workspace.

# Tools
read_file, list_directory, write_file, bash

# Invocation
execute command frontend_debug_component_builder specification_path=<repository-relative path>

# Instructions
## frontend_debug_component_builder

Plan, validate, build, preview, and test selected frontend components in the isolated debug workspace.

## Invocation

Use the discoverable repository skill:

```text
$frontend-debug-component-builder specification_path=docs/frontend/frontend.md
```

`specification_path` is required and must resolve from the repository root.

## Workflow

1. Read repository-root `.caisa/CAISA.md`.
2. Invoke `.caisa/skills/plan-new-frontend.md` with the explicit `specification_path`.
3. Pass the complete returned plan and the same `specification_path` to `.caisa/skills/frontend-plan-validator.md`.
4. Use one initial validation and at most two corrected-plan validations. Continue only with an unchanged `validated_plan` and no validation errors. Preserve validator warnings.
5. Extract only the complete shared-component and feature-component entries from `validated_plan`. Do not reinterpret, expand, or validate them inside this command.
6. Invoke `.caisa/skills/frontend-component-builder-debug.md` once and pass only `component_plan`.
7. Pass the component slugs returned by Frontend Component Builder Debug to `.caisa/skills/vite-dev-environment.md` with `debug_root: source/debug/frontend/` and request dependency preparation, tests, build, an interactive preview, health verification, and component URL verification.
8. Return one report containing the validation status and warnings, the Frontend Component Builder Debug result, and the Vite Dev Environment result.

## Boundaries

- Do not inspect or match Additional Description and Functionality files inside this command.
- Do not implement or edit component code inside this command.
- Do not invoke page building, routing, integration, or production frontend workflows.
- Do not modify production frontend files or prototypes.
- Stop after Frontend Component Builder Debug and Vite Dev Environment return their reports.
