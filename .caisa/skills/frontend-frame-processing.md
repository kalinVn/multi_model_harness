## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

None

# Name
frontend-frame-processing

# Description
Implement lightweight, bounded camera-frame preparation for transport without browser-side inference.

# Instructions

## Migrated contract

## Frontend Frame Processing

Read `../../../claude/skills/frontend-frame-processing.md` and the current Live Analysis WebSocket contract.

Own controlled capture, resize, JPEG encoding/compression, pacing, cancellation, and backpressure. Keep rate, dimensions, and quality configurable from approved requirements; drop stale work instead of building an unbounded queue.

Send the documented metadata and binary JPEG pair without interleaving. Do not perform AI inference or invent production tuning values without measurement.
