## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/pages-and-routes.md
- docs/frontend/frontend.md

# Name
frontend-routing

# Description
Implement or update Vue Router routes, guards, redirects, parameters, layouts, and navigation behavior from current project contracts.

# Instructions

## Migrated contract

## Frontend Routing

Read `../../../claude/skills/frontend-routing.md` for the responsibility boundary, but treat its route list as stale examples.

Use repository-root `docs/frontend/pages-and-routes.md` and `docs/frontend/frontend.md` as authority. Keep routing centralized in `frontend/src/router/`, distinguish visibility from authorization, preserve validated internal return targets, and apply the documented `401`/`403` behavior.

Do not invent routes or duplicate navigation rules. Verify route registration, guards, unknown-route handling, layout targets, and direct navigation.
