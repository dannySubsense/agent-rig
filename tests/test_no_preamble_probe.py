"""Tests for scripts/no_preamble_probe.py — full feature, single slice.

Spec: docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md §13 (acceptance criteria).

Loads the copy the Stop hook is documented to execute (scripts/), never the reference/
mirror — per this repo's own precedent (test_first_turn_contract_probe.py's header note,
test_session_queue_probe.py's drift guard) a suite that imports the wrong copy passes
green against code nothing runs. A separate drift-guard test below confirms scripts/ and
reference/ are byte-identical, per AC8.

Exercises the real entry point, probe.main() via stdin, against constructed fixture
sentences drawn directly from SPEC.md's own worked examples (§13, §3, §5, §14) — never
against internal regex predicates in isolation, matching the sibling suite's stated
evidentiary standard (AC11).

Runnable two ways:
    pytest tests/test_no_preamble_probe.py
    python3 tests/test_no_preamble_probe.py   (falls back to a plain assert-based runner)
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
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "no_preamble_probe.py")
REFERENCE_PROBE_PATH = os.path.join(REPO_ROOT, "reference", "no_preamble_probe.py")
WRAPPER_PATH = os.path.join(REPO_ROOT, ".claude", "hooks", "no-preamble-no-meta-narration.sh")
REMINDER_PATH = os.path.join(REPO_ROOT, "scripts", "no_preamble_reminder.py")
SETTINGS_PATH = os.path.join(REPO_ROOT, ".claude", "settings.json")
GITIGNORE_PATH = os.path.join(REPO_ROOT, ".gitignore")
TRACK_RECORD_REL = "docs/tooling/no-preamble-no-meta-narration-track-record.jsonl"


def _load_probe():
    spec = importlib.util.spec_from_file_location("no_preamble_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()


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
    if not stdout_text:
        return None
    return json.loads(stdout_text)


TRACK_RECORD_KEYS = {
    "timestamp", "session_id", "stop_hook_active", "mode", "decision",
    "flagged_clauses", "reason", "probe_error",
}


def _stdin(message, session_id="s1", stop_hook_active=False):
    return {
        "session_id": session_id,
        "stop_hook_active": stop_hook_active,
        "last_assistant_message": message,
    }


# ---------------------------------------------------------------------------
# AC1 — narrating clause, no concrete-noun signal -> flagged (log_only), allow
# ---------------------------------------------------------------------------

def test_ac1_narration_with_no_concrete_noun_flags_and_allows(monkeypatch, tmp_path):
    """§13 AC1: "Let me dig into this and see what's going on." matches §3.2 ("Let me"),
    contains no §3.3 signal -> flagged track-record entry, mode log_only, allow to Claude Code."""
    stdin_data = _stdin("Let me dig into this and see what's going on.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    entry = entries[-1]
    assert entry["decision"] == "flagged"
    assert entry["mode"] == "log_only"
    assert len(entry["flagged_clauses"]) >= 1
    assert entry["reason"] is None


# ---------------------------------------------------------------------------
# AC2 — narrating clause WITH a §3.3 signal in the same clause -> allow, no flag
# ---------------------------------------------------------------------------

def test_ac2_narration_with_file_path_in_same_clause_allows_no_flag(monkeypatch, tmp_path):
    """§13 AC2: "I'll check config.yaml for the timeout value." matches §3.2 ("I'll") but
    config.yaml is a file-path-shaped token in the same clause -> allow, no flag."""
    stdin_data = _stdin("I'll check config.yaml for the timeout value.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    entry = entries[-1]
    assert entry["decision"] == "allow"
    assert entry["flagged_clauses"] == []


# ---------------------------------------------------------------------------
# AC3 — excluded past-tense verbs -> allow (verify exclusion is real, not just stated)
# ---------------------------------------------------------------------------

def test_ac3_excluded_past_tense_verbs_allow(monkeypatch, tmp_path):
    """§13 AC3: §3.2-excluded past-tense report-of-completed-action verbs must never trigger
    a §3.2 match at all -> allow, regardless of whether a concrete noun follows. Loops over
    3 of §3.2's excluded verbs (not parametrized, matching this repo's existing loop-based
    multi-fixture pattern in test_first_turn_contract_probe.py's prose-mentions test)."""
    for i, message in enumerate([
        "I confirmed the tests pass.",
        "I found the bug in the loop.",
        "I fixed the broken import.",
    ]):
        stdin_data = _stdin(message, session_id=f"s3-{i}")
        stdout_text, entries = _run_probe(
            monkeypatch, tmp_path, stdin_data, track_record_name=f"tr3-{i}.jsonl"
        )
        assert stdout_text == "", f"excluded past-tense verb fixture[{i}] did not allow: {message!r}"
        assert entries[-1]["decision"] == "allow"
        assert entries[-1]["flagged_clauses"] == []


