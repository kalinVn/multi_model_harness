from pathlib import Path
import re

from markdown_it import MarkdownIt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODEX_ROOT = PROJECT_ROOT / ".codex"
CAISA_ROOT = PROJECT_ROOT / ".caisa"

SKILL_DESCRIPTIONS = {
    "frontend-plan-validator": "Independently validate a frontend plan against its specification and authoritative references.",
    "frontend-project-structure": "Establish or review the approved physical frontend structure without scaffolding unrelated implementation.",
    "plan-new-frontend": "Produce a complete source-backed frontend plan before frontend implementation begins."
}

AGENT_TO_WORKFLOW = {
    "code-review-infrastructure-agent": "code-review-infrastructure",
    "devops-agent": "manage-devops",
    "kubernetes-agent": "manage-kubernetes",
    "new-frontend-orchestrator": "new-frontend",
    "testing-infrastructure-agent": "testing-infrastructure",
    "update-frontend-orchestrator": "update-frontend",
    "verification-infrastructure-agent": "verification-infrastructure"
}

READ_ONLY_AGENTS = {
    "code-review-infrastructure-agent",
    "testing-infrastructure-agent",
    "verification-infrastructure-agent"
}

COMMAND_TOOLS = {
    "debug_frontend_plan": "read_file, list_directory, write_file",
    "build_frontend": "read_file, list_directory, write_file, bash, git",
    "frontend_debug_component_builder": "read_file, list_directory, write_file, bash",
    "frontend_debug_page_builder": "read_file, list_directory, write_file, bash",
    "frontend_debug_page_builder_upgrade": "read_file, list_directory, write_file, bash",
    "setup_infrastructure": "read_file, list_directory, write_file, bash, git",
    "setup_production": "read_file, list_directory, write_file, bash, git",
    "update_frontend": "read_file, list_directory, write_file, bash, git"
}


def read_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content

    frontmatter, separator, body = content[4:].partition("\n---\n")

    if not separator:
        return {}, content

    metadata = {}

    for line in frontmatter.splitlines():
        key, separator, value = line.partition(":")

        if separator:
            metadata[key.strip()] = value.strip().strip('"')

    return metadata, body


def first_heading(content: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)

    return match.group(1).strip() if match else ""


def first_paragraph(content: str) -> str:
    _, body = read_frontmatter(content)
    body = re.sub(r"^#\s+.+?\n+", "", body, count=1)

    for paragraph in re.split(r"\n\s*\n", body):
        text = " ".join(line.strip() for line in paragraph.splitlines())

        if text and not text.startswith("#"):
            return text

    return "Migrated repository instruction."


