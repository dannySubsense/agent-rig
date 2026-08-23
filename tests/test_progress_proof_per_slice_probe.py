"""Tests for scripts/progress_proof_per_slice_probe.py — probe core.

Spec: docs/tooling/progress-md-proof-per-slice-hook/SPEC.md §8 (acceptance criteria), against
the current, redesigned §6 (identity-based matching, SLICE-ID added 2026-08-23) — not the
earlier index-based design described in GATE-LOG.md's history.

Loads scripts/progress_proof_per_slice_probe.py directly (the file the wrapper is documented to
execute), exercises the real entry point probe.main() against PreToolUse-Edit-shaped stdin JSON,
same harness pattern as tests/test_domain_boundary_provenance_probe.py.

AC12 (PROVISIONAL-marker presence in the spec doc itself) is a doc-content check, not a
probe-behavior criterion, and is not covered here — same carve-out the sibling test file applies
to its own doc-only AC.

Runnable two ways:
    pytest tests/test_progress_proof_per_slice_probe.py
    python3 tests/test_progress_proof_per_slice_probe.py   (falls back to a plain assert-based runner)
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
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "progress_proof_per_slice_probe.py")


def _load_probe():
    spec = importlib.util.spec_from_file_location("progress_proof_per_slice_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()

TRACK_RECORD_KEYS = {
    "timestamp", "session_id", "file_path", "file_in_scope", "transitions_found",
    "transitions_verified", "matched_by", "proof_status", "decision", "reason", "probe_error",
}


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _write_allowlist(project_dir, prefixes=None, raw=None):
    allowlist_dir = project_dir / "docs" / "tooling"
    allowlist_dir.mkdir(parents=True, exist_ok=True)
    path = allowlist_dir / "progress-proof-allowlist.json"
    if raw is not None:
        path.write_text(raw)
        return str(path)
    data = {
        "schemaVersion": 1,
        "allowedCommandPrefixes": prefixes if prefixes is not None else ["python3 scripts/"],
    }
    path.write_text(json.dumps(data))
    return str(path)


def _write_dummy_script(project_dir, name, exit_code=0, sleep_seconds=None):
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    path = scripts_dir / name
    lines = ["import sys"]
    if sleep_seconds is not None:
        lines.append("import time")
        lines.append(f"time.sleep({sleep_seconds})")
    lines.append(f"sys.exit({exit_code})")
    path.write_text("\n".join(lines) + "\n")
    return f"python3 scripts/{name}"


def _track_record_path(project_dir):
    return project_dir / "docs" / "tooling" / "progress-proof-per-slice-track-record.jsonl"


def _read_entries(project_dir):
    tr_path = _track_record_path(project_dir)
    if not tr_path.is_file():
        return []
    entries = []
    with open(tr_path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _run_probe(monkeypatch, project_dir, stdin_data):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_dir))
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(stdin_data)))
    buf = io.StringIO()
    with redirect_stdout(buf):
        probe.main()
    return buf.getvalue().strip(), _read_entries(project_dir)


def _decision(stdout_text):
    if not stdout_text:
        return None
    return json.loads(stdout_text)


def _edit_stdin(file_path, old_string, new_string, session_id="s1"):
    return {
        "session_id": session_id,
        "tool_name": "Edit",
        "tool_input": {
            "file_path": file_path,
            "old_string": old_string,
            "new_string": new_string,
        },
        "cwd": file_path,
    }


PROGRESS_PATH_SEGMENT = os.path.join("docs", "specs", "sprint", "PROGRESS.md")


def _progress_path(project_dir):
    p = project_dir / "docs" / "specs" / "sprint" / "PROGRESS.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)


# ---------------------------------------------------------------------------
# AC1 — out-of-scope filename always allowed, file_in_scope: false
# ---------------------------------------------------------------------------

def test_ac1_out_of_scope_filename_allows_with_file_in_scope_false(monkeypatch, tmp_path):
    target = tmp_path / "docs" / "notes.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    stdin_data = _edit_stdin(
        str(target),
        old_string="- [ ] Slice 1: thing\n",
        new_string="- [x] Slice 1: thing\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["file_in_scope"] is False


# ---------------------------------------------------------------------------
# AC2 — no candidate lines, or candidates yielding no matched pair -> allow, transitions_found: 0
# ---------------------------------------------------------------------------

def test_ac2_no_candidate_lines_allows_with_transitions_found_zero(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="Some prose line, not a checkbox.\n",
        new_string="Some prose line, edited.\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 0


def test_ac2_candidates_with_no_matched_pair_allows(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    # old-open candidate with a description that never appears among new-done candidates.
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice A: unrelated pending work\n",
        new_string="- [x] Slice B: a totally different, already-complete slice\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 0


# ---------------------------------------------------------------------------
# AC3 — matched transition, no PROOF: marker on new-done candidate -> always allow
# ---------------------------------------------------------------------------

def test_ac3_matched_transition_no_proof_marker_allows(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice 1: no proof declared\n",
        new_string="- [x] Slice 1: no proof declared\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 1
    assert entries[-1]["proof_status"] is None


# ---------------------------------------------------------------------------
# AC4 — matched transition, PROOF: command not allowlisted -> allow, manual_unverified
# ---------------------------------------------------------------------------

def test_ac4_non_allowlisted_proof_command_allows_manual_unverified(monkeypatch, tmp_path):
    _write_allowlist(tmp_path, prefixes=["pytest "])
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice 1: thing — PROOF: curl https://example.com\n",
        new_string="- [x] Slice 1: thing — PROOF: curl https://example.com\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["proof_status"] == "manual_unverified"


# ---------------------------------------------------------------------------
# AC5/AC11 — allowlisted proof command: pass/fail/timeout
# ---------------------------------------------------------------------------

def test_ac5_allowlisted_passing_proof_allows_verified_pass(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "pass.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 1: thing — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 1: thing — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["proof_status"] == "verified_pass"
    assert entries[-1]["transitions_verified"] == 1


def test_ac6_allowlisted_failing_proof_denies_verified_fail(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "fail.py", exit_code=1)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 1: thing — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 1: thing — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "thing" in decision["reason"]
    assert cmd in decision["reason"]
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "verified_fail"


def test_ac6_allowlisted_timing_out_proof_denies_verified_timeout(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "slow.py", exit_code=0, sleep_seconds=2)
    monkeypatch.setattr(probe, "INNER_TIMEOUT", 0.2)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 1: thing — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 1: thing — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "verified_timeout"


# ---------------------------------------------------------------------------
# AC7 — line-count/line-order independence
# ---------------------------------------------------------------------------

def test_ac7_line_count_mismatch_with_real_transition_still_detected(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "pass.py", exit_code=0)
    target = _progress_path(tmp_path)
    old_string = (
        "- [ ] Slice 1: thing — PROOF: " + cmd + "\n"
    )
    # new_string has an extra, unrelated inserted line -> line-count mismatch.
    new_string = (
        "- [x] Slice 1: thing — PROOF: " + cmd + "\n"
        "- [ ] Slice 2: brand new unrelated slice added this edit\n"
    )
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 1
    assert entries[-1]["proof_status"] == "verified_pass"


def test_ac7_reordering_preserves_detection(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "pass.py", exit_code=0)
    target = _progress_path(tmp_path)
    old_string = (
        f"- [ ] Slice A: has proof — PROOF: {cmd}\n"
        "- [ ] Slice B: no proof declared\n"
    )
    # Same two lines, order swapped, Slice A flipped to done with PROOF unchanged.
    new_string = (
        "- [ ] Slice B: no proof declared\n"
        f"- [x] Slice A: has proof — PROOF: {cmd}\n"
    )
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 1
    assert entries[-1]["matched_by"] == "description"
    assert entries[-1]["proof_status"] == "verified_pass"


# ---------------------------------------------------------------------------
# AC7a — SLICE-ID matching survives simultaneous description+PROOF mutation
# ---------------------------------------------------------------------------

def test_ac7a_slice_id_match_survives_simultaneous_mutation(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    old_cmd = _write_dummy_script(tmp_path, "old.py", exit_code=0)
    new_cmd = _write_dummy_script(tmp_path, "new.py", exit_code=0)
    target = _progress_path(tmp_path)
    old_string = (
        f"- [ ] Slice 9: old wording — SLICE-ID: slice-09 — PROOF: {old_cmd}\n"
    )
    new_string = (
        f"- [x] Slice 9: new wording (renamed) — SLICE-ID: slice-09 — PROOF: {new_cmd}\n"
    )
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["matched_by"] == "slice_id"
    assert entries[-1]["proof_status"] == "verified_pass"


def test_ac7a_slice_id_match_never_produces_mutation_denied_on_fail(monkeypatch, tmp_path):
    """Even when the new-side proof fails, an ID-matched pair denies via verified_fail, never
    mutation_denied — §7's schema note: 'Never produced for a matched_by: slice_id pair.'"""
    _write_allowlist(tmp_path)
    old_cmd = _write_dummy_script(tmp_path, "old2.py", exit_code=0)
    new_cmd = _write_dummy_script(tmp_path, "new2.py", exit_code=1)
    target = _progress_path(tmp_path)
    old_string = f"- [ ] Slice 9: old wording — SLICE-ID: slice-09 — PROOF: {old_cmd}\n"
    new_string = f"- [x] Slice 9: new wording — SLICE-ID: slice-09 — PROOF: {new_cmd}\n"
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["matched_by"] == "slice_id"
    assert entries[-1]["proof_status"] == "verified_fail"


