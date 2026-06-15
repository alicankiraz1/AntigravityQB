# AntigravityQB Task Delegation Playbook

Use helper agents when they reduce context pollution, improve parallel evidence gathering, or separate implementation from review.

Do **not** use helper agents for small, obvious, single-file planning tasks.

## Default Rule

The parent AntigravityQB agent owns the official artifact write.

Helper agents may gather evidence, draft options, audit sections, or review changes. They should not write `Planner-docs/` artifacts directly unless the user explicitly asks for that behavior.

## Recommended Helper-Agent Roles

### repo_explorer

Read-only. Maps repository structure, modules, ownership boundaries, tests, CI, docs, and key files. Returns file-path evidence.

### readiness_auditor

Read-only. Checks docs vs implementation, local vs live readiness, smoke vs production claims, and operational gaps.

### security_reviewer

Read-only by default. Checks secret safety, command execution risk, approval gates, insecure defaults, dependency risk, and external mutation boundaries.

### ontology_mapper

Read-only. Extracts domain vocabulary, entities, workflows, module boundaries, invariants, integrations, and open concept questions.

### phase_planner

Planning-only. Drafts sub-phase options for one phase or a small phase cluster. Parent consolidates final sub-plan files.

### implementation_slicer

Step 4 only. Turns a READY sub-plan into the smallest verified implementation slice.

### verification_reviewer

Read-only where practical. Reviews diffs, tests, artifacts, and whether the acceptance criterion is actually met.

## When to Spawn Helper agents

Use helper agents when:

- the repository is large or unfamiliar;
- Step 1.5 Autopsy has multiple independent evidence areas;
- Step 2 has many phases or very different domains;
- Step 3 has many sub-plans and needs separate coverage/readiness/security review;
- Step 4 needs implementation/review separation.

Do not spawn helper agents when:

- the task is small enough for one context window;
- results would be mostly duplicated;
- the user asked for a quick single-step output;
- helper agent writes would create file conflicts.

## Safety Boundaries

- Helper agents inherit and must obey sandbox, approval, secret, and file-boundary rules.
- Do not let multiple helper agents write the same file.
- Only one writer should modify files for a Step 4 implementation slice unless the user explicitly requests parallel branches.
- Parent agent must consolidate helper agent results and cite or summarize evidence before writing final artifacts.