def caisa_reference(path: str) -> str:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name

    if normalized == "AGENTS.md" or normalized.endswith("/AGENTS.md"):
        return ".caisa/CAISA.md"

    match = re.search(r"\.codex/(?:skill-adapters|skills)/([^/]+)/(?:SKILL\.md)$", normalized)
    if match:
        return f".caisa/skills/{match.group(1)}.md"

    match = re.search(r"\.codex/skills/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/skills/{match.group(1)}.md"

    match = re.search(r"\.codex/workflows/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/skills/workflow-{match.group(1)}.md"

    match = re.search(r"\.codex/rules/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/skills/rule-{match.group(1)}.md"

    match = re.search(r"\.codex/references/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/skills/reference-{match.group(1)}.md"

    match = re.search(r"\.codex/commands/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/commands/{match.group(1)}.md"

    match = re.search(r"\.codex/agents/([^/]+)\.md$", normalized)
    if match:
        return f".caisa/agents/{match.group(1)}.md"

    match = re.search(r"(?:^|/)(commands|skills|workflows|rules|references)/([^/]+)\.md$", normalized)
    if match:
        directory, stem = match.groups()

        if directory == "commands":
            return f".caisa/commands/{stem}.md"

        prefix = {"workflows": "workflow-", "rules": "rule-", "references": "reference-"}.get(directory, "")
        return f".caisa/skills/{prefix}{stem}.md"

    if name == "SKILL.md":
        parent = Path(normalized).parent.name
        return f".caisa/skills/{parent}.md"

    return path


def adapt_references(content: str) -> str:
    patterns = [
        r"(?:\.codex/)(?:skill-adapters|skills)/[^\s`\])]+/(?:SKILL\.md)",
        r"(?:\.codex/)(?:skills|workflows|rules|references|commands|agents)/[^\s`\])]+\.md",
        r"(?:\.\./)+(?:commands|skills|workflows|rules|references)/[^\s`\])]+\.md"
    ]

    for pattern in patterns:
        content = re.sub(pattern, lambda match: caisa_reference(match.group(0)), content)

    content = content.replace("`AGENTS.md`", "`.caisa/CAISA.md`")
    content = content.replace("repository-root `AGENTS.md`", "repository-root `.caisa/CAISA.md`")
    content = content.replace("`.codex/skill-adapters/`", "`.caisa/skills/`")
    content = content.replace("under `.codex/skill-adapters/`", "in `.caisa/skills/`")

    return content


def demote_top_level_headings(content: str) -> str:
    lines = content.splitlines(keepends=True)

    for token in MarkdownIt("commonmark").parse(content):
        if token.type != "heading_open" or token.tag != "h1" or token.level != 0 or token.map is None:
            continue

        line_index = token.map[0]
        line = lines[line_index]
        indentation = len(line) - len(line.lstrip())
        stripped = line[indentation:]

        if stripped.startswith("#"):
            lines[line_index] = line[:indentation] + "#" + stripped
            continue

        lines[line_index] = line[:indentation] + "## " + stripped

        if token.map[1] - token.map[0] == 2:
            lines[line_index + 1] = ""

    return "".join(lines)


def skill_document(name: str, description: str, bodies: list[tuple[str, str]]) -> str:
    parts = [f"# Name\n{name}", f"# Description\n{description}", "# Instructions"]

    for label, body in bodies:
        _, body = read_frontmatter(body)
        body = adapt_references(body.strip())
        body = demote_top_level_headings(body)
        parts.append(f"## {label}\n\n{body}")

    return "\n\n".join(parts) + "\n"


def migrate_skills() -> list[tuple[str, str, str, str]]:
    grouped: dict[str, list[tuple[str, str]]] = {}

    for source in sorted((CODEX_ROOT / "skill-adapters").glob("*/SKILL.md")):
        content = source.read_text(encoding="utf-8")
        metadata, _ = read_frontmatter(content)
        name = metadata["name"]
        grouped.setdefault(name, []).append((str(source.relative_to(PROJECT_ROOT)), content))

    for source in sorted((CODEX_ROOT / "skills").glob("*/SKILL.md")):
        content = source.read_text(encoding="utf-8")
        metadata, _ = read_frontmatter(content)
        name = metadata["name"]
        grouped.setdefault(name, []).append((str(source.relative_to(PROJECT_ROOT)), content))

    for source in sorted((CODEX_ROOT / "skills").glob("*.md")):
        content = source.read_text(encoding="utf-8")
        name = source.stem
        grouped.setdefault(name, []).append((str(source.relative_to(PROJECT_ROOT)), content))

    mappings = []
    skills_directory = CAISA_ROOT / "skills"
    skills_directory.mkdir(parents=True, exist_ok=True)

    for name, sources in sorted(grouped.items()):
        metadata = {}

        for _, content in sources:
            source_metadata, _ = read_frontmatter(content)
            metadata.update(source_metadata)

        description = metadata.get("description", SKILL_DESCRIPTIONS.get(name, first_paragraph(sources[-1][1])))
        bodies = [("Migrated contract" if len(sources) == 1 else f"Source: {source}", content) for source, content in sources]
        target = skills_directory / f"{name}.md"
        target.write_text(skill_document(name, description, bodies), encoding="utf-8")

        for source, _ in sources:
            mappings.append((source, str(target.relative_to(PROJECT_ROOT)), "skill", "migrated"))

    return mappings


def migrate_supporting_skills() -> list[tuple[str, str, str, str]]:
    mappings = []

    for source_type, prefix in (("workflows", "workflow-"), ("rules", "rule-"), ("references", "reference-")):
        for source in sorted((CODEX_ROOT / source_type).glob("*.md")):
            content = source.read_text(encoding="utf-8")
            name = f"{prefix}{source.stem}"
            description = first_paragraph(content)
            target = CAISA_ROOT / "skills" / f"{name}.md"
            target.write_text(skill_document(name, description, [("Migrated contract", content)]), encoding="utf-8")
            mappings.append((str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT)), "skill", "migrated"))

    return mappings


def migrate_agents() -> list[tuple[str, str, str, str]]:
    mappings = []
    agents_directory = CAISA_ROOT / "agents"
    agents_directory.mkdir(parents=True, exist_ok=True)

    for source in sorted((CODEX_ROOT / "agents").glob("*.md")):
        name = source.stem
        role_content = source.read_text(encoding="utf-8")
        workflow_name = AGENT_TO_WORKFLOW[name]
        tools = "read_file\nlist_directory\nbash\ngit" if name in READ_ONLY_AGENTS else "read_file\nlist_directory\nwrite_file\nbash\ngit"
        max_steps = "12" if name in READ_ONLY_AGENTS else "30"
        instructions = adapt_references(role_content.strip())
        instructions = demote_top_level_headings(instructions)
        target = agents_directory / source.name
        target.write_text(
            f"# Name\n{name}\n\n# Description\n{adapt_references(first_paragraph(role_content))}\n\n# Tools\n{tools}\n\n"
            f"# Skills\nworkflow-{workflow_name}\n\n# Max Steps\n{max_steps}\n\n# Instructions\n{instructions}\n",
            encoding="utf-8"
        )
        mappings.append((str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT)), "agent", "migrated with workflow skill"))

    return mappings


def migrate_commands() -> list[tuple[str, str, str, str]]:
    mappings = []
    commands_directory = CAISA_ROOT / "commands"
    commands_directory.mkdir(parents=True, exist_ok=True)

    for source in sorted((CODEX_ROOT / "commands").glob("*.md")):
        content = source.read_text(encoding="utf-8")
        metadata, body = read_frontmatter(content)
        name = source.stem
        description = metadata.get("description", first_paragraph(body))
        workflow_name = {
            "build_frontend": "new-frontend",
            "debug_frontend_plan": "frontend-planning",
            "setup_infrastructure": "setup-infrastructure",
            "setup_production": "setup-production",
            "update_frontend": "update-frontend"
        }.get(name)

        if workflow_name:
            workflow = (CODEX_ROOT / "workflows" / f"{workflow_name}.md").read_text(encoding="utf-8")
            body = body.strip() + "\n\n## Embedded Workflow Contract\n\n" + workflow.strip()

        body = demote_top_level_headings(adapt_references(body.strip()))
        invocation = f"execute command {name}"

        if "specification_path" in body:
            invocation += " specification_path=<repository-relative path>"

        target = commands_directory / source.name
        target.write_text(
            f"# Name\n{name}\n\n# Description\n{description}\n\n# Tools\n{COMMAND_TOOLS[name]}\n\n"
            f"# Invocation\n{invocation}\n\n# Instructions\n{body}\n",
            encoding="utf-8"
        )
        mappings.append((str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT)), "command", "migrated"))

    return mappings


