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

LEDGER_LEGACY_HEADINGS = [
    "# Planing Ledger",
    "## 1. Purpose",
    "## 2. Planning Runs",
    "## 3. Implementation Runs",
    "## 4. Current State Snapshot",
    "## 5. Replanning Inputs",
    "## 6. Open Decisions and Follow-Ups",
]

LEDGER_V2_HEADINGS = [
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

LEDGER_HEADINGS = LEDGER_V2_HEADINGS

ARTIFACT_SCHEMA_VERSION = 2
HANDOFF_CONTRACT_VERSION = 1

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

ALLOWED_EVIDENCE_TYPES = {
    "source",
    "test",
    "runtime",
    "history",
    "configuration",
    "documentation",
    "user-confirmed",
}
ALLOWED_CONFIDENCE_VALUES = {"confirmed", "probable", "tentative", "contradicted"}
ALLOWED_CLAIM_TYPES = {
    "structural",
    "behavioral",
    "historical",
    "configuration",
    "user_intent",
    "architectural",
}
ALLOWED_ARCHITECTURE_STATUSES = {"convergent", "divergent", "absent", "unmodeled", "uncertain"}
ALLOWED_ONTOLOGY_QUESTION_STATUSES = {"answered", "partially_answered", "open", "contradicted"}
ALLOWED_LEDGER_STATUSES = {
    "planned",
    "ready",
    "ready_with_warnings",
    "in_progress",
    "implemented",
    "verified",
    "blocked",
    "superseded",
}
ALLOWED_FINDING_STATUSES = {"open", "accepted", "resolved", "not_applicable"}
OPEN_FINDING_STATUSES = {"open", "accepted"}
ALLOWED_READINESS_STATUSES = {
    "READY",
    "READY_WITH_WARNINGS",
    "NEEDS_REPAIR",
    "BLOCKED",
    "COMPLETE",
    "SUPERSEDED",
    "DEFERRED",
}
READY_READINESS_STATUSES = {"READY", "READY_WITH_WARNINGS"}
COMPLETED_READINESS_STATUSES = {"COMPLETE", "SUPERSEDED", "DEFERRED"}
ALLOWED_DEPENDENCY_STATES = {"satisfied", "independent", "blocked", "unknown"}
READINESS_HEADERS = [
    "Sub-Plan Path",
    "Status",
    "Finding IDs",
    "Dependency State",
    "Reason",
    "Required Repair",
]
FINDING_HEADERS = ["Finding ID", "Severity", "Status", "Affected Files", "Issue", "Required Action"]
LEDGER_V2_STATUS_HEADERS = [
    "Sub-plan Path",
    "Status",
    "Snapshot ID",
    "Run ID",
    "Validation Evidence",
    "Blocker",
    "Next Action",
    "Superseded By",
    "Updated At",
]
NOT_APPLICABLE_PREFIX = "NOT_APPLICABLE:"
NO_UNRESOLVED_HYPOTHESES_PREFIX = "NO_UNRESOLVED_HYPOTHESES:"
UNKNOWN_PREFIX = "UNKNOWN:"
UNKNOWN_CELL_VALUES = {"", "-", "n/a", "na", "none", "unknown", "unclear", "not found", "not evidenced"}


@dataclass(frozen=True)
class MarkdownHeading:
    text: str
    level: int
    line: int
    start: int
    end: int


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


def markdown_headings(text: str) -> list[MarkdownHeading]:
    headings: list[MarkdownHeading] = []
    in_fence = False
    fence_marker = ""
    offset = 0
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            offset += len(line)
            continue

        if not in_fence:
            raw = line.rstrip("\r\n")
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw)
            if match:
                heading_text = f"{match.group(1)} {match.group(2).strip()}"
                headings.append(
                    MarkdownHeading(
                        text=heading_text,
                        level=len(match.group(1)),
                        line=line_number,
                        start=offset,
                        end=offset + len(raw),
                    )
                )
        offset += len(line)
    return headings


