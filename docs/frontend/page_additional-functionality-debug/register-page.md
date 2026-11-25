## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/example-apis/register.md
- docs/frontend/example-apis/social-auth.md

# Register Page

## Additional Description and Functionality

Register Page coordinates the registration workflows around the existing `RegisterForm` and `ConfirmLoginForm`. RegisterForm retains its existing fields, local validation, child-component composition, and presentation responsibilities. ConfirmLoginForm remains a presentation-only code collector configured with `purpose: 'registration'`. The page owns the service calls, challenge state, confirmed results, authenticated-data initialization, and navigation described below.

### RegisterForm Integration

Render one `RegisterForm` as the initial registration content. Handle its events as follows:

- `submit(payload)` starts password registration with the validated supported fields;
- `socialRegister({ provider, legalConsent })` starts the backend-owned OAuth registration flow for `google`, `facebook`, or `apple`;
- ignore duplicate password or provider actions while one registration workflow is pending;
- never reinterpret a Register event as Login intent.

RegisterForm does not call endpoints or receive a backend challenge id. The page must not inspect the form's local field state or add provider-derived identity fields to its emitted payloads.

### Password Registration

The password-registration workflow is:

1. Require valid first name, surname, email, password, matching confirm password, accepted Terms of Service, and a completed reCAPTCHA verification. Phone is optional; validate its format when supplied. The page does not collect a separate Privacy Policy acknowledgment and sends `false` for that optional value.
2. Obtain the current short-lived provider `recaptchaToken` through the existing reCAPTCHA field contract. A prototype checkbox or boolean is not a production token.
3. Do not start the request while verification is missing, expired, reset, invalid, or while another registration request is pending.
4. Send `POST /api/v1/auth/register` through the application authentication service with exactly this request body:

```json
{
  "firstName": "Alex",
  "lastName": "Morgan",
  "email": "player@example.com",
  "phone": "+359881234567",
  "password": "…",
  "legalConsent": {
    "termsOfService": true,
    "privacyPolicy": false
  },
  "recaptchaToken": "…"
}
```

`confirmPassword` is validated locally and is not transmitted. Do not add a user id, provider credential, reCAPTCHA secret, legal-document version, or server acceptance time to the frontend payload.

Omit `phone` when the field is empty. The [Register Example API](../example-apis/register.md) defines only the isolated Vite preview behavior; production uses the integration contract below.

The backend normalizes and validates every submitted value, requires Terms of Service acceptance, accepts either Boolean Privacy Policy acknowledgment value, records the applicable legal-document versions and acceptance time, verifies the reCAPTCHA token, hashes the password, checks account conflicts, and creates the account transactionally. An absent phone or false Privacy Policy acknowledgment must not block registration.

A successful `201 Created` result contains `success: true`, `status: 'verification_required'`, the created public user fields, and an email-verification challenge with `challengeId`, offered method, masked destination hint, and expiry. Retain only those non-secret challenge values in page memory and do not treat the result as an authenticated application session. Duplicate email or phone values and validation failures use the shared safe error contract. Never display, log, persist, or echo passwords or reCAPTCHA tokens.

After any expired, reset, invalid, rejected, or consumed reCAPTCHA token, clear the current verification value and require the user to complete reCAPTCHA again before retrying.

### Registration Confirmation Code

After password registration returns a valid email-verification challenge, replace RegisterForm with `ConfirmLoginForm`; do not render both forms simultaneously. Configure the component with `purpose: 'registration'`, the backend-offered `method`, masked `destinationHint`, and page-owned pending, error, and expired state.

When the component emits `submit({ method, code })`, send `POST /api/v1/auth/registration-challenges/{challengeId}/verify` in production. Keep invalid-code failures retryable while attempts remain; terminal challenges require a safe registration restart. The page never generates, delivers, compares, or verifies the code locally.

Only a successful verification establishes the application session. After that confirmed result, clear the code and challenge state, keep the access token only in memory, load `GET /api/v1/user/data` into `UserStore`, and navigate to the existing `/history` route through client-side router navigation without a full-page reload. History consumes the already-populated `UserStore` and must not repeat the initial user-data request. A `201 verification_required` result alone must never trigger navigation.

