## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/pages-and-routes.md

CSS in the prototype Vue components is for visual reference only; production styles may live outside components and use shared design tokens.

# Feature Components

## BaseModal

Name: BaseModal

Description: BaseModal is the reusable generic modal shell. It renders a native modal dialog, backdrop, viewport-safe panel, header, top-right close button, and internally scrollable content area. It contains no cookie, privacy, camera, saving, acceptance, routing, API, or other feature logic. The existing full-screen camera modal remains specialized because its media lifecycle and full-viewport layout are materially different.

### Component Functionality

The standard close button appears at the top right. Escape and a direct backdrop click use the same close path. Closing the shell only dismisses it: it never implies save, accept, reject, submit, or navigation behavior.

The parent may pass ordinary slot content or render its selected Vue component in the default slot. Dynamic selection follows normal Vue composition, conceptually `BaseModal → active content component`; `BaseModal` neither imports nor enumerates its consumers. Cookie policy, privacy policy, and preferences content are consumers of this contract, not part of it.

When opened, the native `dialog.showModal()` behavior provides modal focus containment. The close control receives initial focus, has an accessible name, and remains keyboard visible. The component stores the previously focused element, locks document scrolling while open, and restores both scrolling and focus on close or cleanup. The title is connected through `aria-labelledby`. Tall content scrolls inside the body while the header and close control remain visible; horizontal overflow is contained. Width, maximum height, and mobile spacing remain bounded by the viewport.

### Component Properties and Data Flow

| Prop | Type | Default / requirement |
| --- | --- | --- |
| `open` | Boolean | `false` |
| `title` | String | Required; labels the dialog heading |

Supported states are closed, open, content-overflow/scrolling, and responsive desktop/mobile sizing. The component does not maintain a feature-specific state machine. The parent owns the `open` value and active content selection.

Emits:

- `close` — requests that the parent close the modal. The owning parent responds by updating its `open` state.

Slots:

| Slot | Purpose |
| --- | --- |
| default | Arbitrary modal body content supplied by the parent |
| `eyebrow` | Optional short context label above the title |

```vue
<BaseModal :open="isOpen" :title="activeTitle" @close="isOpen = false">
  <component :is="activeContentComponent" />
</BaseModal>
```

### Prototype References

#### Design Prototypes

- [modals.html](../../prototypes/design/components/modals.html)

#### Vue Components

- [BaseModal.vue](../../prototypes/components/modal/BaseModal.vue)

---


## PrivacyChoicesBanner

Name: PrivacyChoicesBanner

Description: PrivacyChoicesBanner is the visible fixed bottom banner for cookie and privacy choices.

### Component Functionality

The component renders the bottom privacy choices banner with actions for Accept All, Reject All, Manage Preferences, Cookie Policy and Privacy Policy. It directly uses the shared `useCookieConsent` composable: Accept All and Reject All call its persistence actions, while the other actions update its shared active modal flow.

- `Accept All`, `Reject All`, and `Manage Preferences` use the shared `Button` component.
- `Cookie Policy` and `Privacy Policy` use the shared `TextButton` component.

The component does not own persistence, consent state, modal state, preference-category controls, or policy content. It does not delegate these actions to a parent component.

### Component Properties and Data Flow

The component has no props, local state, or emitted consent/modal events. It reads `isBannerVisible` and directly calls `acceptAll`, `rejectAll`, `openPreferences`, `openCookiePolicy`, and `openPrivacyPolicy` from the shared `useCookieConsent` instance.

### Prototype References

#### Design Prototypes

- [cookie-privacy-and-policy-banner.html](../../prototypes/design/components/feature-components/cookie-privacy-and-policy-banner.html)

#### Vue Components

- [PrivacyChoicesBanner.vue](../../prototypes/components/features/CookiePrivacyPolicy/PrivacyChoicesBanner.vue)

---
## CookiePrivacyPolicy

Name: CookiePrivacyPolicy

Description: CookiePrivacyPolicy is the Vue feature component responsible for rendering the modal-based cookie-preference and policy flows. It is not the owner or coordinator of the complete cookie-consent flow and does not compose `PrivacyChoicesBanner`.

### Component Functionality

The shared application shell mounts it independently from authentication state across public and authenticated pages.

`CookiePrivacyPolicy` uses the shared `useCookieConsent` composable and consumes its active modal flow state. Based on that shared state, it renders one `BaseModal` with either `CookiePreferencesContent` or the reusable `PolicyContent` as the active modal body.

The preferences flow renders `CookiePreferencesContent` with the previously saved optional-category values supplied by `useCookieConsent`.

When the user saves the preferences, `CookiePrivacyPolicy` handles the `save` event from `CookiePreferencesContent` and delegates the updated selection to the appropriate action in `useCookieConsent`.

Closing without saving discards the local draft and leaves the previously saved consent state unchanged.

| Category | Prototype behavior |
| --- | --- |
| Essential Cookies | Always enabled and disabled for editing; covers authentication, session handling, security, and required application state. |
| Analytics Cookies | Optional checkbox for anonymous or aggregated product/traffic analytics. |
| Preference Cookies | Optional checkbox for interface or experience preferences. |
| Marketing Cookies | Optional checkbox for advertising, remarketing, pixels, or other optional tracking. |

The policy flow renders the same reusable `PolicyContent` component for Cookie Policy and Privacy Policy, supplying the appropriate policy-specific title and content or sections.

Policy bodies scroll independently over the current route.

Opening or closing policy content is informational only and must not modify consent state, write persistence, or change banner visibility.

`Privacy Policy`, `Cookie Policy`, and `Cookie Settings` actions in the Footer used by either layout family use the shared `TextButton` component and invoke the shared cookie/privacy flow through `useCookieConsent`.

These actions do not make `CookiePrivacyPolicy` responsible for `PrivacyChoicesBanner` or for the banner's `Accept All` and `Reject All` actions.

### Component Properties and Data Flow

`CookiePrivacyPolicy` has no props or emitted events.

It owns only the modal presentation layer.

The active modal flow, consent state, consent actions, and persistence are owned by the shared `useCookieConsent` composable.

`CookiePrivacyPolicy` consumes the active modal flow state, saved category values, modal actions, and preference-saving action from `useCookieConsent`.

It does not implement consent persistence itself and does not decide the active flow independently.

The shared `useCookieConsent` composable owns the cookie/privacy feature state and actions, including:

- consent state
- persistence
- active modal flow
- consent actions
- the versioned `tennis-ai-coach.cookie-consent.v1` browser `localStorage` contract
- compatibility with already-saved records

### Prototype References

#### Design Prototypes

- [cookie-privacy-and-policy-modal.html](../../prototypes/design/components/feature-components/cookie-privacy-and-policy-modal.html)

#### Vue Components

- [CookiePrivacyPolicy.vue](../../prototypes/components/features/CookiePrivacyPolicy/CookiePrivacyPolicy.vue)

