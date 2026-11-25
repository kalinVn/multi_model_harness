## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/pages-and-routes.md
- docs/frontend/integration-contracts.md
- docs/frontend/component_additional-functionality/login-form.md
- docs/frontend/example-apis/login.md
- docs/frontend/example-apis/social-auth.md

# Login Page

## Additional Description and Functionality

Login Page remains available at `/login`, uses the Public Layout, and composes the existing `LoginForm` and `ConfirmLoginForm` feature components. It coordinates production authentication, MFA challenge verification, authenticated user-data initialization, and validated navigation without moving field values or field-level validation out of the forms.

### Page Ownership

Login Page owns:

- handling the `submit` and `socialLogin` events emitted by `LoginForm`;
- preventing duplicate authentication requests while an authentication workflow is pending;
- calling the application authentication service and accepting only confirmed backend outcomes;
- retaining an active MFA `challengeId` and the backend-offered verification methods for the duration of the challenge;
- showing `ConfirmLoginForm` only for an email or SMS method offered by the backend;
- handling the code submitted by `ConfirmLoginForm` and sending it to the active challenge-verification endpoint;
- mapping page-level pending, error, expired-challenge, and success outcomes to the supported form presentation contracts;
- accepting the established application session, keeping the access token in memory, loading `GET /api/v1/user/data` into `UserStore`, and navigating to `/history` through the client-side router without a full-page reload;
- disposing page-owned provider adapters, callbacks, requests, and rendered provider content when the page unmounts.

Login Page does not own input fields, field-level validation, reCAPTCHA presentation, social-button rendering, provider-token verification, authoritative credential verification, MFA code delivery, long-lived token persistence, or authorization decisions.

### LoginForm Integration

Render one `LoginForm` as the initial authentication content.

Wire its events as follows:

- `submit({ email, password, recaptchaToken })` starts the standard credential-login workflow through the production authentication service;
- `socialLogin({ provider })` starts the selected production social-authentication workflow;
- the Google social-login payload contains only `{ provider: 'google' }` and never contains email, password, or `recaptchaToken`;
- the page supplies pending state and safe form-level feedback through the existing `LoginForm` interface;
- field-level validation errors remain owned and displayed by `LoginForm`.

The page must not inspect or reach into the form's local field state. The password-login payload contains only email, password, and `recaptchaToken`; it has no name field. Do not log, persist, or place passwords, reCAPTCHA tokens, provider credentials, MFA codes, or access tokens in URLs or browser storage.

### Standard Login and MFA Challenge

1. Receive the validated `LoginForm` payload and send `POST /api/v1/auth/login` through the application authentication service.
2. Ignore duplicate credential or provider submissions while the current authentication request is pending.
3. When the backend establishes the application session without an additional challenge, accept that confirmed result through the implemented authentication boundary, load `GET /api/v1/user/data` into `UserStore`, and navigate to `/history` through the client-side router only after the user data are ready. Do not reload the document or repeat the initial user-data request on History.
4. When the backend returns an MFA challenge, retain its `challengeId`, expiry, and offered methods as page-owned transient state. Do not treat the challenge as an authenticated session.
5. Select only a backend-offered email or SMS method supported by `ConfirmLoginForm`. Pass the selected method and masked destination hint to the form, then replace the credential form with `ConfirmLoginForm`.
6. Receive `submit({ method, code })` from `ConfirmLoginForm` and send `POST /api/v1/auth/challenges/{challengeId}/verify` with the active challenge and selected method.
7. Keep invalid-code failures retryable while attempts remain. Treat an expired, exhausted, already-used, unavailable, or otherwise terminal challenge as no longer verifiable, clear its transient values, and return the user to a safe authentication state.
8. After successful challenge verification, clear the code and challenge state, keep the returned access token only in memory, load `GET /api/v1/user/data` into `UserStore`, and navigate to `/history` through the client-side router without a full-page reload. History consumes the already-populated store.

The page does not generate, resend, compare, or verify MFA codes locally. The backend owns challenge creation, delivery, expiry, attempt limits, one-time use, credential verification, session creation, and the authoritative error result.

### Google Authentication Handoff

The production Google workflow uses `GoogleAuthService` as the provider-SDK boundary consumed by Login Page. The service is separate from `LoginForm` and from the application's authentication service/API layer.

