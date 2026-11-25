## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/example-apis/login.md

# Register Example API

## Example Request

`POST /api/register` accepts JSON. The form displays first name, surname, email, optional phone, password, and confirm password. It also displays the documented Terms of Service control; there is no separate Privacy Policy checkbox. The optional `legalConsent.privacyPolicy` value is `false`. `confirmPassword` is checked in the form but never sent. An empty phone is omitted, not sent as an empty string.

```json
{
  "firstName": "Alex",
  "lastName": "Morgan",
  "email": "new.player@example.test",
  "password": "<entered local test password>",
  "legalConsent": { "termsOfService": true, "privacyPolicy": false },
  "recaptchaToken": "<provider token or omitted in debug>"
}
```

The local example route may omit or ignore `recaptchaToken` only inside the debug server. Production verifies a provider-issued token. Never log, retain, echo, or persist the submitted password or token.

## Example Response

For a valid new fictional email, return HTTP `201`:

```json
{
  "success": true,
  "status": "verification_required",
  "user": {
    "id": "debug_registration_preview",
    "firstName": "Alex",
    "lastName": "Morgan",
    "email": "new.player@example.test",
    "phone": null
  },
  "verification": {
    "type": "email",
    "required": true,
    "challengeId": "<opaque in-memory registration challenge id>",
    "methods": ["email"],
    "destinationHint": "n***@example.test",
    "expiresIn": 300
  }
}
```

This result is a preview of the email-verification state, not a stored account or session. The Vite server stores the challenge only in memory, binds it to this registration preview, limits attempts, expires it after five minutes, and makes it single-use. When a valid phone was supplied, return that normalized phone in `user.phone`; otherwise return `null`. Do not return password, hashes, reCAPTCHA token, legal-consent details, the expected code, or a session credential.

## Registration Confirmation Fixture

For manual testing, the isolated preview uses the fixed local registration code `135790`. This is a tester-only debug fixture, not a code delivered by email and not a production secret. The browser page must never receive it except when the tester enters it in ConfirmLoginForm.

The page sends the code to `POST /api/auth/registration-challenges/{challengeId}/verify`:

```json
{
  "method": "email",
  "code": "135790"
}
```

The method must be offered by the registration response. Missing or malformed input returns HTTP `400`; a wrong code returns HTTP `401` without exposing the expected code; an expired, exhausted, or already-used challenge returns HTTP `410`.

Successful local confirmation returns HTTP `200` with a fictional projection matching the production `GET /api/v1/user/data` sections required by the existing History page:

```json
{
  "success": true,
  "account": {
    "id": "debug_registration_preview",
    "mfaEnabled": false,
    "passwordChangedAt": null
  },
  "personalInformation": {
    "firstName": "Alex",
    "lastName": "Morgan",
    "username": "alexmorgan",
    "displayName": "Alex",
    "email": "new.player@example.test",
    "emailVerified": true,
    "phoneCountryCode": null,
    "phone": null,
    "phoneVerified": false,
    "dateOfBirth": null,
    "country": null,
    "city": null,
    "bio": null
  },
  "subscription": {
    "status": "none",
    "planId": null,
    "currentPeriodEndsAt": null,
    "paymentMethodDisplay": null,
    "billingManagementAvailable": false
  },
  "dashboard": {
    "statistics": {
      "sessionsCountThisMonth": 0,
      "practiceTime": 0,
      "lastSession": null
    }
  },
  "sessionHistory": { "items": [] },
  "settings": {
    "notifications": {
      "trainingReminders": false,
      "sessionSummaries": true,
      "productUpdates": false,
      "notificationChannel": "email",
      "reminderTime": null
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

The page may hold this response only in debug in-memory state and navigate to `/history` to exercise the existing empty-history presentation. The response creates no production session, refresh cookie, persistent account, or authorization grant. The accepted challenge is immediately invalidated.

## Deterministic Example Outcomes

- `new.player@example.test` with valid fields and accepted Terms: HTTP `201`, the response above. Each accepted request creates one new in-memory, short-lived challenge; the example creates no account.
- Any email already listed among the fictional users in [Login Example API](login.md#example-user-fixtures), including `maria.ivanova@example.test`: HTTP `409`, `EMAIL_ALREADY_REGISTERED`.
- `unavailable@example.test` with otherwise valid fields: HTTP `503`, `TEMPORARILY_UNAVAILABLE`.
- Missing or malformed first name, surname, email, or password; password shorter than 12 characters; invalid nonempty phone; absent or false Terms acceptance; malformed JSON: HTTP `400`, `INVALID_REQUEST`. The response must not echo submitted secrets.
- Unsupported method: HTTP `405`, `METHOD_NOT_ALLOWED`.

Example error envelope:

```json
{
  "success": false,
  "error": { "code": "EMAIL_ALREADY_REGISTERED", "message": "Registration could not be completed with these details." }
}
```

Do not disclose whether an account exists in a credential-check response; registration conflict is a documented, separate example outcome. Keep all examples local and never connect this route to production authentication or persistence.

## Vite Example Behavior

Read these request, response, and outcome definitions before implementing the local mock routes. Register Page sends one registration request when RegisterForm emits a validated submit and one verification request when ConfirmLoginForm emits a locally valid code. The page owns pending, conflict, error, challenge, confirmed user-data, and navigation state. Do not add fields or controls not supported by the component specifications and prototypes. The mock server validates request structure and challenge state and returns only the deterministic results above. No generated account id beyond the fixed preview id, password database, refresh cookie, persistent store, or production protected-page access is needed.