### Social Registration

Google, Facebook, and Apple registration use the backend-owned OAuth start and callback flow. They do not submit the password-registration payload and do not use `recaptchaToken`.

The social-registration workflow is:

1. Require Terms of Service acceptance before starting the provider flow. This page sends `privacyPolicy: false` because it has no separate acknowledgment control.
2. Send `POST /api/v1/auth/oauth/{provider}/start`, where `provider` is `google`, `facebook`, or `apple`, with exactly:

```json
{
  "intent": "register",
  "returnTo": "/history",
  "legalConsent": {
    "termsOfService": true,
    "privacyPolicy": false
  }
}
```

3. Use only the backend-returned `authorizationUrl` to navigate to the selected provider.
4. After the provider interaction, the provider sends its authorization `code` and `state` to `GET /api/v1/auth/oauth/{provider}/callback` on the backend.
5. The backend validates the OAuth state, exchanges the code with the provider, validates the provider response and verified-email signal, creates or safely links the account according to the existing account-linking rules, establishes the normal application session, and redirects to the validated internal destination.
6. Accept registration success only from the confirmed backend callback outcome. Then initialize the authenticated application data through the existing session flow before rendering the existing History route as ready.

Register Page must not send an OAuth provider token to `POST /api/v1/auth/register`, process the provider callback itself, exchange an OAuth code, validate provider claims in the browser, or store provider access tokens, ID tokens, state, secrets, or raw provider errors.

### Local Vite Example Behavior

Only in the isolated debug preview, use the [Register Example API](../example-apis/register.md) instead of the production registration endpoints. A single validated RegisterForm submit sends one `POST /api/register` request. A confirmed local challenge replaces RegisterForm with ConfirmLoginForm and sends the entered code to `POST /api/auth/registration-challenges/{challengeId}/verify`.

The local server owns the in-memory challenge, expiry, attempt limit, fixed tester-only code, and single-use behavior. The browser must not receive the expected code in an API response. After a successful local confirmation, accept the returned fictional user-data projection into debug-only in-memory state and navigate to `/history` through the client-side router, without a full-page reload, so the History page can consume that state. This is preview navigation, not a real account, email delivery, production session, refresh cookie, authorization grant, or protected production access.

Show pending and safe validation, conflict, invalid-code, expired-challenge, and service-error feedback only from actual local HTTP responses; do not use timers to imply success. The debug route may skip provider reCAPTCHA verification only locally. Do not add another registration field or control to support the example route.

For the Google registration entry, use the [Social Auth Example API](../example-apis/social-auth.md#google-registration-example-handoff). The existing Google button starts one debug service handoff and one local HTTP request with explicit registration intent and accepted legal consent. Facebook and Apple remain accessible visual registration entries in debug until their own local example contracts are documented. Do not silently reuse Login intent for any Register action.

### Page States and Error Handling

Support these page states: idle, validation error, reCAPTCHA required, submit pending, verification required, verification pending, invalid code, expired challenge, conflict, recoverable error, success initialization, and unavailable. Social registration additionally uses a provider handoff/pending state within the same page workflow.

Only one registration workflow may be pending at a time. Ignore duplicate submissions until the active request or provider handoff settles. Map backend field errors to the supported form presentation, use stable safe messages for form-level failures, preserve allowed non-secret input after a recoverable failure, and never infer success from a redirect or provider interaction that the backend has not confirmed.

### Ownership Boundary

Register Page owns registration orchestration, authentication-service calls, registration challenge state, pending and result state, acceptance of confirmed backend outcomes, authenticated-data initialization after an established session, and navigation to `/history`.

`RegisterForm` continues to own its visible fields, local field values, client-side validation, reCAPTCHA and social-button presentation, and field-level feedback. `ConfirmLoginForm` owns only the six-digit entry and immediate local validation; its established name does not give it Login workflow ownership when `purpose` is `registration`. The backend owns authoritative input validation, reCAPTCHA verification, legal-consent recording, password hashing, account creation and linking, registration challenge creation and verification, OAuth security, session creation, and authorization.