---

## CookiePreferencesContent

Name: CookiePreferencesContent

Description: CookiePreferencesContent is the dedicated preference editor rendered inside `BaseModal`.

### Component Functionality

The component initializes an editable local draft from its props. Essential remains checked and disabled. Submitting requests that the parent save the current optional-category selection through `useCookieConsent`. Closing the modal without submitting discards the draft and leaves the previously saved consent state unchanged.

### Component Properties and Data Flow

| Prop | Type | Default |
| --- | --- | --- |
| `analytics` | Boolean | `false` |
| `preferences` | Boolean | `false` |
| `marketing` | Boolean | `false` |

Submitting emits `save` with `{ analytics, preferences, marketing }`. The parent delegates persistence to `useCookieConsent` and decides whether to close the modal. The component does not persist values or mutate the saved consent state directly.

### Prototype References

#### Design Prototypes

- [manage-coockie-references-modal.html](../../prototypes/design/components/feature-components/manage-coockie-references-modal.html)

#### Vue Components

- [CookiePreferencesContent.vue](../../prototypes/components/features/CookiePrivacyPolicy/CookiePreferencesContent.vue)



## RecaptchaField

Name: RecaptchaField

Description: RecaptchaField is the authentication verification-field presentation used by LoginForm and RegisterForm.

### Component Functionality

RecaptchaField renders the reCAPTCHA verification widget. After successful verification, the provider returns a short-lived token which the component exposes to the parent form.

The parent form sends the token with the authentication request, while the backend performs the final verification.

Expired, reset, or invalid verification clears the current token.

### Component Properties and Data Flow

- Props:

- modelValue: String | null — current verification token.

- disabled: Boolean — disables interaction when required.

- siteKey: String — optional provider site key.

Emits:

- update:modelValue(token) on successful verification.

- update:modelValue(null) on expiry or reset.

- error(error) on verification errors.

The component does not expose generic getValue() or setValue() methods and does not own authentication business logic.

### Prototype References

#### Design Prototypes

- [recaptcha-field.html](../../prototypes/design/components/fields/recaptcha-field.html)

#### Vue Components

- [RecaptchaField.vue](../../prototypes/components/fields/RecaptchaField.vue)

---

## SocialAuthButton

Name: SocialAuthButton

Description: SocialAuthButton is a single provider authentication action with a provider icon.

### Component Functionality

The selected provider determines the label and icon. Disabled state prevents the individual action; loading state disables it, exposes its busy state, and changes the label to the provider connection state. OAuth behavior remains parent-owned.

For each provider and state, reproduce the corresponding component-only design prototype exactly: use its SVG icon paths, icon size, button shape, spacing, colors, and visible state styling. Do not replace provider icons with letters, emoji, generic shapes, or other placeholders; do not invent colors or button variants. The component plan and implementation must retain these design references, and the rendered button must be checked against them.

### Component Properties and Data Flow

`SocialAuthButton` props:

- `provider` (required): `google`, `facebook`, or `apple`; selects the label and provider icon.
- `actionLabel`: leading label such as `Login` or `Continue`; defaults to `Continue`.
- `disabled`: disables the individual action.
- `loading`: disables the button, exposes its busy state, and changes the label to the provider connection state.
- event: `click(provider)`.

### Prototype References

#### Design Prototypes

- [Continue with Google — default](../../prototypes/design/components/buttons/specimens/social-auth-google-default.html)
- [Continue with Google — hover](../../prototypes/design/components/buttons/specimens/social-auth-google-hover.html)
- [Continue with Google — pressed](../../prototypes/design/components/buttons/specimens/social-auth-google-pressed.html)
- [Continue with Google — focus-visible](../../prototypes/design/components/buttons/specimens/social-auth-google-focus-visible.html)
- [Continue with Google — disabled](../../prototypes/design/components/buttons/specimens/social-auth-google-disabled.html)
- [Connecting to Google — loading](../../prototypes/design/components/buttons/specimens/social-auth-google-loading.html)
- [Continue with Facebook — default](../../prototypes/design/components/buttons/specimens/social-auth-facebook-default.html)
- [Continue with Facebook — hover](../../prototypes/design/components/buttons/specimens/social-auth-facebook-hover.html)
- [Continue with Facebook — pressed](../../prototypes/design/components/buttons/specimens/social-auth-facebook-pressed.html)
- [Continue with Facebook — focus-visible](../../prototypes/design/components/buttons/specimens/social-auth-facebook-focus-visible.html)
- [Continue with Facebook — disabled](../../prototypes/design/components/buttons/specimens/social-auth-facebook-disabled.html)
- [Connecting to Facebook — loading](../../prototypes/design/components/buttons/specimens/social-auth-facebook-loading.html)
- [Continue with Apple — default](../../prototypes/design/components/buttons/specimens/social-auth-apple-default.html)
- [Continue with Apple — hover](../../prototypes/design/components/buttons/specimens/social-auth-apple-hover.html)
- [Continue with Apple — pressed](../../prototypes/design/components/buttons/specimens/social-auth-apple-pressed.html)
- [Continue with Apple — focus-visible](../../prototypes/design/components/buttons/specimens/social-auth-apple-focus-visible.html)
- [Continue with Apple — disabled](../../prototypes/design/components/buttons/specimens/social-auth-apple-disabled.html)
- [Connecting to Apple — loading](../../prototypes/design/components/buttons/specimens/social-auth-apple-loading.html)

#### Vue Components

- [SocialAuthButton.vue](../../prototypes/components/forms/SocialAuthButton.vue)

---

## LoginForm

Name: LoginForm

Description: LoginForm is the dedicated login form for existing users.

### Component Functionality

It contains the shared FormStatusMessage, email field, password field, RecaptchaField, primary Login action, and Create Account navigation to the Register page. Do not add a name field to LoginForm. FormStatusMessage is placed inside the form immediately above the first field. It composes SocialAuthButtons for Google, Facebook, and Apple. The prototype reports the selected provider without starting OAuth, authenticating, or retaining credentials.

### Component Properties and Data Flow

LoginForm has no slots. Shared authentication validation helpers support the prototype form validation. Authentication, OAuth, credential handling, and session ownership remain outside the component.

Parent-controlled workflow props are:

- `workflowState`: `idle`, `pending`, `error`, or `success`; defaults to `idle`;
- `workflowMessage`: optional safe user-facing text; defaults to an empty string;
- `pendingProvider`: optional `google`, `facebook`, or `apple`; defaults to `null` and identifies the social action currently pending.

The form owns the local form/UI state:

- email

- password

- recaptchaToken

- validationErrors

Required form fields are email, password, and recaptchaToken. Email must use a valid email format, password is required, and recaptchaToken is required before submission. Request preparation sends only the fields declared by the central Login integration contract.

After successful local validation, LoginForm emits:

