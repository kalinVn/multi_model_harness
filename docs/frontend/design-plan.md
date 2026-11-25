## Available Agents

None

## Available Skills

None

## Available Rules

- AGENTS.md

## Available Documents

- docs/frontend/frontend.md
- docs/frontend/shared-ui-components.md
- docs/frontend/feature-components.md
- docs/frontend/frontend-project-structure.md

# Tennis AI Coach — Frontend Design Plan

## Frontend Type

`new`

## Sources and Repository Findings

- Requirements: `docs/frontend/frontend.md`.
- Visual references: `prototypes/design/index.html` (catalog) and `prototypes/design/pages` (current application prototypes). The previously referenced standalone `tennis-ai-coach.html` is no longer present; the library preserves the current multi-page prototypes.
- Planning workflow: `claude/skills/plan-new-frontend.md`.
- Shared rules: `claude/rules/frontend/frontend-design-system.md`.
- Existing application: `frontend/index.html` contains only `test 2`. No Vue source, package manifest, application tests, or backend application files were found in the inspected repository. Existing uncommitted content must be preserved when implementation begins.
- The available `codex/workflows/` files concern infrastructure; none is needed for this design-only task. Any later infrastructure change must load its relevant workflow first.
- Use Vue 3, JavaScript, Vue Router, and Vite. The frontend specification explicitly overrides the general AGENTS.md TypeScript default. Retain Pinia under the repository stack agreement; do not add another state library. `UserStore` is the single authoritative frontend store for persisted authenticated application data, while unsaved drafts and transient UI/device state stay local.
- Affected domains: public UI, authentication UI/session navigation, dashboard, training/media/analysis transport, session review/history, subscription and checkout UI, and account preferences. Backend inference, coaching decisions, identity authority, persistence, and billing authority remain external dependencies.

## Design Foundation

### Visual direction and prototype translation

Use the prototype's forest-green background, layered dark panels, off-white text, lime primary actions, and restrained cyan information accents. Retain its split landing hero, court illustration, three feature cards, training preview, subscription plan selection, rounded panels, and compact form composition. The product name remains Tennis AI Coach.

The public page can use subtle radial highlights. Authenticated pages should use calmer surfaces to prioritize training and readable data. Use the prototype's court artwork as an illustration concept, rebuilding maintainable markup or SVG during implementation rather than copying its code. Public sample overlays must be labeled as an illustrative preview, not a live camera or real analysis.

Training is the primary workflow: camera setup → explicit analysis start → one supported coaching cue → stop/end → session review when available. Do not reuse the prototype's fake camera toggles, fabricated duration, metrics, or coaching text as real application state. The prototype's prices, “Most popular,” free-start promise, and sub-second feedback target are not verified product facts; final plan prices and claims require supported product/backend data.

### Required tokens

These are proposed implementation values derived from the reference and shared rules. Validate contrast on actual foreground/background combinations during implementation.

| Family | Tokens / initial values | Use |
| --- | --- | --- |
| Background | background `#07100c`; surface `#0d1913`; secondary `#13231b`; elevated `#17271f` | Page, cards, controls, dialogs |
| Text | primary `#f4f7f5`; muted `#a8b5ae` | Body, labels, secondary descriptions |
| Brand | primary `#b7ff4a`; hover `#c8ff72`; active `#a7eb3d`; secondary `#65e8ff` | Primary actions, selected details, information |
| Semantic | success `#67e8a5`; warning `#ffc857`; danger `#ff6b7a`; information `#65e8ff` | Always accompanied by a readable state label; dark text on bright filled controls |
| Borders | subtle white at 10%; strong white at 20%; explicit focus ring in primary accent | Panel separation; increase contrast for interactive boundaries as required |
| Typography | Inter if supplied, otherwise system sans-serif; weights 400/600/700/800 | Avoid a font download dependency in the initial foundation |
| Type scale | display `clamp(2.5rem, 6vw, 4.875rem)`; page title `clamp(2rem, 4vw, 3rem)`; section title `clamp(1.75rem, 4vw, 3rem)`; component title 1.125rem; body 1rem; small 0.875rem; metadata 0.75rem | Display line height about 1.0, body 1.6; tabular numerals for timers |
| Space | 4, 8, 12, 16, 20, 24, 32, 40, 48, 64px | Shared spacing rhythm; no page-specific duplicate scales |
| Radius | 8, 12, 14, 22, 30px; pill 999px | Small details, navigation, controls, cards, hero/media panels |
| Elevation | small `0 8px 24px rgba(0,0,0,.18)`; large `0 24px 80px rgba(0,0,0,.35)` | Restrained card elevation; preview/dialog prominence |
| Motion | 150ms fast; 200ms normal; 300ms slow, ease | Short interaction feedback; reduced-motion override |
| Layout | public/content max 1160px; auth max 450px; desktop sidebar 220px; page gutters 16–32px | Consistent alignment; training uses remaining viewport width |
| Breakpoints | mobile ≤600px; tablet ≤900px; larger screens >900px | Adjust only when content requires it; test intermediate widths |
| Controls | minimum practical target 44px; standard field height 46px | Touch and keyboard usability |

