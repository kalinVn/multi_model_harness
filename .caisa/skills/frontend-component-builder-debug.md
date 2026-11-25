# Name
frontend-component-builder-debug

# Description
Build only validated Vue components selected by component-specific Markdown files for the isolated frontend debug workspace.

# Instructions

## Migrated contract

## Frontend Component Builder Debug

## Purpose

Implement isolated debug components from the component portion of a validated frontend plan.

This skill is the debug counterpart of Frontend Component Builder. It uses the same component-interface, implementation, accessibility, and verification standards, but selects only components that have an Additional Description and Functionality file.

## Input

Receive only `component_plan`: the complete validated shared-component and feature-component entries from the frontend plan.

Each entry must preserve the component name, responsibility, consumers, interface, states, design requirements, dependencies, approved structure, and declared references.

Do not accept an unvalidated plan. Do not use page, route, service, store, or integration sections as component assignments.

## Fixed Debug Context

- Additional Description and Functionality: `docs/frontend/component_additional-functionality/`
- Component output: `source/debug/frontend/src/components/`
- Scenario output: `source/debug/frontend/src/scenarios/`
- Test output: `source/debug/frontend/tests/`

These paths are owned by this skill and are not caller inputs.

## 1. Select Debug Components

1. Read repository-root `.caisa/CAISA.md` and inspect the existing isolated debug component code, scenarios, mocks, and tests.
2. Enumerate direct `.md` files in the Additional Description and Functionality directory in sorted filename order.
3. Read each file completely. Its first level-one Markdown heading is the component name.
4. Find an exact component-name match in `component_plan`.
5. If a match exists, attach the complete Markdown file to that component entry as `Additional Description and Functionality`.
6. If the heading is missing or the component is absent from `component_plan`, report the file as unmatched and do not implement it.
7. If the additional content directly contradicts the validated component entry, report that component as blocked instead of changing the plan or inventing a resolution.
8. Process matched files sequentially. Finish one component before starting the next.

Do not implement components from `component_plan` that have no Additional Description and Functionality file. Never combine separate files into one assignment or apply a file to another component.

If no direct `.md` files exist, report that there are no debug component assignments and stop without implementation.

## 2. Inspect the Assignment

For each selected component, inspect its merged plan entry, existing debug implementation, tokens, styles, direct dependencies, consumers, and declared references.

Reuse an existing debug component when it satisfies the assignment. Extend it when required and preserve existing scenarios. Create a component only when its name and responsibility exist in `component_plan`.

Report missing or contradictory requirements for the affected component. Do not repair or rewrite the validated plan.

## 3. Define the Component Interface

Define the smallest interface supported by the merged component entry:

- props and defaults for supplied data, variants, and states;
- emitted events for user actions;
- slots for caller-owned content when needed;
- internal presentation state and cleanup behavior.

Keep application decisions and parent-owned data outside the component. Implement only the variants and states required by the merged entry.

## 4. Implement the Component

Use Vue single-file components and the project's approved frontend language and conventions.

Write only to the fixed debug component, scenario, and test paths. Reuse design tokens, shared styles, existing primitives, and direct debug dependencies.

Use explicit debug mocks at browser-service and backend boundaries. Do not implement application services, authentication authority, payment processing, inference, coaching decisions, page routing, stores, or production integration.

Never modify production frontend files, prototypes, production Vite configuration, or `.codex/`.

## 5. Interaction and Accessibility

Apply all relevant merged requirements, including semantic controls, accessible names, keyboard operation, visible focus, field associations, validation messages, disabled and pending behavior, loading and error states, responsive sizing, and reduced-motion support.

Clean up component-owned listeners, timers, rendered provider containers, and other resources on disposal.

## 6. Scenarios and Tests

Register every implemented component with a stable kebab-case slug in the fixed scenario directory.

Add only supported scenarios for props, slots, emitted events, state, loading, disabled behavior, validation, success and failure mocks, keyboard behavior, and accessibility.

Create or update meaningful component tests in the fixed test directory. Do not start the Vite server or run package-level test and build commands; Vite Dev Environment owns those steps after this skill returns.

## Output

Return:

- Additional Description and Functionality files discovered in processing order;
- each file's component heading and whether it matched `component_plan`;
- components created, updated, reused, blocked, or skipped;
- changed component, scenario, mock, and test paths;
- public interfaces and relevant integration notes;
- stable component slugs for Vite Dev Environment;
- component checks performed and unresolved blockers.

Mark the debug component build complete when the selected implementations, scenarios, and tests are ready for Vite Dev Environment verification.
