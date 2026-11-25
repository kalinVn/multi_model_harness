## Available Agents

None

## Available Skills

- .caisa/skills/workflow-update-frontend.md

## Available Rules

- .caisa/CAISA.md

## Available Documents

None

# Name
update_frontend

# Description
Apply a scoped change to an existing frontend.

# Tools
read_file, list_directory, write_file, bash, git

# Invocation
execute command update_frontend specification_path=<repository-relative path>

# Instructions
## update_frontend

Apply a scoped change to an existing frontend.

## Input

Receive an explicit update prompt and/or `update_specification_path`. Accept `frontend_specification_path` when project context is needed.

## Execution

Read `.caisa/CAISA.md`, then execute `.caisa/skills/workflow-update-frontend.md`. Inspect the relevant existing frontend, produce the smallest source-backed update plan, select only required skills, implement the change, and run proportional regression checks.

Do not run the new-frontend build workflow or rebuild unrelated functionality.

## Embedded Workflow Contract

## Existing Frontend Update Workflow

Use only for a scoped change to an existing frontend. This workflow adapts `claude/agents/update-frontend-orchestrator.md`.

1. Read the explicit update request and only the relevant specifications.
2. Inspect affected existing pages, components, routes, layouts, tokens, stores, services, tests, and direct consumers.
3. Apply the `update-existing-frontend-design` skill to produce the smallest correct update plan.
4. Verify that the plan identifies reuse, extension, variants, unavoidable new components, route impact, responsive impact, dependencies, risks, regression boundaries, and update order.
5. Select only the discoverable skills required by that plan.
6. Implement in dependency order, preserving unrelated behavior and existing interfaces where practical.
7. Run relevant responsive, accessibility, security, build, lint, type/static, unit/component, browser, and regression checks.
8. Review for scope expansion, duplication, ownership conflicts, dead state, and frontend/backend boundary violations.

Stop and report missing requirements, missing referenced sources, or required code that cannot be located. Do not silently switch to the new-frontend workflow.

Report the request, skills used, affected/reused/created files and components, routes, checks with actual outcomes, and unresolved issues.