# ---------------------------------------------------------------------------
# AC7b — absence of SLICE-ID falls back to content-based matching, and correctly
# does NOT catch the simultaneous-mutation dodge (the honestly-stated residual).
# ---------------------------------------------------------------------------

def test_ac7b_no_slice_id_falls_back_to_content_matching_regression(monkeypatch, tmp_path):
    """Plain description-preserved match with no SLICE-ID still works as before."""
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "pass.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 3: stable wording — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 3: stable wording — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["matched_by"] == "description"
    assert entries[-1]["proof_status"] == "verified_pass"


def test_ac7b_no_slice_id_simultaneous_mutation_is_allowed_as_unmatched_not_denied(
    monkeypatch, tmp_path
):
    """The honestly-stated residual (§6): with no SLICE-ID on either side, a simultaneous
    description+PROOF mutation falls through as two unmatched candidates -> allow,
    transitions_found: 0. This must be asserted as ALLOWED (the documented residual), not denied
    — denying it would be a stronger, undocumented guarantee this hook does not make."""
    _write_allowlist(tmp_path)
    old_cmd = _write_dummy_script(tmp_path, "old3.py", exit_code=0)
    new_cmd = _write_dummy_script(tmp_path, "new3.py", exit_code=0)
    target = _progress_path(tmp_path)
    old_string = f"- [ ] Slice 9: old wording — PROOF: {old_cmd}\n"
    new_string = f"- [x] Slice 9: new wording (renamed) — PROOF: {new_cmd}\n"
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 0


