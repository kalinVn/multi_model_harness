# Docker Infrastructure

## Purpose

Define the Docker architecture and requirements for the Tennis AI Coach local development environment.

This document is the source of truth for Docker infrastructure.

Operational setup and rebuild logic belongs in:

`claude/commands/setup-infrastructure.md`

The equivalent Codex execution workflow is:

`codex/workflows/setup-infrastructure.md`

## Services

The local environment must provide:

* `client` — Vue 3 user application
* `admin` — Vue 3 admin application
* `api` — FastAPI backend
* `postgres` — PostgreSQL database
* `redis` — cache and realtime state

Add only when implemented:

* `realtime`
* `vision`
* `worker`

Each major application component must run as an independent service.

Do not create one all-in-one application container.

PostgreSQL and Redis alone do not constitute a complete local development environment.

## Local Project Directories

Use fixed host-side development directories:

```text
frontend/
admin/
backend/
```

Map them to services as follows:

```text
frontend/ → client
admin/    → admin
backend/  → api
```

Infrastructure setup must ensure these directories exist.

Creating these directories does not mean generating application source code.

Real Vue and FastAPI source is created by separate application build workflows.

## Development Bind Mounts

During development, mount local source directories into their corresponding containers.

Required mapping:

```text
frontend/ → client:/usr/share/nginx/html/frontend
admin/    → admin:/usr/share/nginx/html/admin
backend/  → api:/app
```

Bind mounts are development-only source mounts.

The container-side paths must remain consistent between:

* Dockerfiles
* Docker Compose
* Nginx configuration

Changes made locally must become visible inside the corresponding development container.

Changes created inside mounted paths must persist back to the host directory.

## Nginx

The `client` and `admin` services use Nginx for HTTP serving.

Nginx configuration must be managed as Docker infrastructure.

### Client

Mounted frontend files must be available under:

`/usr/share/nginx/html/frontend`

Nginx must be configured to serve the client application from that location.

### Admin

Mounted admin files must be available under:

`/usr/share/nginx/html/admin`

Nginx must be configured to serve the admin application from that location.

### Vue Routing

When Vue Router history mode is used, configure Nginx fallback behavior so application routes resolve to the corresponding `index.html`.

Do not return a 404 for valid client-side routes.

### Consistency

Nginx configuration, Docker Compose bind mounts, and Dockerfiles must agree on the same filesystem paths.

Infrastructure setup must generate or update the required Nginx configuration when those paths change.

## Container Architecture

Expected topology:

```text
Browser
   │
   ├──→ client
   │       └──→ api
   │
   └──→ admin
           └──→ api

api
 ├──→ postgres
 └──→ redis
```

The browser runs on the host machine.

It accesses application containers through published localhost ports.

## Placeholder Services

The Docker environment must remain runnable before real application source exists.

When `frontend/`, `admin/`, or `backend/` does not yet contain runnable application source, use infrastructure-only placeholders.

Placeholder source belongs under:

```text
infrastructure/docker/placeholders/
├── client/
├── admin/
└── api/
```

Placeholders must not be copied into the real host-side source directories.

When real application source becomes available, use it instead of the placeholder.

The API placeholder must provide:

`/health`

## Data Volumes

Application source services use development bind mounts.

Data services use Docker named volumes.

PostgreSQL must use a persistent named volume, for example:

```text
postgres_data
```

Redis may use a named volume such as:

```text
redis_data
```

when persistence is required.

Never use application source bind mounts for PostgreSQL or Redis data.

Persistent PostgreSQL data must survive normal infrastructure rebuilds.

## Images

Use lightweight official Linux images.

Prefer:

* Nginx-compatible image for `client`
* Nginx-compatible image for `admin`
* Python slim image for `api`
* official PostgreSQL image
* official Redis image

Do not use a full Ubuntu image unless actual system dependencies require it.

Use multi-stage production builds where useful.

## Docker Files

Docker infrastructure belongs under:

```text
infrastructure/docker/
```

