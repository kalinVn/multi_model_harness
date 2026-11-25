## Available Agents

None

## Available Skills

- .codex/workflows/setup-infrastructure.md
- .caisa/skills/workflow-setup-infrastructure.md
- .caisa/skills/workflow-testing-infrastructure.md

## Available Rules

- .caisa/CAISA.md

## Available Documents

None

# Name
workflow-code-review-infrastructure

# Description
Use after infrastructure testing to review the Docker infrastructure changes made by `.codex/workflows/setup-infrastructure.md`. This is a review workflow: do not modify files unless the user explicitly requests fixes, and do not review or generate missing application source.

# Instructions

## Migrated contract

## Code Review Infrastructure Workflow

Use after infrastructure testing to review the Docker infrastructure changes made by `.caisa/skills/workflow-setup-infrastructure.md`. This is a review workflow: do not modify files unless the user explicitly requests fixes, and do not review or generate missing application source.

Read `.caisa/CAISA.md`, the applicable infrastructure guide, the changed Docker/infrastructure files, the relevant Git diff, and results from `.caisa/skills/workflow-testing-infrastructure.md` when available. Review only the infrastructure affected by the current task; do not redesign unrelated infrastructure or application code, and do not treat missing application source as an infrastructure defect.

Check Docker and Compose configuration, service boundaries, networking, intentionally exposed ports, persistence and volumes, environment configuration, secret handling, health checks, development/production separation, security boundaries, and maintainability. Confirm that persistent data is protected and required tests did not fail.

Prioritize concrete findings as Critical, High, Medium, or Low. For each finding, report the affected file, problem, risk, and recommended fix. Never expose secrets, recommend deleting persistent data as a workaround, or approve infrastructure that failed required tests.

Finish with review status, blocking issues, and remaining risks. If no meaningful problems are found, state that clearly.