`GoogleAuthService` owns:

- loading and initializing Google Identity Services once for the mounted page lifecycle;
- rendering Google's supported sign-in button inside the mounted container supplied by `LoginForm`;
- forwarding the original provider-issued credential to the injected application-authentication callback;
- preventing a second provider handoff while the first backend request is pending;
- reporting initialization, missing-credential, duplicate-request, and backend-handoff failures through its error callback;
- deactivating callbacks and clearing service-owned button containers when disposed.

Its browser configuration uses the public `VITE_GOOGLE_CLIENT_ID`. A Google Client Secret must never be placed in frontend source, browser environment output, page state, or storage.

The service interface is:

- `initialize()` — load and initialize Google Identity Services once;
- `renderButton(container, options)` — render the official provider button into a valid mounted element after initialization;
- `dispose()` — deactivate the service, invalidate late callbacks, clear pending state, and remove service-owned rendered content.

Login Page creates one service instance for its mounted lifecycle and supplies the public client id, the implemented backend-authentication callback, `onAuthenticated(result)`, and `onError(error)`. The injected callback is an application-authentication function, not a second provider service. It keeps provider SDK lifecycle separate from backend authentication and session establishment.

Conceptual wiring:

```js
const googleAuthService = new GoogleAuthService({
  clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
  authenticateWithBackend: idToken =>
    authenticationApi.authenticateGoogleIdToken(idToken),
  onAuthenticated: result => handleConfirmedApplicationSession(result),
  onError: error => presentSafeGoogleError(error),
})
```

The names in this example describe responsibilities. Bind them to implemented application interfaces and authoritative integration contracts; do not invent production API or store methods solely to match the example.

The callback sequence is:

```text
LoginForm socialLogin({ provider: 'google' })
  -> Login Page initializes GoogleAuthService
  -> GoogleAuthService renders the official Google button
  -> Google invokes the configured credential callback
  -> GoogleAuthService passes the original credential to the application backend boundary
  -> the backend verifies the credential and establishes the application session
  -> onAuthenticated(result) updates the page workflow
  -> Login Page loads GET /api/v1/user/data
  -> Login Page uses client-side router navigation to /history without a full-page reload
```

The page must not decode, modify, log, or persist the Google credential. It treats the workflow as successful only after the application backend confirms the session. After that confirmation, the page loads the user-data snapshot into `UserStore` and uses the same client-side router transition to `/history`, without reloading the document. `GoogleAuthService` does not verify provider claims in the browser, identify or link application accounts, create store state directly, persist the application session, load user data, or navigate.

Dispose the page-owned service before the page disappears so late callbacks cannot update state or navigate.

### Page States

Support these page-owned workflow states:

- idle;
- credential login pending;
- MFA challenge required;
- MFA verification pending;
- invalid MFA code with retry available;
- expired or terminal MFA challenge;
- Google authentication pending;
- provider unavailable;
- authenticated user-data initialization pending;
- recoverable authentication error;
- confirmed authentication followed by navigation.

Only one authentication workflow may be pending at a time. A pending provider workflow must not submit the credential form, and a pending credential or MFA workflow must not be replaced by a social-login request.

### Error and Retry Behavior

- Present stable, user-safe messages instead of raw provider, service, or backend errors.
- Never infer successful authentication or an invalid session from a temporary network failure.
- Preserve allowed non-secret form context after a recoverable failure and clear secrets when their lifecycle ends.
- A provider-unavailable or cancelled-provider state keeps the user signed out.
- A duplicate request leaves the first request authoritative and produces no second handoff.
- A failed `GET /api/v1/user/data` initialization must not navigate to a protected page with incomplete authenticated state; follow the shared session recovery contract.

### References

- `docs/frontend/pages-and-routes.md`
- `docs/frontend/integration-contracts.md`
- `docs/frontend/component_additional-functionality/login-form.md`
- `docs/frontend/example-apis/login.md`
- `docs/frontend/example-apis/social-auth.md`
- `prototypes/pages/LoginPage.vue`
- `prototypes/components/forms/LoginForm.vue`
- `prototypes/components/forms/ConfirmLoginForm.vue`
- `prototypes/design/components/forms/confirm-login-form.html`
- `prototypes/tests/auth-prototypes.test.js`