### Layout and responsive principles

- Desktop public hero uses two columns; three-card feature groups and the Subscription plan grid use three columns. Stack them on narrower screens in reading order.
- Desktop application navigation uses a sidebar. At ≤900px, replace it with a labeled menu opening an accessible navigation dialog; keep every documented authenticated destination reachable.
- Training uses a roughly 70/30 media/feedback split where space permits. On mobile, stack media, primary controls, focused cue, then secondary status. Keep stop controls readily reachable and allow scrolling rather than clipping content into a fixed viewport.
- Preserve the actual video aspect ratio with `object-fit: contain`. Overlay coordinates must share the video's scale, offsets, and mirroring. Do not obscure the player with controls or stretch portrait video into a landscape crop.
- Forms remain single-column and comfortably constrained. Prefer readable stacked session information to wide tables on mobile.
- Use semantic headings, labeled inputs, visible focus, text status labels, accessible icon names, and important asynchronous announcements. Dialogs need focus containment/restoration and Escape behavior. Do not announce every frame or timer tick.

## Required Layouts

| Name | Purpose and shared structure | Used by pages |
| --- | --- | --- |
| PublicLayout | Branding, sticky public navigation to Home/Features/Training/Login, authentication actions, empty content container, footer | Landing, Features, Login, Registration |
| AuthenticationLayout | Responsive authenticated navigation and header with an empty content container | Dashboard, Training, History, Subscription, Checkout, Profile, Settings, Session Review |

Dedicated authentication routes are the proposed default. They retain the prototype's compact card and mode-switch appearance while supporting refresh, direct links, and keyboard navigation. A route-backed modal is the optional alternative, not an additional required implementation. Shared dialogs remain needed for mobile navigation and session/account confirmation flows.

## Required Pages

The orchestrator selects implementation skills from the page requirements and dependencies below. This plan defines the work and does not assign skills.

| Page / layout | Purpose and required sections | Shared components | Feature components | Dependencies |
| --- | --- | --- | --- | --- |
| Landing / PublicLayout | Hero and value proposition; features; labeled training preview; login/register entry points; footer | Button, Card, Badge, NavigationItem, PageHeader, AsyncState, Dialog | None | verified product copy; local illustrative court asset |
| Features / PublicLayout | Page-level product capability copy and three numbered feature cards | Button, BaseCard, PageHeader | None | existing BaseCard prototype and parent-supplied content |
| Login / PublicLayout | Email, password, validation, submit/loading/authentication error; registration switch | Button, FormField, Card, AsyncState | None | backend login/session contract; safe return destination |
| Registration / PublicLayout | Name, email, password, validation, submit/loading/registration error; login switch | Button, FormField, Card, AsyncState | None | registration/password policy and session result contract |
| Dashboard / AuthenticationLayout | Recent training, next recommended action, and prominent start-training action | Button, Card, Badge, PageHeader, AsyncState, NavigationItem, Dialog | SessionHistoryList | session summaries and supported focus data |
| Training / AuthenticationLayout | Dominant camera/video preview; permission state; camera and analysis start/stop; focused cue; connection/analysis state; duration/session state; overlay; loading/unavailable/disconnected/error states | Button, Badge, PageHeader, AsyncState, NavigationItem, Dialog | CameraPreview, SessionControls, TrainingOverlay, CoachingFeedback | browser media support and secure context; analysis/session contracts |
| Session Review / AuthenticationLayout | Summary, detected issues, supported metrics, recommendations, analyzed moments when available; incomplete/low-confidence labeling | Button, Card, Badge, PageHeader, AsyncState, NavigationItem, Dialog | SessionSummary |
| History / AuthenticationLayout | Prior sessions, review links, loading/empty/error states | Button, Card, Badge, PageHeader, AsyncState, NavigationItem, Dialog | SessionHistoryList | Session list contract and available paging semantics |
| Subscription / AuthenticationLayout | Available plans, current plan, comparison, subscription actions, and protected checkout | Button, Card, Badge, PageHeader, AsyncState, NavigationItem, Dialog | PaymentCardPlan, BillingDetailsCard, CheckoutFlow | authoritative plan/subscription data, checkout creation/return and transaction verification contracts |
| Profile / AuthenticationLayout | Supported personal information; view/edit, validation, saving, saved/error feedback | Button, FormField, Card, PageHeader, AsyncState, NavigationItem, Dialog | ProfileEditor | personal-information schema, writable fields, update contract |
| Settings / AuthenticationLayout | Account security, privacy and notification settings; save/result feedback and data-management actions | Button, FormField, Card, PageHeader, AsyncState, NavigationItem, Dialog | SettingsEditor | supported notification/privacy schemas, persistence and security/data-management action contracts |

