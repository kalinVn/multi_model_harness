## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/frontend.md
- docs/frontend/shared-ui-components.md
- docs/frontend/feature-components.md
- docs/frontend/components.md
- docs/frontend/pages-and-routes.md
- docs/frontend/layouts.md
- docs/frontend/integration-contracts.md
- docs/frontend/frontend-project-structure.md

# Frontend Implementation Plan

## 1. Frontend Type

`new`. Production `frontend/` contains no established Vue application beyond placeholder/index evidence; prototypes are reference material, not production code.

## 2. Planning Sources

- Root authority: `docs/frontend/frontend.md`.
- Component authorities: `docs/frontend/shared-ui-components.md` and `docs/frontend/feature-components.md`; `docs/frontend/components.md` is only a compatibility index.
- Pages/routes/layouts: `docs/frontend/pages-and-routes.md` and `docs/frontend/layouts.md`.
- Integration proposals: `docs/frontend/integration-contracts.md`; implement against clearly labeled fixtures until backend confirmation/adaptation, and never claim fixture behavior is live.
- Placement: `docs/frontend/frontend-project-structure.md`, the sole structure authority selected by the root specification.
- Shared design constraints: `claude/rules/frontend/frontend-design-system.md`, applied below project specifications and referenced prototypes according to its documented precedence.
- Visual/organization evidence: only exact prototypes declared by the owning specifications, including the shared application background in `prototypes/design/background.html`. Specifications override prototypes; shared design rules are lower-priority defaults.

## 3. Shared UI Components

### 1. Button

- Component name: `Button`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#button`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/buttons/Button.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## Button

Name: Button

Description: Button = presentation + UI state + event emission. This is the authoritative project Button contract. Start Training, Save, Reset, and similar labels are usages of this shared component, never separate reusable button components.

### Props and States

| Prop | Supported values / type | Default |
| --- | --- | --- |
| `variant` | `primary`, `secondary`, `ghost` | `primary` |
| `size` | `small`, `medium` | `medium` |
| `type` | `button`, `submit`, `reset` | `button` |
| `disabled` | Boolean | `false` |
| `loading` | Boolean | `false` |

Supported UI states are default, hover, active, focus-visible, disabled, and loading. Loading displays the existing spinner and sets `aria-busy`; either `disabled` or `loading` disables activation. Content comes from the default slot, including text and optional icons. Native attributes such as accessible names and pressed/expanded state remain supported.

`primary` uses the accent fill; `secondary` uses the panel fill; `ghost` uses a transparent background with the shared border and interaction styles. Ghost is already implemented in the shared stylesheet and required by the Profile, Settings and CollapseForm reset-action designs. Existing styled links may also use ghost CSS; that does not imply a Button navigation prop. No subtle or destructive variants are defined. The existing implementation supports small/medium only, not a large size.

### Emits and Ownership

Emits:

- `click` — forwards the original DOM event when activation is enabled.

The component has no business logic, callback props (`callback`, `onAction`, or similar), store/API access, or page-specific actions. The parent handles `click`; action logic belongs to the page, owning feature, composable, or appropriate store/service. Form submission/reset remains owned by the parent form.

```vue
<Button @click="startTraining">
  Start Training
</Button>
```

The existing [ButtonController.js](../../../prototypes/composables/ButtonController.js) exports `useButtonController`: it derives `isDisabled` from disabled/loading, suppresses disabled clicks, and emits enabled clicks. This is UI behavior, not an action dispatcher. Planned production placement is `frontend/src/components/buttons/Button.vue` plus `frontend/src/composables/ButtonController.ts`, preserving that separation in TypeScript. These planned files are not claimed to exist.


The inspected Button renders a native button and does not support a `to` prop or `RouterLink` mode. Preserve the existing parent-owned navigation convention: an action may invoke the owning page/feature handler, while link destinations use the existing link/navigation components. Do not implement separate navigation logic in page-specific button components or document an unsupported `to` API. Navigation destinations and access policy stay outside Button.

### Prototype References

#### Design Prototypes

- [button primary default](../../../prototypes/design/components/buttons/specimens/button-primary-default.html)
- [button primary hover](../../../prototypes/design/components/buttons/specimens/button-primary-hover.html)
- [button primary pressed](../../../prototypes/design/components/buttons/specimens/button-primary-pressed.html)
- [button primary focus visible](../../../prototypes/design/components/buttons/specimens/button-primary-focus-visible.html)
- [button primary disabled](../../../prototypes/design/components/buttons/specimens/button-primary-disabled.html)
- [button primary loading](../../../prototypes/design/components/buttons/specimens/button-primary-loading.html)
- [button secondary default](../../../prototypes/design/components/buttons/specimens/button-secondary-default.html)
- [button secondary hover](../../../prototypes/design/components/buttons/specimens/button-secondary-hover.html)
- [button secondary pressed](../../../prototypes/design/components/buttons/specimens/button-secondary-pressed.html)
- [button secondary focus visible](../../../prototypes/design/components/buttons/specimens/button-secondary-focus-visible.html)
- [button secondary disabled](../../../prototypes/design/components/buttons/specimens/button-secondary-disabled.html)
- [button secondary loading](../../../prototypes/design/components/buttons/specimens/button-secondary-loading.html)
- [button ghost default](../../../prototypes/design/components/buttons/specimens/button-ghost-default.html)
- [button ghost hover](../../../prototypes/design/components/buttons/specimens/button-ghost-hover.html)
- [button ghost pressed](../../../prototypes/design/components/buttons/specimens/button-ghost-pressed.html)
- [button ghost focus visible](../../../prototypes/design/components/buttons/specimens/button-ghost-focus-visible.html)
- [button ghost disabled](../../../prototypes/design/components/buttons/specimens/button-ghost-disabled.html)
- [button ghost loading](../../../prototypes/design/components/buttons/specimens/button-ghost-loading.html)
- [button size small](../../../prototypes/design/components/buttons/specimens/button-size-small.html)
- [button size medium](../../../prototypes/design/components/buttons/specimens/button-size-medium.html)
- [button type button](../../../prototypes/design/components/buttons/specimens/button-type-button.html)
- [button type submit](../../../prototypes/design/components/buttons/specimens/button-type-submit.html)
- [button type reset](../../../prototypes/design/components/buttons/specimens/button-type-reset.html)

#### Vue Components

- [Button.vue](../../../prototypes/design/components/buttons/Button.vue)

</details>

### 2. TextButton

- Component name: `TextButton`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#textbutton`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/buttons/TextButton.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## TextButton

Name: TextButton

Description: TextButton is the shared lightweight action control for places where a filled primary, secondary, or ghost Button would add too much visual weight. Cookie Policy, Privacy Policy, Cookie Settings, and Manage Preferences are representative usages, not component-owned behavior. It renders a native `button` and contains no navigation, persistence, modal, cookie, or other feature logic.

### Props and States

| Prop | Supported values / type | Default |
| --- | --- | --- |
| `type` | `button`, `submit`, `reset` | `button` |
| `disabled` | Boolean | `false` |
| `tone` | `accent`, `inherit` | `accent` |

Content comes from the default slot. `accent` uses the shared accent color; `inherit` adopts the surrounding text color for visually integrated footer, sidebar, or inline actions. Native attributes, including `aria-label`, `aria-describedby`, `aria-expanded`, and `aria-controls`, fall through to the native button. Parent-supplied `class` and `style` are valid extension points for local layout only; consumers must not replace the component's interaction states or turn it into a feature-specific variant.

Supported states are default, hover, active, focus-visible, and disabled. The component intentionally has no loading state, icon API, size system, routing mode, or feature-specific variants.

### Emits and Ownership

Emits:

- `click` — forwards the original DOM event for enabled activation.

The parent handles the action. Native button semantics provide Enter/Space keyboard activation, and a disabled button is not focusable or activatable. Focus-visible uses the shared cyan outline and does not rely on color alone.

```vue
<TextButton aria-haspopup="dialog" @click="openPreferences">
  Manage Preferences
</TextButton>
```

### Prototype References

#### Design Prototypes

- [text button accent default](../../../prototypes/design/components/buttons/specimens/text-button-accent-default.html)
- [text button accent hover](../../../prototypes/design/components/buttons/specimens/text-button-accent-hover.html)
- [text button accent pressed](../../../prototypes/design/components/buttons/specimens/text-button-accent-pressed.html)
- [text button accent focus visible](../../../prototypes/design/components/buttons/specimens/text-button-accent-focus-visible.html)
- [text button accent disabled](../../../prototypes/design/components/buttons/specimens/text-button-accent-disabled.html)
- [text button inherit default](../../../prototypes/design/components/buttons/specimens/text-button-inherit-default.html)
- [text button inherit hover](../../../prototypes/design/components/buttons/specimens/text-button-inherit-hover.html)
- [text button inherit pressed](../../../prototypes/design/components/buttons/specimens/text-button-inherit-pressed.html)
- [text button inherit focus visible](../../../prototypes/design/components/buttons/specimens/text-button-inherit-focus-visible.html)
- [text button inherit disabled](../../../prototypes/design/components/buttons/specimens/text-button-inherit-disabled.html)

