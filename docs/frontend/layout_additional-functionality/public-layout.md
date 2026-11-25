## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/layouts.md
- docs/frontend/frontend.md
- docs/frontend/feature-components.md

# Public Layout

## Additional Description and Functionality

Public Layout composes the existing `TopNav` and `Footer` feature components and the page-content slot. It must not duplicate their markup inside individual public pages.

Populate `TopNav` with the approved public navigation items, derive the active item from the current route, and handle its Login and Register actions through routing. Supply `Footer` with the approved copyright text and public legal/support actions. Forward consent and policy actions to the global consent feature rather than implementing modal or persistence behavior inside Footer.

Render the active public page only in the layout's page-content slot.

## References

- `docs/frontend/layouts.md`
- `docs/frontend/frontend.md#navigation-requirements`
- `docs/frontend/feature-components.md#footer`
- `docs/frontend/feature-components.md#topnav`
- `prototypes/design/layouts/public.html`
- `prototypes/design/components/navigation/public-navigation.html`
- `prototypes/design/components/footer/footer.html`
