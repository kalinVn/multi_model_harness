# Name
vite-dev-environment

# Description
Prepare, reuse, start, and verify the isolated Vite environment under source/debug/frontend for component previews and documented local example APIs.

# Instructions

## Migrated contract

## Vite Debug Development Environment

## Scope

Manage only `source/debug/frontend/`. Never modify production Vite configuration, production frontend source, prototypes, or `.codex/`.

## Inputs

- `debug_root`, which must resolve to `source/debug/frontend/`.
- optional preferred host and port.
- optional component slugs whose preview URLs must be checked.
- optional page or component documentation for local example API flows.
- whether an interactive preview must remain running after verification.

Reject a debug root outside the required directory.

## Workflow

1. Inspect the debug root, `package.json`, Vite configuration, source harness, scenario registry, tests, installed dependencies, and any existing debug-server metadata.
2. Preserve existing components, scenarios, mocks, and tests. Create only missing infrastructure and repair only debug infrastructure proven broken.
   When an assigned preview needs an example API, follow its component or page documentation to `docs/frontend/example-apis/`. Read the linked request, response, fixture, and scenario definitions before adding any mock route; do not infer an API from a visual prototype alone.
3. Confirm the debug package uses a security-supported Vue/Vite/Vitest toolchain compatible with the repository's Vue 3 code and current Node runtime. Do not upgrade or change production dependencies merely to match the isolated debug package.
4. Run the debug package's declared test and build scripts from its own root when present. Record each command and observed result; never report an unavailable script as passed.
5. Before starting a server, inspect listening processes and the debug metadata file. Reuse a process only when its command/root belong to this debug workspace and `GET /__debug-health` returns the expected marker. A port being open is not sufficient evidence.
6. If no suitable server exists, choose an available loopback port, run the debug package's Vite dev command from its own root, and record its PID, root, origin, and start time in the ignored `.vite/debug-server.json` file.
7. Do not start a second server when a healthy matching server exists. Never terminate an unrelated process. If stale metadata identifies no live matching process, replace only that metadata.
8. Poll the health URL with short bounded retries. On failure, report the command, exit state, and safe log excerpt; do not claim a usable preview.
9. Verify the index and requested `/components/<slug>` URLs. Return the actual origin and URLs, not an assumed port.
   For an assigned example API, also verify its documented success and failure cases with requests to the local server.
10. Leave a reused or newly started server running only when the calling workflow requests an interactive preview. Otherwise stop only the process started by this invocation and remove its metadata.

## Infrastructure Contract

Required files:

- `package.json`
- `index.html`
- `vite.config.js`
- `src/main.js`
- `src/App.vue`
- `src/ComponentPreview.js`
- `src/debug-registry.js`
- `src/scenarios/index.js`

The Vite configuration must:

- keep its root inside the debug directory;
- bind to loopback by default;
- expose `/__debug-health` with an unambiguous debug marker;
- support history fallback for component preview URLs;
- write build output only to the debug root's ignored `dist/`;
- use Vue SFC support without importing production configuration.

## Local Example APIs

When the selected Login preview calls for an example API, implement only the documented mock endpoints in the isolated Vite dev server. The Login example (`../../../docs/frontend/example-apis/login.md`) defines `POST /api/login`, example users, responses, and deterministic failure cases; the social-auth example (`../../../docs/frontend/example-apis/social-auth.md`) defines its separate mock route. Treat these documents as examples for the debug workspace, never as replacements for `docs/frontend/integration-contracts.md`.

When the Login example requires confirmation, also implement its documented `POST /api/auth/challenges/{challengeId}/verify` route. Keep each challenge only in server memory, bind it to its matched fictional fixture and offered method, enforce expiry, bounded attempts, and single use, and return no user data before a correct confirmation. The fixed manual-test code remains a local debug fixture: never include it in browser bundles, page props, responses, logs, URLs, or storage. Verify challenge creation, invalid-code retry, successful confirmation, and rejected reuse before reporting the preview ready.

When the selected Register preview calls for an example API, the Register example (`../../../docs/frontend/example-apis/register.md`) defines its loopback `POST /api/register` request, response, and deterministic outcomes. Keep it separate from production registration; a successful example result is not a stored account or session.

- Keep routes loopback-only and unavailable from production builds. Do not modify production Vite configuration, authentication services, or application source.
- Derive multiple fictional users from the example fixtures, but keep their credentials and salted password hashes in server-only local data. Never send the fixture list, hashes, or raw credentials to the browser. A single matched user's projected data may be returned in a documented success case.
- Implement the documented per-user success and failure scenarios deterministically; do not turn an example failure into a real account lock or authorization decision. Return safe errors without disclosing whether an email exists.
- The email/password mock may skip reCAPTCHA verification only locally. The social-auth mock must not accept fabricated provider tokens as proof of identity or claim to create a production OAuth session.
- Verify route method, payload validation, success and failure statuses, response shape, and absence of secret fields. Do not claim a production authentication test passed because the mock passed.
- When the Google Auth Service Debug stage is selected, provide only the documented loopback `POST /api/auth/google` route in `docs/frontend/example-apis/social-auth.md`. The debug service returns its fixed example token locally and makes no start request; the page sends that token once to this route. Match the documented fixture and return only a deterministic example account response. Reject missing or different tokens safely. This does not verify a Google identity, create an application session, or add a production endpoint.

The harness must discover only debug components, accept scenario props and slots, observe only declared emitted events, show state/error information, and provide stable `/components/<slug>` URLs without creating production pages.

## Dependency Handling

Use the debug package's declared dependencies. Run installation only when dependencies are missing or the lockfile/package manifest changed. Do not use global packages and do not edit another package manifest. Do not add Vitest, Vue Test Utils, Playwright, or MSW unless a selected component requires them and the current debug package cannot perform the assigned checks.

## Output

Report:

- files created or repaired;
- whether dependencies were reused or installed;
- whether a server was reused, started, stopped, or unavailable;
- PID when started by this skill;
- actual origin, index URL, and verified component URLs;
- health/build/test results actually observed;
- runtime errors and blockers.

Never claim that the production frontend was tested by this isolated environment.
