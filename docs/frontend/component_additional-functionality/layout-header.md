## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

None

# LayoutHeader

## Additional Description and Functionality

The active authenticated page supplies its documented page name to `LayoutStore.currentPageTitle` when that page becomes active. The value is page-owned layout context; it is not derived from the router, URL, component filename, visible heading text, or `UserStore`.

For this component build, `LayoutHeader` reads `LayoutStore.currentPageTitle` and the authenticated user's display name from `UserStore` directly. It must not require Authentication Layout to read those stores or pass `pageTitle` and `userName` props. This component-specific requirement overrides the conflicting prop-population boundary in the persistent component specification for this build only.

`LayoutHeader` does not derive the page name from the router and does not mutate either store. When the user activates Log out, it emits the existing `logout` event and Authentication Layout handles that event through the authoritative authentication flow.