- `submit` with `{ email, password, recaptchaToken }`;
- `socialLogin` with `{ provider }`, where `provider` is `google`, `facebook`, or `apple`.

The owning Login Page handles both events. LoginForm does not call an API, read or write a store, navigate, start OAuth, receive provider credentials, or retain application-session state.

LoginForm maps the parent-controlled workflow presentation to FormStatusMessage:

- no active form-level message passes an empty `message` and renders no component output;
- `workflowState: pending` maps to `pending` with `workflowMessage` and disables submission; an active `pendingProvider` also identifies and disables the selected social action;
- `workflowState: error` maps to `error` with `workflowMessage`;
- `workflowState: success` maps to `success` only with a confirmed parent-supplied `workflowMessage`.

The form passes only the resolved `state` and `message` props to FormStatusMessage. FormStatusMessage does not receive credentials, provider tokens, field values, or field-level validation errors. Individual validation errors remain adjacent to their fields.

### Prototype References

#### Vue Components

- [LoginForm.vue](../../prototypes/components/forms/LoginForm.vue)

#### Helpers

- [authValidators.js](../../prototypes/utils/validators/authValidators.js)


---

## ConfirmLoginForm

Name: ConfirmLoginForm

Description: ConfirmLoginForm is the reusable authentication confirmation-code form used for Login MFA through TOTP, email, or SMS and for post-registration verification challenges delivered by email.

### Component Functionality

The component renders only the confirmation form: a short explanation of where the code was sent, one six-digit code field, form-level status feedback, and a purpose-specific submit action. Login uses `Confirm login`; registration uses `Confirm registration`.

The code field uses `inputmode="numeric"`, `autocomplete="one-time-code"`, and a six-character maximum. It accepts digits only and reports a local validation error until exactly six digits are present. The field remains available after an invalid-code response so the user can correct and resubmit it.

ConfirmLoginForm does not request or resend a code, choose a verification method, verify a challenge, create a session, load user data, or navigate. The owning Login Page may show the form for a TOTP, email, or SMS method offered by the backend for its active challenge. Register uses only its backend-offered email verification method. Login MFA and registration verification remain separate backend workflows even though they share this presentation component.

### Component Properties and Data Flow

| Prop | Type / supported values | Requirement |
| --- | --- | --- |
| `purpose` | `login`, `registration` | Required; selects the accessible title, explanatory copy, pending text, and submit label without selecting an endpoint. |
| `method` | `totp`, `email`, `sms` | Required; identifies the backend-offered Login MFA method or the registration email method represented by this form. |
| `destinationHint` | String | Optional masked destination text supplied by the parent for email or SMS; omit it for TOTP and never expose a complete email address or phone number unnecessarily. |
| `pending` | Boolean | Disables the field and shows the Button loading state while verification is in progress. |
| `errorMessage` | String | Optional safe backend or workflow error text. |
| `expired` | Boolean | Marks the challenge as terminal and disables submission. |

Local component state contains only the entered code and its immediate validation error.

Emits:

- `submit` with `{ method, code }` after local validation succeeds.

The owning page retains `challengeId` and selects the endpoint from the workflow context. Login sends `POST /api/v1/auth/challenges/{challengeId}/verify`; Register sends `POST /api/v1/auth/registration-challenges/{challengeId}/verify`. The page distinguishes invalid and expired challenges, stores the returned access token only in memory, loads `GET /api/v1/user/data`, and then performs its documented navigation. The component never receives or derives either endpoint.

### Prototype References

#### Design Prototypes

- [confirm-login-form.html](../../prototypes/design/components/forms/confirm-login-form.html)

#### Vue Components

- [ConfirmLoginForm.vue](../../prototypes/components/forms/ConfirmLoginForm.vue)

---

## RegisterForm

Name: RegisterForm

Description: RegisterForm is the dedicated account-registration form.

### Component Functionality

RegisterForm renders the shared FormStatusMessage immediately above its first field, followed by first name, surname, email, optional phone, password, confirm-password, and required Terms of Service acceptance, RecaptchaField, the primary Register action, Login navigation, and SocialAuthButtons for Google, Facebook, and Apple. There is no separate Privacy Policy checkbox; the optional backend acknowledgment value defaults to false.

Follow the [Register design prototype](../../prototypes/design/pages/register.html) for the form's visual structure: the `Start free` eyebrow, `Create Account` title, `Create your Tennis AI Coach profile.` introduction, a two-column field grid on wider screens that becomes one column on narrow screens, the prototype's field labels and placeholders, the full-width primary action, the social-action divider and buttons, and the `Already have an account? Login` link after the social buttons. Match the prototype's card width, spacing, typography, colors, and control styling. Do not replace this structure with an undifferentiated one-column stack on desktop or move the Login link above the social buttons. The documented Terms of Service requirement remains authoritative.

The form performs client-side validation and delegates registration and social authentication requests to the authentication service according to the central integration contract.

Render only fields, consent controls, actions, and supporting content explicitly required by this component specification and its referenced Register prototype. Do not invent additional UI. Show the documented Terms of Service checkbox, but no second agreement checkbox.



### Component Properties and Data Flow

RegisterForm has no slots. Its parent-controlled workflow props are:

- `workflowState`: `idle`, `pending`, `error`, or `success`; defaults to `idle`;
- `workflowMessage`: optional safe user-facing text; defaults to an empty string;
- `pendingProvider`: optional `google`, `facebook`, or `apple`; defaults to `null` and identifies the social action currently pending.

The form owns only its local UI/form state, including:

- firstName

- lastName

- phone

- email

- password

- recaptchaToken

- confirmPassword

- termsOfServiceAccepted

- validationErrors

Required form fields are firstName, lastName, email, password, confirmPassword, termsOfServiceAccepted, and recaptchaToken. phone is optional. The optional backend `legalConsent.privacyPolicy` value is false when no separate acknowledgment is collected.

Validation Rules

- firstName is required.

- lastName is required.

- email is required and must have a valid email format.

- phone is optional. When provided, validate its format; an empty value must not block submission.

- password is required and must be at least 12 characters long.

- confirmPassword is required and must match password.

- termsOfServiceAccepted is required and must be true before password registration or social registration can begin. It maps to `legalConsent.termsOfService = true`.

- No separate Privacy Policy acceptance is collected by this form. Send `legalConsent.privacyPolicy = false`; this must not block password or social registration.

- recaptchaToken is required before the form can be submitted.


Shared validation helpers may be used for client-side validation.

RegisterForm does not store provider secrets or provider access tokens.

Authentication requests and OAuth-start requests are delegated to the application authentication service/API layer.

RegisterForm emits:

- `submit` with the validated password-registration values, including the current `recaptchaToken` and legal-consent values but excluding `confirmPassword`;
- `socialRegister` with `{ provider, legalConsent }`, where `provider` is `google`, `facebook`, or `apple`, Terms of Service acceptance is `true`, and the optional Privacy Policy acknowledgment is `false`.

