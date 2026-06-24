# AntigravityQB

**Vibecoding-first repo planning for Google Antigravity.**

artifact_schema_version: 2
handoff_contract_version: 1

AntigravityQB is a Google Antigravity Agent Skill that turns an existing repository into a durable planning package. It inspects the project, asks a small set of high-signal intake questions, writes structured planning documents, audits those documents, and finally produces a gated implementation handoff prompt for a separate Antigravity task.

The plugin is designed for serious project work where plans need to survive long context windows, implementation needs clear acceptance criteria, and the agent should not start changing product code before the planning package is complete.

AntigravityQB is the Antigravity-native edition of a repo-aware planning workflow built around Markdown-based stable planning, validation controls, durable project memory, and controlled implementation handoff. It is meant to reduce context drift in long tasks without turning the planning skill itself into an implementation agent.

## Current Release

Current release: `0.2.1`.

This release brings AntigravityQB to the current QB-family planning contract:

- `artifact_schema_version: 2` and `handoff_contract_version: 1`;
- optional `Planner-docs/Project-Comprehension.md` for evidence confidence, CQ/TRACE/ARC links, architecture reflexion, quality scenarios, and validation probes;
- canonical Antigravity task handoffs in `skills/antigravityqb/references/handoffs/`;
- `step3-preflight` validation before `Sub-Planing-Audit.md` exists;
- Ledger v2 support with strict Step 4 migration checks for legacy ledgers;
- semantic Step 4 readiness parsing, `NO_ACTION_REQUIRED`, finding status checks, and unsafe path rejection;
- deterministic fixture corpus checks under `evals/`.

## Development Plan

The next Antigravity-native adaptation plan is tracked in [antigravity-gelistirme2506.md](antigravity-gelistirme2506.md). The stable public release remains `0.2.1`; the plan separates future 0.3.x work from the install and validation instructions below.

Planned 0.3.x work should stay Antigravity-native while adding:

- schema v3 and handoff v2 planning metadata;
- adaptive `wave` and `full` Step 2 planning;
- structured implementation contracts with safe `argv` validation commands;
- policy-digest style run safety checks;
- local run artifacts that avoid vendor-specific paths, commands, and agent APIs.

## What It Does

AntigravityQB creates a planning workflow around the repository you already have open:

- **Repo-aware intake:** reads the current project before asking questions, then proposes practical defaults for project name, intent, target state, and constraints.
- **Project Autopsy + Ontology + Comprehension:** existing projects get a focused `Autopsy.md` report and may get `Project-Ontology.md` plus `Project-Comprehension.md` to capture vocabulary, evidence confidence, CQ/TRACE/ARC links, architecture reflexion, quality scenarios, and open validation probes.
- **Durable planning memory:** writes Markdown files under `Planner-docs/` so the plan, ontology, and implementation ledger can be reviewed, versioned, shared, resumed, and audited.
- **Phase decomposition:** expands a main plan into ordered phase folders and detailed sub-plan files.
- **Quality audit:** checks coverage, sequencing, structure, readiness, ontology consistency, planning-history continuity, security/governance concerns, vibecoding slice quality, and implementation preparedness.
- **Gated Step 4 handoff:** prints a separate implementation prompt only when the audit says implementation can begin; canonical Antigravity task handoffs live under `references/handoffs/`.
- **Queue-continuation semantics:** Step 4 builds an ordered READY/READY_WITH_WARNINGS queue, keeps going through verified slices until a real stop gate is hit, and asks the implementation run to append concise summaries to `Planing-Ledger.md`.
- **Task delegation guidance:** recommends bounded helper agents/tasks only when they reduce context pollution, improve evidence quality, or separate implementation from review.
- **Planning-only guardrails:** keeps P0/P1 audit gates, secret/token hygiene, file boundaries, and implementation safety rules visible at the skill level.
- **Dependency-free validation:** ships a Python standard-library validator and a `make check` release gate.

AntigravityQB is intentionally vibecoding-first: it keeps the target vision clear, reads the repository's real shape, avoids fake certainty, and plans the next useful verified moves instead of freezing unnecessary implementation detail too early. Vibecoding never relaxes safety, secret handling, approval, validation, or file-boundary rules.

## Why Use It

