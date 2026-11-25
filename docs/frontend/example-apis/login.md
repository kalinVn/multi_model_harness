# Login Example API

## Example Request

The loopback-only Vite example server exposes `POST /api/login`. This is an actual HTTP route in the local preview, not the production login route. The Login payload contains email and password, never a `name` field:

```json
{
  "email": "maria.ivanova@example.test",
  "password": "<entered local test password>",
  "recaptchaToken": "<provider token or omitted in debug>"
}
```

Only this debug endpoint may omit or ignore `recaptchaToken`. The production endpoint requires a provider-issued token verified by the backend; a debug checkbox is not verification. Never log the submitted password.

## MFA Challenge Response

For the primary Maria fixture, matching email and password return HTTP `202` with a short-lived email challenge instead of user data:

```json
{
  "success": true,
  "status": "challenge_required",
  "challengeId": "<opaque in-memory debug challenge id>",
  "methods": ["email"],
  "destinationHint": "m***@example.test",
  "expiresIn": 300
}
```

The challenge grants no session and exposes no user data. The Vite server stores it only in memory, binds it to the matched fixture, limits attempts, expires it after five minutes, and makes it single-use.

For manual testing, the isolated preview uses the fixed local confirmation code `246810`. This is a debug fixture, not an OTP delivered by email and not a production secret. The browser page must never receive it except when the tester enters it in `ConfirmLoginForm`.

## Confirm Login Request

The page sends the code to `POST /api/auth/challenges/{challengeId}/verify`:

```json
{
  "method": "email",
  "code": "246810"
}
```

The method must be one of those offered by Login. A missing or malformed payload returns HTTP `400`; a wrong code returns HTTP `401` without exposing the expected code; and an expired, exhausted, or already-used challenge returns HTTP `410`.

## Confirm Login Success Response

Successful verification returns HTTP `200` with `success: true` and data for **only the matched user**. The top-level sections mirror the documented user-data response (`docs/frontend/integration-contracts.md#get-user-data`); there is no redundant outer `user` object. `bio` is the Profile page's “About me” field. `dashboard.statistics` supplies performance figures, and `sessionHistory.items` supplies dated history without duplicating it in `dashboard`. The response creates no production session or authorization. The example below corresponds to the first fixture:

```json
{
  "success": true,
  "account": { "id": "debug_user_1", "mfaEnabled": true, "passwordChangedAt": null },
  "personalInformation": {
    "firstName": "Maria", "lastName": "Ivanova", "username": "mariaivanova", "displayName": "Maria",
    "email": "maria.ivanova@example.test", "emailVerified": true,
    "phoneCountryCode": "+359", "phone": "000000001", "phoneVerified": false,
    "dateOfBirth": "1994-05-14", "country": "Bulgaria", "city": "Sofia",
    "bio": "Practices twice a week."
  },
  "subscription": {
    "status": "active", "planId": "performance", "currentPeriodEndsAt": "2026-11-29T00:00:00Z",
    "paymentMethodDisplay": "Debug only", "billingManagementAvailable": false
  },
  "dashboard": { "statistics": { "sessionsCountThisMonth": 2, "practiceTime": 4860, "lastSession": "2026-10-12T08:30:00Z" } },
  "sessionHistory": { "items": [
    { "id": "debug_session_1", "startedAt": "2026-10-12T08:30:00Z", "durationSeconds": 2520, "status": "complete", "historyStatus": "reviewed", "summary": "Serve practice reviewed on 2026-10-12." }
  ] },
  "settings": {
    "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "18:00" },
    "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false }
  }
}
```

`practiceTime` is measured in seconds, as in the production user-data contract. `planId` uses `starter`, `performance`, or `pro`; “Most popular” is the visual label for Performance, not a fourth plan. This example omits a real access token and refresh cookie. The accepted challenge is immediately invalidated and cannot be reused.

For an unknown email or incorrect password, return the same HTTP `401` response without revealing which field failed:

```json
{
  "success": false,
  "error": { "code": "INVALID_CREDENTIALS", "message": "Invalid email or password." }
}
```

Malformed JSON or missing email/password returns HTTP `400` with `success: false` and a safe validation error. Never return passwords or password hashes.

### Deterministic example outcomes

First validate the supplied email and password against the server-only local fixture. Unknown email or wrong password always returns the same `401` error above. After a valid match, use these examples to exercise different page states:

