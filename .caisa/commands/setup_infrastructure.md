# Name
setup_infrastructure

# Description
Use `.codex/workflows/setup-infrastructure.md` as the Codex-native implementation of `claude/commands/setup-infrastructure.md`.

# Tools
read_file, list_directory, write_file, bash, git

# Invocation
execute command setup_infrastructure

# Instructions
## setup_infrastructure

Use `.caisa/skills/workflow-setup-infrastructure.md` as the Codex-native implementation of `claude/commands/setup-infrastructure.md`.

Read `.caisa/CAISA.md`, `.caisa/skills/workflow-manage-devops.md`, and the Docker specification named by that workflow. Preserve the Codex workflow's stricter safety, persistence, validation, and reporting requirements. Do not invoke Claude agents or overwrite the adapted workflow with the older source text.

## Embedded Workflow Contract

## Setup Infrastructure Workflow

## Purpose

Use this workflow to create, rebuild, validate, or maintain the local Docker infrastructure for Tennis AI Coach.

This workflow manages infrastructure only. Docker architecture and service requirements come from `docs/infrastucture/docker/docker.md`; application source belongs to separate application-build workflows.

## Required Context

Before execution:

1. Read `.caisa/CAISA.md`.
2. Read `.caisa/skills/workflow-manage-devops.md`.
3. Read `docs/infrastucture/docker/docker.md`.
4. Inspect the repository and current Docker state.
5. Preserve persistent data.

The Codex-native equivalents of the Claude workflow dependencies are:

- `devops-agent` → `.caisa/skills/workflow-manage-devops.md`
- `ensure-project-directories` → the Project Directory Preparation operation in this workflow
- `infrastructure-git-safety` → the Git Safety operation in this workflow
- `configure-docker-mounts` → the Development Bind Mounts operation in this workflow
- `testing-infrastructure-agent` → `.caisa/skills/workflow-testing-infrastructure.md`
- `code-review-infrastructure-agent` → `.caisa/skills/workflow-code-review-infrastructure.md`
- `verification-infrastructure-agent` → `.caisa/skills/workflow-verification-infrastructure.md`

These are operational equivalents, not Claude agent or skill invocations. Apply their Codex workflow instructions and preserve Codex-native orchestration.

Do not load unrelated application documentation.

After implementation, use these Codex workflows in order:

1. `.caisa/skills/workflow-testing-infrastructure.md`
2. `.caisa/skills/workflow-code-review-infrastructure.md`
3. `.caisa/skills/workflow-verification-infrastructure.md`

## Responsibilities

Implement the Docker specification in `docs/infrastucture/docker/docker.md` and manage Docker infrastructure under `infrastructure/docker/`.

This may include:

- Dockerfiles
- Docker Compose files
- infrastructure-only placeholder services
- required host-side development directories
- development bind mounts
- networks
- volumes
- environment templates
- root `.gitignore` Git-safety rules
- health checks
- development ports

Do not generate real application source code. Do not invent service requirements, ports, names, or topology that are not supported by the Docker specification or inspected repository state.

## Project Directory Preparation

Ensure these host directories exist, creating only those that are missing:

```text
frontend/
admin/
backend/
```

Use them only for these service mappings:

```text
frontend/ → client
admin/    → admin
backend/  → api
```

Never delete an existing source directory, overwrite its contents, or scaffold Vue or FastAPI source. Preserve existing permissions where practical. Record which directories were found and which were created.

## Git Safety

Apply the infrastructure Git-safety requirements from `docs/infrastucture/docker/docker.md` during every setup or rebuild.

Create the root `.gitignore` when absent or merge missing rules into it when present. Preserve valid existing and user-defined entries, keep the update idempotent, and do not use broad patterns that could hide source, documentation, Docker, infrastructure, or public example configuration. Ensure `.env.example` remains trackable.

Inspect filenames and Git tracking status for potentially sensitive files. Report paths only; never read, print, stage, delete, or expose their contents. Explicitly report sensitive files that are already tracked because `.gitignore` does not untrack them.

Git-safety failure is an infrastructure validation failure. Correct unsafe ignore behavior before performing any disposable cleanup.

## Development Bind Mounts

Configure these development-only bind mounts exactly as defined by `docs/infrastucture/docker/docker.md`:

```text
frontend/ → client:/usr/share/nginx/html/frontend
admin/    → admin:/usr/share/nginx/html/admin
backend/  → api:/app
```

The shared Docker specification takes precedence over stale or conflicting path examples elsewhere. Ensure the host directories and container-side directories exist, and keep Compose, Dockerfile, and Nginx paths consistent. Do not use application-source bind mounts for PostgreSQL or Redis; use named volumes as required by the specification. Verify both host-to-container visibility and persistence of changes made within mounted paths without deleting or replacing source files.

## Nginx Configuration

Manage Nginx for `client` and `admin` as Docker infrastructure. Generate or update the relevant configuration when required so that client content is served from `/usr/share/nginx/html/frontend` and admin content from `/usr/share/nginx/html/admin`.

Ensure Dockerfiles create the required container-side directories and that Dockerfiles, Compose mounts, and Nginx roots agree. When Vue Router history mode is applicable, configure fallback to the corresponding `index.html`. Validate that Nginx can access and serve the mounted frontend and admin content. Do not make ad hoc Nginx changes outside this workflow.