Page composition must not introduce additional project-specific component names beyond the specification's list. Compact feature variants are reuse of those components, not new feature components. Authentication forms remain page composition of shared fields and buttons.

## Required Shared Components

Only patterns required by the specification and reused across pages/layouts are included. `AsyncState` combines loading, empty, error, unavailable, disconnected, and confirmation feedback to avoid redundant components.

| Name | Responsibility | Variants | Major states | Used by pages/layouts |
| --- | --- | --- | --- | --- |
| Button | Presentation, UI state and click emission; parent owns actions | primary, secondary, ghost; small/medium | default, hover, active, focus-visible, disabled, loading | All pages |
| StateLabel | Reusable semantic state label selected by `state` | pending, success, failed, cancelled, expired | Presentational only; parent owns state and behavior | PaymentStatusCard and future status displays |
| FormField | Label, input/control, help and validation message association | Text, email, password, select, textarea, checkbox, radio as required by confirmed fields | Pristine, edited, invalid, disabled, readonly | Login, Registration, Profile, Settings |
| BaseCard | Shared visual card container with header, default, and footer slots | Consumer-defined content and classes | State presentation remains consumer-owned | Features and Subscription plan presentation |
| Badge | Textual status and semantic emphasis | Neutral, success, warning, danger, information | Ready, active, pending, paused, connected, disconnected, incomplete as applicable | Landing preview, Dashboard, Training, Session Review, History, Subscription |
| Dialog | Accessible navigation/confirmation surface | Navigation drawer, confirmation | Closed, open, action pending, error | Public mobile navigation and all app pages through layouts; Training stop/leave and Profile/Settings unsaved-change confirmation when applicable |
| NavigationItem | Shared link/active/focus behavior | Public anchor, application link, compact link | Default, active, hover, focus | PublicLayout, AuthenticationLayout |
| PageHeader | Title, optional summary and relevant actions | Public section, application page | Default; actions disabled/pending through Button | Landing sections and all authenticated pages |
| AsyncState | Consistent explanation, announcement, retry/next action | Loading, empty, error, unavailable, disconnected, success/confirmation | Initial, pending, recoverable failure, completed | All pages where asynchronous data or actions apply |

### Current Button and Plan-Card Ownership