- Maria (first fixture): HTTP `202` with the email challenge above; successful confirmation then returns HTTP `200` with Maria's user data.
- Ivan (second fixture): HTTP `503`, a temporary service-error example, without returning user data.
- Elena (third fixture): HTTP `200`, with Elena's own data, including a missing subscription plan and an incomplete session.
- Nikolay (fourth fixture): HTTP `403`, an email-verification-required example, without returning user data.
- Petya (fifth fixture): HTTP `200`, with Petya's own data.

The failure outcomes are local preview scenarios, not claims about real accounts or backend policy. The second fixture's response is:

```json
{
  "success": false,
  "error": { "code": "TEMPORARILY_UNAVAILABLE", "message": "Login is temporarily unavailable. Please try again." }
}
```

The fourth fixture uses the same envelope with code `EMAIL_VERIFICATION_REQUIRED` and a generic verification message. Never return profile, subscription, history, or settings data in an error response.

## Example user fixtures

These five identities and Bulgarian-format phone placeholders are fictional. `passwordHash` values below are **not usable hashes**. At implementation time, generate server-only salted hashes from a local test password outside source control. Do not put plaintext passwords in fixtures, logs, browser storage, or client bundles. The Vite server should read a server-only fixture file derived from these examples; it must never expose the whole user list to the browser. Each successful response projects one matched fixture into the Example Response shape and excludes `passwordHash`.

The isolated Vite preview currently uses one local, ignored salted hash for all five fictional accounts; the placeholder `passwordHash` fields are documentation only and are not read as credentials. Set a different local test password and hash before sharing the preview with anyone else.

Every fixture includes the Profile fields, all three enabled notification toggles, a preferred notification channel and reminder time, a distinct subscription state, dated history, and dashboard performance data. A `null` or empty value is intentional data, not a missing field.