The social-registration action does not include a password, reCAPTCHA token, provider token, provider subject, email, or profile data. Register Page uses the selected provider only to start the backend-owned OAuth registration flow.

RegisterForm maps the parent-controlled workflow presentation to FormStatusMessage:

- no active form-level message passes an empty `message` and renders no component output;
- `workflowState: pending` maps to `pending` with `workflowMessage` and disables submission; an active `pendingProvider` also identifies and disables the selected social action;
- `workflowState: error` maps to `error` with `workflowMessage`;
- `workflowState: success` maps to `success` only with a confirmed parent-supplied `workflowMessage`.

The form passes only the resolved `state` and `message` props to FormStatusMessage. FormStatusMessage does not receive registration fields, passwords, provider tokens, legal-consent values, or field-level validation errors. Individual validation errors remain adjacent to their fields.

### Prototype References

#### Design Prototypes

- [register.html](../../prototypes/design/pages/register.html)

#### Vue Components

- [RegisterForm.vue](../../prototypes/components/forms/RegisterForm.vue)

#### Helpers

- [authValidators.js](../../prototypes/utils/validators/authValidators.js)

---

## PaymentStatusCard

Name: PaymentStatusCard

Description: PaymentStatusCard is the single presentational component for Checkout payment-return states.

### Component Functionality

It reuses the existing panel, typography, Button, spacing, radius, width, and responsive behavior rather than defining separate pending, success, failed, cancelled, and expired card structures. It renders, in order, the shared `StateLabel`, the selected payment plan title and description, the payment-state explanatory content and optional note, and the shared action `Button`.

`currentState` is passed directly to `StateLabel.state`. StateLabel owns only the semantic label appearance; PaymentStatusCard retains the payment-specific label text and existing payment-state copy.

The visual `success` state represents an already backend-verified successful outcome; it must never be inferred from a browser redirect or query parameter in production. The prototype query parameter selects only which visual design to preview.

### Component Properties and Data Flow

| Prop | Type / requirement | Display responsibility |
| --- | --- | --- |
| `currentState` | Required string: `pending`, `success`, `failed`, `cancelled`, or `expired` | Selects the payment-state content and is passed to `StateLabel.state`. |
| `paymentPlanTitle` | Required string | Displays the name of the currently selected payment or subscription plan. |
| `paymentPlanDescription` | Required string | Displays the description of the currently selected payment or subscription plan. |

The prototype data source is the Pinia `CheckoutStore`, implemented by `useCheckoutStore`. `currentState` originates from `CheckoutStore.status`; `useCheckout` normalizes the store's backend-shaped `succeeded` value to the component's `success` state. `paymentPlanTitle` and `paymentPlanDescription` are resolved by `useCheckout` from the feature-local plan catalog using `CheckoutStore.planId`. `Checkout.vue` passes all three values as props. The data flow is:

`CheckoutStore` → `useCheckout` → `Checkout.vue` → `PaymentStatusCard` props

PaymentStatusCard does not access or mutate CheckoutStore. It passes `currentState` to the presentational `StateLabel`; the shared `Button` receives no application state.

The main Button click causes PaymentStatusCard to emit `action` without a payload:

`Button click` → `PaymentStatusCard` emits `action` → `Checkout.vue` / parent handles behavior

The optional `secondary-action` slot may be used for parent-owned secondary navigation such as Back to Subscription.

The parent owns retry, payment-status refresh, navigation, backend interaction, payment verification, subscription mutation, and any resulting store updates. PaymentStatusCard, StateLabel, and Button perform no API requests, redirects, payment verification, subscription mutation, store mutation, or persistence.

### Prototype References

#### Design Prototypes

- [payment-status-card-states.html](../../prototypes/design/components/cards/payment-status-card-states.html)

#### Vue Components

- [PaymentStatusCard.vue](../../prototypes/components/features/checkout/PaymentStatusCard.vue)
- [StateLabel.vue](../../prototypes/components/labels/StateLabel.vue)

---

## CameraPreviewModal

Name: CameraPreviewModal

Description: CameraPreviewModal is the single Training camera feature component.

