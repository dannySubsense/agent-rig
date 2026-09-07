"""Signpost/Pillar checklist probe — new probe core for the signpost-checklist-redesign sprint.

Replaces `first_turn_contract_probe.py`'s C1/C2/C3 body. See
`docs/specs/signpost-checklist-redesign/02-ARCHITECTURE.md` for the governing design.

This slice (Slice 1) adds only the data schemas (§3) and the three new verbatim parsers
(§4, §5.3): `extract_signpost_lines`, `extract_pillar_rows`, `parse_checklist_row_line`.
Trigger-surface/tool-call-collection functions (§5.1) and `evaluate_checklist`/`build_reason`/
`run` (§5.4) are added in later slices.
"""

import re
from dataclasses import dataclass
from typing import Optional

# --- §3 Data Schemas -------------------------------------------------------


@dataclass(frozen=True)
class SignpostLine:
    """One verbatim claim line extracted from the Signpost section, in source order."""

    text: str  # content after list-marker stripping, byte-identical to source
    raw_line: str  # full original line (for quoting in FAIL reasons)


@dataclass(frozen=True)
class PillarRow:
    """One checklist row parsed from the Pillar section, in source order.
    Authored entirely by the agent (§1a) — this dataclass is the hook's parsed *read* of that
    text, never something the hook writes."""

    label: str  # content between the checkbox and the forced status suffix
    status: str  # forced literal: "verified" or "unverified" — see §5.3
    tool_use_id: Optional[str]  # set only when status == "verified"; always None otherwise
    raw_line: str


@dataclass(frozen=True)
class QualifyingToolCall:
    """A completed (tool_use + matching tool_result present), non-excluded tool call
    preceding the current turn."""

    tool_use_id: str
    name: str
    tool_input: dict


@dataclass(frozen=True)
class RowViolation:
    kind: str  # one of: "missing", "duplicate_label", "stray_prose", "false_claim",
    # "duplicate_id", "malformed_signpost" (§5.4 rule 0a), "unmatched_row" (§5.4 rule 7)
    signpost_text: Optional[str]  # set for "missing"
    row: Optional[PillarRow]  # set for "false_claim" / "duplicate_id" / "unmatched_row" /
    # "duplicate_label"
    line_text: Optional[str]  # set for "stray_prose" — the raw offending line, so
    # build_reason() can quote it per §4's contract


@dataclass(frozen=True)
class EvaluationResult:
    decision: str  # "block" | "allow"
    violations: list  # list[RowViolation], empty on allow
    signpost_heading_absent: bool  # True only for the §5.4 rule-0 fail-closed case (§6 edge case)
    reason: Optional[str]  # human-readable, built from violations; None on allow


# --- §5.3 New: forced checklist-row syntax ---------------------------------

_PILLAR_ROW_RE = re.compile(
    r"^\s*[-*+]\s*\[( |x|X)\]\s*(.*?)\s*"
    r"(?:\(verified:\s*tool_use_id=([A-Za-z0-9_\-]+)\)|\((unverified)\))\s*$"
)

# §4 — markdown list-item marker shape for Signpost claim lines: `-`, `*`, `+`, or `N.`.
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$")

# §4 — Signpost/Pillar heading label, case-insensitive, up to and including the first colon.
# Matches the same heading forms `_SIGNPOST_PILLAR_HEADING_RE` (archive probe, §5.2) accepts:
# leading markdown markup stripped, and arbitrary pre-colon qualifier text tolerated
# (e.g. "## Signpost: ...", "Signpost (this turn): ...") so a valid heading's trailing
# content is never silently dropped by a narrower label-strip here.
_SIGNPOST_LABEL_RE = re.compile(r"^signpost\b[^:\n]*:\s*\**\s*(.*)$", re.IGNORECASE)
_PILLAR_LABEL_RE = re.compile(r"^pillar\b[^:\n]*:\s*\**\s*(.*)$", re.IGNORECASE)


def _strip_leading_markup(line: str) -> str:
    """Strip leading whitespace and markdown emphasis markers (#, *) — matches
    `strip_leading_markup()` in the archived first_turn_contract_probe.py (§5.2), which
    Slice 2 will import unchanged. Duplicated narrowly here so Slice 1's label-stripping
    isn't narrower than the heading detector it must interoperate with."""
    s = line
    while s and s[0] in " \t#*":
        s = s[1:]
    return s


