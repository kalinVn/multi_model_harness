# Name
plan-new-frontend

# Description
Produce a complete source-backed frontend plan for a genuinely new frontend before any frontend code is created.

# Instructions

## Source: `.codex/skill-adapters/plan-new-frontend/SKILL.md`

## Plan New Frontend

Read repository-root `.caisa/skills/rule-frontend-planning.md`, then execute the complete adapted planner contract in repository-root `.caisa/skills/plan-new-frontend.md` with the user's explicit `specification_path`.

Do not substitute a default specification, implement code, select builder skills, or proceed from unresolved blockers. Return the complete plan for independent validation.

## Source: `.codex/skills/plan-new-frontend.md`

## Plan New Frontend

> Codex adaptation of `claude/skills/plan-new-frontend.md`. Used as a planning role/reference, not an automatically discovered standalone skill. Read `.caisa/skills/rule-frontend-planning.md` before applying it.

## Purpose

Analyze the provided frontend specification and all authoritative references it declares to determine the complete scope of the new frontend implementation.

Produce a complete structured frontend plan that defines the required shared and feature components, pages and routes, data and state ownership, contracts and integrations, dependencies, project structure and file placement, blockers, and implementation order.

Provide the Frontend Orchestrator with the planning information required to coordinate the specialized frontend implementation skills.

---

## Skill Rules

Read and follow:

`.caisa/skills/rule-frontend-planning.md`

---

## Input

Receive `specification_path` from the Frontend Orchestrator. Resolve it from the project root and read it as the root frontend specification and owner of the authoritative reference graph. If the path is missing, unreadable, or cannot be resolved, report it to the orchestrator and stop; do not substitute another specification.

---

## Execution Workflow

## Step 1 — Read the Frontend Specification and Its References

Identify all authoritative specifications it declares and read them. Follow additional referenced prototypes or examples only for aspects assigned by those specifications. Respect the source-priority rules declared in the root frontend specification. Use the project sources it declares; Step 2 names its component source for clarity. If a required source is missing, ownership is ambiguous, a reference is broken, or the conflict cannot be resolved by those rules, report it as a blocker and do not invent a replacement requirement.

For visual references, resolve and verify each declared path and record its owning page, layout, component, or state. Do not inspect detailed prototype UI implementation during planning. The narrow structural-inspection exception in Step 4 applies only to organization and ownership examples.

---

## Step 2 — Build the Components Plan

Plan Shared UI Components and Feature Components separately. For every required standalone component declared by the authoritative frontend specifications, read its complete section and declared references. Preserve its documented ownership boundaries and create a separate entry for the Component Builder. A named child documented only through its owning feature or page remains part of that owner's entry; do not require a separate section or plan entry for it. Do not infer additional components from generic examples.

Keep every field in the relevant structure below. Write `None` when the authoritative section does not define a value or reference category; `None` does not resolve a missing required description or reference for a standalone component that prevents planning. Report that as a blocker. Do not invent props, states, events, behavior, endpoints, contracts, or references. Record exact prototype paths from the owning component specification. During this debug planning workflow, verify and map prototype references without detailed prototype UI implementation analysis.

### 2.1 Shared UI Components

Read each required shared component in `docs/frontend/shared-ui-components.md`. Read a feature component's section when the shared component explicitly references it. Capture all documented props, defaults, states, emitted events, slots, parent-owned actions, behavior, accessibility, visual requirements, data flow, dependencies, and file grouping in this structure:

```yaml
Component name:
Source specification:
Source section:
Description:
Component functionality:
Props and defaults:
UI states:
Data flow:
Emits and ownership:
Slots and content:
Behavior and accessibility:
Visual requirements:
Prototype References:
  Design Prototypes:
  Vue Components:
  Other declared references:
Dependencies:
File grouping and placement:
Blockers:
```

### 2.2 Feature Components

Read each required feature component in `docs/frontend/feature-components.md` and the shared components it explicitly composes. Capture its documented functionality, properties, state and data flow, ownership, composed components, visual and accessibility requirements, dependencies, and file grouping in this structure:

