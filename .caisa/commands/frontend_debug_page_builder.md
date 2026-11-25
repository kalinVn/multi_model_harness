## Available Agents

None

## Available Skills

- .caisa/skills/plan-new-frontend.md
- .caisa/skills/frontend-plan-validator.md
- .caisa/skills/frontend-component-builder-debug.md
- .caisa/skills/frontend-layout-builder-debug.md
- .caisa/skills/google-auth-service-debug.md
- .caisa/skills/frontend-page-builder-debug.md
- .caisa/skills/vite-dev-environment.md

## Available Rules

- .caisa/CAISA.md

## Available Documents

None

# Name
frontend_debug_page_builder

# Description
Clean, plan, validate, build, preview, and test selected frontend components, layouts, and pages in the isolated debug workspace.

# Tools
read_file, list_directory, write_file, bash

# Invocation
execute command frontend_debug_page_builder specification_path=<repository-relative path>

# Instructions
## Frontend Debug Page Builder

## Purpose

Coordinate planning, independent validation, clean debug-workspace initialization, component building, layout building, page building, and Vite verification under `source/debug/frontend/`.

This command coordinates the owning skills. It does not discover Additional Description and Functionality assignments, implement Vue code, or repair missing dependencies itself.

## Required Input

- `specification_path`, resolved from the repository root.

Do not substitute a default specification path.

## Workflow

1. Read repository-root `.caisa/CAISA.md`.
2. Invoke `.caisa/skills/plan-new-frontend.md` with the explicit `specification_path`.
3. Pass the complete plan and the same `specification_path` to `.caisa/skills/frontend-plan-validator.md`.
4. Use one initial validation and at most two corrected-plan validations. Continue only with an unchanged `validated_plan` and no validation errors. Preserve validator warnings.
5. Resolve the repository root and the canonical debug root. Continue only when the canonical target is exactly `<repository-root>/source/debug/frontend`. Reject a missing repository root, a target outside the repository, a symlinked target, or any broader path.
6. Before deletion, inspect `source/debug/frontend/.vite/debug-server.json` when present. Stop the recorded Vite process only after verifying that its live command and working root belong to the canonical debug root; never terminate a process based only on a PID or open port. Then remove the complete `source/debug/frontend/` directory when it exists and recreate only that empty directory. This is an intentional clean rebuild of disposable debug output. Report whether an owned Vite process was stopped and that the previous debug workspace was removed. Do not preserve old components, layouts, pages, routes, scenarios, tests, dependencies, build output, or server metadata.
7. Extract the complete shared-component and feature-component entries as `component_plan`, the complete layout entries as `layout_plan`, and the complete page entries as `page_plan`. Preserve the entries unchanged and keep the three plans separate.
8. Invoke `.caisa/skills/frontend-component-builder-debug.md` once with only `component_plan`. Preserve its report. A component is available only when the builder confirms successful creation or reuse in the new workspace.
9. Invoke `.caisa/skills/frontend-layout-builder-debug.md` once with `layout_plan`, the resolved specification, and the Component Builder Debug result. Preserve its report. Do not continue with a page whose required layout is blocked.
10. When the validated Login page is selected and its debug assignment requires the local Google handoff, invoke `.caisa/skills/google-auth-service-debug.md` with that page entry and its existing component dependencies. Keep its report separate; otherwise record this stage as not applicable.
11. Invoke `.caisa/skills/frontend-page-builder-debug.md` once with `page_plan`, the resolved specification, the Component Builder Debug result, the Layout Builder Debug result, and any Google Auth Service Debug result. Do not build the Login page if its required debug service is blocked.
12. Pass the returned component slugs, layout slugs, page slugs, and page routes to `.caisa/skills/vite-dev-environment.md` with `debug_root: source/debug/frontend/`. Request dependency preparation, tests, build, one interactive preview, health verification, and verification of every returned debug URL, including the documented local Google example-token handoff when applicable.
13. Return one consolidated report containing validation status and warnings, clean-workspace confirmation, component results, layout results, debug service results, page results, Vite results, verified URLs, and all blockers.

## Clean-Rebuild Safety Boundary

- The command may recursively remove only the canonical repository path `source/debug/frontend/`.
- Never accept the deletion target as caller input.
- Never remove `source/debug/`, `source/`, the repository root, a production frontend directory, prototypes, documentation, or any path outside the repository.
- Stop before deletion if canonical-path or symlink checks are inconclusive.
- Stop before deletion when plan validation fails.
- Never terminate an unverified or unrelated process. If metadata names a live process whose ownership cannot be verified, stop and report the blocker before deleting its workspace.
- The debug root is disposable output. Do not copy files from the old debug root into the clean rebuild.

## Build Boundaries

- Additional component, layout, and page assignments are owned by their respective builder skills.
- Do not build layouts before Component Builder Debug returns.
- Do not build pages before Layout Builder Debug returns.
- Do not generate missing components or layouts automatically to satisfy a later stage.
- Do not silently skip blocked assignments or invent undocumented requirements, routes, interactions, stores, endpoints, or prototypes.
- Do not modify production frontend files, prototypes, or `claude/`.
- Use only the validated plan and authoritative source-priority rules.
- Vite Dev Environment is the only stage that installs dependencies, runs package scripts, starts the preview, and verifies URLs.
