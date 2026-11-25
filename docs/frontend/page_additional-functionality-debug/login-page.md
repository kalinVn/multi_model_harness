# Login Page

## Additional Description and Functionality

Extend the isolated debug Login Page with standard email/password login, a page-owned debug MFA challenge using `ConfirmLoginForm`, and the Google Identity Services handoff defined by the Google login workflow on the `ai-trener-fronend-debug` branch.

The page remains available at `/login`, uses the Public Layout, and composes the existing `LoginForm` and `ConfirmLoginForm`. It coordinates authentication workflow state without moving field validation, field values, code entry, or provider-button presentation out of their owning components.

### Page Ownership

Login Page owns:

- handling the `submit` and `socialLogin` events emitted by `LoginForm`;
- retaining the active debug `challengeId`, offered method, and masked destination hint after a successful credential check;
- replacing `LoginForm` with `ConfirmLoginForm` while that challenge is active and handling its `submit({ method, code })` event;
- preventing duplicate authentication requests while the current request is pending;
- coordinating the debug authentication adapter or mock;
- mapping page-level pending, error, and success outcomes to the existing `LoginForm` presentation contract;
- accepting the confirmed local user-data projection into debug-only `UserStore` state and navigating to `/history` through the client-side router without a full-page reload;
- disposing page-owned provider adapters, callbacks, and rendered provider content when the page unmounts.

Login Page does not own input fields, field-level validation, reCAPTCHA presentation, social-button rendering, provider-token verification, backend credential verification, or long-lived session persistence.

### LoginForm Integration

Render one `LoginForm` as the page's initial authentication content. When the Login Example API returns a challenge, replace it with one `ConfirmLoginForm`; do not render both forms simultaneously.

Wire its events as follows:

- `submit({ email, password, recaptchaToken })` starts the standard login scenario;
- `socialLogin({ provider })` starts the selected social-authentication scenario;
- the Google social-login payload contains only `{ provider: 'google' }` and never contains email, password, or `recaptchaToken`;
- the page supplies the pending provider and safe form-level feedback through the existing `LoginForm` interface;
- field-level validation errors remain owned and displayed by `LoginForm`.

The page must not inspect or reach into the form's local field state. The Login payload contains only email, password, and `recaptchaToken`; it has no name field.

### Scenario 1: Standard Login

The Login Example API (`docs/frontend/example-apis/login.md`) documents the isolated Vite debug request and response examples for this scenario. It is not the production authentication contract.

1. Receive the validated `submit` payload from `LoginForm`.
2. Ignore a duplicate submission while the standard login request is pending.
3. Set the page workflow to pending and delegate the unchanged email, password, and `recaptchaToken` payload to a debug-only authentication adapter or mock.
4. Do not log or persist the password or reCAPTCHA token in the page, scenario registry, event log, URL, or browser storage.
5. On a recoverable failure, clear pending state, present a safe page-owned error through `LoginForm`, preserve allowed non-secret form context, and allow retry.
6. For a fixture without MFA, accept the returned user-data projection into debug-only `UserStore` state, clear pending state, and use client-side router navigation to `/history` without a full-page reload. For the MFA-enabled Maria fixture, retain the returned challenge and continue with Scenario 2; do not expose user data before confirmation. This preview does not create a production application session or authorization grant.

The debug implementation must not call a production authentication endpoint or claim that a real session has been created.

### Scenario 2: Confirm Login Code

The Login Example API (`docs/frontend/example-apis/login.md`) defines the loopback-only challenge and verification endpoints. The Vite server retains the short-lived challenge and its local confirmation code in memory; neither value is stored in browser storage or treated as a production credential.

