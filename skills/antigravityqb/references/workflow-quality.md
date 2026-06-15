# AntigravityQB Workflow Quality Notes

Use these notes with the active planner prompt. They do not replace the planner
prompt; they clarify reliability practices observed from first real use.

## Read Before Reporting Counts

- Read the full active planner prompt before summarizing requirements.
- Do not report phase, sub-plan, or section counts from memory.
- Report section counts only after reading the prompt or running validation.
- Step 2 sub-plan files require 13 top-level `##` sections after the H1.

## Step 1 Repo-Aware Intake

- Run a bounded read-only repository scan before asking the four Step 1 fields.
- Use `references/repo-aware-intake.md` to infer helpful defaults, but do not treat inferred values as final until the user confirms or edits them.
- Keep the intake conversational and sequential: one plain-text question at a time.
- If the repository is empty or evidence is weak, say so and fall back to concise generic questions.
- Do not let the pre-intake scan replace the full Step 1 inspection required by `First-Planner.md`.

## Step 1.5 Autopsy

- Run Step 1.5 only for existing or partially built projects with meaningful repo evidence.
- Use `references/Autopsy-Planner.md` and write only `Planner-docs/Autopsy.md`.
- Treat `Autopsy.md` as Step 2 feedback, not as a replacement for `Main-Planing.md`.
- Skip Autopsy for new or nearly empty repositories; do not create a speculative autopsy file.
- Step 2 must read `Autopsy.md` when it exists and must not block when it is absent.

## Use The Bundled Validator

Prefer the bundled validator over ad hoc validation snippets. When manually
validating from an AntigravityQB repository checkout, use:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step2 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step3 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root . --mode step4
```

If a skill installation exposes a different active skill script path, use that
bundled validator path instead. If no script path is accessible, perform
equivalent all-file validation and state that validator execution was
unavailable.

The validator is read-only. It checks required sections, phase folders,
filename conventions, index references, duplicate numbering, missing or
unindexed files, and length-bounded secret patterns.

## Keep Antigravity Task Output Concise

- Keep stdout concise during long Antigravity task runs.
- Avoid dumping full generated files unless the user explicitly asks.
- Summarize counts, file paths, blockers, and validation status.
- Preserve detailed evidence inside the generated Markdown artifacts.

## Avoid Noisy Inline Generators

- Avoid very large inline generation scripts when normal file editing is
  practical.
- If a script is unavoidable for bulk document generation, keep it small,
  syntax-check it before use, and validate every generated file afterward.
- Do not rely on sampled reads alone; Step 2 requires all-file structure
  validation.

## Handle Untracked Planner Docs Correctly

`Planner-docs/` is often untracked during first use. `git diff -- Planner-docs`
does not show new untracked files.

Use these checks together:

```bash
find Planner-docs -maxdepth 4 -type f | sort
git status --short -- Planner-docs
git diff -- Planner-docs
```

When comparing an untracked generated file to another file, use
`git diff --no-index` only as a read-only comparison helper.

## Secret Scan Discipline

- Do not use one-character `sk-` prefix patterns; they can match normal
  filenames like `task-spec.yaml`.
- Use length-bounded token patterns such as `sk-[A-Za-z0-9_-]{20,}`.
- Do not print secret values if a secret-like pattern is detected.

## Required Step Handoffs

- Step 1 must hand off Step 2 as text for an Antigravity task.
- Step 1.5 may create `Planner-docs/Autopsy.md` before Step 2 for existing projects.
- Step 2 must finish by handing off Step 3 as text for an Antigravity task.
- Step 3 must write only `Planner-docs/Sub-Planing-Audit.md`.
- Step 3 may hand off Step 4 only after `--mode step4` validation passes.
- Step 4 is implementation work in a new Antigravity task, not a planning-file generation step.

## Step 4 Token Discipline

- Do not load all phase sub-plans at once.
- Read `Sub-Planing-Audit.md` and `Sub-Planing-Index.md` first.
- Build an ordered queue from READY and READY_WITH_WARNINGS sub-plans.
- Load only the active sub-plan and the repo files needed for the current slice.
- Continue to the next acceptance criterion or next queued sub-plan after each verified slice.
- Stop before implementation if audit contains P0/P1 findings.
- Stop during implementation on explicit stop gates such as failing tests, missing required files, approval/credential/live-environment blockers, unsafe external mutations, unrelated dirty worktree, or token/context pressure.
