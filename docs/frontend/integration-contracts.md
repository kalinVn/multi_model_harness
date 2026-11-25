## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

None

# Frontend Integration Contract Examples

## Shared response and error shape

Successful JSON responses use the resource-specific shape below. Failed requests use:

```json
{
  "error": {
    "code": "SESSION_EXPIRED",
    "success": false,
    "message": "Your session has expired.",
    "requestId": "opaque-server-generated-id",
    "retryable": false,
    "errors": {}
  }
}
```

`message` is safe to display; clients must branch on `code`, never parse message text. `errors` is optional. Do not expose stack traces, tokens, provider secrets, or internal diagnostics.

## Authentication and application session

Use same-origin HTTPS requests and an HttpOnly, Secure, SameSite session cookie. The browser does not persist access or refresh tokens in local storage. State-changing cookie-authenticated requests require the backend's CSRF protection. The backend remains authoritative for authentication and authorization.

Authentication values have separate purposes and are not interchangeable:

- `recaptchaToken` is a short-lived anti-abuse proof obtained from the reCAPTCHA provider for the email/password Login or Register submission. The backend verifies it once and does not use it as an application session token.
- OAuth `code` and `state` belong only to the Google, Facebook, or Apple redirect/callback flow. The provider sends them to the backend callback; they are not Login form fields.
- `challengeId` identifies a short-lived Login MFA challenge after the password and reCAPTCHA step succeeds. It contains no OTP and grants no session by itself.
- A registration `challengeId` identifies a separate short-lived email-verification challenge after password registration. It contains no code, grants no session by itself, and is accepted only by the registration-verification endpoint.
- `accessToken` authorizes application API calls through the `Authorization: Bearer <accessToken>` header.
- The refresh token is an application-session credential stored only in a Secure, HttpOnly, SameSite cookie.

Example endpoints:

### Google, Facebook, and Apple OAuth

- `POST /api/v1/auth/oauth/{provider}/start`, where `provider` is `google`, `facebook`, or `apple`.

  Login request:

  ```json
  {
    "intent": "login",
    "returnTo": "/dashboard"
  }
  ```

  Register request also confirms the legal choice made on the Register page:

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

  The backend validates `provider`, permits only an internal allowlisted `returnTo`, creates short-lived OAuth state and PKCE values plus an OIDC nonce where supported, stores them in a Secure, HttpOnly, SameSite cookie, and returns a provider authorization URL. The password form and provider client secrets are never transmitted to Google, Facebook, or Apple by frontend code.

  ```json
  {
    "authorizationUrl": "https://provider.example/authorize?…"
  }
  ```

- `GET /api/v1/auth/oauth/{provider}/callback` receives the provider's authorization code and state. The backend validates state, exchanges the code directly with the selected provider, validates the provider response and verified-email signal, and reads the permitted identity claims such as provider subject, name, and email. Provider access and ID tokens stay on the backend and are never placed in application URLs or browser storage.

  For `login`, the backend signs in the already-linked identity. For `register`, it creates or safely links the account only after the required Terms of Service acceptance; Privacy Policy acknowledgment is optional and may be `false`. Ambiguous email matches require an explicit account-linking flow rather than automatic linking. On success it issues the normal Secure refresh cookie and redirects directly to the validated internal `returnTo` route; the redirect contains no access token and requires no dedicated frontend callback page. When that protected destination is entered without a memory access token, the global authentication guard performs one session-bootstrap call to `POST /api/v1/auth/refresh`, including the backend-required CSRF proof, stores the returned access token only in memory, and only then calls `GET /api/v1/user/data` before resolving navigation. If bootstrap returns `401`, the guard clears authentication and user state and redirects to Login instead of treating the cookie or redirect as an authenticated session. Cancelled, denied, invalid-state, provider-error, and account-link-required outcomes redirect to `/login` with only an allowlisted `oauthStatus` value (`cancelled`, `denied`, `invalid_state`, `provider_error`, or `account_link_required`); tokens and raw provider errors never appear in the URL.


