## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- docs/frontend/integration-contracts.md

# Name
frontend-subscription-ui

# Description
Implement subscription, hosted checkout, verified return states, and customer-portal UI without handling privileged payments in the browser.

# Instructions

## Migrated contract

## Frontend Subscription UI

Read `../../../claude/skills/frontend-subscription-ui.md`, then follow the current Checkout and billing contract in repository-root `docs/frontend/integration-contracts.md`.

Initial subscription truth comes from `UserStore`. Start checkout only through the documented backend endpoint using `planId`, redirect to its returned provider URL, and verify return state through the backend. Treat pending/final/error states explicitly and keep retries cancellable.

Never send payment amounts or raw card credentials, infer payment success from a redirect/query string, expose provider secrets, or call the webhook.