#### Vue Components

- [TextButton.vue](../../../prototypes/design/components/buttons/TextButton.vue)

</details>

### 3. BaseCard

- Component name: `BaseCard`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#basecard`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/cards/BaseCard.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## BaseCard

Name: BaseCard

Description: BaseCard is the shared visual container for card surfaces. It provides only the common border, background, radius, spacing, typography context, and overflow behavior; all semantic content and consumer-owned presentation come from its parent through slots.

### Component Properties and Data Flow

BaseCard has no props, emitted events, application state, or domain logic. Native attributes and consumer classes fall through to its root `<article>`, allowing the parent to provide an accessible label and its own layout or state styling without adding those concepts to BaseCard.

Slots:

- `header`: optional leading content such as a feature number, status, or heading group.
- default: the main card content.
- `footer`: optional trailing content such as parent-owned actions.

Features supplies its number, title, and description through these slots. `PaymentCardPlan` supplies its plan name, price, selected-state indicator, description, and buttons through the same slots. None of those fields or states is a BaseCard prop.

### Prototype References

#### Design Prototypes

- [base-card.html](../../../prototypes/design/components/cards/base-card.html)

#### Vue Components

- [BaseCard.vue](../../../prototypes/components/cards/BaseCard.vue)

---

</details>

### 4. StateLabel

- Component name: `StateLabel`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#statelabel`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/labels/StateLabel.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## StateLabel

Name: StateLabel

Description: StateLabel is a reusable presentational label for displaying semantic UI states.

### Component Functionality

The component receives a state and renders the corresponding label with the existing restrained pill treatment, typography, and semantic colors. Its built-in labels are generic; a parent may provide context-specific text through the default slot while retaining the visual treatment selected by `state`.

### Component Properties and Data Flow

| Prop | Type / supported values | Requirement |
| --- | --- | --- |
| `state` | `pending`, `success`, `failed`, `cancelled`, `expired` | Required; selects the semantic label and visual treatment. |

The optional default slot overrides only the visible text. The parent owns the actual state and all resulting behavior. StateLabel performs no request, verification, persistence, redirect, subscription mutation, or other business logic.

### Prototype References

#### Design Prototypes

- [state-label.html](../../../prototypes/design/components/labels/state-label.html)

#### Vue Components

- [StateLabel.vue](../../../prototypes/components/labels/StateLabel.vue)

---

</details>

### 5. TextField

- Component name: `TextField`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#textfield`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/fields/TextField.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## TextField

Name: TextField

Description: Single-line text input. Use it for names and other short free-text values.

`useTextField` composes the shared `useField` composable and adds text-clearing behavior.

### Prototype References

#### Design Prototypes

- [text-field.html](../../../prototypes/design/components/fields/text-field.html)
- [text-field-states.html](../../../prototypes/design/components/fields/text-field-states.html)

#### Vue Components

- [TextField.vue](../../../prototypes/components/fields/TextField.vue)

</details>

### 6. NumberField

- Component name: `NumberField`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#numberfield`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/fields/NumberField.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## NumberField

Name: NumberField

Description: Numeric input that converts entered values to numbers and represents an empty field as `null`. Use it for quantities or other numeric values.

`useNumberField` composes the shared `useField` composable and adds numeric conversion and unit increment/decrement behavior.

### Prototype References

#### Design Prototypes

- [number-field.html](../../../prototypes/design/components/fields/number-field.html)
- [number-field-states.html](../../../prototypes/design/components/fields/number-field-states.html)

#### Vue Components

- [NumberField.vue](../../../prototypes/components/fields/NumberField.vue)

</details>

### 7. SelectField

- Component name: `SelectField`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#selectfield`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/fields/SelectField.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## SelectField

Name: SelectField

Description: Native selection from supplied options, supporting single or multiple values. Use it when users choose from a predefined set of options.

`useSelectField` composes the shared `useField` composable and adds option selection and selected-option lookup.

### Prototype References

#### Design Prototypes

- [select-field.html](../../../prototypes/design/components/fields/select-field.html)
- [select-field-states.html](../../../prototypes/design/components/fields/select-field-states.html)

#### Vue Components

- [SelectField.vue](../../../prototypes/components/fields/SelectField.vue)

</details>

### 8. DateField

- Component name: `DateField`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#datefield`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/fields/DateField.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## DateField

Name: DateField

Description: Native date input using `YYYY-MM-DD` strings without timezone conversion. Use it for calendar dates that do not require a time of day.

`useDateField` composes the shared `useField` composable and adds date assignment and clearing behavior.

### Prototype References

#### Design Prototypes

- [date-field.html](../../../prototypes/design/components/fields/date-field.html)
- [date-field-states.html](../../../prototypes/design/components/fields/date-field-states.html)

#### Vue Components

- [DateField.vue](../../../prototypes/components/fields/DateField.vue)

</details>

### 9. Badge

- Component name: `Badge`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#badge`
- Description: Shared non-interactive text label for compact statuses and semantic emphasis.
- Component functionality: Renders parent-supplied slot text using the prototype-backed `success` or `neutral` pill treatment.
- Props and defaults: `variant`: `success` or `neutral`; default `success`.
- UI states: `success` is used for Reviewed; `neutral` is used for Sample and Incomplete.
- Data flow: The parent supplies the text and variant. Badge does not infer status semantics.
- Emits and ownership: None. The parent owns status values and behavior.
- Slots and content: Required default slot for visible status text.
- Behavior and accessibility: Non-interactive text; visible text remains the accessible status and color is supplementary.
- Visual requirements: Match the declared Badge, History, and BaseTable design prototypes.
- Prototype References:
  - Design Prototypes: `prototypes/design/components/labels/badge.html`, `prototypes/design/pages/history.html`, `prototypes/design/components/tables/BaseTable.html`
  - Vue Components: None
  - Other declared references: None
- Dependencies: None
- File grouping and placement: `frontend/src/components/labels/Badge.vue`
- Blockers: None

### 10. FormStatusMessage

- Component name: `FormStatusMessage`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#formstatusmessage`
- Description: Shared, centered form-level status above the first field; the parent supplies workflow text and state.
- Component functionality: Renders nothing for an empty message; otherwise shows the documented pending, error, or success treatment and decorative icon.
- Props and defaults: Required `state` (`pending`, `error`, `success`); `message` is an empty string by default.
- UI states: Pending uses polite status and `aria-busy`; error uses assertive alert; success uses polite status. Reduced-motion preference applies to pending animation.
- Data flow: The owning form passes state and message. No store, API, or persistence access.
- Emits and ownership: None. Retry, form validation, authentication, and navigation remain with the parent.
- Slots and content: None; content is the parent-supplied `message`.
- Behavior and accessibility: Suppress the entire element when the message is empty. Icons are decorative; text conveys the full state.
- Visual requirements: Match the three declared state specimens.
- Prototype References:
  - Design Prototypes: `prototypes/design/components/form-status-message/form-status-message-pending.html`, `prototypes/design/components/form-status-message/form-status-message-error.html`, `prototypes/design/components/form-status-message/form-status-message-success.html`
  - Vue Components: `prototypes/components/messages/FormStatusMessage.vue`
  - Other declared references: None
- Dependencies: None
- File grouping and placement: `frontend/src/components/messages/FormStatusMessage.vue`
- Blockers: None

### 11. LayoutHeader

- Component name: `LayoutHeader`
- Source specification: `docs/frontend/shared-ui-components.md`
- Source section: `docs/frontend/shared-ui-components.md#layoutheader`
- Description: Shared authenticated-layout header showing the active page and user and exposing logout.
- Component functionality: Renders `Tennis AI Coach / {pageTitle}`, `userName`, and a shared `Button` labeled `Log out`; shows the `demo user` descriptor only when explicitly requested by a debug or prototype consumer.
- Props and defaults: Required string `pageTitle` and required string `userName`.
- UI states: Responsive desktop/mobile presentation; no component-owned application state.
- Data flow: Authentication Layout supplies the page title and user name.
- Emits and ownership: Emits `logout`; the Authentication Layout owns routing and the authentication flow. No store, API, token, or session access in the component.
- Slots and content: None.
- Behavior and accessibility: Keyboard-accessible logout control and responsive presentation.
- Visual requirements: Match the header and authentication-layout design references.
- Prototype References:
  - Design Prototypes: `prototypes/design/components/header.html`, `prototypes/design/layouts/authentication.html`
  - Vue Components: None
  - Other declared references: None
- Dependencies: `Button`
- File grouping and placement: `frontend/src/components/layout/LayoutHeader.vue`
- Blockers: None

`Field` is the documented shared foundation and composable contract, not an additional visual component. Its `useField` relationship and exact references are preserved inside each field entry's source contract.

## 4. Feature Components

### 1. BaseModal

- Component name: `BaseModal`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#basemodal`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/modal/BaseModal.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [modals.html](../../../prototypes/design/components/modals.html)

#### Vue Components

- [BaseModal.vue](../../../prototypes/components/modal/BaseModal.vue)

---

</details>

### 2. TopNav

- Component name: `TopNav`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#topnav`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/navigation/TopNav.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [public-navigation.html](../../../prototypes/design/components/navigation/public-navigation.html)