# ---------------------------------------------------------------------------
# AC4 — §5.2 heading exemption fires on a genuinely-would-flag clause
# ---------------------------------------------------------------------------

def test_ac4_halt_heading_exempts_narrating_clause_that_would_otherwise_flag(monkeypatch, tmp_path):
    """§13 AC4 — the corrected positive control: "**HALT:** I need to get your decision on
    which option to take." The narrating clause ("I need to get your decision on which option
    to take") matches §3.2's "I need to" and contains no backtick/file-path/capitalized
    token/digit/quoted literal — it would flag without the §5.2 heading exemption. Must allow."""
    stdin_data = _stdin(
        "**HALT:** I need to get your decision on which option to take."
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["flagged_clauses"] == []


def test_ac4_negative_control_same_clause_without_heading_flags(monkeypatch, tmp_path):
    """Negative control for AC4: the identical narrating clause, without the HALT heading,
    must flag — proving the allow above is due to the exemption firing, not an unrelated
    reason (e.g. the clause never matching §3.2 to begin with)."""
    stdin_data = _stdin("I need to get your decision on which option to take.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "flagged"
    assert len(entries[-1]["flagged_clauses"]) >= 1


# ---------------------------------------------------------------------------
# AC5 — stop_hook_active: true always allows, regardless of content
# ---------------------------------------------------------------------------

def test_ac5_stop_hook_active_allows_known_flaggable_message_on_second_call(monkeypatch, tmp_path):
    """§13 AC5: feed a flaggable message twice. First call (stop_hook_active False) flags.
    Second call, same content, stop_hook_active True, allows — mirrors first-turn-contract-
    enforcement's AC6 shape."""
    first_stdin = _stdin("Let me dig into this and see what's going on.", session_id="s5")
    stdout1, entries1 = _run_probe(monkeypatch, tmp_path, first_stdin, track_record_name="tr5.jsonl")
    assert stdout1 == ""
    assert entries1[-1]["decision"] == "flagged"

    second_stdin = dict(first_stdin)
    second_stdin["stop_hook_active"] = True
    stdout2, entries2 = _run_probe(monkeypatch, tmp_path, second_stdin, track_record_name="tr5.jsonl")
    assert stdout2 == ""
    assert entries2[-1]["decision"] == "allow"
    assert entries2[-1]["stop_hook_active"] is True
    assert entries2[-1]["flagged_clauses"] == []


# ---------------------------------------------------------------------------
# AC6 — wrapper/probe failure never blocks, never crashes (fault injection)
# ---------------------------------------------------------------------------

def test_ac6_malformed_stdin_json_fails_open_to_allow(monkeypatch, tmp_path):
    """§13 AC6: malformed (non-JSON) stdin must not crash the probe — read_stdin() returns
    {} on parse failure, run() then treats it as an empty message -> allow."""
    track_path = str(tmp_path / "tr6a.jsonl")
    monkeypatch.setattr(probe, "TRACK_RECORD_PATH", track_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not valid json"))
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = probe.main()
    assert exit_code == 0
    assert buf.getvalue().strip() == ""


def test_ac6_probe_internal_exception_fails_open_and_records_probe_error(monkeypatch, tmp_path):
    """§13 AC6: fault-inject an exception inside run()'s own call graph (analyze) — main()'s
    outer try/except must catch it, emit nothing (allow), and write a probe_error entry,
    never propagate/crash and never block."""
    def _boom(*args, **kwargs):
        raise RuntimeError("injected fault")

    monkeypatch.setattr(probe, "analyze", _boom)
    stdin_data = _stdin("Let me dig into this.", session_id="s6b")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data, track_record_name="tr6b.jsonl")
    assert stdout_text == ""  # never blocks on its own failure
    entry = entries[-1]
    assert entry["decision"] == "probe_error"
    assert entry["flagged_clauses"] == []
    assert entry["reason"] is None
    assert isinstance(entry["probe_error"], str) and "RuntimeError" in entry["probe_error"]
    assert "injected fault" in entry["probe_error"]


# ---------------------------------------------------------------------------
# AC7 — MODE = "blocking" test-only override
# ---------------------------------------------------------------------------

def test_ac7_blocking_mode_emits_block_naming_flagged_clause_verbatim(monkeypatch, tmp_path):
    """§13 AC7: with MODE overridden to "blocking" (test-only), a flagged message produces
    {"decision": "block", "reason": ...} with the flagged clause quoted verbatim."""
    monkeypatch.setattr(probe, "MODE", "blocking")
    stdin_data = _stdin("Let me dig into this and see what's going on.", session_id="s7")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data, track_record_name="tr7.jsonl")
    decision = _decision(stdout_text)
    assert decision is not None
    assert decision["decision"] == "block"
    assert "Let me dig into this and see what's going on" in decision["reason"]
    assert entries[-1]["decision"] == "block"
    assert entries[-1]["mode"] == "blocking"
    assert entries[-1]["reason"] == decision["reason"]


def test_ac10_shipped_mode_constant_defaults_to_log_only():
    """§13 AC10: this document's §6.4 evidence standard exists before any promotion — the
    concrete, directly-checkable half of that requirement is that the shipped MODE constant
    is "log_only", not "blocking", by default (no test override applied)."""
    assert probe.MODE == "log_only"


# ---------------------------------------------------------------------------
# AC8 — artifact existence / wiring / drift-guard checks
# ---------------------------------------------------------------------------

def test_ac8_probe_exists_at_both_locations_and_is_byte_identical():
    assert os.path.isfile(PROBE_PATH)
    assert os.path.isfile(REFERENCE_PROBE_PATH)
    with open(PROBE_PATH, "rb") as f:
        executed = f.read()
    with open(REFERENCE_PROBE_PATH, "rb") as f:
        reference = f.read()
    assert executed == reference, (
        "reference/no_preamble_probe.py has drifted from scripts/no_preamble_probe.py — "
        "the tests exercise scripts/, so the reference copy would propagate untested code."
    )


def test_ac8_wrapper_and_reminder_artifacts_exist():
    assert os.path.isfile(WRAPPER_PATH)
    assert os.path.isfile(REMINDER_PATH)


# ---------------------------------------------------------------------------
# §6.1 — no_preamble_reminder.py behavioral test (not gated by a named AC, but
# a first-class component with defined output content per §6.1/§7 — shipping
# it with zero behavioral coverage is a real gap even though no AC in §13
# names it explicitly).
# ---------------------------------------------------------------------------

def _load_reminder():
    spec = importlib.util.spec_from_file_location("no_preamble_reminder", REMINDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SPEC_6_1_REMINDER_TEXT = (
    "NO-PREAMBLE REMINDER — do not open with intent-announcement, stall, or "
    "self-narration (\"I'll...\", \"Let me...\", \"I think I should...\", \"To be "
    "honest...\"). Start with the substantive action or the concrete answer. A "
    "Stop-hook check inspects this turn for exactly this pattern "
    "(docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md)."
)


def test_6_1_reminder_main_emits_json_matching_spec_literal_string(monkeypatch):
    """§6.1: invoke no_preamble_reminder.py the way UserPromptSubmit does — main() reads
    stdin (ignored, pure static injection) and prints hookSpecificOutput.additionalContext
    on stdout. Asserts the emitted JSON shape and the exact literal reminder text against
    SPEC.md §6.1's fenced block (SPEC_6_1_REMINDER_TEXT above, transcribed directly from the
    spec doc, not from the implementation), so a drift between the two would fail this test
    even if the implementation is internally self-consistent."""
    reminder = _load_reminder()
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = reminder.main()
    assert exit_code == 0
    payload = json.loads(buf.getvalue().strip())
    assert payload == {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": SPEC_6_1_REMINDER_TEXT,
        }
    }
    assert payload["hookSpecificOutput"]["additionalContext"] == SPEC_6_1_REMINDER_TEXT


def test_ac8_settings_json_wires_both_events():
    with open(SETTINGS_PATH) as f:
        settings = json.load(f)
    text = json.dumps(settings)
    assert "no_preamble_reminder.py" in text
    assert "no-preamble-no-meta-narration.sh" in text
    hooks = settings.get("hooks", {})
    assert "UserPromptSubmit" in hooks
    assert "Stop" in hooks


def test_ac8_gitignore_has_track_record_entry():
    with open(GITIGNORE_PATH) as f:
        content = f.read()
    assert TRACK_RECORD_REL in content


# ---------------------------------------------------------------------------
# AC9 — track-record log created, gitignored, schema-conformant per invocation
# ---------------------------------------------------------------------------

def test_ac9_track_record_entry_matches_schema_on_flag_path(monkeypatch, tmp_path):
    stdin_data = _stdin("Let me dig into this and see what's going on.", session_id="s9a")
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data, track_record_name="tr9a.jsonl")
    entry = entries[-1]
    assert set(entry.keys()) == TRACK_RECORD_KEYS
    assert entry["decision"] == "flagged"
    assert isinstance(entry["flagged_clauses"], list) and len(entry["flagged_clauses"]) > 0
    for clause in entry["flagged_clauses"]:
        assert set(clause.keys()) == {"text", "verb_matched"}
    assert entry["reason"] is None
    assert entry["probe_error"] is None
    assert isinstance(entry["timestamp"], str) and entry["timestamp"]
    assert entry["session_id"] == "s9a"


