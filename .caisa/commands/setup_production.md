# Name
setup_production

# Description
Use `.codex/workflows/setup-production.md` as the Codex-native implementation of `claude/commands/setup-production.md`.

# Tools
read_file, list_directory, write_file, bash, git

# Invocation
execute command setup_production

# Instructions
## setup_production

Use `.caisa/skills/workflow-setup-production.md` as the Codex-native implementation of `claude/commands/setup-production.md`.

This command prepares production configuration only. It never authorizes a live deployment. Read `.caisa/CAISA.md` and the linked DevOps/Kubernetes workflows, preserve secret and production safety, and report actual validation results.

## Embedded Workflow Contract

## Setup Production Workflow

Use to prepare or maintain production configuration. This workflow does not authorize a live deployment.

Read `.caisa/CAISA.md` and `.caisa/skills/workflow-manage-devops.md`, then inspect existing infrastructure and implemented services. Read `.caisa/skills/workflow-manage-kubernetes.md` for Kubernetes work and `.caisa/skills/workflow-setup-infrastructure.md` for production Docker changes. Load only relevant documentation.

Prepare only required resources in `.github/workflows/`, `infrastructure/kubernetes/`, production Docker configuration, deployment scripts, and environment templates. The target flow is:

```text
GitHub → CI → production images → container registry → Kubernetes → AWS
```

Provide pull-request CI and protected merge/release flows for building images, publishing to a registry, and deploying. Keep production deployment gated. Use secure GitHub-to-AWS authentication and prefer OIDC or other short-lived credentials; keep infrastructure changes reviewable through Git.

Validate workflow syntax, production builds, Kubernetes resources, required variables, secret handling, and health configuration. Never commit secrets, destroy production resources, expose databases publicly, bypass failed CI, replace working infrastructure unnecessarily, or deploy without explicit authorization.

Report created and modified files, production readiness, missing credentials/configuration, unresolved issues, and the next deployment step.
