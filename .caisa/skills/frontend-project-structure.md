## Available Agents

None

## Available Skills

- .codex/skill-adapters/frontend-project-structure/SKILL.md
- .caisa/skills/reference-frontend-project-structure.md
- .codex/skills/frontend-project-structure.md

## Available Rules

None

## Available Documents

- docs/frontend/frontend-project-structure.md
- docs/frontend/frontend.md
- docs/frontend/pages-and-routes.md
- docs/frontend/shared-ui-components.md
- docs/frontend/feature-components.md

# Name
frontend-project-structure

# Description
Establish or review the approved physical Vue frontend structure without scaffolding feature implementation.

# Instructions

## Source: .codex/skill-adapters/frontend-project-structure/SKILL.md

## Frontend Project Structure

Read repository-root `docs/frontend/frontend-project-structure.md`, the `Project Structure` section of repository-root `docs/frontend/frontend.md`, and repository-root `.caisa/skills/reference-frontend-project-structure.md`.

Inspect the repository before creating anything. Create only directories/files required by an approved implementation plan, keep the tree shallow and responsibility-based, and never introduce a frontend `modules/` feature-root layer or empty placeholders.

## Source: .codex/skills/frontend-project-structure.md

## Frontend Project Structure Reference

Read the `Project Structure` section in `docs/frontend/frontend.md` before planning or implementing frontend file placement. Treat that section as the navigation point: follow every authoritative structure document it references rather than hardcoding a Codex-only source list.

Inspect the existing repository before creating files and use any prototype directories or complex-component examples referenced there only as organization and ownership guidance. Map required frontend work into the documented locations and report genuine conflicts instead of defining or duplicating an alternative structure here. Do not introduce a frontend `modules/` feature-root layer; backend module organization is unaffected.

Current page, route, and shared-versus-feature ownership comes from `docs/frontend/frontend.md`, `docs/frontend/pages-and-routes.md`, `docs/frontend/shared-ui-components.md`, and `docs/frontend/feature-components.md`. `BaseCard` is shared UI; its consumers own card content and domain-specific presentation through slots. Do not restore removed pages such as Progress from `claude/PROJECT_STRUCTURE.md` or older examples.