#### Vue Components

- [TopNav.vue](../../../prototypes/components/navs/TopNav.vue)
- [Button.vue](../../../prototypes/design/components/buttons/Button.vue)

---

</details>

### 3. SidebarNav

- Component name: `SidebarNav`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#sidebarnav`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/navigation/SidebarNav.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [authenticated-navigation.html](../../../prototypes/design/components/navigation/authenticated-navigation.html)

#### Vue Components

- [SidebarNav.vue](../../../prototypes/components/navs/SidebarNav.vue)

---

</details>

### 4. BaseTable

- Component name: `BaseTable`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#basetable`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/tables/BaseTable.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [BaseTable.html](../../../prototypes/design/components/tables/BaseTable.html)
- [BaseTable-review.html](../../../prototypes/design/components/tables/BaseTable-review.html)

#### Vue Components

- [BaseTable.vue](../../../prototypes/components/tables/BaseTable.vue)

---

</details>

### 5. CollapseForm

- Component name: `CollapseForm`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#collapseform`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/forms/CollapseForm.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [CollapseForm.html](../../../prototypes/design/components/forms/CollapseForm.html)

#### Vue Components

- [CollapseForm.vue](../../../prototypes/components/forms/CollapseForm.vue)

---

</details>

### 6. PaymentCardPlan

- Component name: `PaymentCardPlan`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#paymentcardplan`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/subscription/PaymentCardPlan.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [payment-card-plan.html](../../../prototypes/design/components/cards/payment-card-plan.html)
- [payment-card-plan-selected.html](../../../prototypes/design/components/cards/payment-card-plan-selected.html)
- [payment-card-plan-current.html](../../../prototypes/design/components/cards/payment-card-plan-current.html)

#### Vue Components

- [PaymentCardPlan.vue](../../../prototypes/components/features/subscription/PaymentCardPlan.vue)
- [Subscription.vue](../../../prototypes/components/features/subscription/Subscription.vue)

#### Composables

- [useSubscription.js](../../../prototypes/components/features/subscription/useSubscription.js)

---

</details>

### 7. BillingDetailsCard

- Component name: `BillingDetailsCard`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#billingdetailscard`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/subscription/BillingDetailsCard.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [billing-details-card.html](../../../prototypes/design/components/cards/billing-details-card.html)

#### Vue Components

- [BillingDetailsCard.vue](../../../prototypes/components/features/subscription/BillingDetailsCard.vue)

---

</details>

### 8. HomePageInfoSection

- Component name: `HomePageInfoSection`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#homepageinfosection`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/home/HomePageInfoSection.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [home-page-info-section.html](../../../prototypes/design/components/sections/home-page-info-section.html)

#### Vue Components

- [HomePageInfoSection.vue](../../../prototypes/components/sections/HomePageInfoSection.vue)

#### Adapters

- [Home entry](../../../prototypes/home/main.js)

---

</details>

### 9. HomePageVideoSlider

- Component name: `HomePageVideoSlider`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#homepagevideoslider`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/home/home-page-video-slider/`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [slider.css](../../../prototypes/components/sliders/home-page-video-slider/slider.css)

#### Vue Components

- [HomePageVideoSlider.vue](../../../prototypes/components/sliders/home-page-video-slider/HomePageVideoSlider.vue)

#### Helpers

- [SliderLifecycle.js](../../../prototypes/components/sliders/home-page-video-slider/SliderLifecycle.js)
- [SliderConfig.js](../../../prototypes/components/sliders/home-page-video-slider/SliderConfig.js)
- [PixiRenderer.js](../../../prototypes/components/sliders/home-page-video-slider/PixiRenderer.js)

#### Controllers

- [SliderController.js](../../../prototypes/components/sliders/home-page-video-slider/SliderController.js)
- [VideoTimelineController.js](../../../prototypes/components/sliders/home-page-video-slider/VideoTimelineController.js)
- [AudioTimeline.js](../../../prototypes/components/sliders/home-page-video-slider/AudioTimeline.js)
- [PlayerAnalysisTimeline.js](../../../prototypes/components/sliders/home-page-video-slider/PlayerAnalysisTimeline.js)
- [AnimationTimeline.js](../../../prototypes/components/sliders/home-page-video-slider/AnimationTimeline.js)
- [AIMotionTrackingPanel.js](../../../prototypes/components/sliders/home-page-video-slider/AIMotionTrackingPanel.js)

</details>

### 10. RecaptchaField

- Component name: `RecaptchaField`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#recaptchafield`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/auth/RecaptchaField.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [recaptcha-field.html](../../../prototypes/design/components/fields/recaptcha-field.html)

#### Vue Components

- [RecaptchaField.vue](../../../prototypes/components/fields/RecaptchaField.vue)

---

</details>

### 11. SocialAuthButton

- Component name: `SocialAuthButton`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#socialauthbutton`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/auth/SocialAuthButton.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [Continue with Google — default](../../../prototypes/design/components/buttons/specimens/social-auth-google-default.html)
- [Continue with Google — hover](../../../prototypes/design/components/buttons/specimens/social-auth-google-hover.html)
- [Continue with Google — pressed](../../../prototypes/design/components/buttons/specimens/social-auth-google-pressed.html)
- [Continue with Google — focus-visible](../../../prototypes/design/components/buttons/specimens/social-auth-google-focus-visible.html)
- [Continue with Google — disabled](../../../prototypes/design/components/buttons/specimens/social-auth-google-disabled.html)
- [Connecting to Google — loading](../../../prototypes/design/components/buttons/specimens/social-auth-google-loading.html)
- [Continue with Facebook — default](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-default.html)
- [Continue with Facebook — hover](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-hover.html)
- [Continue with Facebook — pressed](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-pressed.html)
- [Continue with Facebook — focus-visible](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-focus-visible.html)
- [Continue with Facebook — disabled](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-disabled.html)
- [Connecting to Facebook — loading](../../../prototypes/design/components/buttons/specimens/social-auth-facebook-loading.html)
- [Continue with Apple — default](../../../prototypes/design/components/buttons/specimens/social-auth-apple-default.html)
- [Continue with Apple — hover](../../../prototypes/design/components/buttons/specimens/social-auth-apple-hover.html)
- [Continue with Apple — pressed](../../../prototypes/design/components/buttons/specimens/social-auth-apple-pressed.html)
- [Continue with Apple — focus-visible](../../../prototypes/design/components/buttons/specimens/social-auth-apple-focus-visible.html)
- [Continue with Apple — disabled](../../../prototypes/design/components/buttons/specimens/social-auth-apple-disabled.html)
- [Connecting to Apple — loading](../../../prototypes/design/components/buttons/specimens/social-auth-apple-loading.html)

#### Vue Components

- [SocialAuthButton.vue](../../../prototypes/components/forms/SocialAuthButton.vue)

---

</details>

### 12. LoginForm

- Component name: `LoginForm`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#loginform`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/auth/LoginForm.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [LoginForm.vue](../../../prototypes/components/forms/LoginForm.vue)

#### Helpers

- [authValidators.js](../../../prototypes/utils/validators/authValidators.js)


---

</details>

### 13. ConfirmLoginForm

- Component name: `ConfirmLoginForm`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#confirmloginform`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/auth/ConfirmLoginForm.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [confirm-login-form.html](../../../prototypes/design/components/forms/confirm-login-form.html)

#### Vue Components

- [ConfirmLoginForm.vue](../../../prototypes/components/forms/ConfirmLoginForm.vue)

---

</details>

### 14. RegisterForm

- Component name: `RegisterForm`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#registerform`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/auth/RegisterForm.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## RegisterForm

Name: RegisterForm

Description: RegisterForm is the dedicated account-registration form.

### Component Functionality

RegisterForm renders the shared FormStatusMessage immediately above its first field, followed by first name, surname, email, optional phone, password, confirm-password, and required Terms of Service acceptance, RecaptchaField, the primary Register action, Login navigation, and SocialAuthButtons for Google, Facebook, and Apple. There is no separate Privacy Policy checkbox; the optional backend acknowledgment value defaults to false.

Follow the [Register design prototype](../../../prototypes/design/pages/register.html) for the form's visual structure: the `Start free` eyebrow, `Create Account` title, `Create your Tennis AI Coach profile.` introduction, a two-column field grid on wider screens that becomes one column on narrow screens, the prototype's field labels and placeholders, the full-width primary action, the social-action divider and buttons, and the `Already have an account? Login` link after the social buttons. Match the prototype's card width, spacing, typography, colors, and control styling. Do not replace this structure with an undifferentiated one-column stack on desktop or move the Login link above the social buttons. The documented Terms of Service requirement remains authoritative.

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

- [register.html](../../../prototypes/design/pages/register.html)

#### Vue Components

- [RegisterForm.vue](../../../prototypes/components/forms/RegisterForm.vue)

#### Helpers

- [authValidators.js](../../../prototypes/utils/validators/authValidators.js)

---

</details>

### 15. PrivacyChoicesBanner

- Component name: `PrivacyChoicesBanner`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#privacychoicesbanner`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/cookie-privacy/PrivacyChoicesBanner.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [cookie-privacy-and-policy-banner.html](../../../prototypes/design/components/feature-components/cookie-privacy-and-policy-banner.html)