- `POST /api/v1/auth/login`
  — request body:

  ```json
  {

    "email": "player@example.com",
    "password": "…",
    "recaptchaToken": "…"
  }
  ```

  After successful authentication, the backend issues a short-lived JWT access token and returns:

  — response body:

  ```json
  {
    "accessToken": "…",
    "tokenType": "Bearer",
    "expiresIn": 900,
    "user": {
      "id": "…",
      "displayName": "…"
    }
  }
  ```

  A long-lived refresh token is issued separately as an `HttpOnly`, `Secure`, `SameSite` cookie and is never exposed to frontend JavaScript.

  If multi-factor authentication is required, the endpoint returns a challenge instead of tokens, for example:

  ```json
  {
    "challengeId": "…",
    "methods": [
      "totp",
      "email",
      "sms"
    ]
  }
  ```

  Invalid credentials return `401 Unauthorized`.

  `POST /api/v1/auth/challenges/{challengeId}/verify` completes the identified Login MFA challenge.

  — request body:

  ```json
  {
    "method": "totp",
    "code": "123456"
  }
  ```

  The `challengeId` is sent in the URL, while `method` must be one of the methods returned by Login. A successful verification returns `200 OK`, issues the refresh token as a Secure, HttpOnly, SameSite cookie, and returns:

  — response body:

  ```json
  {
    "accessToken": "…",
    "tokenType": "Bearer",
    "expiresIn": 900,
    "user": {
      "id": "…",
      "displayName": "…"
    }
  }
  ```

  The backend verifies ownership, expiry, attempt limits, and single use before issuing tokens. Invalid codes return `401 Unauthorized`; malformed requests and methods that were not offered for that challenge return `400 Bad Request`; expired, exhausted, or already-used challenges return `410 Gone`. This endpoint is part of Login MFA and is unrelated to reCAPTCHA and OAuth callbacks.

- `POST /api/v1/auth/refresh`
  — request:

  ```http
  POST /api/v1/auth/refresh HTTP/1.1
  Cookie: refresh_token=<HttpOnly browser cookie>
  X-CSRF-Token: <CSRF proof>
  Content-Length: 0
  ```

  The request has no JSON body. The browser sends the current refresh token only through its Secure, HttpOnly, SameSite cookie. The frontend also supplies the backend's required CSRF proof for this state-changing cookie-authenticated request; it never reads, copies, or serializes the refresh token.

  Successful refresh returns `200 OK`:

  ```http
  HTTP/1.1 200 OK
  Content-Type: application/json
  Set-Cookie: refresh_token=<rotated token>; HttpOnly; Secure; SameSite=<policy>
  ```

  ```json
  {
    "accessToken": "…",
    "tokenType": "Bearer",
    "expiresIn": 900
  }
  ```

  The backend rotates the refresh token on every successful use, invalidates the previous value, and sends the replacement in a new Secure, HttpOnly, SameSite cookie. Missing, invalid, expired, revoked, or reused refresh tokens return `401 Unauthorized` without an access token.

- `POST /api/v1/auth/logout`
  — request:

  ```http
  POST /api/v1/auth/logout HTTP/1.1
  Cookie: refresh_token=<HttpOnly browser cookie>
  X-CSRF-Token: <CSRF proof>
  Content-Length: 0
  ```

  The request has no JSON body. The browser sends the refresh-token cookie automatically, together with the required CSRF proof.

  Successful logout returns:

  ```http
  HTTP/1.1 204 No Content
  Set-Cookie: refresh_token=; Max-Age=0; HttpOnly; Secure; SameSite=<policy>
  ```

  A `204 No Content` response intentionally has no JSON body. The backend revokes the current refresh token or token family and expires the refresh-token cookie. The operation is idempotent: repeating it leaves the session signed out and returns no token or user data.

