"""Tests for scripts/domain_boundary_provenance_probe.py — Slice 1 (probe core).

Spec: docs/tooling/domain-boundary-provenance-hook.md §8 (acceptance criteria), scoped to this
slice per the forge task: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC9. AC8 (repo-diff-scope check) is
a forge-completion verification, not a probe-behavior criterion, and is intentionally not covered
here.

Loads scripts/domain_boundary_provenance_probe.py directly — the file the wrapper is documented
to execute — never a reference/ mirror (none exists for this hook yet; §6's component table lists
only scripts/ for the probe).

Exercises the real entry point, `probe.main()`, against real PreToolUse-stdin-shaped JSON and
inline-constructed manifest/content fixtures (no separate fixture corpus files exist yet — those
are Slice 3's deliverable per PROGRESS.md; this file builds the AC7-named fixture set directly, as
allowed by §6's fixture list being a *minimum set*, not a file-location requirement for Slice 1).

Runnable two ways:
    pytest tests/test_domain_boundary_provenance_probe.py
    python3 tests/test_domain_boundary_provenance_probe.py   (falls back to a plain assert-based runner)
"""

import ast
import importlib.util
import io
import json
import os
import sys
import textwrap
from contextlib import redirect_stdout

try:
    import pytest  # noqa: F401
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "domain_boundary_provenance_probe.py")


