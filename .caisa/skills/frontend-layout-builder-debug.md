# Name
frontend-layout-builder-debug

# Description
Build validated Vue layouts selected by layout-specific debug descriptions after their required debug components exist and before debug pages are built.

# Instructions

## Migrated contract

## Frontend Layout Builder Debug

## Purpose

Implement isolated debug layouts from the layout portion of a validated frontend plan.

This skill runs after Frontend Component Builder Debug and before Frontend Page Builder Debug. It composes existing debug components into layouts and never generates a missing component.

## Input

Receive:

- `layout_plan`: the complete validated layout entries from the frontend plan;
- the resolved authoritative frontend specification;
- the Frontend Component Builder Debug result.

Each layout entry must preserve its canonical name, responsibility, slots, composition, required shared and feature components, states, dependencies, approved structure, and declared design references.

Do not accept an unvalidated plan. Do not reinterpret component assignments or use page, route, service, store, or integration sections as independent layout assignments.

## Fixed Debug Context

- Additional Description and Functionality: `docs/frontend/layout_additional-functionality/`
- Existing debug components: `source/debug/frontend/src/components/`
- Layout output: `source/debug/frontend/src/layouts/`
- Scenario output: `source/debug/frontend/src/scenarios/`
- Test output: `source/debug/frontend/tests/`

These paths are owned by this skill and are not caller inputs. Never write to production frontend paths.

## 1. Select Debug Layouts

1. Read repository-root `.caisa/CAISA.md` and inspect existing debug layouts, components, scenarios, mocks, and tests.
2. Enumerate direct `.md` files in the Additional Description and Functionality directory in sorted filename order.
3. Read every file completely. Its first level-one Markdown heading is the canonical layout name.
4. Find an exact layout-name match in `layout_plan` and verify that the layout is defined in the authoritative layout specification.
5. If matched, attach the complete Markdown file to that layout entry as Additional Description and Functionality.
6. If the heading is missing, ambiguous, or unmatched, report the file and do not implement it.
7. If additional instructions directly contradict the validated layout entry or source priority, report the layout as blocked; do not rewrite the plan or invent a resolution.
8. Process matched layouts sequentially, completing one layout before starting the next.

Do not implement layouts without a matching Additional Description and Functionality file. Never combine separate files into one assignment or apply a file to another layout.

If no direct `.md` files exist, report that there are no debug layout assignments and stop without implementation.

## 2. Verify Component Dependencies

For every selected layout, derive its mandatory component list only from the merged validated layout entry. Typical dependencies may include `TopNav` and `Footer` for Public Layout, and `SidebarNav`, `LayoutHeader`, and `Footer` for Authentication Layout, but the validated entry is authoritative.

Verify each mandatory component as usable Vue source under the debug component directory. Check the filesystem and component interface directly; do not rely only on the component-builder report.

Classify every dependency as:

- found and interface-compatible;
- found but interface-incompatible;
- missing.

If any mandatory component is missing or incompatible, block only the affected layout and report the exact component name and expected path. Do not create, replace, copy, mock, or alter a component. Independent layouts whose dependencies are complete may continue.

## 3. Define the Layout Contract

For every unblocked layout, define the smallest contract supported by its merged entry:

- imported components and their documented props, events, and slots;
- layout-owned shell structure and responsive regions;
- page-content slot placement;
- layout-owned event forwarding and navigation coordination;
- data or store reads explicitly assigned to the layout;
- accessibility, focus, overflow, and responsive behavior;
- cleanup for layout-owned listeners or subscriptions.

Preserve component ownership. Do not move component-owned state or behavior into the layout and do not move page-owned behavior into the layout.

## 4. Implement the Layout

Use Vue single-file components and the project's approved frontend language and conventions. Follow the validated layout composition and its declared design references.

Write only to fixed debug layout, scenario, mock, and test paths. Reuse the verified debug components and preserve their public interfaces. Render the page-content slot exactly once in the documented region.

Reuse an existing debug layout when it already satisfies the assignment; extend it only when required. Preserve unrelated layouts, scenarios, and tests.

Do not implement pages, page routes, production authentication, backend services, or missing component behavior. Never modify production frontend files, component implementations, prototypes, production Vite configuration, or `.codex/` outside this skill's own maintained files.

## 5. Scenarios and Tests

Register every implemented layout with a stable kebab-case slug in the fixed scenario directory.

Add meaningful tests for:

- required component composition;
- page-content slot placement;
- documented props and event forwarding;
- responsive shell behavior;
- accessibility and keyboard behavior;
- dependency failure reporting where the existing test structure supports it.

Do not start Vite or run package-level test and build commands. Vite Dev Environment owns dependency preparation, execution, preview, health checks, and URL verification after the complete debug build workflow returns.

## 6. Gate Frontend Page Builder Debug

Return a layout result before any page builder is invoked.

The result is `ready` only when every layout required by the selected debug pages is either:

- implemented or updated successfully; or
- reused after its contract and dependencies were verified.

The result is `blocked` when a layout required by a selected page is missing, failed, or has a missing or incompatible mandatory component. A caller must not invoke Frontend Page Builder Debug for pages that require a blocked layout.

Pass the complete layout result to Frontend Page Builder Debug so it can verify that each selected page's required layout is ready. The page builder must still verify the layout source on disk and must not create or repair layouts itself.

## Output

Return:

- Additional Description and Functionality files discovered in processing order;
- each file's layout heading and whether it matched `layout_plan`;
- layouts created, updated, reused, blocked, or skipped;
- required components found, incompatible components, and exact missing dependencies;
- changed layout, scenario, mock, and test paths;
- layout contracts, slots, and event-forwarding notes;
- stable layout slugs for later Vite verification;
- the `ready` or `blocked` gate result for Frontend Page Builder Debug;
- checks performed and unresolved blockers.

Mark the debug layout build complete only when selected layouts, scenarios, and tests are ready for the next workflow step. Do not claim that pages, previews, or URLs are ready until their owning workflows confirm them.
