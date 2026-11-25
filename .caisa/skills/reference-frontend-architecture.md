# Name
reference-frontend-architecture

# Description
Use the existing architecture guidance as read-only context rather than copying six maintained documents into another tree:

# Instructions

## Migrated contract

## Frontend Architecture Context for Planning

Use the existing architecture guidance as read-only context rather than copying six maintained documents into another tree:

1. Read the architect entry point (`../../claude/skills/frontend-code-architect/frontend-code-architect.md`) and architecture rules (`../../claude/skills/frontend-code-architect/architecture-rules.md`) for responsibilities, dependency direction, narrow contracts, atomic APIs, and avoiding duplicate ownership or premature abstractions.
2. Read component/feature placement (`../../claude/skills/frontend-code-architect/frontend-structure-and-components.md`) together with the `Project Structure` section in `frontend.md` (`docs/frontend/frontend.md`) and every authoritative structure document it references. Preserve Cards/Fields prototype families as organizational evidence, related composables, separate application stores, and genuinely shared resources without redefining the physical structure or introducing a frontend `modules/` feature-root layer. Current authoritative component classification wins over prototype grouping: `BaseCard` is shared UI, while `BaseModal` is documented with feature components.
3. For resource-owning or asynchronous features, read lifecycle and ownership (`../../claude/skills/frontend-code-architect/lifecycle-and-ownership.md`): initialization/cancellation, idempotent cleanup, one authoritative state owner, distinct timeline/phase duration, completion ownership, and local/global failure policy.
4. Apply the review workflow (`../../claude/skills/frontend-code-architect/review-workflow.md`) at plan level: inspect similar systems when available, define feature boundaries, check dependencies/ownership/placement/CSS contracts/dead state, preserve behavior, and schedule meaningful validation. Do not perform its proposed implementation changes.
5. For complex playback/animation/rendering features, use prototype organization examples linked by `docs/frontend/frontend.md`, including the Home Page Video Slider when referenced there, to understand ownership of supporting files. Consult the architecture reference (`../../claude/skills/frontend-code-architect/reference-home-page-video-slider.md`) only when that additional lifecycle context is relevant. These are examples, not universal hierarchies or proof that every component needs multiple files. The historical review (`docs/code-improvements/home-page-video-slider.md`) is supporting evidence, not a replacement frontend plan.

Use these sources to make concrete placement, state/resource ownership, lifecycle, and dependency decisions inside the normal planner's Project Structure section. Cite the sources actually used. Do not invent additional classes, shared components, or architectural layers just to match an example; keep unspecified mandatory decisions visible as blockers.

Historical maps and examples must not reintroduce pages, routes, stores, services, or tests removed from the current specifications, including the removed Progress feature.