def _load_probe():
    spec = importlib.util.spec_from_file_location("domain_boundary_provenance_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()

TRACK_RECORD_KEYS = {
    "timestamp", "session_id", "tool_name", "file_path", "mode",
    "cross_domain", "local_threshold", "decision", "reason", "probe_error",
}


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

DEFAULT_GLOBS = ["docs/tooling/*.json"]
DEFAULT_IDENTIFIERS = ["EXTERNAL_CAP_V1"]


def _write_manifest(project_dir, globs=None, identifiers=None, raw=None):
    manifest_dir = project_dir / "docs" / "tooling"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    path = manifest_dir / "domain-boundary-manifest.json"
    if raw is not None:
        path.write_text(raw)
        return str(path)
    data = {
        "schemaVersion": 1,
        "pipelineConfigGlobs": globs if globs is not None else DEFAULT_GLOBS,
        "externalSourceIdentifiers": identifiers if identifiers is not None else DEFAULT_IDENTIFIERS,
    }
    path.write_text(json.dumps(data))
    return str(path)


def _write_mode_config(project_dir, mode):
    """Slice 6/7 helper: several pre-Slice-6 tests assert genuine `deny`/blocked-stdout
    behavior, which under the F1 log_only default now downgrades to `flag` (silent). Those
    tests' actual intent is exercising the deny-reason/blocking path, not mode selection, so
    they opt into `mode: "blocking"` explicitly rather than relying on the (now log_only)
    default."""
    mode_dir = project_dir / "docs" / "tooling"
    mode_dir.mkdir(parents=True, exist_ok=True)
    path = mode_dir / "domain-boundary-mode.json"
    path.write_text(json.dumps({"schemaVersion": 1, "mode": mode}))
    return str(path)


def _track_record_path(project_dir):
    return project_dir / "docs" / "tooling" / "domain-boundary-provenance-track-record.jsonl"


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
    """Invoke probe.main() the way the wrapper does: JSON on stdin, decision (if any) on
    stdout, one track-record line appended under project_dir. CLAUDE_PROJECT_DIR is the
    documented repo-root source (§6 step 3) — set it to project_dir, not derived from cwd."""
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


def _write_stdin(tool_name="Write", file_path=None, content=None, new_string=None, session_id="s1"):
    tool_input = {"file_path": file_path}
    if tool_name == "Write":
        tool_input["content"] = content
    elif tool_name == "Edit":
        tool_input["new_string"] = new_string
    return {
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": file_path,
    }


# ---------------------------------------------------------------------------
# AC1 — out-of-scope file (no glob match) -> always allow, file_in_scope: false
# ---------------------------------------------------------------------------

def test_ac1_out_of_scope_file_allows_with_file_in_scope_false(monkeypatch, tmp_path):
    """AC1 covers cross_domain's file_in_scope determination only. Since Slice 7, the
    local-threshold pass ALSO runs on every `.py` file regardless of manifest scope, and this
    fixture's `EXTERNAL_CAP_V1 = 5` is itself an unmarked module-level assignment — so the
    combined (log_only default) decision is now "flag", not "allow". This is the correct,
    designed behavior of composing the two independent passes, not a regression (see
    Architecture §3/§6/§11 and combine()'s F1 test)."""
    _write_manifest(tmp_path)
    unrelated = tmp_path / "src" / "app.py"
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    stdin_data = _write_stdin(
        file_path=str(unrelated), content="EXTERNAL_CAP_V1 = 5\n"
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["cross_domain"]["file_in_scope"] is False
    assert entries[-1]["cross_domain"]["manifest_status"] == "matched"
    assert entries[-1]["local_threshold"]["file_scanned"] is True
    assert entries[-1]["local_threshold"]["matches_found"] == 1
    assert entries[-1]["local_threshold"]["matches_cited"] == 0
    assert entries[-1]["decision"] == "flag"


# ---------------------------------------------------------------------------
# AC2 — no manifest present -> always allow, manifest_status: absent_or_invalid
# ---------------------------------------------------------------------------

def test_ac2_no_manifest_present_allows_with_manifest_status_absent(monkeypatch, tmp_path):
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    stdin_data = _write_stdin(file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["manifest_status"] == "absent_or_invalid"


# ---------------------------------------------------------------------------
# AC3 — in-scope match with a qualifying DOMAIN-BOUNDARY marker -> allow
# ---------------------------------------------------------------------------

def test_ac3_cited_match_is_allowed(monkeypatch, tmp_path):
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = (
        "# DOMAIN-BOUNDARY: sourced from market_data's daily_universe view, see DDR-0014\n"
        "EXTERNAL_CAP_V1 = 5\n"
    )
    stdin_data = _write_stdin(file_path=str(target), content=content)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["file_in_scope"] is True
    assert entries[-1]["cross_domain"]["matches_found"] == 1
    assert entries[-1]["cross_domain"]["matches_cited"] == 1


# ---------------------------------------------------------------------------
# AC4 — in-scope match with no qualifying marker -> deny naming file/identifier/remediation
# ---------------------------------------------------------------------------

def test_ac4_uncited_match_is_denied_naming_file_identifier_and_remediation(monkeypatch, tmp_path):
    """Since Slice 6/7, an unconditional deny only happens under mode == "blocking" (log_only
    downgrades to a silent "flag" — the F1 behavior change). This test's actual intent is
    exercising the deny-reason content, so it opts into blocking mode explicitly."""
    _write_manifest(tmp_path)
    _write_mode_config(tmp_path, "blocking")
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = "EXTERNAL_CAP_V1 = 5\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert "docs/tooling/pipeline.json" in decision["reason"]
    assert "EXTERNAL_CAP_V1" in decision["reason"]
    assert "DOMAIN-BOUNDARY:" in decision["reason"]
    assert entries[-1]["decision"] == "deny"
    assert entries[-1]["cross_domain"]["matches_found"] == 1
    assert entries[-1]["cross_domain"]["matches_cited"] == 0


# ---------------------------------------------------------------------------
# AC5 — fail-open: probe crash and malformed manifest both always allow
# ---------------------------------------------------------------------------

def test_ac5_malformed_manifest_json_allows(monkeypatch, tmp_path):
    _write_manifest(tmp_path, raw="{not valid json")
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["manifest_status"] == "absent_or_invalid"


def test_ac5_manifest_failing_schema_validation_allows(monkeypatch, tmp_path):
    # schemaVersion wrong + identifiers wrong type -> validate_manifest_shape() rejects it.
    _write_manifest(tmp_path, raw=json.dumps({
        "schemaVersion": 2,
        "pipelineConfigGlobs": ["docs/tooling/*.json"],
        "externalSourceIdentifiers": "not-a-list",
    }))
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["manifest_status"] == "absent_or_invalid"


def test_ac5_probe_crash_allows_and_records_probe_error(monkeypatch, tmp_path):
    """§6/§8 AC5: an unexpected exception inside run() must never surface as a block —
    main()'s own try/except is the probe's inner fail-open guarantee, fault-injected here by
    monkeypatching a real function run() calls, exercising the actual except path."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n")

    def _boom(*args, **kwargs):
        raise RuntimeError("injected fault")

    monkeypatch.setattr(probe, "load_manifest", _boom)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "probe_error"
    assert isinstance(entries[-1]["probe_error"], str) and "RuntimeError" in entries[-1]["probe_error"]
    assert "injected fault" in entries[-1]["probe_error"]


# ---------------------------------------------------------------------------
# AC6 — track record is append-only and write-failure-tolerant
# ---------------------------------------------------------------------------

def test_ac6_track_record_is_append_only_across_invocations(monkeypatch, tmp_path):
    """Opts into blocking mode (see test_ac4's note) so the second invocation's fixture still
    produces a genuine "deny" entry, preserving this test's actual intent (append-only across
    invocations), independent of the log_only-vs-blocking mode question."""
    _write_manifest(tmp_path)
    _write_mode_config(tmp_path, "blocking")
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data_allow = _write_stdin(
        file_path=str(target), content="nothing interesting here\n", session_id="s-a"
    )
    stdin_data_deny = _write_stdin(
        file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n", session_id="s-b"
    )
    _run_probe(monkeypatch, tmp_path, stdin_data_allow)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data_deny)
    assert len(entries) == 2
    assert entries[0]["session_id"] == "s-a"
    assert entries[0]["decision"] == "allow"
    assert entries[1]["session_id"] == "s-b"
    assert entries[1]["decision"] == "deny"


def test_ac6_track_record_write_failure_does_not_change_decision(monkeypatch, tmp_path):
    """A write_track_record() failure (e.g. permission error, disk full) must not alter the
    already-computed allow/deny decision emitted to Claude Code — the log is an audit trail,
    not a gate, per write_track_record()'s own docstring. Opts into blocking mode (see
    test_ac4's note) so this fixture still produces a genuine "deny" to prove the point."""
    _write_manifest(tmp_path)
    _write_mode_config(tmp_path, "blocking")
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="EXTERNAL_CAP_V1 = 5\n")

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
    # And the track record file must not exist / must not have crashed the probe.
    assert not _track_record_path(tmp_path).is_file()


# ---------------------------------------------------------------------------
# Slice 2 — load_mode_config (fail-safe mode config loader, §5)
# ---------------------------------------------------------------------------

def test_mode_config_absent_file_defaults_to_log_only(tmp_path):
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_malformed_json_defaults_to_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text("{not valid json")
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_missing_mode_key_defaults_to_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"schemaVersion": 1}))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_invalid_mode_value_defaults_to_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"schemaVersion": 1, "mode": "strict"}))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_valid_blocking_returns_blocking(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"schemaVersion": 1, "mode": "blocking"}))
    assert probe.load_mode_config(str(tmp_path)) == "blocking"


def test_mode_config_valid_json_non_dict_defaults_to_log_only(tmp_path):
    """Independent gap: valid JSON that parses to a non-dict (e.g. a bare list) must not reach
    data.get("mode") — the isinstance(data, dict) guard (line 138) is exercised by none of the
    other five cases, which all pass a dict (or fail parsing entirely)."""
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps(["blocking"]))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_valid_log_only_returns_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"schemaVersion": 1, "mode": "log_only"}))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_wrong_schema_version_defaults_to_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"schemaVersion": 99, "mode": "blocking"}))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


def test_mode_config_missing_schema_version_defaults_to_log_only(tmp_path):
    mode_path = tmp_path / "docs" / "tooling" / "domain-boundary-mode.json"
    mode_path.parent.mkdir(parents=True, exist_ok=True)
    mode_path.write_text(json.dumps({"mode": "blocking"}))
    assert probe.load_mode_config(str(tmp_path)) == "log_only"


