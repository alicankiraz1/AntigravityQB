---
name: antigravityqb
description: Vibecoding-first Antigravity planning with autopsy, ontology, ledger memory, helper-agent-aware QA, and gated handoff.
---

# AntigravityQB

## Overview

Run the bundled planning workflow for a project repository. Keep Step 1 conversational and repo-aware, run Step 1.5 Autopsy for existing projects, and hand off Step 2 and Step 3 as text-only Antigravity task prompts unless the user explicitly asks for a different flow. After Step 3, provide a gated Step 4 implementation handoff prompt only when the audit says implementation can begin.

The bundled prompts are:

- `references/First-Planner.md` for Step 1 main planning.
- `references/Autopsy-Planner.md` for Step 1.5 existing-project autopsy.
- `references/Second-Planner.md` for Step 2 phase sub-planning.
- `references/Third-Planner.md` for Step 3 sub-plan QA and coverage audit.
- `references/Fourth-Planner.md` for the Step 4 implementation Antigravity task handoff prompt template.

Planning behavior references:

- `references/vibecoding-principles.md` for adaptive, small-slice, validation-first planning.
- `references/task-delegation-playbook.md` for safe helper-agent/task delegation and role boundaries.
- `references/planning-ledger.md` for durable plan/implementation history via `Planner-docs/Planing-Ledger.md`.
- `references/project-ontology.md` for durable project vocabulary, entities, workflows, boundaries, and invariants.
- `references/assessment-and-budget.md` for autonomy, Antigravity task, token/context, and budget assessment.
- `references/engineering-principles.md` for domain-appropriate CS, architecture, validation, and secure engineering methods.

Bundled support files:

- `scripts/validate_planner_docs.py` for read-only structural validation of `Planner-docs/`.
- `references/repo-aware-intake.md` for evidence-backed Step 1 intake questions.
- `references/workflow-quality.md` for Antigravity task reliability, validation, token discipline, and handoff practices.

## Workflow Selection

1. If the user asks for normal planner startup, run Step 1.
2. If the user directly asks for Step 1.5 or Autopsy, read `references/Autopsy-Planner.md` and execute it.
3. If the user directly asks for Step 2, read `references/Second-Planner.md` and execute it.
4. If the user directly asks for Step 3, read `references/Third-Planner.md` and execute it.
5. If the user asks only for the Antigravity task prompt text, print the matching Step 2, Step 3, or gated Step 4 copy block without modifying files.

This is a native Antigravity Agent Skill workflow. Do not use legacy package-manager or migration commands for this skill.

## Step 1 Intake

Read `references/repo-aware-intake.md` before asking questions.

Before asking `PROJECT_NAME`, do a bounded, read-only repository scan so the intake can suggest evidence-backed defaults. If `Planner-docs/Planing-Ledger.md` or `Planner-docs/Project-Ontology.md` exists, read it before asking intake questions and use it as supporting history, not as unquestioned truth. Then ask these four fields one at a time in the user's language, using plain text questions only:

1. `PROJECT_NAME`: project name, with an inferred default when possible.
2. `PROJECT_INTENT`: what the project is for and what it should become, with a repo-derived draft when possible.
3. `TARGET_END_STATE`: what done looks like from product, engineering, operations, security, and user-value perspectives, with a five-part draft when possible.
4. `KNOWN_CONSTRAINTS`: team size, infrastructure, budget, timeline, preferred stack, compliance boundaries, must-use tools, must-not-use tools, desired autonomy level, human review cadence, and any token/usage budget with detected constraints and unknowns when possible.

AntigravityQB asks intake questions in the user's language when practical. Generated Planner-docs artifacts are English by default unless the user explicitly requests another body language. Required document headings remain English for validator stability.

## Vibecoding, Memory, Ontology, and Helper-Agent Behavior

AntigravityQB uses a vibecoding-first planning style: understand the repo, preserve a clear target, plan the next useful verified moves, and keep implementation slices small, reversible, and evidence-backed. Vibecoding does not relax safety, validation, secret, approval, or file-boundary rules.

