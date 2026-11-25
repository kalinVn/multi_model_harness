## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/feature-components.md
- docs/frontend/shared-ui-components.md

# DashboardMetricCard

## Additional Description and Functionality

Build `DashboardMetricCard` from its persistent Feature Component specification and declared design and Vue prototypes.

The component accepts exactly three parent-supplied properties:

- `title` — the short label above the metric, such as `Sessions this month`;
- `value` — the already formatted primary value, such as `12`, `8h 40m`, or `Monday`;
- `footer` — one object containing `text`, `type: 'text' | 'badge'`, and an optional Badge `variant`.

Dashboard is the parent and the data owner. It reads the authoritative statistics from `UserStore`, calculates comparisons, formats durations and dates, and supplies all three properties to each card. The card renders the supplied values only. It must not read a store, call an API, calculate a comparison, format source values, own count-up state, navigate, or emit a business action.

When `footer.type` is `badge`, render the existing shared `Badge` with the supplied text and `success` or `neutral` variant. When `footer.type` is `text`, render the text as ordinary muted supporting content. The component always renders one footer treatment and must not infer its type or variant from `title` or `value`.

## References

- `docs/frontend/feature-components.md#dashboardmetriccard`
- `docs/frontend/shared-ui-components.md#badge`
- `prototypes/design/components/feature-components/dashboard-metric-card.html`
- `prototypes/components/features/dashboard/DashboardMetricCard.vue`