- `POST /api/v1/auth/register`
  — request body:

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

  `confirmPassword` is validated by the frontend but is not transmitted. `phone` is optional and omitted when empty; if supplied, the backend validates and normalizes it. The backend validates and normalizes every other supplied field, requires `legalConsent.termsOfService` to be `true`, accepts either Boolean value for the optional `legalConsent.privacyPolicy` acknowledgment, records the applicable legal-document versions and server acceptance time, verifies the reCAPTCHA token, hashes the password, and creates the account in one transaction. An absent phone or `false` Privacy Policy acknowledgment must not block registration.

  Successful creation returns `201 Created`:

  ```json
  {
    "success": true,
    "status": "verification_required",
    "user": {
      "id": "…",
      "firstName": "Alex",
      "lastName": "Morgan",
      "email": "player@example.com",
      "phone": "+359881234567"
    },
    "verification": {
      "type": "email",
      "required": true,
      "challengeId": "…",
      "methods": ["email"],
      "destinationHint": "p***@example.com",
      "expiresIn": 600
    }
  }
  ```

  The created account remains pending and no application session is issued until the registration challenge is verified. No password, password hash, reCAPTCHA token, provider secret, verification code, or internal verification token is returned. Duplicate email or phone values use the shared error envelope with a stable conflict code. Validation failures use field errors without echoing password values.

- `POST /api/v1/auth/registration-challenges/{challengeId}/verify`
  completes the identified post-registration verification challenge. This endpoint is separate from Login MFA and never accepts a Login challenge id.

  — request body:

  ```json
  {
    "method": "email",
    "code": "123456"
  }
  ```

  `method` must be one of the methods returned by the registration response. A successful verification returns `200 OK`, marks the pending account as verified, issues the refresh token as a Secure, HttpOnly, SameSite cookie, and returns:

  ```json
  {
    "accessToken": "…",
    "tokenType": "Bearer",
    "expiresIn": 900,
    "user": {
      "id": "…",
      "displayName": "Alex"
    }
  }
  ```

  The backend verifies challenge ownership, purpose, expiry, attempt limits, and single use before establishing the normal application session. Invalid codes return `401 Unauthorized`; malformed requests or methods that were not offered return `400 Bad Request`; expired, exhausted, or already-used challenges return `410 Gone`. After success, the frontend clears the registration challenge, keeps the access token only in memory, loads `GET /api/v1/user/data` into `UserStore`, and uses client-side router navigation to the existing History route without a full-page reload. History consumes that populated store and does not repeat the initial user-data request.

For Login and Register, `recaptchaToken` is a short-lived provider token, not the prototype checkbox value. The backend verifies it with the provider, including the expected action and hostname, before checking credentials or creating an account. Missing, expired, replayed, or invalid tokens are rejected; provider secrets never enter frontend code.

- Protected API endpoints require the access token in the HTTP header `Authorization: Bearer <accessToken>`. The backend validates the JWT signature, expiration time, issuer/audience where applicable, and required authorization claims before processing the request.

- Google, Facebook, and Apple sign-in use the backend-owned OAuth start/callback contracts above and issue the same application session used by password authentication. Provider client secrets and provider tokens are never exposed to frontend code.

`401 Unauthorized` means that the access token is missing, invalid, or expired. `403 Forbidden` means that the authenticated principal lacks permission. These meanings are part of the HTTP contract; frontend recovery and navigation behavior are defined in `frontend.md`.

After Login, Login MFA verification, registration verification, or OAuth establishes the authenticated application session, the frontend calls `GET /api/v1/user/data` once and stores the complete response in the global `UserStore`. For password Login, MFA verification, registration verification, and any page-owned provider flow that returns a confirmed session to the mounted application, the page then uses client-side router navigation to `/history` without a full-page reload; History consumes the populated store and does not repeat the initial request. A backend-owned OAuth redirect resolves its validated `returnTo` route through the authentication guard and must not trigger an additional frontend reload after that route is ready. Authentication responses remain focused on session establishment and do not duplicate the user-data response.

## Training session and analysis transport

### Training session endpoints