Before long planning runs, read `references/vibecoding-principles.md`, `references/assessment-and-budget.md`, and `references/engineering-principles.md`. For existing projects, also read `references/planning-ledger.md` and `references/project-ontology.md`; if `Planner-docs/Planing-Ledger.md` or `Planner-docs/Project-Ontology.md` exists in the target repo, read them as evidence before replanning.

Use helper agents only when they reduce context pollution or improve evidence quality: large repo exploration, Step 1.5 Autopsy, ontology mapping, multi-phase Step 2 drafting, Step 3 readiness/security audit, or Step 4 implementation/review separation. Read `references/task-delegation-playbook.md` before requesting helper agents. Parent AntigravityQB owns final artifact writes; helper agents should gather evidence, draft options, or review unless the user explicitly asks otherwise.

Antigravity task handoffs must include the outcome, unchanged boundaries, validation checkpoints, stop gates, token/context risk, and whether helper agents are recommended.

After all four values are available:

1. Read `references/First-Planner.md`.
2. Substitute the four collected values into the matching placeholders.
3. Follow the substituted Step 1 prompt exactly.
4. Create or update only `Planner-docs/Main-Planing.md`, as required by the Step 1 prompt.
5. After completing Step 1, decide whether Step 1.5 Autopsy applies.
6. Run Step 1.5 automatically only when the repository is an existing or partially built project: it is not empty and contains meaningful evidence such as README, manifests, source/service/package directories, tests, docs, configs, or CI.
7. Skip Step 1.5 for new or nearly empty projects; do not create `Planner-docs/Autopsy.md` in that case.
8. After Step 1 and any Step 1.5 Autopsy work, ask the user in plain text whether they have feedback for the main plan and autopsy.
9. If feedback is provided, apply it under the same file boundary: update only `Planner-docs/Main-Planing.md` for main plan feedback and only `Planner-docs/Autopsy.md` for autopsy feedback.

## Step 1.5 Autopsy

Step 1.5 is for existing or partially built projects. It should not run for genuinely new or nearly empty repositories.

When Step 1.5 applies:

1. Read `references/Autopsy-Planner.md`.
2. Read `Planner-docs/Main-Planing.md`.
3. Inspect the repository with read-only commands.
4. Create or update `Planner-docs/Autopsy.md`; when enough evidence exists, also create or update `Planner-docs/Project-Ontology.md`.
5. Do not modify source files, `Planner-docs/Main-Planing.md`, or any Step 2/3 files.
6. Treat `Autopsy.md`, `Project-Ontology.md`, and any existing `Planing-Ledger.md` as Step 2 feedback, not as replacements for the main plan.

## Step 2 Handoff

After Step 1 feedback is handled, ask whether the user wants to continue to Step 2. If yes, tell the user to copy the following text, open a new Antigravity task, and send it:

```text
Use the antigravityqb skill. Run Step 2 according to references/Second-Planner.md.

Read all main phases in Planner-docs/Main-Planing.md. If Planner-docs/Autopsy.md, Planner-docs/Project-Ontology.md, or Planner-docs/Planing-Ledger.md exists, read it fully as supporting evidence and account for it in the sub-phase plans. Plan in a vibecoding-first style: small reversible slices, fast validation signals, explicit deferrals, security boundaries, and Antigravity task readiness. For each phase, create Faz-<n>-Plans folders and detailed Faz<n>.<m>-*.md sub-plan files under Planner-docs. Do not stop until all phases are covered. Modify only Planner-docs.
```

When executing Step 2 directly:

1. Read `references/Second-Planner.md`.
2. Read `references/workflow-quality.md`.
3. Read `Planner-docs/Autopsy.md`, `Planner-docs/Project-Ontology.md`, and `Planner-docs/Planing-Ledger.md` when they exist; do not block Step 2 when they are absent.
4. Follow repository inspection, file-boundary, naming, all-file validation, and stopping rules exactly.
5. Run the bundled validator after generation when available. When manually validating from an AntigravityQB repository checkout, use:
   `python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step2 --strict`
   If no script path is accessible, perform equivalent all-file validation and report that fallback clearly.
6. Do not modify files outside `Planner-docs/`.
7. After the Step 2 summary, print the Step 3 Antigravity task handoff block from this skill.

## Step 3 Handoff

