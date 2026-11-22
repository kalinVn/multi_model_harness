# CAISA.md

# Tennis AI Coach

## Purpose

Tennis AI Coach is a commercial subscription-based platform that observes a tennis player through a camera and provides low-latency coaching through headphones.

caisa must:
1. Read this file before significant work.
2. Inspect existing code before modifying it.
3. Load only documentation relevant to the current task.
4. Use specialized agents when appropriate.
5. Preserve existing architecture unless change is justified.

Detailed knowledge belongs in `docs/`, `.caisa/agents/`, `.caisa/rules/`, and `.caisa/skills/`.

---

## Architecture

Core realtime pipeline:

```text
Camera
→ Vision Engine
→ Structured State
→ Coach Engine
→ Instruction
→ Audio
```

Vision answers: **What is happening?**

Coach Engine answers: **What should the player do?**

Keep perception and coaching logic separate.

Major domains:

- Client
- Admin
- API / Auth / Payments
- Realtime
- Vision
- Coach Engine
- Training
- Analysis
- Audio

---

## Technology

Frontend:
- Vue 3
- ES6
- Vue Router
- Vite
- `vite.config.ts` — development server and build configuration
- Pinia — state management
- HTML5
- CSS3 / SCSS
- HTML5 Canvas API — video overlays, pose landmarks, trajectories and visual feedback
- pixi.js
- MediaDevices API — camera access
- ESLint — static code analysis and code-quality rules
- Prettier — code formatting
- Vitest — unit and component tests
- Playwright — end-to-end and browser testing

Backend:
- Python
- FastAPI
- Pydantic

Data:
- PostgreSQL
- SQLAlchemy + Alembic
- Redis
- S3-compatible object storage

Platform:
- WebSockets
- Stripe
- Docker + Docker Compose
- kubernetes
- aws
- github action

Authentication:
- Email/password
- Google
- Apple
- 2FA



Do not replace core technologies without justification.

---

## Docker


Docker configuration belongs in:

`infrastructure/docker/`

Detailed instructions:

`docs/infrastructure/docker.md`

---

## Realtime & AI

Latency is a first-class requirement.

Use lightweight ML models primarily for perception:

- pose
- ball
- racket
- court

Prefer deterministic algorithms where practical for:

- tracking
- geometry
- trajectory
- rally state
- stroke state
- coaching decisions

Do not put an LLM in the per-frame realtime path.

Never fabricate vision data or coaching decisions when confidence is insufficient.

---

## Security & Data

Never commit secrets or expose credentials.

Never store plaintext passwords.

Authorization must be enforced server-side.

Stripe webhooks must be verified and idempotent.

PostgreSQL is the persistent source of truth.

Redis is for cache and temporary/realtime state.

Large videos and binary files belong in object storage.

---

## Agents

Agents live in `.caisa/agents/`.

Use the appropriate specialized agent for each task.

Core agents cover:

- architecture
- frontend
- backend
- auth
- database
- payments
- admin
- vision
- realtime
- tennis coaching
- training
- analysis
- audio
- security
- testing
- performance
- devops
- kubernetes
- ci/cd

Infrastructure agents:
- Testing Infrastructure Agent
- Verification Infrastructure Agent
- Code Review Infrastructure Agent


Agents must respect domain boundaries and shared contracts.

---

## Commands

Commands live in `.caisa/commands/`.

Primary commands:

- `/build-up`
- `/update-app`
- `/analyze-project`
- `/code-review`
- `/refactor`
- `/fix-errors`
- `/run-tests`
/

`/build-up` orchestrates major implementation work.

`/update-app` applies changes to the existing application.
- `/setup-infrastructure`
- `/setup-production`
---

## Context

Load context progressively:

```text
caisa.md
→ Task
→ Relevant Agent
→ Relevant Rules / Skills
→ Relevant Docs
→ Relevant Code
```

Never load the entire documentation tree unnecessarily.

---

## Development Rules

Before implementation:

- understand the task
- inspect existing code
- identify affected domains
- load relevant context

After implementation:

- validate contracts
- run relevant tests
- check security
- check realtime performance when applicable
- update affected documentation

Never rewrite unrelated working code.

Never disable tests just to make a build pass.

Fix root causes.

---

## Priorities

Prioritize:

**Correctness → Security → Latency → Reliability → Maintainability → Scalability → Cost**

Prefer:

**simple → measurable → tested → improved**

Build a production system, not a demo.