# ---------------------------------------------------------------------------
# AC7 — self-test fixture set (minimum named cases)
# ---------------------------------------------------------------------------

def test_ac7_in_scope_no_match_allows(monkeypatch, tmp_path):
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="totally unrelated content\n")
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["file_in_scope"] is True
    assert entries[-1]["cross_domain"]["matches_found"] == 0


def test_ac7_marker_just_outside_window_denies(monkeypatch, tmp_path):
    """§5 PROXIMITY_WINDOW = 5 (inclusive). A marker at exactly line 7 relative to a match on
    line 1 (index 0) is 6 lines away — outside the window — and must deny. Opts into blocking
    mode (see test_ac4's note) so the window-boundary miss still surfaces as a genuine deny."""
    _write_manifest(tmp_path)
    _write_mode_config(tmp_path, "blocking")
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    filler = "\n".join(f"filler line {i}" for i in range(1, 6))  # 5 filler lines
    content = "EXTERNAL_CAP_V1 = 5\n" + filler + "\n# DOMAIN-BOUNDARY: too far away\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["decision"] == "deny"


def test_ac7_marker_at_window_boundary_line_5_allows(monkeypatch, tmp_path):
    """Positive control for the boundary case above: a marker exactly 5 lines away (inclusive
    edge of PROXIMITY_WINDOW) must still qualify."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    filler = "\n".join(f"filler line {i}" for i in range(1, 4))  # 4 filler lines
    content = "EXTERNAL_CAP_V1 = 5\n" + filler + "\n# DOMAIN-BOUNDARY: within window\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"


def test_ac7_pre_existing_uncited_match_unrelated_edit_not_denied(monkeypatch, tmp_path):
    """§6 step 4's scan-surface scope: an Edit whose new_string never touches the line
    carrying a pre-existing, uncited externalSourceIdentifiers match elsewhere in the file must
    not be denied — the probe never inspects old_string or the on-disk file, only new_string."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(
        tool_name="Edit",
        file_path=str(target),
        new_string="totally unrelated replacement text, no identifiers here\n",
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["matches_found"] == 0


def test_ac7_absolute_path_matches_relative_glob(monkeypatch, tmp_path):
    """§6 step 3 / §8 AC7's most load-bearing pair (1/2): a manifest glob written relative to
    repo root (docs/tooling/*.json) must match a realistic, non-relativized ABSOLUTE
    tool_input.file_path — the real envelope shape, per §7's live-verified capture."""
    _write_manifest(tmp_path)
    _write_mode_config(tmp_path, "blocking")
    absolute_target = tmp_path / "docs" / "tooling" / "foo.json"
    stdin_data = _write_stdin(
        file_path=str(absolute_target), content="EXTERNAL_CAP_V1 = 5\n"
    )
    assert os.path.isabs(stdin_data["tool_input"]["file_path"])
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["cross_domain"]["file_in_scope"] is True


