## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

None

# Name
frontend-training-overlay

# Description
Render source-supported structured training analysis over the displayed camera preview with correct coordinate mapping.

# Instructions

## Migrated contract

## Frontend Training Overlay

Read `../../../claude/skills/frontend-training-overlay.md`, then restrict rendering to fields actually supported by the current backend contract and active plan.

Keep overlay rendering separate from camera capture, frame preparation, transport, inference, and coaching decisions. Map coordinates against displayed video dimensions/aspect ratio, represent low-confidence or missing data honestly, and clean up rendering resources.

Do not implement items listed only as future possibilities.