# --- §4 API Contracts -------------------------------------------------------


def extract_signpost_lines(
    text: str, signpost_idx: Optional[int], pillar_idx: Optional[int]
) -> list:
    """Lines in the Signpost section (between signpost_idx and pillar_idx, or end-of-text if
    pillar_idx is None) that match the markdown list-item shape (`-`, `*`, `+`, or `N.` marker).
    Non-list-item lines inside the section (blank lines, prose continuation) are not claim
    lines and are skipped.

    Returns [] if signpost_idx is None (no Signpost heading). Also returns [] when the heading
    IS present but the section (including trailing content on the heading line itself, after
    the `Signpost:` label is stripped) contains any non-blank text with zero matching list-item
    lines. Callers must use a separately-computed `signpost_section_has_content` flag (not
    produced by this function) to distinguish those two cases — see architecture §4.
    """
    if signpost_idx is None:
        return []

    lines = text.split("\n")
    section_end = pillar_idx if pillar_idx is not None else len(lines)

    candidate_lines = []

    # Heading line itself: label stripped, trailing content (if any) is a candidate line.
    heading_raw = lines[signpost_idx] if 0 <= signpost_idx < len(lines) else ""
    label_match = _SIGNPOST_LABEL_RE.match(_strip_leading_markup(heading_raw))
    if label_match:
        trailing = label_match.group(1)
        if trailing:
            candidate_lines.append(trailing)

    # Lines strictly between the heading and the next heading (or end of text).
    for idx in range(signpost_idx + 1, section_end):
        if 0 <= idx < len(lines):
            candidate_lines.append(lines[idx])

    signpost_lines = []
    for raw_line in candidate_lines:
        m = _LIST_ITEM_RE.match(raw_line)
        if not m:
            continue
        signpost_lines.append(SignpostLine(text=m.group(1).strip(), raw_line=raw_line))

    return signpost_lines


def extract_pillar_rows(text: str, pillar_idx: Optional[int], section_end_idx: int):
    """Lines in the Pillar section matching the forced checklist-row syntax (§5.2, §5.3), each
    parsed by `parse_checklist_row_line`. Lines that do NOT match the syntax produce no
    `PillarRow` and are instead collected into `unparsed_lines`.

    The Pillar heading line itself is included in the section span: its own label (`Pillar:`,
    case-insensitive, up to and including the first colon) is stripped and never itself treated
    as a row or as stray prose, but any trailing content after the label on that same heading
    line IS evaluated exactly like a normal line (row-parsed or classified as stray prose).

    Returns a tuple: (list[PillarRow], unparsed_lines: list[str]).
    """
    if pillar_idx is None:
        return [], []

    lines = text.split("\n")

    candidate_lines = []

    heading_raw = lines[pillar_idx] if 0 <= pillar_idx < len(lines) else ""
    label_match = _PILLAR_LABEL_RE.match(_strip_leading_markup(heading_raw))
    if label_match:
        trailing = label_match.group(1)
        if trailing:
            candidate_lines.append(trailing)

    for idx in range(pillar_idx + 1, section_end_idx):
        if 0 <= idx < len(lines):
            candidate_lines.append(lines[idx])

    pillar_rows = []
    unparsed_lines = []
    for raw_line in candidate_lines:
        if not raw_line.strip():
            continue
        row = parse_checklist_row_line(raw_line)
        if row is not None:
            pillar_rows.append(row)
        else:
            unparsed_lines.append(raw_line)

    return pillar_rows, unparsed_lines


def parse_checklist_row_line(raw_line: str) -> Optional[PillarRow]:
    """Regex match against the forced row syntax (§5.3). None if the line doesn't match the full
    shape, including the required, forced status suffix — `(verified: tool_use_id=<id>)` or the
    exact literal `(unverified)`. A line with neither suffix is not a row at all.
    """
    m = _PILLAR_ROW_RE.match(raw_line)
    if not m:
        return None

    label = m.group(2).strip()
    verified_tool_id = m.group(3)
    unverified_literal = m.group(4)

    if verified_tool_id is not None:
        return PillarRow(
            label=label,
            status="verified",
            tool_use_id=verified_tool_id,
            raw_line=raw_line,
        )
    if unverified_literal is not None:
        return PillarRow(
            label=label,
            status="unverified",
            tool_use_id=None,
            raw_line=raw_line,
        )
    return None
