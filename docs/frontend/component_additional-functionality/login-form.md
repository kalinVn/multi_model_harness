# LoginForm

## Additional Description and Functionality

Extend the isolated debug version of `LoginForm` with the Google Identity Services integration boundary defined by the latest commit on the `ai-trener-fronend-debug` branch.

### Google Login Entry

- Keep the existing Google, Facebook, and Apple social-login choices.
- When Google is selected, emit `socialLogin` with the object payload `{ provider: 'google' }`.
- In the isolated debug preview, the existing Google social button starts the one-click example handoff. Do not render a second button or claim that the preview uses Google's official provider UI.
- Facebook and Apple continue to use their existing social-login entry behavior.
- Social login must not submit `email`, `password`, or `recaptchaToken`.

### Ownership Boundary

`LoginForm` owns only its form UI, local validation, provider-selection event, and presentation of the parent-supplied pending or error state.

`LoginForm` must not:

- load or initialize the Google Identity Services SDK;
- read, decode, validate, log, or store a Google credential;
- call an authentication endpoint;
- access or update `AuthStore`;
- create an application session;
- navigate after authentication.

The production parent workflow owns SDK initialization, official-button rendering, credential handoff to the backend authentication boundary, session acceptance, profile initialization, errors, and navigation. The isolated debug parent instead uses `GoogleAuthServiceDebug` and the local example API; it never creates a real session.

### Example Behavior

- For the standard email/password example flow, use the Login Example API (`docs/frontend/example-apis/login.md`) only as a reference for the parent Login Page's request and response states. `LoginForm` emits the validated payload and presents parent-supplied feedback; it does not call the example endpoint.
- Use a debug-only parent service to observe `socialLogin({ provider: 'google' })` and start the local handoff on that click.
- The parent Login Page's Social Auth Example API (`docs/frontend/example-apis/social-auth.md`) defines the local HTTP simulation; `LoginForm` must not call it.
- Clearly identify the result as an example simulation; do not present it as a real Google sign-in.
- Support an idle state, a Google-pending state, a recoverable provider-error state, and a successful mock handoff state.
- While Google authentication is pending, prevent a duplicate Google request without disabling unrelated form controls unless required by the existing component contract.
- Preserve entered non-secret form values after a recoverable Google error. Never retain a password or provider credential in debug logs or scenario output.

### Validation Scenarios

Verify that:

- selecting Google emits exactly one `socialLogin` event with `{ provider: 'google' }`;
- the standard `submit` event is not emitted by the Google flow;
- no standard-login fields are included in the social-login payload;
- no second provider button or hidden trigger is rendered in the isolated debug preview;
- duplicate Google actions are ignored while the first mock request is pending;
- a provider failure is presented safely and allows a retry;
- keyboard focus and an accessible name are preserved for every visible social-login action;
- unmounting the page invalidates pending service callbacks.