After Step 2 is complete, ask whether the user wants to continue to Step 3. If yes, tell the user to copy the following text, open a new Antigravity task, and send it:

```text
Use the antigravityqb skill. Run Step 3 according to references/Third-Planner.md.

Audit Planner-docs/Main-Planing.md, Planner-docs/Sub-Planing-Index.md, Planner-docs/Faz-*-Plans/*.md, and any supporting Planner-docs/Autopsy.md, Planner-docs/Project-Ontology.md, or Planner-docs/Planing-Ledger.md. Analyze main-phase coverage, file naming, sequencing, required section structure, index consistency, content quality, scope drift, readiness realism, ontology consistency, planning-history continuity, security/governance, vibecoding slice quality, and Step 4 readiness. Do not fix any plan files; produce only Planner-docs/Sub-Planing-Audit.md. Do not stop until all phases and sub-plans have been reviewed.
```

When executing Step 3 directly:

1. Read `references/Third-Planner.md`.
2. Read `references/workflow-quality.md`.
3. Run the bundled validator first when available and incorporate its findings into the audit. When manually validating from an AntigravityQB repository checkout, use:
   `python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step3 --strict`
   If no script path is accessible, perform equivalent all-file validation and report that fallback clearly.
4. Follow audit, file-boundary, validation, and stopping rules exactly.
5. Modify only `Planner-docs/Sub-Planing-Audit.md`.
6. After the Step 3 summary, print the Step 4 handoff prompt from `references/Fourth-Planner.md` only if the audit permits implementation.

## Step 4 Handoff

Step 4 is not an AntigravityQB planning step and must not be executed automatically by this skill.

When Step 3 completes:

1. Read `references/Fourth-Planner.md`.
2. Run the bundled validator when available. When manually validating from an AntigravityQB repository checkout, use:
   `python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step4`
   If no script path is accessible, perform equivalent all-file validation and report that fallback clearly.
3. If validation passes, print the Step 4 Antigravity task copy block and remind the user to watch token use.
4. If validation fails because the audit is `BLOCKED` or contains P0/P1 findings, do not print the Step 4 prompt; print the minimal repair or unblock prompt instead.
5. If validation passes with non-blocking warnings, print the Step 4 prompt and state that the implementation run must keep P2/P3 warnings visible.
6. The Step 4 prompt should execute the READY/READY_WITH_WARNINGS queue continuously in small verified slices. It should not stop after the first successful slice unless a stop gate is hit.

## Quality and Validation

- Prefer `scripts/validate_planner_docs.py` over ad hoc validation scripts.
- Use `--mode step1`, `--mode autopsy`, `--mode step2`, `--mode step3`, or `--mode step4` for the active workflow step.
- Use `--strict` in Antigravity task so generic or repeated section warnings become failures.
- Do not report section counts from memory; report counts only after reading the active prompt or running validation.
- For untracked `Planner-docs/`, use `find Planner-docs -maxdepth 4 -type f | sort`, `git status --short -- Planner-docs`, and `git diff -- Planner-docs` together.
- Keep long Antigravity task stdout concise. Put detailed evidence in the generated Markdown artifacts.
- Track planning and implementation continuity through `Planner-docs/Planing-Ledger.md` when available; Step 4 should append concise implementation summaries there.

## Safety Rules

- Treat the current working directory as the project being planned.
- Inspect the repository before writing any planning file, using the safe read-only commands required by the active planner prompt.
- Do not implement product features, refactor source code, install dependencies, commit, push, deploy, or open pull requests.
- Do not write secrets, tokens, credentials, private keys, or local sensitive environment values into planning files.
- Preserve the required misspelled filenames exactly: `Main-Planing.md`, `Sub-Planing-Index.md`, and `Sub-Planing-Audit.md`.
- Preserve `Planner-docs/Autopsy.md` as the Step 1.5 autopsy filename.
- If a required source file is missing, follow the blocker behavior in the active planner prompt instead of inventing speculative output.

## Completion Reporting

For each executed step, report concisely:

- which planner step ran;
- which files were created or updated;
- whether the step succeeded or was blocked;
- the highest-priority next action;
- any uncertainty or blocker discovered.
