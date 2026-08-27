"""Tests for scripts/first_turn_contract_probe.py — Slice 1 (probe core).

Spec: docs/tooling/first-turn-contract-enforcement.md §11 (acceptance criteria), scoped to this
slice per the forge task: AC 1, 2, 3, 6, and the schema half of AC 8 (§6's TrackRecordEntry
shape). AC 4-live-half, 5, 7, 9, 10 belong to later slices (wrapper, reference/ mirror, settings
wiring, .gitignore) and are intentionally not covered here.

Loads the copy the Stop hook is documented to execute (scripts/), never a reference/ mirror —
per this repo's own post-mortem on `test_session_queue_probe.py::test_reference_copy_matches_
executed_copy`, a suite that imports the wrong copy passes green against code nothing runs.

Exercises the real entry point, `probe.run(stdin_data)`, against real JSONL-shaped transcript
fixtures and the real captured-turn corpus in tests/fixtures/first_turn_contract_corpus.json —
never against the internals of a predicate in isolation (the other named failure mode: a test
that asserts on a regex instead of the outcome the consumer sees).

Runnable two ways:
    pytest tests/test_first_turn_contract_probe.py
    python3 tests/test_first_turn_contract_probe.py   (falls back to a plain assert-based runner)
"""

import importlib.util
import io
import json
import os
import sys
from contextlib import redirect_stdout

try:
    import pytest  # noqa: F401
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "first_turn_contract_probe.py")
REFERENCE_PROBE_PATH = os.path.join(REPO_ROOT, "reference", "first_turn_contract_probe.py")
CORPUS_PATH = os.path.join(REPO_ROOT, "tests", "fixtures", "first_turn_contract_corpus.json")
REAL_TRANSCRIPT_PATH = os.path.join(
    REPO_ROOT, "tests", "fixtures", "real_transcript_turn1.jsonl"
)


def _load_probe():
    spec = importlib.util.spec_from_file_location("first_turn_contract_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()

with open(CORPUS_PATH) as f:
    CORPUS = json.load(f)


# ---------------------------------------------------------------------------
# Transcript fixture builders — real JSONL-shaped records, not stubs. The probe
# parses these for the queue-injection marker (§5.1) and the C3 tool-call scan
# (§5.4); stubbing that parsing away would repeat the "asserts on a regex, not
# the real path" failure mode named in the task.
# ---------------------------------------------------------------------------

def _queue_marker_record():
    """Real SessionStart injection shape (§5.1), confirmed against
    tests/fixtures/real_transcript_turn1.jsonl record 1: `type: "attachment"`, no `message`
    key at all — `attachment.content` carries the injected text. A prior version of this
    builder used a synthetic `{"type": "user", "message": {...}}` shape that does not occur
    on this host; every one of this file's 12 original tests routed through it, so the suite
    could not see that the probe (before its own fix) never detected queue injection in a
    real session. Kept in the real shape now so any test written against this builder
    inherits reality rather than repeating that gap."""
    return {
        "parentUuid": None,
        "isSidechain": False,
        "attachment": {
            "type": "hook_additional_context",
            "content": [probe.QUEUE_MARKER + "\nSIGNPOST — from the queue.\n"],
            "hookName": "SessionStart",
            "toolUseID": "SessionStart",
            "hookEvent": "SessionStart",
        },
        "type": "attachment",
        "uuid": "test-attachment-uuid",
    }


def _assistant_text_record(text):
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {"content": [{"type": "text", "text": text}]},
    }


def _tool_use_record(name, tool_id):
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {"content": [{"type": "tool_use", "id": tool_id, "name": name}]},
    }


def _tool_use_record_with_input(name, tool_id, tool_input):
    """Same shape as `_tool_use_record`, but carrying a real `input` payload — needed for
    the C3 claim-subject-matching tests (spec §3.2), which read `tool_use.input`'s
    target fields. `_tool_use_record` above deliberately omits `input` (it exercises the
    absent-input fallback, §3.2), so this is a separate builder rather than a change to it."""
    return {
        "type": "assistant",
        "isSidechain": False,
        "message": {
            "content": [
                {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input}
            ]
        },
    }


def _tool_result_record(tool_id):
    return {
        "type": "user",
        "isSidechain": False,
        "message": {"content": [{"type": "tool_result", "tool_use_id": tool_id}]},
    }


