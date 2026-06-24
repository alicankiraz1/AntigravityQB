from __future__ import annotations

import contextlib
import importlib.util
import io
import re
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "skills/antigravityqb/scripts/validate_planner_docs.py"
CLI_TIMEOUT_SECONDS = 30


@dataclass
class ValidatorResult:
    returncode: int
    stdout: str
    stderr: str


def load_validator_module():
    spec = importlib.util.spec_from_file_location("antigravityqb_validate_planner_docs", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load validator module from {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR_MODULE = load_validator_module()

SECRET_OUTPUT_RE = re.compile(
    r"sk-or-v1-[A-Za-z0-9_-]+"
    r"|sk-[A-Za-z0-9_-]{20,}"
    r"|github_pat_[A-Za-z0-9_]{20,}"
    r"|ghp_[A-Za-z0-9]{20,}"
)

STEP1_HEADINGS = [
    "# Main Planing",
    "## 1. Executive Summary",
    "## 2. Project Vision",
    "## 3. Current State Analysis",
    "## 4. Target End State",
    "## 5. Architecture Direction and Key Decisions",
    "## 6. Phase-Based Master Roadmap",
    "## 7. Critical Risks and Gaps",
    "## 8. Prioritized Next Steps",
    "## 9. Step 2 Preparation Notes",
    "## 10. Repository Review Notes",
]

AUTOPSY_HEADINGS = [
    "# Project Autopsy",
    "## 1. Executive Summary",
    "## 2. Reviewed Sources",
    "## 3. Project Areas and Ownership Boundaries",
    "## 4. Feature Inventory",
    "## 5. Placeholder, Stub, and Skeleton Analysis",
    "## 6. Technical Debt and Maintenance Risks",
    "## 7. Broken or Missing Integrations",
    "## 8. Test, CI, and Validation Gaps",
    "## 9. Security, Secret, and Governance Findings",
    "## 10. Operational Readiness and Observability",
    "## 11. Alignment Analysis with the Main Plan",
    "## 12. Autopsy Feedback for Step 2",
    "## 13. Priority Fix and Planning Signals",
]

COMPREHENSION_HEADINGS = [
    "# Project Comprehension",
    "## 1. Understanding Goals and Competency Questions",
    "## 2. Evidence Register and Confidence",
    "## 3. Domain-to-Code Trace Map",
    "## 4. Structure, Data, and Runtime Flow Model",
    "## 5. Intended vs Implemented Architecture",
    "## 6. Change History, Hotspots, and Ownership Signals",
    "## 7. Quality Attribute Scenarios and Tradeoffs",
    "## 8. Open Hypotheses and Validation Probes",
]

INDEX_HEADINGS = [
    "# Sub-Planing Index",
    "## 1. Purpose",
    "## 2. Source Main Plan",
    "## 3. Planning Scope Manifest",
    "## 4. Phase and Sub-Plan Map",
    "## 5. Execution Waves",
    "## 6. Parent Acceptance Traceability",
    "## 7. Decision Register",
    "## 8. Priority Detailing Order",
    "## 9. Out-of-Scope or Deferred Topics",
    "## 10. Coverage Check",
    "## 11. Repository Review Notes",
]

SUBPLAN_HEADINGS = [
    "## 1. Context",
    "## 2. Goal",
    "## 3. Description",
    "## 4. Scope",
    "## 5. Out of Scope",
    "## 6. Current Repository Evidence",
    "## 7. Planned Work Breakdown",
    "## 8. Acceptance Criteria",
    "## 9. Validation and Test Approach",
    "## 10. Dependencies and Sequencing",
    "## 11. Risks and Mitigations",
    "## 12. Desired End State",
    "## 13. Next Sub-Phase Transition Criteria",
]

AUDIT_HEADINGS = [
    "# Sub-Planing Audit",
    "## 1. Audit Summary",
    "## 2. Reviewed Sources",
    "## 3. Main Phase Coverage Analysis",
    "## 4. Sub-Plan File Inventory",
    "## 5. Naming and Sequencing Check",
    "## 6. Index Consistency Check",
    "## 7. Required Section Structure Check",
    "## 8. Content Quality and Implementability Analysis",
    "## 9. Scope Drift and Architectural Consistency Analysis",
    "## 10. Readiness Realism",
    "## 11. Security and Governance Findings",
    "## 12. Step 4 Readiness Assessment",
    "## 13. Priority Fix List",
    "## 14. Recommended Next Command / Prompt",
    "## 15. Audit Result",
]


def body(label: str) -> str:
    clean_label = label.lstrip("# ").replace("|", " ").strip()
    return f"{clean_label} section has enough length, verifiable detail, and English fixture content."


def normalize_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def redact_output(value: str) -> str:
    return SECRET_OUTPUT_RE.sub("<redacted>", value)


def run_validator(root: Path, mode: str, strict: bool = False) -> ValidatorResult:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            code = VALIDATOR_MODULE.run_validation(root, mode, strict)
        except SystemExit as exc:
            code = int(exc.code or 0) if isinstance(exc.code, int) else 1
    return ValidatorResult(code, stdout.getvalue(), stderr.getvalue())


def run_validator_cli(
    root: Path,
    mode: str,
    strict: bool = False,
    timeout: int = CLI_TIMEOUT_SECONDS,
) -> ValidatorResult:
    command = [sys.executable, str(VALIDATOR), "--root", str(root), "--mode", mode]
    if strict:
        command.append("--strict")
    try:
        completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = redact_output(normalize_output(exc.stdout))
        stderr = redact_output(normalize_output(exc.stderr))
        raise AssertionError(
            f"validator timed out after {timeout}s\n"
            f"mode={mode}\n"
            f"root={root}\n"
            f"command={' '.join(command)}\n"
            f"stdout={stdout}\n"
            f"stderr={stderr}"
        ) from exc
    return ValidatorResult(completed.returncode, completed.stdout, completed.stderr)


def write_main_plan(docs: Path) -> None:
    lines: list[str] = []
    for heading in STEP1_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 6. Phase-Based Master Roadmap":
            lines += [
                "The existing repo includes historical Faz 0B-10 plans and Phase 11 security notes.",
                "",
                "| Phase | Phase name | Goal | Approximate maturity | Main acceptance signals |",
                "|---|---|---|---|---|",
                "| 1 | Local Contract Stabilization | Clarify baseline | M3 | make check |",
                "| 2 | Live Gateway Activation | ready_live evidence | M4 | make smoke |",
                "",
            ]
    (docs / "Main-Planing.md").write_text("\n".join(lines), encoding="utf-8")


def write_autopsy(docs: Path, headings: list[str] | None = None) -> None:
    lines: list[str] = []
    for heading in headings or AUTOPSY_HEADINGS:
        lines += [heading, "", body(heading), ""]
    (docs / "Autopsy.md").write_text("\n".join(lines), encoding="utf-8")


def write_subplan(path: Path, phase: int, subphase: int) -> None:
    lines = [
        "---",
        "artifact_schema_version: 3",
        "handoff_contract_version: 2",
        "generated_by: antigravityqb",
        "plugin_version: 0.3.0",
        "---",
        "",
        f"# Faz {phase}.{subphase} — Test Sub-Plan",
        "",
    ]
    for heading in SUBPLAN_HEADINGS:
        text = body(heading)
        if heading == "## 6. Current Repository Evidence":
            text += " `configs/example.placeholder` is a normal example filename."
        if heading == "## 11. Risks and Mitigations":
            text += " placeholder-safe command wording is not a real placeholder."
        lines += [heading, "", text, ""]
    lines += [
        "### Implementation Contract",
        "",
        "```json",
        "{",
        '  "contract_version": 1,',
        '  "implementation_paths": [',
        f'    {{"path": "src/feature_{phase}_{subphase}.py", "state": "proposed"}},',
        f'    {{"path": "tests/test_feature_{phase}_{subphase}.py", "state": "proposed"}}',
        "  ],",
        '  "validation_commands": [',
        "    {",
        '      "id": "VAL-01",',
        f'      "argv": ["python3", "-m", "pytest", "tests/test_feature_{phase}_{subphase}.py", "-q"],',
        '      "cwd": ".",',
        '      "expected_exit_code": 0,',
        '      "timeout_seconds": 120,',
        '      "network": "deny",',
        '      "probe_tier": 1',
        "    }",
        "  ],",
        f'  "parent_signals": ["MP-PH{phase}-AS-01"],',
        '  "dependencies": {',
        '    "depends_on": [],',
        '    "blocks": [],',
        '    "can_run_in_parallel_with": [],',
        '    "activation_conditions": ["Planning fixture exists"]',
        "  },",
        f'  "outputs": ["src/feature_{phase}_{subphase}.py", "tests/test_feature_{phase}_{subphase}.py"],',
        '  "risk_class": "low",',
        '  "risk_domains": ["none"],',
        '  "security_review_required": false',
        "}",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_index(
    docs: Path,
    relative_refs: bool = False,
    active_phases: list[int] | None = None,
    deferred_phases: list[int] | None = None,
) -> None:
    active = active_phases or [1, 2]
    deferred = deferred_phases or []
    ref_by_phase = {
        1: "Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md",
        2: "Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md",
        3: "Planner-docs/Faz-3-Plans/Faz3.1-future-readiness.md",
    }
    refs = [ref_by_phase[phase] for phase in active if phase in ref_by_phase]
    if relative_refs and refs:
        refs = [
            "Faz-1-Plans/Faz1.1-local-contract.md" if ref.endswith("Faz1.1-local-contract.md") else f"./{ref}"
            for ref in refs
        ]

    lines: list[str] = [
        "---",
        "artifact_schema_version: 3",
        "handoff_contract_version: 2",
        "generated_by: antigravityqb",
        "plugin_version: 0.3.0",
        "---",
        "",
    ]
    for heading in INDEX_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 3. Planning Scope Manifest":
            lines += [
                "```yaml",
                "planning_mode: wave",
                f"active_phases: {active}",
                f"deferred_phases: {deferred}",
                "max_detailed_subplans: 12",
                "max_output_words: 12000",
                "task_token_risk: medium",
                "review_checkpoint: after_wave_1",
                "```",
                "",
            ]
        if heading == "## 4. Phase and Sub-Plan Map":
            lines += [f"- {ref}" for ref in refs] + [""]
        if heading == "## 5. Execution Waves":
            lines += [f"- Wave 1: {ref}" for ref in refs] + [""]
        if heading == "## 9. Out-of-Scope or Deferred Topics" and deferred:
            lines += [
                "| Phase | Status | Deferral Reason | Activation Trigger | Earliest Wave |",
                "|---|---|---|---|---|",
                *[
                    f"| Faz {phase} | deferred | Later phase needs active wave evidence. | Complete current active wave. | wave-2 |"
                    for phase in deferred
                ],
                "",
            ]
    (docs / "Sub-Planing-Index.md").write_text("\n".join(lines), encoding="utf-8")


def write_legacy_index(docs: Path) -> None:
    legacy_headings = [
        "# Sub-Planing Index",
        "## 1. Purpose",
        "## 2. Source Main Plan",
        "## 3. Phase and Sub-Plan Map",
        "## 4. Priority Detailing Order",
        "## 5. Out-of-Scope or Deferred Topics",
        "## 6. Coverage Check",
        "## 7. Repository Review Notes",
    ]
    refs = [
        "Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md",
        "Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md",
    ]
    lines: list[str] = []
    for heading in legacy_headings:
        lines += [heading, "", body(heading), ""]
        if heading == "## 3. Phase and Sub-Plan Map":
            lines += [f"- {ref}" for ref in refs] + [""]
    (docs / "Sub-Planing-Index.md").write_text("\n".join(lines), encoding="utf-8")


def write_ontology(docs: Path, headings: list[str] | None = None) -> None:
    ontology_headings = headings or [
        "# Project Ontology",
        "## 1. Purpose",
        "## 2. Domain Vocabulary",
        "## 3. Core Entities and Concepts",
        "## 4. Module and Boundary Map",
        "## 5. Workflows and Lifecycles",
        "## 6. Integrations and External Systems",
        "## 7. Invariants and Constraints",
        "## 8. Open Ontology Questions",
    ]
    lines: list[str] = []
    for heading in ontology_headings:
        lines += [heading, "", body(heading), ""]
    (docs / "Project-Ontology.md").write_text("\n".join(lines), encoding="utf-8")


def write_ontology_with_competency_status(docs: Path, status: str) -> None:
    lines: list[str] = []
    for heading in [
        "# Project Ontology",
        "## 1. Purpose",
        "## 2. Domain Vocabulary",
        "## 3. Core Entities and Concepts",
        "## 4. Module and Boundary Map",
        "## 5. Workflows and Lifecycles",
        "## 6. Integrations and External Systems",
        "## 7. Invariants and Constraints",
        "## 8. Open Ontology Questions",
    ]:
        lines += [heading, "", body(heading), ""]
        if heading == "## 8. Open Ontology Questions":
            lines += [
                "### Competency Questions",
                "",
                "| Question ID | Question | Status | Evidence |",
                "|---|---|---|---|",
                f"| OQ-01 | Which component owns task lease renewal? | {status} | docs/architecture.md |",
                "",
            ]
    (docs / "Project-Ontology.md").write_text("\n".join(lines), encoding="utf-8")


def write_ledger(
    docs: Path,
    headings: list[str] | None = None,
    version: int = 1,
    status: str = "verified",
    run_id: str = "RUN-001",
    validation_evidence: str = "make check",
    blocker: str = "none",
    next_action: str = "none",
    superseded_by: str = "",
) -> None:
    legacy_headings = [
        "# Planing Ledger",
        "## 1. Purpose",
        "## 2. Planning Runs",
        "## 3. Implementation Runs",
        "## 4. Current State Snapshot",
        "## 5. Replanning Inputs",
        "## 6. Open Decisions and Follow-Ups",
    ]
    v2_headings = [
        "# Planing Ledger",
        "## 1. Purpose",
        "## 2. Planning Runs",
        "## 3. Plan Snapshot Registry",
        "## 4. Sub-Plan Status Matrix",
        "## 5. Implementation Runs",
        "## 6. Current State Snapshot",
        "## 7. Replanning Inputs",
        "## 8. Open Decisions and Follow-Ups",
    ]
    ledger_headings = headings or (v2_headings if version == 2 else legacy_headings)
    lines: list[str] = []
    for heading in ledger_headings:
        lines += [heading, "", body(heading), ""]
        if heading == "## 4. Sub-Plan Status Matrix":
            lines += [
                "| Sub-plan Path | Status | Snapshot ID | Run ID | Validation Evidence | Blocker | Next Action | Superseded By | Updated At |",
                "|---|---|---|---|---|---|---|---|---|",
                f"| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | {status} | SNAP-001 | {run_id} | {validation_evidence} | {blocker} | {next_action} | {superseded_by} | 2026-06-19 |",
                "",
            ]
    (docs / "Planing-Ledger.md").write_text("\n".join(lines), encoding="utf-8")


def write_comprehension(
    docs: Path,
    headings: list[str] | None = None,
    evidence_confidence: str = "confirmed",
    evidence_type: str = "source",
    architecture_status: str = "convergent",
    evidence_source: str = "src/service.py",
    trace_entry: str = "api/routes.py",
    trace_core: str = "src/service.py",
    trace_tests: str = "tests/test_service.py",
    hypothesis_next_probe: str = "Run focused unit test for service boundary.",
    claim_type: str = "structural",
    trace_marker: str = "",
    architecture_marker: str = "",
    hypothesis_marker: str = "",
) -> None:
    lines: list[str] = []
    for heading in headings or COMPREHENSION_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 1. Understanding Goals and Competency Questions":
            lines += [
                "| Question ID | Question | Priority | Answer Criterion |",
                "|---|---|---|---|",
                "| CQ-01 | Which service boundary owns task lease renewal? | high | Source and tests identify a single owner. |",
                "",
            ]
        if heading == "## 2. Evidence Register and Confidence":
            lines += [
                "| Evidence ID | Claim Type | Claim | Evidence source | Evidence type | Confidence | Freshness | Contradiction | Next probe |",
                "|---|---|---|---|---|---|---|---|---|",
                f"| EV-01 | {claim_type} | Service routes through a boundary layer. | {evidence_source} | {evidence_type} | {evidence_confidence} | current | none | Inspect service tests. |",
                "",
            ]
        if heading == "## 3. Domain-to-Code Trace Map":
            if trace_marker:
                lines += [trace_marker, ""]
            else:
                lines += [
                    "| Trace ID | Domain concept / feature | Entry points | Core implementation | State/data | Tests | Docs | Confidence |",
                    "|---|---|---|---|---|---|---|---|",
                    f"| TRACE-01 | Task lease renewal | {trace_entry} | {trace_core} | db/tasks.sql | {trace_tests} | docs/architecture.md | probable |",
                    "",
                ]
        if heading == "## 5. Intended vs Implemented Architecture":
            if architecture_marker:
                lines += [architecture_marker, ""]
            else:
                lines += [
                    "| Relation ID | Intended relation | Source evidence | Status | Impact |",
                    "|---|---|---|---|---|",
                    f"| ARC-01 | API -> service -> repository | api/routes.py -> src/service.py | {architecture_status} | none |",
                    "",
                ]
        if heading == "## 8. Open Hypotheses and Validation Probes":
            if hypothesis_marker:
                lines += [hypothesis_marker, ""]
            else:
                lines += [
                    "| Hypothesis ID | Type | Claim | Confidence | Supporting evidence | Contradicting evidence | Next probe |",
                    "|---|---|---|---|---|---|---|",
                    f"| HYP-01 | how | Retry behavior is idempotent. | tentative | src/service.py | none | {hypothesis_next_probe} |",
                    "",
                ]
    (docs / "Project-Comprehension.md").write_text("\n".join(lines), encoding="utf-8")


def write_audit(
    docs: Path,
    status: str,
    fixes: list[str] | None = None,
    readiness_rows: list[str] | None = None,
) -> None:
    lines: list[str] = []
    default_readiness = [
        "| Sub-Plan Path | Status | Finding IDs | Dependency State | Reason | Required Repair |",
        "|---|---|---|---|---|---|",
        "| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | READY | none | independent | Contract complete and validation path exists. | none |",
    ]
    for heading in AUDIT_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 1. Audit Summary":
            lines += [f"Audit status: {status}", ""]
        if heading == "## 12. Step 4 Readiness Assessment":
            lines += readiness_rows or default_readiness
            lines += [""]
        if heading == "## 13. Priority Fix List":
            if fixes:
                lines += [
                    "| Finding ID | Severity | Status | Affected Files | Issue | Required Action |",
                    "|---|---|---|---|---|---|",
                    *fixes,
                    "",
                ]
            else:
                lines += ["No open findings.", ""]
        if heading == "## 15. Audit Result":
            lines += [f"Final status: {status}", ""]
    (docs / "Sub-Planing-Audit.md").write_text("\n".join(lines), encoding="utf-8")


def write_valid_step2_fixture(root: Path, relative_refs: bool = False) -> Path:
    docs = root / "Planner-docs"
    (docs / "Faz-1-Plans").mkdir(parents=True)
    (docs / "Faz-2-Plans").mkdir(parents=True)
    write_main_plan(docs)
    write_index(docs, relative_refs=relative_refs)
    write_subplan(docs / "Faz-1-Plans/Faz1.1-local-contract.md", 1, 1)
    write_subplan(docs / "Faz-2-Plans/Faz2.1-live-gateway.md", 2, 1)
    return docs


def write_legacy_step2_fixture(root: Path) -> Path:
    docs = root / "Planner-docs"
    (docs / "Faz-1-Plans").mkdir(parents=True)
    (docs / "Faz-2-Plans").mkdir(parents=True)
    write_main_plan(docs)
    write_legacy_index(docs)
    legacy_subplan = [f"# Faz 1.1 — Test Sub-Plan", ""]
    for heading in SUBPLAN_HEADINGS:
        legacy_subplan += [heading, "", body(heading), ""]
    (docs / "Faz-1-Plans/Faz1.1-local-contract.md").write_text("\n".join(legacy_subplan), encoding="utf-8")
    legacy_subplan[0] = "# Faz 2.1 — Test Sub-Plan"
    (docs / "Faz-2-Plans/Faz2.1-live-gateway.md").write_text("\n".join(legacy_subplan), encoding="utf-8")
    return docs


def write_three_phase_main_plan(docs: Path) -> None:
    lines: list[str] = []
    for heading in STEP1_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 6. Phase-Based Master Roadmap":
            lines += [
                "| Phase | Phase name | Goal | Approximate maturity | Main acceptance signals |",
                "|---|---|---|---|---|",
                "| 1 | Local Contract Stabilization | Clarify baseline | M3 | make check |",
                "| 2 | Live Gateway Activation | ready_live evidence | M4 | make smoke |",
                "| 3 | Production Readiness | operational evidence | M5 | make release-check |",
                "",
            ]
    (docs / "Main-Planing.md").write_text("\n".join(lines), encoding="utf-8")


def write_valid_wave_deferred_fixture(root: Path) -> Path:
    docs = root / "Planner-docs"
    (docs / "Faz-1-Plans").mkdir(parents=True)
    write_three_phase_main_plan(docs)
    write_index(docs, active_phases=[1], deferred_phases=[2, 3])
    write_subplan(docs / "Faz-1-Plans/Faz1.1-local-contract.md", 1, 1)
    return docs


class ValidatePlannerDocsTests(unittest.TestCase):

    def test_autopsy_mode_validates_main_autopsy_and_optional_ontology(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = Path(temp_dir) / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)
            write_autopsy(docs)
            write_ontology(docs)
            result = run_validator(Path(temp_dir), "autopsy", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("autopsy_exists=true", result.stdout)
            self.assertIn("ontology_exists=true", result.stdout)

    def test_autopsy_mode_requires_autopsy_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = Path(temp_dir) / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)
            result = run_validator(Path(temp_dir), "autopsy", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("missing_file=Planner-docs/Autopsy.md", result.stdout)

    def test_step2_passes_when_autopsy_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("autopsy_exists=false", result.stdout)
            self.assertIn("planning_mode=wave", result.stdout)

    def test_step2_wave_mode_accepts_deferred_phase_cards_without_folders(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_wave_deferred_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("active_phase_count=1", result.stdout)
            self.assertIn("deferred_phase_count=2", result.stdout)

    def test_step2_legacy_artifacts_get_schema_migration_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_legacy_step2_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "strict_warning=missing_or_invalid_artifact_schema_version=Planner-docs/Sub-Planing-Index.md::missing",
                result.stdout,
            )
            self.assertIn("strict_warning=missing_planning_scope_manifest=Planner-docs/Sub-Planing-Index.md", result.stdout)

    def test_step2_strict_rejects_missing_implementation_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            path = docs / "Faz-1-Plans/Faz1.1-local-contract.md"
            text = path.read_text(encoding="utf-8")
            path.write_text(text.split("### Implementation Contract", 1)[0], encoding="utf-8")
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "strict_warning=subplan_missing_implementation_contract=Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md::missing_section",
                result.stdout,
            )

    def test_step2_strict_rejects_unsafe_implementation_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            path = docs / "Faz-1-Plans/Faz1.1-local-contract.md"
            text = path.read_text(encoding="utf-8").replace('"src/feature_1_1.py"', '"/tmp/feature.py"', 1)
            path.write_text(text, encoding="utf-8")
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "strict_warning=subplan_invalid_implementation_path=Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md::/tmp/feature.py",
                result.stdout,
            )

    def test_step2_strict_rejects_mutating_validation_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            path = docs / "Faz-1-Plans/Faz1.1-local-contract.md"
            text = path.read_text(encoding="utf-8").replace(
                '"argv": ["python3", "-m", "pytest", "tests/test_feature_1_1.py", "-q"]',
                '"argv": ["npm", "run", "deploy"]',
            )
            path.write_text(text, encoding="utf-8")
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(
                "strict_warning=subplan_missing_exact_validation_command=Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md",
                result.stdout,
            )

    def test_cli_step2_success_smoke_uses_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator_cli(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("planner_docs_validation=passed", result.stdout)

    def test_cli_step4_gate_smoke_uses_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(
                docs,
                "PASS_WITH_WARNINGS",
                ["| AUDIT-FIX-01 | P1 | open | Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | repair before implementation | Fix before Step 4. |"],
            )
            result = run_validator_cli(Path(temp_dir), "step4")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("step4_blocked_by_high_severity_findings=P0:0,P1:1", result.stdout)

    def test_cli_timeout_failure_is_readable_and_redacted(self) -> None:
        fake_key = "sk-or-v1-" + "A" * 64
        timeout = subprocess.TimeoutExpired(
            cmd=["validator"],
            timeout=1,
            output=f"partial stdout {fake_key}".encode("utf-8"),
            stderr=None,
        )
        with mock.patch("subprocess.run", side_effect=timeout):
            with self.assertRaises(AssertionError) as raised:
                run_validator_cli(Path("/tmp/example-root"), "step2", timeout=1)

        message = str(raised.exception)
        self.assertIn("validator timed out after 1s", message)
        self.assertIn("mode=step2", message)
        self.assertIn("root=/tmp/example-root", message)
        self.assertIn("command=", message)
        self.assertIn("stdout=partial stdout <redacted>", message)
        self.assertIn("stderr=", message)
        self.assertNotIn(fake_key, message)

    def test_step2_validates_optional_autopsy_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_autopsy(docs)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("autopsy_exists=true", result.stdout)


    def test_step2_validates_optional_ontology_and_ledger_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_ontology(docs)
            write_ledger(docs)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("ontology_exists=true", result.stdout)
            self.assertIn("ledger_exists=true", result.stdout)

    def test_step2_accepts_legacy_and_v2_ledger_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_ledger(docs, version=1)
            legacy_result = run_validator(Path(temp_dir), "step2")
            self.assertEqual(legacy_result.returncode, 0, legacy_result.stdout + legacy_result.stderr)
            self.assertIn("warning=legacy_ledger_schema=Planner-docs/Planing-Ledger.md", legacy_result.stdout)

            write_ledger(docs, version=2)
            v2_result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(v2_result.returncode, 0, v2_result.stdout + v2_result.stderr)
            self.assertIn("ledger_schema=v2", v2_result.stdout)

    def test_step2_validates_optional_project_comprehension_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_comprehension(docs)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("comprehension_exists=true", result.stdout)

    def test_step2_rejects_optional_comprehension_heading_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            bad_headings = COMPREHENSION_HEADINGS.copy()
            bad_headings[2], bad_headings[3] = bad_headings[3], bad_headings[2]
            write_comprehension(docs, headings=bad_headings)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("heading_out_of_order=Planner-docs/Project-Comprehension.md", result.stdout)

    def test_strict_comprehension_rejects_headings_only_and_bad_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = Path(temp_dir) / "Planner-docs"
            docs.mkdir()
            write_main_plan(docs)
            write_autopsy(docs)
            lines: list[str] = []
            for heading in COMPREHENSION_HEADINGS:
                lines += [heading, ""]
            (docs / "Project-Comprehension.md").write_text("\n".join(lines), encoding="utf-8")
            headings_only = run_validator(Path(temp_dir), "autopsy", strict=True)
            self.assertNotEqual(headings_only.returncode, 0, headings_only.stdout + headings_only.stderr)
            self.assertIn("strict_warning=comprehension_missing_question=Planner-docs/Project-Comprehension.md", headings_only.stdout)
            self.assertIn("strict_warning=comprehension_missing_evidence_row=Planner-docs/Project-Comprehension.md", headings_only.stdout)

            write_comprehension(
                docs,
                trace_marker="NOT_APPLICABLE:",
                architecture_marker="UNKNOWN: relation cannot be inferred.",
                hypothesis_marker="NO_UNRESOLVED_HYPOTHESES:",
            )
            bad_markers = run_validator(Path(temp_dir), "autopsy", strict=True)
            self.assertNotEqual(bad_markers.returncode, 0, bad_markers.stdout + bad_markers.stderr)
            self.assertIn("strict_warning=invalid_not_applicable_marker=Planner-docs/Project-Comprehension.md::## 3. Domain-to-Code Trace Map", bad_markers.stdout)
            self.assertIn("strict_warning=unknown_marker_missing_next_probe=Planner-docs/Project-Comprehension.md::## 5. Intended vs Implemented Architecture", bad_markers.stdout)
            self.assertIn("strict_warning=invalid_no_unresolved_hypotheses_marker=Planner-docs/Project-Comprehension.md", bad_markers.stdout)

    def test_comprehension_claim_class_evidence_rules(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_comprehension(
                docs,
                claim_type="structural",
                evidence_confidence="confirmed",
                evidence_type="source",
                evidence_source="plugins/antigravityqb/.antigravity-plugin/plugin.json",
            )
            structural = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(structural.returncode, 0, structural.stdout + structural.stderr)

            write_comprehension(
                docs,
                claim_type="behavioral",
                evidence_confidence="confirmed",
                evidence_type="source",
                evidence_source="src/service.py",
            )
            behavioral = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(behavioral.returncode, 0, behavioral.stdout + behavioral.stderr)
            self.assertIn("strict_warning=confirmed_behavioral_claim_needs_test_or_runtime=Planner-docs/Project-Comprehension.md::EV-01", behavioral.stdout)

            write_comprehension(
                docs,
                claim_type="historical",
                evidence_confidence="confirmed",
                evidence_type="source",
                evidence_source="src/service.py",
            )
            historical = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(historical.returncode, 0, historical.stdout + historical.stderr)
            self.assertIn("strict_warning=historical_claim_requires_history_evidence=Planner-docs/Project-Comprehension.md::EV-01", historical.stdout)

            write_comprehension(
                docs,
                evidence_confidence="tentative",
                hypothesis_next_probe="",
            )
            tentative = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(tentative.returncode, 0, tentative.stdout + tentative.stderr)
            self.assertIn("strict_warning=open_hypothesis_missing_next_probe=Planner-docs/Project-Comprehension.md::HYP-01", tentative.stdout)

    def test_heading_parser_ignores_fenced_code_and_detects_duplicate_headings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            fenced = [
                "```markdown",
                "# Project Ontology",
                "## 1. Purpose",
                "## 2. Domain Vocabulary",
                "## 3. Core Entities and Concepts",
                "## 4. Module and Boundary Map",
                "## 5. Workflows and Lifecycles",
                "## 6. Integrations and External Systems",
                "## 7. Invariants and Constraints",
                "## 8. Open Ontology Questions",
                "```",
            ]
            (docs / "Project-Ontology.md").write_text("\n".join(fenced), encoding="utf-8")
            fenced_result = run_validator(Path(temp_dir), "step2")
            self.assertNotEqual(fenced_result.returncode, 0, fenced_result.stdout + fenced_result.stderr)
            self.assertIn("missing_heading=Planner-docs/Project-Ontology.md::# Project Ontology", fenced_result.stdout)

            write_ontology(
                docs,
                headings=[
                    "# Project Ontology",
                    "## 1. Purpose",
                    "## 1. Purpose",
                    "## 2. Domain Vocabulary",
                    "## 3. Core Entities and Concepts",
                    "## 4. Module and Boundary Map",
                    "## 5. Workflows and Lifecycles",
                    "## 6. Integrations and External Systems",
                    "## 7. Invariants and Constraints",
                    "## 8. Open Ontology Questions",
                ],
            )
            duplicate_result = run_validator(Path(temp_dir), "step2")
            self.assertNotEqual(duplicate_result.returncode, 0, duplicate_result.stdout + duplicate_result.stderr)
            self.assertIn("duplicate_heading=Planner-docs/Project-Ontology.md::## 1. Purpose::2", duplicate_result.stdout)

    def test_comprehension_invalid_statuses_warn_and_strict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_comprehension(
                docs,
                evidence_confidence="certain",
                evidence_type="guess",
                architecture_status="aligned",
            )
            relaxed = run_validator(Path(temp_dir), "step2")
            self.assertEqual(relaxed.returncode, 0, relaxed.stdout + relaxed.stderr)
            self.assertIn("warning=invalid_evidence_type=Planner-docs/Project-Comprehension.md::guess", relaxed.stdout)
            self.assertIn("warning=invalid_confidence=Planner-docs/Project-Comprehension.md::certain", relaxed.stdout)
            self.assertIn("warning=invalid_architecture_status=Planner-docs/Project-Comprehension.md::aligned", relaxed.stdout)

            strict = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(strict.returncode, 0, strict.stdout + strict.stderr)
            self.assertIn("strict_warning=invalid_evidence_type=Planner-docs/Project-Comprehension.md::guess", strict.stdout)

    def test_comprehension_quality_warnings_fail_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_comprehension(
                docs,
                evidence_source="",
                trace_entry="unknown",
                trace_core="unknown",
                trace_tests="unknown",
                hypothesis_next_probe="",
            )
            relaxed = run_validator(Path(temp_dir), "step2")
            self.assertEqual(relaxed.returncode, 0, relaxed.stdout + relaxed.stderr)
            self.assertIn("warning=high_confidence_without_evidence=Planner-docs/Project-Comprehension.md::EV-01", relaxed.stdout)
            self.assertIn("warning=trace_missing_code_or_test_anchor=Planner-docs/Project-Comprehension.md::TRACE-01", relaxed.stdout)
            self.assertIn("warning=open_hypothesis_missing_next_probe=Planner-docs/Project-Comprehension.md::HYP-01", relaxed.stdout)

            strict = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(strict.returncode, 0, strict.stdout + strict.stderr)
            self.assertIn("strict_warning=high_confidence_without_evidence=Planner-docs/Project-Comprehension.md::EV-01", strict.stdout)

    def test_ledger_v2_status_semantics_and_step4_legacy_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_ledger(docs, version=2, status="banana")
            invalid = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)
            self.assertIn("strict_warning=invalid_ledger_status=Planner-docs/Planing-Ledger.md::banana", invalid.stdout)

            write_ledger(docs, version=2, status="in_progress", run_id="")
            in_progress = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(in_progress.returncode, 0, in_progress.stdout + in_progress.stderr)
            self.assertIn("strict_warning=ledger_in_progress_missing_run_id=Planner-docs/Planing-Ledger.md::Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", in_progress.stdout)

            write_ledger(docs, version=2, status="superseded", superseded_by="")
            superseded = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(superseded.returncode, 0, superseded.stdout + superseded.stderr)
            self.assertIn("strict_warning=ledger_superseded_missing_target=Planner-docs/Planing-Ledger.md::Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", superseded.stdout)

            write_audit(docs, "PASS")
            write_ledger(docs, version=1)
            legacy_step4 = run_validator(Path(temp_dir), "step4", strict=True)
            self.assertNotEqual(legacy_step4.returncode, 0, legacy_step4.stdout + legacy_step4.stderr)
            self.assertIn("legacy_ledger_requires_v2_for_step4=Planner-docs/Planing-Ledger.md", legacy_step4.stdout)

    def test_ontology_competency_question_status_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_ontology_with_competency_status(docs, "answered")
            valid = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

            write_ontology_with_competency_status(docs, "resolved")
            invalid = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)
            self.assertIn("strict_warning=invalid_ontology_question_status=Planner-docs/Project-Ontology.md::resolved", invalid.stdout)

    def test_step2_rejects_optional_ontology_heading_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_ontology(docs, headings=["# Project Ontology", "## 2. Domain Vocabulary", "## 1. Purpose"])
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("heading_out_of_order=Planner-docs/Project-Ontology.md", result.stdout)

    def test_step2_rejects_autopsy_heading_order_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            bad_headings = AUTOPSY_HEADINGS.copy()
            bad_headings[3], bad_headings[4] = bad_headings[4], bad_headings[3]
            write_autopsy(docs, headings=bad_headings)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("heading_out_of_order=Planner-docs/Autopsy.md", result.stdout)

    def test_roadmap_table_ignores_historical_phase_mentions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("main_phase_count=2", result.stdout)
            self.assertNotIn("Faz-10-Plans", result.stdout)
            self.assertNotIn("Faz-11-Plans", result.stdout)

    def test_placeholder_safe_and_example_placeholder_are_not_false_positive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("placeholder_text=", result.stdout)

    def test_relative_index_refs_are_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir), relative_refs=True)
            result = run_validator(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("index_reference_count=2", result.stdout)

    def test_long_secret_is_detected_but_short_task_spec_like_text_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            (docs / "task-spec.yaml").write_text("name: task-spec.yaml\nexample: sk-short\n", encoding="utf-8")
            short_result = run_validator(Path(temp_dir), "step2")
            self.assertEqual(short_result.returncode, 0, short_result.stdout + short_result.stderr)
            self.assertIn("secret_findings=0", short_result.stdout)

            (docs / "leak.md").write_text("fake test token: sk-" + "A" * 24 + "\n", encoding="utf-8")
            long_result = run_validator(Path(temp_dir), "step2")
            self.assertNotEqual(long_result.returncode, 0, long_result.stdout + long_result.stderr)
            self.assertIn("secret_pattern=openai_api_key", long_result.stdout)
            self.assertNotIn("A" * 24, long_result.stdout)

    def test_openrouter_secret_is_detected_but_placeholders_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            env_name = "OPENROUTER" + "_API_KEY"
            (docs / "safe-env.md").write_text(
                "\n".join(
                    [
                        f"{env_name}=your_openrouter_api_key",
                        f"{env_name}=<redacted>",
                        f"{env_name}=${env_name}",
                    ]
                ),
                encoding="utf-8",
            )
            placeholder_result = run_validator(Path(temp_dir), "step2")
            self.assertEqual(placeholder_result.returncode, 0, placeholder_result.stdout + placeholder_result.stderr)

            fake_key = "sk-or-v1-" + "B" * 64
            (docs / "leak.md").write_text(f"{env_name}={fake_key}\n", encoding="utf-8")
            leak_result = run_validator(Path(temp_dir), "step2")
            self.assertNotEqual(leak_result.returncode, 0, leak_result.stdout + leak_result.stderr)
            self.assertIn("secret_pattern=openrouter_api_key", leak_result.stdout)
            self.assertNotIn(fake_key, leak_result.stdout)

    def test_step4_missing_audit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("missing_file=Planner-docs/Sub-Planing-Audit.md", result.stdout)

    def test_step3_preflight_passes_without_audit_but_step3_requires_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            preflight = run_validator(Path(temp_dir), "step3-preflight", strict=True)
            self.assertEqual(preflight.returncode, 0, preflight.stdout + preflight.stderr)
            self.assertIn("audit_exists=false", preflight.stdout)

            post_audit = run_validator(Path(temp_dir), "step3", strict=True)
            self.assertNotEqual(post_audit.returncode, 0, post_audit.stdout + post_audit.stderr)
            self.assertIn("missing_file=Planner-docs/Sub-Planing-Audit.md", post_audit.stdout)

    def test_step4_headings_only_audit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            lines: list[str] = []
            for heading in AUDIT_HEADINGS:
                lines += [heading, ""]
                if heading == "## 1. Audit Summary":
                    lines += ["Audit status: PASS", ""]
                if heading == "## 15. Audit Result":
                    lines += ["Final status: PASS", ""]
            (docs / "Sub-Planing-Audit.md").write_text("\n".join(lines), encoding="utf-8")
            result = run_validator(Path(temp_dir), "step4", strict=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("audit_readiness_table_missing=Planner-docs/Sub-Planing-Audit.md", result.stdout)
            self.assertIn("empty_or_too_short_audit_section=Planner-docs/Sub-Planing-Audit.md::## 2. Reviewed Sources", result.stdout)

    def test_step4_blocked_audit_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "BLOCKED")
            result = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("step4_blocked_by_audit_status=BLOCKED", result.stdout)

    def test_step4_pass_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "PASS")
            result = run_validator(Path(temp_dir), "step4")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("audit_status=PASS", result.stdout)
            self.assertIn("execution_queue_state=READY", result.stdout)

    def test_step4_no_action_required_passes_without_ready_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(
                docs,
                "PASS",
                readiness_rows=[
                    "| Sub-Plan Path | Status | Finding IDs | Dependency State | Reason | Required Repair |",
                    "|---|---|---|---|---|---|",
                    "| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | COMPLETE | none | satisfied | Already verified in ledger. | none |",
                    "| Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md | SUPERSEDED | none | satisfied | Replaced by later plan. | none |",
                ],
            )
            result = run_validator(Path(temp_dir), "step4", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("execution_queue_state=NO_ACTION_REQUIRED", result.stdout)

    def test_step4_pass_with_warnings_blocks_on_p0_or_p1(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(
                docs,
                "PASS_WITH_WARNINGS",
                ["| AUDIT-FIX-01 | P1 | open | Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | repair before implementation | Fix before Step 4. |"],
            )
            result = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("step4_blocked_by_high_severity_findings=P0:0,P1:1", result.stdout)

    def test_step4_pass_with_only_p2_or_p3_warns_but_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(
                docs,
                "PASS_WITH_WARNINGS",
                ["| AUDIT-FIX-02 | P2 | open | Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | nonblocking wording repair | Track during Step 4. |"],
                readiness_rows=[
                    "| Sub-Plan Path | Status | Finding IDs | Dependency State | Reason | Required Repair |",
                    "|---|---|---|---|---|---|",
                    "| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | READY_WITH_WARNINGS | AUDIT-FIX-02 | independent | Contract complete with warning. | none |",
                ],
            )
            result = run_validator(Path(temp_dir), "step4")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("warning=step4_has_nonblocking_warnings=P2:1,P3:0", result.stdout)

    def test_step4_pass_rejects_open_p2_but_accepts_resolved_p2(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(
                docs,
                "PASS",
                ["| AUDIT-FIX-02 | P2 | open | Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | nonblocking wording repair | Track during Step 4. |"],
            )
            open_result = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(open_result.returncode, 0, open_result.stdout + open_result.stderr)
            self.assertIn("audit_status_inconsistent_with_open_warnings=PASS::P2:1,P3:0", open_result.stdout)

            write_audit(
                docs,
                "PASS",
                ["| AUDIT-FIX-02 | P2 | resolved | Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | nonblocking wording repair | none |"],
            )
            resolved_result = run_validator(Path(temp_dir), "step4", strict=True)
            self.assertEqual(resolved_result.returncode, 0, resolved_result.stdout + resolved_result.stderr)
            self.assertIn("p2_findings=0", resolved_result.stdout)

    def test_step4_readiness_rejects_unsafe_unknown_or_conflicting_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            scenarios = [
                ("absolute", "/tmp/Faz1.1-local-contract.md", "READY", "independent", "unsafe_subplan_path"),
                ("traversal", "../Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", "READY", "independent", "unsafe_subplan_path"),
                ("missing", "Planner-docs/Faz-1-Plans/Faz1.99-missing.md", "READY", "independent", "missing_readiness_subplan"),
                ("unknown_status", "Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", "BANANA", "independent", "invalid_readiness_status"),
                ("blocked_dependency", "Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md", "READY", "blocked", "ready_row_has_blocked_dependency"),
            ]
            for label, path, status, dependency, expected in scenarios:
                write_audit(
                    docs,
                    "PASS",
                    readiness_rows=[
                        "| Sub-Plan Path | Status | Finding IDs | Dependency State | Reason | Required Repair |",
                        "|---|---|---|---|---|---|",
                        f"| {path} | {status} | none | {dependency} | {label} case. | none |",
                    ],
                )
                result = run_validator(Path(temp_dir), "step4")
                self.assertNotEqual(result.returncode, 0, label + result.stdout + result.stderr)
                self.assertIn(expected, result.stdout, label)

            write_audit(
                docs,
                "PASS_WITH_WARNINGS",
                readiness_rows=[
                    "| Sub-Plan Path | Status | Finding IDs | Dependency State | Reason | Required Repair |",
                    "|---|---|---|---|---|---|",
                    "| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | READY | none | independent | First row. | none |",
                    "| Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md | BLOCKED | none | blocked | Second row. | Fix blocker. |",
                ],
            )
            duplicate = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(duplicate.returncode, 0, duplicate.stdout + duplicate.stderr)
            self.assertIn("conflicting_readiness_status=Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md::READY,BLOCKED", duplicate.stdout)

    def test_step4_pass_with_warnings_no_findings_text_does_not_count_as_findings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "PASS_WITH_WARNINGS", ["No P0/P1 findings. No P2/P3 findings."])
            result = run_validator(Path(temp_dir), "step4")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("p0_findings=0", result.stdout)
            self.assertIn("p1_findings=0", result.stdout)
            self.assertIn("p2_findings=0", result.stdout)
            self.assertIn("p3_findings=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