- `POST /api/v1/training/sessions/create`

  Creates a new training session for the authenticated user. The authenticated principal comes from the access token; the request contains no `userId`.

  — request:

  ```http
  POST /api/v1/training/sessions/create HTTP/1.1
  Authorization: Bearer <accessToken>
  Content-Length: 0
  ```

  The request has no JSON body.

  — response body:

  ```json
  {
    "sessionId": "session_123",
    "status": "ready",
    "analysisWebSocketUrl": "wss://example.com/…"
  }
  ```

  `sessionId` uniquely identifies this training session. `status: "ready"` means that the session was created successfully and is ready for live analysis. `analysisWebSocketUrl` is a short-lived authenticated WebSocket URL generated by the backend.

  `analysisWebSocketUrl` is backend-issued and must not be replaced with a client-constructed or untrusted host. If the live connection drops, the frontend pauses frame sending and performs a bounded number of automatic reconnection attempts for the same active `sessionId`; it must not create another session. A successful reconnect resumes that session and preserves its existing stroke sequence.

  The backend records the interval from detection of the active connection loss until successful reconnection as a session pause. That interval remains associated with the session but is excluded from active training duration. A transient reconnect is not shown as a terminal disconnected state; the frontend exposes an unavailable/disconnected state only after the bounded attempts fail.

- `POST /api/v1/training/sessions/{sessionId}/complete`

  Completes an existing training session after the user finishes normally. The URL identifies the session that must be finalized.

  — request:

  ```http
  POST /api/v1/training/sessions/{sessionId}/complete HTTP/1.1
  Authorization: Bearer <accessToken>
  Content-Length: 0
  ```

  The request has no JSON body. The backend verifies that the session belongs to the authenticated user and finalizes the feedback and summary already associated with that session.

  — response body:

  ```json
  {
    "sessionId": "session_123",
    "status": "complete",
    "completedAt": "2026-10-12T09:00:00Z",
    "summary": {
      "successfulStrokes": 1,
      "detectedMistakes": 0,
      "recommendations": []
    }
  }
  ```

  A successful response means the canonical session result has been finalized and persisted for History and Session Review. The operation is idempotent for the same training session.

- `POST /api/v1/training/sessions/{sessionId}/abandon`

  Ends the identified active training session with `status: "incomplete"` instead of completing it.

  — request:

  ```http
  POST /api/v1/training/sessions/{sessionId}/abandon HTTP/1.1
  Authorization: Bearer <accessToken>
  Content-Length: 0
  ```

  The request has no JSON body.

  — response body:

  ```json
  {
    "sessionId": "session_123",
    "status": "incomplete",
    "endedAt": "2026-10-12T09:00:00Z"
  }
  ```

  The incomplete result may be returned by History but is never equivalent to a completed session. The operation is idempotent: repeating it for an already abandoned session leaves it incomplete and does not create another session.

### Live analysis WebSocket

The authenticated WebSocket URL is short-lived and issued by the backend; the frontend does not construct it from an untrusted host. The example wire protocol sends JSON frame metadata immediately before the matching binary JPEG message:

#### Client-to-server frame message

```json
{
  "type": "frame",
  "frameId": "…",
  "capturedAt": "…",
  "mimeType": "image/jpeg",
  "width": 640,
  "height": 360
}
```

Field contract:

- `type` is required and equals `frame`.
- `frameId` is a required opaque identifier for this transmitted frame.
- `capturedAt` is the required UTC ISO-8601 capture timestamp.
- `mimeType` is required and equals `image/jpeg` for this protocol version.
- `width` and `height` are required positive integer pixel dimensions of the encoded image.

The metadata is the first WebSocket message for one frame and contains no image bytes. The immediately following message contains the matching raw JPEG bytes:

```text
WebSocket message 1 (text):   JSON frame metadata
WebSocket message 2 (binary): <raw JPEG bytes for that frame>
```

The JPEG is binary, not Base64 or a JSON field. Metadata and binary payload form an ordered pair; another frame's metadata must not be interleaved between them.

Frames are analysis inputs and do not individually imply a feedback event. Stroke-level feedback may be returned through the message below; backend aggregation and stroke-completion detection are not part of this wire contract.

#### Server-to-client `player_feedback` message

Server-to-client text messages use a versioned envelope. A completed-stroke feedback event uses server-issued identities and contains only supported feedback:

```json
{
  "version": 1,
  "type": "player_feedback",
  "sessionId": "session_123",
  "payload": {
    "strokeId": "stroke_42",
    "strokeNumber": 12,
    "kind": "detected_mistake",
    "occurredAt": "2026-10-12T09:00:00Z",
    "confidence": 0.91,
    "text": "Contact the ball earlier.",
    "audioUrl": "https://api.example.com/temporary-audio/event_45"
  }
}
```

