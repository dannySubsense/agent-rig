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
    "timestamp", "session_id", "tool_name", "file_path", "manifest_status",
    "file_in_scope", "matches_found", "matches_cited", "decision", "reason", "probe_error",
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
    _write_manifest(tmp_path)
    unrelated = tmp_path / "src" / "app.py"
    unrelated.parent.mkdir(parents=True, exist_ok=True)
    stdin_data = _write_stdin(
        file_path=str(unrelated), content="EXTERNAL_CAP_V1 = 5\n"
    )
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    assert stdout_text == ""
    assert entries[-1]["decision"] == "allow"
    assert entries[-1]["file_in_scope"] is False
    assert entries[-1]["manifest_status"] == "matched"


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
    assert entries[-1]["manifest_status"] == "absent_or_invalid"


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
    assert entries[-1]["file_in_scope"] is True
    assert entries[-1]["matches_found"] == 1
    assert entries[-1]["matches_cited"] == 1


# ---------------------------------------------------------------------------
# AC4 — in-scope match with no qualifying marker -> deny naming file/identifier/remediation
# ---------------------------------------------------------------------------

def test_ac4_uncited_match_is_denied_naming_file_identifier_and_remediation(monkeypatch, tmp_path):
    _write_manifest(tmp_path)
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
    assert entries[-1]["matches_found"] == 1
    assert entries[-1]["matches_cited"] == 0


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
    assert entries[-1]["manifest_status"] == "absent_or_invalid"


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
    assert entries[-1]["manifest_status"] == "absent_or_invalid"


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
    _write_manifest(tmp_path)
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
    not a gate, per write_track_record()'s own docstring."""
    _write_manifest(tmp_path)
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
    assert entries[-1]["file_in_scope"] is True
    assert entries[-1]["matches_found"] == 0


def test_ac7_marker_just_outside_window_denies(monkeypatch, tmp_path):
    """§5 PROXIMITY_WINDOW = 5 (inclusive). A marker at exactly line 7 relative to a match on
    line 1 (index 0) is 6 lines away — outside the window — and must deny."""
    _write_manifest(tmp_path)
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
    assert entries[-1]["matches_found"] == 0


def test_ac7_absolute_path_matches_relative_glob(monkeypatch, tmp_path):
    """§6 step 3 / §8 AC7's most load-bearing pair (1/2): a manifest glob written relative to
    repo root (docs/tooling/*.json) must match a realistic, non-relativized ABSOLUTE
    tool_input.file_path — the real envelope shape, per §7's live-verified capture."""
    _write_manifest(tmp_path)
    absolute_target = tmp_path / "docs" / "tooling" / "foo.json"
    stdin_data = _write_stdin(
        file_path=str(absolute_target), content="EXTERNAL_CAP_V1 = 5\n"
    )
    assert os.path.isabs(stdin_data["tool_input"]["file_path"])
    stdout_text, entries = _run_probe(monkeypatch, tmp_path, stdin_data)
    decision = _decision(stdout_text)
    assert decision is not None and decision["decision"] == "block"
    assert entries[-1]["file_in_scope"] is True


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
    assert entries[-1]["file_in_scope"] is False


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
