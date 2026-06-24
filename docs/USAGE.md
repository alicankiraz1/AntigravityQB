# Usage

artifact_schema_version: 3
handoff_contract_version: 2

AntigravityQB runs a vibecoding-first, repo-aware planning workflow with optional Step 1.5 Autopsy, project ontology, project comprehension, and planning ledger continuity for existing projects.

The workflow is planning-first. AntigravityQB creates and audits `Planner-docs/` artifacts during Steps 1-3, then prints a separate gated implementation prompt for Step 4 only when the audit allows implementation.

Optional continuity artifacts:

```text
Planner-docs/Project-Ontology.md
Planner-docs/Project-Comprehension.md
Planner-docs/Planing-Ledger.md
```

`Project-Ontology.md` preserves vocabulary, entities, workflows, boundaries, integrations, and invariants. `Project-Comprehension.md` records evidence confidence, comprehension questions, domain-to-code traces, architecture reflexion, quality scenarios, and open hypotheses. `Planing-Ledger.md` records planning runs, implementation summaries, current state snapshots, and replanning inputs so later AntigravityQB runs can understand what was planned and what was applied.

## Step 1: Main Plan

Open the project repository you want Antigravity to analyze and ask:

```text
Use the antigravityqb skill to create a main plan for this project.
```

AntigravityQB first performs a bounded read-only scan of the current repository. It may inspect files such as `README.md`, `AGENTS.md`, manifests, CI workflows, docs indexes, deployment files, tests, top-level service directories, and any existing `Planner-docs/Planing-Ledger.md`, `Planner-docs/Project-Ontology.md`, or `Planner-docs/Project-Comprehension.md`.

Then it asks four intake questions, one at a time:

- `PROJECT_NAME`: the project name.
- `PROJECT_INTENT`: what the project is for and what it should become.
- `TARGET_END_STATE`: what done looks like across product, engineering, operations, security, and user value.
- `KNOWN_CONSTRAINTS`: team, infrastructure, budget, timeline, stack, compliance, must-use tools, must-not-use tools, desired autonomy level, human review cadence, and any token/usage budget.

AntigravityQB asks intake questions in the user's language when practical. Generated Planner-docs artifacts are English by default unless the user explicitly requests another content language. Required document headings remain English for validator stability.

After the answers are collected, AntigravityQB loads `First-Planner.md`, substitutes the values, inspects the repository, and creates or updates:

```text
Planner-docs/Main-Planing.md
```

Step 1 is allowed to modify only that file.

## Step 1.5: Existing Project Autopsy

When the target repository is an existing or partially built project, AntigravityQB runs `Autopsy-Planner.md` after Step 1.

Expected output:

```text
Planner-docs/Autopsy.md
Planner-docs/Project-Ontology.md   # optional when enough evidence exists
Planner-docs/Project-Comprehension.md  # optional for non-trivial existing projects
```

The Autopsy report analyzes project sections, feature inventory, placeholders/stubs/skeletons, technical debt, missing or broken integrations, test and CI gaps, security/governance issues, operational readiness, and alignment with `Planner-docs/Main-Planing.md`. The optional ontology captures domain vocabulary, entities, workflows, boundaries, integrations, invariants, and open concept questions. The optional comprehension artifact captures confidence, CQ/TRACE/ARC links, architecture drift, quality scenarios, and open hypotheses.

Step 1.5 is skipped for empty or nearly empty repositories. In that case, `Autopsy.md` is not required and Step 2 should continue without it.

When manually validating Step 1.5 from an AntigravityQB checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode autopsy --strict
```

## Step 2: Phase Sub-Plans

After Step 1, AntigravityQB prints a text block for a new Antigravity task or conversation:

```text
Use the antigravityqb skill. Run Step 2 according to references/Second-Planner.md.

Read and return the exact canonical handoff from references/handoffs/run-step2.md, then execute it.
```

Expected outputs:

```text
Planner-docs/Sub-Planing-Index.md
Planner-docs/Faz-<n>-Plans/Faz<n>.<m>-*.md
```

`Planner-docs/Main-Planing.md` remains the primary source of truth. `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, `Planner-docs/Project-Comprehension.md`, and `Planner-docs/Planing-Ledger.md`, when present, are supporting evidence that should influence sub-plan evidence, work breakdowns, acceptance criteria, risks, ontology consistency, traceability, confidence calibration, and replanning continuity.

Step 2 uses the schema v3 planning contract for new or rewritten index and active sub-plan artifacts. The default mode is `wave`: every main phase is classified as active or deferred, active phases receive detailed sub-plan files, and deferred phases are kept visible as roadmap cards with deferral reason, activation trigger, and earliest wave. Active sub-plans include a structured `### Implementation Contract` JSON block with repo-relative path states, structured safe `argv` validation commands, dependency labels, risk domains, and security-review flags. Use `full` only when the user explicitly asks for full-project decomposition.

