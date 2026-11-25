## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/shared-ui-components.md
- docs/frontend/feature-components.md
- docs/frontend/pages-and-routes.md
- docs/frontend/layouts.md
- docs/frontend/integration-contracts.md
- docs/frontend/frontend-project-structure.md

# Tennis AI Coach — Frontend Specification

## Purpose

Define what the Tennis AI Coach client application must contain and how users interact with it.

This document is the project-specific source of truth for frontend product scope. It describes required pages, layouts, routes, behavior, visual references, and acceptance criteria.

Application source belongs under `frontend/`.

---

## Source Priority

`frontend.md` is the root frontend specification and defines the authoritative source ownership for the frontend.

### Authoritative Specifications

#### `frontend.md`

Root frontend specification and owner of the authoritative reference graph.

Defines which project sources are authoritative for each frontend domain.

#### `shared-ui-components.md` and `feature-components.md`

Authoritative sources for:

- shared UI components in [shared-ui-components.md](shared-ui-components.md);
- feature components in [feature-components.md](feature-components.md);
- component responsibilities;
- component interfaces and ownership.

#### `pages-and-routes.md`

Authoritative source for:

- pages;
- routes;
- layouts;
- navigation;
- page-level requirements;
- page-to-component relationships.

#### `integration-contracts.md`

Authoritative source for:

- frontend/backend integration contracts;
- API endpoints;
- WebSocket communication;
- authentication;
- application data flows;
- training flows;
- checkout and payments;
- integration behavior.

#### Project Structure Specifications

Project-structure specifications referenced by `frontend.md` are authoritative for:

- production folder structure;
- file placement;
- file organization;
- structural conventions.

### Referenced Prototypes and Example Implementations

Referenced design prototypes and example implementations are supporting authoritative references only for the visual, structural, interaction, or implementation aspects explicitly assigned to them by the corresponding authoritative specification.

They do not independently redefine:

- functional requirements;
- ownership;
- integration contracts;
- application architecture.

### Shared Frontend Rules

Shared frontend rules define cross-cutting constraints, conventions, and standards.

They apply across the frontend but do not override explicit requirements from an authoritative domain specification unless the project documentation explicitly states otherwise.

### Conflict Resolution

When sources conflict:

1. Use `frontend.md` to determine source ownership.
2. Follow the authoritative specification for the affected domain.
3. Use explicitly referenced prototypes or examples only for the aspects assigned to them by that specification.
4. Apply shared frontend rules for cross-cutting constraints and defaults.

If a conflict cannot be resolved from the declared source ownership or precedence, report it as a blocker instead of inventing a requirement.

### Page Build Priority

A Page Builder may receive optional page-specific `Additional Description and Functionality`. It is a build-time instruction, not part of the persistent page specification, and has the highest priority only for the specific page build. It overrides only conflicting requirements; all non-conflicting persistent documentation and normal Source Priority and Conflict Resolution rules continue to apply.

Every visible page element, field, filter, control, action, and component must be explicitly supported by the page's authoritative specification, a component contract referenced by that specification, the page's declared design prototype, or the supplied page-specific `Additional Description and Functionality`.

Do not create a visible element or component that is absent from those sources. General wording such as controls, filters, surrounding elements, expected behavior, or common UI does not authorize inventing a concrete field, select, filter, action, state, wrapper, or component. Do not add an element merely because it would be conventional or useful for the page's data.

When page-specific `Additional Description and Functionality` is absent or empty, build the page strictly from its persistent specification, declared prototype, referenced component contracts, and the normal source-priority rules. If a required element cannot be resolved from those sources, report it as a blocker instead of inventing it. Never invent page-specific `Additional Description and Functionality`.

### Component Build Priority

A Component Builder may receive optional `Additional Descriptions` when building a Shared UI Component or optional `Additional Component Requirements` when building a Feature Component. Both are build-time instructions and are not part of the persistent component specification.

`Additional Descriptions` apply only to Shared UI Components.

