## Available Agents

- .codex/agents/code-review-infrastructure-agent.md
- .caisa/agents/code-review-infrastructure-agent.md
- .codex/agents/devops-agent.md
- .caisa/agents/devops-agent.md
- .codex/agents/kubernetes-agent.md
- .caisa/agents/kubernetes-agent.md
- .codex/agents/new-frontend-orchestrator.md
- .caisa/agents/new-frontend-orchestrator.md
- .codex/agents/testing-infrastructure-agent.md
- .caisa/agents/testing-infrastructure-agent.md
- .codex/agents/update-frontend-orchestrator.md
- .caisa/agents/update-frontend-orchestrator.md
- .codex/agents/verification-infrastructure-agent.md
- .caisa/agents/verification-infrastructure-agent.md
- config/agents/AGENTS.md

## Available Skills

- .caisa/skills/reference-claude-to-codex-map.md
- .caisa/skills/reference-frontend-architecture.md
- .caisa/skills/reference-frontend-project-structure.md
- .caisa/skills/rule-frontend-design-system.md
- .caisa/skills/rule-frontend-planning.md
- .codex/skill-adapters/configure-docker-mounts/SKILL.md
- .caisa/skills/configure-docker-mounts.md
- .codex/skill-adapters/ensure-project-directories/SKILL.md
- .caisa/skills/ensure-project-directories.md
- .codex/skill-adapters/frontend-analysis-client/SKILL.md
- .caisa/skills/frontend-analysis-client.md
- .codex/skill-adapters/frontend-auth-ui/SKILL.md
- .caisa/skills/frontend-auth-ui.md
- .codex/skill-adapters/frontend-camera/SKILL.md
- .caisa/skills/frontend-camera.md
- .codex/skill-adapters/frontend-code-architect/SKILL.md
- .caisa/skills/frontend-code-architect.md
- .codex/skill-adapters/frontend-code-quality/SKILL.md
- .caisa/skills/frontend-code-quality.md
- .codex/skill-adapters/frontend-component-builder/SKILL.md
- .caisa/skills/frontend-component-builder.md
- .codex/skill-adapters/frontend-frame-processing/SKILL.md
- .caisa/skills/frontend-frame-processing.md
- .codex/skill-adapters/frontend-page-builder/SKILL.md
- .caisa/skills/frontend-page-builder.md
- .codex/skill-adapters/frontend-plan-validator/SKILL.md
- .caisa/skills/frontend-plan-validator.md
- .codex/skill-adapters/frontend-project-structure/SKILL.md
- .caisa/skills/frontend-project-structure.md
- .codex/skill-adapters/frontend-responsive-ui/SKILL.md
- .caisa/skills/frontend-responsive-ui.md
- .codex/skill-adapters/frontend-routing/SKILL.md
- .caisa/skills/frontend-routing.md
- .codex/skill-adapters/frontend-subscription-ui/SKILL.md
- .caisa/skills/frontend-subscription-ui.md
- .codex/skill-adapters/frontend-training-overlay/SKILL.md
- .caisa/skills/frontend-training-overlay.md
- .codex/skill-adapters/infrastructure-git-safety/SKILL.md
- .caisa/skills/infrastructure-git-safety.md
- .codex/skill-adapters/plan-new-frontend/SKILL.md
- .caisa/skills/plan-new-frontend.md
- .codex/skill-adapters/update-existing-frontend-design/SKILL.md
- .caisa/skills/update-existing-frontend-design.md
- .codex/skills/debug-frontend-plan/SKILL.md
- .caisa/skills/debug-frontend-plan.md
- .codex/skills/frontend-component-builder-debug/SKILL.md
- .caisa/skills/frontend-component-builder-debug.md
- .codex/skills/frontend-debug-component-builder/SKILL.md
- .caisa/skills/frontend-debug-component-builder.md
- .codex/skills/frontend-layout-builder-debug/SKILL.md
- .caisa/skills/frontend-layout-builder-debug.md
- .codex/skills/frontend-page-builder-debug/SKILL.md
- .caisa/skills/frontend-page-builder-debug.md
- .codex/skills/frontend-plan-validator.md
- .codex/skills/frontend-project-structure.md
- .codex/skills/google-auth-service-debug/SKILL.md
- .caisa/skills/google-auth-service-debug.md
- .codex/skills/plan-new-frontend.md
- .codex/skills/vite-dev-environment/SKILL.md
- .caisa/skills/vite-dev-environment.md
- .codex/workflows/code-review-infrastructure.md
- .caisa/skills/workflow-code-review-infrastructure.md
- .codex/workflows/frontend-planning.md
- .caisa/skills/workflow-frontend-planning.md
- .codex/workflows/manage-devops.md
- .caisa/skills/workflow-manage-devops.md
- .codex/workflows/manage-kubernetes.md
- .caisa/skills/workflow-manage-kubernetes.md
- .codex/workflows/new-frontend.md
- .caisa/skills/workflow-new-frontend.md
- .codex/workflows/setup-infrastructure.md
- .caisa/skills/workflow-setup-infrastructure.md
- .codex/workflows/setup-production.md
- .caisa/skills/workflow-setup-production.md
- .codex/workflows/testing-infrastructure.md
- .caisa/skills/workflow-testing-infrastructure.md
- .codex/workflows/update-frontend.md
- .caisa/skills/workflow-update-frontend.md
- .codex/workflows/verification-infrastructure.md
- .caisa/skills/workflow-verification-infrastructure.md

