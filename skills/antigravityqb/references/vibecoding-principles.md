# Vibecoding Planning Principles

AntigravityQB plans in a vibecoding-first style.

Vibecoding-first does **not** mean careless, unstructured, or unsafe. It means the planning system keeps a strong target vision while staying adaptive to repository evidence and fast feedback.

## Core Behavior

- Start from the repo's current feel: structure, naming, tests, docs, active modules, and actual evidence.
- Prefer the next useful verified move over a frozen speculative mega-plan.
- Plan small, reversible slices that can be implemented, validated, and reviewed independently.
- Keep acceptance criteria concrete enough for a coding agent to execute.
- Preserve room for discovery during Step 4 instead of over-specifying every implementation detail too early.
- Say when evidence is weak instead of creating fake certainty.
- Separate stable document contracts from flexible planning content.
- Use fast validation signals: existing tests, focused new tests, lint/typecheck, smoke commands, artifact checks, and review evidence.
- Update planning assumptions when real implementation feedback contradicts the original plan.

## What Vibecoding Must Not Relax

Vibecoding never weakens:

- file-boundary rules;
- secret safety;
- secure coding expectations;
- approval gates;
- test and validation requirements;
- review and audit requirements;
- local vs live readiness distinctions;
- destructive or external mutation controls.

## Planning Output Expectations

Each plan should help a coding agent answer:

1. What is the target?
2. What does the repo already prove?
3. What is the smallest useful next slice?
4. What should be validated first?
5. What is intentionally deferred until more evidence exists?
6. What must not be touched without human approval?

## Antigravity task Fit

Long AntigravityQB runs should be phrased as Antigravity task work: define the outcome, unchanged boundaries, validation checkpoints, stop gates, and the final summary expected from the agent.

A good Antigravity task handoff is larger than one prompt but smaller than an unbounded backlog.