def migrate_legacy_prompt_command() -> list[tuple[str, str, str, str]]:
    source = PROJECT_ROOT / "codex_promt_commands"

    if not source.is_file():
        return []

    target = CAISA_ROOT / "commands" / "document_project_structure.md"
    original = source.read_text(encoding="utf-8").strip()
    target.write_text(
        "# Name\ndocument_project_structure\n\n"
        "# Description\nInspect the current Harness source and update the project structure documentation.\n\n"
        "# Tools\nread_file, list_directory, write_file\n\n"
        "# Invocation\nexecute command document_project_structure\n\n"
        "# Instructions\nInspect `src/harness/` and summarize the current objects, responsibilities, logic, and workflow "
        "in `doc/project_structure.md`. Include an architecture schema based on files that actually exist. "
        "Do not rely on stale structure documentation without verifying the repository.\n\n"
        f"## Original Prompt\n\n{original}\n",
        encoding="utf-8"
    )

    return [("codex_promt_commands", ".caisa/commands/document_project_structure.md", "command", "adapted from legacy prompt")]


def migrate_project_context() -> list[tuple[str, str, str, str]]:
    caisa_path = CAISA_ROOT / "CAISA.md"
    current = caisa_path.read_text(encoding="utf-8").rstrip()
    agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8").rstrip()
    project_adapter = (CODEX_ROOT / "configuration" / "project.md").read_text(encoding="utf-8").rstrip()
    marker = "# Migrated Repository Instructions"

    if marker in current:
        current = current.split(marker, 1)[0].rstrip()

    migrated = (
        f"{current}\n\n{marker}\n\n"
        "The existing artist-application context above remains authoritative. The Codex configuration also contains "
        "Tennis/frontend contracts whose referenced `claude/` and `docs/frontend/` sources are absent from this repository. "
        "Those contracts are available as Caisa commands, agents, and skills, but must stop with a clear blocker when their "
        "required source files are missing; they do not override the project context above.\n\n"
        "## Repository Python Rules\n\n"
        f"{agents}\n\n"
        "## Codex Project Adapter\n\n"
        f"{adapt_references(project_adapter)}\n"
    )
    caisa_path.write_text(migrated, encoding="utf-8")

    return [
        ("AGENTS.md", ".caisa/CAISA.md", "project instructions", "merged"),
        (".codex/configuration/project.md", ".caisa/CAISA.md", "project instructions", "merged with conflict note")
    ]


