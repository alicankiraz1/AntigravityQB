# Repo-Aware Step 1 Intake

Use this reference before `First-Planner.md` when AntigravityQB starts a normal Step 1 planning run.

The goal is to ask the same four required fields, but make the questions active, evidence-backed, and useful for an existing repository.

## Boundaries

- Ask in the user's language.
- Ask one question at a time.
- Use plain text only. Do not use pop-ups, forms, or multiple-choice UI.
- Do not write files during intake.
- Do not run networked, destructive, install, commit, push, deploy, or PR commands.
- Treat the current working directory as the project repository.
- Make it clear when a statement is inferred from repo evidence.
- If evidence is weak, say that repo evidence is limited and ask the concise generic version of the question.

## Pre-Intake Scan

Before asking `PROJECT_NAME`, inspect the repository with a bounded read-only pass.

Prefer commands like:

```bash
pwd
git status --short --branch
git branch --show-current
find . -maxdepth 2 \( -path './.git' -o -path './node_modules' -o -path './.venv' -o -path './dist' -o -path './build' -o -path './artifacts' \) -prune -o -type f -print | sort | head -120
find . -maxdepth 2 \( -path './.git' -o -path './node_modules' -o -path './.venv' -o -path './dist' -o -path './build' -o -path './artifacts' \) -prune -o -type d -print | sort | head -80
ls
```

Read likely evidence files when they exist:

- `README.md`
- `AGENTS.md`
- `Makefile`
- `package.json`
- `pyproject.toml`
- `Cargo.toml`
- `go.mod`
- `docker-compose.yml` or `compose.yml`
- `.github/workflows/*.yml`
- `docs/` index, architecture, roadmap, runbook, deployment, security, or testing files
- top-level service, package, app, config, script, test, and infra directories

Use `rg` only for targeted discovery when useful:

```bash
rg -n "architecture|roadmap|runbook|production|security|policy|workflow|worker|scheduler|gateway|adapter|dashboard|test|smoke|deploy|Kubernetes|Docker|Postgres|queue|approval|audit|artifact|observability" . --glob '!.git/**' --glob '!node_modules/**' --glob '!.venv/**' --glob '!dist/**' --glob '!build/**' --glob '!artifacts/**'
```

Keep this pass brief. Its purpose is to make the intake questions smarter, not to replace the full repository analysis in `First-Planner.md`.

## What To Infer

Infer a draft answer only when there is evidence.

- `PROJECT_NAME`: prefer README title, package/app name, repository directory name, product docs, or manifest names.
- `PROJECT_INTENT`: infer what the project does, its target users, main components, integrations, and what it seems to be trying to become.
- `TARGET_END_STATE`: draft the "done" state across product, engineering, operations, security, and user value.
- `KNOWN_CONSTRAINTS`: infer stack, deployment model, test commands, CI, compliance/security boundaries, must-use tools, must-not-use tools, timeline hints, and unknown constraints that need user confirmation.

Do not treat inferred values as final until the user confirms or edits them.

## Question Style

Start with a short setup sentence:

```text
I will ask four short questions one by one. I will enrich the questions with evidence I saw in the repository; after your answers, I will generate the main plan.
```

Translate this sentence to the user's language when the user is not writing in English.

### Question 1 / 4 - PROJECT_NAME

Use this shape:

```text
Question 1 / 4 - PROJECT_NAME (Project Name)

Let's clarify which project this plan is for.

Based on what I saw in the repository, this project appears to be "<inferred name>". Evidence: <short evidence such as README title, package name, or repo folder>.

Should I use "<inferred name>" as the project name, or should I use a different official name?
```

If evidence is weak:

```text
Question 1 / 4 - PROJECT_NAME (Project Name)

Repository evidence is limited, so I need you to clarify the project name.

Which project name should this plan use?
```

After the answer, confirm:

```text
PROJECT_NAME = "<final value>" has been saved.
```

### Question 2 / 4 - PROJECT_INTENT

Use this shape:

```text
Question 2 / 4 - PROJECT_INTENT (Project Purpose)

This field explains why the project exists and what it is trying to become.

Here is the draft I inferred from the repository:

<1-2 concise paragraphs describing inferred intent, components, target users, and direction.>

Questions:

1. Is this description correct, or are there points you want to correct or add?
2. What is the final target this project is trying to reach?

You can answer in a few short sentences; I will turn it into professional plan text.
```

After the answer, confirm the stored value in one sentence:

```text
PROJECT_INTENT saved: <brief normalized summary>.
```

### Question 3 / 4 - TARGET_END_STATE

Use this shape:

```text
Question 3 / 4 - TARGET_END_STATE (Target End State / Definition of Done)

I want to clarify the definition of done from five angles. Here is the draft I prepared from repository evidence:

- Product: <product outcome>
- Engineering: <engineering outcome>
- Operations: <operations outcome>
- Security: <security outcome>
- User value: <user-value outcome>

Do these five dimensions reflect your definition of done? Is there anything you want to add, remove, or change?
```

After the answer, confirm:

```text
TARGET_END_STATE saved: <brief normalized summary>.
```

### Question 4 / 4 - KNOWN_CONSTRAINTS

Use this shape:

```text
Question 4 / 4 - KNOWN_CONSTRAINTS (Known Constraints)

Here is the constraint draft I saw in the repository or could not yet confirm:

- Stack/tools: <detected stack or unknown>
- Operations/infra: <detected deployment/runtime or unknown>
- Test/validation: <detected commands or unknown>
- Security/compliance: <detected boundaries or unknown>
- Time/team/budget: <known if present, otherwise unknown>
- Must-use / must-not-use: <known if present, otherwise unknown>

Is there anything I should add, correct, or specifically avoid in this list?
```

After the answer, confirm:

```text
KNOWN_CONSTRAINTS saved: <brief normalized summary>.
```

## After Intake

When all four fields are confirmed:

1. Read `references/First-Planner.md`.
2. Substitute the confirmed field values.
3. Treat user-confirmed field values as source of truth.
4. Treat repo-inferred intake notes as supporting context only.
5. Continue with the full Step 1 repository analysis required by `First-Planner.md`.
