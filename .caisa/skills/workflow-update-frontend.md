# Name
workflow-update-frontend

# Description
Use only for a scoped change to an existing frontend. This workflow adapts `claude/agents/update-frontend-orchestrator.md`.

# Instructions

## Migrated contract

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