`Additional Component Requirements` apply only to Feature Components. They are optional and are not required during the initial frontend planning stage. They may be added later, after the frontend plan and persistent Feature Component specification already exist, and supplied separately to the Component Builder for a specific component build. Do not automatically write them into [feature-components.md](feature-components.md).

`Additional Component Requirements` may describe additional UI elements, component composition, layout adjustments, behavior, actions, state requirements, or other build-specific requirements. For example, a planned Feature Component may already define its base form structure while build-time requirements add an upload control above the form, use a different footer composition, add labels, or include other page-specific elements for that build.

When either type of build-time instruction is supplied, it has the highest priority for that specific component build and overrides only conflicting requirements. All non-conflicting persistent documentation continues to apply, including:

- `Description`;
- `Component Functionality`;
- `Component Properties and Data Flow`;
- Prototype References;
- the normal Source Priority and Conflict Resolution rules.

When `Additional Descriptions` are absent or empty, build the Shared UI Component from its persistent specification and the normal source-priority rules. When `Additional Component Requirements` are absent or empty, build the Feature Component entirely from its persistent specification and the normal source-priority rules.

Never invent `Additional Descriptions` or `Additional Component Requirements`.

### Component Documentation Convention

Frontend component specifications use `### Component Properties and Data Flow` as their standard component-properties section. Keep it concise and include the applicable parts of:

1. accepted props, their types, and required/default values;
2. locally owned UI state;
3. the real source of externally supplied data;
4. the data path, normally `Store → Parent/Page → Feature Component props`;
5. values passed to child or shared components;
6. emitted events and slots;
7. parent/page ownership, store ownership, and responsibility boundaries.

When application state supplies a feature-component value, name the existing store and describe how the parent or page adapts and passes that value. Do not invent stores, let a presentational component read a store directly, or add endpoint payloads and backend integration details to an individual component specification unless the documented architecture explicitly requires them.

A child component named only within its owning feature or page is documented through that owner's section. It does not require a separate component section or standalone plan entry unless this specification explicitly lists it as a required standalone component.


----------------------


### Optional / Future

- Three.js / WebGL — 3D court, 3D skeleton and spatial visualizations
---

## Visual Prototype

Visual design prototype references are specified with their owners: pages in [pages-and-routes.md](pages-and-routes.md), shared UI components in [shared-ui-components.md](shared-ui-components.md), and feature components in [feature-components.md](feature-components.md).

Shared visual elements used across pages and layouts are referenced here. The [application background design prototype](../../prototypes/design/background.html) shows only the approved background, sourced from the shared prototype stylesheet. Read it alongside the page, layout, and component references when planning or building the frontend; apply that background globally rather than substituting the flat `--bg` fallback or duplicating it in every page. Other shared visual prototypes can be listed here as they are added.

Shared frontend design rules: [claude/rules/frontend/frontend-design-system.md](../../claude/rules/frontend/frontend-design-system.md).

---

## User Types

### Guest

May view the landing page, product features, login, and registration. Plan selection requires an authenticated application session.

### Authenticated User

May access Dashboard, Training, Session Review, History, Subscription, Checkout, Profile, and Settings.

### Subscriber

May access features enabled by the active plan. The frontend displays plan state but does not make protected billing decisions locally.

---

## Required Layouts

Defines the required frontend layouts and their existing structure.

The authoritative layout specification is [docs/frontend/layouts.md](layouts.md).

---

## Required Pages and Routes

Defines the required frontend pages, routes, and page-specific requirements.

The authoritative pages and routes specification is [docs/frontend/pages-and-routes.md](pages-and-routes.md). Example frontend/backend request and event shapes are in [docs/frontend/integration-contracts.md](integration-contracts.md); these proposals require backend confirmation before live integration. Training, authentication, subscription, and checkout feature requirements are specified with the relevant pages and cross-page flows there.

