# SidebarNav

## Additional Description and Functionality

For this component build, `SidebarNav` reads its authenticated application navigation from `AuthenticatedNavigationStore` instead of requiring Authentication Layout to construct and pass the `items` property.

`AuthenticatedNavigationStore` owns the static authenticated destinations in this order:

- Dashboard
- Training
- History
- Subscription
- Profile
- Settings
- Checkout

The store supplies each destination's existing label and route target and marks the active destination from the current authenticated navigation context. `SidebarNav` renders that store-provided collection and retains its existing desktop sidebar, responsive drawer, accessibility, focus, scroll-lock, dismissal, and cleanup behavior.

Session Review remains reachable from Dashboard or History session rows and is not a persistent sidebar destination.

This authenticated-navigation store is navigation state only. It is not `AuthStore`, does not own the authenticated session or tokens, does not authorize routes, and does not own user data. `SidebarNav` does not call APIs or mutate authentication or user state.

This component-specific build requirement overrides only the conflicting persistent boundary that requires Authentication Layout to populate and pass the `items` property. All other persistent `SidebarNav` requirements continue to apply.