Field contract:

- `version` is required and equals `1`, the current WebSocket schema version.
- `type` is required and equals `player_feedback`.
- `sessionId` is required and identifies the active training session.

- `payload.strokeId` is a required opaque, server-generated identifier for one detected tennis stroke. Feedback events for the same stroke use the same `strokeId`; different strokes use different identifiers.
- `payload.strokeNumber` is a required positive ordinal assigned by the backend to the detected stroke within the training session. It starts at `1` and increases for each newly detected stroke; it is not a frame number or frame count.
- `payload.kind` is required and is one of `successful_stroke`, `detected_mistake`, or `recommendation`.
- `payload.occurredAt` is a required UTC ISO-8601 timestamp associated with the feedback/stroke event.
- `payload.confidence` is a required number from `0` to `1` expressing the backend's confidence in this stroke-level result.
- `payload.text` is optional human-readable coaching feedback. When present, it is the canonical persisted coaching content.
- `payload.audioUrl` is optional. When present, it is an authenticated, temporary, expiring URL for backend-generated Text-to-Speech audio corresponding to `text`. Permanent generated-audio persistence is not guaranteed; audio may be regenerated later from persisted text.

`strokeId`, `strokeNumber`, `kind`, `occurredAt`, `confidence`, and `text` form the stable feedback content for the completed stroke. The optional `audioUrl` is transient delivery metadata, is excluded from canonical summaries, and may be omitted or newly issued when the feedback is retrieved later.

`frameId` remains only in the client-to-server frame metadata so the transport can identify the metadata/JPEG pair. It is not included in aggregated `player_feedback` or the persisted canonical session summary.

Other valid server message discriminators are `analysis_started`, `analysis_unavailable`, `analysis_error`, and `session_status`; their payload schemas require backend confirmation before use.

#### Client-to-server `stop_analysis` message

Analysis stop uses this message:

```json
{ "version": 1, "type": "stop_analysis", "sessionId": "…" }
```

`version` is the schema version, `type` is the `stop_analysis` discriminator, and `sessionId` identifies the active session. After accepting it, the server must not treat later frame messages as part of active analysis. The binary JPEG/WebSocket schemas remain proposed contracts requiring backend adoption or versioned replacement.

## Session History and Session Review

### Session History

The unified user-data response contains the initial History collection used by Dashboard and History. The dedicated list endpoint remains available for pagination, an explicit refresh, and loading data beyond the initial collection; successful responses update the `sessionHistory` section of the global `UserStore` rather than a second history store.

- `GET /api/v1/training/sessions?cursor={opaqueCursor}&limit={1..50}`

  Returns the authenticated user's training sessions. `cursor` is an optional opaque pagination cursor. `limit` is optional and must be an integer from `1` to `50`.

  — request body:

  The request has no JSON body.

  — response body:

  ```json
  {
    "items": [
      {
        "id": "session_123",
        "startedAt": "2026-10-12T08:30:00Z",
        "durationSeconds": 1800,
        "status": "complete",
        "historyStatus": "reviewed",
        "summary": null
      }
    ],
    "nextCursor": null
  }
  ```

  `status` is the training workflow result and is either `complete` or `incomplete`. `historyStatus` is the History presentation classification and is `reviewed`, `sample`, or `incomplete`; the backend supplies it explicitly, and the frontend must not infer `sample` or `reviewed` from `status` or `summary`. `durationSeconds` is the canonical duration field used in both this endpoint and `UserStore.sessionHistory`; the page formats it into minutes for display. `nextCursor` is `null` when there is no next page.

  — relevant errors/status codes:

  Authorization failures and invalid query parameters use the shared error envelope with the applicable HTTP status code.

### Session Review