def migrate_metadata() -> list[tuple[str, str, str, str]]:
    source = CODEX_ROOT / "skills" / "debug-frontend-plan" / "agents" / "openai.yaml"
    target = CAISA_ROOT / "skills" / "debug-frontend-plan.md"
    content = target.read_text(encoding="utf-8").rstrip()
    metadata = source.read_text(encoding="utf-8").strip()
    target.write_text(f"{content}\n\n## Former Codex Interface Metadata\n\n```yaml\n{metadata}\n```\n", encoding="utf-8")

    return [(str(source.relative_to(PROJECT_ROOT)), str(target.relative_to(PROJECT_ROOT)), "skill metadata", "embedded; no native Caisa UI metadata")]


def write_report(mappings: list[tuple[str, str, str, str]]) -> None:
    rows = ["| Original | Caisa file | Type | Status |", "| --- | --- | --- | --- |"]
    rows.extend(f"| `{source}` | `{target}` | {file_type} | {status} |" for source, target, file_type, status in mappings)
    rows.extend([
        "| `config/agents/AGENTS.md` | — | empty project instruction | skipped: empty |",
        "| `.codex/README.md` | `.caisa/MIGRATION.md` | documentation | represented by this report |"
    ])
    report = """# Codex to Caisa Migration

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

""" + "\n".join(rows) + "\n"
    (CAISA_ROOT / "MIGRATION.md").write_text(report, encoding="utf-8")


def main() -> None:
    mappings = []
    mappings.extend(migrate_project_context())
    mappings.extend(migrate_skills())
    mappings.extend(migrate_supporting_skills())
    mappings.extend(migrate_agents())
    mappings.extend(migrate_commands())
    mappings.extend(migrate_legacy_prompt_command())
    mappings.extend(migrate_metadata())
    write_report(sorted(mappings))


if __name__ == "__main__":
    main()
