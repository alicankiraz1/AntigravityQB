# Usage

AntigravityQB runs a repo-aware planning workflow with an optional Step 1.5 Autopsy for existing projects.

## Step 1: Main Plan

Open the project repository you want Antigravity to analyze and ask:

```text
Use the antigravityqb skill to create a main plan for this project.
```

AntigravityQB first performs a bounded read-only scan of the current repository. It may inspect files such as `README.md`, `AGENTS.md`, manifests, CI workflows, docs indexes, deployment files, tests, and top-level service directories.

Then it asks four intake questions, one at a time:

- `PROJECT_NAME`: the project name.
- `PROJECT_INTENT`: what the project is for and what it should become.
- `TARGET_END_STATE`: what done looks like across product, engineering, operations, security, and user value.
- `KNOWN_CONSTRAINTS`: team, infrastructure, budget, timeline, stack, compliance, must-use tools, and must-not-use tools.

AntigravityQB asks intake questions in the user's language when practical. Generated Planner-docs artifacts are English by default unless the user explicitly requests another body language. Required document headings remain English for validator stability.

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
```

Step 1.5 is skipped for empty or nearly empty repositories. In that case, `Autopsy.md` is not required and Step 2 should continue without it.

## Step 2: Phase Sub-Plans

After Step 1, AntigravityQB prints a text block for a new Antigravity task or conversation:

```text
Use the antigravityqb skill. Run Step 2 according to references/Second-Planner.md.

Read all main phases in Planner-docs/Main-Planing.md. If Planner-docs/Autopsy.md exists, read it fully as a supporting feedback source and account for it in the sub-phase plans. For each phase, create Faz-<n>-Plans folders and detailed Faz<n>.<m>-*.md sub-plan files under Planner-docs. Do not stop until all phases are covered. Modify only Planner-docs.
```

Expected outputs:

```text
Planner-docs/Sub-Planing-Index.md
Planner-docs/Faz-<n>-Plans/Faz<n>.<m>-*.md
```

When manually validating from an AntigravityQB repository checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
```

## Step 3: Sub-Plan QA Audit

After Step 2, AntigravityQB prints another text block for a new Antigravity task or conversation:

```text
Use the antigravityqb skill. Run Step 3 according to references/Third-Planner.md.

Audit Planner-docs/Main-Planing.md, Planner-docs/Sub-Planing-Index.md, and Planner-docs/Faz-*-Plans/*.md. Analyze main-phase coverage, file naming, sequencing, required section structure, index consistency, content quality, scope drift, readiness realism, security/governance, and Step 4 readiness. Do not fix any plan files; produce only Planner-docs/Sub-Planing-Audit.md. Do not stop until all phases and sub-plans have been reviewed.
```

Expected output:

```text
Planner-docs/Sub-Planing-Audit.md
```

When manually validating from an AntigravityQB repository checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
```

## Step 4: Gated Implementation Handoff

After Step 3, AntigravityQB may print a Step 4 implementation prompt. This prompt is for a separate implementation task; AntigravityQB itself does not implement product changes during Steps 1-3.

AntigravityQB should print the Step 4 prompt only when:

- `Planner-docs/Sub-Planing-Audit.md` exists;
- the audit status is `PASS`, or `PASS_WITH_WARNINGS` with no P0/P1 findings;
- the Step 4 validator passes.

When manually checking readiness from an AntigravityQB repository checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

If the audit is `BLOCKED` or contains P0/P1 findings, repair the planning package first. If only P2/P3 warnings remain, the implementation prompt may be used but the warnings should stay visible.

The implementation handoff tells Antigravity to use relevant skills, project rules, and security review guidance by scope; execute the READY/READY_WITH_WARNINGS queue continuously in small reversible slices; test before or with code changes; report exact blockers; avoid secrets; and limit token use by reading the audit/index first and only the active sub-plan afterward.

The implementation task should continue to the next acceptance criterion or next queued sub-plan after each verified slice. It should stop only for explicit gates such as P0/P1 or safety/security findings, failing tests, missing required files, plan/audit/repo contradictions, approval or credential blockers, unsafe external mutations, unrelated dirty worktree state, unavailable validation with no fallback, token/context pressure, or a user stop request.

## Safety Expectations

AntigravityQB is not an implementation tool. It is designed to produce planning artifacts only.

If AntigravityQB finds missing source files or missing planner outputs, it should follow the blocker behavior in the active planner prompt instead of inventing speculative output.
