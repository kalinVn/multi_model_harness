## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/feature-components.md
- docs/frontend/integration-contracts.md
- docs/frontend/page_additional-functionality/register-page.md
- docs/frontend/example-apis/social-auth.md

# RegisterForm

## Additional Description and Functionality

### Registration Submission

Keep the existing password-registration fields, validation, reCAPTCHA presentation, legal-consent control, and visual structure. After local validation, emit `submit` with the supported registration values. Do not include `confirmPassword`, a user id, provider subject, provider token, or server-owned legal metadata.

RegisterForm does not call registration, verification, user-data, or navigation endpoints. Register Page owns those operations and supplies the form's pending and safe form-level result state.

### Social Registration Entry

Keep the existing Google, Facebook, and Apple actions in `SocialAuthButtons`; do not add a second provider-button group or reuse the Login form. All three buttons are registration entries on this form even when their visible label is the neutral `Continue with …`.

Require accepted Terms of Service before emitting a provider action. When a provider is selected, emit:

```js
socialRegister({
  provider,
  legalConsent: {
    termsOfService: true,
    privacyPolicy: false,
  },
})
```

The provider must be `google`, `facebook`, or `apple`. Do not include password fields, `recaptchaToken`, provider credentials, provider subject, email, or profile claims. Register Page uses this event to call the backend-owned OAuth start endpoint with `intent: 'register'`.

### Google Registration Entry

The Google action follows the same component boundary as the other social-registration buttons:

- it is rendered by `SocialAuthButtons` inside RegisterForm;
- it remains disabled while another registration workflow is pending;
- it reports missing Terms acceptance through the existing form-level feedback;
- it emits `socialRegister({ provider: 'google', legalConsent })` exactly once for one user action;
- it does not initialize a provider SDK, decode or retain a Google credential, call an OAuth callback, establish a session, load user data, or navigate.

Production provider authorization, verified identity claims, account creation or safe linking, and session establishment remain backend-owned. The Login and Register forms may share provider-button presentation, but their emitted intent and page-owned workflows must remain distinct.

## References

- `docs/frontend/feature-components.md#registerform`
- `docs/frontend/integration-contracts.md#authentication-and-application-session`
- `docs/frontend/page_additional-functionality/register-page.md`
- `docs/frontend/example-apis/social-auth.md#google-registration-example-handoff`
- `prototypes/design/pages/register.html`
- `prototypes/components/forms/RegisterForm.vue`