```yaml
Component name:
Source specification:
Source section:
Description:
Component functionality:
Component properties and data flow:
  Props, events, and slots:
  Local UI state:
  Data source and ownership:
  Parent and child data flow:
UI states and behavior:
Visual and accessibility requirements:
Prototype References:
  Design Prototypes:
  Vue Components:
  Other declared references:
Dependencies and composed components:
File grouping and placement:
Blockers:
```

Pass complete component entries to the Component Builder as the planning input. `Additional Descriptions` for a Shared UI Component are optional later build-time input, not generated or stored in the Components Plan. When absent, use the persistent component specification and normal source priority. Report missing required sources, unresolved conflicts, or missing descriptions/dependencies for required standalone components as blockers; do not move backend-owned logic into components.

---

## Step 3 — Build the Pages, Routes, and Layouts Plan

Read the authoritative pages-and-routes specification and the authoritative layout specification declared by the root frontend specification.

Read the complete section for every planned page and every relevant layout.

Follow references declared by those sections when required to understand the page, route, layout, state, data source, integration, or visual result. For pages, resolve and record declared design prototype paths without analyzing their detailed UI implementation in this planning step.

### 3.1 Layouts

For each layout, record:

```text
Layout:
Source: exact layout section in the authoritative layout specification
Pages using layout:
Navigation:
Design / prototype references:
Blockers:
```

Analyze referenced layout/navigation design prototypes when they are declared.

Do not place page-specific business logic in the layout unless an authoritative specification explicitly assigns it there.

### 3.2 Pages and Routes

For every page, create one plan entry containing:

```text
Page:
Purpose:
Route:
Route name:
Access:
Route parameters:
Layout:
Navigation behavior:
Required shared components:
Required feature components:
Design prototype references:
Description / page requirements:
Data source and ownership:
Services:
Integration contracts and page responsibility:
States:
Workflows / functional requirements:
Dependencies:
Blockers:
```

Every shared component referenced by a page must exist in the Shared UI Components plan. Every feature component referenced by a page must exist in the Feature Components plan. If a required component is absent, add a blocker naming the page, missing component, and source instead of inventing it.

For each page, identify where its data comes from and whether the page, a component, or a shared store owns loading and updates. Do not assign the same data load to multiple owners.

Read the relevant integration contracts. For each contract that affects a page, record its exact section and the page's responsibility. Do not duplicate endpoint details or assign an operation to a page when another unit owns it.

For larger workflows such as authentication, training, live analysis, checkout, or session review, record the authoritative workflow source and only the page's responsibility within it.

---

## Step 4 — Resolve Project Structure

After planning the components, pages, routes, and layouts, read the `Project Structure` section of the root frontend specification and the authoritative structure references it names.

Inspect the existing `prototypes/` directory for examples of how related implementation files are grouped, excluding `prototypes/design/`, `prototypes/dist/`, and generated dependencies such as `prototypes/node_modules/`. Use these examples to inform grouping, not to override the authoritative production structure or copy prototype folders blindly.

For each planned implementation unit, specify its production file placement and any necessary grouping of related files according to the authoritative structure. Do not invent directories or layers, create placeholder files, or implement the frontend in this step.

---

## Step 5 — Open Questions and Blockers

Return an empty list when there are no unresolved issues. Otherwise, for every issue include:

```text
question_or_missing_information:
source:
affected_plan_items:
implementation_impact:
blocking:
required_resolution:
```

Create blockers for unresolved missing sources or sections, required pages or components, required prototypes, ownership conflicts, data-population ownership, integration contracts, and conflicting authoritative requirements. Do not convert blockers into assumptions or mark blocked work as implementation-ready.

---

## Step 6 — Build Order

Return a dependency-aware implementation order derived from the resolved plan rather than a hardcoded project-specific list.

At minimum, establish project structure before implementation files; build shared UI before its consumers; build feature components and layouts before dependent pages; establish shared stores, services, and integration foundations before consumers; configure routes after pages, layouts, and access requirements are known; and perform responsive, accessibility, test, and verification work after the units it validates.

Return each phase with concrete planned items where possible:

```text
Phase:
Items:
Depends on:
Unblocks:
Reason:
```

