"""Signpost/Pillar checklist probe — new probe core for the signpost-checklist-redesign sprint.

Replaces `first_turn_contract_probe.py`'s C1/C2/C3 body. See
`docs/specs/signpost-checklist-redesign/02-ARCHITECTURE.md` for the governing design.

Slice 1 added the data schemas (§3) and the three new verbatim parsers (§4, §5.3):
`extract_signpost_lines`, `extract_pillar_rows`, `parse_checklist_row_line`.

Slice 2 copied the architecture-designated §5.1 trigger-surface/tool-call-collection functions
from the archived probe (archive/first-turn-contract-enforcement/scripts/
first_turn_contract_probe.py), unmodified in behavior, plus one additive change per §5.1a
(`collect_qualifying_tool_calls()`). Slice 3 added `evaluate_checklist`/`build_reason` (§5.4).
Slice 4 (this addition) wires `run()`/`main()` (§4, §5.1's gating order) and the row-level
`write_track_record()` schema.
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK_RECORD_PATH = os.path.join(
    REPO_ROOT, "docs", "tooling", "signpost-checklist-track-record.jsonl"
)

# The first line of session_queue_probe.py's HEADER (§5.1) — emitted only on the success
# path (a tagged queue row was found and injected). Copied unchanged from the archived probe
# per §5.1.
QUEUE_MARKER = "SESSION QUEUE — SIGNPOST, NOT PILLAR."

# Tools excluded from the qualifying-tool-call set (§5.1a) — bookkeeping, not verification.
# Renamed from the archived probe's `C3_EXCLUDED_TOOLS`; same value.
EXCLUDED_TOOLS = {"TodoWrite"}

# §5.2/§5.3 (archived probe) — heading-line predicate: after leading whitespace/#/* markup is
# stripped, a line starting with Signpost or Pillar, followed (before end of line) by a colon
# that closes the heading label. Trailing prose on the same line is permitted. Copied
# unchanged from the archived probe per §5.1 — heading detection itself is unchanged by this
# redesign.
_SIGNPOST_PILLAR_HEADING_RE = re.compile(
    r"^(Signpost|Pillar)\b[^:\n]*:\s*\**\s*$|^(Signpost|Pillar)\b[^:\n]*:\s*\**\s*\S",
    re.IGNORECASE,
)

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
    label_match = _SIGNPOST_LABEL_RE.match(strip_leading_markup(heading_raw))
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
    label_match = _PILLAR_LABEL_RE.match(strip_leading_markup(heading_raw))
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


# --- §5.1 Reused trigger-surface / stdin contract (copied unchanged from the archived probe:
# archive/first-turn-contract-enforcement/scripts/first_turn_contract_probe.py) -------------


def read_stdin():
    """Best-effort stdin JSON parse. Absence or malformed stdin must not crash the probe;
    the caller treats a resulting empty dict as "nothing to check", which allows."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def strip_leading_markup(line):
    """Strip leading whitespace and markdown emphasis markers (#, *), per §5.2 (archived
    probe)."""
    s = line
    while s and s[0] in " \t#*":
        s = s[1:]
    return s


def find_signpost_pillar_positions(text):
    """§5.2 (archived probe) — first Signpost heading line index and first Pillar heading
    line index (by line number in `text`), or None for either not found."""
    signpost_idx = None
    pillar_idx = None
    for idx, raw_line in enumerate(text.split("\n")):
        stripped = strip_leading_markup(raw_line)
        m = _SIGNPOST_PILLAR_HEADING_RE.match(stripped)
        if not m:
            continue
        label = (m.group(1) or m.group(2)).lower()
        if label == "signpost" and signpost_idx is None:
            signpost_idx = idx
        elif label == "pillar" and pillar_idx is None:
            pillar_idx = idx
    return signpost_idx, pillar_idx


def find_pillar_heading_line(text, pillar_idx):
    """Recover the raw heading line at `pillar_idx` for quoting in a reason string."""
    if pillar_idx is None:
        return None
    lines = text.split("\n")
    if 0 <= pillar_idx < len(lines):
        return lines[pillar_idx].strip()
    return None


