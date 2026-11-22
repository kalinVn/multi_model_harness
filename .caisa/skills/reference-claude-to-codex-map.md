# Name
reference-claude-to-codex-map

# Description
- `claude/CLAUDE.md` → active project instructions in root `AGENTS.md`; Codex-specific source routing remains in `.codex/rules/` and this map. - `claude/PROJECT_STRUCTURE.md` → inventory only, never proof that a listed file exists. Actual files are verified before use, and historical entries such as the removed frontend Progress view must not be restored when absent from current frontend specifications.

# Instructions

## Migrated contract

## Claude-to-Codex Adaptation Map

## Configuration

- `claude/CLAUDE.md` → active project instructions in root `.caisa/CAISA.md`; Codex-specific source routing remains in `.codex/rules/` and this map.
- `claude/PROJECT_STRUCTURE.md` → inventory only, never proof that a listed file exists. Actual files are verified before use, and historical entries such as the removed frontend Progress view must not be restored when absent from current frontend specifications.

## Commands and Orchestration

- `claude/commands/build-frontend.md` → `.caisa/commands/build_frontend.md` → `.caisa/skills/workflow-new-frontend.md`.
- `claude/commands/frontend-debug-component-builder.md` → `.caisa/commands/frontend_debug_component_builder.md` → the discoverable `.codex/skills/frontend-debug-component-builder/` entrypoint.
- Empty `claude/commands/update-frontend.md` plus `claude/agents/update-frontend-orchestrator.md` → `.caisa/commands/update_frontend.md` → `.caisa/skills/workflow-update-frontend.md`.
- Infrastructure commands/agents → `.caisa/commands/setup_infrastructure.md`, `.caisa/commands/setup_production.md`, `.codex/agents/`, and the maintained `.codex/workflows/` implementations.
- `claude/agents/new-frontend-orchestrator.md` → full-build workflow; its Steps 1–3 also back the planning-only `.caisa/skills/workflow-frontend-planning.md`.

## Skills

Discoverable Codex adapters live under `.caisa/skills/<skill-name>.md` and are linked from `.agents/skills/<skill-name>`. They preserve current project instructions and route to authoritative specifications instead of copying stale examples.

The planning-only debug workflow keeps its detailed planner and validator role contracts at `.caisa/skills/plan-new-frontend.md` and `.caisa/skills/frontend-plan-validator.md`. Their discoverable adapters route to those contracts.

The isolated component-debug workflow uses `.codex/skills/frontend-component-builder-debug/` for component selection and implementation and `.codex/skills/vite-dev-environment/` for the isolated runtime and verification boundary.

## Rules and References

- Claude's frontend design-system source is read in place through `.caisa/skills/rule-frontend-design-system.md`.
- Frontend architecture sources are routed through `.caisa/skills/reference-frontend-architecture.md`.
- Frontend physical placement is routed through `.caisa/skills/reference-frontend-project-structure.md`.

## Intentional Non-Copies

- No literal copy of `claude/CLAUDE.md`, `claude/PROJECT_STRUCTURE.md`, or the large design-system file: doing so would create competing maintained configuration.
- No native Claude agent registry emulation: Codex role files and collaboration tools provide the equivalent behavior.
- No direct reuse of stale example route lists, JavaScript-only defaults, or frontend `modules/` placement from older Claude skills; active `.caisa/CAISA.md` and `docs/frontend/` override them.
- No invented CI/CD agent: `claude/agents/devops-agent.md` references one that does not exist on disk. Production coordination stays in the verified Codex workflows.
