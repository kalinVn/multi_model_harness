## Available Agents

None

## Available Skills

- .caisa/skills/frontend-plan-validator.md
- .caisa/skills/frontend-component-builder-debug.md
- .caisa/skills/frontend-layout-builder-debug.md
- .caisa/skills/google-auth-service-debug.md
- .caisa/skills/frontend-page-builder-debug.md
- .caisa/skills/vite-dev-environment.md

## Available Rules

- .caisa/CAISA.md

## Available Documents

- docs/frontend/frontend.md
- docs/frontend/plan/new-frontend-plan.md

# Name
frontend_debug_page_builder_upgrade

# Description
Incrementally upgrade the existing isolated debug frontend from its validated plan and debug Additional Description and Functionality assignments.

# Tools
read_file, list_directory, write_file, bash

# Invocation
execute command frontend_debug_page_builder_upgrade

# Instructions
## Frontend Debug Page Builder Upgrade

## Purpose

Incrementally extend the existing frontend under `source/debug/frontend/` without deleting or rebuilding the complete debug workspace.

This command starts from the already-created canonical frontend plan, discovers component, layout, and page debug assignments, merges each matched Additional Description and Functionality file into its existing plan entry for the current run, and creates, updates, or reuses only the required debug artifacts.

The command is debug-only. It never upgrades or writes to the production frontend.

## Fixed Context

- Authoritative specification: `docs/frontend/frontend.md`
- Existing validated plan: `docs/frontend/plan/new-frontend-plan.md`
- Component assignments: `docs/frontend/component_additional-functionality/`
- Layout assignments: `docs/frontend/layout_additional-functionality/`
- Page assignments: `docs/frontend/page_additional-functionality-debug/`
- Existing debug workspace: `source/debug/frontend/`

These paths are resolved from the repository root and are not caller-selected deletion or production targets.

## Preconditions

1. Read repository-root `.caisa/CAISA.md`.
2. Require the authoritative specification, canonical plan, and existing debug workspace to be present and readable.
3. Reject a debug root outside `<repository-root>/source/debug/frontend`, a symlinked debug root, or an unresolved repository root.
4. Read the complete existing plan. Do not invoke the new-frontend planner and do not regenerate, correct, or overwrite the plan.
5. Pass the unchanged plan and authoritative specification to `.caisa/skills/frontend-plan-validator.md` for one read-only validation. Continue only when it returns the same plan with no validation errors. Preserve warnings. If the plan is stale or invalid, stop and report that planning must be rerun separately.
6. Inspect the existing debug components, layouts, pages, routes, scenarios, mocks, tests, package files, and server metadata before invoking builders. Preserve unrelated work and existing working behavior.

## Assignment Matching

For each component, layout, and page assignment directory:

1. Enumerate only direct `.md` files in sorted filename order.
2. Read every file completely.
3. Treat its first level-one Markdown heading as the canonical assignment name.
4. Find an exact canonical-name match in the corresponding complete validated plan section.
5. Attach the complete Markdown assignment to that plan entry as Additional Description and Functionality for this run only.
6. Report a missing, ambiguous, duplicate, or unmatched heading and do not build that assignment.
7. Report direct conflicts with the validated plan or source priority as blockers; never invent a resolution or rewrite the plan.

The existence of an assignment file does not create a new plan entry. An entry in the plan without a matching assignment file is not selected for this debug upgrade.

## Workflow