When manually validating from an AntigravityQB checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
```

To create local preview artifacts without starting execution, use:

```bash
python3 skills/antigravityqb/scripts/task_run.py --root /path/to/project --stage step2
```

The preview helper writes `Task-Run.json`, `Task-Prompt.md`, and `Task-Result.json` under `Planner-docs/Task-Runs/<task-run-id>/`. It records source snapshots and policy metadata, and returns BLOCKED instead of an execution prompt when prerequisites are missing.

To add local run state around that preview without executing product work:

```bash
python3 skills/antigravityqb/scripts/task_apply.py prepare --root /path/to/project --stage step2 --evidence "planner prerequisites validated"
python3 skills/antigravityqb/scripts/task_apply.py validate --run-dir /path/to/project/Planner-docs/Task-Runs/<task-run-id>
python3 skills/antigravityqb/scripts/task_apply.py finalize --run-dir /path/to/project/Planner-docs/Task-Runs/<task-run-id> --evidence "final review complete"
```

`task_apply.py` maintains `Progress.json`, append-only `Events.jsonl`, `Writer-Lock.json`, and `Result.json`. It also supports `recover-lock` for expired writer locks.

## Step 3: Sub-Plan QA Audit

After Step 2, AntigravityQB prints another text block for a new Antigravity task or conversation:

```text
Use the antigravityqb skill. Run Step 3 according to references/Third-Planner.md.

Read and return the exact canonical handoff from references/handoffs/run-step3.md, then execute it.
```

Expected output:

```text
Planner-docs/Sub-Planing-Audit.md
```

When manually validating from an AntigravityQB checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3-preflight --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
```

The task preview helper also supports Step 3:

```bash
python3 skills/antigravityqb/scripts/task_run.py --root /path/to/project --stage step3
```

## Step 4: Gated Implementation Handoff

After Step 3, AntigravityQB may print a Step 4 implementation prompt. This prompt is for a separate Antigravity implementation task; AntigravityQB itself does not implement product changes during Steps 1-3.

AntigravityQB should print the Step 4 prompt only when:

- `Planner-docs/Sub-Planing-Audit.md` exists;
- the audit status is `PASS`, or `PASS_WITH_WARNINGS` with no P0/P1 findings;
- the Step 4 validator passes.

When manually checking readiness from an AntigravityQB checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

The task preview helper supports Step 4 readiness artifact generation:

```bash
python3 skills/antigravityqb/scripts/task_run.py --root /path/to/project --stage step4
```

If the audit is `BLOCKED` or contains P0/P1 findings, repair the planning package first. If only open or accepted P2/P3 warnings remain, the implementation prompt may be used only with `PASS_WITH_WARNINGS` and the warnings should stay visible. If the audit says `NO_ACTION_REQUIRED`, Step 4 must report why there is no queue and must not start implementation.

The implementation handoff comes from `references/handoffs/run-step4.md`. It tells Antigravity to use relevant skills, project rules, helper agents when available, and security review guidance by scope; execute the READY/READY_WITH_WARNINGS queue continuously in small reversible slices; test before or with code changes; report exact blockers; avoid secrets; update `Planner-docs/Planing-Ledger.md` with concise verified-slice or stop-event summaries; and limit token use by reading the audit/index first and only the active sub-plan afterward.

The implementation task should continue to the next acceptance criterion or next queued sub-plan after each verified slice. It should stop only for explicit gates such as P0/P1 or safety/security findings, failing tests, missing required files, plan/audit/repo contradictions, approval or credential blockers, unsafe external mutations, unrelated dirty worktree state, unavailable validation with no fallback, token/context pressure, or a user stop request.

## Validation Notes

If `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, `Planner-docs/Project-Comprehension.md`, or `Planner-docs/Planing-Ledger.md` exists, the validator checks required heading order and supported semantic fields during Step 2/3/4 validation. If these optional continuity docs do not exist, Step 2/3 validation continues without treating them as required. Use `--mode autopsy --strict` after Step 1.5 when `Autopsy.md` should be required.

The validator uses stable exit codes: `0` means validation passed, `1` means document validation failed, and `2` means invocation/configuration/I/O error. With `--strict`, repeated or generic section warnings become failures except documented legacy compatibility warnings.

## Safety Expectations

AntigravityQB is not an implementation tool. It is designed to produce planning artifacts only during Steps 1-3.

If AntigravityQB finds missing source files or missing planner outputs, it should follow the blocker behavior in the active planner prompt instead of inventing speculative output.
