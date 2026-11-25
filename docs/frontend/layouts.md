## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/feature-components.md
- docs/frontend/frontend.md
- docs/frontend/shared-ui-components.md
- docs/frontend/integration-contracts.md

## Required Layouts

### Public Layout

The Public Layout is the reusable shell for public pages. It composes the [TopNav Feature Component](feature-components.md#topnav), the [Footer Feature Component](feature-components.md#footer), and an empty responsive page-content area. Page-specific sections, cards, promotional content, and authentication forms belong to pages or components rather than the layout.

Public Layout owns the composition and population of its shell components. It supplies TopNav with the approved public navigation items from [Navigation Requirements](frontend.md#navigation-requirements), marks the active public destination, and handles TopNav's Login and Register actions through routing. It supplies Footer with the approved copyright and public footer actions and forwards legal/consent actions to the global consent feature. TopNav and Footer remain presentational and do not read route, authentication, or consent state directly.

Authoritative prototype: `prototypes/design/layouts/public.html`.

### Global Consent Placement

The cookie/privacy feature is global application UI, not Home page content and not a replacement for the footer. The repository's prototypes are multi-page HTML rather than one Vue root above both layout families, so the shared `app.js` shell loads the feature-local [mount adapter](../../prototypes/components/features/CookiePrivacyPolicy/mountCookiePrivacyPolicy.js) on every application page. That adapter mounts `PrivacyChoicesBanner` and `CookiePrivacyPolicy` as independent roots that consume the same shared `useCookieConsent` state. Individual pages do not own or duplicate their logic. A future routed application with a single root should mount both components once above both layouts without making either component the parent of the other.

The banner directly calls `useCookieConsent` and stays full-width at the viewport bottom until Accept All, Reject All, or Save Preferences writes the versioned `localStorage` record. `CookiePrivacyPolicy` watches the same composable's active modal state and uses one reusable `BaseModal` for preferences and both policy views through reusable `PolicyContent`. Legal actions use `TextButton` through the Footer in both layout families. Cookie Settings therefore remains available after consent and reopens saved values without showing the initial banner. Consent enforcement, tracking-provider initialization, legal approval, and backend storage remain outside the prototype scope.

### Authentication Layout

The Authentication Layout is the reusable shell for authenticated pages, including Training, Subscription, and Checkout. It composes the [SidebarNav Feature Component](feature-components.md#sidebarnav), the [LayoutHeader Shared Component](shared-ui-components.md#layoutheader), the [Footer Feature Component](feature-components.md#footer), and an empty responsive page-content area. In the main layout column, LayoutHeader remains at the top, the active page renders in the middle content area, and Footer remains at the bottom. Dashboard, Training, History, Session Review, Subscription, Profile, Settings, and Checkout render their page-specific UI inside that content area.

Authentication Layout owns the composition and population of its shell components. It supplies SidebarNav with Dashboard, Training, History, Subscription, Profile, Settings, and Checkout, including the active item derived from the current route. It supplies LayoutHeader with the current page name and authenticated user's display name. It handles LayoutHeader's `logout` event through the authoritative authentication flow; LayoutHeader never ends the session itself. It supplies Footer with the approved copyright and legal/support actions and forwards consent and policy actions to the global consent feature. Footer remains presentational and does not read route, authentication, or consent state directly. Session Review remains reachable from History and Dashboard session rows rather than becoming a persistent SidebarNav item.

Authoritative prototype: `prototypes/design/layouts/authentication.html`.

For navigation items, appearance, and responsive states, `prototypes/design/components/navigation/authenticated-navigation.html` remains authoritative over the embedded navigation in this layout, as specified in [Navigation Requirements](frontend.md#navigation-requirements).

Training and every other authenticated page use this same shell; no page-specific layout is defined. Training-specific camera, coaching, status, controls, and session UI belong to the Training page and its components, not to a reusable layout.

Authentication forms may still be presented through the public login/registration interaction. Their session behavior must preserve a validated internal return target, close only after a confirmed result or explicit cancellation, and expose pending, validation, error, second-factor, and expired-session states as described in [integration contract examples](integration-contracts.md#authentication-and-application-session).

---
