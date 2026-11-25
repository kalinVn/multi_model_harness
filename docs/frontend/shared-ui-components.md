CSS in the prototype Vue components is for visual reference only; production styles may live outside components and use shared design tokens.

# Shared UI Components

## LayoutHeader

Name: LayoutHeader

Description: LayoutHeader is the shared authenticated-layout header that identifies the active page, displays the current user, and exposes the logout action without owning authentication state or logout behavior.

### Props and States

| Prop | Type | Requirement |
| --- | --- | --- |
| `pageTitle` | String | Required; the active page name displayed after the `Tennis AI Coach /` prefix. |
| `userName` | String | Required; the authenticated user's display name. |

The component renders the page context as `Tennis AI Coach / {pageTitle}`, the supplied user name, the `demo user` descriptor only when the consuming debug or prototype context explicitly requests it, and a shared `Button` labeled `Log out`.

The header must remain keyboard accessible, responsive, and usable next to the mobile form of SidebarNav. It does not determine the current route, read the authenticated user, or perform logout itself.

### Emits and Ownership

Emits:

- `logout` — emitted when the Log out Button is activated.

The Authentication Layout receives `pageTitle` from the active page contract, reads `userName` from the authenticated application state, and handles `logout` through the authoritative authentication flow. LayoutHeader has no router, store, API, token, session, or redirect ownership.

### Prototype References

#### Design Prototypes

- [header.html](../../prototypes/design/components/header.html)
- [authentication.html](../../prototypes/design/layouts/authentication.html)

#### Vue Components

None

---

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

The existing [ButtonController.js](../../prototypes/composables/ButtonController.js) exports `useButtonController`: it derives `isDisabled` from disabled/loading, suppresses disabled clicks, and emits enabled clicks. This is UI behavior, not an action dispatcher. Planned production placement is `frontend/src/components/buttons/Button.vue` plus `frontend/src/composables/ButtonController.ts`, preserving that separation in TypeScript. These planned files are not claimed to exist.


The inspected Button renders a native button and does not support a `to` prop or `RouterLink` mode. Preserve the existing parent-owned navigation convention: an action may invoke the owning page/feature handler, while link destinations use the existing link/navigation components. Do not implement separate navigation logic in page-specific button components or document an unsupported `to` API. Navigation destinations and access policy stay outside Button.

### Prototype References

#### Design Prototypes

- [button primary default](../../prototypes/design/components/buttons/specimens/button-primary-default.html)
- [button primary hover](../../prototypes/design/components/buttons/specimens/button-primary-hover.html)
- [button primary pressed](../../prototypes/design/components/buttons/specimens/button-primary-pressed.html)
- [button primary focus visible](../../prototypes/design/components/buttons/specimens/button-primary-focus-visible.html)
- [button primary disabled](../../prototypes/design/components/buttons/specimens/button-primary-disabled.html)
- [button primary loading](../../prototypes/design/components/buttons/specimens/button-primary-loading.html)
- [button secondary default](../../prototypes/design/components/buttons/specimens/button-secondary-default.html)
- [button secondary hover](../../prototypes/design/components/buttons/specimens/button-secondary-hover.html)
- [button secondary pressed](../../prototypes/design/components/buttons/specimens/button-secondary-pressed.html)
- [button secondary focus visible](../../prototypes/design/components/buttons/specimens/button-secondary-focus-visible.html)
- [button secondary disabled](../../prototypes/design/components/buttons/specimens/button-secondary-disabled.html)
- [button secondary loading](../../prototypes/design/components/buttons/specimens/button-secondary-loading.html)
- [button ghost default](../../prototypes/design/components/buttons/specimens/button-ghost-default.html)
- [button ghost hover](../../prototypes/design/components/buttons/specimens/button-ghost-hover.html)
- [button ghost pressed](../../prototypes/design/components/buttons/specimens/button-ghost-pressed.html)
- [button ghost focus visible](../../prototypes/design/components/buttons/specimens/button-ghost-focus-visible.html)
- [button ghost disabled](../../prototypes/design/components/buttons/specimens/button-ghost-disabled.html)
- [button ghost loading](../../prototypes/design/components/buttons/specimens/button-ghost-loading.html)
- [button size small](../../prototypes/design/components/buttons/specimens/button-size-small.html)
- [button size medium](../../prototypes/design/components/buttons/specimens/button-size-medium.html)
- [button type button](../../prototypes/design/components/buttons/specimens/button-type-button.html)
- [button type submit](../../prototypes/design/components/buttons/specimens/button-type-submit.html)
- [button type reset](../../prototypes/design/components/buttons/specimens/button-type-reset.html)

