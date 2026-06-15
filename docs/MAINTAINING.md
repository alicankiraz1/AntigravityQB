# Maintaining AntigravityQB

This document covers validation and release maintenance for AntigravityQB.

## Dependency-Free Repo Check

Run the default repository validation before every release:

```bash
make check
```

This checks required package files, Antigravity skill frontmatter, stale platform invocation names, release secret hygiene, archive hygiene when Git metadata is available, installer dry-runs, and the Python unit test suite. It intentionally uses only shell and Python standard-library commands.

On a normal local development machine, `make check` is expected to complete well under 30 seconds. Validator CLI smoke tests have a 30-second timeout, and any timeout or hang is a release blocker. CI pins Python 3.12 with `actions/setup-python`.

If a real key is exposed in chat, logs, docs, examples, or commits, treat it as compromised and rotate it outside the repository before release. Validation output must identify only the file, line, and pattern name; it must not print the matched secret value.

## Validate Planner Docs

The skill ships a read-only validator for generated `Planner-docs/` outputs. From an AntigravityQB repository checkout, run:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step1
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

When changing the validator, test at least:

- a valid Step 2 fixture;
- a missing-section fixture;
- a normal filename containing `sk-` such as `task-spec.yaml`;
- a fake long secret token that should be detected;
- an OpenRouter key or an `OPENROUTER_API_KEY` entry set to a real value that should be detected while placeholder values remain allowed;
- roadmap table extraction with historical phase references such as `Faz 0B-10` or `Phase 11`;
- optional `Autopsy.md` validation when present, and no failure when it is absent;
- Step 4 readiness gating for missing audit, `BLOCKED`, `PASS`, `PASS_WITH_WARNINGS`, and prose such as `no P0/P1 findings`.

Run:

```bash
python3 -m unittest discover -s tests -v
```

## Release Flow

1. Update `skills/antigravityqb/SKILL.md` and references as needed.
2. Update `skills/antigravityqb/references/repo-aware-intake.md` if Step 1 intake behavior changes.
3. Update `skills/antigravityqb/references/Autopsy-Planner.md` if Step 1.5 autopsy behavior changes.
4. Update `skills/antigravityqb/references/Fourth-Planner.md` if implementation handoff behavior changes.
5. Update `skills/antigravityqb/scripts/validate_planner_docs.py` if planner structure or readiness gates change.
6. Run `make check`.
7. Install into a disposable project with `scripts/install.sh --scope ide-project --target "$(mktemp -d)" --dry-run`.
8. Preview the Antigravity app cache install with `scripts/install.sh --scope app-global --dry-run`.
9. Manually install to the desired Antigravity scope when ready.
10. Start a new Antigravity conversation or task before testing.

## Sanitized Export

Do not create release zips with Finder or generic directory compression, because ignored files such as `.git/`, `__pycache__/`, `.env`, `artifacts/`, `logs/`, or `tmp/` can be included.

Use the tracked-file export target when this folder is inside a Git checkout:

```bash
make export-sanitized
```

This writes `AntigravityQB-sanitized.zip` with `git archive`. The default `make check` gate validates archive contents when Git metadata is available and skips that archive check explicitly when this folder is being edited as a non-Git export.

## Contribution Guidelines

- Keep the skill concise.
- Keep long planner prompts in `references/`.
- Preserve the `Planner-docs/*Planing*` filenames required by the bundled prompts.
- Do not add MCP servers, hooks, or generated assets unless validation is updated accordingly.
- Do not put secrets or environment-specific credentials into docs, planner prompts, or examples.
