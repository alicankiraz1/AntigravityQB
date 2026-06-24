# Maintaining AntigravityQB

artifact_schema_version: 3
handoff_contract_version: 2

This document covers validation and release maintenance for AntigravityQB.

## Dependency-Free Repo Check

Run the default repository validation before every release:

```bash
make check
```

This checks required package files, Antigravity skill frontmatter, stale platform invocation names, vibecoding/ontology/ledger/task-delegation wiring, release secret hygiene in Git checkouts, package secret hygiene in Gitless exports, archive hygiene in Git checkouts, package hygiene in Gitless exports, installer dry-runs, and the Python unit test suite. It intentionally uses only shell and Python standard-library commands.

On a normal local development machine, `make check` is expected to complete well under 30 seconds. Validator CLI smoke tests have a 30-second timeout, and any timeout or hang is a release blocker. CI pins Python 3.12 with `actions/setup-python`.

If a real key is exposed in chat, logs, docs, examples, or commits, treat it as compromised and rotate it outside the repository before release. Validation output must identify only the file, line, and pattern name; it must not print the matched secret value.

## Validate Planner Docs

The skill ships a read-only validator for generated `Planner-docs/` outputs. From an AntigravityQB repository checkout, run:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step1
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode autopsy --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3-preflight --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

When changing the validator, test at least:

- a valid Step 2 fixture;
- schema v3 frontmatter and Planning Scope Manifest validation for Step 2 artifacts;
- wave-mode deferred roadmap cards without detailed folders for deferred phases;
- active sub-plan Implementation Contracts rejecting unsafe paths and mutating validation commands in strict mode;
- `task_run.py` preview artifacts for READY and BLOCKED stage prerequisites without executing product work;
- `task_apply.py` prepare, validate, finalize, append-only event log, and expired writer-lock recovery behavior;
- legacy schema v2 Step 2 artifacts reporting migration warnings in strict mode;
- a missing-section fixture;
- a normal filename containing `sk-` such as `task-spec.yaml`;
- a fake long secret token that should be detected;
- an OpenRouter key or an `OPENROUTER_API_KEY` entry set to a real value that should be detected while placeholder values remain allowed;
- roadmap table extraction with historical phase references such as `Faz 0B-10` or `Phase 11`;
- `--mode autopsy` requiring `Autopsy.md`;
- `step3-preflight` validating Step 2 artifacts before `Sub-Planing-Audit.md` exists;
- optional `Autopsy.md`, `Project-Ontology.md`, `Project-Comprehension.md`, and `Planing-Ledger.md` validation when present, and no failure when optional continuity docs are absent;
- Ledger v2 headings with `Plan Snapshot Registry` and `Sub-Plan Status Matrix`, while legacy v1 ledgers remain accepted outside strict Step 4 execution with a deprecation warning;
- Step 4 readiness gating for missing audit, headings-only audit, `BLOCKED`, `PASS`, `PASS_WITH_WARNINGS`, NO_ACTION_REQUIRED, unsafe readiness paths, duplicate conflicting rows, and prose such as `no P0/P1 findings`.

Run:

```bash
python3 -m unittest discover -s tests -v
```

For task preview helper changes, also verify that generated `Task-Run.json`, `Task-Prompt.md`, and `Task-Result.json` stay inside `Planner-docs/Task-Runs/`, include source snapshot and policy digests, and report BLOCKED when stage prerequisites are missing.

For run-state helper changes, verify that `Progress.json`, `Events.jsonl`, `Writer-Lock.json`, and `Result.json` stay inside the same task-run directory, validation rejects missing or malformed state files, and `recover-lock` only succeeds for available or expired locks.

## Release Flow

1. Update `skills/antigravityqb/SKILL.md` and references as needed.
2. Update `skills/antigravityqb/references/repo-aware-intake.md` if Step 1 intake behavior changes.
3. Update `skills/antigravityqb/references/Autopsy-Planner.md` if Step 1.5 autopsy behavior changes.
4. Update `skills/antigravityqb/references/Fourth-Planner.md` if implementation handoff behavior changes.
5. Update `skills/antigravityqb/references/handoffs/` when Antigravity task handoff contracts change.
6. Update `skills/antigravityqb/references/vibecoding-principles.md`, `task-delegation-playbook.md`, `planning-ledger.md`, `project-ontology.md`, `project-comprehension-methods.md`, `probe-policy.md`, `assessment-and-budget.md`, or `engineering-principles.md` when planning behavior changes.
7. Update `skills/antigravityqb/scripts/validate_planner_docs.py` if planner structure, continuity docs, or readiness gates change.
8. Run `make check`.
9. Install into a disposable project with `scripts/install.sh --scope ide-project --target "$(mktemp -d)" --dry-run`.
10. Preview the Antigravity app cache install with `scripts/install.sh --scope app-global --dry-run`.
11. Manually install to the desired Antigravity scope when ready.
12. Start a new Antigravity conversation or task before testing.

## Task Handoff and Replanning Memory Checks

When changing replanning behavior, verify that `Planing-Ledger.md`, `Project-Ontology.md`, and `Project-Comprehension.md` are read as supporting evidence and never treated as stronger than current repository state or explicit user intent.

When changing Step 4 behavior, verify that the prompt:

- continues through the READY/READY_WITH_WARNINGS queue after verified slices;
- reports NO_ACTION_REQUIRED without starting implementation when no work is queued;
- appends concise ledger summaries when file writes are allowed;
- records confirmed or contradicted `Project-Comprehension.md` hypotheses when relevant;
- keeps P0/P1 gates blocking;
- states whether helper agents/tasks are useful or unnecessary;
- keeps exact blocker reporting and token/context stop gates.

## Sanitized Export

Do not create release zips with Finder or generic directory compression, because ignored files such as `.git/`, `__pycache__/`, `.env`, `artifacts/`, `logs/`, or `tmp/` can be included.

Use the tracked-file export target when this folder is inside a Git checkout:

```bash
make export-sanitized
```

This writes `AntigravityQB-sanitized.zip` with `git archive`, requires a clean index/worktree, and prefixes archive contents with `AntigravityQB/`. The default `make check` gate validates archive contents when Git metadata is available. In an extracted or copied package without `.git`, `make check` falls back to filesystem package hygiene and package secret hygiene; that fallback does not claim tracked-file or archive guarantees.

Before claiming release readiness, extract the archive to a temporary directory and run:

```bash
ANTIGRAVITYQB_VALIDATE_SKIP_UNITTESTS=1 bash scripts/validate.sh
```

Local install parity should exclude generated Python caches:

```bash
rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' skills/antigravityqb/ ~/.gemini/config/plugins/antigravityqb/skills/antigravityqb/
diff -ru -x __pycache__ skills/antigravityqb ~/.gemini/config/plugins/antigravityqb/skills/antigravityqb
```

## Contribution Guidelines

- Keep the skill concise.
- Keep long planner prompts in `references/`.
- Preserve the `Planner-docs/*Planing*` filenames required by the bundled prompts.
- Do not add MCP servers, hooks, or generated assets unless validation is updated accordingly.
- Do not put secrets or environment-specific credentials into docs, planner prompts, or examples.