def test_ac7_absolute_path_outside_project_dir_allows(monkeypatch, tmp_path):
    """§6 step 3 / §8 AC7's most load-bearing pair (2/2): the fail-open edge case — an
    absolute tool_input.file_path resolving outside $CLAUDE_PROJECT_DIR entirely must allow
    with file_in_scope: false, without ever attempting a glob match."""
    _write_manifest(tmp_path)
    outside_dir = tmp_path.parent / "outside_project"
    outside_dir.mkdir(exist_ok=True)
    outside_target = outside_dir / "docs" / "tooling" / "foo.json"
    outside_target.parent.mkdir(parents=True, exist_ok=True)
    stdin_data = _write_stdin(
        file_path=str(outside_target), content="EXTERNAL_CAP_V1 = 5\n"
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["cross_domain"]["file_in_scope"] is False


# ---------------------------------------------------------------------------
# AC9 — PROVISIONAL markers preserved as-authored (spec §5/§6 constants)
# ---------------------------------------------------------------------------

def test_ac9_proximity_window_and_marker_string_match_spec_provisional_values(monkeypatch, tmp_path):
    """§8 AC9: this sprint's PROVISIONAL constants (§5's 5-line window) must ship exactly as
    the spec states them — a silent drift here would ship an unmarked, unreviewed change to a
    value the spec explicitly flags as owner-revisable, not free-floating."""
    assert probe.PROXIMITY_WINDOW == 5
    assert probe.MARKER == "DOMAIN-BOUNDARY:"


# ---------------------------------------------------------------------------
# Non-Edit/Write tool -> allow unconditionally (§6 step 1)
# ---------------------------------------------------------------------------

def test_non_edit_write_tool_allows_unconditionally(monkeypatch, tmp_path):
    _write_manifest(tmp_path)
    stdin_data = {
        "session_id": "s-read",
        "tool_name": "Read",
        "tool_input": {"file_path": str(tmp_path / "docs" / "tooling" / "pipeline.json")},
        "cwd": str(tmp_path),
    }
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"


# ---------------------------------------------------------------------------
# Slice 1 — direct unit tests for run_cross_domain_pass()'s PassResult
# ---------------------------------------------------------------------------

def test_cross_domain_pass_no_manifest_returns_ran_false(tmp_path):
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    result = probe.run_cross_domain_pass(
        str(tmp_path), {"file_path": str(target)}, "EXTERNAL_CAP_V1 = 5\n"
    )
    assert result["ran"] is False
    assert result["matches_found"] is None
    assert result["matches_cited"] is None
    assert result["unmarked"] == []
    assert result["detail"]["manifest_status"] == "absent_or_invalid"


def test_cross_domain_pass_out_of_scope_file_returns_ran_false(tmp_path):
    _write_manifest(tmp_path)
    unrelated = tmp_path / "src" / "app.py"
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    result = probe.run_cross_domain_pass(
        str(tmp_path), {"file_path": str(unrelated)}, "EXTERNAL_CAP_V1 = 5\n"
    )
    assert result["ran"] is False
    assert result["matches_found"] is None
    assert result["matches_cited"] is None
    assert result["unmarked"] == []
    assert result["detail"]["manifest_status"] == "matched"
    assert result["detail"]["file_in_scope"] is False


def test_cross_domain_pass_in_scope_no_identifier_match(tmp_path):
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    result = probe.run_cross_domain_pass(
        str(tmp_path), {"file_path": str(target)}, "totally unrelated content\n"
    )
    assert result["ran"] is True
    assert result["matches_found"] == 0
    assert result["matches_cited"] == 0
    assert result["unmarked"] == []
    assert result["detail"]["file_in_scope"] is True


def test_cross_domain_pass_match_with_citation(tmp_path):
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = (
        "# DOMAIN-BOUNDARY: sourced from market_data's daily_universe view, see DDR-0014\n"
        "EXTERNAL_CAP_V1 = 5\n"
    )
    result = probe.run_cross_domain_pass(str(tmp_path), {"file_path": str(target)}, content)
    assert result["ran"] is True
    assert result["matches_found"] == 1
    assert result["matches_cited"] == 1
    assert result["unmarked"] == []


def test_cross_domain_pass_match_with_no_citation(tmp_path):
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = "EXTERNAL_CAP_V1 = 5\n"
    result = probe.run_cross_domain_pass(str(tmp_path), {"file_path": str(target)}, content)
    assert result["ran"] is True
    assert result["matches_found"] == 1
    assert result["matches_cited"] == 0
    assert len(result["unmarked"]) == 1
    assert result["unmarked"][0][1] == "EXTERNAL_CAP_V1"


# ---------------------------------------------------------------------------
# Slice 3 — detect_threshold_literals()
# ---------------------------------------------------------------------------
# Spec: docs/specs/domain-boundary-provenance-hook/04-ROADMAP.md "### Slice 3", Architecture
# §2/§2.1/§7. Three syntactic contexts (comparison, slice_truncation,
# assign_module_or_class), no vocabulary/case gate on context 3, no literal-value
# exclusion set ({0,1,-1,2} removed 2026-09-05), a 3-strategy fragment-robust parse chain
# for context 3 (ast.parse -> dedent retry -> per-line regex fallback).


def test_context1_comparison_operand_flagged():
    flags = probe.detect_threshold_literals("app.py", "if retries > 3:\n    pass\n")
    assert [f for f in flags if f["context"] == "comparison" and f["literal_repr"] == "3"]


def test_context2_slice_truncation_flagged():
    flags = probe.detect_threshold_literals("app.py", "x = data[:50000]\n")
    assert [
        f for f in flags if f["context"] == "slice_truncation" and f["literal_repr"] == "50000"
    ]


def test_context3_module_level_assignment_flagged():
    flags = probe.detect_threshold_literals("app.py", "MAX_RETRIES = 500\n")
    assert [
        f
        for f in flags
        if f["context"] == "assign_module_or_class" and f["literal_repr"] == "500"
    ]


def test_context3_class_level_assignment_flagged():
    source = "class Config:\n    filing_text_max_bytes: int = 512_000\n"
    flags = probe.detect_threshold_literals("app.py", source)
    assert [
        f
        for f in flags
        if f["context"] == "assign_module_or_class" and f["literal_repr"] == "512000"
    ]


def test_non_slice_stop_index_not_flagged():
    flags = probe.detect_threshold_literals("app.py", "x = data[i]\n")
    assert flags == []


def test_slice_stop_is_flagged():
    flags = probe.detect_threshold_literals("app.py", "x = data[:50000]\n")
    assert any(f["literal_repr"] == "50000" for f in flags)


def test_small_idiomatic_literals_are_flagged_no_exclusion():
    # 2026-09-05: {0,1,-1,2} exclusion REMOVED — these must now be flagged like any other
    # threshold-shaped literal, direction-reversed from the prior draft.
    source = "\n".join(
        [
            "if retries > 0:",
            "    pass",
            "y = data[:1]",
            "class C:",
            "    FLAG = -1",
            "    OTHER = 2",
        ]
    )
    flags = probe.detect_threshold_literals("app.py", source)
    literal_reprs = {f["literal_repr"] for f in flags}
    assert {"0", "1", "-1", "2"} <= literal_reprs


def test_test_path_component_produces_no_flags():
    for path in ("tests/foo.py", "src/test/bar.py", "fixtures/baz.py"):
        flags = probe.detect_threshold_literals(path, "MAX_RETRIES = 500\n")
        assert flags == [], path


def test_lowercase_module_level_assignment_flagged_context_assign():
    flags = probe.detect_threshold_literals("app.py", "filing_text_max_bytes = 512_000\n")
    assert any(
        f["context"] == "assign_module_or_class" and f["literal_repr"] == "512000"
        for f in flags
    )


def test_no_import_graph_check_in_detect_threshold_literals():
    # Structural test (G-4-adjacent): no domain-crossing/import-graph check exists in this
    # function — grep the source for import-related AST node types; none gate a decision.
    import inspect

    source_text = inspect.getsource(probe.detect_threshold_literals)
    source_text += inspect.getsource(probe._walk_comparison_and_slice_contexts)
    source_text += inspect.getsource(probe._walk_assignment_context)
    source_text += inspect.getsource(probe._regex_fallback_assignment_context)
    for forbidden in ("ast.Import", "ast.ImportFrom", "import_graph", "ImportFrom"):
        assert forbidden not in source_text


def test_syntax_error_input_unrecoverable_returns_empty_list():
    # A fragment that fails all three parse strategies (no assignment-shaped line for the
    # regex fallback to recover) must return [] rather than raise.
    source = "def foo(:\n    this is not python at all *&^%\n"
    flags = probe.detect_threshold_literals("app.py", source)
    assert flags == []


def test_fragment_robustness_indented_class_body_recovers_via_dedent_or_regex():
    # I2's real shape: an indented class-body line, no enclosing `class Foo:` in the
    # fragment — raises IndentationError under a bare ast.parse.
    source = "    filing_text_max_bytes: int = 512_000\n"
    flags = probe.detect_threshold_literals("app.py", source)
    assert any(
        f["context"] == "assign_module_or_class" and f["literal_repr"] == "512000"
        for f in flags
    )


def test_fragment_robustness_module_level_single_line_flagged_via_strategy1():
    # I1's shape: a bare module-level assignment fragment, valid standalone at column 0 —
    # recovered by strategy 1 (plain ast.parse), unchanged.
    source = "_HEAD_BYTES = 65_536\n"
    flags = probe.detect_threshold_literals("app.py", source)
    assert any(
        f["context"] == "assign_module_or_class" and f["literal_repr"] == "65536"
        for f in flags
    )


def test_fragment_regex_fallback_widened_for_float_literal():
    # A fragment shaped so all three ast strategies fail to parse it as-is but that IS a
    # bare top-level assignment line — still recoverable via strategy 1 directly since a
    # single well-formed top-level float assignment already parses. Exercise the regex
    # fallback function directly for the float-widening fix (Architecture §2.1).
    flags = probe._regex_fallback_assignment_context("    dilution_pct_min: float = 0.10\n")
    assert flags == [(0, "assign_module_or_class", "0.1")]


def test_fragment_robustness_strategy3_regex_fallback_exercised_end_to_end():
    # Distinct-path regression: strategy 1 (plain ast.parse) fails with IndentationError
    # (indented first line); strategy 2 (dedent retry) also fails, because after dedent
    # the second line is still genuinely invalid syntax (not merely a leftover indent
    # problem) — so only strategy 3 (per-line regex fallback) can recover the assignment.
    # This exercises the fallback through the real `detect_threshold_literals` entry
    # point, not by calling the private regex helper directly (which strategy-1/2 tests
    # already do implicitly and would falsely appear to "cover" strategy 3 otherwise).
    source = "    MAX_ITEMS = 999\n    def broken(:\n"
    # Sanity: confirm strategy 1 and strategy 2 really do fail on this fragment, so the
    # only way a flag can appear is via strategy 3.
    try:
        ast.parse(source)
        assert False, "expected strategy 1 to fail on this fragment"
    except IndentationError:
        pass
    try:
        ast.parse(textwrap.dedent(source))
        assert False, "expected strategy 2 (dedent) to also fail on this fragment"
    except SyntaxError:
        pass

    flags = probe.detect_threshold_literals("app.py", source)
    assert any(
        f["context"] == "assign_module_or_class" and f["literal_repr"] == "999"
        for f in flags
    )


# ---------------------------------------------------------------------------
# Slice 4: has_threshold_provenance_marker()
# ---------------------------------------------------------------------------

def test_threshold_marker_same_line_with_citation_satisfies():
    lines = ["FOO = 5  # THRESHOLD-PROVENANCE: docs/research/x/results.md §5"]
    assert probe.has_threshold_provenance_marker(lines, 0) is True


def test_threshold_marker_same_line_with_owner_satisfies():
    lines = ["FOO = 5  # THRESHOLD-PROVENANCE: PROVISIONAL — owner: wright"]
    assert probe.has_threshold_provenance_marker(lines, 0) is True


def test_threshold_marker_two_lines_above_with_citation_satisfies():
    lines = [
        "# THRESHOLD-PROVENANCE: DDR-0014",
        "",
        "FOO = 5",
    ]
    assert probe.has_threshold_provenance_marker(lines, 2) is True


def test_threshold_marker_three_lines_away_does_not_satisfy():
    lines = [
        "# THRESHOLD-PROVENANCE: DDR-0014",
        "",
        "",
        "FOO = 5",
    ]
    assert probe.has_threshold_provenance_marker(lines, 3) is False


def test_threshold_marker_two_lines_below_with_citation_satisfies():
    """Window-boundary gap: the existing exact-2/exact-3 tests only exercise the marker
    positioned ABOVE the literal. The window is computed symmetrically (`match_line_idx -
    PROXIMITY_WINDOW_THRESHOLD` .. `match_line_idx + PROXIMITY_WINDOW_THRESHOLD`) — confirm
    the below direction independently rather than assuming symmetry from the above-only
    tests."""
    lines = [
        "FOO = 5",
        "",
        "# THRESHOLD-PROVENANCE: DDR-0014",
    ]
    assert probe.has_threshold_provenance_marker(lines, 0) is True


def test_threshold_marker_three_lines_below_does_not_satisfy():
    lines = [
        "FOO = 5",
        "",
        "",
        "# THRESHOLD-PROVENANCE: DDR-0014",
    ]
    assert probe.has_threshold_provenance_marker(lines, 0) is False


def test_threshold_marker_no_trailing_content_does_not_satisfy():
    lines = ["# THRESHOLD-PROVENANCE:", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is False


def test_threshold_marker_bare_provisional_does_not_satisfy():
    lines = ["# THRESHOLD-PROVENANCE: PROVISIONAL", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is False


def test_threshold_marker_bare_todo_does_not_satisfy():
    lines = ["# THRESHOLD-PROVENANCE: TODO", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is False


def test_threshold_marker_placeholder_owner_todo_does_not_satisfy():
    lines = ["# THRESHOLD-PROVENANCE: PROVISIONAL — owner: TODO", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is False


def test_threshold_marker_placeholder_owner_all_blocklist_tokens_do_not_satisfy():
    """Independent-review gap: the prior suite only exercised TODO as a placeholder owner
    value. A regex-based blocklist can silently miss a token if only one or two examples
    are tested — probe each of the seven documented placeholders individually
    (Architecture §4 / roadmap Slice 4)."""
    for placeholder in ("TODO", "TBD", "unassigned", "unknown", "none", "self", "N/A"):
        lines = [f"# THRESHOLD-PROVENANCE: PROVISIONAL — owner: {placeholder}", "FOO = 5"]
        assert probe.has_threshold_provenance_marker(lines, 1) is False, placeholder


def test_threshold_marker_placeholder_owner_case_insensitive_do_not_satisfy():
    """The blocklist check is documented as case-insensitive — confirm mixed-case
    placeholder tokens (not just the exact-case forms already tested) are still caught."""
    for placeholder in ("Todo", "tbd", "UNASSIGNED", "Unknown", "NONE", "SELF", "n/a"):
        lines = [f"# THRESHOLD-PROVENANCE: PROVISIONAL — owner: {placeholder}", "FOO = 5"]
        assert probe.has_threshold_provenance_marker(lines, 1) is False, placeholder


def test_threshold_marker_real_owner_name_satisfies():
    lines = ["# THRESHOLD-PROVENANCE: PROVISIONAL — owner: wright", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is True


def test_domain_boundary_marker_or_bare_provisional_does_not_satisfy_threshold_check():
    lines = ["# DOMAIN-BOUNDARY: docs/foo.md", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines, 1) is False
    lines2 = ["# PROVISIONAL", "FOO = 5"]
    assert probe.has_threshold_provenance_marker(lines2, 1) is False


def test_incumbent_proximity_window_constant_flagged_on_self_scan():
    """PROXIMITY_WINDOW = 5 (the incumbent's own existing assignment, unmodified and
    uncommented by this sprint) IS flagged by the local-threshold pass when this probe
    file is scanned, with `unmarked` populated and `context: "assign_module_or_class"` —
    self-scan regression confirming restored assignment-detection behavior."""
    probe_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "domain_boundary_provenance_probe.py",
    )
    with open(probe_path, "r") as fh:
        source = fh.read()
    lines = source.split("\n")
    flags = probe.detect_threshold_literals(probe_path, source)
    incumbent_flag = next(
        f
        for f in flags
        if f["context"] == "assign_module_or_class" and f["literal_repr"] == "5"
        and "PROXIMITY_WINDOW" in lines[f["line_index"]]
        and "PROXIMITY_WINDOW_THRESHOLD" not in lines[f["line_index"]]
    )
    assert probe.has_threshold_provenance_marker(lines, incumbent_flag["line_index"]) is False


def test_new_threshold_window_constant_not_flagged_as_unmarked_on_self_scan():
    """PROXIMITY_WINDOW_THRESHOLD = 2 (this slice's own new constant) is NOT flagged as
    unmarked — its accompanying THRESHOLD-PROVENANCE: citation comment satisfies the check
    within the 2-line window."""
    probe_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts",
        "domain_boundary_provenance_probe.py",
    )
    with open(probe_path, "r") as fh:
        source = fh.read()
    lines = source.split("\n")
    flags = probe.detect_threshold_literals(probe_path, source)
    new_flag = next(
        f
        for f in flags
        if f["context"] == "assign_module_or_class" and f["literal_repr"] == "2"
        and "PROXIMITY_WINDOW_THRESHOLD" in lines[f["line_index"]]
    )
    assert probe.has_threshold_provenance_marker(lines, new_flag["line_index"]) is True


# ---------------------------------------------------------------------------
# Slice 5: run_local_threshold_pass()
# ---------------------------------------------------------------------------

def test_run_local_threshold_pass_non_py_file_does_not_run():
    result = probe.run_local_threshold_pass("Write", "app.txt", "if retries > 3:\n", "log_only")
    assert result["ran"] is False
    assert result["matches_found"] is None
    assert result["matches_cited"] is None
    assert result["unmarked"] == []
    assert result["detail"]["file_scanned"] is False


def test_run_local_threshold_pass_test_path_excluded():
    result = probe.run_local_threshold_pass(
        "Write", "tests/fixtures/app.py", "if retries > 3:\n", "log_only"
    )
    assert result["ran"] is False
    assert result["detail"]["file_scanned"] is False


def test_run_local_threshold_pass_unmarked_literal_flagged():
    result = probe.run_local_threshold_pass(
        "Write", "app.py", "MAX_RETRIES = 500\n", "log_only"
    )
    assert result["ran"] is True
    assert result["matches_found"] == 1
    assert result["matches_cited"] == 0
    assert len(result["unmarked"]) == 1
    assert result["unmarked"][0][1] == "500"
    assert result["detail"]["file_scanned"] is True


def test_run_local_threshold_pass_marked_literal_cited():
    source = "MAX_RETRIES = 500  # THRESHOLD-PROVENANCE: docs/foo.md\n"
    result = probe.run_local_threshold_pass("Write", "app.py", source, "log_only")
    assert result["ran"] is True
    assert result["matches_found"] == 1
    assert result["matches_cited"] == 1
    assert result["unmarked"] == []


def test_run_local_threshold_pass_no_manifest_coupling(tmp_path):
    # No domain-boundary-manifest.json anywhere near the fixture — this pass must not
    # consult one, and its output must be identical whether or not one exists.
    manifest_path = tmp_path / "domain-boundary-manifest.json"
    assert not manifest_path.exists()
    result = probe.run_local_threshold_pass(
        "Write", "app.py", "MAX_RETRIES = 500\n", "log_only"
    )
    assert result["ran"] is True
    assert result["matches_found"] == 1
    assert not manifest_path.exists()


def test_run_local_threshold_pass_manifest_present_produces_identical_result(tmp_path, monkeypatch):
    """Independent-review gap: the sibling test above only proves the ABSENT-manifest case.
    "No manifest coupling" (Architecture §3) is a claim about identical behavior regardless
    of manifest presence — this complements it by writing a real, well-formed
    domain-boundary-manifest.json into a CLAUDE_PROJECT_DIR and confirming
    run_local_threshold_pass's output for the same inputs is byte-identical either way. The
    function takes no project_dir argument and never reads CLAUDE_PROJECT_DIR itself, but we
    set it anyway to simulate the realistic caller environment (run()/main() do read it for
    other passes) and confirm this pass is genuinely blind to it."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    _write_manifest(tmp_path)
    assert (tmp_path / "docs" / "tooling" / "domain-boundary-manifest.json").is_file()
    result = probe.run_local_threshold_pass(
        "Write", "app.py", "MAX_RETRIES = 500\n", "log_only"
    )
    assert result == {
        "ran": True,
        "matches_found": 1,
        "matches_cited": 0,
        "unmarked": [(0, "500")],
        "detail": {"file_scanned": True, "file_path": "app.py"},
    }


def test_run_local_threshold_pass_mode_parameter_does_not_affect_output():
    """Architecture §3 forbids the mode-based deny->flag downgrade from happening inside this
    function — it belongs solely in combine() (Slice 6). Confirm `mode` is a true no-op here:
    identical scan_surface with mode="log_only" vs mode="blocking" (and an arbitrary
    unrecognized value) must produce byte-identical PassResults."""
    source = "MAX_RETRIES = 500\n"
    result_log_only = probe.run_local_threshold_pass("Write", "app.py", source, "log_only")
    result_blocking = probe.run_local_threshold_pass("Write", "app.py", source, "blocking")
    result_other = probe.run_local_threshold_pass("Write", "app.py", source, "not-a-real-mode")
    assert result_log_only == result_blocking == result_other


# ---------------------------------------------------------------------------
# Slice 6 — combine()
# ---------------------------------------------------------------------------
# Spec: docs/specs/domain-boundary-provenance-hook/04-ROADMAP.md "### Slice 6", Architecture
# §3/§5/§6/§7. mode-gated single-decision combination of the two passes.

_ALLOW_PASS = {
    "ran": True,
    "matches_found": 0,
    "matches_cited": 0,
    "unmarked": [],
    "detail": {"relative_path": "app.py", "file_path": "app.py"},
}


def _denying_pass(unmarked, path="app.py"):
    return {
        "ran": True,
        "matches_found": len(unmarked),
        "matches_cited": 0,
        "unmarked": unmarked,
        "detail": {"relative_path": path, "file_path": path},
    }


def test_both_passes_allow_regardless_of_mode():
    for mode in ("log_only", "blocking"):
        result = probe.combine(_ALLOW_PASS, _ALLOW_PASS, mode)
        assert result["decision"] == "allow"
        assert result["reason"] is None


def test_cross_domain_pass_flag_under_log_only(tmp_path):
    """Named test F1 (Frank spec-gate attempt 1, required). A fixture that would deny under
    the incumbent's unmodified cross-domain logic (an unmarked in-scope manifest match, the
    exact LOCKED-doc §6 step 6 / AC4 scenario) resolves to combined decision "flag", not
    "deny", when mode == "log_only". This is the direct regression test for the LOCKED-doc
    behavior-change note in Architecture §3/§6/§11."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = "EXTERNAL_CAP_V1 = 5\n"
    cross_domain_result = probe.run_cross_domain_pass(
        str(tmp_path), {"file_path": str(target)}, content
    )
    # Sanity: this fixture really would deny under the incumbent's unconditional logic.
    assert cross_domain_result["unmarked"] != []

    local_threshold_result = probe.run_local_threshold_pass(
        "Write", str(target), content, "log_only"
    )

    combined = probe.combine(cross_domain_result, local_threshold_result, "log_only")
    assert combined["decision"] == "flag"
    assert combined["reason"] is None


def test_cross_domain_pass_denies_under_blocking_same_fixture(tmp_path):
    """Companion to F1: proves the F1 fixture is a genuine mode-dependent behavior change,
    not just an assertion of "flag" on something that was never going to deny. Same fixture
    as test_cross_domain_pass_flag_under_log_only, run through combine() under
    mode="blocking" instead — must resolve to "deny", confirming the log_only case above
    really did downgrade a real deny, not merely restate an allow."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    content = "EXTERNAL_CAP_V1 = 5\n"
    cross_domain_result = probe.run_cross_domain_pass(
        str(tmp_path), {"file_path": str(target)}, content
    )
    local_threshold_result = probe.run_local_threshold_pass(
        "Write", str(target), content, "blocking"
    )
    combined = probe.combine(cross_domain_result, local_threshold_result, "blocking")
    assert combined["decision"] == "deny"
    assert "[domain-boundary]" in combined["reason"]


def test_local_threshold_pass_flags_under_log_only():
    unmarked_local = _denying_pass([(0, "500")])
    combined = probe.combine(_ALLOW_PASS, unmarked_local, "log_only")
    assert combined["decision"] == "flag"
    assert combined["reason"] is None


def test_blocking_cross_domain_denies_alone():
    unmarked_cross = _denying_pass([(0, "EXTERNAL_CAP_V1")])
    combined = probe.combine(unmarked_cross, _ALLOW_PASS, "blocking")
    assert combined["decision"] == "deny"
    assert "[domain-boundary]" in combined["reason"]
    assert "[threshold-provenance]" not in combined["reason"]


def test_blocking_local_threshold_denies_alone():
    unmarked_local = _denying_pass([(0, "500")])
    combined = probe.combine(_ALLOW_PASS, unmarked_local, "blocking")
    assert combined["decision"] == "deny"
    assert "[threshold-provenance]" in combined["reason"]
    assert "[domain-boundary]" not in combined["reason"]


def test_blocking_both_passes_deny_reason_concatenates_both_labeled():
    unmarked_cross = _denying_pass([(0, "EXTERNAL_CAP_V1")])
    unmarked_local = _denying_pass([(1, "500")])
    combined = probe.combine(unmarked_cross, unmarked_local, "blocking")
    assert combined["decision"] == "deny"
    assert "[domain-boundary]" in combined["reason"]
    assert "[threshold-provenance]" in combined["reason"]
    assert "EXTERNAL_CAP_V1" in combined["reason"]
    assert "500" in combined["reason"]


def test_combine_constructs_at_most_one_deny_payload_structural():
    """Done-When structural check: no code path in combine() allows more than one deny
    payload to be constructed for emission. Verified two ways: (1) combine() always returns
    exactly one CombinedResult dict — a single object, never a list/tuple of payloads or a
    second call-site; (2) the source of combine() contains exactly one literal construction
    of a "deny" decision (one `return {"decision": "deny", ...}` site), so there is no
    duplicate/parallel deny-payload builder to drift out of sync with it."""
    import inspect

    result = probe.combine(
        _denying_pass([(0, "X")]), _denying_pass([(1, "Y")]), "blocking"
    )
    assert isinstance(result, dict)
    assert set(result.keys()) == {"decision", "reason"}

    source_text = inspect.getsource(probe.combine)
    assert source_text.count('"decision": "deny"') == 1
    assert source_text.count('"decision": "flag"') == 1
    assert source_text.count('"decision": "allow"') == 1


# ---------------------------------------------------------------------------
# Slice 7 — restructured run(): single write_track_record, both passes always run,
# nested cross_domain/local_threshold track-record shape (Architecture §6).
# ---------------------------------------------------------------------------

def test_run_writes_track_record_exactly_once_per_invocation(monkeypatch, tmp_path):
    """Objective 3: the whole point of the run() restructure — one write_track_record()
    call per invocation, not one per pass."""
    _write_manifest(tmp_path)
    target = tmp_path / "docs" / "tooling" / "pipeline.json"
    stdin_data = _write_stdin(file_path=str(target), content="MAX_RETRIES = 500\n")

    calls = []
    real_write = probe.write_track_record

    def _counting_write(project_dir, entry):
        calls.append(entry)
        return real_write(project_dir, entry)

    monkeypatch.setattr(probe, "write_track_record", _counting_write)
    _run_probe(monkeypatch, tmp_path, stdin_data)
    assert len(calls) == 1


def test_run_entry_has_nested_cross_domain_and_local_threshold_and_mode(monkeypatch, tmp_path):
    """Objective 5 / Architecture §6: a fixture that trips BOTH passes (an in-scope,
    uncited manifest identifier AND an uncited threshold literal in the same content)
    produces a single track-record entry with both nested sub-dicts populated and a
    top-level mode field, per the restructured build_track_record_entry() shape.

    Target file is `.py` (the local-threshold pass is `.py`-only by design) and the manifest
    glob is widened to match `.py` so the cross-domain pass can also fire on the same file.
    The cross-domain identifier appears in a comment rather than an assignment so it isn't
    ALSO picked up as a module-level-assignment threshold literal by the local-threshold
    pass — keeping each pass's matches_found at exactly 1, as originally intended."""
    _write_manifest(tmp_path, globs=["docs/tooling/*.py"])
    target = tmp_path / "docs" / "tooling" / "pipeline.py"
    content = "# note: EXTERNAL_CAP_V1 legacy behavior\nMAX_RETRIES = 500\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert entry["mode"] == "log_only"
    assert entry["cross_domain"]["matches_found"] == 1
    assert entry["cross_domain"]["matches_cited"] == 0
    assert entry["local_threshold"]["matches_found"] == 1
    assert entry["local_threshold"]["matches_cited"] == 0
    assert entry["decision"] == "flag"


def test_run_only_cross_domain_pass_trips(monkeypatch, tmp_path):
    """Objective 5: only the cross-domain pass finds an unmarked match; the
    local-threshold pass runs (file_scanned: True) but finds nothing to flag.

    Target file must be `.py` (Category B fix): the local-threshold pass never scans a
    `.json` file, so `file_scanned` would always be False regardless of content, which would
    contradict what this test is proving. The manifest glob is widened to `docs/tooling/*.py`
    so the cross-domain pass can still fire on the same `.py` path. The identifier appears in
    a comment (not an assignment) so the local-threshold pass has nothing to flag."""
    _write_manifest(tmp_path, globs=["docs/tooling/*.py"])
    target = tmp_path / "docs" / "tooling" / "pipeline.py"
    content = "# note: EXTERNAL_CAP_V1 legacy behavior\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert entry["cross_domain"]["matches_found"] == 1
    assert entry["cross_domain"]["matches_cited"] == 0
    assert entry["local_threshold"]["file_scanned"] is True
    assert entry["local_threshold"]["matches_found"] == 0
    assert entry["decision"] == "flag"


def test_run_only_local_threshold_pass_trips(monkeypatch, tmp_path):
    """Objective 5: only the local-threshold pass finds an unmarked literal; the
    cross-domain pass runs (in scope) but finds no identifier match.

    Target file must be `.py` (Category B fix, same reasoning as the sibling test above) —
    the manifest glob is widened to `docs/tooling/*.py` so the cross-domain pass has an
    opportunity to fire (and correctly find nothing) on the same path."""
    _write_manifest(tmp_path, globs=["docs/tooling/*.py"])
    target = tmp_path / "docs" / "tooling" / "pipeline.py"
    content = "MAX_RETRIES = 500\n"
    stdin_data = _write_stdin(file_path=str(target), content=content)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert entry["cross_domain"]["file_in_scope"] is True
    assert entry["cross_domain"]["matches_found"] == 0
    assert entry["local_threshold"]["matches_found"] == 1
    assert entry["local_threshold"]["matches_cited"] == 0
    assert entry["decision"] == "flag"


def test_run_both_passes_always_invoked_regardless_of_cross_domain_outcome(monkeypatch, tmp_path):
    """Objective 2: run_local_threshold_pass must fire even when the cross-domain pass
    early-returns ran=False (out-of-scope file) — confirming the two passes are truly
    independent, not short-circuited off each other."""
    _write_manifest(tmp_path)
    unrelated = tmp_path / "src" / "app.py"
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    content = "MAX_RETRIES = 500\n"
    stdin_data = _write_stdin(file_path=str(unrelated), content=content)
    _, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    entry = entries[-1]
    assert entry["cross_domain"]["file_in_scope"] is False
    assert entry["local_threshold"]["file_scanned"] is True
    assert entry["local_threshold"]["matches_found"] == 1


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
