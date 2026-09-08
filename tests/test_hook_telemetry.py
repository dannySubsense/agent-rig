"""Tests for scripts/hook_telemetry.py — Slice 1 (normalized envelope + shared writer).

Spec: docs/tooling/hook-telemetry-schema/SPEC.md §3 (TelemetryEvent), §4
(write_telemetry_event / write_telemetry_pg / to_jsonl_line).

Loads the copy under scripts/, matching this repo's existing test convention (see
tests/test_signpost_checklist_probe.py's header note).

Runnable two ways:
    pytest tests/test_hook_telemetry.py
    python3 tests/test_hook_telemetry.py   (falls back to a plain assert-based runner)
"""

import importlib.util
import json
import os

try:
    import pytest  # noqa: F401
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_PATH = os.path.join(REPO_ROOT, "scripts", "hook_telemetry.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("hook_telemetry", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


telemetry = _load_module()


def _read_lines(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


# ---------------------------------------------------------------------------
# write_telemetry_event — shape + verbatim decision
# ---------------------------------------------------------------------------

def test_write_telemetry_event_writes_one_correctly_shaped_json_line(tmp_path):
    path = str(tmp_path / "log.jsonl")
    telemetry.write_telemetry_event(
        hook_name="signpost-checklist",
        jsonl_path=path,
        session_id="s1",
        decision="allow",
        reason=None,
        probe_error=None,
        payload={"stop_hook_active": False},
    )
    lines = _read_lines(path)
    assert len(lines) == 1
    entry = lines[0]
    assert set(entry.keys()) == {
        "hook_name", "timestamp", "session_id", "decision", "reason",
        "probe_error", "payload",
    }
    assert entry["hook_name"] == "signpost-checklist"
    assert entry["session_id"] == "s1"
    assert entry["decision"] == "allow"
    assert entry["payload"] == {"stop_hook_active": False}
    assert isinstance(entry["timestamp"], str) and entry["timestamp"]


def test_decision_recorded_verbatim_deny_not_remapped_to_block(tmp_path):
    path = str(tmp_path / "log.jsonl")
    telemetry.write_telemetry_event(
        hook_name="progress-proof-per-slice",
        jsonl_path=path,
        session_id="s1",
        decision="deny",
        reason="no proof",
        probe_error=None,
        payload={"file_path": "foo.py"},
    )
    entry = _read_lines(path)[0]
    assert entry["decision"] == "deny"


def test_payload_never_gets_a_conditional_decision_key(tmp_path):
    """payload's keyset must be exactly what the caller passed, independent of decision value —
    no 'decision' key ever gets injected into payload based on decision's value."""
    path = str(tmp_path / "log.jsonl")
    for decision in ("allow", "block", "deny", "flagged", "probe_error"):
        telemetry.write_telemetry_event(
            hook_name="h",
            jsonl_path=path,
            session_id=None,
            decision=decision,
            reason=None,
            probe_error=None,
            payload={"x": 1},
        )
    for entry in _read_lines(path):
        assert entry["payload"] == {"x": 1}
        assert "decision" not in entry["payload"]


def test_write_telemetry_event_never_raises_on_unwritable_path(tmp_path):
    """Best-effort contract: a path under a non-existent, uncreatable location must not raise
    into the caller. Uses a file (not a dir) as a path component to force os.makedirs to fail,
    isolated entirely under tmp_path."""
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("i am a file, not a directory")
    bad_path = str(blocker / "nested" / "log.jsonl")
    telemetry.write_telemetry_event(
        hook_name="h",
        jsonl_path=bad_path,
        session_id=None,
        decision="allow",
        reason=None,
        probe_error=None,
        payload={},
    )
    # No exception propagated — that is the entire assertion.


# ---------------------------------------------------------------------------
# write_telemetry_pg — true no-op
# ---------------------------------------------------------------------------

def test_write_telemetry_pg_is_a_true_noop(tmp_path):  # noqa: ARG001 (fixture unused, kept for fallback-runner uniformity)
    event = telemetry.TelemetryEvent(
        hook_name="h",
        timestamp="2026-09-07T00:00:00+00:00",
        session_id="s1",
        decision="allow",
        reason=None,
        probe_error=None,
        payload={"a": 1},
    )
    result = telemetry.write_telemetry_pg(event)
    assert result is None


# ---------------------------------------------------------------------------
# to_jsonl_line
# ---------------------------------------------------------------------------

def test_to_jsonl_line_round_trips_all_fields(tmp_path):  # noqa: ARG001
    event = telemetry.TelemetryEvent(
        hook_name="no-preamble-no-meta-narration",
        timestamp="2026-09-07T00:00:00+00:00",
        session_id="s2",
        decision="flagged",
        reason="narrating clause",
        probe_error=None,
        payload={"mode": "advisory"},
    )
    line = telemetry.to_jsonl_line(event)
    parsed = json.loads(line)
    assert parsed["hook_name"] == "no-preamble-no-meta-narration"
    assert parsed["decision"] == "flagged"
    assert parsed["payload"] == {"mode": "advisory"}


# ---------------------------------------------------------------------------
# Plain-runner fallback
# ---------------------------------------------------------------------------

if not HAVE_PYTEST:
    import tempfile

    class _TmpPath:
        def __init__(self, path):
            self._path = path

        def __truediv__(self, name):
            return _TmpPath(os.path.join(self._path, name))

        def write_text(self, text):
            with open(self._path, "w") as fh:
                fh.write(text)

        def __str__(self):
            return self._path

    def _run_all():
        tests = [v for k, v in globals().items() if k.startswith("test_")]
        failures = 0
        for t in tests:
            with tempfile.TemporaryDirectory() as d:
                try:
                    t(_TmpPath(d))
                except Exception as e:  # noqa: BLE001
                    failures += 1
                    print(f"FAIL {t.__name__}: {e}")
                else:
                    print(f"PASS {t.__name__}")
        print(f"\n{len(tests) - failures}/{len(tests)} passed")

    if __name__ == "__main__":
        _run_all()