def load_transcript_records(transcript_path):
    """Parse the transcript JSONL, filtered to isSidechain: false (§5.1). Malformed lines
    are skipped; a missing/unreadable file yields an empty list (fail toward "not
    queue-injected", never toward blocking)."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return []
    records = []
    try:
        with open(transcript_path, errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if not isinstance(obj, dict):
                    continue
                if obj.get("isSidechain") is not False:
                    continue
                records.append(obj)
    except Exception:
        return []
    return records


def _extract_message_texts(message):
    """Pull every text string out of a `message` dict's content, whether content is a
    bare string (user turns can be) or a list of content blocks (text blocks only —
    tool_use/tool_result/thinking blocks carry no prose to scan)."""
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str):
                    texts.append(text)
        return texts
    return []


def _extract_attachment_texts(attachment):
    """Pull text out of an `attachment` record's payload (e.g. SessionStart hook
    `additionalContext`, seen on this host as `type: "attachment"` records with no
    `message` key). `attachment.content` may be a bare string, a list of strings, or a
    list of content blocks; `attachment.stdout` (hook stdout capture) may also carry
    injected text."""
    if not isinstance(attachment, dict):
        return []
    texts = []
    for key in ("content", "stdout"):
        value = attachment.get(key)
        if isinstance(value, str):
            texts.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        texts.append(text)
    return texts


def extract_texts(record):
    """Pull every text string out of a transcript record — `message.content` (assistant
    and user turns) plus `attachment.content`/`attachment.stdout` (SessionStart queue
    injection and other hook-emitted records, which carry no `message` key on this
    host — see docs/tooling/first-turn-contract-enforcement.md §5.1)."""
    texts = _extract_message_texts(record.get("message"))
    texts.extend(_extract_attachment_texts(record.get("attachment")))
    return texts


def is_assistant_text_record(record):
    """An assistant record carrying real (non-empty, after stripping) text content —
    i.e. not a thinking-only or tool-use-only record (§5.1)."""
    if record.get("type") != "assistant":
        return False
    return any(t.strip() for t in extract_texts(record))


def analyze_queue_injection_and_first_turn(records):
    """§5.1 — (a) is the session queue-injected (HEADER marker present at or before the
    first assistant record), and (b) is the turn currently ending the *first* turn (at
    most one prior assistant-text record). Returns
    (queue_injected: bool, first_turn: bool, current_turn_index: int|None) where
    current_turn_index is the position, in `records`, of the last assistant-text record
    (the one `last_assistant_message` corresponds to), or None if no such record exists
    yet in the transcript."""
    first_assistant_idx = None
    for idx, r in enumerate(records):
        if r.get("type") == "assistant":
            first_assistant_idx = idx
            break

    queue_injected = False
    if first_assistant_idx is not None:
        scan_range = records[: first_assistant_idx + 1]
    else:
        scan_range = records
    for r in scan_range:
        for text in extract_texts(r):
            if QUEUE_MARKER in text:
                queue_injected = True
                break
        if queue_injected:
            break

    assistant_text_indices = [
        idx for idx, r in enumerate(records) if is_assistant_text_record(r)
    ]
    first_turn = len(assistant_text_indices) <= 1
    current_turn_index = assistant_text_indices[-1] if assistant_text_indices else None

    return queue_injected, first_turn, current_turn_index


# --- §5.1a Reused with one additive change (not byte-identical) ----------------------------


def collect_qualifying_tool_calls(preceding):
    """Shared collection of completed, non-excluded tool calls from `preceding` records.

    Copied from the archived probe's `_collect_qualifying_tool_calls()`
    (archive/first-turn-contract-enforcement/scripts/first_turn_contract_probe.py:474-503) —
    same tool_use/tool_result correlation logic and `EXCLUDED_TOOLS` filtering — with one
    additive change per architecture §5.1a: `tool_id` (already available as the dict key in
    the archived loop) is captured into each returned item, and results are returned as
    `QualifyingToolCall` instances rather than bare `(name, input)` tuples, so rule 4 (§5.4)
    has a real `tool_use_id` to look up a claimed ID against."""
    tool_use_info = {}
    tool_result_ids = set()
    for r in preceding:
        message = r.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_use":
                tool_id = block.get("id")
                if tool_id:
                    tool_use_info[tool_id] = (block.get("name"), block.get("input"))
            elif btype == "tool_result":
                tool_id = block.get("tool_use_id")
                if tool_id:
                    tool_result_ids.add(tool_id)

    return [
        QualifyingToolCall(tool_use_id=tool_id, name=name, tool_input=tool_input)
        for tool_id, (name, tool_input) in tool_use_info.items()
        if tool_id in tool_result_ids and name not in EXCLUDED_TOOLS
    ]


# --- §5.1 emit/track-record helpers (mechanism unchanged; schema updated per §3's
# EvaluationResult) -------------------------------------------------------------------------


def write_track_record(
    session_id, stop_hook_active, queue_injected, first_turn,
    decision, violations, reason, probe_error,
):
    """Appends one entry per invocation to the gitignored track-record log. Mechanism
    (best-effort append, never raises into the caller) unchanged from the archived probe;
    `violations` here is a list of serialized `RowViolation` (or equivalent) entries per
    §3's `EvaluationResult`, rather than the archived probe's C1/C2/C3 string labels."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "stop_hook_active": bool(stop_hook_active),
        "queue_injected": bool(queue_injected),
        "first_turn": bool(first_turn),
        "decision": decision,
        "violations": violations,
        "reason": reason,
        "probe_error": probe_error,
    }
    try:
        os.makedirs(os.path.dirname(TRACK_RECORD_PATH), exist_ok=True)
        with open(TRACK_RECORD_PATH, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        # The track record is an audit trail, not a gate — a write failure here must not
        # change or block the probe's decision to Claude Code.
        pass


# --- §5.4 Evaluation core ---------------------------------------------------


def _evaluate_verified_row(row, qualifying_calls, claimed_tool_use_ids):
    """Rules 3-5 (§5.4), shared between the per-Signpost-line matching pass and the rule-7
    residue pass. Returns a list of RowViolation (0 or 1 entries) and mutates
    `claimed_tool_use_ids` (a set) in place when a row's tool_use_id is newly claimed.
    Only called for rows with status == "verified"; "unverified" rows are never subject to
    rules 3-5 (rule 2)."""
    if row.tool_use_id is None:
        # Rule 3: defensive — should not occur given §5.3's regex.
        return [RowViolation(kind="false_claim", signpost_text=None, row=row, line_text=None)]

    if not any(call.tool_use_id == row.tool_use_id for call in qualifying_calls):
        # Rule 4: claimed tool_use_id does not exist in qualifying_calls.
        return [RowViolation(kind="false_claim", signpost_text=None, row=row, line_text=None)]

    if row.tool_use_id in claimed_tool_use_ids:
        # Rule 5: tool_use_id already claimed by an earlier-evaluated "verified" row.
        return [RowViolation(kind="duplicate_id", signpost_text=None, row=row, line_text=None)]

    claimed_tool_use_ids.add(row.tool_use_id)
    return []


def evaluate_checklist(
    signpost_lines,
    pillar_rows,
    qualifying_calls,
    signpost_heading_present,
    signpost_section_has_content,
    pillar_unparsed_lines,
):
    """Pure function, no I/O. Implements §5.4's evaluation rules 0, 0a, 1, 1a, 1b, 2-5, 6, 7.
    See architecture §5.4 for the full rule text — in particular the 2026-09-07 clarification
    that rule 5's "earlier" is resolved as evaluation order (this function's own processing
    order: the per-Signpost-line matching pass over `signpost_lines`, followed by the rule-7
    residue pass over unmatched `pillar_rows`), not the order rows appear in the agent's raw
    reply text."""
    # Rule 0: Signpost heading absent entirely — immediate fail-closed block, no per-line
    # rules evaluated.
    if not signpost_heading_present:
        result = EvaluationResult(
            decision="block", violations=[], signpost_heading_absent=True, reason=None
        )
        return EvaluationResult(
            decision=result.decision,
            violations=result.violations,
            signpost_heading_absent=result.signpost_heading_absent,
            reason=build_reason(result),
        )

    # Rule 0a: heading present, section has content, but zero claim lines parsed —
    # fail-closed block.
    if signpost_section_has_content and not signpost_lines:
        result = EvaluationResult(
            decision="block",
            violations=[
                RowViolation(
                    kind="malformed_signpost", signpost_text=None, row=None, line_text=None
                )
            ],
            signpost_heading_absent=False,
            reason=None,
        )
        return EvaluationResult(
            decision=result.decision,
            violations=result.violations,
            signpost_heading_absent=result.signpost_heading_absent,
            reason=build_reason(result),
        )

    violations = []
    claimed_tool_use_ids = set()
    matched_row_ids = set()

    # Per-Signpost-line matching pass (rules 1, 1a, 1b's counterpart, 2-5).
    for line in signpost_lines:
        matches = [row for row in pillar_rows if row.label.strip() == line.text.strip()]

        if not matches:
            # Rule 1: no matching row found.
            violations.append(
                RowViolation(
                    kind="missing", signpost_text=line.text, row=None, line_text=None
                )
            )
            continue

        if len(matches) > 1:
            # Rule 1a: more than one PillarRow matches the same SignpostLine.text — every
            # matching row is flagged; none proceed to rules 2-5.
            for row in matches:
                matched_row_ids.add(id(row))
                violations.append(
                    RowViolation(
                        kind="duplicate_label", signpost_text=None, row=row, line_text=None
                    )
                )
            continue

        row = matches[0]
        matched_row_ids.add(id(row))

        # Rule 2: "unverified" is always allowed, never a violation.
        if row.status == "unverified":
            continue

        # Rules 3-5.
        violations.extend(_evaluate_verified_row(row, qualifying_calls, claimed_tool_use_ids))

    # Rule 1b: every unparsed Pillar line is a stray-prose violation.
    for raw_line in pillar_unparsed_lines:
        violations.append(
            RowViolation(kind="stray_prose", signpost_text=None, row=None, line_text=raw_line)
        )

    # Rule 7: residue pass over PillarRows with no matching SignpostLine, run strictly after
    # the main per-line loop above. Each unmatched row is still run through rules 3-5 exactly
    # as a matched row would be, and always additionally produces an "unmatched_row" violation.
    for row in pillar_rows:
        if id(row) in matched_row_ids:
            continue
        if row.status == "verified":
            violations.extend(
                _evaluate_verified_row(row, qualifying_calls, claimed_tool_use_ids)
            )
        violations.append(
            RowViolation(kind="unmatched_row", signpost_text=None, row=row, line_text=None)
        )

    decision = "block" if violations else "allow"
    result = EvaluationResult(
        decision=decision,
        violations=violations,
        signpost_heading_absent=False,
        reason=None,
    )
    return EvaluationResult(
        decision=result.decision,
        violations=result.violations,
        signpost_heading_absent=result.signpost_heading_absent,
        reason=build_reason(result) if violations else None,
    )


# §5.3 forced row syntax, quoted verbatim for the self-teaching reason strings below. Keep this
# in sync with the CLAUDE.md "Signpost/Pillar Checklist Row Syntax" section — both channels must
# describe the same syntax (Slice 5, architecture §5.3).
_ROW_SYNTAX_EXAMPLE = (
    "- [x] <verbatim Signpost line text> (verified: tool_use_id=<id>)\n"
    "- [ ] <verbatim Signpost line text> (unverified)"
)

_TRANSCRIPT_LOOKUP_INSTRUCTION = (
    "A tool_use_id is never already visible in your reply context. Before writing a "
    "(verified: tool_use_id=<id>) row, you must actively look it up: read your own current "
    "session's transcript file (the most recently modified *.jsonl under "
    "~/.claude/projects/<project>/) and search backward from the end of that file for the "
    "tool_use block matching the call you want to cite, to read that block's real id. This is "
    "an active lookup step you must perform every time, not something already in your context. "
    "Skipping it leaves only two honest options: perform the lookup, or write (unverified)."
)

_ROW_SYNTAX_INSTRUCTION = (
    "Each Pillar row must be written in exactly one of these two forced forms, one row per "
    f"Signpost line, label copied verbatim from the Signpost line:\n{_ROW_SYNTAX_EXAMPLE}\n"
    f"{_TRANSCRIPT_LOOKUP_INSTRUCTION}"
)


def build_reason(result) -> str:
    """One sentence per violation, concatenated — quotes the exact Signpost/Pillar line text
    involved. Rule-0 (`signpost_heading_absent`) and rule-0a (`malformed_signpost`) results
    each get their own distinct, non-per-row message rather than a per-row violation list, and
    every reason string is a complete, self-teaching specification of the required row syntax
    (Slice 5, architecture §5.3) — not merely a list of which rows were violated — so an agent
    that hits this block without CLAUDE.md guidance in context can still recover."""
    if result.signpost_heading_absent:
        return (
            "Blocked: this turn was expected to include a Signpost section, but no Signpost "
            "heading was found in the reply. Add a `Signpost:` section listing each claim as "
            f"its own list item, and a matching `Pillar:` section. {_ROW_SYNTAX_INSTRUCTION}"
        )

    sentences = []
    for violation in result.violations:
        if violation.kind == "malformed_signpost":
            sentences.append(
                "Blocked: the Signpost section has content — including any text written "
                "directly on the `Signpost:` heading line — but no lines were written as list "
                "items (`-`, `*`, `+`, or `N.`), so no claims could be parsed. Rewrite each "
                "claim as its own list item; do not add a Pillar row without a matching "
                f"Signpost list item. {_ROW_SYNTAX_INSTRUCTION}"
            )
        elif violation.kind == "missing":
            sentences.append(
                f'Missing Pillar row for Signpost line: "{violation.signpost_text}". Add a row '
                f"in the required syntax:\n{_ROW_SYNTAX_EXAMPLE}\n{_TRANSCRIPT_LOOKUP_INSTRUCTION}"
            )
        elif violation.kind == "duplicate_label":
            sentences.append(
                f'Duplicate Pillar row label: "{violation.row.label}" matched more than one row. '
                "Each Signpost line may have exactly one matching Pillar row."
            )
        elif violation.kind == "stray_prose":
            sentences.append(
                f'Unrecognized line in Pillar section: "{violation.line_text}". Every '
                "non-blank line in the Pillar section must match the forced row syntax:\n"
                f"{_ROW_SYNTAX_EXAMPLE}"
            )
        elif violation.kind == "false_claim":
            sentences.append(
                f'Unbacked verification claim in row: "{violation.row.label}". A '
                "(verified: tool_use_id=<id>) row must cite a real tool_use_id found in this "
                f"turn's qualifying tool calls. {_TRANSCRIPT_LOOKUP_INSTRUCTION} If the claim "
                "was not actually verified, write (unverified) instead."
            )
        elif violation.kind == "duplicate_id":
            sentences.append(
                f'Reused tool_use_id in row: "{violation.row.label}". Each verified row must '
                "cite a distinct tool_use_id — one real tool call cannot back more than one row."
            )
        elif violation.kind == "unmatched_row":
            sentences.append(
                f'Pillar row does not match any Signpost line: "{violation.row.label}". This '
                "row's label does not equal any Signpost line's text. Either correct the label "
                "to match an existing Signpost line verbatim, or add the missing Signpost list "
                "item this row was meant to back — do not leave an orphaned row in place."
            )
        else:
            sentences.append(f"Unrecognized violation kind: {violation.kind}.")

    return " ".join(sentences)


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def emit_allow():
    # §3.2 (archived probe) — silence-means-allow; emitting nothing is equivalent to `{}`.
    pass


# --- §4/§5.4 run()/main() wiring --------------------------------------------


def _compute_signpost_section_has_content(text, signpost_idx, pillar_idx):
    """§4/§5.4 rule 0a — whether the Signpost section (heading line's trailing content,
    per the `Signpost:` label being stripped, PLUS every line strictly between the
    heading and the next heading/end-of-text) has any non-blank text, independent of
    whether that text parses into a list-item `SignpostLine`. Mirrors
    `extract_signpost_lines`'s own candidate-line collection so the two stay in sync;
    kept separate because `extract_signpost_lines` cannot itself distinguish "truly
    empty" from "content present but unparseable" by its return value alone (§4)."""
    if signpost_idx is None:
        return False

    lines = text.split("\n")
    section_end = pillar_idx if pillar_idx is not None else len(lines)

    candidate_lines = []

    heading_raw = lines[signpost_idx] if 0 <= signpost_idx < len(lines) else ""
    label_match = _SIGNPOST_LABEL_RE.match(strip_leading_markup(heading_raw))
    if label_match:
        trailing = label_match.group(1)
        if trailing:
            candidate_lines.append(trailing)

    for idx in range(signpost_idx + 1, section_end):
        if 0 <= idx < len(lines):
            candidate_lines.append(lines[idx])

    return any(line.strip() for line in candidate_lines)


def _find_pillar_section_end(lines, pillar_idx):
    """Same section-boundary scan as the archived probe's `run()` (line 674-683): from
    the line after the Pillar heading, the section ends at the next Signpost/Pillar
    heading match, or end-of-text."""
    if pillar_idx is None:
        return len(lines)
    section_end = len(lines)
    for idx in range(pillar_idx + 1, len(lines)):
        stripped = strip_leading_markup(lines[idx])
        if _SIGNPOST_PILLAR_HEADING_RE.match(stripped):
            section_end = idx
            break
    return section_end


def _serialize_violation(violation):
    """RowViolation -> a JSON-safe dict for the track-record log (§3's `EvaluationResult`
    shape, row-level — not the archived probe's C1/C2/C3 string-label schema)."""
    row = violation.row
    return {
        "kind": violation.kind,
        "signpost_text": violation.signpost_text,
        "row": (
            {
                "label": row.label,
                "status": row.status,
                "tool_use_id": row.tool_use_id,
                "raw_line": row.raw_line,
            }
            if row is not None
            else None
        ),
        "line_text": violation.line_text,
    }


def run(stdin_data: dict) -> None:
    """Top-level entry point, same stdin contract, same stop_hook_active / queue-marker /
    first-turn gating as the archived probe's `run()` (§5.1, unchanged) — that ordering is
    fixed and not reordered here. Once gating passes, locates the Signpost/Pillar sections,
    parses them, evaluates the checklist (§5.4), and emits block/allow, writing one
    track-record row on every path."""
    session_id = stdin_data.get("session_id")
    transcript_path = stdin_data.get("transcript_path")
    stop_hook_active = bool(stdin_data.get("stop_hook_active", False))
    last_assistant_message = stdin_data.get("last_assistant_message") or ""

    # §5.1 — stop_hook_active bypass, checked first. Always allow, no further processing.
    if stop_hook_active:
        write_track_record(session_id, True, False, False, "allow", [], None, None)
        emit_allow()
        return

    records = load_transcript_records(transcript_path)
    queue_injected, first_turn, current_turn_index = (
        analyze_queue_injection_and_first_turn(records)
    )

    if not queue_injected:
        write_track_record(session_id, False, False, False, "allow", [], None, None)
        emit_allow()
        return

    if not first_turn:
        write_track_record(session_id, False, True, False, "allow", [], None, None)
        emit_allow()
        return

    signpost_idx, pillar_idx = find_signpost_pillar_positions(last_assistant_message)
    signpost_heading_present = signpost_idx is not None
    signpost_section_has_content = _compute_signpost_section_has_content(
        last_assistant_message, signpost_idx, pillar_idx
    )
    signpost_lines = extract_signpost_lines(last_assistant_message, signpost_idx, pillar_idx)

    lines = last_assistant_message.split("\n")
    pillar_section_end = _find_pillar_section_end(lines, pillar_idx)
    pillar_rows, pillar_unparsed_lines = extract_pillar_rows(
        last_assistant_message, pillar_idx, pillar_section_end
    )

    preceding = records if current_turn_index is None else records[:current_turn_index]
    qualifying_calls = collect_qualifying_tool_calls(preceding)

    result = evaluate_checklist(
        signpost_lines,
        pillar_rows,
        qualifying_calls,
        signpost_heading_present,
        signpost_section_has_content,
        pillar_unparsed_lines,
    )

    if result.decision == "block":
        violations_payload = [_serialize_violation(v) for v in result.violations]
        write_track_record(
            session_id, False, True, True, "block", violations_payload, result.reason, None
        )
        emit_block(result.reason)
        return

    write_track_record(session_id, False, True, True, "allow", [], None, None)
    emit_allow()


def main():
    stdin_data = read_stdin()
    try:
        run(stdin_data)
    except Exception as exc:  # noqa: BLE001 — this probe must never crash into a block
        write_track_record(
            stdin_data.get("session_id"),
            stdin_data.get("stop_hook_active", False),
            False,
            False,
            "probe_error",
            [],
            None,
            f"{exc.__class__.__name__}: {exc}",
        )
        emit_allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
