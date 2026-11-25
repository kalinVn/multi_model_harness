# Name
update-existing-frontend-design

# Description
Analyze a scoped change to an existing frontend and return the smallest source-backed update plan without implementing it.

# Instructions

## Migrated contract

## Update Existing Frontend Design

Read the full compatibility source at `../../../claude/skills/update-existing-frontend-design.md`, then apply these active overrides:

- use `../../../claude/rules/frontend/frontend-design-system.md` rather than its stale missing rule path;
- use TypeScript and the structure in repository-root `docs/frontend/frontend-project-structure.md`;
- do not introduce a frontend `modules/` layer;
- use current routes, components, contracts, and prototypes from repository-root `docs/frontend/`, not example lists in the compatibility source.

Inspect affected code and direct consumers. Return reuse/extend/variant/new decisions, route/design impact, risks, regression checks, and dependency order. Do not implement the update.