```json
[
  {
    "passwordHash": "<server-only salted hash 1>",
    "account": { "id": "debug_user_1", "mfaEnabled": true, "passwordChangedAt": null },
    "personalInformation": { "firstName": "Maria", "lastName": "Ivanova", "username": "mariaivanova", "displayName": "Maria", "email": "maria.ivanova@example.test", "emailVerified": true, "phoneCountryCode": "+359", "phone": "000000001", "phoneVerified": false, "dateOfBirth": "1994-05-14", "country": "Bulgaria", "city": "Sofia", "bio": "Practices twice a week." },
    "subscription": { "status": "active", "planId": "performance", "currentPeriodEndsAt": "2026-11-29T00:00:00Z", "paymentMethodDisplay": "Debug only", "billingManagementAvailable": false },
    "dashboard": { "statistics": { "sessionsCountThisMonth": 2, "practiceTime": 4860, "lastSession": "2026-10-12T08:30:00Z" } },
    "sessionHistory": { "items": [{ "id": "debug_session_1", "startedAt": "2026-10-12T08:30:00Z", "durationSeconds": 2520, "status": "complete", "historyStatus": "reviewed", "summary": "Serve practice reviewed on 2026-10-12." }] },
    "settings": { "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "18:00" }, "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false } }
  },
  {
    "passwordHash": "<server-only salted hash 2>",
    "account": { "id": "debug_user_2", "mfaEnabled": false, "passwordChangedAt": null },
    "personalInformation": { "firstName": "Ivan", "lastName": "Petrov", "username": "ivanpetrov", "displayName": "Ivan", "email": "ivan.petrov@example.test", "emailVerified": true, "phoneCountryCode": "+359", "phone": "000000002", "phoneVerified": false, "dateOfBirth": "1988-11-03", "country": "Bulgaria", "city": "Plovdiv", "bio": "Working on serve consistency." },
    "subscription": { "status": "active", "planId": "starter", "currentPeriodEndsAt": "2026-11-01T00:00:00Z", "paymentMethodDisplay": "Debug only", "billingManagementAvailable": false },
    "dashboard": { "statistics": { "sessionsCountThisMonth": 1, "practiceTime": 2100, "lastSession": "2026-10-09T17:00:00Z" } },
    "sessionHistory": { "items": [{ "id": "debug_session_2", "startedAt": "2026-10-09T17:00:00Z", "durationSeconds": 2100, "status": "complete", "historyStatus": "reviewed", "summary": null }] },
    "settings": { "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "17:30" }, "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false } }
  },
  {
    "passwordHash": "<server-only salted hash 3>",
    "account": { "id": "debug_user_3", "mfaEnabled": false, "passwordChangedAt": null },
    "personalInformation": { "firstName": "Elena", "lastName": "Georgieva", "username": "elenageorgieva", "displayName": "Elena", "email": "elena.georgieva@example.test", "emailVerified": true, "phoneCountryCode": "+359", "phone": "000000003", "phoneVerified": false, "dateOfBirth": "1999-02-21", "country": "Bulgaria", "city": "Varna", "bio": "New to tennis training." },
    "subscription": { "status": null, "planId": null, "currentPeriodEndsAt": null, "paymentMethodDisplay": "Not connected", "billingManagementAvailable": false },
    "dashboard": { "statistics": { "sessionsCountThisMonth": 0, "practiceTime": 0, "lastSession": "2026-10-25T09:00:00Z" } },
    "sessionHistory": { "items": [{ "id": "debug_session_3", "startedAt": "2026-10-25T09:00:00Z", "durationSeconds": 0, "status": "incomplete", "historyStatus": "incomplete", "summary": null }] },
    "settings": { "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "19:00" }, "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false } }
  },
  {
    "passwordHash": "<server-only salted hash 4>",
    "account": { "id": "debug_user_4", "mfaEnabled": false, "passwordChangedAt": null },
    "personalInformation": { "firstName": "Nikolay", "lastName": "Dimitrov", "username": "nikolaydimitrov", "displayName": "Nikolay", "email": "nikolay.dimitrov@example.test", "emailVerified": false, "phoneCountryCode": "+359", "phone": "000000004", "phoneVerified": false, "dateOfBirth": "1991-07-30", "country": "Bulgaria", "city": "Burgas", "bio": "Returning after a break." },
    "subscription": { "status": "active", "planId": "pro", "currentPeriodEndsAt": "2026-11-15T00:00:00Z", "paymentMethodDisplay": "Debug only", "billingManagementAvailable": false },
    "dashboard": { "statistics": { "sessionsCountThisMonth": 0, "practiceTime": 1080, "lastSession": "2026-10-19T09:15:00Z" } },
    "sessionHistory": { "items": [{ "id": "debug_session_4", "startedAt": "2026-10-19T09:15:00Z", "durationSeconds": 1080, "status": "incomplete", "historyStatus": "incomplete", "summary": null }] },
    "settings": { "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "08:30" }, "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false } }
  },
  {
    "passwordHash": "<server-only salted hash 5>",
    "account": { "id": "debug_user_5", "mfaEnabled": false, "passwordChangedAt": null },
    "personalInformation": { "firstName": "Petya", "lastName": "Stoyanova", "username": "petyastoyanova", "displayName": "Petya", "email": "petya.stoyanova@example.test", "emailVerified": true, "phoneCountryCode": "+359", "phone": "000000005", "phoneVerified": false, "dateOfBirth": "1996-12-08", "country": "Bulgaria", "city": "Ruse", "bio": "Focused on movement and footwork." },
    "subscription": { "status": "active", "planId": "performance", "currentPeriodEndsAt": "2026-11-01T00:00:00Z", "paymentMethodDisplay": "Debug only", "billingManagementAvailable": false },
    "dashboard": { "statistics": { "sessionsCountThisMonth": 1, "practiceTime": 3060, "lastSession": "2026-10-22T15:20:00Z" } },
    "sessionHistory": { "items": [{ "id": "debug_session_5", "startedAt": "2026-10-22T15:20:00Z", "durationSeconds": 3060, "status": "complete", "historyStatus": "reviewed", "summary": "Footwork review completed on 2026-10-23." }] },
    "settings": { "notifications": { "trainingReminders": true, "sessionSummaries": true, "productUpdates": true, "notificationChannel": "email", "reminderTime": "15:00" }, "privacy": { "saveVideos": false, "videoRetention": "30", "historyVisibility": "private", "performanceAnalytics": true, "optionalTelemetry": false } }
  }
]
```

## Vite Example Behavior

1. Keep the endpoint inside the loopback-only debug Vite server, not the production backend.
2. Validate JSON shape and normalize email before lookup; compare the submitted password against a server-only salted hash. Ignore reCAPTCHA verification only for this debug endpoint.
3. For the primary fixture, return only a short-lived in-memory challenge after credentials match. Do not return user data before verification.
4. Verify the offered method and submitted code against that active challenge, enforce expiry, attempt limits, and single use, and return only the matched fixture's projected data after success.
5. Let Login Page own credential, challenge, pending, error, and success UI states. `LoginForm` and `ConfirmLoginForm` must not fetch endpoints or store credentials.
6. Do not claim that a successful debug response grants authorization, creates a real session, sends a real email, or replaces the production Login, MFA, and `GET /api/v1/user/data` sequence.
