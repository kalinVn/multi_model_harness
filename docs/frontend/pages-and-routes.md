## Required Pages and Routes

### Home Page
- purpose: `Main public entry page of the application`
- route: `/`
- layout: `Public Layout`
- Example Prototype: `design/pages/index.html`
- name: `home`
- description: `Left Section: application branding and introductory information, main headline, short introductory description, two primary action buttons, small statistic or information cards. Right Section: Animated Banner, animated visual preview of the Tennis AI Coach training and AI analysis experience.HomePageInfoSection renders the left section directly from the Home Page prototype, with CTA actions using shared Button and parent-owned handlers; do not introduce additional static-section or page-specific button components.`
- required shared components: `Button`
- required feature components: `HomePageInfoSection`, `HomePageVideoSlider`
- dependencies: None

### Features
- purpose: `Public page that presents the core capabilities of the product and helps users understand what it can do.`
- route: `/features`
- layout: `Public Layout`
- Example Prototype: `design/pages/features.html`
- name: `feature`
- description: `Main Section: headline, short description, three numbered feature cards, and two primary buttons. The Features page should follow the Public Layout and match the prototype directly for the page title, secondary description, and all other page-level content; each card supplies its number, title, and description through the shared BaseCard slots.`
- required shared components: `Button`, `BaseCard`
- dependencies: None

### Login Page
- purpose: `Allow an existing user to enter email and password or choose a supported social login entry point.`
- route: `/login`
- layout: `Public Layout`
- Example Prototype: `design/pages/login.html`
- name: `login`
- description: `Dedicated public authentication page. Render the LoginForm with email and password fields. Place the RecaptchaField immediately before the primary Login action, include a Create Account link to Register, and provide the SocialAuthButtons for Google, Facebook, and Apple. When valid credentials return a TOTP, email, or SMS MFA challenge, replace the credential form with ConfirmLoginForm for the active backend-offered method. Authentication, OAuth, MFA, and reCAPTCHA verification authority remain on the backend; the prototypes do not create a session, start an OAuth flow, send a real code, or issue a real reCAPTCHA token.`
- required shared components: None
- required feature components: `LoginForm`, `ConfirmLoginForm`
- data contract: `POST /api/v1/auth/login` with email, password, and provider reCAPTCHA token; `POST /api/v1/auth/challenges/{challengeId}/verify` for a backend-offered TOTP, email, or SMS challenge. After confirmed authentication, load `GET /api/v1/user/data` into `UserStore` and use client-side router navigation to `/history` without a full-page reload.
- dependencies: None

#### Feature Requirements