- `GET /api/v1/training/sessions/{sessionId}/review`

  Returns the authorized review for the training session identified by `sessionId`, including persisted server-issued feedback, the canonical successful-stroke/mistake/recommendation summary, supported measurements, and optional key moments.

  — request body:

  The request has no JSON body.

  — response body:

  ```json
  {
    "sessionId": "session_123",
    "status": "complete",
    "summary": {
      "successfulStrokes": 1,
      "detectedMistakes": 1,
      "recommendations": [
        "Contact the ball earlier."
      ]
    },
    "feedbackEvents": [
      {
        "strokeId": "stroke_42",
        "strokeNumber": 12,
        "kind": "detected_mistake",
        "occurredAt": "2026-10-12T09:00:00Z",
        "confidence": 0.91,
        "text": "Contact the ball earlier.",
        "audioUrl": null
      }
    ],
    "measurements": [],
    "keyMoments": []
  }
  ```

  Each supported measurement includes its value, unit, time range, and server-defined provenance/confidence. Missing evidence is `null` with an availability reason. `keyMoments` is optional. A persisted review does not depend on a temporary `audioUrl`; it may be `null` or omitted.

  — relevant errors/status codes:

  Authorization failures, an unknown or inaccessible `sessionId`, and unavailable review data use the shared error envelope with the applicable HTTP status code.

## Checkout and billing

The frontend sends plan identifiers, never amounts or card credentials, to the backend:

- `POST /api/v1/billing/checkout-sessions`

  Creates a provider-hosted checkout session for the selected plan. `returnPath` must be a validated internal application path.

  — request body:

  ```json
  {
    "planId": "performance",
    "provider": "paypal",
    "returnPath": "/subscription"
  }
  ```

  `provider` is required and must be one of `stripe` or `paypal`. The backend validates the selected provider and creates the corresponding hosted checkout session; the frontend never calls Stripe or PayPal privileged APIs directly.

  — response body:

  ```json
  {
    "provider": "paypal",
    "checkoutUrl": "https://provider.example/…",
    "checkoutSessionId": "checkout_123"
  }
  ```

  The frontend redirects the user to the returned `checkoutUrl`. The payment provider, not the frontend, collects and processes card or other payment credentials.

  — relevant errors/status codes:

  Invalid plans, invalid return paths, authorization failures, and provider failures use the shared error envelope with the applicable HTTP status code.

- `GET /api/v1/billing/checkout-sessions/{checkoutSessionId}`

  Returns the backend-verified state of the checkout session identified by `checkoutSessionId`. Query parameters or browser redirects alone never prove payment success.

  — request body:

  The request has no JSON body.

  — response body:

  ```json
  {
    "status": "pending",
    "displayText": "Payment confirmation is pending."
  }
  ```

  `status` is one of `pending`, `succeeded`, `cancelled`, `failed`, or `expired`. `displayText` is safe to display to the user.

  — relevant errors/status codes:

  Authorization failures, an unknown or inaccessible `checkoutSessionId`, and provider availability failures use the shared error envelope with the applicable HTTP status code.

- `GET /api/v1/subscriptions/status`

  Returns the authenticated user's authoritative subscription status. Initial Subscription page data comes from the unified user-data response; this endpoint remains for checkout-return verification and explicit refreshes. A successful response updates the `subscription` section of the global `UserStore`.

  — request body:

  The request has no JSON body.

  — response body:

  ```json
  {
    "status": "active",
    "planId": "performance",
    "currentPeriodEndsAt": "2026-10-26T00:00:00Z",
    "paymentMethodDisplay": "Not connected",
    "billingManagementAvailable": false
  }
  ```

  Supported status values include `pending`, `active`, `paid`, and `failed`. A successful response replaces `UserStore.subscription` with the normalized returned object.

  — relevant errors/status codes:

  Authorization and subscription-status lookup failures use the shared error envelope with the applicable HTTP status code.

- `POST /api/v1/manage-billing/customer-portal-sessions`

  Creates a provider-hosted customer portal session for the Subscription page's Manage billing action. `returnPath` must be a validated internal application path.

  — request body:

  ```json
  {
    "returnPath": "/subscription"
  }
  ```

  — response body:

  ```json
  {
    "portalUrl": "https://provider.example.com/customer-portal/…"
  }
  ```

  — relevant errors/status codes:

  Invalid return paths, authorization failures, missing provider-customer state, and provider failures use the shared error envelope with the applicable HTTP status code.

