# New Frontend Plan

## 1. Frontend Scope and Source Authority

### Frontend Type
`new`

### Root Specification
- `specification_path`
- resolved root frontend specification

### Authoritative Supporting Sources
- supporting specifications referenced by the root frontend specification
- visual references required for planning
- shared frontend rules referenced by the specification

### Source Priority
1. Root frontend specification and its authoritative supporting specifications
2. Referenced visual prototypes
3. Shared frontend design-system rules

### Frontend Scope
Describe the complete frontend implementation scope that must be planned.

### Planning Boundary
Define what belongs to frontend planning and which responsibilities remain outside the frontend.

---

## 2. Project Structure

### Authoritative Structure Sources
List the project-structure specifications referenced by the root frontend specification.

### Frontend Root
Define the application root directory.

### Planned Directory Structure
Define the required production structure for:
- pages
- layouts
- shared components
- feature components
- stores
- composables
- services
- routing
- styles
- assets
- utilities
- configuration
- tests
- component-specific supporting files

### Placement Rules
For every planned page, component, store, composable, service, and supporting file, define where it belongs.

### Ownership Rules
Define which files and logic belong to which page, component, or feature owner.

### Structural Constraints
Record architectural layers or structures that must not be introduced.

---

## 3. User Types and Access

For each user type define:

### User Type
- name
- authentication state
- accessible pages
- restricted pages
- feature access
- subscription-related access
- relevant navigation

---

## 4. Layouts

For every required layout define:

### Layout
- name
- purpose
- public or authenticated
- pages using the layout
- navigation used
- shared components
- relevant prototype reference
- responsive requirements
- accessibility requirements

---

## 5. Pages and Routes

For every required page define:

### Page
- page name
- route
- access type
- required layout
- route parameters
- navigation entry
- feature components
- shared components
- required stores
- required composables
- required services
- backend dependencies
- application states
- relevant prototype reference
- implementation location
- acceptance requirements

---

## 6. Navigation

### Public Navigation
Define:
- visible items
- destinations
- authentication behavior
- mobile behavior
- prototype reference

### Authenticated Navigation
Define:
- visible items
- destinations
- authentication requirements
- session-state behavior
- mobile behavior
- prototype reference

### Navigation State Transitions
Define behavior after:
- login
- logout
- authentication expiration
- authorization failure
- route protection

---

## 7. Shared Components

For every shared component define:

### Shared Component
- component name
- purpose
- pages/features using it
- props/input contract
- emitted events
- states
- accessibility requirements
- prototype reference
- implementation location
- dependencies

---

## 8. Feature Components

For every feature-specific component define:

### Feature Component
- component name
- owning feature/page
- purpose
- child components
- shared components used
- local state
- composables
- stores
- services
- backend dependencies
- prototype reference
- implementation location

---

## 9. State Management and Data Ownership

### Global Stores
For each store define:
- store name
- responsibility
- authoritative data owned
- consumers
- update sources
- reset/cleanup conditions

### Local State
Define which state remains page-local, feature-local, or device-local.

### Data Ownership Rules
Define:
- single sources of truth
- data that must not be duplicated
- server-authoritative state
- temporary frontend-only state

---

## 10. Composables

For every required composable define:

### Composable
- name
- responsibility
- owner
- inputs
- outputs
- stores used
- services used
- lifecycle responsibilities
- implementation location

---

## 11. Services and Integration

For every frontend service define:

### Service
- name
- responsibility
- backend endpoints or transports
- authentication requirements
- consumers
- error handling
- retry/recovery behavior
- implementation location

---

## 12. Feature Workflows

For every significant feature workflow define:

### Workflow
- name
- entry condition
- ordered frontend steps
- involved pages/components
- stores
- composables
- services
- backend dependencies
- success state
- failure states
- recovery behavior
- cleanup behavior

Examples may include:
- authentication
- MFA
- OAuth
- authenticated application initialization
- training/live analysis
- subscription
- checkout
- session review

---

## 13. Frontend / Backend Boundary

### Frontend Responsibilities
List responsibilities owned by the frontend.

### Backend Responsibilities
List responsibilities that must remain backend-owned.

### Integration Boundaries
Define where frontend and backend communicate.

### Forbidden Responsibility Movement
Record backend responsibilities that must not be implemented in the browser.

---

## 14. Application States and Recovery

For each relevant page or feature define:

- initial
- loading
- empty
- success
- validation error
- recoverable error
- unavailable
- disconnected
- unauthorized
- forbidden

For each state define:
- user-visible behavior
- preserved data
- available actions
- retry behavior
- recovery behavior

---

## 15. Responsive Requirements

Define required behavior for:
- desktop
- tablet
- mobile

Include:
- navigation adaptation
- layout stacking
- typography
- controls
- media
- camera preview
- overflow behavior
- feature-specific responsive constraints

---

## 16. Accessibility Requirements

Define applicable requirements for:
- semantic HTML
- labels
- keyboard navigation
- focus states
- contrast
- non-color state communication
- icon-only controls
- asynchronous announcements
- reduced motion

---

## 17. Dependencies

For each planned item define:

- dependency
- dependent item
- reason
- whether dependency is frontend or backend
- whether it blocks implementation
- required resolution

---

## 18. Open Questions and Blockers

For every unresolved issue include:

```text
question_or_missing_information
affected_plan_items
implementation_impact
blocking
required_resolution
```

If no unresolved issues exist, return an empty list.

---

## 19. Build Order

Return the recommended implementation sequence based on actual dependencies.

Example structure:

1. project structure
2. design foundation
3. shared components
4. feature components
5. stores and shared state
6. composables
7. services and integrations
8. layouts
9. pages
10. routing and navigation
11. specialized feature workflows
12. responsive behavior
13. accessibility
14. testing
15. verification

The actual order must be derived from project dependencies rather than copied blindly from this example.

---

## 20. Verification and Testing Plan

For every acceptance requirement define:

### Verification Item
- requirement
- implementation items affected
- verification method
- test type
- expected result
- backend dependency, if any
- whether mocks are allowed or required

Include:
- routes
- navigation
- visual consistency
- feature states
- responsive behavior
- accessibility
- loading/error/disconnected states
- production build
- unit/component tests
- end-to-end tests
- linting/static checks
- unresolved backend dependencies

---

## 21. Final Acceptance Criteria

List the conditions that must be satisfied before the frontend can be considered complete.

---

## 22. Plan Summary

Provide a concise summary of:
- total planned pages
- total layouts
- shared components
- feature components
- global stores
- composables
- services
- major workflows
- blocking issues
- backend dependencies
- recommended implementation phases