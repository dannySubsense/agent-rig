"""Tests for .claude/hooks/signpost-checklist.sh — Slice 6 (hook wrapper + settings wiring).

Spec: docs/specs/signpost-checklist-redesign/04-ROADMAP.md "## Slice 6" Tests section.

Integration-style: invokes the real wrapper script via subprocess against crafted stdin
payloads, comparing its block/allow decision to calling scripts/signpost_checklist_probe.py
directly, and confirms fail-open behavior on a deliberately broken probe invocation. No
precedent wrapper-level test file exists in
archive/first-turn-contract-enforcement/tests/ (checked before writing this) — this is a new
file, following that directory's naming/docstring convention.

Runnable two ways:
    pytest tests/test_signpost_checklist_wrapper.py
    python3 tests/test_signpost_checklist_wrapper.py   (falls back to a plain assert-based runner)
"""

import json
import os
import shutil
import subprocess
import tempfile

try:
    import pytest  # noqa: F401
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRAPPER_PATH = os.path.join(REPO_ROOT, ".claude", "hooks", "signpost-checklist.sh")
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "signpost_checklist_probe.py")


def _isolated_track_record_env():
    """Redirect TRACK_RECORD_PATH (probe) / track_record_path (wrapper's write_probe_error)
    to a per-call tmp path via SIGNPOST_TRACK_RECORD_PATH, honored by both
    scripts/signpost_checklist_probe.py and .claude/hooks/signpost-checklist.sh, so subprocess
    invocations never write into the live gitignored log."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    os.remove(path)  # writers must create it fresh
    env = dict(os.environ)
    env["SIGNPOST_TRACK_RECORD_PATH"] = path
    return env, path


def _run_wrapper(stdin_payload, wrapper_path=WRAPPER_PATH, cwd=REPO_ROOT):
    env, track_path = _isolated_track_record_env()
    try:
        return subprocess.run(
            ["bash", wrapper_path],
            input=json.dumps(stdin_payload),
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=15,
            env=env,
        )
    finally:
        if os.path.exists(track_path):
            os.remove(track_path)


def _run_probe_directly(stdin_payload):
    env, track_path = _isolated_track_record_env()
    try:
        return subprocess.run(
            ["python3", PROBE_PATH],
            input=json.dumps(stdin_payload),
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=15,
            env=env,
        )
    finally:
        if os.path.exists(track_path):
            os.remove(track_path)


# ---------------------------------------------------------------------------
# Slice 6 Test 1: wrapper decision matches direct probe invocation.
# ---------------------------------------------------------------------------

def test_wrapper_stop_hook_active_matches_direct_probe_allow():
    """stop_hook_active=True is an unconditional, deterministic allow (run()'s first gate,
    no transcript needed) — same crafted payload through the wrapper and the probe directly
    must produce the same (empty-stdout, exit-0, allow) decision."""
    payload = {
        "session_id": "wrapper-test-session",
        "stop_hook_active": True,
        "transcript_path": "/nonexistent/does-not-matter.jsonl",
        "last_assistant_message": "irrelevant on this gate",
    }
    wrapper_result = _run_wrapper(payload)
    probe_result = _run_probe_directly(payload)

    assert probe_result.returncode == 0
    assert wrapper_result.returncode == 0
    assert probe_result.stdout.strip() in ("", "{}")
    assert wrapper_result.stdout.strip() == ""


def test_wrapper_no_queue_marker_matches_direct_probe_allow():
    """No queue-injection marker in the transcript -> mechanism does not activate (US-5 AC3),
    an allow decision reachable without stop_hook_active. Verifies the wrapper relays the same
    allow decision as the probe for a second, distinct gating path."""
    payload = {
        "session_id": "wrapper-test-session-2",
        "stop_hook_active": False,
        "transcript_path": "/nonexistent/does-not-matter.jsonl",
        "last_assistant_message": "irrelevant on this gate",
    }
    wrapper_result = _run_wrapper(payload)
    probe_result = _run_probe_directly(payload)

    assert probe_result.returncode == 0
    assert wrapper_result.returncode == 0
    assert probe_result.stdout.strip() in ("", "{}")
    assert wrapper_result.stdout.strip() == ""


# ---------------------------------------------------------------------------
# Slice 6 Test 2: wrapper fails open on a broken probe invocation.
# ---------------------------------------------------------------------------

def test_wrapper_fails_open_when_probe_script_missing(tmp_path=None):
    """A deliberately broken probe invocation (script path does not exist) must not make the
    wrapper block or crash — it must exit 0 with no blocking output, matching repo convention
    (fail-open on every failure mode, per the wrapper's own header comment).

    Isolated fixture, never touches the real live probe: the wrapper resolves REPO_DIR from
    the current working directory (`REPO_DIR="$(pwd)"`, see signpost-checklist.sh line 9 —
    changed from BASH_SOURCE-based resolution so a globally-installed copy at
    ~/.claude/hooks/ still resolves to whatever project invoked it, not the wrapper's own
    install location). So invoking the real wrapper script with cwd=tmp_root resolves
    REPO_DIR to tmp_root — a throwaway directory where scripts/signpost_checklist_probe.py is
    simply never created. This is structurally isolated: nothing here reads, moves, or
    deletes the real repo's scripts/signpost_checklist_probe.py, so no failure mode
    (assertion, SIGKILL, SIGINT, collection abort, parallel test runs) can leave the live
    probe absent.
    """
    own_tmp_dir = tmp_path is None
    tmp_root = tempfile.mkdtemp(prefix="signpost-wrapper-test-") if own_tmp_dir else str(tmp_path)
    try:
        # Deliberately do NOT create tmp_root/scripts/ — the probe path the wrapper resolves
        # to (tmp_root/scripts/signpost_checklist_probe.py) is missing by construction.

        payload = {
            "session_id": "wrapper-test-session-broken",
            "stop_hook_active": False,
            "transcript_path": "/nonexistent/does-not-matter.jsonl",
            "last_assistant_message": "irrelevant on this gate",
        }
        result = _run_wrapper(payload, wrapper_path=WRAPPER_PATH, cwd=tmp_root)
        assert result.returncode == 0
        assert result.stdout.strip() == ""
    finally:
        if own_tmp_dir:
            shutil.rmtree(tmp_root, ignore_errors=True)


# ---------------------------------------------------------------------------
# Plain-assert fallback runner (matches archived probe's test file convention).
# ---------------------------------------------------------------------------

def _run_all():
    tests = [obj for name, obj in globals().items() if name.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__" and not HAVE_PYTEST:
    _run_all()