#### Vue Components

- [PrivacyChoicesBanner.vue](../../../prototypes/components/features/CookiePrivacyPolicy/PrivacyChoicesBanner.vue)

---

</details>

### 16. CookiePrivacyPolicy

- Component name: `CookiePrivacyPolicy`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#cookieprivacypolicy`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/cookie-privacy/CookiePrivacyPolicy.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [cookie-privacy-and-policy-modal.html](../../../prototypes/design/components/feature-components/cookie-privacy-and-policy-modal.html)

#### Vue Components

- [CookiePrivacyPolicy.vue](../../../prototypes/components/features/CookiePrivacyPolicy/CookiePrivacyPolicy.vue)

---

</details>

### 17. OrderSummaryCard

- Component name: `OrderSummaryCard`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#ordersummarycard`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/checkout/OrderSummaryCard.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [order-summary-card.html](../../../prototypes/design/components/cards/order-summary-card.html)

#### Vue Components

- [OrderSummaryCard.vue](../../../prototypes/components/features/checkout/OrderSummaryCard.vue)

---

</details>

### 18. PaymentStatusCard

- Component name: `PaymentStatusCard`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#paymentstatuscard`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/checkout/PaymentStatusCard.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [payment-status-card-states.html](../../../prototypes/design/components/cards/payment-status-card-states.html)

#### Vue Components

- [PaymentStatusCard.vue](../../../prototypes/components/features/checkout/PaymentStatusCard.vue)
- [StateLabel.vue](../../../prototypes/components/labels/StateLabel.vue)

---

</details>

### 19. Checkout

- Component name: `Checkout`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#checkout`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/checkout/`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

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

- [checkout.html](../../../prototypes/design/components/checkout/checkout.html)

#### Vue Components

- [Checkout.vue](../../../prototypes/components/features/checkout/Checkout.vue)

#### Composables

- [useCheckout.js](../../../prototypes/components/features/checkout/useCheckout.js)
- [useCheckoutStore.js](../../../prototypes/stores/useCheckoutStore.js)

#### Services

- [demoCheckoutService.js](../../../prototypes/services/demoCheckoutService.js)

#### Adapters

- [Checkout entry](../../../prototypes/design/components/checkout/main.js)

---

</details>

### 20. CameraPreviewModal

- Component name: `CameraPreviewModal`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#camerapreviewmodal`
- Complete documented contract: The exact source section below is part of this entry and supplies the description, functionality, concrete props/defaults, states, local state, data flow, events/slots, ownership, accessibility/visual requirements, dependencies, and exact declared reference paths. Values not defined there are `None`; no additional API is inferred.
- File grouping and placement: `frontend/src/components/training/CameraPreviewModal.vue`; colocate only supporting files explicitly owned by the source contract and place reusable/store/service resources in their approved top-level directories.
- Blockers: None.

<details>
<summary>Exact authoritative contract</summary>

## CameraPreviewModal

Name: CameraPreviewModal

Description: CameraPreviewModal is the single Training camera feature component.