def validate_heading_order(text: str, headings: list[str], path: Path, state: ValidationState) -> None:
    parsed = markdown_headings(text)
    positions_by_heading: dict[str, list[MarkdownHeading]] = defaultdict(list)
    for parsed_heading in parsed:
        positions_by_heading[parsed_heading.text].append(parsed_heading)

    last_pos = -1
    for heading in headings:
        matches = positions_by_heading.get(heading, [])
        if not matches:
            state.error(f"missing_heading={state.rel(path)}::{heading}")
            continue
        if len(matches) > 1:
            state.error(f"duplicate_heading={state.rel(path)}::{heading}::{len(matches)}")
        pos = matches[0].start
        if pos < last_pos:
            state.error(f"heading_out_of_order={state.rel(path)}::{heading}")
        last_pos = pos


def markdown_section(text: str, heading: str) -> str:
    parsed = markdown_headings(text)
    current_index = next((index for index, item in enumerate(parsed) if item.text == heading), None)
    if current_index is None:
        return ""
    current = parsed[current_index]
    body_start = text.find("\n", current.end)
    body_start = len(text) if body_start == -1 else body_start + 1
    next_heading = next((item for item in parsed[current_index + 1 :] if item.level <= current.level), None)
    body_end = next_heading.start if next_heading else len(text)
    return text[body_start:body_end].strip()


