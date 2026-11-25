# Name
debug_frontend_plan

# Description
Run the normal new-frontend planning process, save its English plan and a Bulgarian translation, then STOP. This command never authorizes implementation.

# Tools
read_file, list_directory, write_file

# Invocation
execute command debug_frontend_plan specification_path=<repository-relative path>

# Instructions
## debug_frontend_plan

Run the normal new-frontend planning process, save its English plan and a Bulgarian translation, then STOP. This command never authorizes implementation.

## Invocation

Use the repository skill:

```text
$debug-frontend-plan specification_path=docs/frontend/frontend.md
```

Or explicitly ask Codex:

```text
Run .caisa/commands/debug_frontend_plan.md with specification_path=<path>.
```

`debug_frontend_plan` is the command name; `debug-frontend-plan` is its Codex skill adapter. A repository `.codex/commands/` Markdown file alone does not register a native slash command. The discovery link under `.agents/skills/` makes the adapter available without changing user-wide Codex configuration.

## Input and Execution

- Receive an explicit `specification_path`, resolving it from the repository root. A task/prototype must be supplied through, or associated with, that specification, as in the normal build command. The example path above is not a fallback when input is absent.
- Read the root `.caisa/CAISA.md`, planning rules (`.caisa/skills/rule-frontend-planning.md`), and planning workflow (`.caisa/skills/workflow-frontend-planning.md`). Execute that workflow completely, including its independent plan-validation gate and bounded corrections.
- Read required source and specification files without changing them. Resolve and verify referenced prototype paths. Detailed UI implementation analysis remains out of scope, but prototype directory/file organization explicitly referenced by `docs/frontend/frontend.md` for project-structure guidance may be inspected read-only. Do not call the original full build orchestrator: its post-validation steps implement the frontend.
- The only repository writes allowed during command execution are the two output files below and creation of their parent directory. Do not create application directories, scaffold code, install dependencies, run builders, change configuration, fix inspected code, commit, or deploy. Planning future implementation/tests is allowed; executing them is not.

## Output Contract

Use these literal paths relative to the repository root:

```text
docs/debug_plan_outputs/new_frontend_plan_N.md
docs/debug_plan_outputs/new_frontend_plan_BG.md
```

These paths intentionally override the normal planner destination `docs/frontend/plan/new-frontend-plan.md` for this debug-only command. Do not create or update the canonical plan file during a debug run.

`N` is literal, not a counter. Each execution replaces this pair with the current run's English report and translation; it does not create additional history files. Preserve unrelated files and do not run two executions against this fixed pair concurrently.

Both files contain the same complete plan and execution record. If planning is blocked, save the source-supported partial plan or an explicit blocked planning report in both languages; never fabricate a successful plan to satisfy file creation. Filesystem failures must be reported with the actual written/missing paths, not concealed as success.

## Terminal Boundary

After saving and checking both files, report their paths, validation status, correction attempts, warnings/blockers, and translation checks. State that implementation was not started, then end the turn. Do not invoke implementation steps, automatically continue, or request implementation approval as the next step of this command. Implementation requires a separate later user request.

## Embedded Workflow Contract

## New Frontend Planning — Debug Execution

This is the planning prefix of `claude/agents/new-frontend-orchestrator.md` (Steps 1–3), with the original planner and validator contracts adapted for Codex. Its terminal artifact/translation phase replaces every implementation step. The coordinator runs the planner role itself and uses a separate agent for validation; a Claude-specific agent registry is not required.

## 1. Establish the Run

- Receive the explicit `specification_path` from debug_frontend_plan (`.caisa/commands/debug_frontend_plan.md`). Follow its write boundary for this entire run, including delegated work.
- Record the starting repository status in memory so pre-existing edits are not attributed to this run. Keep run evidence in memory until the two final artifacts are written; no additional repository trace files.
- Load planning rules (`.caisa/skills/rule-frontend-planning.md`), the supplied specification, and the required references selected by that specification. Missing input/source, unresolved conflicts, or unavailable required evidence stop the planning/validation phase; continue to artifact publication with an honest blocked report.

## 2. Generate the English Plan

- Execute Plan New Frontend (`.caisa/skills/plan-new-frontend.md`) as the planner role, applying architecture context (`.caisa/skills/reference-frontend-architecture.md`). Do not replace it with an example or shortened debug-only planner.
- Preserve its complete Output Contract: Frontend Type (`new`), Project Structure, Open Questions and Blockers, and Build Order. For Project Structure, read `docs/frontend/frontend.md`, resolve the structure documents and examples referenced by its `Project Structure` section, and add only plan-specific ownership, supporting files, or concrete placement needed for implementation. Do not reproduce authoritative trees or general placement rules. Include the source-required design foundation, layouts, pages/routes/access, shared/feature components, ownership, dependencies, responsive/accessibility states, and acceptance/test requirements needed for the validator and future builders. Use subsections/tables as appropriate; do not invent requirements solely to populate a template.
- Resolve and verify referenced prototype paths and record their specification-declared page/component/state mappings. Detailed UI implementation analysis remains downstream work; only prototype organization explicitly referenced by `docs/frontend/frontend.md` for structural guidance may be inspected for ownership, grouping, and complex-component support files. Identify source-backed decisions from the authoritative specifications, reusable resources verified on disk, planned new paths, and unresolved dependencies. Do not claim visual/runtime verification during planning.
- Return a complete English plan. No project directories or implementation files are created. The planner's normal canonical destination is `docs/frontend/plan/new-frontend-plan.md`, but this debug workflow overrides it: do not write that file here; the coordinator saves only the validated debug artifacts below. Implementation skill selection remains outside this planning command, as in the source planner.