# ---------------------------------------------------------------------------
# Description-only / PROOF-only mutation -> C2 deny
# ---------------------------------------------------------------------------

def test_proof_only_mutation_denies_matched_by_description(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    old_cmd = _write_dummy_script(tmp_path, "old4.py", exit_code=0)
    new_cmd = _write_dummy_script(tmp_path, "new4.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 4: identical wording — PROOF: {old_cmd}\n",
        new_string=f"- [x] Slice 4: identical wording — PROOF: {new_cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "mutation_denied"
    assert entries[-1]["matched_by"] == "description"
    # command never executed for a mutation-denied pair — no track-record verified count.
    assert entries[-1]["transitions_verified"] == 0


def test_proof_removed_on_completion_denies_matched_by_description(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "removed.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 5: identical wording — PROOF: {cmd}\n",
        new_string="- [x] Slice 5: identical wording\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["proof_status"] == "mutation_denied"
    assert entries[-1]["matched_by"] == "description"


def test_description_only_mutation_denies_matched_by_proof_identity(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "stable.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 6: old wording — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 6: reworded description — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "mutation_denied"
    assert entries[-1]["matched_by"] == "proof_identity"


# ---------------------------------------------------------------------------
# Adding a PROOF while completing (no PROOF on old, new adds one) -> verified, not silently allowed
# ---------------------------------------------------------------------------

def test_adding_proof_on_completion_is_verified_not_silently_allowed(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "added.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice 7: no proof yet\n",
        new_string=f"- [x] Slice 7: no proof yet — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["matched_by"] == "description"
    assert entries[-1]["proof_status"] == "verified_pass"
    assert entries[-1]["transitions_verified"] == 1


def test_adding_proof_on_completion_denies_when_added_command_fails(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "added_fail.py", exit_code=1)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice 7: no proof yet\n",
        new_string=f"- [x] Slice 7: no proof yet — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "verified_fail"


# ---------------------------------------------------------------------------
# Ambiguous duplicate identity -> conservative deny
# ---------------------------------------------------------------------------

def test_ambiguous_duplicate_description_denied(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    old_string = (
        "- [ ] Slice N: same wording\n"
        "- [ ] Slice N: same wording\n"
    )
    new_string = "- [x] Slice N: same wording\n"
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "ambiguous_match_denied"
    assert entries[-1]["matched_by"] is None


def test_duplicate_description_no_completion_allowed(monkeypatch, tmp_path):
    """Non-ambiguous counterpart: duplicate pending descriptions with no [x] completion claim
    for that description at all -> allowed, not ambiguous."""
    target = _progress_path(tmp_path)
    old_string = (
        "- [ ] Slice N: same wording\n"
        "- [ ] Slice N: same wording\n"
    )
    new_string = (
        "- [ ] Slice N: same wording\n"
        "- [ ] Slice N: same wording\n"
    )
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 0


def test_ambiguous_duplicate_slice_id_denied(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    old_string = (
        "- [ ] Slice X: a — SLICE-ID: dup-id\n"
        "- [ ] Slice Y: b — SLICE-ID: dup-id\n"
    )
    new_string = "- [x] Slice X: a — SLICE-ID: dup-id\n"
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["proof_status"] == "ambiguous_match_denied"
    assert entries[-1]["matched_by"] is None


# ---------------------------------------------------------------------------
# transition-with-inserted-completion-metadata
# ---------------------------------------------------------------------------

def test_inserted_completion_metadata_between_description_and_proof_is_verified(
    monkeypatch, tmp_path
):
    _write_allowlist(tmp_path)
    cmd = _write_dummy_script(tmp_path, "meta.py", exit_code=0)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 4: Wrapper wiring — PROOF: {cmd}\n",
        new_string=(
            f"- [x] Slice 4: Wrapper wiring — COMPLETE 2026-08-22 (15/15 tests) — PROOF: {cmd}\n"
        ),
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["proof_status"] == "verified_pass"


# ---------------------------------------------------------------------------
# multiple-transitions-in-one-edit-mixed-outcomes
# ---------------------------------------------------------------------------

def test_multiple_transitions_mixed_outcomes_denies_whole_edit(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    pass_cmd = _write_dummy_script(tmp_path, "mixed_pass.py", exit_code=0)
    fail_cmd = _write_dummy_script(tmp_path, "mixed_fail.py", exit_code=1)
    target = _progress_path(tmp_path)
    old_string = (
        f"- [ ] Slice 1: passes — PROOF: {pass_cmd}\n"
        f"- [ ] Slice 2: fails — PROOF: {fail_cmd}\n"
    )
    new_string = (
        f"- [x] Slice 1: passes — PROOF: {pass_cmd}\n"
        f"- [x] Slice 2: fails — PROOF: {fail_cmd}\n"
    )
    stdin_data = _edit_stdin(target, old_string=old_string, new_string=new_string)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["transitions_found"] == 2


# ---------------------------------------------------------------------------
# Already-[x] lines never inspected (construction guarantee)
# ---------------------------------------------------------------------------

def test_already_done_old_line_is_never_treated_as_old_open_candidate(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [x] Slice 1: already done, editing trailing metadata\n",
        new_string="- [x] Slice 1: already done, editing trailing metadata (typo fixed)\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["transitions_found"] == 0


# ---------------------------------------------------------------------------
# Fail-open: no manifest/allowlist present, malformed allowlist, probe crash
# ---------------------------------------------------------------------------

def test_no_allowlist_present_always_allows_manual_unverified(monkeypatch, tmp_path):
    cmd = "python3 scripts/does_not_matter.py"
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 1: thing — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 1: thing — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["proof_status"] == "manual_unverified"


def test_malformed_allowlist_json_allows_manual_unverified(monkeypatch, tmp_path):
    _write_allowlist(tmp_path, raw="{not valid json")
    cmd = "python3 scripts/does_not_matter.py"
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string=f"- [ ] Slice 1: thing — PROOF: {cmd}\n",
        new_string=f"- [x] Slice 1: thing — PROOF: {cmd}\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["proof_status"] == "manual_unverified"


def test_probe_crash_allows_and_records_probe_error(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice 1: thing\n",
        new_string="- [x] Slice 1: thing\n",
    )

    def _boom(*args, **kwargs):
        raise RuntimeError("injected fault")

    monkeypatch.setattr(probe, "load_allowlist", _boom)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "probe_error"
    assert isinstance(entries[-1]["probe_error"], str) and "RuntimeError" in entries[-1]["probe_error"]
    assert "injected fault" in entries[-1]["probe_error"]


def test_malformed_stdin_allows(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(sys, "stdin", io.StringIO("{not valid json"))
    buf = io.StringIO()
    with redirect_stdout(buf):
        probe.main()
    assert buf.getvalue().strip() == ""


def test_non_edit_tool_allows_unconditionally(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = {
        "session_id": "s-write",
        "tool_name": "Write",
        "tool_input": {"file_path": target, "content": "- [x] Slice 1: thing\n"},
        "cwd": str(tmp_path),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"


def test_missing_old_or_new_string_allows(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = {
        "session_id": "s-partial",
        "tool_name": "Edit",
        "tool_input": {"file_path": target, "new_string": "- [x] Slice 1: thing\n"},
        "cwd": str(tmp_path),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"


# ---------------------------------------------------------------------------
# AC10 — track-record append-only + schema field names exact per §7
# ---------------------------------------------------------------------------

def test_track_record_is_append_only_across_invocations(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    target = _progress_path(tmp_path)
    stdin_allow = _edit_stdin(
        target, old_string="prose only\n", new_string="prose edited\n", session_id="s-a"
    )
    stdin_deny = _edit_stdin(
        target,
        old_string="- [ ] Slice N: same wording\n- [ ] Slice N: same wording\n",
        new_string="- [x] Slice N: same wording\n",
        session_id="s-b",
    )
    _run_probe(monkeypatch, tmp_path, stdin_allow)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_deny)
    assert len(entries) == 2
    assert entries[0]["session_id"] == "s-a"
    assert entries[0]["decision"] == "allow"
    assert entries[1]["session_id"] == "s-b"
    assert entries[1]["decision"] == "deny"


def test_track_record_write_failure_does_not_change_decision(monkeypatch, tmp_path):
    _write_allowlist(tmp_path)
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target,
        old_string="- [ ] Slice N: same wording\n- [ ] Slice N: same wording\n",
        new_string="- [x] Slice N: same wording\n",
    )

    real_open = open

    def _boom_open(path, mode="r", *args, **kwargs):
        if "a" in mode:
            raise OSError("disk full")
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(probe, "open", _boom_open, raising=False)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(stdin_data)))
    buf = io.StringIO()
    with redirect_stdout(buf):
        probe.main()
    decision = _decision(buf.getvalue().strip())
    assert decision is not None and decision["decision"] == "block"
    assert not _track_record_path(tmp_path).is_file()


def test_track_record_entry_schema_field_names_exact_per_spec_section_7(monkeypatch, tmp_path):
    target = _progress_path(tmp_path)
    stdin_data = _edit_stdin(
        target, old_string="prose only\n", new_string="prose edited\n"
    )
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert set(entries[-1].keys()) == TRACK_RECORD_KEYS


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
            self._env_restores = []

        def setattr(self, obj, name, value, raising=True):
            old = getattr(obj, name, None)
            self._restores.append((obj, name, old))
            setattr(obj, name, value)

        def setenv(self, name, value):
            old = os.environ.get(name)
            self._env_restores.append((name, old))
            os.environ[name] = value

        def undo(self):
            for obj, name, old in reversed(self._restores):
                setattr(obj, name, old)
            for name, old in reversed(self._env_restores):
                if old is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = old

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
