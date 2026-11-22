# Name
workflow-manage-devops

# Description
Use as the coordination point for delivery and infrastructure work spanning Docker, GitHub Actions, CI/CD, AWS, or Kubernetes. Inspect existing infrastructure first, preserve separate development and production environments, and keep infrastructure changes reviewable through Git.

# Instructions

## Migrated contract

## DevOps Coordination Workflow

Use as the coordination point for delivery and infrastructure work spanning Docker, GitHub Actions, CI/CD, AWS, or Kubernetes. Inspect existing infrastructure first, preserve separate development and production environments, and keep infrastructure changes reviewable through Git.

Route implementation details without duplicating their guidance:

- Read `.caisa/skills/workflow-setup-infrastructure.md` and `docs/infrastucture/docker/docker.md` for local Docker work.
- Read `.caisa/skills/workflow-setup-production.md` for CI/CD and production preparation.
- Read `.caisa/skills/workflow-manage-kubernetes.md` for Kubernetes work.
- After Docker implementation, use `.caisa/skills/workflow-testing-infrastructure.md`, then `.caisa/skills/workflow-code-review-infrastructure.md`, then `.caisa/skills/workflow-verification-infrastructure.md`.

Preserve Docker Compose for local development. Prepare production services to scale independently through container builds, a registry, Kubernetes, and AWS. Use secure GitHub-to-AWS authentication and prefer OIDC or other short-lived credentials.

Keep infrastructure work separate from application construction. Docker workflows may prepare application-service definitions before source exists, but must not scaffold application code; report unavailable services as `PENDING APPLICATION BUILD`.

Validate coordinated infrastructure changes. Keep secrets outside source control and never deploy automatically without explicit authorization.
