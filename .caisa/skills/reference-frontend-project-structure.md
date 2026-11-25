## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/frontend-project-structure.md
- docs/frontend/frontend.md

# Name
reference-frontend-project-structure

# Description
Read `docs/frontend/frontend-project-structure.md` as the physical source of truth and the `Project Structure` section of `docs/frontend/frontend.md` as the navigation point for related structural examples.

# Instructions

## Migrated contract

## Frontend Project-Structure Reference

Read `docs/frontend/frontend-project-structure.md` as the physical source of truth and the `Project Structure` section of `docs/frontend/frontend.md` as the navigation point for related structural examples.

Application source belongs under `frontend/`. Keep the approved top-level source tree shallow, group by responsibility, avoid a frontend `modules/` feature-root layer, and create no empty placeholder files or directories.

`claude/skills/frontend-project-structure.md` remains a compatibility pointer to the same documentation and does not define a second structure.

Do not restore removed routes or pages from historical maps or examples. In particular, the current frontend specifications contain no Progress feature; `BaseCard` is shared UI despite the prototype's cards-directory grouping, and `BaseModal` is documented with feature components.