def test_ac9_track_record_entry_matches_schema_on_allow_path(monkeypatch, tmp_path):
    stdin_data = _stdin("I confirmed the tests pass.", session_id="s9b")
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data, track_record_name="tr9b.jsonl")
    entry = entries[-1]
    assert set(entry.keys()) == TRACK_RECORD_KEYS
    assert entry["decision"] == "allow"
    assert entry["flagged_clauses"] == []
    assert entry["reason"] is None
    assert entry["probe_error"] is None


def test_ac9_gitignore_predicate_is_honored_for_track_record_path():
    """§13 AC9: git check-ignore confirms the real track-record path (not a tmp_path stand-
    in) is ignored per the .gitignore entry asserted in test_ac8_gitignore_has_track_record_
    entry — i.e. an invocation against the real path would never show as dirty."""
    import subprocess
    result = subprocess.run(
        ["git", "check-ignore", TRACK_RECORD_REL],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"git check-ignore did not confirm {TRACK_RECORD_REL} is ignored "
        f"(stdout={result.stdout!r} stderr={result.stderr!r})"
    )


# ---------------------------------------------------------------------------
# Known false-positive class (§14) — bare epistemic-verb clause with substantive
# complement flags, as designed. Documented and verified, not fixed.
# ---------------------------------------------------------------------------

