# Name
frontend-page-builder-debug

# Description
Build validated Vue pages selected by page-specific debug descriptions after their required debug layouts and components are ready.

# Instructions

## Migrated contract

## Frontend Page Builder Debug

## Purpose

Implement isolated debug pages from the page portion of a validated frontend plan.

This skill runs after Frontend Component Builder Debug and Frontend Layout Builder Debug. It composes existing debug layouts and components and never generates or repairs a missing dependency.

## Input

Receive:

- `page_plan`: the complete validated page entries from the frontend plan;
- the resolved authoritative frontend specification;
- the Frontend Component Builder Debug result;
- the Frontend Layout Builder Debug result.
- the Google Auth Service Debug result when the selected Login page requires its local Google example.

Each page entry must preserve its canonical page name, route, access rules, responsibility, required layout and components, states, data and interaction requirements, dependencies, approved structure, and declared design references.

Do not accept an unvalidated plan. Do not reinterpret component or layout assignments. Consult service, store, and integration sections only where a validated page entry explicitly requires them.

## Fixed Debug Context

- Debug Additional Description and Functionality: `docs/frontend/page_additional-functionality-debug/`
- Existing debug components: `source/debug/frontend/src/components/`
- Existing debug layouts: `source/debug/frontend/src/layouts/`
- Page output: `source/debug/frontend/src/pages/`
- Debug-only routing: `source/debug/frontend/src/router/`
- Scenario output: `source/debug/frontend/src/scenarios/`
- Test output: `source/debug/frontend/tests/`

These paths are owned by this skill and are not caller inputs. Never write to production frontend paths.

## 1. Select Debug Pages

1. Read repository-root `.caisa/CAISA.md` and inspect existing debug pages, routes, layouts, components, scenarios, mocks, and tests.
2. Enumerate direct `.md` files in the Additional Description and Functionality directory in sorted filename order.
3. Read every file completely. Its first level-one Markdown heading is the canonical page name.
4. Find an exact page-name match in `page_plan` and verify that the page is defined in the authoritative page specification.
5. If matched, attach the complete Markdown file to the page entry as Additional Description and Functionality.
6. If the heading is missing, ambiguous, or unmatched, report the file and do not implement it.
7. If additional instructions directly contradict the validated page entry or source priority, report the page as blocked; do not rewrite the plan or invent a resolution.
8. Process matched pages sequentially, completing one page before starting the next.

Do not implement pages without a matching Additional Description and Functionality file. Never combine separate files into one assignment or apply a file to another page.

If no direct `.md` files exist, report that there are no debug page assignments and stop without implementation.

## 2. Verify Layout and Component Dependencies

For every selected page, inspect its merged validated entry and determine its required layout and mandatory components.

Require the Frontend Layout Builder Debug result to mark the page's layout as ready. Then verify the layout Vue source directly under the debug layout directory. Also verify every mandatory component as usable Vue source under the debug component directory.

If the layout is blocked, missing, or incompatible, block the page and report its canonical layout name and expected path. If a mandatory component is missing or incompatible, block the page and report its exact name and expected path.

For the local Google example, require the Google Auth Service Debug result to confirm a usable service before wiring the Login page. The page owns the service instance and the backend-example callback; it does not generate a mock credential itself.

Do not create, replace, repair, copy, or mock a missing layout or component. Independent pages whose dependencies are complete may continue.

## 3. Define the Page Interface

Define the smallest page-level contract supported by the merged page entry:

- route path, route name, layout, and access expectations;
- layout slots and documented layout events;
- component imports and their documented props, events, and slots;
- page-owned composition, reactive state, data population, and event handling;
- loading, empty, success, error, and navigation states where required;
- mock boundaries for external services and backend dependencies.

Respect existing layout and component interfaces. Do not change their props, emits, slots, or source code to accommodate the page. Keep backend authority and production integration outside the debug page.

## 4. Implement the Page and Debug Routes

Use Vue single-file components and the project's approved frontend language and conventions. Follow the validated page composition and its declared design and interaction references.

Write only to fixed debug page, router, scenario, mock, and test paths. Wrap each page with its required verified debug layout, supply page content through the documented layout slot, import existing debug components, implement page-owned state and interactions, and register the documented route in the isolated debug router.

Preserve unrelated debug routes and pages. Report route collisions rather than silently overriding them. Do not implement production authentication, authorization, payments, inference, or backend services. Use explicit debug mocks where required.

Never modify production frontend files, layout or component implementations, prototypes, production Vite configuration, or `.codex/`.

## 5. Interaction, Accessibility, and Cleanup

Apply relevant merged requirements: semantic structure, page titles and headings, keyboard navigation, focus management, responsive layout, loading and error states, form and component event coordination, and reduced-motion behavior.

Dispose of page-owned listeners, subscriptions, timers, provider adapters, and other resources when unmounted.

## 6. Scenarios and Tests

Register each implemented page with a stable kebab-case slug and its debug route. Preserve unrelated scenarios.

Add meaningful tests for page composition, required layout use, page-content slot placement, routing, event wiring, mock success and failure, accessibility, and responsive behavior.

Do not start Vite or run package-level test and build commands. Vite Dev Environment owns those actions after this skill returns.

## Output

Return:

- Additional Description and Functionality files discovered in processing order;
- each file's page heading and whether it matched `page_plan`;
- pages created, updated, reused, blocked, or skipped;
- required layouts and components found and exact missing dependencies;
- changed page, route, scenario, mock, and test paths;
- page contracts, routes, layout use, and relevant integration notes;
- stable page slugs and debug routes for Vite Dev Environment;
- checks performed and unresolved blockers.

Mark the debug page build complete only when selected pages, routes, scenarios, and tests are ready for Vite verification. Do not claim the preview is running or URLs are verified until the Vite skill confirms them.