#### Vue Components

- [Button.vue](../../prototypes/design/components/buttons/Button.vue)

---

## Badge

Name: Badge

Description: Badge is the shared presentational text label for compact statuses and semantic emphasis. It provides the restrained pill treatment used by History and BaseTable without owning the status value or any resulting behavior.

### Component Properties and Data Flow

| Prop | Supported values / type | Default |
| --- | --- | --- |
| `variant` | `success`, `neutral` | `success` |

The visible text comes from the required default slot. `success` uses the existing green History status treatment shown for `Reviewed`. `neutral` uses the existing muted History status treatment shown for `Sample` and `Incomplete`.

The parent owns the status value and selects the variant. Badge has no application state, emitted events, store or API access, navigation, persistence, icon behavior, or business logic. It must not infer a variant from arbitrary slot text.

Badge renders non-interactive text and must not be used as a button or link. Its text remains the accessible status value; color is supplementary and never the only status indicator.

### Prototype References

#### Design Prototypes

- [badge.html](../../prototypes/design/components/labels/badge.html)
- [History](../../prototypes/design/pages/history.html)
- [BaseTable](../../prototypes/design/components/tables/BaseTable.html)

#### Vue Components

- [Badge.vue](../../prototypes/components/labels/Badge.vue)

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

- [text button accent default](../../prototypes/design/components/buttons/specimens/text-button-accent-default.html)
- [text button accent hover](../../prototypes/design/components/buttons/specimens/text-button-accent-hover.html)
- [text button accent pressed](../../prototypes/design/components/buttons/specimens/text-button-accent-pressed.html)
- [text button accent focus visible](../../prototypes/design/components/buttons/specimens/text-button-accent-focus-visible.html)
- [text button accent disabled](../../prototypes/design/components/buttons/specimens/text-button-accent-disabled.html)
- [text button inherit default](../../prototypes/design/components/buttons/specimens/text-button-inherit-default.html)
- [text button inherit hover](../../prototypes/design/components/buttons/specimens/text-button-inherit-hover.html)
- [text button inherit pressed](../../prototypes/design/components/buttons/specimens/text-button-inherit-pressed.html)
- [text button inherit focus visible](../../prototypes/design/components/buttons/specimens/text-button-inherit-focus-visible.html)
- [text button inherit disabled](../../prototypes/design/components/buttons/specimens/text-button-inherit-disabled.html)

#### Vue Components

- [TextButton.vue](../../prototypes/design/components/buttons/TextButton.vue)

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

- [base-card.html](../../prototypes/design/components/cards/base-card.html)

#### Vue Components

- [BaseCard.vue](../../prototypes/components/cards/BaseCard.vue)

---

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

- [state-label.html](../../prototypes/design/components/labels/state-label.html)

#### Vue Components

- [StateLabel.vue](../../prototypes/components/labels/StateLabel.vue)

---

## FormStatusMessage

Name: FormStatusMessage

Description: FormStatusMessage is the shared, centered form-level feedback component used above the first field in LoginForm, RegisterForm, CollapseForm content, and other forms that expose an overall workflow state. It presents parent-supplied status text with a state-specific icon and visual treatment without owning form, authentication, request, or navigation behavior.

### Component Functionality

The component supports three visible states. When `message` is empty, it renders no output and occupies no layout space.

| State | Visible behavior | Accessibility behavior |
| --- | --- | --- |
| `pending` | Shows the pending icon and centered parent-supplied progress text. | Uses `role="status"`, `aria-live="polite"`, and `aria-busy="true"`. |
| `error` | Shows the error icon and centered parent-supplied recoverable-error text. | Uses `role="alert"` and `aria-live="assertive"`. |
| `success` | Shows the success icon and centered parent-supplied confirmed-success text. | Uses `role="status"` and `aria-live="polite"`. |

Icons are decorative and hidden from assistive technology because the visible text carries the complete meaning. State is never communicated by color or icon alone. Pending motion respects `prefers-reduced-motion`.

### Component Properties and Data Flow