1. Accept only an email or SMS method returned for the active challenge; the primary debug fixture offers email.
2. Render `ConfirmLoginForm` with the offered method and masked destination hint, while retaining `challengeId` only in page memory.
3. On `submit({ method, code })`, prevent duplicates, set confirmation pending, and send the payload to `POST /api/auth/challenges/{challengeId}/verify`.
4. On an invalid code, show a safe error through `ConfirmLoginForm`, preserve the active challenge, clear the submitted code from page-owned request state, and allow retry.
5. On an expired, exhausted, or already-used challenge, mark the form expired and require the user to restart Login.
6. On success, clear the challenge and code, store the complete returned user-data projection in debug-only `UserStore` state, and use client-side router navigation to `/history` without a full-page reload. History consumes that state and does not repeat the initial debug user-data initialization. No production session or authorization is created.

The debug page must never display, log, persist, or derive the expected code. The expected local code is a server-side Vite fixture documented only for manual testing.

### Scenario 3: Google Authentication Handoff

The Social Auth Example API (`docs/frontend/example-apis/social-auth.md`) defines the local HTTP simulation for this page-owned handoff; it is not the production provider flow. This debug-only one-click flow takes precedence over the production SDK render sequence described later in this document.

1. Receive exactly one `socialLogin({ provider: 'google' })` event from `LoginForm`.
2. On that same click, set the page's Google workflow to pending and call the separate `GoogleAuthServiceDebug`. Do not add a second button or alter the component's design-prototype appearance.
3. `GoogleAuthServiceDebug` simulates the provider callback locally and returns the documented example token without making an HTTP request. The page-owned `authenticateWithExampleBackend` function sends that token to the loopback-only Vite `POST /api/auth/google` mock. This is the only HTTP request in the Google debug flow; the service itself does not make it.
4. Treat the token as a debug-only fixture, never as a Google ID token, provider credential, application access token, or authentication authority. Never log, persist, or place it in a URL.
5. Ignore duplicate Google requests until the first request settles. On a recoverable failure, clear pending state, show a safe error through `LoginForm`, preserve non-secret form context, clear any retained password, and allow retry.
6. On a successful local response, accept the returned user-data projection into debug-only `UserStore` state and use client-side router navigation to `/history` without a full-page reload. Do not claim a provider credential, production application session, or authorization grant. Production OAuth follows the backend-owned provider contract and must not add a redundant reload after its validated return route resolves.

Facebook and Apple keep their existing social-login entry behavior. Do not invent provider SDK handling or new contracts for them in this page assignment.

### Provider Lifecycle Boundary

The production ownership model remains the one established by the Google login workflow:

- the provider adapter loads and initializes Google Identity Services and renders Google's supported button;
- the authentication service/API layer sends the provider credential to the application backend;
- the backend verifies the credential and creates the application session;
- the page coordinates UI state, accepts only a confirmed application-session result, initializes authenticated profile data, and navigates;
- `LoginForm` owns only its UI, local validation, events, and presentation of parent-supplied workflow state.

The isolated debug page represents these boundaries with mocks. It must not load the real Google SDK, contact Google, call a production backend, or create production authentication state.

When the debug page unmounts, dispose of `GoogleAuthServiceDebug`, abort the page-owned mock-backend request, and ensure that a late completion cannot update page state or navigate.

### GoogleAuthService Contract

The Google workflow defined on the `ai-trener-fronend-debug` branch uses `GoogleAuthService` as the provider-SDK boundary consumed by Login Page. The service is separate from both `LoginForm` and the application's authentication service/API layer.

`GoogleAuthService` owns:

- loading the Google Identity Services script once and reusing the shared load promise;
- initializing `google.accounts.id` with the public Google client ID and credential callback;
- rendering Google's official sign-in button inside the mounted container supplied by `LoginForm`;
- forwarding the original provider-issued ID token to an injected `authenticateWithBackend(idToken)` callback;
- preventing a second credential handoff while the first backend request is pending;
- reporting initialization, missing-credential, duplicate-request, and backend-handoff failures through its error callback;
- deactivating callbacks and clearing service-owned button containers when disposed.

