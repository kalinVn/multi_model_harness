## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/feature-components.md

# ConfirmLoginForm

## Additional Description and Functionality

Build the isolated debug `ConfirmLoginForm` from its authoritative feature-component contract and declared design and Vue prototypes. Despite its established component name, the form is the shared feature-level presentation for both Login MFA and registration verification.

The component remains presentation-only. It accepts `purpose`, the backend-offered `method`, masked `destinationHint`, `pending`, `errorMessage`, and `expired` state; it owns only the entered six-digit code and immediate local validation; and it emits `submit({ method, code })` only after exactly six digits are present. `purpose: 'login'` uses Login wording, while `purpose: 'registration'` uses registration-confirmation wording.

Do not let the component create or retain a challenge, choose a verification method, select or call an endpoint, load user data, create a session, or navigate. Those responsibilities belong to the owning Login or Register Page. Reusing the component must not merge Login MFA and registration verification into one backend challenge type.

## Debug Scenarios and Verification

- Render an email challenge with a masked destination hint.
- Render both `login` and `registration` purposes and verify their title, pending copy, and submit label are distinct.
- Verify incomplete and non-numeric input is rejected locally.
- Verify pending disables editing and prevents duplicate submission.
- Verify invalid-code feedback leaves the field available for correction.
- Verify expired state disables submission.
- Preserve the accessible field label, one-time-code autocomplete, numeric input mode, visible focus, and error announcement required by the authoritative contract.

## References

- `docs/frontend/feature-components.md#confirmloginform`
- `prototypes/design/components/forms/confirm-login-form.html`
- `prototypes/components/forms/ConfirmLoginForm.vue`
