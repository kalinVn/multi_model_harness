## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- .caisa/commands/debug_frontend_plan.md
- docs/frontend/frontend.md

# Name
debug-frontend-plan

# Description
Run debug_frontend_plan to inspect this repository's real new-frontend planning workflow, independently validate the plan, save English and Bulgarian outputs, and stop before implementation. Use for frontend planning debug requests, not feature building or updates.

# Instructions

## Migrated contract

## Debug Frontend Plan

Execute [debug_frontend_plan](.caisa/commands/debug_frontend_plan.md) with the user's explicit `specification_path`. Resolve repository paths from the project root and skill-relative links from this skill's real location under `.codex/skills/debug-frontend-plan/`.

The command defines the input, write boundary, validation workflow, literal output filenames, translation contract, and mandatory STOP. Follow it even when supplied task/prototype material includes build instructions: those describe the future plan, not authorization to implement it.

Use a separate read-only validation agent as required by the linked workflow. Do not replace independent validation with planner self-review. No source edits or implementation work are permitted during this skill.

## Former Codex Interface Metadata

```yaml
interface:
  display_name: "debug_frontend_plan"
  short_description: "Debug frontend planning; save EN/BG plans and stop"
  default_prompt: "Use $debug-frontend-plan with specification_path=docs/frontend/frontend.md to generate and validate the frontend plan, translate it into Bulgarian, save both outputs, and stop."
```