- `POST /api/v1/billing/webhooks/stripe`
- `POST /api/v1/billing/webhooks/paypal`

  These are backend-only endpoints called directly by Stripe and PayPal respectively. The frontend never calls them.

  — request body:

  The body is the provider-defined event payload accompanied by that provider's signature or verification metadata. Its schema is intentionally not duplicated in this frontend-facing contract.

  — response body:

  No response body is consumed by the frontend. Provider acknowledgement and error responses are part of the backend/provider integration contract.

  — relevant errors/status codes:

  The backend verifies the provider signature and processes accepted events idempotently. Invalid signatures and duplicate or failed event processing are handled entirely by the backend.

The checkout flow is:

1. The frontend calls `POST /api/v1/billing/checkout-sessions` with `planId`, the selected `provider` (`stripe` or `paypal`), and the validated internal `returnPath`.
2. The backend creates the provider-hosted checkout session and returns `checkoutUrl` and `checkoutSessionId`.
3. The frontend redirects the user to `checkoutUrl`.
4. The payment provider collects and processes the payment information.
5. The provider redirects the user back to the validated internal `returnPath`.
6. The frontend calls `GET /api/v1/billing/checkout-sessions/{checkoutSessionId}`.
7. The backend returns the authoritative checkout status: `pending`, `succeeded`, `cancelled`, `failed`, or `expired`.
8. When appropriate, the frontend refreshes the authoritative subscription state through `GET /api/v1/subscriptions/status`.
9. Stripe and PayPal webhook processing remains backend-to-backend through their dedicated billing webhook endpoints; the frontend never calls those endpoints.

The provider hosts payment fields and receives card data. Raw card data must not be transmitted to or stored by the frontend application. Provider callbacks/webhooks are backend-verified and idempotent; browser redirects and query parameters are not payment confirmation.

## Contract adoption

Backend and product owners must confirm endpoint names, required fields, units, bounds, retention, authentication, rate limits, idempotency, feedback-event provenance, session completion, and error mappings before connecting live services. Until then, frontend contract tests may use fixtures matching these proposed examples.

## Authenticated application data and persisted user updates

All endpoints in this section require the authenticated application session and use the shared error envelope. `UserStore` is the single frontend source of truth for the returned persisted user/application data. Pages may keep unsaved form drafts locally, but they must not create another authoritative copy of server state.

### Get user data

- `GET /api/v1/user/data`

  Returns all persisted user-specific data required to initialize the authenticated application after Login, MFA verification, OAuth session establishment, or a full application reload with a recoverable session. This replaces the former initial-load `GET /api/v1/dashboard`, `GET /api/v1/users/me`, and `GET /api/v1/users/me/preferences` requests.

  — request:

  ```http
  GET /api/v1/user/data HTTP/1.1
  Authorization: Bearer <accessToken>
  ```

  The request has no JSON body. The backend identifies the current user from the validated access token; the frontend does not send a separate `userId`.

  — response body:

  ```json
  {
    "account": {
      "id": "user_123",
      "mfaEnabled": false,
      "passwordChangedAt": null
    },
    "personalInformation": {
      "firstName": "Alex",
      "lastName": "Morgan",
      "username": "alexmorgan",
      "displayName": "Alex",
      "email": "player@example.com",
      "emailVerified": true,
      "phoneCountryCode": "+359",
      "phone": "888123456",
      "phoneVerified": false,
      "dateOfBirth": null,
      "country": null,
      "city": null,
      "bio": null
    },
    "subscription": {
      "status": "active",
      "planId": "performance",
      "currentPeriodEndsAt": "2026-10-26T00:00:00Z",
      "paymentMethodDisplay": "Not connected",
      "billingManagementAvailable": false
    },
    "dashboard": {
      "statistics": {
        "sessionsCountThisMonth": 8,
        "practiceTime": 12600,
        "lastSession": "2026-10-11T18:30:00Z"
      }
    },
    "sessionHistory": {
      "items": [
        {
          "id": "session_123",
          "startedAt": "2026-10-12T08:30:00Z",
          "durationSeconds": 2520,
          "status": "complete",
          "historyStatus": "reviewed",
          "summary": null
        },
        {
          "id": "session_122",
          "startedAt": "2026-10-08T16:00:00Z",
          "durationSeconds": 2100,
          "status": "complete",
          "historyStatus": "reviewed",
          "summary": null
        },
        {
          "id": "session_121",
          "startedAt": "2026-10-03T07:15:00Z",
          "durationSeconds": 2880,
          "status": "incomplete",
          "historyStatus": "incomplete",
          "summary": null
        }
      ]
    },
    "settings": {
      "notifications": {
        "trainingReminders": true,
        "sessionSummaries": true,
        "productUpdates": false,
        "notificationChannel": "email",
        "reminderTime": "18:00"
      },
      "privacy": {
        "saveVideos": false,
        "videoRetention": "30",
        "historyVisibility": "private",
        "performanceAnalytics": true,
        "optionalTelemetry": false
      }
    }
  }
  ```

  `sessionHistory.items` uses the same item schema as `GET /api/v1/training/sessions`: `durationSeconds` is canonical, and `historyStatus` explicitly supplies the History label classification. This allows pagination or refresh responses to replace or append store items without field normalization or status inference.

  `sessionHistory.items` is the single initial session collection used by both Dashboard recent activity and History; the response does not duplicate those session records inside `dashboard`. Empty arrays and `null` values are valid data states, not transport errors.

  Physical device identifiers, camera/microphone availability, permission state, the currently selected browser device, audio-output routing, and unsaved avatar previews are intentionally absent. They remain local browser state.

  On success, the frontend replaces the complete authenticated-data snapshot in `UserStore` atomically. It does not distribute the sections into additional Dashboard, Profile, Settings, Subscription, or History stores.

  — relevant errors/status codes:

  Authorization and user-data availability failures use the shared error envelope with the applicable HTTP status code. A failed initial load leaves authenticated application data unavailable; pages must not issue the removed GET requests as independent fallbacks.