Its production configuration uses `VITE_GOOGLE_CLIENT_ID`. This value is a public browser client identifier. A Google Client Secret must never be placed in frontend source, environment output, debug scenarios, or browser state.

The service interface from that branch is:

- `initialize()` — loads and initializes Google Identity Services once;
- `renderButton(container, options)` — renders the official provider button into a valid mounted element after initialization;
- `dispose()` — deactivates the service, invalidates late callbacks, clears pending state, and removes service-owned rendered content.

Login Page creates one `GoogleAuthService` instance for its mounted lifecycle. It supplies:

- `clientId`: the public value read from `import.meta.env.VITE_GOOGLE_CLIENT_ID`;
- `authenticateWithBackend(idToken)`: the injected authentication callback called with the original Google credential;
- `onAuthenticated(result)`: the page callback invoked only after the backend-authentication handoff succeeds;
- `onError(error)`: the page callback used to translate service or backend-handoff failures into safe UI state;
- optional `windowRef` and `documentRef` dependencies only when the debug implementation needs controlled test doubles.

The callback passed to the service is named `authenticateWithBackend`. It is not a second service created by `GoogleAuthService`; it is a function owned by the page's authentication adapter/API boundary. This injection keeps the provider SDK lifecycle separate from the application's backend authentication request.

Conceptual production wiring:

```js
const googleAuthService = new GoogleAuthService({
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
  authenticateWithBackend: idToken =>
    authenticationApi.authenticateGoogleIdToken(idToken),
  onAuthenticated: result => handleConfirmedApplicationSession(result),
  onError: error => presentSafeGoogleError(error),
})
```

The names `authenticationApi.authenticateGoogleIdToken`, `handleConfirmedApplicationSession`, and `presentSafeGoogleError` describe responsibilities. Bind them to implemented application interfaces when those interfaces exist; do not invent production API or AuthStore method names solely to satisfy this example.

When Google is selected, the page initializes the existing service instance and renders the official button only after its container is mounted:

```js
async function handleSocialLogin({ provider }) {
  if (provider !== 'google') {
    return startExistingRedirectOAuth(provider)
  }

  if (googleRequestPending) return

  await googleAuthService.initialize()
  googleAuthService.renderButton(googleButtonContainer)
}
```

The page does not call `authenticateWithBackend` directly after the social-button event. Google Identity Services first renders and owns the official button. After the user completes Google's interaction, GIS invokes the credential callback registered by `GoogleAuthService`; that callback extracts `response.credential` and passes it to `authenticateWithBackend`.

The callback sequence is:

```text
LoginForm socialLogin({ provider: 'google' })
  -> Login Page initializes GoogleAuthService
  -> GoogleAuthService renders the official GIS button
  -> Google invokes the configured credential callback
  -> GoogleAuthService calls authenticateWithBackend(response.credential)
  -> the application backend verifies the credential and returns an application result
  -> onAuthenticated(result) updates the page workflow
  -> Login Page accepts the confirmed session, initializes Profile data, and navigates
```

Failures follow the parallel error path:

```text
SDK load, missing credential, duplicate handoff, network, or backend failure
  -> GoogleAuthService calls onError(error)
  -> Login Page maps the failure to a safe FormStatusMessage state
  -> the application remains signed out
  -> retry is enabled only when the failure is recoverable
```

The mounted lifecycle must create or activate only this page-owned service instance and must dispose it before the page disappears:

```js
onBeforeUnmount(() => {
  googleAuthService.dispose()
})
```

The Google credential callback receives `response.credential` and forwards that original encoded ID token without logging, decoding, modifying, or storing it. `response.select_by` may describe how Google selected the credential, but it is not authentication authority. Login Page must treat the workflow as successful only after `authenticateWithBackend` returns a confirmed application-session result.

`GoogleAuthService` does not:

- own the Login Page or LoginForm state;
- render a custom imitation of Google's button;
- verify provider signatures or claims in the browser;
- identify or link application accounts;
- create AuthStore state directly;
- create, refresh, or persist the application session;
- navigate after authentication.