AntigravityQB is useful when a project is too large for a single ad hoc prompt and too important for vague planning notes. It gives Antigravity a repeatable workflow:

1. Understand the repository first.
2. Ask only the questions needed to lock direction.
3. Write a main plan.
4. Audit the current project when it already exists.
5. Break the plan into implementation-ready sub-plans.
6. Audit the full planning package.
7. Hand implementation to a separate Antigravity task with explicit gates.

This keeps planning, auditing, and implementation separate. The result is less drift, clearer stop conditions, and planning files that can be validated outside the chat.

## Requirements

- Google Antigravity IDE or Antigravity CLI.
- Python 3 for the bundled planner validator.
- A fresh Antigravity conversation or task after installation so the skill list refreshes.
- No third-party Python packages are required for validation.

## Installation

Clone the repository:

```bash
git clone https://github.com/alicankiraz1/AntigravityQB.git
cd AntigravityQB
```

Install into the Antigravity app global plugin cache:

```bash
scripts/install.sh --scope app-global --force
```

Update all local global Antigravity scopes:

```bash
scripts/install.sh --scope app-global --force
scripts/install.sh --scope ide-global --force
scripts/install.sh --scope cli-global --force
```

Install into one Antigravity IDE project:

```bash
scripts/install.sh --scope ide-project --target /path/to/project
```

Install globally for Antigravity IDE:

```bash
scripts/install.sh --scope ide-global
```

Install into one Antigravity CLI project:

```bash
scripts/install.sh --scope cli-project --target /path/to/project
```

Install globally for Antigravity CLI:

```bash
scripts/install.sh --scope cli-global
```

Preview any install without copying files:

```bash
scripts/install.sh --scope ide-project --target /path/to/project --dry-run
```

## Installation Targets

AntigravityQB is distributed as a skill folder:

```text
skills/antigravityqb/
  SKILL.md
  scripts/
  references/
```

The installer copies that folder into one of the supported Antigravity skill locations:

| Scope | Destination |
| --- | --- |
| `app-global` | `~/.gemini/config/plugins/antigravityqb/skills/antigravityqb` |
| `ide-project` | `/path/to/project/.agents/skills/antigravityqb` |
| `ide-global` | `~/.agents/skills/antigravityqb` |
| `cli-project` | `/path/to/project/.agent/skills/antigravityqb` |
| `cli-global` | `~/.gemini/antigravity-cli/skills/antigravityqb` |

Manual installation is also possible by copying `skills/antigravityqb/` to one of those destinations.

## Quick Start

Open Antigravity in the repository you want to plan and ask:

```text
Use the antigravityqb skill to inspect this repo and plan this project.
```

AntigravityQB will perform a bounded read-only scan, ask four intake questions, then create the first planning artifact:

```text
Planner-docs/Main-Planing.md
```

The `Planing` spelling is intentionally preserved because the bundled prompts and validator use these exact filenames.

## Workflow

| Step | Purpose | Output |
| --- | --- | --- |
| Step 1 | Repository scan, intake questions, and master plan creation. | `Planner-docs/Main-Planing.md` |
| Step 1.5 | Existing-project autopsy plus optional ontology and comprehension capture when the repo is already built or partially built. | `Planner-docs/Autopsy.md`, optional `Planner-docs/Project-Ontology.md`, optional `Planner-docs/Project-Comprehension.md` |
| Step 2 | Full phase and sub-plan generation. | `Planner-docs/Sub-Planing-Index.md`, `Planner-docs/Faz-*-Plans/*.md` |
| Step 3 | Read-only QA audit of the planning package. | `Planner-docs/Sub-Planing-Audit.md` |
| Step 4 | Copy-ready implementation handoff prompt for a separate task and optional implementation ledger updates. | Text prompt only, optional `Planner-docs/Planing-Ledger.md` updates |

### Step 1: Main Plan

AntigravityQB scans the repository and asks:

- `PROJECT_NAME`
- `PROJECT_INTENT`
- `TARGET_END_STATE`
- `KNOWN_CONSTRAINTS`

AntigravityQB asks intake questions in the user's language when practical. Generated Planner-docs artifacts are English by default unless the user explicitly requests another content language. Required document headings remain English for validator stability.

