# Name
frontend-plan-validator

# Description
Independently validate a proposed new-frontend plan against its original specification and authoritative references.

# Instructions

## Source: .codex/skill-adapters/frontend-plan-validator/SKILL.md

## Frontend Plan Validator

Use the read-only validator contract at repository-root `.caisa/skills/frontend-plan-validator.md`. Require both `specification_path` and the complete `frontend_plan`.

Read raw sources independently. Return the structured result without correcting the plan or editing files. A valid result must contain the exact unchanged submitted plan.

## Source: .codex/skills/frontend-plan-validator.md

## Frontend Plan Validator

> Codex adaptation of `claude/skills/frontend-plan-validator.md`. Used as a planning role/reference, not an automatically discovered standalone skill. Read `.caisa/skills/rule-frontend-planning.md` before applying it.

## Purpose

Independently validate a proposed frontend plan against its original sources before project structure or implementation begins. Return findings, not a corrected plan.

## Input

- `specification_path` — path to the original frontend specification; resolve relative paths from the project root.
- `frontend_plan` — the complete structured plan returned by Plan New Frontend, including any open questions.

Do not substitute a default specification, a saved example, or a previous plan for either input.

## Required Context and Rules

Read the supplied specification and its required referenced specifications and prototypes independently; do not rely on the plan's claims that they were inspected.

Read and apply:

- `../../claude/rules/frontend/frontend-design-system.md` — applicable design constraints and source precedence.
- `./plan-new-frontend.md` — Output Contract, not its self-validation verdict.
- `../../docs/frontend/frontend.md`, especially its `Project Structure` section, and every authoritative structure document referenced from that section; read only.

Respect active project instructions and explicit task requirements. For product and design decisions, the supplied specification takes priority over its prototype and shared design defaults, as documented in the planning skill and design rules. Do not promote example token values or optional patterns into mandatory requirements. If applicable sources contradict one another and no explicit precedence or override resolves the conflict, report an error citing both sources.

Resolve referenced resources using their documented path convention (repository-root paths from the project root, explicitly document-relative paths from the referring file). Missing, unreadable, or ambiguous required sources are validation errors. If required visual evidence cannot be inspected, report the limitation rather than claiming alignment. A prototype that is neither referenced nor required is not a missing requirement.

## Validation Workflow

### 1. Establish Requirement Coverage

Check that both inputs are usable and that the plan contains the information required by the planning skill's Output Contract. Accept equivalent structured representations; do not reject a complete plan solely for different heading names.

Map each applicable specification requirement to its plan section or item. Check both omissions and unsupported additions. An existing plan item is not proof that the specification requires it.

### 2. Check the Plan

- **Pages and layouts:** all required screens, sections, states, layouts, shared navigation, and content structure are represented; each page's layout exists and its consumers agree.
- **Routes and access:** paths, parameters, page/layout targets, public/protected access, redirects, unknown-route behavior, and navigation visibility match the specification. Visibility is not authorization. Detect duplicate or conflicting routes and dangling targets.
- **Components:** required shared patterns and feature components are covered, consumers resolve, responsibilities do not overlap unnecessarily, and variants, states, and data requirements are adequate. Do not demand components merely listed as examples in skills.
- **Ownership and project structure:** the plan resolves structure authority through `frontend.md` without copying it, and its concrete page/component ownership, support files, service boundaries, and state boundaries comply with every referenced structure source. Check relevant prototype organization examples only when `frontend.md` names them as structural guidance. Reject a frontend `modules/` feature-root layer, but do not apply that restriction to backend organization. Do not require placeholder folders or an alternative directory tree.
- **Design and prototypes:** the plan carries the applicable visual direction, reusable tokens, interaction states, responsive behavior and accessibility requirements from authoritative specifications and records the required prototype mappings. Do not require detailed prototype UI implementation analysis at planning time. Structural prototype inspection supports ownership and grouping only and is not rendered or pixel-level verification.
- **Dependencies and build order:** references resolve to planned work, existing verified resources, or explicitly identified external dependencies; prerequisites precede consumers and there are no cycles or contradictory ownership. Required integration, tests, and acceptance checks are scheduled. Missing implementation files are expected before building and are not themselves errors.
- **Missing requirements and boundaries:** cover all applicable functional and nonfunctional requirements, including frontend/backend responsibilities. Flag invented APIs or data, omitted acceptance criteria, unresolved mandatory decisions, and blockers that prevent safe execution.

Assess unresolved dependencies by impact. A documented external dependency may be a warning only if it does not prevent executing the plan and has explicit handling without fabricated functionality. Missing contracts or decisions required for planned implementation are errors even if the plan labels them non-blocking.

### 3. Classify and Return Findings

Errors block implementation: missing mandatory requirements, contradictions, broken references, invalid dependency order, unavailable required evidence, and unresolved blocking decisions. Warnings are non-blocking recommendations or deferred checks that do not violate a requirement.

Every finding must identify the affected plan section/item, the relevant requirement and its source location, the observed problem, and an actionable correction or recommendation. For missing inputs, cite this skill's Input section. For consistency errors, cite the applicable contract/convention and the conflicting plan entries. Do not invent source line numbers.

Return all independently verifiable findings in one pass. Do not claim checks passed when their sources could not be inspected.

## Output Contract

Return one structured result:

```text
status: valid | invalid
errors:
  - section: affected plan section or item
    requirement: applicable requirement
    source: source path and heading, selector, or verified line
    problem: observed mismatch or missing information
    action: specific correction or clarification needed
warnings:
  - section: affected plan section or item
    requirement: applicable requirement or recommendation
    source: source path and location
    problem: non-blocking concern
    action: recommended follow-up
validated_plan: complete unchanged input plan when valid; null when invalid
```

- `valid` requires all mandatory checks to be completed and `errors: []`. Warnings may remain.
- `invalid` requires at least one actionable error and `validated_plan: null`.
- Use empty lists when there are no findings of that category.
- A valid result returns the exact input plan without edits, omissions, normalization, or new requirements.

## Important Boundary

Do not modify the plan, specification, rules, prototypes, or application files. Do not select implementation skills, create architecture, run builders, or perform the correction loop. The orchestrator owns bounded retries; Plan New Frontend owns corrections.

The planning skill's internal checks remain useful but never replace this independent validation.

## Final Rule

Approve only a source-checked, complete and consistent plan. Otherwise return actionable errors and no validated plan.