Follow [Button](shared-ui-components.md#button) and [PaymentCardPlan](feature-components.md#paymentcardplan) as the single contract source. Start Training and Save are Button labels/usages, not components. Button emits `click` with the DOM event; no callback/onAction prop, business logic, store/API access or navigation policy belongs inside it. `type` supports button/submit/reset, and disabled/loading both prevent activation. There is no existing `to`/RouterLink mode; navigation stays with the owning handler or existing link component.

Plan `frontend/src/components/buttons/Button.vue` with `frontend/src/composables/ButtonController.ts`, adapting the inspected `useButtonController` UI behavior. Reuse the existing PaymentCardPlan contract for Subscription; `selected` defaults to false and only changes presentation. BillingDetailsCard owns the separate existing billing panel, with page-handled actions. Checkout retains its distinct ChoosePlanCard summary; no display-prop consolidation with that summary is required. Prototype implementations and entries are linked from the shared and feature component specifications.

For E8, map CameraPreviewModal's external UI behavior and media ownership exactly as documented in [CameraPreviewModal](feature-components.md#camerapreviewmodal): `src/composables/useCameraPreviewModal.ts` owns modal UI/attachment/mute/feedback/closure; `useCameraSession.ts` owns tracks; `useVideoAnalysis.ts` owns capture and cancellation; `src/services/trainingTransport.ts` owns transport. These are future implementation placements, not completed code changes.

## Required Feature Components

The following legacy feature list requires revalidation against the current specification; it is not authority to add components. Data names below are conceptual requirements, not implemented API contracts.

| Name | Responsibility / used by page | Dependencies and data requirements |
| --- | --- | --- |
| PaymentCardPlan | One plan presentation for Subscription option, selected, and current-plan states | Parent-supplied selection/current-plan display; Subscription owns actions and state |
| BillingDetailsCard | Existing renewal/payment-method display for Subscription | Parent-supplied display data and page-handled action |
| PaymentStatusCard | One Checkout payment-return presentation composed from StateLabel and Button | Parent-supplied `currentState`, `paymentPlanTitle`, and `paymentPlanDescription`; emits `action` without payment logic |
| CameraPreview | Media preview, permissions and availability / Training | Browser stream or supported video source, permission/lifecycle/error state; release tracks on stop/unmount |
| SessionControls | Explicit camera, analysis, and session start/stop / Training | Camera availability, connection/analysis/session state, pending action results; distinguish stop analysis from stop camera/end session |
| TrainingOverlay | Supported visual markers / Training | Structured marker coordinates, timestamps, confidence, frame dimensions, video fitting/mirroring; suppress unsupported/stale markers |
| CoachingFeedback | One focused cue and analysis/connection status / Training | Backend coaching output, confidence, recency, connection; show waiting/unavailable states when no supported cue exists |
| SessionSummary | Duration, issues, metrics, recommendations, optional moments, completeness / Session Review | Authorized completed or partial session result, confidence and media references |
| SessionHistoryList | Sessions and review links / History, compact Dashboard | Session identifiers, summaries and dates, loading/empty/error state; paging only if supported |
| CheckoutFlow | Checkout start and success/cancel/failure/recovery states / Subscription | Backend checkout request/result, provider redirect, backend verification of final state; no card data in application code |
| ProfileEditor | View/update supported personal details / Profile | Authorized personal-information schema, validation, writable fields, save result |
| SettingsEditor | View/update supported preferences / Settings | Authorized settings schema, browser capability state, validation and save result |

Prefer provider-hosted checkout for the initial implementation; no custom payment modal is required. Use the existing Subscription route for return states if the backend/provider contract supports it. A redirect query string alone must never establish payment success.

## Required Routes

| Path | Page | Access | Layout | Parameters | Navigation visibility |
| --- | --- | --- | --- | --- | --- |
| `/` | Landing | Public | PublicLayout | None | Brand/home; Features and Training entry points |
| `/features` | Features | Public | PublicLayout | None | Public navigation |
| `/login` | Login | Public; session-aware redirect | PublicLayout | None; optional validated internal return target | Public login action; registration switch |
| `/register` | Registration | Public; session-aware redirect | PublicLayout | None | Public registration action; login switch |
| `/app` | Dashboard | Authenticated | AuthenticationLayout | None | App navigation |
| `/app/training` | Training | Authenticated | AuthenticationLayout | None | App navigation and start-training actions |
| `/app/sessions/:sessionId` | Session Review | Authenticated and server-authorized result | AuthenticationLayout | `sessionId` | History/Dashboard session links; History remains active |
| `/app/history` | History | Authenticated | AuthenticationLayout | None | App navigation |
| `/app/subscription` | Subscription | Authenticated | AuthenticationLayout | None | App navigation and plan actions |
| `/app/profile` | Profile | Authenticated | AuthenticationLayout | None | App navigation |
| `/app/settings` | Settings | Authenticated | AuthenticationLayout | None | App navigation |

Use a safe redirect to `/` for unknown routes; a separate not-found page is not required. Resolve session state before rendering protected content. Unauthenticated access redirects to login; authenticated visitors to authentication routes go to Dashboard when appropriate, or to an explicitly validated internal return destination. Browser guards improve navigation only; the server must authorize data and actions. Handle unavailable session verification distinctly from a confirmed signed-out state.

## Training State and Contract Plan

- Camera: initial/off, requesting permission, ready, denied, unavailable, ended/error. Permission is requested only following a clear user action. Starting analysis requires a usable source; do not silently claim camera access as the prototype does.
- Transport: idle, connecting, connected, disconnected, recoverable error. Stop frame sending when analysis is stopped, transport cannot accept input, or the component is disposed. Use bounded latest-frame preparation/backpressure; never grow an unbounded frame queue.
- Analysis: idle, starting, active, stopping, unavailable/error. Confirm state from the supported contract; do not label a socket connection as active analysis automatically.
- Session: idle, starting, running, ending, complete, incomplete/error. Session duration reflects real elapsed session state; review navigation requires a returned session identifier/result.
- Feedback: waiting, supported current cue, low-confidence/partial, stale, disconnected. Suppress unsupported cue/overlay data and explain the current state. Exact expiry and confidence rules must come from the agreed backend contract.
- Stop camera also halts capture/sending. End session stops processing and releases media resources. Leaving Training during a session must clearly resolve the active session and clean up resources. Do not retry session creation/end blindly without agreed idempotency behavior.
- Keep inference and coaching decisions off the browser. Capture/resize/throttle only; no LLM in the frame path. Browser rendering consumes structured backend state.

## Build Order

1. Establish only the structure defined by [Frontend Project Structure](frontend-project-structure.md). Preserve the existing placeholder and unrelated changes; create directories only when implementation requires them.
2. Implement tokens, typography, base accessibility, shared UI, and the two layouts. This is the first visual review milestone.
3. Compose Landing, Login and Registration with the proposed dedicated routes. Add the full route map and session-aware shell before linking protected flows. Represent missing services explicitly; never fake login success.
4. Compose Dashboard and Training initial/empty/unavailable states. Implement real browser camera lifecycle and control transitions. This is the first usable camera milestone, independent of live analysis availability.
5. Agree and integrate authentication/session and analysis transport contracts. Add bounded frame preparation, structured overlays/cues, stop/cleanup behavior, and real session creation/completion. Validate permission denial, disconnects, stale results, and end/leave behavior.
6. Implement Session Review and History against supported result/list contracts. Reuse compact history views on Dashboard. Keep absent or insufficient data honest.
7. Implement Profile and Settings against supported fields, including save and recovery behavior.
8. Implement Subscription plan/current-state presentation and provider-hosted CheckoutFlow with backend-verified outcomes.
9. Validate all required pages at desktop/tablet/mobile widths, including 320px mobile and intermediate sizes, portrait/landscape media, keyboard-only operation, focus/announcements, reduced motion, and no unintended overflow. Review visual consistency against the prototype.
10. Run production build, lint/static checks, and meaningful component/integration tests for route access, form validation, camera cleanup, training state transitions/backpressure, stale-data handling, and checkout return verification. Perform browser/manual checks using available services, and report unavailable integrations accurately.

Backend contracts may be prepared in parallel with UI implementation, but functional completion must wait for verified integrations. No backend application, production deployment, or infrastructure rebuild is part of this planning deliverable.

## Decisions and Outstanding Inputs

### Concrete first design decisions

- Keep the prototype's dark green/lime identity and camera-led composition.
- Use dedicated `/login` and `/register` pages by default, preserving the compact form appearance; optional user preference may select route-backed modals instead.
- Use a desktop sidebar and an accessible compact navigation menu on smaller screens; expose every documented authenticated application destination.
- Make camera start and analysis start distinct, with one trustworthy cue and explicit unavailable/low-confidence states.
- Begin implementation with shared foundation, public/authentication pages, app shell, and usable browser camera controls; retain the full documented page scope in later phases.
- Use JavaScript as expressly required by the frontend specification.

### Inputs needed for integration, not for initial design work

- Authentication/session and password policies. AGENTS.md requires Google, Apple and 2FA support at the system level, while the frontend specification only details email/password forms. Confirm their frontend entry points and challenge/callback behavior through a specification update before claiming complete authentication coverage; do not fabricate provider actions.
- Analysis/session transport schemas, accepted frame format/rate/size, timestamps, confidence/expiry rules, coordinate system, reconnection and session completion semantics.
- Session/history result schemas and optional analyzed-moment media access.
- Supported profile/settings fields and privacy/data-handling behavior.
- Real plan definitions, entitlements, price/free-trial claims, checkout contracts, and backend-confirmed return states.
- Final privacy/terms/support destinations; do not create dead links or invent policy content.

The only immediate optional user choice is authentication presentation. The default permits continued design/foundation work if no preference is provided. No approval is required by the planning skill; its scope ends at this complete implementation plan.

## Planning Validation

- All required pages and routes, both layouts, and the documented feature areas are represented using the canonical [Frontend Project Structure](frontend-project-structure.md).
- All specified feature components are accounted for, without inventing a payment modal or extra feature component families.
- Shared patterns have multiple consumers; loading/error/confirmation patterns share one component family.
- Prototype palette, typography, hierarchy, media prominence, form styling and subscription-plan composition are represented; omissions and simulated data are explicitly corrected by specification requirements.
- Frontend/backend responsibilities, route authorization limits, sensitive-payment boundary, accessibility, responsive behavior and realtime lifecycle constraints are recorded.
- Dependency order and unresolved backend/product inputs are explicit. Build/runtime tests are not applicable to this documentation-only deliverable and have not been claimed as passing.