The [Training page requirements](pages-and-routes.md#training) own session creation, reconnection, frame-preparation policy, feedback/audio sequencing, and completion or abandonment. This section describes only the component's UI, inputs and outputs, and resource ownership.

### Component Functionality
CameraPreviewModal displays the Training camera experience as a viewport-sized modal without replacing or navigating away from the Training page.

The component provides the camera preview, StateLabel, feedback/analysis presentation, microphone mute control, and the three user action buttons defined by the camera design.

It manages the camera-related UI lifecycle, including camera requesting/loading, permission errors, microphone mute state, analysis start/stop state, and modal closure.

When video analysis is active, camera frames are passed through the video-analysis flow to the backend analysis layer. Analysis results received through that flow are presented inside the modal as feedback to the user.

Stop Video Analysis stops the active analysis while keeping the camera preview available. Closing the modal through Return to Training, Escape, device loss, or component unmount ends the camera session and releases the owned camera and microphone resources.

The component does not perform browser-side coaching inference or generate fabricated coaching feedback. It only presents analysis/feedback received through the defined analysis flow.


### Component Properties and Data Flow

CameraPreviewModal contains the main camera experience used during Training.

The component UI contains:

a StateLabel displayed in the upper area of the modal

the main camera preview container positioned in the center of the modal, where the active camera stream is displayed

camera and microphone controls

three shared Button components for the actions defined by the camera design

the feedback/analysis area used to display received analysis results

The modal accepts an optional externally owned stream. If no stream is supplied, useCameraSession is responsible for requesting and owning the camera and microphone stream.

An optional analysisFps property may be provided when the analysis capture rate needs to be configured externally; otherwise the analysis layer uses its default configuration.

The component emits:

analysis-result when a new analysis result is received and needs to be forwarded to the parent/session layer

close when the camera modal is closed

The optional overlay slot receives the latest analysis result and can be used to display analysis or feedback information over the camera preview.

The high-level data flow is:

CameraPreviewModal → useVideoAnalysis → trainingTransport → Backend

Analysis results flow back through the same frontend layers:

Backend → trainingTransport → useVideoAnalysis → CameraPreviewModal

CameraPreviewModal owns the modal presentation, camera preview, user controls, local UI state, and presentation of the received feedback.

useCameraSession owns camera and microphone acquisition and track lifecycle.

useVideoAnalysis owns the video-analysis lifecycle.

trainingTransport owns communication with the backend.

Transport-specific details such as frame encoding, WebSocket message formats, backend event types, and protocol implementation are documented in the corresponding transport and integration contracts rather than in this component section.

### Prototype References

#### Design Prototypes

- [camera.html](../../prototypes/design/pages/camera.html)

#### Vue Components

- [CameraPreviewModal.vue](../../prototypes/components/modal/CameraPreviewModal.vue)

#### Composables

- [useCameraSession.js](../../prototypes/composables/useCameraSession.js)
- [useVideoAnalysis.js](../../prototypes/composables/useVideoAnalysis.js)

#### Services

- [trainingTransport.js](../../prototypes/services/trainingTransport.js)

---

## CollapseForm

Name: CollapseForm

Description: CollapseForm is a reusable collapsible form container based on the remaining Personal Information section in Profile.

### Component Functionality

CollapseForm is a reusable collapsible form container used primarily for viewing and updating user-related information and settings, such as personal information, account details, notification preferences, profile settings, and other configurable user data. It composes FormStatusMessage at the top of its expanded content, immediately above the first parent-supplied field. It does not hardcode any form fields; all fields, field groups, components, and layout containers are provided by the parent through the default slot. The named footer slot is used for the form actions area, where the parent provides the shared Button components with their labels, variants, and actions. CollapseForm is responsible only for the collapsible container structure and presentation; it does not own the user data, field values, validation, persistence, or update logic.

### Component Properties and Data Flow

The `title` prop is required and `description` is optional. Optional `statusState` and `statusMessage` props are passed directly to FormStatusMessage as its `state` and `message`; `statusState` supports `pending`, `error`, and `success`, while an empty `statusMessage` suppresses the message. The component provides a default slot and a named `footer` slot.

The parent reads Pinia/store values, passes them to slotted fields, receives field changes, updates the store from its footer actions, and owns the status state and text passed through CollapseForm. `CollapseForm` holds no form data and never accesses or updates Pinia. It does not render a `<form>` or handle submission; the parent may wrap it in a form and own submit/reset behavior. FormStatusMessage remains visible above the first field whenever `statusMessage` is non-empty.

### Prototype References

#### Design Prototypes

- [CollapseForm.html](../../prototypes/design/components/forms/CollapseForm.html)

#### Vue Components

- [CollapseForm.vue](../../prototypes/components/forms/CollapseForm.vue)

---

## Footer

Name: Footer

Description: Footer is the reusable layout footer with parent-supplied copyright information and legal/support actions.

### Component Functionality

Footer renders the compact responsive footer defined by its dedicated design prototype. It presents the copyright text and an ordered set of layout footer actions without owning their navigation, consent, policy, or support behavior.

Items with `href` render as links. Items with `action` render through the shared TextButton and emit the selected action. Footer does not open policy modals, persist consent, call APIs, or inspect authentication and routing state.

### Component Properties and Data Flow

- `copyrightText`: required parent-supplied product copyright text.
- `items`: required ordered array of `{ label, href?, action? }` objects.
- `action`: emitted with the selected parent-defined action identifier.

Public Layout and Authentication Layout supply the content and handle emitted actions for their respective shells. The application-level consent feature owns Cookie Settings, Privacy, and Terms behavior. Footer remains one presentational feature component shared by both layout families.

### Prototype References

#### Design Prototypes

- [footer.html](../../prototypes/design/components/footer/footer.html)

#### Vue Components

None

---

## TopNav

Name: TopNav

Description: TopNav is the reusable public navigation for the application brand and parent-supplied links.

### Component Functionality

It renders the existing AI logo and Tennis AI Coach title. The approved visible navigation follows the dedicated prototype and Navigation Requirements in frontend.md. The component owns the responsive menu toggle, Escape dismissal, and resize cleanup.

Login uses the shared Button with `variant="secondary"` and `size="small"`. Start Free uses the same Button with `variant="primary"` and `size="small"`.

The design prototype defines the branding, alignment, actions, link states, and mobile menu appearance. It takes precedence over the older two-action arrangement in the public layout. The Vue component defines the reusable structure, props, menu interactions, and action events; it requires Vue 3.5+ (for instance-specific menu IDs) and an SFC/SCSS-capable build environment.

### Component Properties and Data Flow

- `items`: array of `{ label, href, active? }` objects; defaults to an empty array. Use unique `href` values. Optional `active` marks the current page.
- Login emits `login`.
- Start Free emits `register`.

The parent owns the handlers that navigate Login to the dedicated Login page and Start Free/Register to the dedicated Register page. TopNav contains no authentication logic, routing, API access, or store integration.

The public navigation items are defined as static application navigation data. Public Layout reads that data, determines the active item, and passes the resulting items to TopNav. TopNav does not own or mutate the navigation configuration.

### Prototype References

#### Design Prototypes

- [public-navigation.html](../../prototypes/design/components/navigation/public-navigation.html)

#### Vue Components

- [TopNav.vue](../../prototypes/components/navs/TopNav.vue)
- [Button.vue](../../prototypes/design/components/buttons/Button.vue)

---

## SidebarNav

Name: SidebarNav

Description: SidebarNav is the reusable vertical application navigation for the authenticated layout.

### Component Functionality

It renders the existing AI logo and Coach title as a brand section plus navigation items and mobile drawer controls; there is no Compose section or additional action area. Links navigate normally to application pages and `active` sets the current-page state.

The component preserves the 244px desktop sidebar and phone drawer breakpoints. On phones, the menu control opens a modal drawer with focus containment, scroll locking, and dismissal through Close, Escape, backdrop, or a link. Resizing and unmounting release the scroll lock.

The design prototype defines the sidebar's appearance, branding, link states, and responsive layout. The Vue component defines the reusable structure and drawer behavior; it uses the shared Button for drawer controls and requires Vue 3.5+ and an SFC/SCSS-capable build environment.

### Component Properties and Data Flow

SidebarNav accepts an items property containing the navigation entries rendered by the component.

Each navigation item has the following structure:

{ label, href, active?, icon? }
- label defines the visible navigation text.
- href defines the target application route and must be unique within the navigation list.
- active is optional and indicates whether the item represents the currently active page.
- icon is optional and may contain a Vue icon component or registered component name supplied by the parent.
The parent or authenticated layout is responsible for creating and populating the items array, including determining which item is active.

SidebarNav only renders the supplied navigation data and does not determine the current route itself.

The component owns only its local responsive drawer UI state, including opening, closing, focus handling, scroll locking, and cleanup.

SidebarNav has no API access, store integration, authentication logic, or custom navigation data ownership. Navigation data and application state are provided by the parent/layout.

The authenticated navigation items are defined as static application navigation data. Authentication Layout supplies Dashboard, Training, History, Subscription, Profile, Settings, and Checkout, determines the active item, and passes the resulting items to SidebarNav. SidebarNav does not own or mutate the navigation configuration.

### Prototype References

#### Design Prototypes

- [authenticated-navigation.html](../../prototypes/design/components/navigation/authenticated-navigation.html)

#### Vue Components

- [SidebarNav.vue](../../prototypes/components/navs/SidebarNav.vue)

---

## DashboardMetricCard

Name: DashboardMetricCard

Description: DashboardMetricCard is the reusable presentational statistic card used by Dashboard for values such as sessions this month, practice time, and the most recent session day. It does not calculate, fetch, format, compare, or persist statistics.

### Component Functionality

The component renders one compact card from exactly three parent-supplied props: `title`, `value`, and `footer`. The `footer` object selects either ordinary supporting text or the existing shared `Badge`. It always produces one footer row.

The Dashboard page is the parent. It reads the Dashboard statistics from `UserStore`, calculates comparisons, formats durations and dates, and supplies all three props to each card. Dashboard also owns count-up animation, loading, and error states. The component has no store, API, timer, navigation, click action, emitted event, or business rule. It must not infer footer content or Badge presentation from the statistic value.

### Component Properties and Data Flow

| Prop | Type | Default / requirement |
| --- | --- | --- |
| `title` | String | Required; short statistic name |
| `value` | String | Required; caller-formatted display value |
| `footer` | `{ text: String, type: 'text' \| 'badge', variant?: 'success' \| 'neutral' }` | Required; one supporting row. `variant` applies only to Badge and defaults to `success` |

Dependencies: shared `Badge` and the existing card surface styling. Dashboard remains the data and presentation-state owner.

```vue
<DashboardMetricCard
  title="Sessions this month"
  value="12"
  :footer="{ text: '+3 vs last month', type: 'badge', variant: 'success' }"
/>
```

### Prototype References

#### Design Prototypes

- [dashboard-metric-card.html](../../prototypes/design/components/feature-components/dashboard-metric-card.html)
- [Dashboard](../../prototypes/design/pages/dashboard.html)

#### Vue Components

- [DashboardMetricCard.vue](../../prototypes/components/features/dashboard/DashboardMetricCard.vue)

---

## TennisBallSlider

Name: TennisBallSlider

Description: TennisBallSlider is the self-contained rotating WebGL tennis-ball presentation used by the Training page. It combines the seamless green felt texture, two off-white curved seams, soft directional shading, and two identical textured `PLAY` labels placed on opposite sides of the rotating surface.

### Component Functionality

`TennisBallSlider.vue` owns only the canvas ref and mount/unmount integration. It creates one `TennisBallSliderController`, calls `init()` and `play()` after mount, and calls `destroy()` before unmount. The controller owns WebGL initialization, the sphere mesh, shaders, textures, animation-frame loop, resize observation, `play()`, `stop()`, and idempotent teardown. It never starts camera access, reads a store, calls an API, selects a route, or owns training state.

The tennis ball is decorative and hidden from assistive technology. The felt surface, seams, and labels rotate horizontally together through 360 degrees. The two `PLAY` labels use the same fuzzy felt character as the ball in a dark treatment and sit on opposite sides, so the second enters view as the first disappears behind the sphere. Soft local highlights and edge shading provide depth without exposing a geometry grid or making the ball predominantly dark. The ball does not bounce, travel vertically, move forward and backward, render a court background, or load a decorative player image. The controller stops advancing the rotation for reduced-motion users.

### Component Properties and Data Flow

The component has no props, emitted application actions, slots, store, service, API, router, or persistence dependency. The repository-owned felt asset is imported internally. The Training page owns the separate shared `Button` and the action that opens the existing camera/training flow.

### Prototype References

#### Design Prototypes

- [tennis-ball-slider.html](../../prototypes/design/components/sliders/tennis-ball-slider.html)
- [Training](../../prototypes/design/pages/training.html)

#### Vue Components

- [TennisBallSlider.vue](../../prototypes/components/sliders/tennis-ball-slider/TennisBallSlider.vue)
- [TennisBallSliderController.js](../../prototypes/components/sliders/tennis-ball-slider/TennisBallSliderController.js)
- [TrainingPage.vue](../../prototypes/pages/TrainingPage.vue)

---

## BaseTable

Name: BaseTable

Description: BaseTable is the reusable presentational table based on the History / Training Sessions table.

### Component Functionality

It renders a supplied title, dynamic columns, and rows. When the supplied columns contain both `Session Name` and `Focus` (matched by normalized label or key), BaseTable removes those two columns and appends a `Review` action column. Its default cell links to `row.reviewHref` when supplied, otherwise to `/sessions/{row[rowKey]}`, with the visible label `Review Session`. If either trigger column is absent, the component returns and renders the original columns unchanged.

The table preserves the History panel, headers, borders, spacing, and local horizontal scrolling on phone-sized screens. Scoped CSS is prototype-level visual guidance; production styling can later use external styles or shared design tokens. The HTML defines the visual reference; the Vue component defines the reusable rendering component. A Vue 3.5+ SFC build environment is required.

### Component Properties and Data Flow

The parent supplies:

- `title`;
- `columns` as `{ key, label }` entries;
- `rows`, where each column selects `row[column.key]`;
- optional `rowKey`, defaulting to `id` and falling back to the row index when absent.

Per-column `cell-<key>` slots receive `value`, `row`, and `column` for parent-owned formatting. History uses the shared `Badge` through `cell-status`: `Reviewed` uses the `success` variant, while `Sample` and `Incomplete` use `neutral`. The `cell-reviewSession` slot can override the Review cell.

History derives those visible labels from the authoritative row field `historyStatus`: `reviewed` becomes `Reviewed`, `sample` becomes `Sample`, and `incomplete` becomes `Incomplete`. The workflow-level `status` field remains separate and must not be used to infer sample or review classification.

The parent owns configuration, data, formatting, and any integration with Pinia. The component contains no store access, duplicated state, API calls, or History-specific business logic.

BaseTable does not own Badge state or status semantics. The parent selects the Badge variant from its authoritative status contract and supplies the formatted status cell.

Dependencies: the shared `Badge` component is used by consumers that render semantic status cells, including History.

Да. The parent/page is responsible for sourcing the table data from the relevant application store, preparing the columnsandrows, and passing them to BaseTable through its properties. 

### Prototype References

#### Design Prototypes

- [BaseTable.html](../../prototypes/design/components/tables/BaseTable.html)
- [BaseTable-review.html](../../prototypes/design/components/tables/BaseTable-review.html)

#### Vue Components

- [BaseTable.vue](../../prototypes/components/tables/BaseTable.vue)

---

## PaymentCardPlan

Name: PaymentCardPlan

Description: PaymentCardPlan is the single Subscription plan card for option, selected, and current-plan presentation.

### Component Functionality

Documentation, Vue prototypes, the Subscription entry, and visual prototypes use this one authoritative identity. Do not create separate plan-card components for performance, selected, or subscription states; selected and current-plan presentation are states of this component.

The plan-option state uses the existing `2px solid #b7ff4a80` outline, Most popular eyebrow and primary Button. Non-selected plan options use a secondary Button. Subscription initially supplies `planName="No selected plan"` and `actionLabel="Change plan"` without a price, status label, or selected state. After the page selects a plan, the larger current-plan card receives that plan's name, description, price and billing period, plus `statusLabel="Selected plan"`, `actionLabel="Change plan"`, and `continueActionLabel="Continue"`. The `.plan-grid` container controls compact title/price/description ordering, while Subscription retains its larger current-plan hierarchy.

### Component Properties and Data Flow

These components belong to the **Subscription feature**. Subscription is the feature owner; `PaymentCardPlan` and `BillingDetailsCard` are its focused child components. Their shared directory provides the physical grouping.

| Prop | Type / default | Display responsibility |
| --- | --- | --- |
| `planName` | Required string | Plan name |
| `price` | String, empty by default | Parent-formatted price such as `€19`; the component performs no calculation |
| `billingPeriod` | String, empty by default | Text after the slash, such as `month`; hidden when absent |
| `description` | String, empty by default | Existing short plan description; hidden when absent |
| `features` | String array, empty by default | Optional feature list; hidden when empty |
| `statusLabel` | String, empty by default | Current-plan status such as `Active · demo`; independent of selection |
| `selected` | Boolean, `false` | Presentation-only selected outline, label and primary action styling |
| `selectedLabel` | String, `Most popular` | Selected-plan highlight label; empty hides the label |
| `actionLabel` | String, empty | Explicit button label; otherwise `Change plan` when `statusLabel` exists or `Choose plan` |
| `continueActionLabel` | String, empty | Optional second primary action, used by the current-plan state after a plan has been selected |

The explicit TypeScript-facing contract is:

```vue
<PaymentCardPlan
  plan-name="Performance"
  price="€19"
  billing-period="month"
  description="Realtime coaching, richer insights and session review tools."
  :selected="true"
/>
```

The component emits `action` and the optional `continue` without payloads through shared Button clicks. The page owns actions and data. The card contains no callback prop, store access, backend request, price calculation or billing logic.

Subscription owns the plan-card state through its feature component and local composable. It reveals the three plan cards after Change plan, keeps the options visible after selection, updates the larger current-plan card, and enables Continue to Checkout only when a plan exists.

### Prototype References

#### Design Prototypes

- [payment-card-plan.html](../../prototypes/design/components/cards/payment-card-plan.html)
- [payment-card-plan-selected.html](../../prototypes/design/components/cards/payment-card-plan-selected.html)
- [payment-card-plan-current.html](../../prototypes/design/components/cards/payment-card-plan-current.html)

#### Vue Components

- [PaymentCardPlan.vue](../../prototypes/components/features/subscription/PaymentCardPlan.vue)
- [Subscription.vue](../../prototypes/components/features/subscription/Subscription.vue)

#### Composables

- [useSubscription.js](../../prototypes/components/features/subscription/useSubscription.js)

---

## BillingDetailsCard

Name: BillingDetailsCard is a reusable presentation component for displaying billing summary information and a related billing action.

Description: BillingDetailsCard is the Subscription billing-details presentation.

### Component Functionality

It presents the heading, next-renewal text, payment-method text, and Manage billing action. It is distinct from a plan card and adds no billing fields or real integration.

The component does not add billing address, invoices, card brand, last four digits, expiry, customer identifiers, or real integration because those fields are absent from the current Subscription UI. Both the Vue implementation and design prototype use Subscription's existing panel typography, spacing and content. Subscription has no separate comparison-page link because its Change plan action reveals the three plan options directly.

### Component Properties and Data Flow

The parent component is responsible for providing the billing data and handling the emitted action. BillingDetailsCard only renders the supplied data and emits the action event; it has no direct store access, backend requests, or billing integration.

| Prop | Type / default | Display responsibility |
| --- | --- | --- |
| `title` | String, `Billing details` | Card heading |
| `renewalText` | Required string | Existing renewal line, currently `Next renewal: Oct 26, 2026 (illustrative).` |
| `paymentMethodText` | Required string | Existing payment-method line, currently `Payment method: Not connected.` |
| `actionLabel` | String, `Manage billing` | Shared secondary Button label |

The explicit TypeScript-facing contract is:

Example usage keeps the two visible billing fields exactly as they appear in Subscription:

```vue
<BillingDetailsCard
  renewal-text="Next renewal: Oct 26, 2026 (illustrative)."
  payment-method-text="Payment method: Not connected."
  @action="openBillingMessage"
/>
```

The component emits `action` without a payload via the shared secondary Button. The Subscription page owns the action and existing informational demo message.

The Vue implementation and design prototype are listed below.

The parent component is responsible for preparing the plan data and passing the required values to PaymentCardPlan through its properties.

PaymentCardPlan only renders the supplied data and emits action and continue events. It has no direct store access, backend requests, price calculations, or billing logic.

### Prototype References

#### Design Prototypes

- [billing-details-card.html](../../prototypes/design/components/cards/billing-details-card.html)

#### Vue Components

- [BillingDetailsCard.vue](../../prototypes/components/features/subscription/BillingDetailsCard.vue)

---


## Checkout

Name: Checkout

Description: Checkout is the feature component for selected-plan checkout and payment-return presentation.

### Component Functionality

The Checkout design prototype is the visual reference for the selected-plan, status, and successful order-summary cards. Pay with Stripe and Pay with PayPal are placed under the selected plan. The right-hand area shows PaymentStatusCard until backend-verified success, then replaces it with OrderSummaryCard. Checkout contains no Payment Information section or raw payment fields. Static labels match the prototype.

### Component Properties and Data Flow

These components belong to the **Checkout feature**. Checkout is the feature owner; `ChoosePlanCard`, `PaymentStatusCard`, and `OrderSummaryCard` are its focused child components. Their shared directory provides the physical grouping.

Checkout composes `ChoosePlanCard`, `PaymentStatusCard`, and `OrderSummaryCard`. Its feature-local composable adapts checkout state into their props and actions. Transient hosted-checkout state belongs to a Pinia store in the common stores directory because it must survive navigation and a provider return. The prototype store calls a demo checkout service; production replaces that demo boundary with the documented backend endpoints. Persisted, backend-verified subscription truth remains only in `UserStore.subscription` and is never duplicated into CheckoutStore.

The colocated Checkout entry installs Pinia and mounts the composition. Child cards contain no composables, fetching, store access, payment calculations, or page-level business logic. No props, emitted events, or slots are specified for Checkout in the current documentation.

### Prototype References

#### Design Prototypes

- [checkout.html](../../prototypes/design/components/checkout/checkout.html)

#### Vue Components

- [Checkout.vue](../../prototypes/components/features/checkout/Checkout.vue)

#### Composables

- [useCheckout.js](../../prototypes/components/features/checkout/useCheckout.js)
- [useCheckoutStore.js](../../prototypes/stores/useCheckoutStore.js)

#### Services

- [demoCheckoutService.js](../../prototypes/services/demoCheckoutService.js)

#### Adapters

- [Checkout entry](../../prototypes/design/components/checkout/main.js)

---

## OrderSummaryCard

Name: OrderSummaryCard

Description: OrderSummaryCard is the Checkout presentation for a successful order summary.

### Component Functionality

It presents the Plan, Billing period, Subtotal, Tax, Demo total, and payment Status rows, plus an explanatory note and page-owned actions. Checkout renders it only after backend-verified success; the prototype displays `Paid`.

### Component Properties and Data Flow

Required string props are `headingId`, `title`, `plan`, `billingPeriod`, `subtotal`, `tax`, `total`, `paymentStatus`, `note`, `actionLabel`, `cancelLabel`, and `cancelHref`. `statusMessage` is an optional string defaulting to empty. Amounts and status are supplied as formatted display strings.

The action emits `complete` without a payload; the page handles it. Cancel follows `cancelHref`. The card performs no transaction or subscription logic.

OrderSummaryCard renders a StateLabel for the payment status and two Button components for actions; it contains no business logic.

The parent component retrieves the order summary data from the appropriate store and passes it to OrderSummaryCard via props. OrderSummaryCard uses the reusable StateLabel component to display the payment status and two Button components for user actions. The card does not access the store directly or contain business logic.


### Prototype References

#### Design Prototypes

- [order-summary-card.html](../../prototypes/design/components/cards/order-summary-card.html)

#### Vue Components

- [OrderSummaryCard.vue](../../prototypes/components/features/checkout/OrderSummaryCard.vue)

---

## HomePageInfoSection

Name: HomePageInfoSection

Description: HomePageInfoSection is the reusable Home section for introductory content and feature cards.

### Component Functionality

It contains the existing eyebrow, headline, description, both CTA links, and all three feature cards. Production CTA actions use the shared Button contract, with page/feature-owned handlers; no page-specific button components are introduced. The current prototype still contains inline CTA links and must be adapted during implementation while preserving navigation semantics.

The component reuses the Home styles. The Home prototype entry mounts it; direct-`file://` previews preserve the equivalent static markup.

### Component Properties and Data Flow

`trainingHref` and `dashboardHref` default to the existing Home page destinations. The component measures headline alignment on mount, font readiness, and resize, and cleans up its observer on unmount. CTA navigation actions remain page/feature-owned. No store, composable, service, API call, or additional state contract is specified.

### Prototype References

#### Design Prototypes

- [home-page-info-section.html](../../prototypes/design/components/sections/home-page-info-section.html)

#### Vue Components

- [HomePageInfoSection.vue](../../prototypes/components/sections/HomePageInfoSection.vue)

#### Adapters

- [Home entry](../../prototypes/home/main.js)

---

## HomePageVideoSlider

Name: HomePageVideoSlider

Description: HomePageVideoSlider is the reusable Home video slider and interactive AI tennis-analysis preview.

### Component Functionality

The component uses `Pixi.js` for rendering, animations, and visual overlay logic. It includes the video slider, microphone control, audio connection state, three information/status control elements, and Motion Tracking visualization. Motion Tracking displays analysis overlays such as body tracking lines, movement vectors, angles, and biomechanical values synchronized with the active video sequence.

Video pause/resume and seek handlers do not update tracking text. Coaching sentences occupy equal slots across the full configured slider cycle (currently five 4.8-second slots across 24 seconds, each with 3.3 seconds of sentence display and 1.5 seconds of `...`), independently of freezes. Explicit pause points at `timelineItem.time / playbackRate` invoke `onVideoPause()`, stopping the main timeline and video. `PlayerAnalysisTimeline` creates its GSAP timeline only when a hold begins, runs the drawing sequence, and invokes `onVideoResume()` after the configured duration.

HTML-only/file previews retain the original Canvas demo, using the same relocated video asset; Home under Vite mounts the Vue/Pixi component. Microphone/status cues remain illustrative, with no audio recording.

### Component Properties and Data Flow

The Vue component owns all DOM refs, video and slider state, microphone interaction, analysis timing, Pixi.js rendering lifecycle, resize handling, cleanup on unmount, and initialization-error handling. It interacts only with a controller instance through explicit `init()`, `play()`, and `destroy()` calls.

The controller owns the renderer, video timeline controller, lifecycle handler, and AI motion-tracking panel, validates required elements before async initialization, and coordinates cleanup. `play()` starts playback without calling `init()`. The AI motion-tracking panel independently rotates demo Phase statuses every 2.5 seconds; the controller starts its single interval on playback and clears it on destruction.

Local configuration contains static timing and annotation data. The renderer handles overlays and only prepares geometry, draws individual segments/labels, and renders the stage. The video timeline controller creates the main timeline and initializes the audio timeline in `init()`; `play()` coordinates video playback and audio-timeline playback through public APIs. The audio timeline owns coaching, typing, and microphone UI. The player-analysis timeline owns the analysis phase and starts an animation-timeline GSAP sequence nested within that phase. Segment tweens control drawing order, progress, and label alpha. Both GSAP timelines repeat indefinitely.

The controller exposes `init()`, `play()`, `pause()`, and `destroy()`. The lifecycle handler handles only video errors by showing the error UI and pausing video through the controller, and removes its listener on destruction. The controller's `play()` starts the video controller directly after initialization. Visibility, page hide/show, resize, intersection, readiness, buffering, and seek events no longer drive automatic playback control. There is no separate RAF loop, hold timer, or Pixi ticker for video timing.

All class files use PascalCase names. The component stylesheet preserves the presentation. The component imports its video from its own assets directory. No composable or service is used.

### Prototype References

#### Design Prototypes

- [slider.css](../../prototypes/components/sliders/home-page-video-slider/slider.css)

#### Vue Components

- [HomePageVideoSlider.vue](../../prototypes/components/sliders/home-page-video-slider/HomePageVideoSlider.vue)

#### Helpers

- [SliderLifecycle.js](../../prototypes/components/sliders/home-page-video-slider/SliderLifecycle.js)
- [SliderConfig.js](../../prototypes/components/sliders/home-page-video-slider/SliderConfig.js)
- [PixiRenderer.js](../../prototypes/components/sliders/home-page-video-slider/PixiRenderer.js)

#### Controllers

- [SliderController.js](../../prototypes/components/sliders/home-page-video-slider/SliderController.js)
- [VideoTimelineController.js](../../prototypes/components/sliders/home-page-video-slider/VideoTimelineController.js)
- [AudioTimeline.js](../../prototypes/components/sliders/home-page-video-slider/AudioTimeline.js)
- [PlayerAnalysisTimeline.js](../../prototypes/components/sliders/home-page-video-slider/PlayerAnalysisTimeline.js)
- [AnimationTimeline.js](../../prototypes/components/sliders/home-page-video-slider/AnimationTimeline.js)
- [AIMotionTrackingPanel.js](../../prototypes/components/sliders/home-page-video-slider/AIMotionTrackingPanel.js)
