# Installation

AntigravityQB is distributed as a Google Antigravity Agent Skill folder.

## Requirements

- Google Antigravity IDE or Antigravity CLI.
- Python 3 for the bundled read-only planner validator.
- A new Antigravity conversation or task after installation so the skill list refreshes.

## Install With The Script

From this repository checkout:

```bash
scripts/install.sh --scope app-global
scripts/install.sh --scope ide-project --target /path/to/project
scripts/install.sh --scope ide-global
scripts/install.sh --scope cli-project --target /path/to/project
scripts/install.sh --scope cli-global
```

Use `--dry-run` to preview the destination:

```bash
scripts/install.sh --scope ide-project --target /path/to/project --dry-run
```

Use `--force` to replace an existing installed copy:

```bash
scripts/install.sh --scope ide-global --force
```

## Install Manually

Copy the skill folder to one of Antigravity's documented skills directories:

```bash
mkdir -p ~/.gemini/config/plugins/antigravityqb/skills
cp -R skills/antigravityqb ~/.gemini/config/plugins/antigravityqb/skills/antigravityqb
cp -R skills/antigravityqb /path/to/project/.agents/skills/antigravityqb
cp -R skills/antigravityqb ~/.agents/skills/antigravityqb
cp -R skills/antigravityqb /path/to/project/.agent/skills/antigravityqb
cp -R skills/antigravityqb ~/.gemini/antigravity-cli/skills/antigravityqb
```

Use `~/.gemini/config/plugins/<plugin>/skills` for the Antigravity app global plugin cache, `.agents/skills` for Antigravity IDE project scope, `.agent/skills` for Antigravity CLI project scope, `~/.agents/skills` for Antigravity IDE global scope, and `~/.gemini/antigravity-cli/skills` for Antigravity CLI global scope.

## Verify Installation

In Antigravity IDE, ask:

```text
What skills are available?
```

In Antigravity CLI, use:

```text
/skills
```

Then test:

```text
Use the antigravityqb skill to create a main plan for this project.
```

Expected behavior:

1. AntigravityQB performs a bounded read-only scan of the current repository.
2. It asks for `PROJECT_NAME`, ideally with a repo-derived default.
3. It asks for `PROJECT_INTENT`, ideally with a repo-derived draft.
4. It asks for `TARGET_END_STATE`, ideally across product, engineering, operations, security, and user value.
5. It asks for `KNOWN_CONSTRAINTS`, including detected stack, infra, validation, security, and unknown constraints.
6. It uses the confirmed values to create or update `Planner-docs/Main-Planing.md`.
7. For existing or partially built repositories, it may create or update `Planner-docs/Autopsy.md` as Step 1.5.

## Troubleshooting

If `antigravityqb` is not listed:

- start a new Antigravity conversation or task;
- confirm the folder contains `SKILL.md`;
- confirm it is installed under one of the documented skills directories;
- reinstall with `--force` if a partial copy already exists.

Step 2, Step 3, and Step 4 are intentionally handed off as text prompts so you can launch long-running planning, audit, or implementation work explicitly.
