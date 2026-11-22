# Name
infrastructure-git-safety

# Description
Maintain safe, idempotent Git ignore rules and perform filename-only sensitive-file audits for project infrastructure.

# Instructions

## Migrated contract

## Infrastructure Git Safety

Read `../../../claude/skills/infrastructure-git-safety.md`, repository-root `.caisa/skills/workflow-setup-infrastructure.md`, and the Docker specification.

Merge missing root `.gitignore` rules without replacing user entries or hiding source/docs/infrastructure. Keep `.env.example` trackable. Audit sensitive candidates by filename and Git status only; never read, print, delete, stage, or automatically untrack their contents.

Report rules added/preserved and sensitive paths requiring manual action.
