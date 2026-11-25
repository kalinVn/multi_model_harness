# Name
frontend-camera

# Description
Implement or update browser camera and microphone acquisition, selection, preview, errors, and resource cleanup for training.

# Instructions

## Migrated contract

## Frontend Camera

Read `../../../claude/skills/frontend-camera.md`, then use the current Training/component contracts in repository-root `docs/frontend/`.

Keep acquisition and track cleanup in the approved composable/service owner. Expose honest idle/requesting/ready/streaming/error/stopped states, handle denied/unavailable/device-loss cases, and release resources idempotently on stop, close, route exit, and unmount.

Do not perform inference, pose estimation, object detection, coaching, or microphone upload unless a current approved contract requires it.