## Available Rules

- .caisa/CAISA.md
- .codex/configuration/project.md
- .codex/rules/frontend-design-system.md
- .codex/rules/frontend-planning.md
- AGENTS.md

## Available Documents

- .codex/commands/build_frontend.md
- .caisa/commands/build_frontend.md
- .codex/commands/debug_frontend_plan.md
- .caisa/commands/debug_frontend_plan.md
- .codex/commands/frontend_debug_component_builder.md
- .caisa/commands/frontend_debug_component_builder.md
- .codex/commands/frontend_debug_page_builder.md
- .caisa/commands/frontend_debug_page_builder.md
- .codex/commands/frontend_debug_page_builder_upgrade.md
- .caisa/commands/frontend_debug_page_builder_upgrade.md
- .codex/commands/setup_infrastructure.md
- .caisa/commands/setup_infrastructure.md
- .codex/commands/setup_production.md
- .caisa/commands/setup_production.md
- .codex/commands/update_frontend.md
- .caisa/commands/update_frontend.md
- .codex/references/claude-to-codex-map.md
- .codex/references/frontend-architecture.md
- .codex/references/frontend-project-structure.md
- .caisa/commands/document_project_structure.md
- .codex/README.md

# Codex to Caisa Migration

This report records the repository-local Markdown migration. Original Codex files remain unchanged.

## Format Decisions

- YAML frontmatter was converted to Caisa H1 sections.
- Nested Codex skills were flattened to `.caisa/skills/<name>.md`.
- Workflows, rules, and references were represented as skills because Caisa has no separate runtime schema for them.
- Codex UI metadata was preserved inside the related skill, but Caisa has no equivalent UI metadata contract.
- Agent role files reference their migrated workflow through Caisa's `# Skills` contract.
- Commands with owning workflows embed those workflows in `# Instructions`.
- Native Codex `$skill` discovery and collaboration-agent spawning have no direct Caisa equivalent. Skills are loaded into `SkillRegistry`; migrated agents reference workflow skills explicitly. Caisa does not automatically dispatch ordinary user messages to those agents.
- Command arguments remain present in the original user message, but the current command context builder does not expose a separate structured arguments field.

## Known Conflict and Missing Sources

The existing `.caisa/CAISA.md` describes an artist application. The Codex tree describes a Tennis frontend and references absent `claude/`, `docs/frontend/`, `docs/infrastucture/`, `frontend/`, and `source/debug/frontend/` sources. The migration preserves those contracts but does not invent the missing authorities. Any migrated command, agent, or skill requiring them must report a blocker. Existing Caisa project context remains authoritative until that conflict is resolved explicitly.

## Source Map