### Profile update and get data endpoints

All endpoints in this section require the authenticated application session and use the shared error envelope. `UserStore` is the single frontend source of truth for the returned persisted user/application data.

### Get user data

- `GET /api/v1/user/data`

Returns all persisted user-specific data required to initialize the authenticated application after Login, MFA verification, OAuth session establishment, or a full application reload with a recoverable session.

The request has no JSON body. The backend identifies the current user from the validated access token; the frontend does not send a separate `userId`.

### Profile update endpoints

- `PATCH /api/v1/user/personal-information`

Updates the authenticated user's Personal Information form. Omitted writable fields remain unchanged.

— request body:

```json
{
  "firstName": "Alex",
  "lastName": "Morgan",
  "username": "alexmorgan",
  "displayName": "Alex",
  "email": "player@example.com",
  "phoneCountryCode": "+359",
  "phone": "888123456",
  "dateOfBirth": null,
  "country": null,
  "city": null,
  "bio": null
}
```

`emailVerified` and `phoneVerified` are server-owned values and are not accepted in this request.

### Settings update endpoints

- `PATCH /api/v1/user/preferences/notifications`

Updates the authenticated user's Notifications form.

— request body:

```json
{
  "trainingReminders": true,
  "sessionSummaries": true,
  "productUpdates": false,
  "notificationChannel": "email",
  "reminderTime": "18:00"
}
```

- `PATCH /api/v1/user/preferences/privacy`

Updates the authenticated user's Privacy & Data form.

— request body:

```json
{
  "saveVideos": false,
  "videoRetention": "30",
  "historyVisibility": "private",
  "performanceAnalytics": true,
  "optionalTelemetry": false
}
```

### Security and data-management actions

- `PATCH /api/v1/user/save-password`

Changes the authenticated user's password as a separate security action.

— request body:

```json
{
  "currentPassword": "…",
  "newPassword": "…"
}
```

`confirmPassword` is checked by the frontend and is not transmitted. Password values are never persisted in `UserStore`.

- `POST /api/v1/user/data-exports`

Starts a data export for the authenticated user.

- `GET /api/v1/user/data-exports/{exportId}`

Returns the current state of the authenticated user's previously requested data export identified by `exportId`.

- `DELETE /api/v1/user`

Submits the authenticated user's account deletion action after explicit confirmation and any recent-authentication step required by the backend.