The [Training page requirements](../pages-and-routes.md#training) own session creation, reconnection, frame-preparation policy, feedback/audio sequencing, and completion or abandonment. This section describes only the component's UI, inputs and outputs, and resource ownership.

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

- [camera.html](../../../prototypes/design/pages/camera.html)

#### Vue Components

- [CameraPreviewModal.vue](../../../prototypes/components/modal/CameraPreviewModal.vue)

#### Composables

- [useCameraSession.js](../../../prototypes/composables/useCameraSession.js)
- [useVideoAnalysis.js](../../../prototypes/composables/useVideoAnalysis.js)

#### Services

- [trainingTransport.js](../../../prototypes/services/trainingTransport.js)

---

</details>

### 21. Footer

- Component name: `Footer`
- Source specification: `docs/frontend/feature-components.md`
- Source section: `docs/frontend/feature-components.md#footer`
- Description: Reusable footer supplied by Public Layout and Authentication Layout.
- Component functionality: Renders parent-supplied copyright text and ordered legal/support actions. Items with `href` are links; items with `action` use shared `TextButton` and emit the action identifier.
- Component properties and data flow:
  - Props, events, and slots: Required `copyrightText`; required `items` array of `{ label, href?, action? }`; emits `action`; no slots specified.
  - Local UI state: None.
  - Data source and ownership: The owning layout supplies the text and items and handles actions.
  - Parent and child data flow: Layout → Footer props → link or TextButton → Footer `action` event → layout/application consent feature.
- UI states and behavior: Compact responsive footer; no component-owned navigation, consent, policy, support, store, or API behavior.
- Visual and accessibility requirements: Match the dedicated footer prototype; use semantic links/buttons and keyboard-accessible actions.
- Prototype References:
  - Design Prototypes: `prototypes/design/components/footer/footer.html`
  - Vue Components: None
  - Other declared references: None
- Dependencies and composed components: `TextButton`; Public Layout and Authentication Layout consume Footer.
- File grouping and placement: `frontend/src/components/layout/Footer.vue`
- Blockers: None

Child-only `SocialAuthButtons`, `CookiePreferencesContent`, `PolicyContent`, and `ChoosePlanCard` remain inside their documented owners and receive no unsupported standalone plan entry.

## 5. Layouts

### Public Layout

- Source: `docs/frontend/layouts.md#public-layout`.
- Pages using layout: Home, Features, Login, Register, Not Found.
- Navigation and shell: TopNav, page-content slot, and Footer; dedicated public-navigation prototype overrides embedded older examples; footer legal actions open the global consent feature.
- Design / prototype references: `prototypes/design/layouts/public.html`; `prototypes/design/components/navigation/public-navigation.html`; `prototypes/design/components/footer/footer.html`.
- Blockers: None.

### Authentication Layout

- Source: `docs/frontend/layouts.md#authentication-layout`.
- Pages using layout: Training, Dashboard, History, Session Review, Subscription, Profile, Settings, Checkout.
- Navigation and shell: SidebarNav, LayoutHeader, page-content slot, and Footer; LayoutHeader remains at the top and Footer at the bottom of the main layout column. The dedicated authenticated-navigation prototype overrides embedded examples; server retains authorization.
- Design / prototype references: `prototypes/design/layouts/authentication.html`; `prototypes/design/components/navigation/authenticated-navigation.html`; `prototypes/design/components/header.html`; `prototypes/design/components/footer/footer.html`.
- Blockers: None.

Global consent placement: `frontend/src/App.vue` mounts PrivacyChoicesBanner and CookiePrivacyPolicy once above both layouts. They are independent consumers of one shared feature-local useCookieConsent state.

## 6. Pages and Routes

### 1. Home Page

- Page: Home Page
- Source: `docs/frontend/pages-and-routes.md#home-page`
- Purpose: `Main public entry page of the application`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/`
- Route name: `home`
- Access: Public
- Route parameters: None
- Layout: Public Layout
- Navigation behavior: After confirmed authentication and UserStore initialization, use client-side router navigation to `/history` without a full-page reload; visibility never replaces server authorization.
- Required shared components: `Button`
- Required feature components: `HomePageInfoSection`, `HomePageVideoSlider`
- Design prototype references: `prototypes/design/pages/index.html`
- Data source and ownership: Page owns CTA navigation and composition; no remote data.
- Services: None
- Integration contracts and page responsibility: None; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: None
- Production placement: `frontend/src/pages/HomePage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Home Page
- purpose: `Main public entry page of the application`
- route: `/`
- layout: `Public Layout`
- Example Prototype: `design/pages/index.html`
- name: `home`
- description: `Left Section: application branding and introductory information, main headline, short introductory description, two primary action buttons, small statistic or information cards. Right Section: Animated Banner, animated visual preview of the Tennis AI Coach training and AI analysis experience.HomePageInfoSection renders the left section directly from the Home Page prototype, with CTA actions using shared Button and parent-owned handlers; do not introduce additional static-section or page-specific button components.`
- required shared components: `Button`
- required feature components: `HomePageInfoSection`, `HomePageVideoSlider`
- dependencies: None

</details>

### 2. Features

- Page: Features
- Source: `docs/frontend/pages-and-routes.md#features`
- Purpose: `Public page that presents the core capabilities of the product and helps users understand what it can do.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/features`
- Route name: `feature`
- Access: Public
- Route parameters: None
- Layout: Public Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: `Button`, `BaseCard`
- Required feature components: None
- Design prototype references: `prototypes/design/pages/features.html`
- Data source and ownership: Page owns card contents and CTA actions.
- Services: None
- Integration contracts and page responsibility: None; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: None
- Production placement: `frontend/src/pages/FeaturesPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Features
- purpose: `Public page that presents the core capabilities of the product and helps users understand what it can do.`
- route: `/features`
- layout: `Public Layout`
- Example Prototype: `design/pages/features.html`
- name: `feature`
- description: `Main Section: headline, short description, three numbered feature cards, and two primary buttons. The Features page should follow the Public Layout and match the prototype directly for the page title, secondary description, and all other page-level content; each card supplies its number, title, and description through the shared BaseCard slots.`
- required shared components: `Button`, `BaseCard`
- dependencies: None

</details>

### 3. Login Page

- Page: Login Page
- Source: `docs/frontend/pages-and-routes.md#login-page`
- Purpose: `Allow an existing user to enter email and password or choose a supported social login entry point.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/login`
- Route name: `login`
- Access: Public
- Route parameters: None
- Layout: Public Layout
- Navigation behavior: After confirmed authentication and UserStore initialization, use client-side router navigation to `/history` without a full-page reload; visibility never replaces server authorization.
- Required shared components: None
- Required feature components: `LoginForm`, `ConfirmLoginForm`
- Design prototype references: `prototypes/design/pages/login.html`
- Data source and ownership: Form/page own local fields; AuthStore owns auth workflow; UserStore owns the confirmed authenticated application snapshot consumed by History.
- Services: auth service
- Integration contracts and page responsibility: Authentication and application session; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `AuthStore`, `UserStore`
- Production placement: `frontend/src/pages/LoginPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Login Page
- purpose: `Allow an existing user to enter email and password or choose a supported social login entry point.`
- route: `/login`
- layout: `Public Layout`
- Example Prototype: `design/pages/login.html`
- name: `login`
- description: `Dedicated public authentication page. Render the LoginForm with email and password fields. Place the RecaptchaField immediately before the primary Login action, include a Create Account link to Register, and provide the SocialAuthButtons for Google, Facebook, and Apple. When valid credentials return a TOTP, email, or SMS MFA challenge, replace the credential form with ConfirmLoginForm for the active backend-offered method. Authentication, OAuth, MFA, and reCAPTCHA verification authority remain on the backend; the prototypes do not create a session, start an OAuth flow, send a real code, or issue a real reCAPTCHA token.`
- required shared components: None
- required feature components: `LoginForm`, `ConfirmLoginForm`
- data contract: `POST /api/v1/auth/login` with email, password, and provider reCAPTCHA token; `POST /api/v1/auth/challenges/{challengeId}/verify` for a backend-offered TOTP, email, or SMS challenge. After confirmed authentication, load `GET /api/v1/user/data` into `UserStore` and use client-side router navigation to `/history` without a full-page reload.
- dependencies: `AuthStore`, `UserStore`

#### Feature Requirements

Login owns credential entry, immediate form validation, OAuth entry, MFA challenge presentation, challenge verification, authenticated user-data initialization, client-side navigation, and user-facing authentication errors. It passes its pending provider, workflow state, and safe workflow message back into LoginForm through the documented parent-controlled props. `LoginForm` composes the feature-owned `RecaptchaField`; `ConfirmLoginForm` collects only the code for the selected backend-offered TOTP, email, or SMS method. The page does not reclassify either form as shared UI. After confirmed password, MFA, or page-owned Google authentication, Login loads the unified authenticated user data into `UserStore` and navigates to History through the client-side router without a full-page reload. Follow the [cross-page authentication and session requirements](../pages-and-routes.md#authentication-and-session) for token lifecycle, authenticated data initialization, refresh, logout, and backend authority.

</details>

### 4. Register Page

- Page: Register Page
- Source: `docs/frontend/pages-and-routes.md#register-page`
- Purpose: `Allow a new user to enter the details required to create an account and accept the Terms of Service.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/register`
- Route name: `register`
- Access: Public
- Route parameters: None
- Layout: Public Layout
- Navigation behavior: After confirmed registration and UserStore initialization, use client-side router navigation to `/history` without a full-page reload; visibility never replaces server authorization.
- Required shared components: None
- Required feature components: `RegisterForm`, `ConfirmLoginForm`
- Design prototype references: `prototypes/design/pages/register.html`
- Data source and ownership: RegisterForm owns the registration draft; Register Page owns transient registration-verification challenge state; AuthStore owns authentication/session workflow; UserStore owns the confirmed authenticated application snapshot.
- Services: auth service
- Integration contracts and page responsibility: Authentication and application session; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `AuthStore`, `UserStore`
- Production placement: `frontend/src/pages/RegisterPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Register Page
- purpose: `Allow a new user to enter the details required to create an account and accept the Terms of Service.`
- route: `/register`
- layout: `Public Layout`
- Example Prototype: `design/pages/register.html`
- name: `register`
- description: `Dedicated public registration page. Render the RegisterForm with first name, surname, email, optional phone, password, confirm-password, required Terms of Service acceptance, and the RecaptchaField immediately before the primary Create Account action, plus SocialAuthButtons for Google, Facebook, and Apple and an existing-account link to Login. Do not add a separate Privacy Policy checkbox or any other field absent from the component specification and referenced prototype. Social registration requires Terms of Service acceptance before its backend OAuth start request; the optional Privacy Policy acknowledgment is false. When password registration returns its email-verification challenge, replace RegisterForm with ConfirmLoginForm configured for registration. The prototypes alone do not create an account, issue a real reCAPTCHA token, start OAuth, deliver a code, or establish a session.`
- required shared components: None
- required feature components: `RegisterForm`, `ConfirmLoginForm`
- data contract: `POST /api/v1/auth/register` with the form's first name, surname, email, optional phone, password, legal consent, and provider reCAPTCHA token; confirm password is client-only. A successful `201 Created` response returns the created public user fields and an email-verification challenge. Confirm it through `POST /api/v1/auth/registration-challenges/{challengeId}/verify`. After the backend establishes the session, load `GET /api/v1/user/data` into `UserStore` and use client-side router navigation to the existing History route without a full-page reload; see [integration contract examples](../integration-contracts.md#authentication-and-application-session).
- states: idle, validation error, reCAPTCHA required, submit pending, verification required, verification pending, invalid code, expired challenge, conflict, recoverable error, unavailable.
- dependencies: `AuthStore`, `UserStore`

#### Feature Requirements

Register owns its form validation, required Terms of Service acceptance, provider verification input, OAuth registration entry, registration-verification challenge state, confirmed session handling, authenticated user-data initialization, and navigation to the existing History route. It passes its pending provider, workflow state, and safe workflow message back into RegisterForm through the documented parent-controlled props. The optional backend Privacy Policy acknowledgment remains false because this page does not collect it separately. `RegisterForm` composes the feature-owned `RecaptchaField`; `ConfirmLoginForm` is reused only as the presentation and local-validation boundary for the registration code. The page does not reclassify either component as shared UI and does not reuse the Login MFA endpoint for registration verification. Follow the [cross-page authentication and session requirements](../pages-and-routes.md#authentication-and-session) for session establishment, token handling, and backend authority.

</details>

### 5. Training

- Page: Training
- Source: `docs/frontend/pages-and-routes.md#training`
- Purpose: `Primary page for real-time training where the user records strokes, sees instant analysis, and receives guidance.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/training`
- Route name: `training`
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: `Button`
- Required feature components: `CameraPreviewModal`; `CollapseForm` only for collapsible form sections present in the referenced prototype (none in the current prototype).
- Design prototype references: `prototypes/design/pages/training.html`
- Data source and ownership: TrainingSessionStore owns session/phase/feedback; page owns workflow.
- Services: session, media, WebSocket and audio services
- Integration contracts and page responsibility: Training session and analysis transport; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `AuthStore`, `TrainingSessionStore`
- Production placement: `frontend/src/pages/TrainingPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Training
- purpose: `Primary page for real-time training where the user records strokes, sees instant analysis, and receives guidance.`
- route: `/training`
- layout: `Authentication Layout`
- Example Prototype: `design/pages/training.html`
- camera design reference: [camera.html](../../../prototypes/design/pages/camera.html) previews the camera modal; it is not a separate application route. The Training prototype mounts `CameraPreviewModal` for its Start Training action when run through Vite, while the static HTML fallback links to this camera design reference.
- name: `training`
- description: `Follow the referenced Training HTML prototype for the page title, secondary text, section titles, descriptions, fields, labels, buttons/actions, and all other page-level content. The current prototype contains the camera preview/entry area and Coaching Cue, Connection, and Session panels; it contains no collapsible form sections, so do not invent any. Where the referenced prototype contains collapsible form sections, use the existing CollapseForm Feature Component. The Training page component owns and creates each such form configuration, deriving its title, secondary description, fields, labels, relevant field configuration, buttons/actions, and other required content directly from that prototype. Supply the corresponding CollapseForm instances through their existing title/description props and page-rendered default/footer slots; Training-specific data, configuration, form handling, and actions belong to the page, while CollapseForm remains reusable. Implement all remaining elements directly as page-level DOM/layout matching the prototype; do not extract static sections into new components. Keep the shared Button for Start Training near the camera preview. Preserve the existing camera/full-screen training modal or camera training flow, reusing its implementation without duplicate camera logic or a second training flow. Do not invent fields, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: `Button`
- required feature components: `CameraPreviewModal`; `CollapseForm` only for collapsible form sections present in the referenced prototype (none in the current prototype).
- data contract: Create the session with `POST /api/v1/training/sessions/create` before connecting to the backend-issued analysis WebSocket. Finish normally with `POST /api/v1/training/sessions/{sessionId}/complete`; use `POST /api/v1/training/sessions/{sessionId}/abandon` for cancellation or early exit. Bounded automatic reconnect keeps the same session id and stroke sequence, while the backend records the disconnected interval as a pause excluded from active training duration. See [integration contract examples](../integration-contracts.md#training-session-and-analysis-transport).
- states: idle, creating session, ready, connecting, live, reconnecting, completing, complete, abandoning, incomplete, recoverable error, unavailable.
- dependencies: `AuthStore`, `TrainingSessionStore`

#### Feature Requirements

##### Camera

- Allow switching between available cameras when supported by the device.
- Keep the selected camera active until the user changes it.
- Handle camera permission denied, unavailable camera, and initialization errors.

##### Frame Preparation

The frontend may perform lightweight frame capture, resizing, throttling, or formatting for transport. It must not perform computer-vision inference.

##### Training / Live Analysis Workflow

The frontend orchestrates live training in this order without performing computer-vision inference, stroke recognition, coaching decisions, or Text-to-Speech itself:

1. The user starts training and the frontend creates an authenticated session. See [Training session endpoints — `POST /api/v1/training/sessions/create`](../integration-contracts.md#training-session-endpoints).
2. The response supplies the authoritative `sessionId` and short-lived `analysisWebSocketUrl`; the frontend opens that backend-issued URL and never constructs an analysis host itself.
3. Camera capture and frame sampling begin only when the training session and socket state permit them.
4. For each selected frame, the frontend sends the JSON metadata message and then its matching binary JPEG without interleaving another frame pair. See [Live analysis WebSocket — Client-to-server frame message](../integration-contracts.md#client-to-server-frame-message).
5. The backend receives frames over time, performs temporal analysis, and decides internally when enough evidence exists to identify and evaluate a completed stroke. The frontend does not impose a fixed frame count or infer stroke boundaries.
6. The backend assigns the stroke's `strokeId` and `strokeNumber` and may return one or more `player_feedback` events. Each event provides canonical text feedback and may also include an optional temporary `audioUrl` for backend-generated audio of that text. See [Live analysis WebSocket — Server-to-client `player_feedback` message](../integration-contracts.md#server-to-client-player_feedback-message).
7. The frontend validates the event's active `sessionId`, displays the backend-supplied coaching text, and, when audio is enabled and the event includes `audioUrl`, plays the matching audio. It never fabricates missing observations or advice.
8. When audio is enabled and `audioUrl` is present, the frontend plays that temporary backend-generated resource. It does not generate provider-side TTS, upload coaching audio, or treat temporary audio as persistent session history. Text remains the canonical feedback.
9. If the socket disconnects, the frontend pauses frame sending and performs a bounded number of automatic reconnection attempts for the same `sessionId`. A successful reconnect resumes the same session and its stroke sequence. The backend records the disconnected interval as a session pause and excludes it from active training duration. The frontend shows an unavailable/disconnected state only after the automatic attempts fail; it never silently creates a new session.
10. Normal stop ends capture immediately, prevents later frame sends, sends the documented `stop_analysis` message, and completes the session. Early exit abandons the session as incomplete. Permission loss or a transport failure that remains after the bounded reconnect attempts becomes an explicit unavailable/disconnected state rather than silently starting a new session. See [Training session endpoints](../integration-contracts.md#training-session-endpoints) and [Live analysis WebSocket](../integration-contracts.md#live-analysis-websocket).

##### Audio Output

- Play optional `audioUrl` resources delivered with current-session `player_feedback` when audio is enabled.
- Queue playback so coaching clips do not overlap, and allow current playback to stop when training ends or newer product rules require replacement.
- If audio is unavailable, expired, or playback fails, show a clear non-blocking `Audio unavailable` message and continue with the canonical textual feedback. The training remains active and the backend still records the strokes and final session summary normally; audio failure does not change analysis or session truth.
- Release playback resources when they are no longer needed.

</details>

### 6. Dashboard

- Page: Dashboard
- Source: `docs/frontend/pages-and-routes.md#dashboard`
- Purpose: `Provides the user with an overview of their training activity, recent sessions, and quick access to the main application features.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/dashboard`
- Route name: `dashboard`
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: None
- Design prototype references: `prototypes/design/pages/dashboard.html`
- Data source and ownership: UserStore owns dashboard and initial history snapshot.
- Services: unified user-data service
- Integration contracts and page responsibility: Authenticated application data; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`
- Production placement: `frontend/src/pages/DashboardPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Dashboard
- purpose: `Provides the user with an overview of their training activity, recent sessions, and quick access to the main application features.`
- route: `/dashboard`
- layout: `Authentication Layout`
- Example Prototype: `design/pages/dashboard.html`
- name: `dashboard`
- description: `Follow the Dashboard prototype directly for all page content, sections, containers, text, and visual structure, implemented as page-level DOM/layout. Do not introduce page-specific shared components or extract static sections into reusable components. Keep Session History available as defined in the prototype. Each returned session row opens Session Review using its server-supplied session id. Sidebar, top header, and footer remain provided by the Authentication Layout and are not part of the page sections.`
- required shared components: None
- required feature components: None
- data contract: initial Dashboard aggregates and History items come from `GET /api/v1/user/data`; see [authenticated application data](../integration-contracts.md#authenticated-application-data-and-persisted-user-updates). The page does not issue a separate initial Dashboard request.
- states: loading, empty, success, recoverable error, unavailable.
- dependencies: `UserStore`

</details>

### 7. History

- Page: History
- Source: `docs/frontend/pages-and-routes.md#history`
- Purpose: `allows the user to review previous training sessions, results, performance metrics, and past coaching feedback`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/history`
- Route name: None
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: `Badge`
- Required feature components: `BaseTable`
- Design prototype references: `prototypes/design/pages/history.html`
- Data source and ownership: UserStore.sessionHistory owns the collection.
- Services: session service
- Integration contracts and page responsibility: Authenticated application data and session list; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`
- Production placement: `frontend/src/pages/HistoryPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### History
- purpose: `allows the user to review previous training sessions, results, performance metrics, and past coaching feedback`
- Route: `/history`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/history.html`
- description: `Follow the History HTML/design prototype for all sections and page-level elements. Use the existing BaseTable Feature Component for the Training Sessions table, showing only Date, Duration, Status, and a Review Session action linked to /sessions/:sessionId. Render each Status value with the shared Badge component: Reviewed uses success; Sample and Incomplete use neutral. Keep pagination at the bottom of the section. All other headings, descriptions, containers, surrounding layout, and visual elements remain page-level DOM/layout matching the prototype; do not create additional shared components or extract static sections into reusable components. Do not add fields, filters, controls, actions, states, wrappers, or components absent from the prototype or explicit page-specific Additional Description and Functionality.`
- required shared components: `Badge`
- required feature components: `BaseTable`
- data contract: the initial collection comes from `UserStore.sessionHistory`, populated by `GET /api/v1/user/data`. Items use canonical `durationSeconds`, formatted by the page for display, and explicit `historyStatus` values `reviewed`, `sample`, or `incomplete` for the visible Badge label. `GET /api/v1/training/sessions` returns the same item shape for pagination or explicit refresh and writes its result back to that store section; see [integration contract examples](../integration-contracts.md#session-history-and-session-review).
- states: loading, empty, success, recoverable error, unavailable.
- dependencies: `UserStore`

</details>

### 8. Session Review

- Page: Session Review
- Source: `docs/frontend/pages-and-routes.md#session-review`
- Purpose: Review a previous training session's supported results and coaching feedback, including available key moments, movement trends, and next recommended focus.
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/sessions/:sessionId`
- Route name: `session-review`
- Access: Authenticated
- Route parameters: sessionId (opaque)
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: None
- Design prototype references: `prototypes/design/pages/history.html`, `prototypes/design/components/training-session-card.html` (visual cues only).
- Data source and ownership: UserStore owns current authorized review result.
- Services: session service
- Integration contracts and page responsibility: Authorized session review; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`, `sessionService`
- Production placement: `frontend/src/pages/SessionReviewPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Session Review

- purpose: Review a previous training session's supported results and coaching feedback, including available key moments, movement trends, and next recommended focus.
- page/component: `frontend/src/pages/SessionReviewPage.vue`.
- route: `/sessions/:sessionId`
- name: `session-review`
- layout: `Authentication Layout`
- access: Authenticated; the backend authorizes access to the requested session.
- route parameters: required `sessionId` opaque identifier. Reject malformed identifiers and show not-found/unauthorized states without leaking whether another user's session exists.
- navigation destination: Session rows on History and Dashboard link to this route using their returned session ids. Session Review is not a top-level sidebar item; History remains the active navigation section.
- data contract: `GET /api/v1/training/sessions/{sessionId}/review`; see [frontend integration contract examples](../integration-contracts.md#session-history-and-session-review).
- visual references: [History](../../../prototypes/design/pages/history.html) and [Training Session Card](../../../prototypes/design/components/training-session-card.html). These provide visual cues only; they do not establish data or behavior beyond this entry.
- state owner: `frontend/src/stores/UserStore.ts`; data access: `frontend/src/services/sessionService.ts`. Route-specific review loading must not create another authoritative history store.
- states: loading, not found/unauthorized, success, partial/insufficient data, recoverable error, unavailable.

</details>

### 9. Subscription

- Page: Subscription
- Source: `docs/frontend/pages-and-routes.md#subscription`
- Purpose: `allows the user to view their current subscription plan, manage billing details, and change or upgrade their subscription.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/subscription`
- Route name: None
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: `PaymentCardPlan`, `BillingDetailsCard`
- Design prototype references: `prototypes/design/components/subscription/subscription.html`
- Data source and ownership: UserStore.subscription owns persisted truth; page owns selection draft.
- Services: billing/subscription services
- Integration contracts and page responsibility: Subscription and checkout; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`
- Production placement: `frontend/src/pages/SubscriptionPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Subscription
- purpose: `allows the user to view their current subscription plan, manage billing details, and change or upgrade their subscription.`
- Route: `/subscription`
- Layout: `Authentication Layout`
- Example Prototype: `design/components/subscription/subscription.html`
- description: `Required section is the Subscription section, which includes a page heading, a short description, and two main cards: the Subscription Plan Card and the Billing or Plan Management Card. Before a plan is selected, render the larger PaymentCardPlan Feature Component with No selected plan, no price, no status label, no selected styling, and a clear explanation that training services require selecting a plan. Use BillingDetailsCard for the existing billing panel. Change plan reveals the Starter, Performance, and Pro PaymentCardPlan options, with Performance marked Most popular. Manage billing remains page-owned. Do not add a separate comparison-page button or payment-status prototype controls to this page.`
- required shared components: None
- required feature components: `PaymentCardPlan`, `BillingDetailsCard`
- data contract: initial subscription data come from `GET /api/v1/user/data`. Checkout verification, plan changes, and the provider-hosted customer portal remain dedicated operations; see [integration contract examples](../integration-contracts.md#checkout-and-billing).
- states: loading, no active subscription, active, pending change, recoverable error, unavailable.
- dependencies: `UserStore`

#### Feature Requirements

Subscription reads its initial plan and billing presentation from `UserStore.subscription`, with no separate initial status request. It owns plan selection and the page-owned Manage billing action. The provider-hosted payment flow and shared backend boundaries are defined in the [Subscription and Checkout requirements](../pages-and-routes.md#subscription-and-checkout).

</details>

### 10. Profile

- Page: Profile
- Source: `docs/frontend/pages-and-routes.md#profile`
- Purpose: `Allow authenticated users to view and manage their personal profile information.`
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/profile`
- Route name: `profile`
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: `CollapseForm`
- Design prototype references: `prototypes/design/pages/profile.html`
- Data source and ownership: Page draft; UserStore.personalInformation owns confirmed state.
- Services: user-data service
- Integration contracts and page responsibility: Persisted user updates; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`
- Production placement: `frontend/src/pages/ProfilePage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Profile
- purpose: `Allow authenticated users to view and manage their personal profile information.`
- Route: `/profile`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/profile.html`
- name: `profile`
- description: `Follow the referenced Profile HTML prototype for the page title, secondary text, and the remaining Personal Information section, which uses the existing CollapseForm Feature Component. The Profile page component owns and creates the section's data/configuration, deriving its title, secondary description, fields, labels, relevant configuration, buttons/actions, and any additional content directly from the prototype. Supply the CollapseForm instance through its existing title/description props and page-rendered default/footer slots. Profile-specific values, configuration, form handling, and actions remain in the Profile page; CollapseForm stays reusable. Do not create additional Profile section components unless explicitly required elsewhere. Implement all remaining page-level elements directly as DOM/layout matching the prototype. Do not invent fields, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: None
- required feature components: `CollapseForm`
- data contract: initial Personal Information data come from `GET /api/v1/user/data`. The dedicated Personal Information `PATCH` endpoint replaces the normalized `UserStore.personalInformation` section. See [authenticated application data and persisted user updates](../integration-contracts.md#authenticated-application-data-and-persisted-user-updates).
- states: loading, loaded, validation error, save pending, recoverable error, unavailable.
- dependencies: `UserStore`

</details>

### 11. Settings

- Page: Settings
- Source: `docs/frontend/pages-and-routes.md#settings`
- Purpose: None
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/settings`
- Route name: `settings`
- Access: Authenticated
- Route parameters: None
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: `CollapseForm`
- Design prototype references: `prototypes/design/pages/settings.html`
- Data source and ownership: Page drafts; UserStore owns confirmed setting groups.
- Services: user-data service
- Integration contracts and page responsibility: Persisted user updates; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `UserStore`
- Production placement: `frontend/src/pages/SettingsPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Settings

- Route: `/settings`
- Layout: `Authentication Layout`
- Example Prototype: `design/pages/settings.html`
- name: `settings`
- description: `Follow the referenced Settings HTML prototype as the source of truth for the page title, secondary text, and the remaining Account Security · Change Password, Notifications, and Privacy & Data sections. Each collapsible section uses the existing CollapseForm Feature Component. The Settings page owns and creates each section's data/configuration directly from the prototype. Pass only the section title/header and secondary title/description through the existing title and description props. Define and render all section-specific fields, labels, selects, controls, buttons, actions, and other body content in the Settings page, supplying that content through CollapseForm's default slot and its footer slot where appropriate. Field configuration, values, validation, form handling, and action behavior remain owned by the Settings page; do not pass a field schema to CollapseForm or move Settings-specific content or behavior into it. Keep CollapseForm reusable. Do not create separate components for individual Settings sections unless explicitly required elsewhere. Implement all remaining page-level elements directly as DOM/layout matching the prototype. Do not invent fields, controls, buttons, labels, descriptions, states, or components absent from the prototype or explicit project requirements.`
- required shared components: None
- required feature components: `CollapseForm`
- data contract: initial Notifications and Privacy & Data settings come from `GET /api/v1/user/data`. Each independently saved persisted group uses its dedicated `PATCH` endpoint; Change Password, data export, and account deletion remain separate actions. See [authenticated application data and persisted user updates](../integration-contracts.md#authenticated-application-data-and-persisted-user-updates).
- states: loading, loaded, validation error, save pending, recoverable error, unavailable.
- dependencies: `UserStore`

</details>

### 12. Not Found

- Page: Not Found
- Source: `docs/frontend/pages-and-routes.md#not-found`
- Purpose: None
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/not-found`
- Route name: `not-found`
- Access: Public
- Route parameters: None
- Layout: Public Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: None
- Design prototype references: `prototypes/design/pages/not-found.html`
- Data source and ownership: No application data.
- Services: None
- Integration contracts and page responsibility: None; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: None
- Production placement: `frontend/src/pages/NotFoundPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Not Found

- Route: `/not-found`
- Layout: `Public Layout`
- Example Prototype: `design/pages/not-found.html`
- name: `not-found`
- description: `The page show 404 not found`
- required shared components: None
- required feature components: None
- dependencies: None

</details>

### 13. Checkout

- Page: Checkout
- Source: `docs/frontend/pages-and-routes.md#checkout`
- Purpose: None
- Description / page requirements: Captured verbatim in the exact source contract below, including prohibitions and recovery behavior.
- Route: `/checkout`
- Route name: `checkout`
- Access: Authenticated
- Route parameters: Validated provider return context only as documented
- Layout: Authentication Layout
- Navigation behavior: Apply the root public/authenticated navigation rules; visibility never replaces server authorization; preserve documented active-state/return behavior.
- Required shared components: None
- Required feature components: `Checkout`
- Design prototype references: `prototypes/design/components/checkout/checkout.html`
- Data source and ownership: CheckoutStore owns transient phase; UserStore.subscription owns persisted truth; page owns billing workflow.
- Services: billing service
- Integration contracts and page responsibility: Checkout and billing; exact contract links and page responsibilities remain in the source contract below.
- States and workflows: Every state and feature requirement in the exact source contract below, plus the applicable Application State Matrix row; no unsupported state is invented.
- Dependencies: `CheckoutStore`
- Production placement: `frontend/src/pages/CheckoutPage.vue`.
- Blockers: None.

<details>
<summary>Exact authoritative page contract</summary>

### Checkout

- Route: `/checkout`
- Layout: `Authentication Layout`
- Example Prototype: `design/components/checkout/checkout.html`
- name: `checkout`
- description: `The Checkout page renders the Checkout feature component and owns the page-level billing workflow. Checkout composes a selected-plan ChoosePlanCard with Pay with Stripe and Pay with PayPal actions underneath. Its right-hand area renders backend-verified pending/cancelled/failed/expired states through PaymentStatusCard; after verified success it replaces the status card with OrderSummaryCard showing the chosen plan, price, and Paid status. It contains no Payment Information section and never collects raw card details.`
- required shared components: None
- required feature components: `Checkout`
- data contract: provider-hosted checkout start and server-verified return; see [integration contract examples](../integration-contracts.md#checkout-and-billing).
- states: pending, succeeded only after backend verification, cancelled, failed, expired, recoverable error, unavailable.
- dependencies: `CheckoutStore`

#### Feature Requirements

The Checkout page owns provider selection, redirect to the backend-returned hosted URL, and the page-level handling of return, pending, final, failure, and retry states. The `Checkout` feature adapts that state and composes its focused child cards without taking over requests, redirects, verification, or persisted subscription ownership. The page must obtain backend-verified subscription status rather than infer success from a redirect. Follow the [Subscription and Checkout requirements](../pages-and-routes.md#subscription-and-checkout) and the [billing integration contract](../integration-contracts.md#checkout-and-billing).

## Cross-Page Feature Requirements

</details>

Router policy: public/protected routing, validated internal return targets, one refresh-and-single-retry policy for 401, distinct 403 authorization handling, unknown-route redirect to `/not-found`, and active navigation derived from route identity.

## 7. Project Structure

Use the shallow structure in `docs/frontend/frontend-project-structure.md`; no frontend `modules/` root and no empty placeholders.

### Concrete placement map

- Pages: `frontend/src/pages/HomePage.vue`, `FeaturesPage.vue`, `LoginPage.vue`, `RegisterPage.vue`, `TrainingPage.vue`, `DashboardPage.vue`, `HistoryPage.vue`, `SessionReviewPage.vue`, `SubscriptionPage.vue`, `ProfilePage.vue`, `SettingsPage.vue`, `NotFoundPage.vue`, `CheckoutPage.vue`.
- Layouts: `frontend/src/layouts/PublicLayout.vue`, `frontend/src/layouts/AuthenticationLayout.vue`.
- Shared/feature components: exact placement is recorded in every component entry above; simple units remain single Vue files, while only the Home slider and explicitly documented checkout/cookie feature systems keep focused supporting files.
- Stores: `frontend/src/stores/AuthStore.ts`, `UserStore.ts`, `TrainingSessionStore.ts`, `CheckoutStore.ts`.
- Services: focused authenticated HTTP/auth/user-data/session/training-transport/browser-media/audio/billing services under `frontend/src/services/`; after backend OAuth success returns directly to a validated protected destination, the global authentication guard bootstraps the memory-only access token through the CSRF-protected refresh contract before resolving navigation or loading user data. No dedicated frontend OAuth callback route is created. History services preserve the canonical `durationSeconds` and explicit `historyStatus` item shape across initial load and pagination. Use `frontend/src/proxy/` only if a real adapter boundary is required.
- Router: route records in `frontend/src/router/index.ts` and focused guards/helpers under `frontend/src/router/` only when required.
- Global host: `frontend/src/App.vue`; bootstrap `frontend/src/main.ts`.
- Shared composables: field/Button and genuinely reusable browser/UI lifecycles under `frontend/src/composables/`; feature-only `useCookieConsent.ts`, `useCheckout.ts`, and slider collaborators remain with their owners.
- Runtime configuration, constants, utilities, assets, global tokens/styles and tests use the corresponding approved `frontend/src/` directories. Apply the shared background from `prototypes/design/background.html` through global styles rather than a flat fallback or page-by-page copies. Do not create any of these as placeholders during planning.

### Acceptance and Test Plan

1. Route/access coverage: Vitest verifies all thirteen routes, names only where specified, layouts, opaque session parameter handling, public/protected guards, validated returns, 401 single retry, 403 behavior, unknown-route redirect and active navigation; Playwright verifies every route loads its expected page.
2. Component contracts: unit/component tests cover every documented prop/default/event/slot/state, parent ownership, no duplicate store/API access, keyboard/focus behavior, accessible names/labels/announcements and responsive states.
3. Cookie/privacy: verify versioned persistence, accept/reject/preferences, Essential locked on, close-without-save, policy actions not changing consent, global single mount, and survival across routes, refresh, login and logout.
4. Authentication/security: verify LoginForm and RegisterForm emit validated request payloads while their pages return pending/provider/error/success state through the documented props; Login submits only the declared email, password, and reCAPTCHA token; Register field/legal-consent and `socialRegister` mapping; TOTP/email/SMS Login MFA and separate registration-verification challenges; registration confirmation before `GET /api/v1/user/data` and History navigation; protected-route OAuth refresh bootstrap before navigation and user-data loading; allowlisted OAuth failure status handling; reCAPTCHA token distinction; challenge expiry and single use; memory-only access token; Secure HttpOnly refresh cookie; CSRF use; refresh single retry; logout cleanup; no provider secrets or localStorage tokens.
5. Store ownership: atomic UserStore initialization; section-only normalized replacement; identical History item shape across unified initialization and pagination, including canonical `durationSeconds` and explicit `historyStatus`; no duplicate history/review/subscription truth; recoverable pages preserve confirmed snapshots and unsaved drafts.
6. Training transport/lifecycle: session create/complete/abandon, backend-issued socket, immediate JSON-metadata then binary-JPEG pairing without interleaving, bounded capture/backpressure, structured event/session/stroke filtering, bounded reconnect with same session/sequence, audio queue cleanup, and idempotent release of tracks/socket/timers/listeners/encodes on stop/error/unmount.
7. Checkout security/lifecycle: provider-hosted start, validated internal returnPath, backend-authoritative status, pending backoff, no overlapping polls, cancellation/route-exit cleanup, terminal mapping, timeout never becoming success, subscription refresh after success, no raw cards/frontend confirmation/webhook calls.
8. Responsive/accessibility/visual: representative desktop/tablet/mobile viewports, safe Training mobile state, navigation/forms/tables/modals/banner/cards/media proportions, no horizontal overflow, focus visibility/restoration, contrast, touch targets, semantic markup, reduced motion and visual regression against mapped prototypes without claiming pixel-perfect production equivalence.
9. Quality gates: production build, TypeScript/static checks, ESLint, Vitest and Playwright; do not disable failures. Clearly label mocks/fixtures and never display fabricated analysis, history, authentication or payment outcomes as production truth.

## 8. Open Questions and Blockers

None for planning. Backend adoption is a non-blocking live-integration warning: build state/services against clearly identified contract-shaped fixtures, while live connection remains pending confirmation/adaptation/versioning of endpoint names, schemas, retry bounds, error mappings and provider behavior.

## 9. Build Order

### Phase 1 — Foundation
- Items: approved Vite/TypeScript structure, dependencies, tokens/global styles, runtime config, error model and test harness.
- Depends on: validated plan.
- Unblocks: every production unit.
- Reason: implementation files require the approved structure and shared conventions.

### Phase 2 — Shared UI
- Items: Button, TextButton, Field foundation and four fields, BaseCard, StateLabel, Badge, FormStatusMessage, LayoutHeader with focused unit/accessibility tests.
- Depends on: Phase 1.
- Unblocks: feature components and pages.
- Reason: consumers must not duplicate primitives.

### Phase 3 — State, services and routing foundations
- Items: authenticated client, AuthStore, UserStore, TrainingSessionStore, CheckoutStore, auth/user/session/training/billing services and route access policy.
- Depends on: Phase 1; use explicitly labeled contract-shaped fixtures until backend owners confirm or adapt live contracts.
- Unblocks: data-owning features/pages.
- Reason: establish one authoritative owner before consumers.

### Phase 4 — Layout and global feature UI
- Items: TopNav, SidebarNav, Footer, BaseModal, Public/Authentication layouts, cookie/privacy components and global App mount.
- Depends on: Phases 1–2.
- Unblocks: all route pages and global consent verification.
- Reason: shells and global UI precede page composition.

### Phase 5 — Public/authentication/Home features
- Items: RecaptchaField, SocialAuthButton and owner-local groups, LoginForm, ConfirmLoginForm, RegisterForm, HomePageInfoSection, HomePageVideoSlider, Home/Features/Login/Register/Not Found pages.
- Depends on: Phases 2–4.
- Unblocks: public flows and authenticated entry.
- Reason: build feature owners before their page consumers.

### Phase 6 — Authenticated data pages
- Items: BaseTable, CollapseForm, PaymentCardPlan, BillingDetailsCard, Dashboard, History, Session Review, Profile, Settings and Subscription.
- Depends on: Phases 2–4 and UserStore/services.
- Unblocks: authenticated data and billing entry workflows.
- Reason: reuse the atomic user snapshot without duplicate ownership.

### Phase 7 — Realtime Training
- Items: CameraPreviewModal, camera/preview/frame/transport/audio lifecycles, Training page and cleanup/reconnect tests.
- Depends on: Phases 2–4 and TrainingSessionStore/services.
- Unblocks: complete training workflow.
- Reason: latency/resource-sensitive work follows stable transport and ownership boundaries.

### Phase 8 — Checkout
- Items: Checkout owner, ChoosePlanCard child, PaymentStatusCard, OrderSummaryCard, Checkout page, bounded verification polling and subscription refresh.
- Depends on: Phases 2–4, Subscription foundations and billing contracts.
- Unblocks: hosted checkout and verified return flow.
- Reason: payment UI must depend on backend-authoritative verification and shared state labels/buttons.

### Phase 9 — Routing, quality and verification
- Items: finalize router registration/guards/navigation, responsive and accessibility pass, Vitest/component tests, Playwright route/workflow tests, visual-state comparisons, production build/static checks and manual verification.
- Depends on: Phases 4–8.
- Unblocks: implementation handoff.
- Reason: validate the integrated system without disabling failures or presenting mocks as live behavior.