| Original | Caisa file | Type | Status |
| --- | --- | --- | --- |
| `.codex/agents/code-review-infrastructure-agent.md` | `.caisa/agents/code-review-infrastructure-agent.md` | agent | migrated with workflow skill |
| `.codex/agents/devops-agent.md` | `.caisa/agents/devops-agent.md` | agent | migrated with workflow skill |
| `.codex/agents/kubernetes-agent.md` | `.caisa/agents/kubernetes-agent.md` | agent | migrated with workflow skill |
| `.codex/agents/new-frontend-orchestrator.md` | `.caisa/agents/new-frontend-orchestrator.md` | agent | migrated with workflow skill |
| `.codex/agents/testing-infrastructure-agent.md` | `.caisa/agents/testing-infrastructure-agent.md` | agent | migrated with workflow skill |
| `.codex/agents/update-frontend-orchestrator.md` | `.caisa/agents/update-frontend-orchestrator.md` | agent | migrated with workflow skill |
| `.codex/agents/verification-infrastructure-agent.md` | `.caisa/agents/verification-infrastructure-agent.md` | agent | migrated with workflow skill |
| `.codex/commands/build_frontend.md` | `.caisa/commands/build_frontend.md` | command | migrated |
| `.codex/commands/debug_frontend_plan.md` | `.caisa/commands/debug_frontend_plan.md` | command | migrated |
| `.codex/commands/frontend_debug_component_builder.md` | `.caisa/commands/frontend_debug_component_builder.md` | command | migrated |
| `.codex/commands/frontend_debug_page_builder.md` | `.caisa/commands/frontend_debug_page_builder.md` | command | migrated |
| `.codex/commands/frontend_debug_page_builder_upgrade.md` | `.caisa/commands/frontend_debug_page_builder_upgrade.md` | command | migrated |
| `.codex/commands/setup_infrastructure.md` | `.caisa/commands/setup_infrastructure.md` | command | migrated |
| `.codex/commands/setup_production.md` | `.caisa/commands/setup_production.md` | command | migrated |
| `.codex/commands/update_frontend.md` | `.caisa/commands/update_frontend.md` | command | migrated |
| `.codex/configuration/project.md` | `.caisa/CAISA.md` | project instructions | merged with conflict note |
| `.codex/references/claude-to-codex-map.md` | `.caisa/skills/reference-claude-to-codex-map.md` | skill | migrated |
| `.codex/references/frontend-architecture.md` | `.caisa/skills/reference-frontend-architecture.md` | skill | migrated |
| `.codex/references/frontend-project-structure.md` | `.caisa/skills/reference-frontend-project-structure.md` | skill | migrated |
| `.codex/rules/frontend-design-system.md` | `.caisa/skills/rule-frontend-design-system.md` | skill | migrated |
| `.codex/rules/frontend-planning.md` | `.caisa/skills/rule-frontend-planning.md` | skill | migrated |
| `.codex/skill-adapters/configure-docker-mounts/SKILL.md` | `.caisa/skills/configure-docker-mounts.md` | skill | migrated |
| `.codex/skill-adapters/ensure-project-directories/SKILL.md` | `.caisa/skills/ensure-project-directories.md` | skill | migrated |
| `.codex/skill-adapters/frontend-analysis-client/SKILL.md` | `.caisa/skills/frontend-analysis-client.md` | skill | migrated |
| `.codex/skill-adapters/frontend-auth-ui/SKILL.md` | `.caisa/skills/frontend-auth-ui.md` | skill | migrated |
| `.codex/skill-adapters/frontend-camera/SKILL.md` | `.caisa/skills/frontend-camera.md` | skill | migrated |
| `.codex/skill-adapters/frontend-code-architect/SKILL.md` | `.caisa/skills/frontend-code-architect.md` | skill | migrated |
| `.codex/skill-adapters/frontend-code-quality/SKILL.md` | `.caisa/skills/frontend-code-quality.md` | skill | migrated |
| `.codex/skill-adapters/frontend-component-builder/SKILL.md` | `.caisa/skills/frontend-component-builder.md` | skill | migrated |
| `.codex/skill-adapters/frontend-frame-processing/SKILL.md` | `.caisa/skills/frontend-frame-processing.md` | skill | migrated |
| `.codex/skill-adapters/frontend-page-builder/SKILL.md` | `.caisa/skills/frontend-page-builder.md` | skill | migrated |
| `.codex/skill-adapters/frontend-plan-validator/SKILL.md` | `.caisa/skills/frontend-plan-validator.md` | skill | migrated |
| `.codex/skill-adapters/frontend-project-structure/SKILL.md` | `.caisa/skills/frontend-project-structure.md` | skill | migrated |
| `.codex/skill-adapters/frontend-responsive-ui/SKILL.md` | `.caisa/skills/frontend-responsive-ui.md` | skill | migrated |
| `.codex/skill-adapters/frontend-routing/SKILL.md` | `.caisa/skills/frontend-routing.md` | skill | migrated |
| `.codex/skill-adapters/frontend-subscription-ui/SKILL.md` | `.caisa/skills/frontend-subscription-ui.md` | skill | migrated |
| `.codex/skill-adapters/frontend-training-overlay/SKILL.md` | `.caisa/skills/frontend-training-overlay.md` | skill | migrated |
| `.codex/skill-adapters/infrastructure-git-safety/SKILL.md` | `.caisa/skills/infrastructure-git-safety.md` | skill | migrated |
| `.codex/skill-adapters/plan-new-frontend/SKILL.md` | `.caisa/skills/plan-new-frontend.md` | skill | migrated |
| `.codex/skill-adapters/update-existing-frontend-design/SKILL.md` | `.caisa/skills/update-existing-frontend-design.md` | skill | migrated |
| `.codex/skills/debug-frontend-plan/SKILL.md` | `.caisa/skills/debug-frontend-plan.md` | skill | migrated |
| `.codex/skills/debug-frontend-plan/agents/openai.yaml` | `.caisa/skills/debug-frontend-plan.md` | skill metadata | embedded; no native Caisa UI metadata |
| `.codex/skills/frontend-component-builder-debug/SKILL.md` | `.caisa/skills/frontend-component-builder-debug.md` | skill | migrated |
| `.codex/skills/frontend-debug-component-builder/SKILL.md` | `.caisa/skills/frontend-debug-component-builder.md` | skill | migrated |
| `.codex/skills/frontend-layout-builder-debug/SKILL.md` | `.caisa/skills/frontend-layout-builder-debug.md` | skill | migrated |
| `.codex/skills/frontend-page-builder-debug/SKILL.md` | `.caisa/skills/frontend-page-builder-debug.md` | skill | migrated |
| `.codex/skills/frontend-plan-validator.md` | `.caisa/skills/frontend-plan-validator.md` | skill | migrated |
| `.codex/skills/frontend-project-structure.md` | `.caisa/skills/frontend-project-structure.md` | skill | migrated |
| `.codex/skills/google-auth-service-debug/SKILL.md` | `.caisa/skills/google-auth-service-debug.md` | skill | migrated |
| `.codex/skills/plan-new-frontend.md` | `.caisa/skills/plan-new-frontend.md` | skill | migrated |
| `.codex/skills/vite-dev-environment/SKILL.md` | `.caisa/skills/vite-dev-environment.md` | skill | migrated |
| `.codex/workflows/code-review-infrastructure.md` | `.caisa/skills/workflow-code-review-infrastructure.md` | skill | migrated |
| `.codex/workflows/frontend-planning.md` | `.caisa/skills/workflow-frontend-planning.md` | skill | migrated |
| `.codex/workflows/manage-devops.md` | `.caisa/skills/workflow-manage-devops.md` | skill | migrated |
| `.codex/workflows/manage-kubernetes.md` | `.caisa/skills/workflow-manage-kubernetes.md` | skill | migrated |
| `.codex/workflows/new-frontend.md` | `.caisa/skills/workflow-new-frontend.md` | skill | migrated |
| `.codex/workflows/setup-infrastructure.md` | `.caisa/skills/workflow-setup-infrastructure.md` | skill | migrated |
| `.codex/workflows/setup-production.md` | `.caisa/skills/workflow-setup-production.md` | skill | migrated |
| `.codex/workflows/testing-infrastructure.md` | `.caisa/skills/workflow-testing-infrastructure.md` | skill | migrated |
| `.codex/workflows/update-frontend.md` | `.caisa/skills/workflow-update-frontend.md` | skill | migrated |
| `.codex/workflows/verification-infrastructure.md` | `.caisa/skills/workflow-verification-infrastructure.md` | skill | migrated |
| `AGENTS.md` | `.caisa/CAISA.md` | project instructions | merged |
| `codex_promt_commands` | `.caisa/commands/document_project_structure.md` | command | adapted from legacy prompt |
| `config/agents/AGENTS.md` | — | empty project instruction | skipped: empty |
| `.codex/README.md` | `.caisa/MIGRATION.md` | documentation | represented by this report |
