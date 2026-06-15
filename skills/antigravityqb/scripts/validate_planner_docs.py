#!/usr/bin/env python3
"""Validate AntigravityQB Planner-docs outputs.

This helper is intentionally read-only. It checks the planning documents that
AntigravityQB generates without editing or normalizing them.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


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

ONTOLOGY_HEADINGS = [
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

LEDGER_HEADINGS = [
    "# Planing Ledger",
    "## 1. Purpose",
    "## 2. Planning Runs",
    "## 3. Implementation Runs",
    "## 4. Current State Snapshot",
    "## 5. Replanning Inputs",
    "## 6. Open Decisions and Follow-Ups",
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

FOLDER_RE = re.compile(r"^Faz-(\d+)-Plans$")
SUBPLAN_RE = re.compile(r"^Faz(\d+)\.(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
INDEX_REF_RE = re.compile(
    r"(?:\./)?(?:Planner-docs/)?Faz-\d+-Plans/Faz\d+\.\d+-[a-z0-9]+(?:-[a-z0-9]+)*\.md"
)
MAIN_PHASE_RE = re.compile(r"\b(?:Faz|Phase|Stage)\s*-?\s*(\d+)\b", re.IGNORECASE)
ROADMAP_HEADING = "## 6. Phase-Based Master Roadmap"
ROADMAP_TABLE_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|", re.MULTILINE)
ROADMAP_HEADING_PHASE_RE = re.compile(r"^#{3,6}\s*(?:Faz|Phase|Stage)\s*-?\s*(\d+)\b", re.MULTILINE | re.IGNORECASE)
H1_SUBPLAN_RE = re.compile(r"^# Faz\s+(\d+)\.(\d+)\s+[—-]\s+.+$", re.MULTILINE)
SECTION_RE = re.compile(r"^(##\s+\d+\.\s+.+)$", re.MULTILINE)
AUDIT_FIX_RE = re.compile(
    r"^\s*(?:[-*]\s*)?\|?\s*(AUDIT-FIX-\d+)\s*(?:\||:|\u2014|\u2013|-)\s*(P0|P1|P2|P3)\b",
    re.MULTILINE,
)

SECRET_PATTERNS = [
    (
        "openrouter_api_key",
        re.compile(
            r"\bsk-or-v1-[A-Za-z0-9_-]{20,}\b"
            r"|OPENROUTER_API_KEY\s*=\s*"
            r"(?!(?:['\"]?(?:\$OPENROUTER_API_KEY|<redacted>|your_openrouter_api_key)['\"]?)(?:\s|$))"
            r"[^\s#]+",
            re.IGNORECASE,
        ),
    ),
    ("openai_api_key", re.compile(r"\bsk-(?!or-v1-)[A-Za-z0-9_-]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("github_legacy_pat", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private_key", re.compile(r"BEGIN (?:RSA|OPENSSH|DSA|EC|PRIVATE) KEY")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
]

PLACEHOLDER_PATTERNS = [
    ("todo", re.compile(r"\bTODO\b", re.IGNORECASE)),
    ("tbd", re.compile(r"\bTBD\b", re.IGNORECASE)),
    ("fixme", re.compile(r"\bFIXME\b", re.IGNORECASE)),
    ("lorem_ipsum", re.compile(r"\blorem ipsum\b", re.IGNORECASE)),
    ("to_be_filled", re.compile(r"\bto be filled\b|\bto_be_filled\b", re.IGNORECASE)),
    ("angle_placeholder", re.compile(r"<(?:TODO|TBD|PLACEHOLDER|TO_BE_FILLED)[^>]*>", re.IGNORECASE)),
    ("brace_placeholder", re.compile(r"\{\{[^{}]*(?:TODO|TBD|PLACEHOLDER|TO_BE_FILLED)[^{}]*\}\}", re.IGNORECASE)),
]

REPEATED_SENTENCE_MIN_COUNT = 5
REPEATED_SENTENCE_MIN_LENGTH = 80
ALLOWED_REPEATED_SENTENCE_FRAGMENTS = (
    "secret",
    "token",
    "credential",
    "private key",
    "local env",
    "source code",
    "config, test",
    "planning file",
    "planning files",
    "real secret",
)


@dataclass
class ValidationState:
    root: Path
    mode: str
    strict: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, int | str] = field(default_factory=dict)

    @property
    def planner_docs(self) -> Path:
        return self.root / "Planner-docs"

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def read_text(path: Path, state: ValidationState) -> str | None:
    if not path.exists():
        state.error(f"missing_file={state.rel(path)}")
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        state.error(f"non_utf8_file={state.rel(path)}")
    except OSError as exc:
        state.error(f"read_error={state.rel(path)}:{exc}")
    return None


def validate_heading_order(text: str, headings: list[str], path: Path, state: ValidationState) -> None:
    last_pos = -1
    for heading in headings:
        pos = text.find(heading)
        if pos == -1:
            state.error(f"missing_heading={state.rel(path)}::{heading}")
            continue
        if pos < last_pos:
            state.error(f"heading_out_of_order={state.rel(path)}::{heading}")
        last_pos = pos


def markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    body_start = start + len(heading)
    next_match = re.search(r"^##\s+\d+\.\s+", text[body_start:], flags=re.MULTILINE)
    body_end = body_start + next_match.start() if next_match else len(text)
    return text[body_start:body_end].strip()


def extract_main_phase_numbers(text: str) -> list[int]:
    roadmap = markdown_section(text, ROADMAP_HEADING)
    if roadmap:
        table_numbers = sorted({int(match.group(1)) for match in ROADMAP_TABLE_ROW_RE.finditer(roadmap)})
        if table_numbers:
            return table_numbers

        heading_numbers = sorted({int(match.group(1)) for match in ROADMAP_HEADING_PHASE_RE.finditer(roadmap)})
        if heading_numbers:
            return heading_numbers

        return sorted({int(match.group(1)) for match in MAIN_PHASE_RE.finditer(roadmap)})

    return []


def collect_phase_folders(state: ValidationState) -> dict[int, Path]:
    folders: dict[int, Path] = {}
    if not state.planner_docs.exists():
        state.error("missing_directory=Planner-docs")
        return folders

    for folder in sorted(state.planner_docs.glob("Faz-*-Plans")):
        if not folder.is_dir():
            continue
        match = FOLDER_RE.match(folder.name)
        if not match:
            state.error(f"invalid_phase_folder={state.rel(folder)}")
            continue
        phase = int(match.group(1))
        if phase in folders:
            state.error(f"duplicate_phase_folder=Faz-{phase}-Plans")
        folders[phase] = folder
    return folders


def collect_subplans(state: ValidationState) -> list[tuple[int | None, int | None, Path]]:
    result: list[tuple[int | None, int | None, Path]] = []
    for folder in sorted(state.planner_docs.glob("Faz-*-Plans")):
        if not folder.is_dir():
            continue
        folder_match = FOLDER_RE.match(folder.name)
        folder_phase = int(folder_match.group(1)) if folder_match else None
        for path in sorted(folder.glob("*.md")):
            match = SUBPLAN_RE.match(path.name)
            if not match:
                state.error(f"invalid_subplan_filename={state.rel(path)}")
                result.append((folder_phase, None, path))
                continue
            file_phase = int(match.group(1))
            subphase = int(match.group(2))
            if folder_phase is not None and file_phase != folder_phase:
                state.error(
                    f"folder_file_phase_mismatch={state.rel(path)}::folder={folder_phase}::file={file_phase}"
                )
            result.append((file_phase, subphase, path))
    return result


def section_body(text: str, heading: str) -> str:
    return markdown_section(text, heading)


def normalized_body(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", compact) if item.strip()]


def is_allowed_repeated_sentence(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(fragment in lowered for fragment in ALLOWED_REPEATED_SENTENCE_FRAGMENTS)


def add_repeated_sentence_candidates(
    state: ValidationState,
    path: Path,
    text: str,
    repeated_sentences: dict[str, list[str]],
) -> None:
    for sentence in split_sentences(text):
        if len(sentence) < REPEATED_SENTENCE_MIN_LENGTH:
            continue
        if is_allowed_repeated_sentence(sentence):
            continue
        repeated_sentences[sentence].append(state.rel(path))


def validate_step1(state: ValidationState) -> list[int]:
    main_path = state.planner_docs / "Main-Planing.md"
    text = read_text(main_path, state)
    if text is None:
        state.metrics["main_phase_count"] = 0
        return []

    validate_heading_order(text, STEP1_HEADINGS, main_path, state)
    phases = extract_main_phase_numbers(text)
    state.metrics["main_phase_count"] = len(phases)
    if not phases:
        state.error("main_plan_has_no_detected_phases=Planner-docs/Main-Planing.md")
    return phases


def validate_autopsy_optional(state: ValidationState) -> None:
    autopsy_path = state.planner_docs / "Autopsy.md"
    state.metrics["autopsy_exists"] = "true" if autopsy_path.exists() else "false"
    if not autopsy_path.exists():
        return

    text = read_text(autopsy_path, state)
    if text is None:
        return

    validate_heading_order(text, AUTOPSY_HEADINGS, autopsy_path, state)


def validate_autopsy_required(state: ValidationState) -> None:
    autopsy_path = state.planner_docs / "Autopsy.md"
    state.metrics["autopsy_exists"] = "true" if autopsy_path.exists() else "false"
    if not autopsy_path.exists():
        state.error("missing_file=Planner-docs/Autopsy.md")
        return

    text = read_text(autopsy_path, state)
    if text is not None:
        validate_heading_order(text, AUTOPSY_HEADINGS, autopsy_path, state)


def validate_optional_continuity_docs(state: ValidationState) -> None:
    ontology_path = state.planner_docs / "Project-Ontology.md"
    ledger_path = state.planner_docs / "Planing-Ledger.md"

    state.metrics["ontology_exists"] = "true" if ontology_path.exists() else "false"
    state.metrics["ledger_exists"] = "true" if ledger_path.exists() else "false"

    if ontology_path.exists():
        text = read_text(ontology_path, state)
        if text is not None:
            validate_heading_order(text, ONTOLOGY_HEADINGS, ontology_path, state)

    if ledger_path.exists():
        text = read_text(ledger_path, state)
        if text is not None:
            validate_heading_order(text, LEDGER_HEADINGS, ledger_path, state)


def validate_index(state: ValidationState) -> set[str]:
    index_path = state.planner_docs / "Sub-Planing-Index.md"
    text = read_text(index_path, state)
    if text is None:
        state.metrics["index_reference_count"] = 0
        return set()

    validate_heading_order(text, INDEX_HEADINGS, index_path, state)
    refs = set()
    for match in INDEX_REF_RE.finditer(text):
        ref = match.group(0)
        if ref.startswith("./"):
            ref = ref[2:]
        if not ref.startswith("Planner-docs/"):
            ref = f"Planner-docs/{ref}"
        refs.add(ref)
    state.metrics["index_reference_count"] = len(refs)
    return refs


def validate_subplan_structure(
    state: ValidationState,
    phase: int | None,
    subphase: int | None,
    path: Path,
    repeated_bodies: dict[str, list[str]],
    repeated_sentences: dict[str, list[str]],
) -> None:
    text = read_text(path, state)
    if text is None:
        return

    h1_match = H1_SUBPLAN_RE.search(text)
    if not h1_match:
        state.error(f"missing_or_invalid_h1={state.rel(path)}")
    else:
        h1_phase = int(h1_match.group(1))
        h1_subphase = int(h1_match.group(2))
        if phase is not None and h1_phase != phase:
            state.error(f"h1_phase_mismatch={state.rel(path)}::h1={h1_phase}::file={phase}")
        if subphase is not None and h1_subphase != subphase:
            state.error(f"h1_subphase_mismatch={state.rel(path)}::h1={h1_subphase}::file={subphase}")

    validate_heading_order(text, SUBPLAN_HEADINGS, path, state)

    headings = SECTION_RE.findall(text)
    for required in SUBPLAN_HEADINGS:
        count = headings.count(required)
        if count > 1:
            state.error(f"duplicate_heading={state.rel(path)}::{required}::{count}")
        body = section_body(text, required)
        if required in text and len(body) < 20:
            state.error(f"empty_or_too_short_section={state.rel(path)}::{required}")
        for pattern_name, pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(body):
                state.warning(f"placeholder_text={state.rel(path)}::{required}::pattern={pattern_name}")

    for heading in ("## 3. Description", "## 7. Planned Work Breakdown"):
        body = normalized_body(section_body(text, heading))
        if len(body) >= 160:
            repeated_bodies[f"{heading}:{body}"].append(state.rel(path))

    for heading in (
        "## 3. Description",
        "## 6. Current Repository Evidence",
        "## 8. Acceptance Criteria",
        "## 11. Risks and Mitigations",
    ):
        add_repeated_sentence_candidates(state, path, section_body(text, heading), repeated_sentences)


def validate_step2(state: ValidationState) -> None:
    main_phases = validate_step1(state)
    validate_autopsy_optional(state)
    validate_optional_continuity_docs(state)
    index_refs = validate_index(state)
    folders = collect_phase_folders(state)
    subplans = collect_subplans(state)

    state.metrics["phase_folder_count"] = len(folders)
    state.metrics["subplan_count"] = len([item for item in subplans if item[1] is not None])

    if main_phases:
        for phase in main_phases:
            if phase not in folders:
                state.error(f"missing_phase_folder=Planner-docs/Faz-{phase}-Plans")
        for phase in sorted(folders):
            if phase not in main_phases:
                state.warning(f"extra_phase_folder_without_main_phase=Planner-docs/Faz-{phase}-Plans")

    actual_refs = {state.rel(path) for _, subphase, path in subplans if subphase is not None}
    for ref in sorted(actual_refs - index_refs):
        state.error(f"unindexed_subplan={ref}")
    for ref in sorted(index_refs - actual_refs):
        state.error(f"missing_index_target={ref}")

    seen: set[tuple[int, int]] = set()
    per_phase: dict[int, list[int]] = defaultdict(list)
    repeated_bodies: dict[str, list[str]] = defaultdict(list)
    repeated_sentences: dict[str, list[str]] = defaultdict(list)

    for phase, subphase, path in subplans:
        if phase is None or subphase is None:
            continue
        key = (phase, subphase)
        if key in seen:
            state.error(f"duplicate_subplan_number=Faz{phase}.{subphase}")
        seen.add(key)
        per_phase[phase].append(subphase)
        validate_subplan_structure(state, phase, subphase, path, repeated_bodies, repeated_sentences)

    for phase, folder in sorted(folders.items()):
        numbers = sorted(per_phase.get(phase, []))
        if not numbers:
            state.error(f"phase_has_no_subplans={state.rel(folder)}")
            continue
        expected = list(range(1, max(numbers) + 1))
        if numbers != expected:
            state.error(f"subplan_numbering_gap=Faz{phase}::expected={expected}::actual={numbers}")

    for key, paths in sorted(repeated_bodies.items()):
        if len(paths) >= 3:
            heading = key.split(":", 1)[0]
            joined = ",".join(paths)
            state.warning(f"repeated_section_body={heading}::files={joined}")

    for sentence, paths in sorted(repeated_sentences.items()):
        if len(paths) >= REPEATED_SENTENCE_MIN_COUNT:
            preview = sentence[:120].replace("=", "-")
            joined = ",".join(paths[:10])
            state.warning(f"repeated_boilerplate_sentence=count:{len(paths)}::text={preview}::files={joined}")


def validate_step3_preflight(state: ValidationState) -> None:
    validate_step2(state)
    audit_path = state.planner_docs / "Sub-Planing-Audit.md"
    state.metrics["audit_exists"] = "true" if audit_path.exists() else "false"
    if state.mode == "all" and not audit_path.exists():
        state.error("missing_file=Planner-docs/Sub-Planing-Audit.md")
    if audit_path.exists():
        text = read_text(audit_path, state)
        if text is not None:
            validate_heading_order(text, AUDIT_HEADINGS, audit_path, state)


def extract_audit_status(text: str) -> str | None:
    status_pattern = re.compile(
        r"(?:overall audit status|audit status|final status|status|denetim durumu|nihai durum)"
        r"\s*[:：-]\s*(PASS_WITH_WARNINGS|BLOCKED|PASS)\b",
        re.IGNORECASE,
    )
    match = status_pattern.search(text)
    if match:
        return match.group(1).upper()

    for line in text.splitlines():
        stripped = line.strip(" -*`|:")
        if stripped in {"PASS", "PASS_WITH_WARNINGS", "BLOCKED"}:
            return stripped
    return None


def count_audit_severities(text: str) -> dict[str, int]:
    fix_section = markdown_section(text, "## 13. Priority Fix List")
    counts = {severity: 0 for severity in ("P0", "P1", "P2", "P3")}
    for _, severity in AUDIT_FIX_RE.findall(fix_section):
        counts[severity] += 1
    return counts


def validate_step4_readiness(state: ValidationState) -> None:
    validate_step3_preflight(state)
    audit_path = state.planner_docs / "Sub-Planing-Audit.md"
    text = read_text(audit_path, state)
    if text is None:
        state.metrics["audit_status"] = "missing"
        return

    status = extract_audit_status(text)
    state.metrics["audit_status"] = status or "unknown"
    if status is None:
        state.error("audit_status_missing=Planner-docs/Sub-Planing-Audit.md")
    elif status == "BLOCKED":
        state.error("step4_blocked_by_audit_status=BLOCKED")

    severity_counts = count_audit_severities(text)
    for severity, count in severity_counts.items():
        state.metrics[f"{severity.lower()}_findings"] = count
    if severity_counts["P0"] or severity_counts["P1"]:
        state.error(
            f"step4_blocked_by_high_severity_findings=P0:{severity_counts['P0']},P1:{severity_counts['P1']}"
        )
    if status == "PASS_WITH_WARNINGS" and (severity_counts["P2"] or severity_counts["P3"]):
        state.warning(
            f"step4_has_nonblocking_warnings=P2:{severity_counts['P2']},P3:{severity_counts['P3']}"
        )


def scan_secrets(state: ValidationState) -> None:
    secret_findings = 0
    root = state.planner_docs if state.planner_docs.exists() else state.root
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                secret_findings += 1
                line = text.count("\n", 0, match.start()) + 1
                state.error(f"secret_pattern={name}::{state.rel(path)}:{line}")
    state.metrics["secret_findings"] = secret_findings


def finalize(state: ValidationState) -> int:
    if state.strict:
        for warning in state.warnings:
            state.errors.append(f"strict_warning={warning}")

    state.metrics["warning_count"] = len(state.warnings)
    state.metrics["error_count"] = len(state.errors)

    status = "failed" if state.errors else "passed"
    print(f"planner_docs_validation={status}")
    print(f"mode={state.mode}")
    print(f"root={state.root}")
    for key in sorted(state.metrics):
        print(f"{key}={state.metrics[key]}")
    for warning in sorted(state.warnings):
        print(f"warning={warning}")
    for error in sorted(state.errors):
        print(f"error={error}")
    return 1 if state.errors else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AntigravityQB Planner-docs outputs.")
    parser.add_argument("--root", default=".", help="Project root containing Planner-docs/; default: current directory.")
    parser.add_argument(
        "--mode",
        choices=("step1", "autopsy", "step2", "step3", "step4", "all"),
        default="all",
        help="Validation scope.",
    )
    parser.add_argument("--strict", action="store_true", help="Treat quality warnings as failures.")
    return parser.parse_args(argv)


def run_validation(root: Path, mode: str, strict: bool = False) -> int:
    state = ValidationState(root=root.resolve(), mode=mode, strict=strict)

    if mode == "step1":
        validate_step1(state)
    elif mode == "autopsy":
        validate_step1(state)
        validate_autopsy_required(state)
        validate_optional_continuity_docs(state)
    elif mode == "step2":
        validate_step2(state)
    elif mode in {"step3", "all"}:
        validate_step3_preflight(state)
    elif mode == "step4":
        validate_step4_readiness(state)
    else:
        state.error(f"unknown_mode={mode}")

    scan_secrets(state)
    return finalize(state)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return run_validation(Path(args.root), args.mode, args.strict)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