def test_known_false_positive_epistemic_verb_with_substantive_complement_flags(monkeypatch, tmp_path):
    """§14: "I think the bug is in `parse.py`." — §3.1's epistemic-verb clause boundary
    splits "I think" from its complement "the bug is in `parse.py`" before evaluating §3.3,
    so the complement's concrete noun (parse.py) never reaches the narrating clause. "I
    think" alone matches §3.2, has no concrete-noun signal of its own -> flags. This is the
    SPEC-predicted v1 characteristic (§14, not a bug), verified here as an executed check."""
    stdin_data = _stdin("I think the bug is in `parse.py`.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    entry = entries[-1]
    assert entry["decision"] == "flagged"
    assert any(c["verb_matched"] == "I think" for c in entry["flagged_clauses"])


# ---------------------------------------------------------------------------
# Regression — mid-word periods in file paths (e.g. config.yaml) must not split
# a clause boundary and strand the extension in the next clause.
# ---------------------------------------------------------------------------

def test_regression_midword_period_in_file_path_does_not_split_clause(monkeypatch, tmp_path):
    """Bug found and fixed during forge: a naive '.' clause-boundary regex would treat the
    period inside `config.yaml` as a sentence end, splitting "I'll check config" from "yaml
    for the timeout value" and stranding the file-path signal in the wrong clause span,
    causing a false flag. Must allow (matches AC2's fixture, this test targets the specific
    mid-word-period mechanism, not just the end-to-end outcome)."""
    stdin_data = _stdin("I'll check config.yaml for the timeout value.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["flagged_clauses"] == []

    # Direct unit check on the clause-splitting function itself, isolating the mechanism:
    # the period in "config.yaml" must not appear as a boundary end-position.
    text = "I'll check config.yaml for the timeout value."
    boundaries = probe.find_clause_boundaries(text)
    midword_period_pos = text.index("config.yaml") + len("config.")
    assert midword_period_pos not in boundaries


# ---------------------------------------------------------------------------
# Regression — §3.3(5) quoted-literal neutralizer was matching any apostrophe
# pair (contractions/possessives), not genuine quotes. Fixed with a lookaround
# regex requiring quote marks not adjacent to letters. Both fixtures below are
# SPEC.md §5.1's own worked examples of clauses that must flag.
# ---------------------------------------------------------------------------

def test_regression_contraction_apostrophes_do_not_falsely_neutralize_1(monkeypatch, tmp_path):
    """§5.1 worked example: "I'll take a look at what's going on." — before the fix, the
    apostrophes in "I'll" and "what's" were wrongly paired as a genuine quoted literal,
    neutralizing the clause. Must flag."""
    stdin_data = _stdin("I'll take a look at what's going on.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    entry = entries[-1]
    assert entry["decision"] == "flagged"
    assert len(entry["flagged_clauses"]) >= 1


def test_regression_contraction_apostrophes_do_not_falsely_neutralize_2(monkeypatch, tmp_path):
    """§5.1 worked example: "Let me look at what's here and see what's next." — two
    contractions' apostrophes must not be wrongly paired as a genuine quoted literal. Must
    flag."""
    stdin_data = _stdin("Let me look at what's here and see what's next.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    entry = entries[-1]
    assert entry["decision"] == "flagged"
    assert len(entry["flagged_clauses"]) >= 1


def test_regression_genuine_single_quoted_literal_still_neutralizes(monkeypatch, tmp_path):
    """Confirms the apostrophe-lookaround fix did not over-correct: a genuine quoted term
    ('Let me check the "timeout" setting.') must still allow — §3.3(5) exists to handle this
    case."""
    stdin_data = _stdin('Let me check the "timeout" setting.')
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["flagged_clauses"] == []


# ---------------------------------------------------------------------------
# Regression — §3.3(2) file-path signal, token-scoping fix. (See KNOWN ISSUE
# note below for the "and/or" fixture originally requested for this class:
# it does not actually distinguish old vs. new behavior and is omitted —
# reported back to @code-executor rather than encoded as a false-negative
# regression test.)
# ---------------------------------------------------------------------------

def test_regression_genuine_file_path_token_still_neutralizes(monkeypatch, tmp_path):
    """Confirms the token-scoping fix to §3.3(2) did not break the legitimate case: a real
    file-path token ("scripts/no_preamble_probe.py") in the same clause as the narrating verb
    must still allow."""
    stdin_data = _stdin("I'll check scripts/no_preamble_probe.py for the timeout.")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["flagged_clauses"] == []


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
