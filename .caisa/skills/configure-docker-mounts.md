## Available Agents

None

## Available Skills

- .caisa/skills/workflow-setup-infrastructure.md

## Available Rules

None

## Available Documents

- docs/infrastucture/docker/docker.md

# Name
configure-docker-mounts

# Description
Configure and verify this project's development Docker bind mounts and named-volume boundaries.

# Instructions

## Migrated contract

## Configure Docker Mounts

Use repository-root `.caisa/skills/workflow-setup-infrastructure.md` and `docs/infrastucture/docker/docker.md` as authority. The shorter source at `../../../claude/skills/configure-docker-mounts.md` is compatibility context only when its paths agree with those sources.

Change development mounts only, preserve source, never mount unrelated host paths, and keep PostgreSQL on its required persistent named volume. Validate host/container paths and actual visibility, then report created/preserved mounts and volumes.