If `Planner-docs/Planing-Ledger.md`, `Planner-docs/Project-Ontology.md`, or `Planner-docs/Project-Comprehension.md` already exists, Step 1 reads it as supporting history before intake. Current repository state and user-confirmed intent still win over stale continuity docs.

### Step 1.5: Autopsy

For existing or partially built projects, AntigravityQB creates `Planner-docs/Autopsy.md` and may create `Planner-docs/Project-Ontology.md` and `Planner-docs/Project-Comprehension.md` when enough evidence exists. The autopsy reviews:

- project structure and major modules;
- implemented, partial, and missing features;
- placeholder or mock behavior;
- technical debt and architecture risks;
- validation and CI gaps;
- security, privacy, and operational concerns;
- readiness issues that should influence Step 2.

`Project-Ontology.md` captures domain vocabulary, entities, concepts, module boundaries, workflows, lifecycles, integrations, invariants, constraints, and open ontology questions.

`Project-Comprehension.md` is optional and intended for medium or large existing projects. It records question-driven comprehension, evidence registers, confidence, domain-to-code trace maps, intended-vs-implemented architecture relations, bounded history/hotspot signals, quality scenarios, and open hypotheses with next probes.

Empty or nearly empty repositories can skip this step.

### Step 2: Sub-Plans

Step 2 expands every main phase into detailed sub-plan files under `Planner-docs/Faz-<n>-Plans/`. It uses `Autopsy.md`, `Project-Ontology.md`, `Project-Comprehension.md`, and `Planing-Ledger.md` as supporting evidence when present and writes an index at:

```text
Planner-docs/Sub-Planing-Index.md
```

Step 2 should continue until all phases from the main plan are represented.

### Step 3: QA Audit

Step 3 creates:

```text
Planner-docs/Sub-Planing-Audit.md
```

The audit checks plan coverage, file naming, phase ordering, required sections, index consistency, scope drift, readiness realism, ontology consistency, planning-history continuity, security/governance coverage, vibecoding slice quality, and Step 4 readiness. It does not repair plan files.

### Step 4: Gated Implementation Handoff

Step 4 is intentionally not product implementation. It is a handoff prompt for a new Antigravity task.

The Step 4 prompt is printed only when:

- `Planner-docs/Sub-Planing-Audit.md` exists;
- the audit status is `PASS`, or `PASS_WITH_WARNINGS` without P0/P1 findings;
- the Step 4 validator passes.

The implementation handoff must build an ordered queue from READY and READY_WITH_WARNINGS items. After each verified slice, the implementation task should continue to the next acceptance criterion or next eligible sub-plan instead of stopping after the first successful slice.

When file writes are allowed in the Step 4 implementation task, the handoff asks the run to append a concise verified-slice or stop-event summary to `Planner-docs/Planing-Ledger.md`. The ledger is replanning memory, not a transcript dump.

It should stop only when a real stop gate is hit, such as:

- P0/P1 finding or safety/security blocker;
- failing tests that cannot be resolved in the current slice;
- missing required files or planner outputs;
- contradiction between the plan, audit, repository, or user instruction;
- credential, payment, or live-approval requirement;
- unsafe external mutation;
- unrelated dirty worktree or merge conflict;
- unavailable validation with no reasonable fallback;
- token/context budget too low to continue safely;
- explicit user stop request.

## Generated Artifact Tree

A complete planning run usually creates:

```text
Planner-docs/
  Main-Planing.md
  Autopsy.md
  Project-Ontology.md
  Project-Comprehension.md
  Planing-Ledger.md
  Sub-Planing-Index.md
  Sub-Planing-Audit.md
  Faz-1-Plans/
    Faz1.1-*.md
    Faz1.2-*.md
  Faz-2-Plans/
    Faz2.1-*.md
    Faz2.2-*.md
```

`Autopsy.md`, `Project-Ontology.md`, `Project-Comprehension.md`, and `Planing-Ledger.md` are optional depending on repository maturity and prior runs. The phase and sub-plan count depends on the project scope.

## Validation

From an AntigravityQB checkout, validate generated planner docs with:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step1
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode autopsy --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3-preflight --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