def _write_transcript(tmp_path, records, name="transcript.jsonl"):
    path = tmp_path / name
    with open(path, "w") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    return str(path)


def _run_probe(monkeypatch, tmp_path, stdin_data, track_record_name="track-record.jsonl"):
    """Invoke probe.main() the way the wrapper does: JSON on stdin, decision (if any) on
    stdout, one track-record line appended to a temp file. Returns (stdout_text, entries)."""
    track_path = str(tmp_path / track_record_name)
    monkeypatch.setattr(probe, "TRACK_RECORD_PATH", track_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(stdin_data)))
    buf = io.StringIO()
    with redirect_stdout(buf):
        probe.main()
    entries = []
    if os.path.isfile(track_path):
        with open(track_path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return buf.getvalue().strip(), entries


def _decision(stdout_text):
    """None if silent (allow, §3.2); parsed dict if a decision object was printed."""
    if not stdout_text:
        return None
    return json.loads(stdout_text)


TRACK_RECORD_KEYS = {
    "timestamp", "session_id", "stop_hook_active", "queue_injected", "first_turn",
    "decision", "violations", "reason", "probe_error",
}


# ---------------------------------------------------------------------------
# AC1 — true_positive_c1_and_c2 -> block naming C1
# ---------------------------------------------------------------------------

def test_ac1_true_positive_c1_blocks_naming_c1(monkeypatch, tmp_path):
    """§11 AC1: feeding the real corpus's true_positive_c1_and_c2 turn (Pillar heading appears
    before any Signpost heading) as last_assistant_message must block, naming C1 and quoting the
    Pillar heading."""
    transcript = _write_transcript(tmp_path, [_queue_marker_record()])
    stdin_data = {
        "session_id": "s1",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C1 violation" in decision["reason"]
    assert entries[-1]["decision"] == "block"
    assert "C1" in entries[-1]["violations"]


# ---------------------------------------------------------------------------
# Real transcript fixture — tests/fixtures/real_transcript_turn1.jsonl, 8 records lifted
# verbatim (structure-preserved, payloads redacted) from the actual session transcript that
# produced true_positive_c1_and_c2 / true_positive_c2_heading. These drive the gating path
# (queue-injection detection, first-turn determination, end-to-end block) against the real
# record shapes Claude Code actually writes — `type: "attachment"` for the SessionStart
# injection, real `thinking`/`tool_use`/`tool_result` records — not a hand-built stand-in.
# This is the fixture that caught the probe reading only `message.content` and missing the
# `attachment.content`/`attachment.stdout` SessionStart shape entirely; every synthetic test
# in this file routed through `_queue_marker_record()` and could not see that gap.
# ---------------------------------------------------------------------------

def _load_real_fixture_lines():
    with open(REAL_TRANSCRIPT_PATH) as fh:
        return [line for line in (l.strip() for l in fh) if line]


def _write_real_fixture(tmp_path, name="real_transcript_turn1.jsonl", drop_marker=False):
    """Copy the committed real-shape fixture into tmp_path (never read/write the repo's copy
    directly from a test) with each invocation getting a fresh session_id-scoped file. If
    drop_marker is True, the SessionStart `attachment` record (line 1, the only record
    carrying QUEUE_MARKER) is excluded — the negative control proving detection keys on the
    marker's presence, not on the file merely existing."""
    lines = _load_real_fixture_lines()
    if drop_marker:
        lines = lines[1:]
    path = tmp_path / name
    with open(path, "w") as fh:
        for line in lines:
            fh.write(line + "\n")
    return str(path)


def test_real_fixture_is_detected_as_queue_injected_and_first_turn(monkeypatch, tmp_path):
    """Gating behaviour, driven by the real fixture rather than a synthetic record: the actual
    SessionStart `attachment` record must be recognized as the queue-injection marker, and with
    no assistant-text record yet in the transcript, this must read as the first turn."""
    transcript = _write_real_fixture(tmp_path)
    stdin_data = {
        "session_id": "s-real-detect",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": "compliant reply, no headings at all",
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""  # compliant content -> allow, but the point is what got recorded
    assert entries[-1]["queue_injected"] is True
    assert entries[-1]["first_turn"] is True


def test_real_fixture_end_to_end_blocks_true_positive_c1(monkeypatch, tmp_path):
    """§11 AC1, driven end-to-end against the real transcript that produced the violation: feed
    true_positive_c1_and_c2 as last_assistant_message with the real fixture as transcript_path.
    This is the exact case that was silently unreachable before the implementation fix — the
    probe read queue_injected=False against this transcript's real record shapes and allowed a
    known C1 violation."""
    transcript = _write_real_fixture(tmp_path, name="real_c1.jsonl")
    stdin_data = {
        "session_id": "s-real-c1",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C1" in entries[-1]["violations"]
    assert entries[-1]["queue_injected"] is True
    assert entries[-1]["first_turn"] is True


def test_real_fixture_without_marker_record_is_not_queue_injected(monkeypatch, tmp_path):
    """Negative control: the same real fixture with the SessionStart `attachment` record (the
    only record carrying QUEUE_MARKER) removed must read queue_injected=False and allow, even
    though every other real record (thinking, tool_use, tool_result) is still present and the
    file still parses. Proves detection keys on the marker itself, not on transcript shape or
    file presence generally — the file existing and parsing was never in question; whether the
    marker's absence is honored is."""
    transcript = _write_real_fixture(tmp_path, name="real_no_marker.jsonl", drop_marker=True)
    stdin_data = {
        "session_id": "s-real-no-marker",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["queue_injected"] is False
    assert entries[-1]["violations"] == []


# ---------------------------------------------------------------------------
# AC2 — true_positive_c2_heading -> block naming C2, quoting the offending heading
# ---------------------------------------------------------------------------

def test_ac2_true_positive_c2_blocks_naming_c2_and_quotes_heading(monkeypatch, tmp_path):
    """§11 AC2: the corpus's true_positive_c2_heading turn carries a forbidden "Not yet verified
    this session:" third section; the probe must block naming C2 and quote that heading."""
    transcript = _write_transcript(tmp_path, [_queue_marker_record()])
    stdin_data = {
        "session_id": "s2",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c2_heading"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C2" in entries[-1]["violations"]
    assert "C2 violation" in decision["reason"]
    assert "Not yet verified this session" in decision["reason"]


# ---------------------------------------------------------------------------
# AC3 — Pillar asserted with zero qualifying tool calls -> block naming C3
# ---------------------------------------------------------------------------

_COMPLIANT_SIGNPOST_THEN_PILLAR = (
    "**Signpost:** from the queue, not re-checked.\n\n"
    "**Pillar:** verified this session by method.\n"
)


def test_ac3_pillar_with_zero_tool_calls_blocks_naming_c3(monkeypatch, tmp_path):
    """§11 AC3: a Pillar heading asserted with NO tool calls anywhere in the preceding
    transcript must block, naming C3."""
    transcript = _write_transcript(tmp_path, [_queue_marker_record()])
    stdin_data = {
        "session_id": "s3a",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _COMPLIANT_SIGNPOST_THEN_PILLAR,
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "C3 violation" in decision["reason"]


def test_ac3_todowrite_only_transcript_still_violates_c3(monkeypatch, tmp_path):
    """§5.4 / §11 AC3: TodoWrite is explicitly excluded from the qualifying-tool-call set. A
    transcript whose only preceding tool call is TodoWrite (with a matching tool_result) must
    still be treated as zero qualifying tool calls and block naming C3 — otherwise the exclusion
    is unenforced (theater)."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record("TodoWrite", "toolu_1"),
        _tool_result_record("toolu_1"),
    ])
    stdin_data = {
        "session_id": "s3b",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _COMPLIANT_SIGNPOST_THEN_PILLAR,
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]


def test_ac3_qualifying_non_todowrite_tool_call_avoids_c3(monkeypatch, tmp_path):
    """Positive control for AC3/AC4: a real (non-TodoWrite) completed tool call preceding the
    Pillar heading satisfies C3 — combined with a compliant Signpost-then-Pillar order and no
    forbidden third section, the whole turn must allow. This is the "compliant Signpost-then-
    Pillar turn with a qualifying tool call" fixture named in §11 AC4."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record("Read", "toolu_2"),
        _tool_result_record("toolu_2"),
    ])
    stdin_data = {
        "session_id": "s3c",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _COMPLIANT_SIGNPOST_THEN_PILLAR,
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""  # silence means allow, §3.2
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["violations"] == []


# ---------------------------------------------------------------------------
# C3 claim-subject matching — SPEC.md docs/tooling/first-turn-contract-c3-claim-matching §5
# AC1-AC7. §5 AC3 (un-extractable subject fallback, both sub-cases) is already exercised by
# test_ac3_pillar_with_zero_tool_calls_blocks_naming_c3 (no qualifying call -> violation) and
# test_ac3_qualifying_non_todowrite_tool_call_avoids_c3 (qualifying call exists -> pass)
# above — both use _COMPLIANT_SIGNPOST_THEN_PILLAR, whose Pillar text ("verified this session
# by method") yields zero extracted claim subjects, so no new test duplicates that coverage
# here. §5 AC8 (non-C3 regression) is verified by running the full suite, not a new test.
# ---------------------------------------------------------------------------

def _signpost_then_pillar(pillar_text):
    return (
        "**Signpost:** from the queue, not re-checked.\n\n"
        f"**Pillar:** {pillar_text}\n"
    )


def test_c3_matching_ac1_true_positive_path_match_allows(monkeypatch, tmp_path):
    """§5 AC1: Pillar section names a file path; a Read call on exactly that path precedes the
    turn -> C3 passes (whole turn allows, given compliant Signpost-before-Pillar order)."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Read", "toolu_p1", {"file_path": "scripts/foo.py"}),
        _tool_result_record("toolu_p1"),
    ])
    stdin_data = {
        "session_id": "c3m-ac1",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `scripts/foo.py` behaves correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["violations"] == []


def test_c3_matching_ac2_true_negative_unrelated_target_blocks_c3(monkeypatch, tmp_path):
    """§5 AC2 — the exact gap being closed: Pillar section names file path A; a qualifying tool
    call exists but targets unrelated file path B (no substring/basename overlap, no other
    subject overlap) -> C3 violates, with the "subject(s) do not match" reason variant."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Read", "toolu_p2", {"file_path": "scripts/bar.py"}),
        _tool_result_record("toolu_p2"),
    ])
    stdin_data = {
        "session_id": "c3m-ac2",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `scripts/foo.py` behaves correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "do not match any qualifying tool" in decision["reason"]
    assert "scripts/foo.py" in decision["reason"]


def test_c3_matching_ac4_pr_number_match_allows(monkeypatch, tmp_path):
    """§5 AC4: Pillar claims "PR #42 was reviewed"; a Bash call with `gh pr view 42` in its
    command precedes the turn -> C3 passes."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Bash", "toolu_p4", {"command": "gh pr view 42"}),
        _tool_result_record("toolu_p4"),
    ])
    stdin_data = {
        "session_id": "c3m-ac4",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar("PR #42 was reviewed."),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["violations"] == []


def test_c3_matching_ac4_pr_number_mismatch_blocks_c3(monkeypatch, tmp_path):
    """§5 AC4 (negative half): Pillar claims "PR #42 was reviewed"; the only qualifying call
    references #7, a different number entirely -> C3 violates."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Bash", "toolu_p4n", {"command": "gh pr view 7"}),
        _tool_result_record("toolu_p4n"),
    ])
    stdin_data = {
        "session_id": "c3m-ac4-neg",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar("PR #42 was reviewed."),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]


def test_c3_matching_ac4a_pr_digit_substring_collision_blocks_c3(monkeypatch, tmp_path):
    """§5 AC4a — the false-positive this fix closes: Pillar claims "PR #4 was reviewed"; the
    only qualifying call references `gh pr view 42` (digit-substring superset, not an exact
    match), and no call references #4 exactly -> C3 must VIOLATE, not pass on the substring
    collision. Verifies §3.3's exact-equality carve-out for PR/issue numbers."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Bash", "toolu_p4a", {"command": "gh pr view 42"}),
        _tool_result_record("toolu_p4a"),
    ])
    stdin_data = {
        "session_id": "c3m-ac4a",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar("PR #4 was reviewed."),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "do not match any qualifying tool" in decision["reason"]


def test_c3_matching_ac4a_backtick_gh_command_digit_substring_collision_blocks_c3(
    monkeypatch, tmp_path
):
    """§5 AC4a gap closed: Pillar claims via backtick gh-command form `gh pr view 4`
    (not prose `#4`); the only qualifying call references `gh pr view 42` (digit-substring
    superset, not an exact match) -> C3 must VIOLATE. Verifies the backtick-gh-span claim
    extraction classifies `gh pr view 4` as a `pr` subject (value "4"), not a `command`
    subject, so it goes through the exact-match PR/issue-number carve-out instead of
    plain substring containment."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Bash", "toolu_p4b", {"command": "gh pr view 42"}),
        _tool_result_record("toolu_p4b"),
    ])
    stdin_data = {
        "session_id": "c3m-ac4a-backtick",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar("reviewed `gh pr view 4`."),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "do not match any qualifying tool" in decision["reason"]


def test_c3_matching_ac5a_partial_coverage_of_two_subjects_blocks_c3(monkeypatch, tmp_path):
    """§5 AC5a — require-all-subjects: Pillar section names two files; a qualifying tool call
    matches only one of them -> C3 violates (partial coverage is not enough)."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Read", "toolu_p5a", {"file_path": "scripts/foo.py"}),
        _tool_result_record("toolu_p5a"),
    ])
    stdin_data = {
        "session_id": "c3m-ac5a",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `scripts/foo.py` and `scripts/bar.py` both behave correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "scripts/bar.py" in decision["reason"]


def test_c3_matching_ac5b_full_coverage_of_two_subjects_allows(monkeypatch, tmp_path):
    """§5 AC5b: Pillar section names two files; qualifying tool calls collectively cover both
    subjects (one call per subject) -> C3 passes."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input("Read", "toolu_p5b1", {"file_path": "scripts/foo.py"}),
        _tool_result_record("toolu_p5b1"),
        _tool_use_record_with_input("Read", "toolu_p5b2", {"file_path": "scripts/bar.py"}),
        _tool_result_record("toolu_p5b2"),
    ])
    stdin_data = {
        "session_id": "c3m-ac5b",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `scripts/foo.py` and `scripts/bar.py` both behave correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["violations"] == []


def test_c3_matching_ac6_absolute_vs_relative_path_basename_match_allows(monkeypatch, tmp_path):
    """§5 AC6: claim quotes a relative path; the tool call's file_path is absolute with the
    same basename -> C3 passes via the basename fallback."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input(
            "Read", "toolu_p6", {"file_path": "/home/d-tuned/agent-rig/scripts/foo.py"}
        ),
        _tool_result_record("toolu_p6"),
    ])
    stdin_data = {
        "session_id": "c3m-ac6",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `scripts/foo.py` behaves correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["violations"] == []


def test_c3_matching_ac7_identifier_exact_match_collision_blocks_c3(monkeypatch, tmp_path):
    """§5 AC7: Pillar section names identifier subject `check_c3`; a qualifying tool call's
    target text contains the longer identifier `check_c3_violation` (substring-superset, no
    exact match) and no other qualifying call references `check_c3` exactly -> C3 must
    VIOLATE, not pass on the substring-containment collision. Verifies §3.3's exact-equality
    carve-out for identifier/symbol subjects."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _tool_use_record_with_input(
            "Bash", "toolu_p7", {"command": "grep -n check_c3_violation scripts/x.py"}
        ),
        _tool_result_record("toolu_p7"),
    ])
    stdin_data = {
        "session_id": "c3m-ac7",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": _signpost_then_pillar(
            "verified `check_c3` handles this correctly."
        ),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "C3" in entries[-1]["violations"]
    assert "do not match any qualifying tool" in decision["reason"]


