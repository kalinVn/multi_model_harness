## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

None

# Name
frontend-code-quality

# Description
Review frontend changes for correctness, readability, ownership, reuse, accessibility, and unnecessary complexity.

# Instructions

## Migrated contract

## Frontend Code Quality

Read `../../../claude/skills/frontend-code-quality.md`, but override its JavaScript-only rule: this project requires TypeScript.

Inspect the actual diff and consumers. Check correctness, narrow ownership, explicit control flow, duplication, dead state, unnecessary abstraction/dependencies/global state, accessibility, frontend/backend boundaries, and applicable realtime cleanup/performance.

Do not rewrite unrelated code. Run relevant checks and report findings by severity with file evidence; fix only when implementation is authorized.