The validator checks required sections, optional autopsy/ontology/comprehension/ledger headings, phase folders, filename conventions, index references, duplicate numbering, unindexed files, length-bounded secret patterns, and Step 4 readiness. In `--mode step4`, open P0/P1 audit findings block implementation readiness, open or accepted P2/P3 findings require `PASS_WITH_WARNINGS`, resolved or not-applicable P2/P3 findings may coexist with `PASS`, and `NO_ACTION_REQUIRED` is valid when all in-scope rows are COMPLETE, SUPERSEDED, or DEFERRED.

| Mode | Purpose |
| --- | --- |
| `step1` | Validate `Main-Planing.md`. |
| `autopsy` | Require and validate `Autopsy.md` plus optional continuity artifacts. |
| `step2` | Validate Step 2 artifacts and optional continuity artifacts. |
| `step3-preflight` | Validate Step 2 artifacts before `Sub-Planing-Audit.md` exists. |
| `step3` | Validate Step 2 artifacts plus the audit. |
| `step4` | Enforce semantic readiness, finding status, NO_ACTION_REQUIRED, and Ledger v2 strict execution gates. |

Maintainers should run the full package check before release:

```bash
make check
```

The repository also includes a deterministic fixture corpus under `evals/` so future live skill evaluations have stable inputs.

`make check` validates:

- required repository files;
- Antigravity skill frontmatter;
- stale platform invocation names;
- release secret hygiene in Git checkouts or package secret hygiene in Gitless exports;
- archive hygiene in Git checkouts or package hygiene in Gitless exports;
- installer dry-runs;
- Python unit tests;
- fixture corpus integrity.

## Security And Privacy

AntigravityQB is designed to keep planning artifacts safe to review and commit:

- It does not require API keys or service credentials.
- It should not print, store, or invent secrets.
- The validator scans for common leaked secret patterns, including long fake tokens and real-looking provider keys.
- Human-readable placeholder values are allowed; real provider keys are release blockers.
- Planning prompts instruct the agent to report credential blockers instead of bypassing them.
- Generated plans should avoid unnecessary personal data, direct contact details, payment identifiers, or environment-specific secrets.

If a real key is exposed in chat, logs, docs, examples, or commits, treat it as compromised and rotate it outside this repository before release.

## Language Contract

- Repository documentation and bundled planner artifacts are English by default.
- Required validator-facing headings remain English.
- The user-facing intake conversation can use the user's language when practical.
- Do not mix platform-specific terms from other agent environments into AntigravityQB documentation or prompts.

## Repository Layout

```text
.github/workflows/validate.yml
CHANGELOG.md
docs/
  INSTALLATION.md
  MAINTAINING.md
  USAGE.md
evals/
  run_fixture_corpus_checks.py
  fixtures/
scripts/
  install.sh
  validate.sh
skills/
  antigravityqb/
    SKILL.md
    scripts/validate_planner_docs.py
    references/
      vibecoding-principles.md
      task-delegation-playbook.md
      planning-ledger.md
      project-ontology.md
      project-comprehension-methods.md
      probe-policy.md
      assessment-and-budget.md
      engineering-principles.md
      handoffs/
        run-step2.md
        run-step3.md
        run-step4.md
tests/
Makefile
LICENSE
README.md
```

## CI

The repository includes a GitHub Actions workflow at:

```text
.github/workflows/validate.yml
```

The workflow runs the dependency-free validation gate on push and pull request events.

## Troubleshooting

If Antigravity does not list `antigravityqb`:

- start a new Antigravity conversation or task;
- confirm the installed folder contains `SKILL.md`;
- confirm the skill was copied to one of the documented Antigravity skill directories;
- reinstall with `--force` if a partial copy already exists;
- use `/skills` in Antigravity CLI to refresh and inspect available skills.

If Step 4 is not printed:

- confirm `Planner-docs/Sub-Planing-Audit.md` exists;
- run the Step 4 validator;
- resolve P0/P1 findings first;
- confirm the audit status is `PASS` or eligible `PASS_WITH_WARNINGS`.

If validation fails:

- read the exact file and line reported by the validator;
- repair the planning package or repository metadata;
- rerun the same command before continuing.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Usage](docs/USAGE.md)
- [Maintaining AntigravityQB](docs/MAINTAINING.md)

## License

MIT. See [LICENSE](LICENSE).
