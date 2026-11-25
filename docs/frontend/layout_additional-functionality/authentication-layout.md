# Authentication Layout

## Additional Description and Functionality

Authentication Layout composes the existing `SidebarNav` feature component, the shared `LayoutHeader`, the shared layout `Footer` feature component, and the page-content slot. It must not duplicate their markup inside individual authenticated pages.

Render `SidebarNav` without making Authentication Layout responsible for constructing its navigation items or deriving its active item. The component-specific additional requirements for `SidebarNav` own its read from `AuthenticatedNavigationStore`. Session Review is opened from a session row in Dashboard or History and is not a persistent sidebar item.

Render `LayoutHeader` without making Authentication Layout responsible for its page-title or user-name data. The component-specific additional requirements for `LayoutHeader` own its reads from `LayoutStore.currentPageTitle` and `UserStore`. Authentication Layout handles the header's `logout` event through the authoritative authentication flow.

Supply `Footer` with the approved copyright text and authenticated-layout legal/support actions. Forward consent and policy actions to the global consent feature rather than implementing modal or persistence behavior inside Footer.

Render `LayoutHeader` at the top of the main layout column, the active authenticated page only in the page-content slot, and `Footer` after that slot at the bottom of the main layout column.

## References

- `docs/frontend/layouts.md`
- `docs/frontend/frontend.md#navigation-requirements`
- `docs/frontend/shared-ui-components.md#layoutheader`
- `docs/frontend/feature-components.md#footer`
- `docs/frontend/feature-components.md#sidebarnav`
- `prototypes/design/layouts/authentication.html`
- `prototypes/design/components/navigation/authenticated-navigation.html`
- `prototypes/design/components/header.html`
- `prototypes/design/components/footer/footer.html`