# ---------------------------------------------------------------------------
# AC6 — stop_hook_active: true always allows, regardless of content
# ---------------------------------------------------------------------------

def test_ac6_stop_hook_active_allows_a_known_violating_fixture_on_second_call(monkeypatch, tmp_path):
    """§11 AC6: feed a known-violating fixture twice. First call (stop_hook_active absent/false)
    must block. Second call, same content, with stop_hook_active: true, must allow — proving the
    flag overrides content-based checks rather than merely being untested alongside them."""
    transcript = _write_transcript(tmp_path, [_queue_marker_record()])

    first_stdin = {
        "session_id": "s6",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout1, entries1 = _run_probe(monkeypatch, tmp_path, first_stdin, track_record_name="tr6.jsonl")
    assert _decision(stdout1)["decision"] == "block"

    second_stdin = dict(first_stdin)
    second_stdin["stop_hook_active"] = True
    stdout2, entries2 = _run_probe(monkeypatch, tmp_path, second_stdin, track_record_name="tr6.jsonl")
    assert stdout2 == ""
    assert entries2[-1]["decision"] == "allow"
    assert entries2[-1]["stop_hook_active"] is True


# ---------------------------------------------------------------------------
# must_not_block_prose_mentions — the false-positive guard
# ---------------------------------------------------------------------------

def test_must_not_block_prose_mentions_all_allow(monkeypatch, tmp_path):
    """§11 AC4 / §5.3's empirical basis: turns that merely discuss "Signpost"/"Pillar"/"not yet
    verified" in prose (not as headings) must never block. This is the single most load-bearing
    guard in the file — a probe that blocks on substring mentions would have flagged 6 of 7 real
    occurrences in the session that motivated this tool (§10's anti-pattern table)."""
    fixtures = CORPUS["must_not_block_prose_mentions"]
    for i, text in enumerate(fixtures):
        transcript = _write_transcript(tmp_path, [_queue_marker_record()], name=f"prose-{i}.jsonl")
        stdin_data = {
            "session_id": f"prose-{i}",
            "transcript_path": transcript,
            "stop_hook_active": False,
            "last_assistant_message": text,
        }
        stdout_text, entries = _run_probe(
            monkeypatch, tmp_path, stdin_data, track_record_name=f"tr-prose-{i}.jsonl"
        )
        assert stdout_text == "", (
            f"must_not_block_prose_mentions[{i}] blocked: {stdout_text}"
        )
        assert entries[-1]["decision"] == "allow"

    # Non-blocking shape sanity, AFTER the behavioural assertions above have already run
    # against every fixture — a corpus-shape surprise must never mask a false-positive
    # regression the way it did on the first attempt at this test (corpus was 3 entries,
    # the assertion ran first, and the guard silently checked nothing). Known-hard cases
    # are matched by content, not by index/length, so a regenerated corpus doesn't break
    # this on shape alone.
    assert len(fixtures) > 0
    joined = "\n".join(fixtures)
    assert "\"Not yet verified\" is me reporting an unfinished job as a finding" in joined
    assert "**There is no third section.**" in joined


# ---------------------------------------------------------------------------
# Not queue-injected -> allow unconditionally
# ---------------------------------------------------------------------------

def test_not_queue_injected_allows_even_with_violating_content(monkeypatch, tmp_path):
    """§5.1: a session whose transcript never carried the QUEUE_MARKER is not queue-injected;
    the probe must allow unconditionally, without running C1/C2/C3, even when the content would
    otherwise violate them."""
    transcript = _write_transcript(tmp_path, [
        {"type": "user", "isSidechain": False, "message": {"content": "no marker here"}},
    ])
    stdin_data = {
        "session_id": "s-noqueue",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["queue_injected"] is False
    assert entries[-1]["violations"] == []


# ---------------------------------------------------------------------------
# Turn 2+ -> allow (out of scope, §1)
# ---------------------------------------------------------------------------

def test_turn_two_of_session_allows_regardless_of_content(monkeypatch, tmp_path):
    """§5.1/§8: once a second assistant-text record already exists in the transcript, this is no
    longer the first turn and the probe has no opinion on it — allow, even with violating
    content in last_assistant_message."""
    transcript = _write_transcript(tmp_path, [
        _queue_marker_record(),
        _assistant_text_record("turn 1 reply, whatever shape"),
        _assistant_text_record("turn 2 reply — this is the current one"),
    ])
    stdin_data = {
        "session_id": "s-turn2",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["first_turn"] is False


# ---------------------------------------------------------------------------
# Track-record entry shape — §6 TrackRecordEntry, on block/allow/error paths
# ---------------------------------------------------------------------------

def test_track_record_entry_shape_on_block_path(monkeypatch, tmp_path):
    """§6/§11 AC8 (schema half): a block entry has exactly TrackRecordEntry's fields, with the
    right types, and reason non-null."""
    transcript = _write_transcript(tmp_path, [_queue_marker_record()])
    stdin_data = {
        "session_id": "s-shape-block",
        "transcript_path": transcript,
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert set(entry.keys()) == TRACK_RECORD_KEYS
    assert entry["decision"] == "block"
    assert isinstance(entry["violations"], list) and len(entry["violations"]) > 0
    assert isinstance(entry["reason"], str) and entry["reason"]
    assert entry["probe_error"] is None
    assert isinstance(entry["timestamp"], str) and entry["timestamp"]
    assert entry["session_id"] == "s-shape-block"


def test_track_record_entry_shape_on_allow_path(monkeypatch, tmp_path):
    """§6/§11 AC8: an allow entry has empty violations and a null reason."""
    stdin_data = {
        "session_id": "s-shape-allow",
        "transcript_path": None,
        "stop_hook_active": False,
        "last_assistant_message": "hello",
    }
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert set(entry.keys()) == TRACK_RECORD_KEYS
    assert entry["decision"] == "allow"
    assert entry["violations"] == []
    assert entry["reason"] is None
    assert entry["probe_error"] is None


def test_track_record_entry_shape_on_probe_error_path(monkeypatch, tmp_path):
    """§6/§11 AC8: main()'s own inner fail-open — if run() raises, the probe must still allow
    (emit nothing) and record a probe_error entry naming the exception class and message, not
    crash and not block. Fault-injected by monkeypatching a real function run() depends on to
    raise, exercising main()'s actual except path rather than asserting on it in isolation."""
    def _boom(*args, **kwargs):
        raise RuntimeError("injected fault")

    monkeypatch.setattr(probe, "load_transcript_records", _boom)
    stdin_data = {
        "session_id": "s-shape-error",
        "transcript_path": "/nonexistent/does/not/matter.jsonl",
        "stop_hook_active": False,
        "last_assistant_message": CORPUS["true_positive_c1_and_c2"],
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""  # never denies on its own failure
    entry = entries[-1]
    assert set(entry.keys()) == TRACK_RECORD_KEYS
    assert entry["decision"] == "probe_error"
    assert entry["violations"] == []
    assert entry["reason"] is None
    assert isinstance(entry["probe_error"], str) and "RuntimeError" in entry["probe_error"]
    assert "injected fault" in entry["probe_error"]


# ---------------------------------------------------------------------------
# Drift guard — reference/ vs scripts/ (spec §10, Slice 2)
# ---------------------------------------------------------------------------

def test_reference_copy_matches_executed_copy():
    """reference/ is the propagation template; scripts/ is what the Stop hook actually runs
    (this suite loads scripts/, per the header note above). A fix landing in one and not the
    other ships a probe nothing tested — the exact gap
    test_session_queue_probe.py::test_reference_copy_matches_executed_copy exists to catch for
    the sibling probe; this is the same guard for first_turn_contract_probe.py."""
    with open(PROBE_PATH, "rb") as f:
        executed = f.read()
    with open(REFERENCE_PROBE_PATH, "rb") as f:
        reference = f.read()
    assert executed == reference, (
        "reference/first_turn_contract_probe.py has drifted from "
        "scripts/first_turn_contract_probe.py — the tests exercise scripts/, so the reference "
        "copy would propagate untested code."
    )


# ---------------------------------------------------------------------------
# Plain assert-based runner (used if pytest is not installed)
# ---------------------------------------------------------------------------

def _run_without_pytest():
    import tempfile
    import types
    import inspect
    import pathlib

    class FakeMonkeypatch:
        def __init__(self):
            self._restores = []

        def setattr(self, obj, name, value):
            old = getattr(obj, name)
            self._restores.append((obj, name, old))
            setattr(obj, name, value)

        def undo(self):
            for obj, name, old in reversed(self._restores):
                setattr(obj, name, old)

    failures = []
    passed = 0
    mod = sys.modules[__name__]
    test_fns = [
        (name, fn) for name, fn in vars(mod).items()
        if name.startswith("test_") and isinstance(fn, types.FunctionType)
    ]
    for name, fn in test_fns:
        params = inspect.signature(fn).parameters
        kwargs = {}
        mp = None
        tmp_dir_ctx = None
        try:
            if "monkeypatch" in params:
                mp = FakeMonkeypatch()
                kwargs["monkeypatch"] = mp
            if "tmp_path" in params:
                tmp_dir_ctx = tempfile.TemporaryDirectory()
                kwargs["tmp_path"] = pathlib.Path(tmp_dir_ctx.name)
            fn(**kwargs)
            passed += 1
            print(f"PASS {name}")
        except Exception as exc:  # noqa: BLE001
            failures.append((name, exc))
            print(f"FAIL {name}: {exc}")
        finally:
            if mp is not None:
                mp.undo()
            if tmp_dir_ctx is not None:
                tmp_dir_ctx.cleanup()

    print(f"\n{passed}/{len(test_fns)} passed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    _run_without_pytest()