Expected files include:

```text
infrastructure/docker/
├── Dockerfile.client
├── Dockerfile.admin
├── Dockerfile.api
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── nginx/
│   ├── client.conf
│   └── admin.conf
└── placeholders/
    ├── client/
    ├── admin/
    └── api/
```

Add additional Dockerfiles only when additional services are implemented.

Also maintain where required:

```text
.dockerignore
.env.example
.gitignore
```

## Development

`docker-compose.dev.yml` must support:

* required services
* source bind mounts
* Nginx configuration
* hot reload when supported by the real application workflow
* Docker networking
* service dependencies
* readable logs
* health checks
* persistent PostgreSQL data
* required localhost port mappings

Git remains the source of truth for source code.

Containers are disposable execution environments.

Persistent data and host source directories are not disposable.

## Networking

Use Docker service names for internal communication.

Expected relationships:

```text
client → api
admin → api
api → postgres
api → redis
```

Never hardcode container IP addresses.

PostgreSQL and Redis must remain private in production.

## Ports and Browser Access

Actual development port numbers belong in Docker Compose configuration.

Do not duplicate fixed port numbers in this document.

Verification must read actual published ports and report exact browser URLs.

## Infrastructure Git Safety

Local infrastructure setup must create or safely update the root `.gitignore`.

Preserve valid existing and user-defined rules.

Add missing protections idempotently.

Never replace the file wholesale when merging rules is sufficient.

Protect:

* local environment files
* secrets
* credentials
* private keys
* SSH private keys
* private certificates
* credential directories
* `node_modules`
* Node caches and build output
* Python virtual environments
* Python caches
* test caches
* coverage output
* logs
* temporary files
* local runtime data
* IDE-local files
* OS-generated files

Patterns must not hide:

* application source
* project documentation
* Dockerfiles
* Docker Compose files
* required infrastructure configuration
* `.env.example`

`.env` and `.env.*` must be ignored while `.env.example` remains trackable.

During setup, inspect filenames and Git tracking status for potentially sensitive files.

Report paths only.

Never read, print, stage, delete, or expose sensitive contents.

## Persistence Safety

Infrastructure rebuilds must preserve:

* PostgreSQL named volumes
* required Redis volumes
* `frontend/`
* `admin/`
* `backend/`
* `.env`
* application source
* unrelated Docker resources

Never remove persistent resources automatically.

## Development vs Production

Keep development and production configuration separate.

Development may use:

* bind mounts
* development ports
* debugging

Production must:

* use production builds
* avoid development source mounts
* expose only required ports
* keep services independently deployable

## Vision / GPU

Vision infrastructure remains separate from the API.

GPU support is optional and isolated to Vision.

The rest of the application must not require GPU support.

## Workflow Coordination

Claude and Codex infrastructure workflows must use this document as the Docker source of truth.

After infrastructure changes, run:

1. infrastructure testing
2. infrastructure code review
3. infrastructure verification

Verify actual configuration and runtime state rather than assuming values.

## Rules

* Use Linux containers.
* Keep services independent.
* Keep development and production separate.
* Use bind mounts for development application source.
* Use Nginx for client/admin HTTP serving.
* Keep Nginx paths consistent with Docker mounts.
* Use named volumes for persistent service data.
* Preserve local source directories.
* Prefer lightweight official images.
* Keep secrets outside images.
* Preserve PostgreSQL data.
* Keep PostgreSQL and Redis private in production.
* Keep placeholders separate from real application source.
* Replace placeholders with real applications when source becomes available.
* Never report unverified runtime state.

## Goal

Provide a reproducible local Docker environment containing:

`client + admin + api + postgres + redis`

with:

```text
frontend/ → client:/usr/share/nginx/html/frontend
admin/    → admin:/usr/share/nginx/html/admin
backend/  → api:/app
```

and Nginx configured consistently to serve the mounted client and admin applications.

The same Docker architecture must be used consistently by both Claude and Codex.
