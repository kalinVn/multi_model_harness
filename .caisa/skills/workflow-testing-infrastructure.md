# Name
workflow-testing-infrastructure

# Description
Use after application or infrastructure changes to validate only the affected system. For Docker infrastructure work, run this workflow after implementation and before infrastructure code review.

# Instructions

## Migrated contract

## Testing Infrastructure Workflow

Use after application or infrastructure changes to validate only the affected system. For Docker infrastructure work, run this workflow after implementation and before infrastructure code review.

Read `.caisa/CAISA.md`, the applicable setup workflow, the relevant infrastructure guide, and only the changed files and configuration needed for the tests. Inspect the repository before selecting commands; do not assume files listed in `claude/PROJECT_STRUCTURE.md` exist.

Test only infrastructure and application services that can currently run. When Docker is affected, verify applicable Compose configuration, available image builds, available container startup and health, PostgreSQL and Redis connectivity, required volumes, and required networks. Test API responses and frontend-to-API access only when the corresponding application source and services exist. Missing application source is `PENDING APPLICATION BUILD`, not an infrastructure-test failure.

Never delete production data or persistent volumes without explicit permission. Do not hide failures, disable tests to obtain a passing result, or claim success when a required test failed. Fix only safe, clearly in-scope issues when the requested work authorizes fixes.

Report tests executed, passed, failed, and skipped; include relevant errors or logs without exposing secrets, and recommend the next action. A successful build alone is not proof that the system works.
