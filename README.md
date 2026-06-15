# AntigravityQB

**Repo-aware project planning for Google Antigravity.**

AntigravityQB is a Google Antigravity Agent Skill that turns an existing repository into a durable planning package. It inspects the project, asks a small set of high-signal intake questions, writes structured planning documents, audits those documents, and finally produces a gated implementation handoff prompt for a separate Antigravity task.

The plugin is designed for serious project work where plans need to survive long context windows, implementation needs clear acceptance criteria, and the agent should not start changing product code before the planning package is complete.

AntigravityQB is the Antigravity-native edition of a repo-aware planning workflow built around Markdown-based stable planning, validation controls, and controlled implementation handoff. It is meant to reduce context drift in long tasks without turning the planning skill itself into an implementation agent.

## What It Does

AntigravityQB creates a planning workflow around the repository you already have open:

- **Repo-aware intake:** reads the current project before asking questions, then proposes practical defaults for project name, intent, target state, and constraints.
- **Existing-project autopsy:** identifies current modules, features, placeholder code, technical debt, integration gaps, validation gaps, and readiness risks.
- **Durable planning artifacts:** writes Markdown files under `Planner-docs/` so the plan can be reviewed, versioned, shared, resumed, and audited.
- **Phase decomposition:** expands a main plan into ordered phase folders and detailed sub-plan files.
- **Quality audit:** checks coverage, sequencing, structure, readiness, security/governance concerns, and implementation preparedness.
- **Gated Step 4 handoff:** prints a separate implementation prompt only when the audit says implementation can begin.
- **Queue-continuation semantics:** Step 4 builds an ordered READY/READY_WITH_WARNINGS queue and keeps going through verified slices until a real stop gate is hit.
- **Planning-only guardrails:** keeps P0/P1 audit gates, secret/token hygiene, file boundaries, and implementation safety rules visible at the skill level.
- **Dependency-free validation:** ships a Python standard-library validator and a `make check` release gate.

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
| Step 1.5 | Existing-project autopsy when the repo is already built or partially built. | `Planner-docs/Autopsy.md` |
| Step 2 | Full phase and sub-plan generation. | `Planner-docs/Sub-Planing-Index.md`, `Planner-docs/Faz-*-Plans/*.md` |
| Step 3 | Read-only QA audit of the planning package. | `Planner-docs/Sub-Planing-Audit.md` |
| Step 4 | Copy-ready implementation handoff prompt for a separate task. | Text prompt only |

### Step 1: Main Plan

AntigravityQB scans the repository and asks:

- `PROJECT_NAME`
- `PROJECT_INTENT`
- `TARGET_END_STATE`
- `KNOWN_CONSTRAINTS`

AntigravityQB asks intake questions in the user's language when practical. Generated Planner-docs artifacts are English by default unless the user explicitly requests another body language. Required document headings remain English for validator stability.

### Step 1.5: Autopsy

For existing or partially built projects, AntigravityQB creates `Planner-docs/Autopsy.md`. The autopsy reviews:

- project structure and major modules;
- implemented, partial, and missing features;
- placeholder or mock behavior;
- technical debt and architecture risks;
- validation and CI gaps;
- security, privacy, and operational concerns;
- readiness issues that should influence Step 2.

Empty or nearly empty repositories can skip this step.

### Step 2: Sub-Plans

Step 2 expands every main phase into detailed sub-plan files under `Planner-docs/Faz-<n>-Plans/`. It uses `Autopsy.md` as feedback when present and writes an index at:

```text
Planner-docs/Sub-Planing-Index.md
```

Step 2 should continue until all phases from the main plan are represented.

### Step 3: QA Audit

Step 3 creates:

```text
Planner-docs/Sub-Planing-Audit.md
```

The audit checks plan coverage, file naming, phase ordering, required sections, index consistency, scope drift, readiness realism, security/governance coverage, and Step 4 readiness. It does not repair plan files.

### Step 4: Gated Implementation Handoff

Step 4 is intentionally not product implementation. It is a handoff prompt for a new Antigravity task.

The Step 4 prompt is printed only when:

- `Planner-docs/Sub-Planing-Audit.md` exists;
- the audit status is `PASS`, or `PASS_WITH_WARNINGS` without P0/P1 findings;
- the Step 4 validator passes.

The implementation handoff must build an ordered queue from READY and READY_WITH_WARNINGS items. After each verified slice, the implementation task should continue to the next acceptance criterion or next eligible sub-plan instead of stopping after the first successful slice.

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
  Sub-Planing-Index.md
  Sub-Planing-Audit.md
  Faz-1-Plans/
    Faz1.1-*.md
    Faz1.2-*.md
  Faz-2-Plans/
    Faz2.1-*.md
    Faz2.2-*.md
```

`Autopsy.md` is optional for greenfield repositories. The phase and sub-plan count depends on the project scope.

## Validation

From an AntigravityQB checkout, validate generated planner docs with:

```bash
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step1
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step2 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step3 --strict
python3 skills/antigravityqb/scripts/validate_planner_docs.py --root /path/to/project --mode step4
```

Maintainers should run the full package check before release:

```bash
make check
```

`make check` validates:

- required repository files;
- Antigravity skill frontmatter;
- stale platform invocation names;
- release secret hygiene;
- archive hygiene when Git metadata is available;
- installer dry-runs;
- Python unit tests.

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
docs/
  INSTALLATION.md
  MAINTAINING.md
  USAGE.md
scripts/
  install.sh
  validate.sh
skills/
  antigravityqb/
    SKILL.md
    scripts/validate_planner_docs.py
    references/
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
