# Name
frontend-analysis-client

# Description
Implement the frontend transport boundary for live training sessions and structured backend analysis events.

# Instructions

## Migrated contract

## Frontend Analysis Client

Read `../../../claude/skills/frontend-analysis-client.md`, then follow repository-root `docs/frontend/integration-contracts.md` and the Training workflow in repository-root `docs/frontend/frontend.md`.

Keep connection, frame transmission, structured event reception, errors, disconnect, stop, and approved reconnect behavior outside UI components. Use only the backend-issued authenticated WebSocket URL and the active `sessionId`.

Never fabricate observations/advice, add replay semantics, or move inference/coaching/TTS generation into the browser.
