# History

## Additional Description and Functionality

History uses `Authentication Layout` and supplies `History` as the active page name through the existing `LayoutStore.currentPageTitle` page-context boundary.

Populate the page's initial training-session collection from `UserStore.sessionHistory`. The page must not issue a redundant initial request when the authenticated `UserStore` snapshot already contains that collection.

Preserve the existing History page contract:

- render the existing `BaseTable` Feature Component for the Training Sessions table;
- show Date, Duration, Status, and the existing Review Session action;
- render status values with the shared `Badge`: `Reviewed` uses `success`; `Sample` and `Incomplete` use `neutral`;
- link each Review Session action to `/sessions/:sessionId` using the server-supplied session id;
- keep pagination at the bottom of the section;
- keep the remaining headings, descriptions, containers, and surrounding visual structure as page-owned markup from the declared History design prototype;
- do not add any field, filter, control, action, state, wrapper, or component that is absent from the declared History design prototype and this file.

Treat an empty `UserStore.sessionHistory` collection as a successful empty state. Preserve the documented loading, success, recoverable-error, and unavailable states. Pagination or an explicit refresh may use the existing session-list service boundary and must write the confirmed result back to `UserStore.sessionHistory`; the page must not create a second authoritative history collection.

`UserStore` owns the confirmed session-history data. History owns only page presentation, pagination/filter interaction state, and coordination of supported refresh actions. `Authentication Layout` owns the shell, while `SidebarNav`, `LayoutHeader`, and `Footer` retain their own component responsibilities.