The backend-authentication callback owns the request to this application's backend. The backend verifies the Google token, applies explicit account-linking policy, creates the normal application session, and returns the application result. Only after that result is confirmed does Login Page accept the session through the implemented AuthStore boundary, initialize Profile data, and navigate.

For the isolated debug page, use the separate `GoogleAuthServiceDebug` stage. It preserves pending, error, callback, and disposal boundaries, but starts directly from the existing SocialAuthButton and does not render a second provider button. It returns the documented example token locally; Login Page sends it to the loopback mock once. The example token is not a real provider credential. Do not load the real Google SDK or create an application session.

Source behavior inspected from the debug branch:

- `ai-trener-fronend-debug:prototypes/services/GoogleAuthService.js`
- `ai-trener-fronend-debug:docs/frontend/frontend-project-structure.md`
- `ai-trener-fronend-debug:docs/frontend/pages-and-routes.md`
- `ai-trener-fronend-debug:prototypes/tests/auth-prototypes.test.js`

### Page States

Support the following page-owned workflow states:

- idle;
- standard login pending;
- active MFA challenge;
- confirmation-code pending;
- invalid or expired MFA challenge;
- Google authentication pending;
- recoverable authentication error;
- provider unavailable;
- confirmed mock success.

Only one authentication workflow may be pending at a time. A pending Google workflow must not submit the standard login form, and a pending standard login must not be replaced by a social-login request.

### Error and Retry Behavior

- Present stable, user-safe messages instead of raw provider, adapter, or backend errors.
- Do not infer success, logout, or an invalid session from a temporary network-style mock failure.
- A recoverable failure returns the page to a retryable state.
- A provider-unavailable state keeps the user signed out and does not render a false success.
- A dismissed or cancelled provider interaction leaves the page signed out without inventing an error that the adapter did not report.
- A duplicate request keeps the first request authoritative and produces no second handoff.

### Debug Scenarios and Verification

Provide three primary page scenarios in the debug page registry:

1. **Standard login** — exercises a pending credential request, safe recoverable failure, retry, and the MFA challenge response for the primary fixture.
2. **Confirm login code** — exercises `ConfirmLoginForm`, invalid-code retry, expiry handling, single-use challenge verification, and the complete local user-data response without production session creation or protected navigation.
3. **Google authentication handoff** — exercises the provider-only event payload, one-click local example-token callback, one mock-backend request, pending guard, safe provider failure, retry, cleanup, and a confirmed local example response without session creation or protected navigation.

Verify that:

- Login Page renders the existing `LoginForm` and does not duplicate its fields or buttons;
- Login Page replaces `LoginForm` with the existing `ConfirmLoginForm` only after a valid debug challenge is returned;
- user data is unavailable before successful confirmation and is returned only after the active challenge accepts the correct code;
- the code is never logged, persisted, placed in a URL, or included in scenario output;
- standard login receives only email, password, and `recaptchaToken`;
- Google login receives only `{ provider: 'google' }`;
- Google login never emits or triggers the standard `submit` workflow;
- duplicate standard and Google requests are ignored while a request is pending;
- pending, error, and success outcomes are presented through the supported `LoginForm` contract;
- no password, reCAPTCHA token, provider credential, or raw authentication error appears in logs, scenario output, URLs, or storage;
- a successful local example response displays its account summary without creating a session or navigating to `/profile`;
- a failed example request never navigates and remains retryable when the failure is recoverable;
- unmounting removes provider-owned debug content and prevents late callbacks from changing state;
- keyboard focus and accessible names remain valid throughout both scenarios.

### References

- `docs/frontend/pages-and-routes.md`
- `docs/frontend/integration-contracts.md`
- `docs/frontend/component_additional-functionality/login-form.md`
- `prototypes/pages/LoginPage.vue`
- `prototypes/components/forms/LoginForm.vue`
- `prototypes/tests/auth-prototypes.test.js`
