"""Signpost/Pillar checklist probe — new probe core for the signpost-checklist-redesign sprint.

Replaces `first_turn_contract_probe.py`'s C1/C2/C3 body. See
`docs/specs/signpost-checklist-redesign/02-ARCHITECTURE.md` for the governing design.

Slice 1 added the data schemas (§3) and the three new verbatim parsers (§4, §5.3):
`extract_signpost_lines`, `extract_pillar_rows`, `parse_checklist_row_line`.

Slice 2 (this addition) copies the architecture-designated §5.1 trigger-surface/tool-call-
collection functions from the archived probe (archive/first-turn-contract-enforcement/scripts/
first_turn_contract_probe.py), unmodified in behavior, plus one additive change per §5.1a
(`collect_qualifying_tool_calls()`). `evaluate_checklist`/`build_reason`/`run`/`main` (§5.4) are
added in a later slice.
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


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def emit_allow():
    # §3.2 (archived probe) — silence-means-allow; emitting nothing is equivalent to `{}`.
    pass
