## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/examples/workflow-examples/plan-new-frontend-example-result.md

# Build Frontend Workflow

## Purpose

Explain in human-readable form what the `/build-frontend` command does, which files it reads, how the New Frontend Orchestrator coordinates the work, what the planning skill returns, and how the frontend is verified.

This document is explanatory. Executable workflow rules remain in the command, orchestrator, and skills under `claude/`.

## Start the Workflow

The `/build-frontend` command invokes the New Frontend Orchestrator and provides the path to the frontend specification.

## New Frontend Orchestrator

1. The orchestrator invokes the `plan-new-frontend` skill and provides the path to the frontend specification.
2. The planning skill reads and analyzes the frontend specification, its referenced prototype, and the applicable design rules.
3. The planning skill returns a complete structured frontend plan to the orchestrator.

### Receive the Frontend Plan

The New Frontend Orchestrator receives the complete structured plan returned by `plan-new-frontend`. It becomes the implementation map only after independent validation in Step 3.

Example result: [Plan New Frontend — Example Result](./plan-new-frontend-example-result.md).

### Validate the Frontend Plan

In Step 3, the orchestrator invokes `frontend-plan-validator` with `specification_path` and the complete `frontend_plan`. The validator independently reads the original specification, applicable design rules, and referenced prototypes. It checks requirement coverage, layouts, pages, routes/access, components, ownership and flat project structure, dependencies, and build order. The planning skill retains its internal checks; the orchestrator does not repeat the validator's detailed review.

The validator returns `status`, actionable `errors`, non-blocking `warnings`, and the unchanged `validated_plan` only when valid. A valid result with no errors allows Step 4 to establish structure using that validated plan. Warnings remain visible to downstream work and the final report.

For an invalid result, the orchestrator sends the original specification path, rejected plan, and actionable errors to `plan-new-frontend`, then validates the complete corrected plan again. Allow at most two correction attempts after the initial validation (three validator invocations total). If errors remain, stop and report a blocker with remaining errors and required resolution. Stop earlier for missing sources, required user decisions, or failed/malformed validator results. Never proceed with an invalid plan or reset the retry limit to bypass unresolved errors. Later plan revisions require independent validation again.

### Select and Execute Implementation Skills

The planning skill returns the planned work, dependencies, and Build Order. The orchestrator selects the necessary implementation skills from its available skills, including Component Builder and Page Builder when applicable, and passes each its relevant requirements.

Plan validation returns incomplete or contradictory requirements to the planning skill for correction. Skill availability and execution coverage are checked by the orchestrator; missing skills are execution blockers, not a request for a Required Skills section in the frontend plan.
