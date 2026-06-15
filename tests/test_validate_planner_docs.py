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

INDEX_HEADINGS = [
    "# Sub-Planing Index",
    "## 1. Purpose",
    "## 2. Source Main Plan",
    "## 3. Phase and Sub-Plan Map",
    "## 4. Priority Detailing Order",
    "## 5. Out-of-Scope or Deferred Topics",
    "## 6. Coverage Check",
    "## 7. Repository Review Notes",
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
    lines = [f"# Faz {phase}.{subphase} — Test Sub-Plan", ""]
    for heading in SUBPLAN_HEADINGS:
        text = body(heading)
        if heading == "## 6. Current Repository Evidence":
            text += " `configs/example.placeholder` is a normal example filename."
        if heading == "## 11. Risks and Mitigations":
            text += " placeholder-safe command wording is not a real placeholder."
        lines += [heading, "", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_index(docs: Path, relative_refs: bool = False) -> None:
    refs = [
        "Faz-1-Plans/Faz1.1-local-contract.md",
        "./Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md",
    ] if relative_refs else [
        "Planner-docs/Faz-1-Plans/Faz1.1-local-contract.md",
        "Planner-docs/Faz-2-Plans/Faz2.1-live-gateway.md",
    ]

    lines: list[str] = []
    for heading in INDEX_HEADINGS:
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


def write_ledger(docs: Path, headings: list[str] | None = None) -> None:
    ledger_headings = headings or [
        "# Planing Ledger",
        "## 1. Purpose",
        "## 2. Planning Runs",
        "## 3. Implementation Runs",
        "## 4. Current State Snapshot",
        "## 5. Replanning Inputs",
        "## 6. Open Decisions and Follow-Ups",
    ]
    lines: list[str] = []
    for heading in ledger_headings:
        lines += [heading, "", body(heading), ""]
    (docs / "Planing-Ledger.md").write_text("\n".join(lines), encoding="utf-8")


def write_audit(docs: Path, status: str, fixes: list[str] | None = None) -> None:
    lines: list[str] = []
    for heading in AUDIT_HEADINGS:
        lines += [heading, "", body(heading), ""]
        if heading == "## 1. Audit Summary":
            lines += [f"Audit status: {status}", ""]
        if heading == "## 13. Priority Fix List":
            for fix in fixes or []:
                lines += [fix, ""]
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

    def test_cli_step2_success_smoke_uses_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_valid_step2_fixture(Path(temp_dir))
            result = run_validator_cli(Path(temp_dir), "step2", strict=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("planner_docs_validation=passed", result.stdout)

    def test_cli_step4_gate_smoke_uses_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "PASS_WITH_WARNINGS", ["- AUDIT-FIX-01 | P1 | repair before implementation"])
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

    def test_step4_pass_with_warnings_blocks_on_p0_or_p1(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "PASS_WITH_WARNINGS", ["- AUDIT-FIX-01 | P1 | repair before implementation"])
            result = run_validator(Path(temp_dir), "step4")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("step4_blocked_by_high_severity_findings=P0:0,P1:1", result.stdout)

    def test_step4_pass_with_only_p2_or_p3_warns_but_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs = write_valid_step2_fixture(Path(temp_dir))
            write_audit(docs, "PASS_WITH_WARNINGS", ["- AUDIT-FIX-02 | P2 | nonblocking wording repair"])
            result = run_validator(Path(temp_dir), "step4")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("warning=step4_has_nonblocking_warnings=P2:1,P3:0", result.stdout)

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
