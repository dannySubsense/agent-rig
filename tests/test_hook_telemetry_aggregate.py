"""Tests for scripts/hook_telemetry_aggregate.py — Slice 1.

Spec: docs/tooling/hook-telemetry-schema/SPEC.md §4 (load_events / summarize / print_report).

Runnable two ways:
    pytest tests/test_hook_telemetry_aggregate.py
    python3 tests/test_hook_telemetry_aggregate.py   (falls back to a plain assert-based runner)
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
MODULE_PATH = os.path.join(REPO_ROOT, "scripts", "hook_telemetry_aggregate.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("hook_telemetry_aggregate", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


aggregate = _load_module()


def _write_lines(path, dicts_or_strs):
    with open(path, "w") as fh:
        for item in dicts_or_strs:
            line = item if isinstance(item, str) else json.dumps(item)
            fh.write(line + "\n")


# ---------------------------------------------------------------------------
# load_events
# ---------------------------------------------------------------------------

def test_load_events_missing_file_returns_empty_list(tmp_path):
    path = str(tmp_path / "does-not-exist.jsonl")
    assert aggregate.load_events(path) == []


def test_load_events_skips_malformed_json_line_not_raises(tmp_path):
    path = str(tmp_path / "log.jsonl")
    _write_lines(path, ["{not valid json"])
    assert aggregate.load_events(path) == []


def test_load_events_mix_of_valid_and_invalid_returns_only_valid(tmp_path):
    path = str(tmp_path / "log.jsonl")
    valid1 = {"decision": "allow", "probe_error": None, "timestamp": "2026-09-07T00:00:00+00:00"}
    valid2 = {"decision": "block", "probe_error": None, "timestamp": "2026-09-07T00:01:00+00:00"}
    _write_lines(path, [valid1, "{broken", valid2, ""])
    events = aggregate.load_events(path)
    assert events == [valid1, valid2]


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------

def test_summarize_decision_counts_keeps_deny_and_block_as_separate_keys():
    events = [
        {"decision": "deny", "probe_error": None},
        {"decision": "block", "probe_error": None},
        {"decision": "deny", "probe_error": None},
    ]
    summary = aggregate.summarize(events)
    assert summary["decision_counts"] == {"deny": 2, "block": 1}


def test_summarize_block_side_count_sums_block_and_deny():
    events = [
        {"decision": "deny", "probe_error": None},
        {"decision": "block", "probe_error": None},
        {"decision": "allow", "probe_error": None},
    ]
    summary = aggregate.summarize(events)
    assert summary["block_side_count"] == 2


def test_summarize_error_count_derived_from_probe_error_field_not_decision_string():
    """A case where decision != 'probe_error' but probe_error is set must still count as an
    error — error_count is derived from `probe_error is not None`, never a decision match."""
    events = [
        {"decision": "allow", "probe_error": "unexpected exception in analyze()"},
        {"decision": "probe_error", "probe_error": "timeout"},
        {"decision": "allow", "probe_error": None},
    ]
    summary = aggregate.summarize(events)
    assert summary["error_count"] == 2
    assert summary["error_rate"] == 2 / 3


def test_summarize_handles_legacy_flat_shape_and_new_envelope_shape_in_same_file():
    """Both shapes carry `decision`/`probe_error` at the top level — summarize() must produce
    correct counts regardless of whether hook-specific fields are flat (legacy) or nested under
    `payload` (new envelope), since summarize() never reads anything but decision/probe_error/
    timestamp at the top level."""
    legacy_flat = {
        "timestamp": "2026-09-07T00:00:00+00:00",
        "session_id": "s1",
        "stop_hook_active": False,
        "mode": "blocking",
        "decision": "block",
        "flagged_clauses": [],
        "reason": "r",
        "probe_error": None,
    }
    new_envelope = {
        "hook_name": "no-preamble-no-meta-narration",
        "timestamp": "2026-09-07T00:01:00+00:00",
        "session_id": "s2",
        "decision": "allow",
        "reason": None,
        "probe_error": None,
        "payload": {"stop_hook_active": False, "mode": "blocking", "flagged_clauses": []},
    }
    summary = aggregate.summarize([legacy_flat, new_envelope])
    assert summary["total"] == 2
    assert summary["decision_counts"] == {"block": 1, "allow": 1}
    assert summary["block_side_count"] == 1
    assert summary["error_count"] == 0
    assert summary["first_ts"] == "2026-09-07T00:00:00+00:00"
    assert summary["last_ts"] == "2026-09-07T00:01:00+00:00"


def test_summarize_empty_events_gives_zero_total_and_zero_error_rate():
    summary = aggregate.summarize([])
    assert summary["total"] == 0
    assert summary["error_rate"] == 0.0
    assert summary["decision_counts"] == {}
    assert summary["first_ts"] is None
    assert summary["last_ts"] is None


# ---------------------------------------------------------------------------
# print_report — smoke test only
# ---------------------------------------------------------------------------

def test_print_report_runs_without_raising_on_typical_summary(capsys):
    per_hook = {
        "signpost-checklist": aggregate.summarize(
            [{"decision": "allow", "probe_error": None, "timestamp": "t1"}]
        ),
        "no-preamble-no-meta-narration": aggregate.summarize([]),
    }
    combined = aggregate.summarize(
        [{"decision": "allow", "probe_error": None, "timestamp": "t1"}]
    )
    aggregate.print_report(per_hook, combined)
    captured = capsys.readouterr()
    assert "signpost-checklist" in captured.out
    assert "combined" in captured.out


if not HAVE_PYTEST:
    import tempfile

    class _TmpPath:
        def __init__(self, path):
            self._path = path

        def __truediv__(self, name):
            return _TmpPath(os.path.join(self._path, name))

        def __str__(self):
            return self._path

    def _run_all():
        tests = [(k, v) for k, v in globals().items() if k.startswith("test_")]
        failures = 0
        for name, t in tests:
            import inspect
            params = inspect.signature(t).parameters
            kwargs = {}
            tmp_ctx = None
            if "tmp_path" in params:
                tmp_ctx = tempfile.TemporaryDirectory()
                kwargs["tmp_path"] = _TmpPath(tmp_ctx.name)
            if "capsys" in params:
                print(f"SKIP {name} (needs pytest capsys)")
                continue
            try:
                t(**kwargs)
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {e}")
            else:
                print(f"PASS {name}")
            finally:
                if tmp_ctx:
                    tmp_ctx.cleanup()
        print(f"\n{len(tests) - failures}/{len(tests)} passed (capsys tests skipped in fallback runner)")

    if __name__ == "__main__":
        _run_all()