def markdown_tables(section: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    tables: list[tuple[list[str], list[dict[str, str]]]] = []
    lines = section.splitlines()
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith("|"):
            index += 1
            continue
        block: list[str] = []
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            block.append(lines[index].strip())
            index += 1
        if len(block) < 2:
            continue
        headers = [cell.strip() for cell in block[0].strip("|").split("|")]
        separator = [cell.strip() for cell in block[1].strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
            continue
        rows: list[dict[str, str]] = []
        for line in block[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) < len(headers):
                cells.extend([""] * (len(headers) - len(cells)))
            rows.append(dict(zip(headers, cells)))
        tables.append((headers, rows))
    return tables


def canonical_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.strip().lower())


def headers_match(headers: list[str], required: list[str]) -> bool:
    return [canonical_header(item) for item in headers[: len(required)]] == [
        canonical_header(item) for item in required
    ]


def row_value(row: dict[str, str], *names: str) -> str:
    canonical = {canonical_header(key): value for key, value in row.items()}
    for name in names:
        value = canonical.get(canonical_header(name))
        if value is not None:
            return value.strip()
    return ""


def split_cell_values(value: str | None) -> list[str]:
    if value is None:
        return []
    items = re.split(r"[,;/]+|\band\b", value, flags=re.IGNORECASE)
    return [item.strip().lower() for item in items if item.strip()]


def normalized_cell(value: str | None) -> str:
    return (value or "").strip().strip("`").lower()


def cell_has_evidence(value: str | None) -> bool:
    return normalized_cell(value) not in UNKNOWN_CELL_VALUES


def markdown_link_target(value: str) -> str:
    match = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", value.strip())
    return match.group(1).strip() if match else value.strip()


def resolve_within_root(root: Path, rel_path: str) -> Path | None:
    target_text = markdown_link_target(rel_path)
    target = Path(target_text)
    if target.is_absolute() or ".." in target.parts:
        return None
    candidate = (root / target).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def safe_subplan_path(state: ValidationState, value: str) -> tuple[Path | None, str | None]:
    target_text = markdown_link_target(value)
    target = Path(target_text)
    if target.is_absolute() or ".." in target.parts:
        return None, "unsafe"
    if len(target.parts) != 3 or target.parts[0] != "Planner-docs":
        return None, "unsafe"
    if not FOLDER_RE.match(target.parts[1]) or not SUBPLAN_RE.match(target.name):
        return None, "unsafe"
    resolved = resolve_within_root(state.root, target_text)
    if resolved is None:
        return None, "unsafe"
    if not resolved.exists():
        return resolved, "missing"
    return resolved, None


def section_has_table(section: str) -> bool:
    return any(rows for _, rows in markdown_tables(section))


def marker_reason(value: str, prefix: str) -> str | None:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return None


def valid_marker_reason(value: str, prefix: str) -> bool:
    reason = marker_reason(value, prefix)
    return reason is not None and cell_has_evidence(reason) and len(reason) >= 8


def unknown_marker_has_next_probe(value: str) -> bool:
    reason = marker_reason(value, UNKNOWN_PREFIX)
    if reason is None or not cell_has_evidence(reason):
        return False
    return "next probe" in reason.lower() and len(reason) >= 12


def evidence_is_direct_for_claim(claim_type: str, evidence_type: str, evidence_source: str) -> bool:
    if not cell_has_evidence(evidence_source):
        return False
    if claim_type == "structural":
        return evidence_type == "source"
    if claim_type == "configuration":
        return evidence_type == "configuration"
    return False


def has_independent_evidence(evidence_type: str, evidence_source: str) -> bool:
    evidence_types = {item for item in split_cell_values(evidence_type) if item in ALLOWED_EVIDENCE_TYPES}
    locators = {item for item in split_cell_values(evidence_source) if cell_has_evidence(item)}
    return len(evidence_types) >= 2 and len(locators) >= 2


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


def validate_ontology_competency_questions(text: str, path: Path, state: ValidationState) -> None:
    question_section = markdown_section(text, "## 8. Open Ontology Questions")
    if "Competency Questions" not in question_section:
        return
    for _, rows in markdown_tables(question_section):
        for row in rows:
            status = normalized_cell(row.get("Status"))
            question_id = row.get("Question ID") or row.get("ID") or row.get("Question") or "unknown"
            if status and status not in ALLOWED_ONTOLOGY_QUESTION_STATUSES:
                state.warning(f"invalid_ontology_question_status={state.rel(path)}::{status}")
            if status in {"answered", "partially_answered"} and not cell_has_evidence(row.get("Evidence")):
                state.warning(f"ontology_question_missing_evidence={state.rel(path)}::{question_id}")


def validate_optional_comprehension_doc(state: ValidationState) -> None:
    path = state.planner_docs / "Project-Comprehension.md"
    state.metrics["comprehension_exists"] = "true" if path.exists() else "false"
    if not path.exists():
        return

    text = read_text(path, state)
    if text is None:
        return

    validate_heading_order(text, COMPREHENSION_HEADINGS, path, state)

    question_section = markdown_section(text, "## 1. Understanding Goals and Competency Questions")
    if "CQ-" not in question_section and "question id" not in question_section.lower():
        state.warning(f"comprehension_missing_question={state.rel(path)}")

    evidence_section = markdown_section(text, "## 2. Evidence Register and Confidence")
    evidence_rows: list[dict[str, str]] = []
    for _, rows in markdown_tables(evidence_section):
        evidence_rows.extend(rows)
        for row in rows:
            evidence_id = row.get("Evidence ID") or row.get("ID") or "unknown"
            evidence_type = normalized_cell(row_value(row, "Evidence type", "Evidence Type"))
            evidence_source = row_value(row, "Evidence source", "Evidence Source")
            confidence = normalized_cell(row.get("Confidence"))
            claim_type = normalized_cell(row_value(row, "Claim Type", "Type")) or "structural"
            if claim_type not in ALLOWED_CLAIM_TYPES:
                state.warning(f"invalid_claim_type={state.rel(path)}::{claim_type}")
            if evidence_type and evidence_type not in ALLOWED_EVIDENCE_TYPES:
                state.warning(f"invalid_evidence_type={state.rel(path)}::{evidence_type}")
            if confidence and confidence not in ALLOWED_CONFIDENCE_VALUES:
                state.warning(f"invalid_confidence={state.rel(path)}::{confidence}")
            if confidence == "confirmed" and not cell_has_evidence(evidence_source):
                state.warning(f"high_confidence_without_evidence={state.rel(path)}::{evidence_id}")
            if confidence == "confirmed" and cell_has_evidence(evidence_source):
                if claim_type == "behavioral" and evidence_type not in {"test", "runtime"}:
                    if not has_independent_evidence(evidence_type, evidence_source):
                        state.warning(
                            f"confirmed_behavioral_claim_needs_test_or_runtime={state.rel(path)}::{evidence_id}"
                        )
                elif claim_type == "historical" and evidence_type != "history":
                    state.warning(f"historical_claim_requires_history_evidence={state.rel(path)}::{evidence_id}")
                elif claim_type == "user_intent" and evidence_type != "user-confirmed":
                    state.warning(f"user_intent_claim_requires_user_confirmed_evidence={state.rel(path)}::{evidence_id}")
                elif claim_type == "architectural":
                    if evidence_type not in {"source", "configuration"} and not has_independent_evidence(
                        evidence_type, evidence_source
                    ):
                        state.warning(f"architectural_claim_needs_relation_evidence={state.rel(path)}::{evidence_id}")
                elif claim_type in {"structural", "configuration"}:
                    if not evidence_is_direct_for_claim(claim_type, evidence_type, evidence_source):
                        if not has_independent_evidence(evidence_type, evidence_source):
                            state.warning(f"confirmed_{claim_type}_claim_needs_direct_evidence={state.rel(path)}::{evidence_id}")
    if not evidence_rows:
        state.warning(f"comprehension_missing_evidence_row={state.rel(path)}")

    trace_section = markdown_section(text, "## 3. Domain-to-Code Trace Map")
    trace_has_rows = False
    if marker_reason(trace_section, NOT_APPLICABLE_PREFIX) is not None and not valid_marker_reason(
        trace_section, NOT_APPLICABLE_PREFIX
    ):
        state.warning(f"invalid_not_applicable_marker={state.rel(path)}::## 3. Domain-to-Code Trace Map")
    if marker_reason(trace_section, UNKNOWN_PREFIX) is not None and not unknown_marker_has_next_probe(trace_section):
        state.warning(f"unknown_marker_missing_next_probe={state.rel(path)}::## 3. Domain-to-Code Trace Map")
    for _, rows in markdown_tables(trace_section):
        trace_has_rows = trace_has_rows or bool(rows)
        for row in rows:
            trace_id = row.get("Trace ID") or row.get("ID") or "unknown"
            confidence = normalized_cell(row.get("Confidence"))
            if confidence and confidence not in ALLOWED_CONFIDENCE_VALUES:
                state.warning(f"invalid_confidence={state.rel(path)}::{confidence}")
            has_code_anchor = cell_has_evidence(row.get("Entry points")) or cell_has_evidence(row.get("Core implementation"))
            has_test_anchor = cell_has_evidence(row.get("Tests"))
            if not has_code_anchor and not has_test_anchor:
                state.warning(f"trace_missing_code_or_test_anchor={state.rel(path)}::{trace_id}")
    if not trace_has_rows and not valid_marker_reason(trace_section, NOT_APPLICABLE_PREFIX):
        state.warning(f"comprehension_missing_trace={state.rel(path)}")

    architecture_section = markdown_section(text, "## 5. Intended vs Implemented Architecture")
    architecture_has_rows = False
    if marker_reason(architecture_section, NOT_APPLICABLE_PREFIX) is not None and not valid_marker_reason(
        architecture_section, NOT_APPLICABLE_PREFIX
    ):
        state.warning(f"invalid_not_applicable_marker={state.rel(path)}::## 5. Intended vs Implemented Architecture")
    if marker_reason(architecture_section, UNKNOWN_PREFIX) is not None and not unknown_marker_has_next_probe(
        architecture_section
    ):
        state.warning(
            f"unknown_marker_missing_next_probe={state.rel(path)}::## 5. Intended vs Implemented Architecture"
        )
    for _, rows in markdown_tables(architecture_section):
        architecture_has_rows = architecture_has_rows or bool(rows)
        for row in rows:
            status = normalized_cell(row.get("Status"))
            if status and status not in ALLOWED_ARCHITECTURE_STATUSES:
                state.warning(f"invalid_architecture_status={state.rel(path)}::{status}")
    if not architecture_has_rows and not valid_marker_reason(architecture_section, NOT_APPLICABLE_PREFIX):
        state.warning(f"comprehension_missing_architecture={state.rel(path)}")

    hypothesis_section = markdown_section(text, "## 8. Open Hypotheses and Validation Probes")
    hypothesis_has_rows = False
    if marker_reason(hypothesis_section, NO_UNRESOLVED_HYPOTHESES_PREFIX) is not None and not valid_marker_reason(
        hypothesis_section, NO_UNRESOLVED_HYPOTHESES_PREFIX
    ):
        state.warning(f"invalid_no_unresolved_hypotheses_marker={state.rel(path)}")
    if marker_reason(hypothesis_section, UNKNOWN_PREFIX) is not None and not unknown_marker_has_next_probe(
        hypothesis_section
    ):
        state.warning(
            f"unknown_marker_missing_next_probe={state.rel(path)}::## 8. Open Hypotheses and Validation Probes"
        )
    for _, rows in markdown_tables(hypothesis_section):
        hypothesis_has_rows = hypothesis_has_rows or bool(rows)
        for row in rows:
            hypothesis_id = row.get("Hypothesis ID") or row.get("ID") or "unknown"
            confidence = normalized_cell(row.get("Confidence"))
            if confidence and confidence not in ALLOWED_CONFIDENCE_VALUES:
                state.warning(f"invalid_confidence={state.rel(path)}::{confidence}")
            if not cell_has_evidence(row.get("Next probe")):
                state.warning(f"open_hypothesis_missing_next_probe={state.rel(path)}::{hypothesis_id}")
    if not hypothesis_has_rows and not valid_marker_reason(hypothesis_section, NO_UNRESOLVED_HYPOTHESES_PREFIX):
        state.warning(f"comprehension_missing_hypothesis_or_marker={state.rel(path)}")


def validate_ledger_v2_rows(text: str, path: Path, state: ValidationState) -> None:
    section = markdown_section(text, "## 4. Sub-Plan Status Matrix")
    found_table = False
    active_rows: dict[str, str] = {}
    for headers, rows in markdown_tables(section):
        if not headers_match(headers, LEDGER_V2_STATUS_HEADERS):
            continue
        found_table = True
        for row in rows:
            subplan = row_value(row, "Sub-plan Path", "Sub-plan", "Sub-Plan Path")
            status = normalized_cell(row_value(row, "Status"))
            run_id = row_value(row, "Run ID")
            validation = row_value(row, "Validation Evidence", "Validation evidence")
            blocker = row_value(row, "Blocker")
            next_action = row_value(row, "Next Action")
            superseded_by = row_value(row, "Superseded By")

            if status not in ALLOWED_LEDGER_STATUSES:
                state.warning(f"invalid_ledger_status={state.rel(path)}::{status or 'missing'}")
                continue
            if subplan:
                resolved, reason = safe_subplan_path(state, subplan)
                if reason == "unsafe":
                    state.warning(f"unsafe_ledger_subplan_path={state.rel(path)}::{subplan}")
                elif reason == "missing":
                    state.warning(f"missing_ledger_subplan={state.rel(path)}::{subplan}")
                key = state.rel(resolved) if resolved is not None else subplan
                previous = active_rows.get(key)
                if previous and previous != status and status not in {"superseded"} and previous not in {"superseded"}:
                    state.warning(f"conflicting_ledger_status={state.rel(path)}::{key}::{previous},{status}")
                active_rows[key] = status

            if status == "in_progress" and not cell_has_evidence(run_id):
                state.warning(f"ledger_in_progress_missing_run_id={state.rel(path)}::{subplan or 'unknown'}")
            if status == "implemented" and not cell_has_evidence(validation):
                state.warning(f"ledger_implemented_missing_validation={state.rel(path)}::{subplan or 'unknown'}")
            if status == "verified" and not cell_has_evidence(validation):
                state.warning(f"ledger_verified_missing_validation={state.rel(path)}::{subplan or 'unknown'}")
            if status == "blocked":
                if not cell_has_evidence(blocker):
                    state.warning(f"ledger_blocked_missing_blocker={state.rel(path)}::{subplan or 'unknown'}")
                if not cell_has_evidence(next_action):
                    state.warning(f"ledger_blocked_missing_next_action={state.rel(path)}::{subplan or 'unknown'}")
            if status == "superseded" and not cell_has_evidence(superseded_by):
                state.warning(f"ledger_superseded_missing_target={state.rel(path)}::{subplan or 'unknown'}")
    if not found_table:
        state.warning(f"ledger_v2_status_matrix_missing_table={state.rel(path)}")


def validate_optional_continuity_docs(state: ValidationState) -> None:
    ontology_path = state.planner_docs / "Project-Ontology.md"
    ledger_path = state.planner_docs / "Planing-Ledger.md"

    state.metrics["ontology_exists"] = "true" if ontology_path.exists() else "false"
    state.metrics["ledger_exists"] = "true" if ledger_path.exists() else "false"
    state.metrics["comprehension_exists"] = "true" if (state.planner_docs / "Project-Comprehension.md").exists() else "false"

    if ontology_path.exists():
        text = read_text(ontology_path, state)
        if text is not None:
            validate_heading_order(text, ONTOLOGY_HEADINGS, ontology_path, state)
            validate_ontology_competency_questions(text, ontology_path, state)

    if ledger_path.exists():
        text = read_text(ledger_path, state)
        if text is not None:
            headings = {item.text for item in markdown_headings(text)}
            has_v2 = all(heading in headings for heading in LEDGER_V2_HEADINGS)
            has_legacy = all(heading in headings for heading in LEDGER_LEGACY_HEADINGS)
            if has_v2:
                state.metrics["ledger_schema"] = "v2"
                validate_heading_order(text, LEDGER_V2_HEADINGS, ledger_path, state)
                validate_ledger_v2_rows(text, ledger_path, state)
            elif has_legacy:
                state.metrics["ledger_schema"] = "legacy_v1"
                validate_heading_order(text, LEDGER_LEGACY_HEADINGS, ledger_path, state)
                if state.mode == "step4" and state.strict:
                    state.error("legacy_ledger_requires_v2_for_step4=Planner-docs/Planing-Ledger.md")
                else:
                    state.warning("legacy_ledger_schema=Planner-docs/Planing-Ledger.md")
            else:
                state.metrics["ledger_schema"] = "unknown"
                validate_heading_order(text, LEDGER_V2_HEADINGS, ledger_path, state)

    validate_optional_comprehension_doc(state)


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


def parse_audit_findings(text: str, path: Path, state: ValidationState) -> list[dict[str, str]]:
    fix_section = markdown_section(text, "## 13. Priority Fix List")
    findings: list[dict[str, str]] = []
    for headers, rows in markdown_tables(fix_section):
        if not headers_match(headers, FINDING_HEADERS):
            continue
        for row in rows:
            finding_id = row_value(row, "Finding ID")
            severity = row_value(row, "Severity").upper()
            status = normalized_cell(row_value(row, "Status")) or "open"
            if not finding_id.startswith("AUDIT-FIX-"):
                continue
            if severity not in {"P0", "P1", "P2", "P3"}:
                state.error(f"invalid_finding_severity={state.rel(path)}::{finding_id}::{severity or 'missing'}")
            if status not in ALLOWED_FINDING_STATUSES:
                state.error(f"invalid_finding_status={state.rel(path)}::{finding_id}::{status or 'missing'}")
            findings.append(
                {
                    "id": finding_id,
                    "severity": severity,
                    "status": status,
                    "affected_files": row_value(row, "Affected Files"),
                }
            )
    if findings:
        return findings

    for finding_id, severity in AUDIT_FIX_RE.findall(fix_section):
        findings.append({"id": finding_id, "severity": severity, "status": "open", "affected_files": ""})
    return findings


def active_severity_counts(findings: list[dict[str, str]]) -> dict[str, int]:
    counts = {severity: 0 for severity in ("P0", "P1", "P2", "P3")}
    for finding in findings:
        severity = finding.get("severity", "")
        status = finding.get("status", "")
        if severity in counts and status in OPEN_FINDING_STATUSES:
            counts[severity] += 1
    return counts


def parse_readiness_rows(text: str, path: Path, state: ValidationState) -> list[dict[str, str]]:
    section = markdown_section(text, "## 12. Step 4 Readiness Assessment")
    for headers, rows in markdown_tables(section):
        if headers_match(headers, READINESS_HEADERS):
            return rows
    state.error(f"audit_readiness_table_missing={state.rel(path)}")
    return []


def validate_audit_section_depth(text: str, path: Path, state: ValidationState) -> None:
    for heading in AUDIT_HEADINGS:
        if heading == "# Sub-Planing Audit":
            continue
        body = markdown_section(text, heading)
        if len(body) < 20:
            state.error(f"empty_or_too_short_audit_section={state.rel(path)}::{heading}")


def validate_readiness_rows(
    rows: list[dict[str, str]],
    path: Path,
    state: ValidationState,
    findings: list[dict[str, str]],
) -> None:
    by_id = {finding.get("id", ""): finding for finding in findings}
    seen: dict[str, str] = {}
    ready_count = 0
    terminal_count = 0

    if not rows:
        state.metrics["execution_queue_state"] = "BLOCKED"
        return

    for row in rows:
        subplan = row_value(row, "Sub-Plan Path", "Sub-plan Path", "Subplan Path")
        status = row_value(row, "Status").upper()
        finding_ids = row_value(row, "Finding IDs", "Finding ID")
        dependency = normalized_cell(row_value(row, "Dependency State"))

        if status not in ALLOWED_READINESS_STATUSES:
            state.error(f"invalid_readiness_status={state.rel(path)}::{status or 'missing'}")
        if dependency not in ALLOWED_DEPENDENCY_STATES:
            state.error(f"invalid_dependency_state={state.rel(path)}::{dependency or 'missing'}")

        resolved, reason = safe_subplan_path(state, subplan)
        if reason == "unsafe":
            state.error(f"unsafe_subplan_path={state.rel(path)}::{subplan}")
            key = subplan
        elif reason == "missing":
            state.error(f"missing_readiness_subplan={subplan}")
            key = subplan
        else:
            key = state.rel(resolved) if resolved is not None else subplan

        previous = seen.get(key)
        if previous and previous != status:
            state.error(f"conflicting_readiness_status={key}::{previous},{status}")
        seen[key] = status

        if status in READY_READINESS_STATUSES:
            ready_count += 1
            if dependency not in {"satisfied", "independent"}:
                state.error(f"ready_row_has_blocked_dependency={key}::{dependency}")
        elif status in COMPLETED_READINESS_STATUSES:
            terminal_count += 1

        ids = [item.strip() for item in re.split(r"[,; ]+", finding_ids) if item.strip() and item.strip().lower() != "none"]
        if status == "READY_WITH_WARNINGS":
            for finding_id in ids:
                finding = by_id.get(finding_id)
                if finding and finding.get("status") in OPEN_FINDING_STATUSES and finding.get("severity") in {"P0", "P1"}:
                    state.error(f"ready_with_warnings_references_blocking_finding={key}::{finding_id}")

    if ready_count:
        state.metrics["execution_queue_state"] = "READY"
    elif terminal_count == len(rows):
        state.metrics["execution_queue_state"] = "NO_ACTION_REQUIRED"
    else:
        state.metrics["execution_queue_state"] = "BLOCKED"


def validate_audit_required(state: ValidationState, require_readiness: bool) -> None:
    audit_path = state.planner_docs / "Sub-Planing-Audit.md"
    text = read_text(audit_path, state)
    if text is None:
        state.metrics["audit_status"] = "missing"
        return

    validate_heading_order(text, AUDIT_HEADINGS, audit_path, state)
    validate_audit_section_depth(text, audit_path, state)

    status = extract_audit_status(text)
    state.metrics["audit_status"] = status or "unknown"
    if status is None:
        state.error("audit_status_missing=Planner-docs/Sub-Planing-Audit.md")
    elif status == "BLOCKED":
        state.error("step4_blocked_by_audit_status=BLOCKED")

    findings = parse_audit_findings(text, audit_path, state)
    severity_counts = active_severity_counts(findings)
    for severity, count in severity_counts.items():
        state.metrics[f"{severity.lower()}_findings"] = count
    if severity_counts["P0"] or severity_counts["P1"]:
        state.error(
            f"step4_blocked_by_high_severity_findings=P0:{severity_counts['P0']},P1:{severity_counts['P1']}"
        )
    if status == "PASS" and (severity_counts["P2"] or severity_counts["P3"]):
        state.error(f"audit_status_inconsistent_with_open_warnings=PASS::P2:{severity_counts['P2']},P3:{severity_counts['P3']}")
    if status == "PASS_WITH_WARNINGS" and (severity_counts["P2"] or severity_counts["P3"]):
        state.warning(
            f"step4_has_nonblocking_warnings=P2:{severity_counts['P2']},P3:{severity_counts['P3']}"
        )
    elif status == "PASS_WITH_WARNINGS" and not (severity_counts["P0"] or severity_counts["P1"]):
        state.warning("audit_status_has_no_open_warnings=PASS_WITH_WARNINGS")

    if require_readiness:
        rows = parse_readiness_rows(text, audit_path, state)
        validate_readiness_rows(rows, audit_path, state, findings)


def validate_step3_post_audit(state: ValidationState) -> None:
    validate_step3_preflight(state)
    validate_audit_required(state, require_readiness=False)


def validate_step4_readiness(state: ValidationState) -> None:
    validate_step3_preflight(state)
    validate_audit_required(state, require_readiness=True)


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
            if warning.startswith("legacy_ledger_schema=") and state.mode != "step4":
                continue
            state.errors.append(f"strict_warning={warning}")

    state.metrics["warning_count"] = len(state.warnings)
    state.metrics["error_count"] = len(state.errors)

    status = "failed" if state.errors else "passed"
    print(f"planner_docs_validation={status}")
    print(f"validation_status={status}")
    print(f"mode={state.mode}")
    print(f"validation_mode={state.mode}")
    print(f"root={state.root}")
    for key in sorted(state.metrics):
        print(f"{key}={state.metrics[key]}")
    for warning in sorted(state.warnings):
        print(f"warning={warning}")
    for error in sorted(state.errors):
        print(f"error={error}")
    if any(error.startswith(("unknown_mode=", "read_error=", "non_utf8_file=")) for error in state.errors):
        return 2
    return 1 if state.errors else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate AntigravityQB Planner-docs outputs.")
    parser.add_argument("--root", default=".", help="Project root containing Planner-docs/; default: current directory.")
    parser.add_argument(
        "--mode",
        choices=("step1", "autopsy", "step2", "step3-preflight", "step3", "step4", "all"),
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
    elif mode == "step3-preflight":
        validate_step3_preflight(state)
    elif mode == "step3":
        validate_step3_post_audit(state)
    elif mode == "all":
        validate_step3_post_audit(state)
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