Its [Session Review](pages-and-routes.md#session-review) entry defines that route's access, parameters, navigation, and states. Proposed API examples are in [frontend integration contracts](integration-contracts.md); backend owners must confirm them before live integration.

---

## Navigation Requirements

- Public navigation links to relevant landing-page sections and authentication.
- Authenticated navigation exposes all required application pages.
- Public horizontal navigation is visible when the user is not authenticated and includes Home, Training, and Login; Start Free actions navigate to Register where present. It does not expose subscription or checkout destinations.
- Authenticated vertical navigation is visible when the user is authenticated and includes Dashboard, Training, History, Subscription, Profile, Settings, and Checkout.
- Session Review access is authenticated. History and Dashboard session rows open Session Review.
- Navigation remains usable with keyboard input and on mobile screens.

The visual sources of truth for shared navigation layouts and states are:

- Public: [public-navigation.html](../../prototypes/design/components/navigation/public-navigation.html)
- Authenticated: [authenticated-navigation.html](../../prototypes/design/components/navigation/authenticated-navigation.html)

These dedicated prototypes take precedence over navigation examples in older page and layout prototypes.
---

## Shared UI Requirements

Shared UI components are generic, reusable UI primitives used across pages and features.

The required shared components are:

- Badge
- Button
- DateField
- NumberField
- SelectField
- TextField
- BaseCard
- FormStatusMessage
- LayoutHeader
- StateLabel
- TextButton

Each shared visual pattern uses one reusable implementation across pages. Lightweight text actions are shared across features rather than reimplemented by individual pages. [shared-ui-components.md](shared-ui-components.md) is the authoritative source for generic shared component contracts, states, behavior, accessibility, styling, and prototype references.

---

## Feature Components

Feature components are project-, layout-, navigation-, page-, or feature-specific composed UI components, distinct from generic shared UI primitives.

[feature-components.md](feature-components.md) is the authoritative source for their contracts, ownership, and prototype references. Read it together with [shared-ui-components.md](shared-ui-components.md) when a feature composes shared UI.

- `BaseModal` — reusable modal shell with parent-owned content and close behavior; it remains distinct from the specialized full-screen camera modal.
- `Footer` — reusable footer shared by Public Layout and Authentication Layout, with parent-supplied copyright and legal/support actions.
- `TopNav` — public-layout navigation with parent-supplied links and authentication-page actions.
- `SidebarNav` — authenticated-layout navigation with parent-supplied application links and responsive drawer behavior.
- `BaseTable` — application table presentation for History and Training Sessions, with parent-owned data and formatting.
- `DashboardMetricCard` — presentational Dashboard statistic card receiving exactly `title`, preformatted `value`, and `footer`; Dashboard owns all values and comparisons, while `footer` selects plain text or the shared Badge treatment.
- `TennisBallSlider` — self-contained Training-page WebGL tennis-ball presentation with a Vue lifecycle shell and controller-owned mesh, animation loop, play/stop behavior, felt texture, curved seams, soft depth lighting, and opposite textured `PLAY` labels.
- `CollapseForm` — reusable page-specific collapsible form container for Profile, Settings, and any explicitly documented collapsible form sections.
- `PaymentCardPlan` — the Subscription feature's single plan-card component for option, selected, and current-plan states.
- `BillingDetailsCard` — the Subscription feature's focused billing-details presentation with a page-owned action.
- `HomePageInfoSection` — existing Home headline, description, CTA links and feature cards.
- `HomePageVideoSlider` — interactive Home video and illustrative AI tennis-analysis preview.
- `RecaptchaField` — authentication verification-field presentation used by LoginForm and RegisterForm, with backend-owned production verification.
- `SocialAuthButton` — one provider-specific authentication action with parent-owned OAuth behavior and error handling.
- `LoginForm` — dedicated Login form UI using the RecaptchaField and SocialAuthButtons Feature Components, with prototype-only authentication feedback.
- `ConfirmLoginForm` — reusable Login MFA and registration-verification code form for a backend-offered email or SMS challenge, with parent-owned verification and navigation.
- `RegisterForm` — dedicated registration form UI using the RecaptchaField and SocialAuthButtons Feature Components, with prototype-only validation feedback.
- `PrivacyChoicesBanner` — the global consent banner. It directly uses the shared `useCookieConsent` instance for Accept All, Reject All, preference opening, and both policy-opening actions; it emits no consent or modal actions to a parent.
- `CookiePrivacyPolicy` — the modal host mounted alongside `PrivacyChoicesBanner` across public and authenticated pages. It does not compose or coordinate the banner. It reads the shared active modal state, renders `CookiePreferencesContent` or the reusable `PolicyContent` through one `BaseModal`, and delegates saving and closing to `useCookieConsent`. Consent is independent from authentication and survives navigation, refresh, login, and logout.
- `OrderSummaryCard` — focused Checkout child presenting order amounts, notes, and actions from Checkout-supplied props; emits the checkout action for Checkout to pass to the page-owned workflow.
- `PaymentStatusCard` — Checkout return-state presentation composed from shared `StateLabel` and `Button`; it receives `currentState`, `paymentPlanTitle`, and `paymentPlanDescription` from Checkout, preserves the pending, success, failed, cancelled, and expired behavior, and leaves actions and payment/subscription logic to its parent.
- `Checkout` — the Checkout feature component, composed from the focused `ChoosePlanCard`, `PaymentStatusCard`, and `OrderSummaryCard` children in the same feature directory. Its local `useCheckout` composable adapts the global transient `CheckoutStore`, while the page owns billing requests and redirects and backend-verified subscription truth remains in `UserStore.subscription`.
- `CameraPreviewModal` — the single Training camera feature component; requests camera and microphone access, handles permission states, opens the live preview, and displays analysis controls and backend feedback.

---

## Composables

Reusable frontend logic should be extracted into Vue composables and placed in the `composables/` directory.

---

## Services

Backend communication, API access, and external integration logic should be placed in the `services/` directory.

---

## Authenticated Application Data and Global Store

The cross-page initialization, store ownership, and page data-flow requirements are in [Authenticated Application Data and Global Store](pages-and-routes.md#authenticated-application-data-and-global-store). Request and response contracts remain in [Authenticated application data and persisted user updates](integration-contracts.md#authenticated-application-data-and-persisted-user-updates).

---

## Frontend / Backend Boundary

Frontend owns browser UI, user interaction, camera access, lightweight frame preparation, backend transport, rendering structured results, overlays, checkout interaction through protected provider integrations, and client-side states.

Backend owns computer-vision inference, pose, ball, and racket detection, stroke analysis, AI interpretation, coaching logic, authentication authority, databases, creation and confirmation of payment transactions, payment webhooks, and server-side business rules. Sensitive payment data remains the responsibility of the payment provider and backend integration and must not pass through frontend application code.

Do not move backend responsibilities into the browser unless the architecture is explicitly changed.

---

## Responsive Requirements

Support desktop, tablet, and mobile layouts with adaptive navigation, readable typography, usable controls, sensible stacking, usable media proportions, and no unintended horizontal overflow.

The Training page may prioritize larger screens but must provide a safe and understandable mobile state.

---

## Accessibility Requirements

- Use semantic HTML.
- Associate labels with controls.
- Support keyboard navigation.
- Provide visible focus states.
- Maintain adequate color contrast.
- Do not communicate state through color alone.
- Name icon-only controls accessibly.
- Announce important asynchronous errors and state changes.
- Respect reduced-motion preferences where applicable.

---

## Required Application States

Applicable pages and features must define initial, loading, empty, success, validation, recoverable error, unavailable, and disconnected states. The page-by-page matrix and recovery behavior are defined in [pages-and-routes.md](pages-and-routes.md#application-state-matrix); example data and transport distinctions are in [integration-contracts.md](integration-contracts.md). In particular, distinguish empty from unavailable, signed-out from session-check failure, and partial analysis from a complete result.

Frontend recovery behavior follows these orchestration rules:

| Surface | Empty / insufficient data | Recoverable failure | Unavailable / disconnected | Frontend recovery |
| --- | --- | --- | --- | --- |
| Dashboard | Show an honest empty state when no sessions or supported focus exist | Show a `Refresh` button without inventing data | Preserve the shell, explain that data cannot be loaded, and keep `Refresh` available | `Refresh` retries unified user-data initialization; keep Training and History navigation available when the stored snapshot is usable |
| History | Treat an empty initial session list as successful | Preserve the current cursor and offer retry | Explain that history is unavailable | Read the initial collection from `UserStore`; use the dedicated list endpoint only for pagination or explicit refresh and write its result back to the store |
| Session Review | Use safe not-found/unauthorized/insufficient states | Preserve the session route and offer retry | Explain that review is unavailable | Retry or return to History |
| Training | Treat no analysis data as waiting, not a zero-valued result | Pause frame sending and run bounded automatic reconnect attempts for the same session | Distinguish camera/device failure from a terminal analysis disconnect after retries fail | Resume the same `sessionId` and stroke sequence after reconnect; expose reconnect/stop only after automatic recovery fails |
| Subscription / Checkout | Distinguish no active subscription from unknown status | Preserve the selected plan and offer retry | Explain billing/provider unavailability | Use the initial `UserStore` section; re-fetch backend status for checkout verification and write it back to the store, never infer payment success from a redirect |
| Profile / Settings | Keep optional empty values empty | Preserve last confirmed store values and unsaved form input | Keep the local page usable while identifying unavailable persistence | Retry the section save; replace only the corresponding `UserStore` section with the normalized success response and never claim an unsuccessful save |
| Authentication | Distinguish standard sign-in from an explicit challenge | Preserve non-secret fields and field errors | Keep authentication unknown when lookup/refresh is unavailable | Retry lookup/request; clear secrets after terminal failure |

A `401 Unauthorized` starts the documented refresh/sign-in recovery flow when appropriate; a `403 Forbidden` remains an authorization failure and does not log the user out. Network failure alone never proves logout, successful completion, or successful payment. Sensitive transient values are cleared on logout, challenge expiry, or terminal authentication failure.

Do not present fabricated analysis, session, or subscription data as real.

---

## Project Structure

Use [Frontend Project Structure](frontend-project-structure.md) as the authoritative source for physical frontend directories and global placement rules. This section is the navigation point for structural references; it does not redefine that structure.

Inspect the existing prototypes only as organization and ownership guidance:

- [Prototype components](../../prototypes/components/) show the current shared and feature component families.

- [Visual page prototypes](../../prototypes/design/pages/) show page-level composition, while [Vue page examples](../../prototypes/pages/) and the existing [Home](../../prototypes/home/) demonstrate current page wiring.

[Subscription](../../prototypes/design/components/subscription/), [Checkout](../../prototypes/design/components/checkout/), and [Training](../../prototypes/training/) entry directories show current page wiring examples.

- [Prototype composables](../../prototypes/composables/), [stores](../../prototypes/stores/), and [services](../../prototypes/services/) show existing behavior, state, and communication boundaries where examples are present.

- The [Home Page Video Slider](../../prototypes/components/sliders/home-page-video-slider/) is the reference for a complex component that owns substantial internal logic and several supporting files. Its current organization includes a Vue component, multiple supporting JavaScript classes/files, controller and lifecycle logic, rendering and animation logic, configuration, component-specific styles, a local [README](../../prototypes/components/sliders/home-page-video-slider/README.md), and related [tests](../../prototypes/tests/home-page-video-slider.test.js).

Use these references to understand practical grouping and ownership, not as files to copy blindly. A simple component may remain one `.vue` file when that is sufficient; only components with genuine internal complexity should group multiple supporting files with a clear owner. Component-specific logic and styles may stay grouped with that owner when allowed by the authoritative structure.

Prototype `assets/` directories do not determine production asset placement. Shared application assets belong in the approved global `src/assets/` location. Shared or global Sass/CSS likewise follows the authoritative global structure and must not become feature-owned merely because a prototype keeps styling nearby.

Do not introduce a frontend `modules/` feature-root layer.

---

## Verification and Testing

### Acceptance Criterion 1 — All Required Pages and Routes Exist

This validation corresponds to the first item in the `Acceptance Criteria` section:

- `all required pages and routes exist`

Validation must include:

- Verify that all pages and routes defined in `pages-and-routes.md` are implemented.
- Verify that every required route is registered in Vue Router.
- Use Vitest to validate the registered router configuration.
- Use Playwright end-to-end tests to verify that each required route loads the expected page.
- Verify that public routes are accessible without authentication.
- Verify that protected routes require authentication and follow the expected redirect behavior.
- Verify that no required route results in a missing page or unexpected routing error.

### Acceptance Criterion 2 — Public and Protected Navigation Behave Correctly

This validation corresponds to the second item in the `Acceptance Criteria` section:

- `public and protected navigation behave correctly`

Validation must include:

- Use Playwright end-to-end tests to verify public and authenticated navigation behavior in the running application.
- Verify that unauthenticated users see the required public navigation.
- Verify that unauthenticated users do not see authenticated-only navigation.
- Verify that public navigation contains the required items defined in the `Navigation Requirements` section and the authoritative navigation prototypes.
- Verify that public navigation items lead to the expected page, section, or authentication flow.
- Verify that unauthenticated users attempting to access protected routes are redirected to the expected login flow.
- Verify that authenticated users see the required authenticated navigation.
- Verify that authenticated navigation contains the required items defined in the `Navigation Requirements` section and the authoritative navigation prototypes.
- Verify that authenticated navigation items lead to the expected protected pages.
- Verify that navigation updates correctly after login and logout.
- Verify that navigation remains usable with keyboard input.
- Verify that navigation remains usable on supported mobile layouts.


### Acceptance Criterion 3 — Visual Direction Is Consistent with the Prototype

This validation corresponds to the third item in the `Acceptance Criteria` section:

- `visual direction is consistent with the prototype`

Validation must include:

- Use Playwright visual tests to capture screenshots of the main frontend pages and important application states.
- Compare the implemented frontend against the authoritative visual prototypes and shared design-system rules.
- Verify that the main page layouts follow the intended visual structure and hierarchy.
- Verify that navigation composition and placement are consistent with the relevant navigation prototypes.
- Verify that the Training screen composition follows the intended prototype structure.
- Verify that authentication interaction and subscription-plan presentation remain visually consistent with their prototypes.
- Verify that shared spacing, typography, controls, and reusable visual patterns remain consistent with the frontend design system.
- Treat the prototypes as visual references rather than pixel-perfect production specifications.
- Use the verification agent to review significant visual differences and report any inconsistencies that require correction.

### Acceptance Criterion 4 — Training Exposes All Required Camera and Analysis States

This validation corresponds to the fourth item in the `Acceptance Criteria` section:

- `Training exposes all required camera and analysis states`

Validation must include:

- Use Playwright end-to-end tests to verify the Training interface and its main controls.
- Verify that the camera can be started and that the camera preview becomes available.
- Verify that the required Training controls such as Start, Stop, and Exit perform the expected frontend actions.
- Verify that starting analysis causes the frontend to prepare and send the expected data to the configured backend endpoint or transport contract.
- Mock or intercept the backend endpoint when the real backend is not available.
- Verify that the outgoing request or transport message contains the expected payload and data format.
- Verify that stopping analysis stops further data transmission.
- Verify that exiting the Training flow releases the required frontend camera and media resources.
- Verify applicable camera error states, including denied permission, unavailable camera, and initialization failure.
- Do not require a working backend response when the backend implementation is not yet available.



### Acceptance Criterion 5 — Desktop, Tablet, and Mobile Behavior Is Validated

This validation corresponds to the fifth item in the `Acceptance Criteria` section:

- `desktop, tablet, and mobile behavior is validated`

Validation must include:

- Use Playwright end-to-end tests to validate the frontend at representative desktop, tablet, and mobile viewport sizes.
- Verify that page layouts adapt correctly across supported viewport sizes.
- Verify that navigation adapts correctly for desktop, tablet, and mobile layouts.
- Verify that text remains readable and controls remain usable across supported viewport sizes.
- Verify that page sections stack and reposition correctly when the available screen width changes.
- Verify that media, camera previews, and other visual elements maintain usable proportions.
- Verify that no unintended horizontal overflow appears on supported viewport sizes.
- Verify that the Training page provides a safe and understandable mobile state.
- Compare responsive behavior against the authoritative frontend design-system rules and relevant visual prototypes.
- Use Playwright screenshots where useful to detect responsive layout regressions.
- Do not invent component dimensions or responsive thresholds in tests when they are not defined by the design system or supporting specifications.

### Acceptance Criterion 6 — Loading, Empty, Error, and Disconnected States Exist Where Applicable

This validation corresponds to the sixth item in the `Acceptance Criteria` section:

- `loading, empty, error, and disconnected states exist where applicable`

Validation must include:

- Use Playwright end-to-end tests to trigger loading, empty, error, and disconnected states on applicable pages and features.
- Verify that loading states are displayed while required data or operations are in progress.
- Verify that empty states are displayed when no data is available.
- Verify that error states are displayed when a request or operation fails.
- Verify that disconnected states are displayed when the frontend loses the required connection or transport.
- Mock or intercept backend responses where necessary to reproduce each state without requiring a working backend.
- Verify that each state provides clear and understandable information to the user.
- Verify that the UI does not display fabricated analysis, session, or subscription data when real data is unavailable.
- Verify that the user can recover from recoverable error states where the interface provides a retry or recovery action.


### Acceptance Criterion 6 — Loading, Empty, Error, and Disconnected States Exist Where Applicable

This validation corresponds to the sixth item in the `Acceptance Criteria` section:

- `loading, empty, error, and disconnected states exist where applicable`

Validation must include:

- Use Playwright end-to-end tests to trigger loading, empty, error, and disconnected states on applicable pages and features.
- Verify that loading states are displayed while required data or operations are in progress.
- Verify that empty states are displayed when no data is available.
- Verify that error states are displayed when a request or operation fails.
- Verify that disconnected states are displayed when the frontend loses the required connection or transport.
- Mock or intercept backend responses where necessary to reproduce each state without requiring a working backend.
- Verify that each state provides clear and understandable information to the user.
- Verify that the UI does not display fabricated analysis, session, or subscription data when real data is unavailable.
- Verify that the user can recover from recoverable error states where the interface provides a retry or recovery action.

### Acceptance Criterion 8 — Applicable Tests, Linting, and Static Checks Pass

This validation corresponds to the next item in the `Acceptance Criteria` section:

- `applicable tests, linting, and static checks pass`

Validation must include:

- Run all applicable frontend automated tests.
- Run Vitest unit and component tests.
- Run Playwright end-to-end and browser tests.
- Run ESLint static code analysis.
- Verify that all applicable test commands complete successfully.
- Verify that no ESLint errors remain.
- Verify that failed tests or failed static checks cause this acceptance criterion to fail.
- Do not require checks that are not used by the frontend project.


### Acceptance Criterion 9 — Unresolved Backend Dependencies Are Reported and Not Represented as Completed Functionality

This validation corresponds to the next item in the `Acceptance Criteria` section:

- `unresolved backend dependencies are reported and not represented as completed functionality`

Validation must include:

- Identify frontend functionality that depends on backend endpoints, services, analysis logic, authentication authority, payment processing, or other backend capabilities that are not yet implemented or available.
- Report each unresolved backend dependency clearly.
- Do not mark a feature as fully completed when required backend functionality is still unavailable.
- Allow the frontend portion of a feature to be marked as complete when its own implementation is finished and verified independently.
- Use mocks or intercepted requests where appropriate to validate the frontend portion without requiring the real backend.
- Distinguish clearly between completed frontend functionality and unresolved backend functionality.
- Do not present mocked, placeholder, or simulated backend behavior as completed production functionality.
- Treat unreported unresolved backend dependencies as a failed acceptance criterion.


---

## Acceptance Criteria

The frontend is complete only when:

- all required pages and routes exist
- public and protected navigation behave correctly
- visual direction is consistent with the prototype
- Training exposes all required camera and analysis states
- desktop, tablet, and mobile behavior is validated
- loading, empty, error, and disconnected states exist where applicable
- the production build succeeds
- applicable tests, linting, and static checks pass
- unresolved backend dependencies are reported and not represented as completed functionality
