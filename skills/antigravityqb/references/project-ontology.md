# AntigravityQB Project Ontology

AntigravityQB uses `Planner-docs/Project-Ontology.md` as an optional durable project-understanding artifact.

## Purpose

The ontology helps Antigravity and coding agents understand the project's language, boundaries, workflows, and invariants before planning or implementation.

## Recommended File

```text
Planner-docs/Project-Ontology.md
```

## Recommended Headings

```markdown
# Project Ontology

## 1. Purpose
## 2. Domain Vocabulary
## 3. Core Entities and Concepts
## 4. Module and Boundary Map
## 5. Workflows and Lifecycles
## 6. Integrations and External Systems
## 7. Invariants and Constraints
## 8. Open Ontology Questions
```

## What to Capture

- domain nouns and verbs;
- core entities and their lifecycle states;
- modules and ownership boundaries;
- workflows and state transitions;
- integration points and external systems;
- security, compliance, or business invariants;
- ambiguous terms that require human confirmation.

## How to Use It

- Step 1.5 should create or update the ontology for existing projects when enough evidence exists.
- Step 2 should use it to keep sub-plans consistent with project concepts and boundaries.
- Step 3 should audit whether plans contradict important invariants.
- Step 4 should read only the ontology sections relevant to the active slice.

## Safety

Do not include secrets, local credentials, private customer data, or full production data examples. Use redacted examples or abstract concept names when needed.