## 3. Independently Validate and Correct

- Spawn a separate read-only validation agent using Frontend Plan Validator (`.caisa/skills/frontend-plan-validator.md`). Supply the original `specification_path`, the complete latest English plan, active project/task constraints, the planning rules, and access to raw referenced sources. Instruct it to read those sources independently and return its structured result without edits. Do not coach it toward a desired verdict.
- A valid result requires `status: valid`, empty `errors`, and an exact unchanged `validated_plan`. Retain warnings. An invalid result requires actionable errors and `validated_plan: null`.
- On invalid results, give the planner the original specification, rejected plan, and errors. Generate a complete corrected plan and validate it independently again. Permit at most two corrections after the initial validation: three validator invocations total. Do not reset this counter or alter a valid plan after the gate without revalidation.
- Stop the correction loop immediately for missing required material, a necessary user decision, a failed/absent/malformed result, or unavailable independent-agent capability. Do not silently self-validate or mark an unvalidated plan valid. Save the latest draft with blocked status and the exact limitation. If all three results are invalid, report remaining errors and attempts used.
- Even a valid result does not permit project-structure creation or any implementation step. Continue only to saving and translation.

## 4. Save the English Artifact

Write `docs/debug_plan_outputs/new_frontend_plan_N.md` in English. Use a Markdown report containing:

1. **Execution Record:** command, explicit specification path (or missing input), outcome (`valid`, `invalid`, or `blocked`), validator invocations, correction attempts, source paths/locations actually inspected, relevant source precedence/overrides, and the concrete evidence behind architectural decisions. Report findings/decisions, not hidden reasoning or invented execution logs.
2. **Frontend Implementation Plan:** the complete final validated plan unchanged, or the latest unvalidated/rejected draft clearly labeled. If no draft could be produced, say why and list what source material is required; do not invent an example plan.
3. **Validation Findings:** all unresolved errors, non-blocking warnings, and unavailable checks with source locations and required resolution. Distinguish plan validity from future implementation tests, which have not run.
4. **Stop Status:** planning only; no implementation started.

The execution envelope is not part of `validated_plan`; do not represent report metadata added after validation as a modification of the approved plan. Do not repeat the complete plan inside the validator-result metadata.

## 5. Translate the Saved English Artifact

- Read the exact saved English file and translate it into Bulgarian at `docs/debug_plan_outputs/new_frontend_plan_BG.md`. The English artifact is the sole content source for translation; do not rerun planning or independently derive decisions from prototypes/specifications.
- Preserve heading levels/order, sections, list numbering/nesting, table dimensions/row order, all steps, decisions, warnings, blockers, qualifications, and meaning. Translate narrative headings/text while retaining the same structure.
- Preserve file paths, URLs/link destinations, identifiers, class/component names, API names, technical terminology, inline code, fenced code, configuration keys, literal statuses, numeric values/units, and file-tree/code examples exactly. Use natural Bulgarian for surrounding prose; do not rename technical entities or add explanations absent from English.
- Do not summarize, omit, reorder, add, or silently correct the plan in translation. If an English-plan correction is necessary, return through validation within the same bounded budget and regenerate the translation from the newly saved English artifact. Corrections limited to translation do not change the English plan.

## 6. Check the Pair and STOP

- Check both saved files are present, nonempty, and belong to this run, rather than leaving a previous Bulgarian report paired with a new English one.
- Compare heading/list/table structure, numbered steps, code blocks, inline technical tokens, links, paths, numeric values, architecture decisions, and all findings. Perform a semantic translation review; structural checks alone cannot prove equivalence.
- Recheck repository changes against the starting status. Only the two output files may change during this execution; report any unexpected edits without overwriting or reverting user work.
- Report paths, actual planning/validation outcome, attempts, remaining findings, and translation checks. If saving/translation fails, explicitly report the incomplete pair and never claim success.
- **STOP.** Never proceed to original orchestrator Step 4 (Establish Project Structure) or any subsequent build/integration/testing/implementation phase. A Build Order in the plan is future work, not an instruction to execute now.

```text
Task / Prototype via explicit specification_path
→ Frontend Planning (real planner + relevant architecture context)
→ Generate New Frontend Plan
→ Independent Validation ↔ bounded Planner Corrections
→ Save English Plan
→ Translate Same Saved Plan to Bulgarian
→ Save Bulgarian Plan
→ Verify Pair
→ STOP
```
