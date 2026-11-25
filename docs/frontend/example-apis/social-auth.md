## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/example-apis/login.md
- docs/frontend/example-apis/register.md

# Social Auth Example API

## Google Example Handoff

One click on the existing Google button emits `socialLogin({ provider: 'google' })`. The page calls `GoogleAuthServiceDebug`, which simulates the provider callback locally and returns the fixed example token `debug-google-example-token` without an HTTP request. The service never contacts Google or the Vite server. This string is a test fixture, not a Google ID token, OAuth code, proof of identity, or application credential.

The Login page then makes the only HTTP request in this debug flow:

```http
POST /api/auth/google
Content-Type: application/json

{"provider":"google","token":"debug-google-example-token"}
```

The loopback-only Vite mock checks that `provider` is `google` and `token` exactly matches the documented fixture, then returns HTTP `200` with `success: true` and the same safe example account response shape as [Login](login.md#example-response). This check only selects a deterministic example response; it does not verify a Google identity or create an application session. A missing or different token returns a safe HTTP `401`; malformed JSON or an unsupported provider returns HTTP `400`. A documented `exampleScenario: "unavailable"` on this request returns HTTP `503` for failure testing without account data. Do not send a password, reCAPTCHA token, client secret, or the fixture list in this flow. Do not store or log the example token in the browser, URL, or persistent storage. Do not return a refresh cookie or application access token.

Do not create `/api/debug/google/start`, `/api/debug/google/complete`, or `/api/debug/auth/google` in a clean rebuild. The path `/api/auth/google` is an HTTP-shaped local example implemented by Vite, not a claim that this production endpoint exists. Production retains the backend-owned OAuth start/callback contract linked above; this fixture token must never be accepted by a production backend.

Facebook and Apple remain visual entry points without local example endpoints in this document. Production uses the unchanged OAuth contract, not these debug routes.

## Google Registration Example Handoff

On Register Page, the same visible Google action has registration intent. Accepted Terms of Service are required before RegisterForm emits:

```js
socialRegister({
  provider: 'google',
  legalConsent: {
    termsOfService: true,
    privacyPolicy: false,
  },
})
```

The debug page calls `GoogleAuthServiceDebug` and receives the same fixed `debug-google-example-token` fixture. It then makes one local request:

```http
POST /api/auth/google
Content-Type: application/json

{
  "provider": "google",
  "token": "debug-google-example-token",
  "intent": "register",
  "legalConsent": {
    "termsOfService": true,
    "privacyPolicy": false
  }
}
```

The loopback-only mock requires the exact fixture token, `intent: "register"`, and accepted Terms of Service. It returns the fictional confirmed user-data projection from the [Register Example API](register.md#registration-confirmation-fixture), without creating a challenge because the simulated provider identity represents an already provider-verified email. Register Page may hold that result in debug-only memory and navigate to `/history` to exercise the existing page. Missing Terms acceptance returns HTTP `400`; a missing or different fixture token returns HTTP `401`; the unavailable scenario returns HTTP `503` without account data.

This debug branch must not submit RegisterForm password fields, `recaptchaToken`, email, provider subject, or profile claims. The fixed token selects an example only; it is not decoded or persisted. Production registration continues to use `POST /api/v1/auth/oauth/{provider}/start` with `intent: "register"`, followed by the backend callback, verified provider claims, account creation or safe linking, and the normal application session.

Facebook and Apple remain visual registration entries without local example endpoints. Their production registration behavior uses the same backend-owned OAuth start/callback contract with their selected provider value.