Do not return generic counts as a substitute for implementation order.

---



## Output Contract

Return one complete structured frontend plan to the Frontend Orchestrator.

The plan must contain, in this order:

```text
1. Frontend Type
2. Planning Sources
3. Shared UI Components
4. Feature Components
5. Layouts
6. Pages and Routes
7. Project Structure
8. Open Questions and Blockers
9. Build Order
```

The Frontend Type, Planning Sources, Project Structure, Open Questions and Blockers, and Build Order sections must always be present.

## Frontend Type

```text
new
```

## Planning Sources

Record the root frontend specification and the authoritative supporting sources actually used to produce the plan. Do not list implementation skills or unrelated files.

## Project Structure

Read the `Project Structure` section in the root frontend specification. Collect every frontend project-structure document referenced there and use those referenced files as the authority for frontend placement and organization. Do not hardcode the authoritative structure-document list in this planning role; the root specification owns that navigation and may change it.

Use the resolved references to determine placement for pages, reusable components, simple and complex component support files, composables, Pinia stores, services, routing, layouts, styles, assets, utilities, configuration, and other shared frontend resources. Do not introduce a frontend `modules/` feature-root layer. This frontend rule does not alter backend module organization.

When the Project Structure section points to prototype directories or examples, inspect only their organization and ownership patterns. Complex examples may show a Vue component with supporting JavaScript files or classes, controller/lifecycle logic, rendering or animation logic, configuration, component-specific styles, tests, or documentation. Use those examples only when the planned component has comparable complexity; a simple component may remain a single `.vue` file. Do not treat prototype-local assets or global styles as authority over the referenced production structure, and do not use structural inspection to infer detailed UI requirements.

Record only plan-specific ownership, supporting files, and concrete placement needed to make implementation unambiguous. Do not reproduce the referenced directory trees or general rules, copy example structures blindly, invent architectural layers, or create placeholder files. If a requirement conflicts with an authoritative structure reference, report it as a blocker instead of defining an alternative.

Return the resolved project-structure requirements as part of the plan. The orchestrator passes the validated plan and resolved references to downstream implementation work; this planning role creates neither directories nor implementation files.



Use the Step 5 blocker structure and Step 6 dependency-aware phase structure for the final two sections.

---

## Important Boundary

This skill produces the complete frontend plan. The Frontend Orchestrator owns implementation-skill selection and execution.

It does not:

- build final pages
- build final layouts
- build final reusable components
- configure final routing
- implement stores or services
- implement backend APIs
- perform Vision inference
- implement payment server logic

Those responsibilities belong to specialized skills coordinated by the Frontend Orchestrator.

---

## Validation

Before returning the plan, verify that every planned standalone component and page has an authoritative source; every page route/layout and component mapping is resolved; required references exist; data ownership is not duplicated; contracts are attached to the correct owner; structure follows authoritative rules; blockers are explicit; and Build Order respects dependencies.

If validation errors are returned, use them as correction context and return a complete corrected plan.

---

## Plan Output

For the normal new-frontend planning workflow, write the completed frontend plan to `docs/frontend/plan/new-frontend-plan.md`, creating `docs/frontend/plan/` when needed. Use that as the canonical output unless the invoking workflow explicitly defines another path.

When this role is invoked by `debug_frontend_plan`, its command contract intentionally overrides the normal destination: the coordinator writes the validated English report and Bulgarian translation only to the two debug output paths declared by that command. The planner role must not create the canonical plan file during a debug run.

---

## Final Rule

Read the root frontend specification and the references it declares. Plan the actual frontend implementation units and their relationships.

For each standalone component, page, and layout, make its authoritative source, references, ownership, dependencies, data/integration context, and required implementation result explicit.

Analyze referenced design prototypes for components and layouts only where their authoritative specifications assign them a role. For pages, record declared prototype references without analyzing detailed UI implementation during planning.

Resolve project structure only after the implementation units and ownership boundaries are known. Do not invent missing requirements.

Return one complete implementation-ready frontend plan to the planning coordinator. In `debug_frontend_plan`, implementation is outside scope even when the plan is valid.
