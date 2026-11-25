## Available Agents

- .caisa/agents/new-frontend-orchestrator.md

## Available Skills

- .caisa/skills/rule-frontend-planning.md
- .caisa/skills/plan-new-frontend.md
- .caisa/skills/frontend-plan-validator.md

## Available Rules

None

## Available Documents

- docs/frontend/frontend-project-structure.md

# Name
build_frontend

# Description
Build a new frontend from an explicit specification path.

# Tools
read_file, list_directory, write_file, bash, git

# Invocation
execute command build_frontend specification_path=<repository-relative path>

# Instructions
## build_frontend

Build a new frontend from an explicit specification path.

## Input

```text
specification_path=<repository-relative path>
```

The input is required. Resolve it from the repository root and stop if it is missing or unreadable.

## Embedded Workflow Contract

## New Frontend Workflow

Use only when the user explicitly requests construction of a new frontend and supplies `specification_path`. This workflow is the Codex adaptation of `.caisa/agents/new-frontend-orchestrator.md`.

## Gate

1. Read  `.caisa/skills/rule-frontend-planning.md`, and the supplied specification.
2. Run the planner contract in `.caisa/skills/plan-new-frontend.md`.
3. Use a separate read-only agent with `.caisa/skills/frontend-plan-validator.md`.
4. Require `status: valid`, no errors, and an exact unchanged `validated_plan`.
5. Permit at most two planner corrections after the initial validation. Stop earlier for missing evidence, a required user decision, malformed validation, or unavailable independent validation.
6. Never implement from an invalid or unvalidated plan.

## Delivery

After validation, use the plan's Build Order and select only required discoverable skills under `.caisa/skills/`. Establish structure from `docs/frontend/frontend-project-structure.md`; do not add a frontend `modules/` layer or empty placeholders.

Build in dependency order:

1. design foundation and application structure
2. shared components
3. feature components and browser/integration boundaries
4. layouts and pages
5. routing and guards
6. responsive/accessibility behavior
7. integration, tests, code-quality review, and final verification

## Verification and Report

Run applicable build, type/static checks, lint, unit/component tests, and browser tests. Verify responsive/accessibility and security-sensitive contracts. Do not claim unperformed or mocked work as live functionality.

Report the specification, validation attempts/warnings, skills used, files and routes changed, integrations, checks with actual outcomes, and unresolved dependencies.
