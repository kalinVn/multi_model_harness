## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/integration-contracts.md

# Name
frontend-auth-ui

# Description
Implement frontend login, registration, OAuth entry, MFA, logout, and protected-route UI against backend-owned authentication contracts.

# Instructions

## Migrated contract

## Frontend Authentication UI

Read `../../../claude/skills/frontend-auth-ui.md`, then use the Authentication section of repository-root `docs/frontend/integration-contracts.md` and current page/component contracts.

Keep the access token in memory and refresh credentials in Secure HttpOnly cookies. Submit provider reCAPTCHA tokens, use backend-owned OAuth start/callback flows, show only offered MFA methods, and distinguish `401`, `403`, network-unavailable, and terminal session states.

Never store secrets/provider tokens in frontend storage or treat hidden routes as authorization.