## Placeholder Services

If real source code for `client`, `admin`, or `api` does not exist, create minimal infrastructure-only placeholders under:

```text
infrastructure/docker/placeholders/
├── client/
├── admin/
└── api/
```

Each placeholder must:

- build successfully
- start successfully
- expose a simple HTTP response
- remain separate from real application source

The API placeholder must provide `/health`.

When real application source exists, use it instead of the corresponding placeholder. Placeholder creation is infrastructure preparation and must not scaffold Vue, FastAPI, backend, business-logic, route, or component source in application directories.

## Complete Rebuild

For a complete rebuild:

1. Inspect and identify only this project's Docker resources.
2. Stop project containers.
3. Remove disposable project containers.
4. Remove disposable project images that must be rebuilt.
5. Recreate disposable project networks when required.
6. Preserve persistent volumes and PostgreSQL data.
7. Preserve `.env`, application source, and `frontend/`, `admin/`, and `backend/`.
8. Remove outdated generated Docker configuration when safe.
9. Regenerate Docker and Nginx configuration from the current specification.
10. Validate the generated configuration.
11. Build required images.
12. Create and start required containers.

Never use broad system-wide cleanup commands or affect unrelated Docker resources. Preserve any resource whose ownership or persistence is uncertain.

## Execution Sequence

Follow this order:

```text
Inspect
→ Plan
→ Ensure Project Directories
→ Apply Git Safety
→ Clean Disposable Project Infrastructure
→ Generate / Update Docker Configuration
→ Configure Development Mounts
→ Configure Nginx
→ Validate Configuration
→ Build Required Images
→ Create and Start Required Containers
→ Health Check
→ Infrastructure Testing
→ Infrastructure Code Review
→ Infrastructure Verification
→ Report
```

Use Linux containers, Docker service-name networking, environment configuration, dependencies, health checks, volumes, and development port mappings where applicable. PostgreSQL data must survive normal rebuilds. Redis may remain disposable unless the Docker specification explicitly requires persistence. Make all operations safe to repeat.

Ensure the host-side project directories and development bind mounts defined in `docs/infrastucture/docker/docker.md` exist and agree with the active Dockerfiles and Compose configuration. Creating required directories is infrastructure preparation; never populate them with application source.

## Safety

Never:

- delete persistent PostgreSQL data
- delete a persistent volume without explicit permission
- delete unrelated or ambiguously owned Docker resources
- overwrite `.env`
- commit or embed secrets
- overwrite valid user-defined `.gitignore` rules
- hide required source, documentation, or infrastructure configuration with broad ignore patterns
- delete or modify application source
- generate real application source code
- hide failed builds, tests, or health checks
- report false runtime state
- deploy Kubernetes, AWS infrastructure, or production services
- create or connect a GitHub repository without an explicit request

## Validation

Before reporting success, verify every currently required service defined in `docs/infrastucture/docker/docker.md`.

Verify where applicable:

- Docker configuration and expected infrastructure files
- required project directories
- required development bind mounts and exact container paths
- Nginx roots, routing fallback where applicable, and access to mounted frontend/admin files
- image builds
- container creation and startup
- health checks
- networking
- PostgreSQL
- Redis
- real application containers or infrastructure-only placeholders
- persistent data protection
- root `.gitignore` coverage and `.env.example` trackability
- filename-only sensitive-file and Git-tracking audit

Fix safe, in-scope infrastructure failures. Do not report success when a required service is missing or unhealthy, and never claim a missing or failed application service is running.

## Post-Implementation Validation

Run in this order:

1. Use `.caisa/skills/workflow-testing-infrastructure.md` to test the resulting Docker environment, including required placeholders where real application source is unavailable. For this setup workflow, successfully created placeholders are required runnable services and must be tested rather than reported as `PENDING APPLICATION BUILD`.
2. Use `.caisa/skills/workflow-code-review-infrastructure.md` to review only infrastructure created or modified by this workflow.
3. Use `.caisa/skills/workflow-verification-infrastructure.md` to verify actual runtime state and provide exact manual developer instructions.

Never invent ports, URLs, container names, image names, or health status.

## Report

Report briefly:

- files created, regenerated, or modified
- project directories created or preserved
- Docker and Nginx files created, regenerated, or modified
- development bind mounts created or preserved
- disposable project containers and images removed
- images built
- containers created and running
- networks created
- persistent volumes preserved
- `.gitignore` rules added or preserved
- potentially sensitive files detected and whether they are tracked
- per-service and overall health status
- infrastructure testing result
- infrastructure code review result
- infrastructure verification result
- actual exposed ports
- actual browser URLs
- actual API URL
- actual health URL
- status command
- logs command
- start command
- stop command
- rebuild command
- unresolved errors
- required manual actions

## Scope

This workflow manages local Docker infrastructure only. It must not:

- create real Vue applications
- create real FastAPI applications
- deploy Kubernetes
- deploy AWS infrastructure
- deploy production services

## Final Rule

`docs/infrastucture/docker/docker.md` defines what the Docker environment must contain.

This workflow defines how that environment is created, rebuilt, validated, tested, reviewed, and verified.

When real `client`, `admin`, or `api` source is unavailable, use infrastructure-only placeholders rather than blocking Docker setup.