| Prop | Type / supported values | Requirement |
| --- | --- | --- |
| `state` | `pending`, `error`, `success` | Required; selects the icon, semantic role, and state-specific CSS treatment. |
| `message` | String, empty by default | Parent-supplied visible feedback. An empty value suppresses the component entirely. |

The parent owns the actual workflow state and message and passes both through props. FormStatusMessage has no slots, local application state, emitted events, store access, API calls, retry behavior, authentication logic, persistence, or navigation.

Field-level validation remains with the owning form and its fields. FormStatusMessage is only for form-level workflow feedback and does not replace labels, descriptions, or individual validation errors.

### Prototype References

#### Design Prototypes

- [form-status-message-pending.html](../../prototypes/design/components/form-status-message/form-status-message-pending.html)
- [form-status-message-error.html](../../prototypes/design/components/form-status-message/form-status-message-error.html)
- [form-status-message-success.html](../../prototypes/design/components/form-status-message/form-status-message-success.html)

#### Vue Components

- [FormStatusMessage.vue](../../prototypes/components/messages/FormStatusMessage.vue)

---

## Field

Name: Field

Description: The field prototypes in `prototypes/components/fields/` demonstrate a label and native control with standard Vue `v-model`. They are reference implementations, without application, store, or API integration.

### Shared Composable

[useField.js](../../prototypes/composables/useField.js) provides shared value updates, reset-to-initial-value behavior, and label detection. It is a composable, not a visual component. Each field-specific composable composes `useField` and adds only its specialized behavior.

The parent owns the value. The Vue component binds the control to its field-specific composable, and updates pass through `useField` to emit `update:modelValue`.

```text
useField
   ↓
useTextField / useNumberField / useSelectField / useDateField
   ↓
Corresponding Vue component
```

### Usage and Source of Truth

These prototypes require a Vue 3 SFC build environment. Pass a unique `id` and a parent-owned `v-model`. Labels are optional; provide `aria-label` when omitting a visible label. Native attributes are forwarded to the control.

Use the linked HTML prototypes for visual design and the Vue files and composables for current props, events, and behavior. Keep shared behavior in `useField` and field-specific behavior in the corresponding composable; do not duplicate those implementations in this document.

### Prototype References

#### Design Prototypes

None

#### Vue Components

None

## TextField

Name: TextField

Description: Single-line text input. Use it for names and other short free-text values.

`useTextField` composes the shared `useField` composable and adds text-clearing behavior.

### Prototype References

#### Design Prototypes

- [text-field.html](../../prototypes/design/components/fields/text-field.html)
- [text-field-states.html](../../prototypes/design/components/fields/text-field-states.html)

#### Vue Components

- [TextField.vue](../../prototypes/components/fields/TextField.vue)

## NumberField

Name: NumberField

Description: Numeric input that converts entered values to numbers and represents an empty field as `null`. Use it for quantities or other numeric values.

`useNumberField` composes the shared `useField` composable and adds numeric conversion and unit increment/decrement behavior.

### Prototype References

#### Design Prototypes

- [number-field.html](../../prototypes/design/components/fields/number-field.html)
- [number-field-states.html](../../prototypes/design/components/fields/number-field-states.html)

#### Vue Components

- [NumberField.vue](../../prototypes/components/fields/NumberField.vue)

## SelectField

Name: SelectField

Description: Native selection from supplied options, supporting single or multiple values. Use it when users choose from a predefined set of options.

`useSelectField` composes the shared `useField` composable and adds option selection and selected-option lookup.

### Prototype References

#### Design Prototypes

- [select-field.html](../../prototypes/design/components/fields/select-field.html)
- [select-field-states.html](../../prototypes/design/components/fields/select-field-states.html)

#### Vue Components

- [SelectField.vue](../../prototypes/components/fields/SelectField.vue)

## DateField

Name: DateField

Description: Native date input using `YYYY-MM-DD` strings without timezone conversion. Use it for calendar dates that do not require a time of day.

`useDateField` composes the shared `useField` composable and adds date assignment and clearing behavior.

### Prototype References

#### Design Prototypes

- [date-field.html](../../prototypes/design/components/fields/date-field.html)
- [date-field-states.html](../../prototypes/design/components/fields/date-field-states.html)

#### Vue Components

- [DateField.vue](../../prototypes/components/fields/DateField.vue)