1. Extract the complete shared-component and feature-component entries as `component_plan`, the complete layout entries as `layout_plan`, and the complete page entries as `page_plan`. Preserve every selected plan entry unchanged before its matched Additional Description and Functionality is attached by the owning builder.
2. Invoke `.caisa/skills/frontend-component-builder-debug.md` once with only `component_plan`. It must inspect the existing debug workspace and classify every matched component as created, updated, reused, blocked, or skipped. Preserve its report.
3. Invoke `.caisa/skills/frontend-layout-builder-debug.md` once with `layout_plan`, the authoritative specification, and the Component Builder Debug result. It must reuse a compatible existing layout and create or update only matched debug layouts. Preserve its report and do not continue with pages whose required layout is blocked.
4. When a matched Login Page assignment requires the local Google handoff, invoke `.caisa/skills/google-auth-service-debug.md` with the Login page entry and its verified component dependencies. Otherwise record this stage as not applicable.
5. Invoke `.caisa/skills/frontend-page-builder-debug.md` once with the complete `page_plan`, the authoritative specification, the Component Builder Debug result, the Layout Builder Debug result, and any Google Auth Service Debug result. The page builder must inspect every direct page assignment, match it by exact page name, reuse a compatible existing debug page, and create or update a page only when its matched assignment requires it.
6. Preserve existing unrelated debug routes, pages, components, layouts, scenarios, mocks, and tests. Report route or scenario collisions instead of overwriting another assignment.
7. Pass all component, layout, and page slugs and page routes returned by the builders to `.caisa/skills/vite-dev-environment.md` with `debug_root: source/debug/frontend/`. Request dependency reuse or preparation, tests, build, one interactive preview, health verification, and verification of every returned debug URL and documented local example API flow. Preserve and reuse a healthy owned Vite process when the upgrade changes only client source handled by Vite HMR. When the upgrade changes Vite configuration, server middleware, server-only fixtures, package or lock files, or other startup-time infrastructure, restart only the process proven by command, root, metadata, and health marker to belong to this debug workspace, then replace `.vite/debug-server.json` with the new verified PID, root, origin, and start time. If no owned process is running, start one without deleting unrelated metadata or processes.
8. Return one consolidated report containing plan-validation status and warnings, discovered assignment files and exact-name matches, created/updated/reused/blocked/skipped artifacts, dependency gates, changed debug paths, test and build results, verified URLs, and unresolved blockers.

## Incremental Upgrade Rules

- Never remove or recreate the complete `source/debug/frontend/` directory.
- Never run the clean-rebuild step from `frontend_debug_page_builder`.
- Never copy an existing production page into the debug workspace.
- Never create a page, layout, or component that is absent from the validated plan or lacks a matching Additional Description and Functionality file.
- Reuse an existing debug artifact only after verifying its source and public interface against the merged assignment.
- Update an existing debug artifact only when the matched assignment requires a supported change.
- Create an artifact only when it is selected, missing, and all required earlier-stage dependencies are ready.
- Process components before layouts and layouts before pages.
- A missing or incompatible dependency blocks only its dependent assignments; independent assignments may continue.
- Keep the workflow idempotent: a second run with unchanged inputs must reuse the verified artifacts instead of duplicating routes, scenarios, tests, or source files.
- Preserve `.vite/debug-server.json` while its recorded process is healthy and owned by this debug workspace. Rewrite it only after an owned restart, a new owned server start, or proof that the existing metadata is stale.

## Safety Boundary

- Write only inside `source/debug/frontend/` during command execution.
- Do not modify `frontend/`, `admin/`, `backend/`, prototypes, specifications, plan files, Additional Description and Functionality files, `.codex/`, or `claude/`.
- Do not install or change production dependencies.
- Do not implement production authentication, authorization, payments, persistence, inference, coaching, or backend services.
- Use only documented loopback debug mocks and keep fixture credentials, codes, and tokens out of browser bundles, logs, URLs, and storage.
- Do not stop or reuse a Vite process unless its command, working root, metadata, and health response prove that it belongs to the canonical debug workspace.
- Do not commit, push, deploy, or modify infrastructure as part of this command.

## Completion Condition

The upgrade is complete only when every matched, unblocked assignment is created, updated, or verified as reusable; the debug tests and build pass; the preview health check succeeds; and every returned component, layout, page, and example-API URL is verified.

If no new or changed assignment requires implementation, still verify the reusable artifacts and report a successful no-op upgrade rather than rewriting them.
