#!/usr/bin/env python3
"""Stop hook — no-preamble / no-meta-narration enforcement (probe core).

Reads Stop-hook stdin JSON and applies the grammatical rule of
docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md §3 to
`last_assistant_message`: a clause matching subject ("I"/"we") + an
internal/communicative verb, with no concrete noun in the same clause,
"flags". §5's exemptions (heading-label colons, HALT/BLOCKER/STATUS/
PROGRESS UPDATE/WAITING ON structural reports) apply on top.

Unlike scripts/first_turn_contract_probe.py, this probe:
  - does not gate on queue injection or first-turn status (applies to every turn);
  - never reads the transcript — `last_assistant_message` is the only input;
  - still checks `stop_hook_active` first and allows unconditionally if true.

Runs in one of two modes (§6.3), MODE below, flipped only by a deliberate code
change + commit, never by env var. Emits the block/allow decision Claude
Code's `Stop` hook understands (top-level `{"decision": "block", "reason":
...}`, or nothing/`{}` to allow) and appends one entry per invocation to the
gitignored track-record log (§8).

Pure function of stdin. No LORE access, no network. Never blocks on its own
failure — any exception here is caught and treated as an allow, with a
`probe_error` track-record entry (the wrapper's fail-open is the outer
guarantee; this is this probe's own inner one).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACK_RECORD_PATH = os.path.join(
    REPO_ROOT, "docs", "tooling", "no-preamble-no-meta-narration-track-record.jsonl"
)

# §6.3 — "log_only" | "blocking". Flipped only per §6.4's evidence bar, by a
# deliberate code change + commit, never by runtime env var.
MODE = "log_only"

# §3.2 — closed v1 verb set. Each entry: (canonical label, list of literal word
# sequences that all mean the same subject+verb match). Order matters only for
# the canonical label reported in track records; matching itself is
# whole-token, word-boundary anchored, case-insensitive, with one optional
# adverb allowed between the subject token ("I"/"We") and the rest of the verb
# phrase, per §3.2's own text.
_VERB_GROUPS = [
    ("I'll", ["I'll", "I will"]),
    ("I'm going to", ["I'm going to", "I am going to"]),
    ("I'm about to", ["I'm about to"]),
    ("I plan to", ["I plan to"]),
    ("I intend to", ["I intend to"]),
    ("I need to", ["I need to"]),
    ("I have to", ["I have to"]),
    ("I should", ["I should"]),
    ("I want to", ["I want to"]),
    ("I'd like to", ["I'd like to", "I would like to"]),
    ("I think", ["I think"]),
    ("I believe", ["I believe"]),
    ("I feel", ["I feel"]),
    ("I realize", ["I realize"]),
    ("I recognize", ["I recognize"]),
    ("I understand", ["I understand"]),
    ("Let me", ["Let me"]),
    ("Let's", ["Let's", "Let us"]),
    ("I'm", ["I'm", "I am"]),  # only when followed by a gerund-class word (see below)
    ("To be honest", ["To be honest"]),
    ("Honestly", ["Honestly"]),
    ("Frankly", ["Frankly"]),
    ("I apologize", ["I apologize"]),
    ("I'm sorry", ["I'm sorry"]),
    ("My apologies", ["My apologies"]),
    ("I should have", ["I should have"]),
    ("I made a mistake", ["I made a mistake"]),
    ("We'll", ["We'll", "We will"]),
    ("We're going to", ["We're going to", "We are going to"]),
    ("We need to", ["We need to"]),
    ("We should", ["We should"]),
]

# §3.2 — "I'm"/"I am" only counts when immediately followed by one of these.
_IM_FOLLOWERS = {"going", "trying", "working on", "doing", "starting", "looking"}

# §3.1 — the six epistemic verbs that are themselves a clause boundary.
_EPISTEMIC_VERBS = {"I think", "I believe", "I feel", "I realize", "I recognize", "I understand"}

# §3.2 — explicitly excluded past-tense report-of-completed-action verbs. Not part
# of the trigger set; listed here only to document the exclusion is deliberate.
_EXCLUDED_PAST_TENSE = {
    "I found", "I ran", "I read", "I wrote", "I changed", "I fixed",
    "I confirmed", "I verified",
}

# §3.3(3) — function words excluded from the capitalized-token signal.
_FUNCTION_WORDS = {"The", "This", "That", "These", "Those", "It", "A", "An"}

# §3.3(2) — file-path-shaped extension list.
_FILE_EXT_RE = re.compile(
    r"\b[\w-]+\.(md|py|ts|tsx|js|json|yaml|yml|sh|txt|log)\b", re.IGNORECASE
)

# §5.2 — HALT/BLOCKER/STATUS/PROGRESS UPDATE/WAITING ON structural exemption.
# Markup-stripped, first word of the line, optional parenthetical, then a colon.
_HEADING_MARKER_RE = re.compile(
    r'^[\s*_#]*(HALT|BLOCKER|STATUS|PROGRESS UPDATE|WAITING ON)\b'
    r'(\s*\([^)]*\))?\s*\**\s*:',
    re.IGNORECASE,
)

# Build one master regex per verb group: literal alternation, whole-token,
# word-boundary anchored, case-insensitive, with an optional single adverb
# word between the leading subject token ("I"/"We"/"Let") and the remainder.


def _compile_verb_patterns():
    patterns = []
    for label, variants in _VERB_GROUPS:
        for variant in variants:
            words = variant.split(" ")
            if len(words) > 1 and words[0] in ("I", "We", "Let"):
                # allow one optional adverb between the subject token and the rest
                escaped_rest = r"\s+".join(re.escape(w) for w in words[1:])
                pattern = (
                    r"\b" + re.escape(words[0]) + r"\b"
                    + r"(?:\s+\w+)?\s+"
                    + escaped_rest
                    + r"\b"
                )
            else:
                pattern = r"\b" + r"\s+".join(re.escape(w) for w in words) + r"\b"
            patterns.append((label, re.compile(pattern, re.IGNORECASE)))
    return patterns


_VERB_PATTERNS = _compile_verb_patterns()

_IM_RE = re.compile(r"\b(I'm|I am)\b\s*(?:\s+\w+)?\s*", re.IGNORECASE)


def strip_leading_markup(s):
    """Strip leading whitespace and markdown emphasis markers (#, *, _)."""
    while s and s[0] in " \t#*_":
        s = s[1:]
    return s


def _is_heading_label_line_prefix(prefix):
    """§3.4 — does `prefix` (markup-stripped text before a colon, on its own
    line) look like a capitalized-word/phrase heading label (not a narrating
    clause)?"""
    stripped = strip_leading_markup(prefix).strip()
    if not stripped:
        return False
    return bool(re.match(r"^[A-Z][A-Za-z0-9 '\-]*$", stripped))


def find_clause_boundaries(text):
    """§3.1 — return a sorted list of boundary end-positions (index in `text`
    right after the boundary token) from: sentence punctuation/semicolon,
    non-heading colons, comma+coordinating-conjunction, and line breaks."""
    boundaries = set()
    lines = text.split("\n")
    offset = 0
    for line in lines:
        # Sentence-ending punctuation only counts as a boundary when it is
        # followed by whitespace or end-of-line — a mid-word period (e.g. the
        # one in `config.yaml`) must not split the clause and strand the
        # file-path token's extension in the next clause.
        for m in re.finditer(r"[.!?;](?=\s|$)", line):
            boundaries.add(offset + m.end())
        for m in re.finditer(r":", line):
            colon_pos = m.start()
            prefix = line[:colon_pos]
            if not _is_heading_label_line_prefix(prefix):
                boundaries.add(offset + m.end())
        for m in re.finditer(r",\s+(?:and|but|so)\b", line, re.IGNORECASE):
            boundaries.add(offset + m.end())
        offset += len(line) + 1  # +1 for the '\n' consumed by split
        boundaries.add(min(offset, len(text)))  # line break boundary
    boundaries.add(len(text))
    return sorted(b for b in boundaries if 0 < b <= len(text))


def _match_epistemic_boundary(clause_text):
    """§3.1's sixth boundary type: if `clause_text` (after stripping leading
    markup) begins with one of the six epistemic verbs, return the end offset
    (within clause_text) of the matched verb phrase; else None."""
    stripped = strip_leading_markup(clause_text)
    lead_len = len(clause_text) - len(stripped)
    for verb in _EPISTEMIC_VERBS:
        m = re.match(r"\b" + re.escape(verb) + r"\b", stripped, re.IGNORECASE)
        if m:
            return lead_len + m.end()
    return None


def split_clauses(text):
    """Return a list of (start, end) spans over `text`, splitting first on
    §3.1's punctuation/conjunction/line-break boundaries, then further
    splitting each resulting span on the epistemic-verb boundary (§3.1)."""
    raw_boundaries = find_clause_boundaries(text)
    spans = []
    start = 0
    for b in raw_boundaries:
        if b > start:
            spans.append((start, b))
        start = b
    if start < len(text):
        spans.append((start, len(text)))

    final_spans = []
    for s, e in spans:
        clause_text = text[s:e]
        boundary_offset = _match_epistemic_boundary(clause_text)
        if boundary_offset is not None and (s + boundary_offset) < e:
            final_spans.append((s, s + boundary_offset))
            final_spans.append((s + boundary_offset, e))
        else:
            final_spans.append((s, e))
    return final_spans


def match_verb(clause_text):
    """§3.2 — does this clause match the subject+verb trigger pattern? Returns
    (verb_label) or None. Clause must match at clause start (after stripping
    leading markdown emphasis markers/whitespace)."""
    stripped = strip_leading_markup(clause_text)
    if not stripped:
        return None

    # "I'm"/"I am" special-case: only counts when immediately followed by one
    # of the listed gerund-class words.
    im_match = re.match(r"^(I'm|I am)\b", stripped, re.IGNORECASE)
    if im_match:
        rest = stripped[im_match.end():].lstrip()
        for follower in _IM_FOLLOWERS:
            if re.match(re.escape(follower) + r"\b", rest, re.IGNORECASE):
                return "I'm"
        # fall through — may still match a longer sequence below (e.g.
        # "I'm going to" is handled by its own explicit group), otherwise no match
        # from this special case alone.

    best = None
    for label, pattern in _VERB_PATTERNS:
        m = pattern.match(stripped)
        if m:
            if best is None or m.end() > best[1]:
                best = (label, m.end())
    if best:
        return best[0]
    return None


def is_neutralized(clause_text):
    """§3.3 — five-way concrete-noun test, any one signal neutralizes."""
    # 1. backtick-delimited code span
    if re.search(r"`[^`]+`", clause_text):
        return True
    # 2. file-path-shaped token (token-scoped: at least one whitespace-
    # delimited token containing a "/", or matching the file-extension regex)
    if any("/" in tok for tok in clause_text.split()) or _FILE_EXT_RE.search(clause_text):
        return True
    # 4. digit sequence
    if re.search(r"\d+", clause_text):
        return True
    # 5. quoted literal — a genuine opening/closing quote mark, not an
    # apostrophe used for a contraction ("I'll", "what's") or possessive
    # ("Frank's"). A real opening quote is not immediately preceded by a
    # letter; a real closing quote is not immediately followed by a letter.
    if re.search(r'"[^"]+"', clause_text) or re.search(
        r"(?<![A-Za-z])'[^']+'(?![A-Za-z])", clause_text
    ):
        return True
    # 3. capitalized multi-word/proper-noun token at position 2+
    tokens = re.findall(r"[A-Za-z][\w'\-]*", clause_text)
    for idx, tok in enumerate(tokens):
        if idx == 0:
            continue
        if tok[0].isupper() and tok not in _FUNCTION_WORDS:
            return True
    return False


def find_heading_exemption_span(text):
    """§5.2 — if `text` begins with a HALT/BLOCKER/STATUS/PROGRESS UPDATE/
    WAITING ON heading marker, return the end position of the marker's colon
    (and any trailing markup) so callers can exempt the heading clause and the
    clause immediately following it. Returns None if no such marker."""
    m = _HEADING_MARKER_RE.match(text)
    if not m:
        return None
    end = m.end()
    while end < len(text) and text[end] in "*_ \t":
        end += 1
    return end


def read_stdin():
    """Best-effort stdin JSON parse. Absence or malformed stdin must not crash
    the probe; the caller treats a resulting empty dict as "nothing to
    check", which allows."""
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


def analyze(last_assistant_message):
    """Returns a list of {"text": ..., "verb_matched": ...} for every flagged
    clause in `last_assistant_message`, per §3.5 and §5's exemptions."""
    if not last_assistant_message:
        return []

    heading_exempt_end = find_heading_exemption_span(last_assistant_message)

    spans = split_clauses(last_assistant_message)
    flagged = []
    exempted_next = False
    for s, e in spans:
        clause_text = last_assistant_message[s:e]

        # §5.2 — heading clause itself, or the clause immediately following it.
        if heading_exempt_end is not None and s < heading_exempt_end:
            exempted_next = True
            continue
        if exempted_next:
            exempted_next = False
            continue

        verb = match_verb(clause_text)
        if verb is None:
            continue
        if is_neutralized(clause_text):
            continue
        flagged.append({"text": clause_text.strip(), "verb_matched": verb})
    return flagged


def build_reason(flagged_clauses):
    parts = [
        f'flagged clause: "{c["text"]}" (matched "{c["verb_matched"]}", §3.2)'
        for c in flagged_clauses
    ]
    return (
        "no-preamble-no-meta-narration violation — "
        + "; ".join(parts)
        + ". Restate the turn leading with the substantive content, not the "
        "narrating clause(s) above."
    )


def write_track_record(session_id, stop_hook_active, mode, decision, flagged_clauses,
                        reason, probe_error):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "stop_hook_active": bool(stop_hook_active),
        "mode": mode,
        "decision": decision,
        "flagged_clauses": flagged_clauses,
        "reason": reason,
        "probe_error": probe_error,
    }
    try:
        os.makedirs(os.path.dirname(TRACK_RECORD_PATH), exist_ok=True)
        with open(TRACK_RECORD_PATH, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        # The track record is an audit trail, not a gate — a write failure
        # here must not change or block the probe's decision to Claude Code.
        pass


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def emit_allow():
    # §6.2 — silence-means-allow; emitting nothing is equivalent to `{}`.
    pass


def run(stdin_data):
    session_id = stdin_data.get("session_id")
    stop_hook_active = bool(stdin_data.get("stop_hook_active", False))
    last_assistant_message = stdin_data.get("last_assistant_message") or ""

    # §6.2 — checked first, before any check runs. Always allow.
    if stop_hook_active:
        write_track_record(session_id, True, MODE, "allow", [], None, None)
        emit_allow()
        return

    flagged_clauses = analyze(last_assistant_message)

    if not flagged_clauses:
        write_track_record(session_id, False, MODE, "allow", [], None, None)
        emit_allow()
        return

    if MODE == "blocking":
        reason = build_reason(flagged_clauses)
        write_track_record(session_id, False, MODE, "block", flagged_clauses, reason, None)
        emit_block(reason)
        return

    # log_only (§6.3 default) — record the flag, always allow.
    write_track_record(session_id, False, MODE, "flagged", flagged_clauses, None, None)
    emit_allow()


def main():
    stdin_data = read_stdin()
    try:
        run(stdin_data)
    except Exception as exc:  # noqa: BLE001 — this probe must never crash into a block
        write_track_record(
            stdin_data.get("session_id"),
            stdin_data.get("stop_hook_active", False),
            MODE,
            "probe_error",
            [],
            None,
            f"{exc.__class__.__name__}: {exc}",
        )
        emit_allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
