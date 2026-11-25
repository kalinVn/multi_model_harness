# Name
google-auth-service-debug

# Description
Build and verify the isolated Login page's one-click Google example-token callback, without changing production OAuth or treating a fixture as a real identity credential.

# Instructions

## Migrated contract

## Google Auth Service Debug

Use this stage only when the validated Login page and its Additional Description and Functionality require the local Google example. Run it after debug components and layouts are ready and before the Login page is built. Read `docs/frontend/example-apis/social-auth.md` and the Login page assignment before implementing anything.

Create the debug service under `source/debug/frontend/src/services/` and its tests under `source/debug/frontend/tests/`. The service receives `socialLogin({ provider: 'google' })` from the page, never reads form credentials, and simulates a provider callback locally with the exact example token documented in `docs/frontend/example-apis/social-auth.md`. It makes no HTTP request. Its `signIn` result returns that token to the owning Login page; the service does not call the mock backend. The page passes the token to its own backend-example function, which sends one request to the documented loopback Vite route and accepts only its confirmed response. One click on the existing Google button starts the flow; do not render a second button or change the design prototype. Guard duplicate requests and invalidate late results on disposal.

The token is a fixed local test fixture, not a Google ID token, OAuth code, provider credential, or production authentication authority. Do not place it in a URL, browser storage, logs, scenario output, or a production build. The loopback Vite route matches only the documented fixture to select a deterministic example response; this is not identity verification. The response may show example account data but must not create an application session or grant protected access. Keep real Google SDK loading, callback verification, account linking, and session creation on the existing production backend-owned OAuth contract.

Return the service interface, changed paths, test results, and any blocked dependency. The Login page builder consumes the service result; Vite Dev Environment owns the loopback endpoints and package-level test/build/runtime verification.
