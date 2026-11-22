# Name
workflow-manage-kubernetes

# Description
Use for production Kubernetes design, creation, validation, or maintenance. Local development remains Docker Compose based.

# Instructions

## Migrated contract

## Kubernetes Workflow

Use for production Kubernetes design, creation, validation, or maintenance. Local development remains Docker Compose based.

Read `.caisa/CAISA.md`, inspect implemented services and infrastructure, and prefer AWS EKS when production Kubernetes is introduced. Store resources under `infrastructure/kubernetes/`, preferably using `base/` and `overlays/staging/` and `overlays/production/` when multiple environments exist.

For implemented client, admin, API, realtime, Vision, and worker services, create only applicable Deployments, Services, ConfigMaps, external secret integration, readiness/liveness probes, resource requests/limits, rolling updates, ingress, and horizontal scaling.

Keep API, realtime, Vision, and workers independently scalable. Isolate Vision/GPU workloads so ordinary services do not require GPU nodes. Prefer managed AWS PostgreSQL and Redis rather than running them in the cluster.

Apply least-privilege IAM, private internal services where possible, restricted public ingress, and private production databases. Never store secrets in Git. Avoid unnecessary Kubernetes complexity.

Generate and validate resources first. Never perform a production deployment unless explicitly requested. Report validations, assumptions, unresolved requirements, and any separately authorized deployment step.