Login owns credential entry, immediate form validation, OAuth entry, MFA challenge presentation, challenge verification, authenticated user-data initialization, client-side navigation, and user-facing authentication errors. It passes its pending provider, workflow state, and safe workflow message back into LoginForm through the documented parent-controlled props. `LoginForm` composes the feature-owned `RecaptchaField`; `ConfirmLoginForm` collects only the code for the selected backend-offered TOTP, email, or SMS method. The page does not reclassify either form as shared UI. After confirmed password, MFA, or page-owned Google authentication, Login loads the unified authenticated user data into `UserStore` and navigates to History through the client-side router without a full-page reload. Follow the [cross-page authentication and session requirements](#authentication-and-session) for token lifecycle, authenticated data initialization, refresh, logout, and backend authority.

### Register Page
- purpose: `Allow a new user to enter the details required to create an account and accept the Terms of Service.`
- route: `/register`
- layout: `Public Layout`
- Example Prototype: `design/pages/register.html`
- name: `register`
- description: `Dedicated public registration page. Render the RegisterForm with first name, surname, email, optional phone, password, confirm-password, required Terms of Service acceptance, and the RecaptchaField immediately before the primary Create Account action, plus SocialAuthButtons for Google, Facebook, and Apple and an existing-account link to Login. Do not add a separate Privacy Policy checkbox or any other field absent from the component specification and referenced prototype. Social registration requires Terms of Service acceptance before its backend OAuth start request; the optional Privacy Policy acknowledgment is false. When password registration returns its email-verification challenge, replace RegisterForm with ConfirmLoginForm configured for registration. The prototypes alone do not create an account, issue a real reCAPTCHA token, start OAuth, deliver a code, or establish a session.`
- required shared components: None
- required feature components: `RegisterForm`, `ConfirmLoginForm`
- data contract: `POST /api/v1/auth/register` with the form's first name, surname, email, optional phone, password, legal consent, and provider reCAPTCHA token; confirm password is client-only. A successful `201 Created` response returns the created public user fields and an email-verification challenge. Confirm it through `POST /api/v1/auth/registration-challenges/{challengeId}/verify`. After the backend establishes the session, load `GET /api/v1/user/data` into `UserStore` and use client-side router navigation to the existing History route without a full-page reload; see integration contract examples (`docs/frontend/integration-contracts.md#authentication-and-application-session`).
- states: idle, validation error, reCAPTCHA required, submit pending, verification required, verification pending, invalid code, expired challenge, conflict, recoverable error, unavailable.
- dependencies: `AuthStore`, `UserStore`

#### Feature Requirements

Register owns its form validation, required Terms of Service acceptance, provider verification input, OAuth registration entry, registration-verification challenge state, confirmed session handling, authenticated user-data initialization, and navigation to the existing History route. It passes its pending provider, workflow state, and safe workflow message back into RegisterForm through the documented parent-controlled props. The optional backend Privacy Policy acknowledgment remains false because this page does not collect it separately. `RegisterForm` composes the feature-owned `RecaptchaField`; `ConfirmLoginForm` is reused only as the presentation and local-validation boundary for the registration code. The page does not reclassify either component as shared UI and does not reuse the Login MFA endpoint for registration verification. Follow the [cross-page authentication and session requirements](#authentication-and-session) for session establishment, token handling, and backend authority.

### Training
- purpose: `Primary page for real-time training where the user records strokes, sees instant analysis, and receives guidance.`
- route: `/training`
- layout: `Authentication Layout`
- Example Prototype: `design/pages/training.html`
- Vue Prototype: [TrainingPage.vue](../../prototypes/pages/TrainingPage.vue)
- camera design reference: [camera.html](../../prototypes/design/pages/camera.html) previews the camera modal; it is not a separate application route. The Training prototype mounts `CameraPreviewModal` for its Start Training action when run through Vite, while the static HTML fallback links to this camera design reference.
- name: `training`
- description: `Follow the referenced HTML and Vue Training prototypes for the page title, secondary text, section titles, descriptions, fields, labels, buttons/actions, and all other page-level content. Align the full Training content panel to the same left content edge as the Tennis AI Coach / Training header instead of centering it inside a narrower max-width container. In the left column, place TennisBallSlider in the former heading position with the Training heading and introductory sentence immediately to its right. Keep that hero row directly below the LIVE COACHING eyebrow without an additional vertical gap. Place the shared Start Training Button below that hero row and align it under the ball. Keep the ball and action surfaces transparent and without a frame. In the right column, align the top of the Coaching Cue, Connection, and Session stack with the LIVE COACHING eyebrow immediately below the authenticated navigation bar. On narrow screens, move the status stack below the left-column content. The current prototype contains no collapsible form sections, so do not invent any. Training-specific data, configuration, form handling, and actions belong to the page. Preserve the existing camera/full-screen training modal or camera training flow behind Start Training, reusing its implementation without duplicate camera logic or a second training flow. Do not invent fields, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: `Button`
- required feature components: `TennisBallSlider`, `CameraPreviewModal`; `CollapseForm` only for collapsible form sections present in the referenced prototype (none in the current prototype).
- data contract: Create the session with `POST /api/v1/training/sessions/create` before connecting to the backend-issued analysis WebSocket. Finish normally with `POST /api/v1/training/sessions/{sessionId}/complete`; use `POST /api/v1/training/sessions/{sessionId}/abandon` for cancellation or early exit. Bounded automatic reconnect keeps the same session id and stroke sequence, while the backend records the disconnected interval as a pause excluded from active training duration. See integration contract examples (`docs/frontend/integration-contracts.md#training-session-and-analysis-transport`).
- states: idle, creating session, ready, connecting, live, reconnecting, completing, complete, abandoning, incomplete, recoverable error, unavailable.
- dependencies: `AuthStore`, `TrainingSessionStore`

#### Feature Requirements

##### Camera

- Allow switching between available cameras when supported by the device.
- Keep the selected camera active until the user changes it.
- Handle camera permission denied, unavailable camera, and initialization errors.

##### Frame Preparation

The frontend may perform lightweight frame capture, resizing, throttling, or formatting for transport. It must not perform computer-vision inference.

##### Training / Live Analysis Workflow

The frontend orchestrates live training in this order without performing computer-vision inference, stroke recognition, coaching decisions, or Text-to-Speech itself:

1. The user starts training and the frontend creates an authenticated session. See Training session endpoints — `POST /api/v1/training/sessions/create` (`docs/frontend/integration-contracts.md#training-session-endpoints`).
2. The response supplies the authoritative `sessionId` and short-lived `analysisWebSocketUrl`; the frontend opens that backend-issued URL and never constructs an analysis host itself.
3. Camera capture and frame sampling begin only when the training session and socket state permit them.
4. For each selected frame, the frontend sends the JSON metadata message and then its matching binary JPEG without interleaving another frame pair. See Live analysis WebSocket — Client-to-server frame message (`docs/frontend/integration-contracts.md#client-to-server-frame-message`).
5. The backend receives frames over time, performs temporal analysis, and decides internally when enough evidence exists to identify and evaluate a completed stroke. The frontend does not impose a fixed frame count or infer stroke boundaries.
6. The backend assigns the stroke's `strokeId` and `strokeNumber` and may return one or more `player_feedback` events. Each event provides canonical text feedback and may also include an optional temporary `audioUrl` for backend-generated audio of that text. See Live analysis WebSocket — Server-to-client `player_feedback` message (`docs/frontend/integration-contracts.md#server-to-client-player_feedback-message`).
7. The frontend validates the event's active `sessionId`, displays the backend-supplied coaching text, and, when audio is enabled and the event includes `audioUrl`, plays the matching audio. It never fabricates missing observations or advice.
8. When audio is enabled and `audioUrl` is present, the frontend plays that temporary backend-generated resource. It does not generate provider-side TTS, upload coaching audio, or treat temporary audio as persistent session history. Text remains the canonical feedback.
9. If the socket disconnects, the frontend pauses frame sending and performs a bounded number of automatic reconnection attempts for the same `sessionId`. A successful reconnect resumes the same session and its stroke sequence. The backend records the disconnected interval as a session pause and excludes it from active training duration. The frontend shows an unavailable/disconnected state only after the automatic attempts fail; it never silently creates a new session.
10. Normal stop ends capture immediately, prevents later frame sends, sends the documented `stop_analysis` message, and completes the session. Early exit abandons the session as incomplete. Permission loss or a transport failure that remains after the bounded reconnect attempts becomes an explicit unavailable/disconnected state rather than silently starting a new session. See Training session endpoints (`docs/frontend/integration-contracts.md#training-session-endpoints`) and Live analysis WebSocket (`docs/frontend/integration-contracts.md#live-analysis-websocket`).

##### Audio Output

- Play optional `audioUrl` resources delivered with current-session `player_feedback` when audio is enabled.
- Queue playback so coaching clips do not overlap, and allow current playback to stop when training ends or newer product rules require replacement.
- If audio is unavailable, expired, or playback fails, show a clear non-blocking `Audio unavailable` message and continue with the canonical textual feedback. The training remains active and the backend still records the strokes and final session summary normally; audio failure does not change analysis or session truth.
- Release playback resources when they are no longer needed.

### Dashboard
- purpose: `Provides the user with an overview of their training activity, recent sessions, and quick access to the main application features.`
- route: `/dashboard`
- layout: `Authentication Layout`
- Example Prototype: `design/pages/dashboard.html`
- name: `dashboard`
- description: `Follow the Dashboard prototype directly for all page content, sections, containers, text, and visual structure, implemented as page-level DOM/layout. Do not introduce page-specific shared components or extract static sections into reusable components. Keep Session History available as defined in the prototype. Each returned session row opens Session Review using its server-supplied session id. Sidebar, top header, and footer remain provided by the Authentication Layout and are not part of the page sections.`
- required shared components: None
- required feature components: `DashboardMetricCard`
- data contract: initial Dashboard aggregates and History items come from `GET /api/v1/user/data`; see authenticated application data (`docs/frontend/integration-contracts.md#authenticated-application-data-and-persisted-user-updates`). The page does not issue a separate initial Dashboard request.
- states: loading, empty, success, recoverable error, unavailable.
- dependencies: `UserStore`


### History
- purpose: `allows the user to review previous training sessions, results, performance metrics, and past coaching feedback`
- Route: `/history`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/history.html`
- description: `Follow the History HTML/design prototype for all sections and page-level elements. Use the existing BaseTable Feature Component for the Training Sessions table, showing only Date, Duration, Status, and a Review Session action linked to /sessions/:sessionId. Render each Status value with the shared Badge component: Reviewed uses success; Sample and Incomplete use neutral. Keep pagination at the bottom of the section. All other headings, descriptions, containers, surrounding layout, and visual elements remain page-level DOM/layout matching the prototype; do not create additional shared components or extract static sections into reusable components. Do not add fields, filters, controls, actions, states, wrappers, or components absent from the prototype or explicit page-specific Additional Description and Functionality.`
- required shared components: `Badge`
- required feature components: `BaseTable`
- data contract: the initial collection comes from `UserStore.sessionHistory`, populated by `GET /api/v1/user/data`. Items use canonical `durationSeconds`, formatted by the page for display, and explicit `historyStatus` values `reviewed`, `sample`, or `incomplete` for the visible Badge label. `GET /api/v1/training/sessions` returns the same item shape for pagination or explicit refresh and writes its result back to that store section; see integration contract examples (`docs/frontend/integration-contracts.md#session-history-and-session-review`).
- states: loading, empty, success, recoverable error, unavailable.
- dependencies: `UserStore`

### Session Review

- purpose: Review a previous training session's supported results and coaching feedback, including available key moments, movement trends, and next recommended focus.
- page/component: `frontend/src/pages/SessionReviewPage.vue`.
- route: `/sessions/:sessionId`
- name: `session-review`
- layout: `Authentication Layout`
- access: Authenticated; the backend authorizes access to the requested session.
- route parameters: required `sessionId` opaque identifier. Reject malformed identifiers and show not-found/unauthorized states without leaking whether another user's session exists.
- navigation destination: Session rows on History and Dashboard link to this route using their returned session ids. Session Review is not a top-level sidebar item; History remains the active navigation section.
- data contract: `GET /api/v1/training/sessions/{sessionId}/review`; see frontend integration contract examples (`docs/frontend/integration-contracts.md#session-history-and-session-review`).
- visual references: [History](../../prototypes/design/pages/history.html) and [Training Session Card](../../prototypes/design/components/training-session-card.html). These provide visual cues only; they do not establish data or behavior beyond this entry.
- state owner: `frontend/src/stores/UserStore.ts`; data access: `frontend/src/services/sessionService.ts`. Route-specific review loading must not create another authoritative history store.
- states: loading, not found/unauthorized, success, partial/insufficient data, recoverable error, unavailable.

### Application State Matrix

| Surface | Loading | Empty / partial | Error / unavailable | Success owner |
| --- | --- | --- | --- | --- |
| Dashboard | Unified user-data request pending | No sessions is an honest empty state | Retry authenticated application initialization; preserve shell | `UserStore.dashboard` and `UserStore.sessionHistory` |
| History | Unified initialization or later-page request pending | Empty initial list is successful | Retry initialization, current cursor, or explicit refresh as applicable | `UserStore.sessionHistory` |
| Session Review | Review request pending | Insufficient supported result is labeled | Safe not-found/unauthorized; retry recoverable failures | Server-authorized review response |
| Training | Camera/transport/analysis transitions shown separately | Waiting for first supported result | Camera and transport failures remain distinct | Backend analysis/session events |
| Subscription / Checkout | Unified initialization or checkout verification pending | No active plan is distinct from unknown state | Retry initialization or server/provider verification | `UserStore.subscription` plus backend-verified checkout refreshes |
| Profile / Settings | Unified initialization or section save pending | Optional values can be empty | Retain last confirmed store values and unsaved user edits | Normalized section response written to `UserStore` |
| Authentication | Session lookup/request pending | Signed out is distinct from lookup failure | Field/challenge/session errors shown | Backend session/auth response |

Recovery behavior and shared error semantics follow the matrix above and the shared error envelope (`docs/frontend/integration-contracts.md#shared-response-and-error-shape`).

### Subscription
- purpose: `allows the user to view their current subscription plan, manage billing details, and change or upgrade their subscription.`
- Route: `/subscription`
- Layout: `Authentication Layout`
- Example Prototype: `design/components/subscription/subscription.html`
- description: `Required section is the Subscription section, which includes a page heading, a short description, and two main cards: the Subscription Plan Card and the Billing or Plan Management Card. Before a plan is selected, render the larger PaymentCardPlan Feature Component with No selected plan, no price, no status label, no selected styling, and a clear explanation that training services require selecting a plan. Use BillingDetailsCard for the existing billing panel. Change plan reveals the Starter, Performance, and Pro PaymentCardPlan options, with Performance marked Most popular. Manage billing remains page-owned. Do not add a separate comparison-page button or payment-status prototype controls to this page.`
- required shared components: None
- required feature components: `PaymentCardPlan`, `BillingDetailsCard`
- data contract: initial subscription data come from `GET /api/v1/user/data`. Checkout verification, plan changes, and the provider-hosted customer portal remain dedicated operations; see integration contract examples (`docs/frontend/integration-contracts.md#checkout-and-billing`).
- states: loading, no active subscription, active, pending change, recoverable error, unavailable.
- dependencies: `UserStore`

#### Feature Requirements

Subscription reads its initial plan and billing presentation from `UserStore.subscription`, with no separate initial status request. It owns plan selection and the page-owned Manage billing action. The provider-hosted payment flow and shared backend boundaries are defined in the [Subscription and Checkout requirements](#subscription-and-checkout).

### Profile
- purpose: `Allow authenticated users to view and manage their personal profile information.`
- Route: `/profile`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/profile.html`
- name: `profile`
- description: `Follow the referenced Profile HTML prototype for the page title, secondary text, and the remaining Personal Information section, which uses the existing CollapseForm Feature Component. The Profile page component owns and creates the section's data/configuration, deriving its title, secondary description, fields, labels, relevant configuration, buttons/actions, and any additional content directly from the prototype. Supply the CollapseForm instance through its existing title/description props and page-rendered default/footer slots. Profile-specific values, configuration, form handling, and actions remain in the Profile page; CollapseForm stays reusable. Do not create additional Profile section components unless explicitly required elsewhere. Implement all remaining page-level elements directly as DOM/layout matching the prototype. Do not invent fields, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: None
- required feature components: `CollapseForm`
- data contract: initial Personal Information data come from `GET /api/v1/user/data`. The dedicated Personal Information `PATCH` endpoint replaces the normalized `UserStore.personalInformation` section. See authenticated application data and persisted user updates (`docs/frontend/integration-contracts.md#authenticated-application-data-and-persisted-user-updates`).
- states: loading, loaded, validation error, save pending, recoverable error, unavailable.
- dependencies: `UserStore`

### Settings

- Route: `/settings`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/settings.html`
- name: `settings`
- description: `Follow the referenced Settings HTML prototype as the source of truth for the page title, secondary text, and the remaining Account Security · Change Password, Notifications, and Privacy & Data sections. Each collapsible section uses the existing CollapseForm Feature Component. The Settings page owns and creates each section's data/configuration directly from the prototype. Pass only the section title/header and secondary title/description through the existing title and description props. Define and render all section-specific fields, labels, selects, controls, buttons, actions, and other body content in the Settings page, supplying that content through CollapseForm's default slot and its footer slot where appropriate. Field configuration, values, validation, form handling, and action behavior remain owned by the Settings page; do not pass a field schema to CollapseForm or move Settings-specific content or behavior into it. Keep CollapseForm reusable. Do not create separate components for individual Settings sections unless explicitly required elsewhere. Implement all remaining page-level elements directly as DOM/layout matching the prototype. Do not invent fields, controls, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: None
- required feature components: `CollapseForm`
- data contract: initial Notifications and Privacy & Data settings come from `GET /api/v1/user/data`. Each independently saved persisted group uses its dedicated `PATCH` endpoint; Change Password, data export, and account deletion remain separate actions. See authenticated application data and persisted user updates (`docs/frontend/integration-contracts.md#authenticated-application-data-and-persisted-user-updates`).
- states: loading, loaded, validation error, save pending, recoverable error, unavailable.
- dependencies: `UserStore`

### Not Found

- Route: `/not-found`
- Layout: `Public Layout`
- Example Prototype: `design/pages/not-found.html`
- name: `not-found`
- description: `The page show 404 not found`
- required shared components: None
- required feature components: None
- dependencies: None


### Checkout

- Route: `/checkout`
- Layout: `Authentication Layout`
- Example Prototype: `design/components/checkout/checkout.html`
- name: `checkout`
- description: `The Checkout page renders the Checkout feature component and owns the page-level billing workflow. Checkout composes a selected-plan ChoosePlanCard with Pay with Stripe and Pay with PayPal actions underneath. Its right-hand area renders backend-verified pending/cancelled/failed/expired states through PaymentStatusCard; after verified success it replaces the status card with OrderSummaryCard showing the chosen plan, price, and Paid status. It contains no Payment Information section and never collects raw card details.`
- required shared components: None
- required feature components: `Checkout`
- data contract: provider-hosted checkout start and server-verified return; see integration contract examples (`docs/frontend/integration-contracts.md#checkout-and-billing`).
- states: pending, succeeded only after backend verification, cancelled, failed, expired, recoverable error, unavailable.
- dependencies: `CheckoutStore`

#### Feature Requirements

The Checkout page owns provider selection, redirect to the backend-returned hosted URL, and the page-level handling of return, pending, final, failure, and retry states. The `Checkout` feature adapts that state and composes its focused child cards without taking over requests, redirects, verification, or persisted subscription ownership. The page must obtain backend-verified subscription status rather than infer success from a redirect. Follow the [Subscription and Checkout requirements](#subscription-and-checkout) and the billing integration contract (`docs/frontend/integration-contracts.md#checkout-and-billing`).

## Cross-Page Feature Requirements

### Authenticated Application Data and Global Store

`UserStore` is the single global source of truth for persisted user-specific application data after authentication. `AuthStore` may own access-token and authentication workflow state, but it must not keep a second authoritative copy of the user profile or application data.

The authenticated initialization flow is:

1. Login or MFA verification establishes the authenticated application session and returns the short-lived access token. OAuth establishes the refresh-cookie session first and redirects directly to its validated protected `returnTo`; when no memory access token exists, the global authentication guard obtains one through a single CSRF-protected `POST /api/v1/auth/refresh` bootstrap request before resolving that navigation.
2. The frontend immediately calls `GET /api/v1/user/data` once with that authenticated session.
3. `UserStore` atomically stores the complete response: account and personal information, subscription, Dashboard aggregates, the initial History collection, and persisted Settings groups.
4. Dashboard, Profile, Settings, Subscription, History, the authenticated layout, and other authenticated consumers read their initial server data from `UserStore`. Route entry must not trigger redundant initial-load GET requests for data already present in that snapshot.
5. Dedicated endpoints remain available only where the operation is independently necessary: History pagination or explicit refresh, Session Review detail, checkout verification, customer-portal creation, and other action-specific operations.
6. Each successful Profile or Settings update returns the normalized persisted section. `UserStore` replaces that corresponding section immediately; the page does not keep a separate authoritative server copy.
7. Logout, terminal authentication failure, or accepted account deletion clears the complete `UserStore` snapshot as well as authentication state.

Pages may own validation state, pending state, error messages, and unsaved form drafts. Those local drafts are not server truth. Components receive store-backed values through their owning page or feature and do not independently fetch or cache the same initial data.

Dashboard reuses `sessionHistory` rather than maintaining duplicate recent-session records.

Camera and microphone availability, permissions, discovered device identifiers, current physical-device selection, audio-output routing, and other runtime browser capabilities remain local device state.

The unified user-data response and every section-specific update contract are defined in Authenticated application data and persisted user updates (`docs/frontend/integration-contracts.md#authenticated-application-data-and-persisted-user-updates`).

### Authentication and Session

The technical request/response definitions are in Frontend Integration Contract Examples — Authentication and application session (`docs/frontend/integration-contracts.md#authentication-and-application-session`), including the OAuth start/callback endpoints, `POST /api/v1/auth/login`, `POST /api/v1/auth/register`, `POST /api/v1/auth/challenges/{challengeId}/verify`, `POST /api/v1/auth/refresh`, and `POST /api/v1/auth/logout`. This section owns the frontend sequence and UI behavior; it does not repeat those schemas.

Credentials, session validation, and authorization authority remain the responsibility of the backend.

- Provide token-based authentication with login, logout, access-token refresh, and multi-factor verification flows.

- For OAuth, request the backend-owned provider authorization URL and navigate to it. After backend exchange, success returns directly to the validated protected `returnTo`; the global authentication guard must bootstrap the memory-only access token with the CSRF-protected refresh endpoint and load user data before resolving navigation. There is no dedicated frontend OAuth callback route. Safe failures return to `/login` with only the allowlisted `oauthStatus` values defined by the integration contract. Never expose provider tokens, application tokens, secrets, or raw provider errors in frontend state persistence or URLs.

- When Login returns an MFA challenge, show only the methods offered for that `challengeId`, submit the selected verification method/code, and create authenticated frontend state only after successful verification.

- After authentication succeeds, load the unified authenticated application data before treating protected page data as ready. A successful authentication response alone does not populate Dashboard, Profile, Settings, Subscription, or History.

- Display the sign-in UI whenever authentication is required.

- Send authentication requests to the backend.

- Before submission, validate authentication form fields in the frontend for required values, supported formats, length constraints, and matching password confirmation where applicable. These checks provide immediate UI feedback but never replace authoritative backend validation.

- Store the short-lived JWT access token in application memory and use it for authenticated API requests.

- Store the refresh token as a HttpOnly, Secure, SameSite cookie managed by the browser and inaccessible to frontend JavaScript.

- Keep the user authenticated while a valid access token is available.

- When the access token expires, attempt to obtain a new access token through the backend refresh endpoint.

- Display clear user-facing errors for invalid credentials, failed authentication requests, failed multi-factor verification, and authentication states that require the user to sign in again.

- If an authenticated API request returns 401 Unauthorized, attempt token refresh when appropriate.

- If the refresh succeeds, retry the original request once with the new access token.

- If the refresh token is invalid, expired, revoked, or reused, clear the local authentication state and redirect the user to the login flow.

- Treat 403 Forbidden as an authorization failure for an authenticated user and do not treat it as logout or authentication expiration.

- Clear the access token and local authentication state when the user logs out or when authentication can no longer be renewed.

- Treat temporary network failures during authentication or token refresh as an unavailable state rather than immediately treating the user as signed out.

- Keep frontend authentication logic limited to authentication forms, access-token state, routing, multi-factor and verification UI flows, and user-facing authentication states.

- Keep credential verification, JWT issuance and validation, refresh-token rotation and revocation, multi-factor verification, authorization permissions, and security rules on the backend.

### Subscription and Checkout

The frontend owns the user-facing subscription and checkout flow. Exact request, response, verified status, and payment-data boundaries are defined in Frontend Integration Contract Examples — Checkout and billing (`docs/frontend/integration-contracts.md#checkout-and-billing`); they are not duplicated here.

The Subscription page reads its initial plan and billing presentation from `UserStore.subscription`. It does not issue a separate initial status request. Dedicated billing endpoints remain responsible for checkout creation, customer-portal creation, and backend-verified checkout-return refreshes.

- When the user starts a subscription checkout, the frontend sends the selected plan and payment provider to the backend. The backend creates either a Stripe or PayPal hosted checkout session and returns its provider-hosted checkout URL. The frontend redirects the user only to that returned URL.

- The payment is completed on Stripe's or PayPal's hosted page, not inside the application.

- After the payment flow finishes, the selected provider redirects the user back to the application's configured success or cancellation page.

- The redirect to the success page must not be treated as final proof that the payment has been confirmed. Stripe or PayPal also sends a webhook event directly to the backend. The backend applies the provider-specific verification, processes the payment result idempotently, and updates the authoritative subscription state in the database.

- When the user returns to the success page, the frontend requests the current subscription status from the backend.

- Because the provider webhook and browser redirect can happen at nearly the same time, the backend may temporarily return a `pending` status. The frontend should display a pending state and retry the subscription-status request until the backend reports a final state such as `active`, `paid`, or `failed`.

- The frontend is responsible for displaying user-facing states such as checkout in progress, payment confirmation pending, successful activation, cancellation, payment failure, and recoverable network errors.

- The frontend must never store or process raw card or PayPal account credentials. Stripe, PayPal, and the backend remain responsible for payment processing, provider-specific webhook verification, transaction confirmation, and maintaining the authoritative subscription state.

---
