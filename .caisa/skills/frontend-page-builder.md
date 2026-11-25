# Name
frontend-page-builder

# Description
Create or update Vue route pages by composing approved layouts, shared components, feature components, and page-owned state.

# Instructions

## Migrated contract

## Frontend Page Builder

Read `../../../claude/skills/frontend-page-builder.md`, then use the validated plan or scoped update plus repository-root `docs/frontend/pages-and-routes.md`.

Before implementing an assigned page, look for a direct Markdown file in repository-root `docs/frontend/page_additional-functionality/` whose first `#` heading exactly matches the page's canonical name. When a matching file exists, read the complete file and merge its additional requirements with the validated page entry. A missing file does not create a page or expand the assignment. If the additional requirements conflict with the validated plan or an authoritative specification, report the conflict instead of inventing a resolution.

Inspect existing pages, routes, components, layouts, stores, and services first. Keep route views in `frontend/src/pages/`, keep page business coordination at page/store/service boundaries, and do not recreate shared patterns or unrelated logic. Update routing only when assigned.

Use TypeScript and run relevant page, routing, accessibility, responsive, and regression checks.
