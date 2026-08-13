"""Tests for reference/session_queue_probe.py — the SessionStart staleness/parser logic.

Spec: docs/tooling/session-queue-hardening.md §2b (three staleness cases) and §3 (writer-session-id
regex). Writer contract: commands/lore-close.md Step 4 ("session-queue-meta:" fenced block).

Scope discipline: these tests exercise only the pure functions `extract_writer_session_id` and
`newer_session_transcripts`. No LORE/DB/network access — `fetch_tagged_queue` and
`fetch_most_recent_untagged` (which import psycopg2 and open a connection) are never called.

Runnable two ways:
    pytest tests/test_session_queue_probe.py
    python3 tests/test_session_queue_probe.py   (falls back to a plain assert-based runner)
"""

import importlib.util
import os
import sys
from datetime import datetime, timedelta, timezone

try:
    import pytest
    HAVE_PYTEST = True
except ImportError:
    HAVE_PYTEST = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBE_PATH = os.path.join(REPO_ROOT, "reference", "session_queue_probe.py")


def _load_probe():
    spec = importlib.util.spec_from_file_location("session_queue_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()


# ---------------------------------------------------------------------------
# extract_writer_session_id
# ---------------------------------------------------------------------------

VALID_UUID = "9c760bae-3c48-44c4-bbca-a39fd1981c68"


def test_valid_writer_session_id_in_fenced_block_returns_uuid():
    """§3: a well-formed writer-session-id line inside a session-queue-meta block parses."""
    content = (
        "some capture body\n\n"
        "session-queue-meta:\n"
        f"  writer-session-id: {VALID_UUID}\n"
    )
    assert probe.extract_writer_session_id(content) == VALID_UUID


def test_writer_exact_emitted_text_from_lore_close_step4():
    """Writer/reader contract: reproduce the literal block commands/lore-close.md Step 4
    instructs an agent to write (fence lines, 2-space indent, "writer-session-id:" key), with
    the placeholder substituted for a real session id — exactly what a compliant agent emits.
    If this ever stops matching, the mechanism silently never engages (§6.3's named risk)."""
    content = (
        "git-state:\n"
        "  branch: main\n"
        "  head: 6d6ded2\n"
        "  unpushed: 0\n"
        "  dirty: false\n"
        "\n"
        "session-queue-meta:\n"
        f"  writer-session-id: {VALID_UUID}\n"
    )
    assert probe.extract_writer_session_id(content) == VALID_UUID


def test_field_absent_entirely_returns_none():
    """§2b case 3 / legacy capture: no session-queue-meta block at all → None (writer unknown),
    not a crash."""
    content = "git-state:\n  branch: main\n  head: abc123\n  unpushed: 0\n  dirty: false\n"
    assert probe.extract_writer_session_id(content) is None


def test_empty_content_returns_none():
    assert probe.extract_writer_session_id("") is None
    assert probe.extract_writer_session_id(None) is None


def test_malformed_value_not_a_uuid_returns_none_no_crash():
    """§6.3's named gap: a malformed value must yield None, not raise."""
    content = "session-queue-meta:\n  writer-session-id: not-a-uuid\n"
    assert probe.extract_writer_session_id(content) is None


def test_malformed_value_too_short_returns_none():
    content = "session-queue-meta:\n  writer-session-id: 9c760bae-3c48\n"
    assert probe.extract_writer_session_id(content) is None


def test_malformed_value_empty_returns_none():
    content = "session-queue-meta:\n  writer-session-id:\n"
    assert probe.extract_writer_session_id(content) is None


def test_unsubstituted_template_placeholder_returns_none():
    """A writer that forgot to substitute the literal instruction text from lore-close.md
    Step 4 (`<value of $CLAUDE_CODE_SESSION_ID>`) must not produce a false match."""
    content = "session-queue-meta:\n  writer-session-id: <value of $CLAUDE_CODE_SESSION_ID>\n"
    assert probe.extract_writer_session_id(content) is None


def test_raw_unexpanded_env_var_literal_returns_none():
    """A writer whose shell substitution failed and left the raw variable name behind must
    also not match — it is not a 36-char UUID-shaped value."""
    content = "session-queue-meta:\n  writer-session-id: $CLAUDE_CODE_SESSION_ID\n"
    assert probe.extract_writer_session_id(content) is None


def test_uppercase_uuid_normalized_to_lowercase_on_extraction():
    """The regex is case-insensitive (re.IGNORECASE) and [0-9a-f-]{36} matches an uppercase
    UUID's characters too, so this parses as "writer known" rather than falling through to
    UNKNOWN. But extract_writer_session_id now lowercases the result at the single point of
    extraction, so it matches the lowercase filenames Claude Code actually writes to disk."""
    uppercase_uuid = VALID_UUID.upper()
    content = f"session-queue-meta:\n  writer-session-id: {uppercase_uuid}\n"
    result = probe.extract_writer_session_id(content)
    assert result == VALID_UUID  # normalized to lowercase, matching real transcript filenames
    assert result != uppercase_uuid


def test_uppercase_writer_id_excludes_own_lowercase_transcript_on_disk(monkeypatch, tmp_path):
    """DOWNSTREAM behaviour, not just the extractor: given a capture whose writer-session-id
    is hand-edited/migrated to uppercase, and the writer's real transcript file on disk under
    its lowercase name (as Claude Code actually writes it), the writer's own transcript MUST
    still be excluded from the staleness count. This is the exact path main() exercises:
    extract_writer_session_id(content) -> exclude_names.add(f"{writer_id}.jsonl") ->
    newer_session_transcripts(...). Before the fix, the uppercase id built a filename that
    never matched the lowercase file on disk, so the writer's own close-out tail was silently
    counted as a stale session — reintroducing Round 2's exact bug for this input shape."""
    repo_dir = "/home/d-tuned/agent-rig"
    _patch_home(monkeypatch, tmp_path)
    d = _make_transcripts_dir(tmp_path, repo_dir)

    created_at = datetime(2026, 8, 13, 5, 14, 48, tzinfo=timezone.utc)
    writer_id_lower = "0098cb1e-1cb7-4656-b821-69d5367a6b8e"
    reader_id = "9c760bae-3c48-44c4-bbca-a39fd1981c68"

    # Real transcript file on disk: always lowercase, as Claude Code writes it.
    _touch_with_mtime(d / f"{writer_id_lower}.jsonl", created_at + timedelta(minutes=16))
    _touch_with_mtime(d / f"{reader_id}.jsonl", created_at + timedelta(minutes=20))

    # Capture's recorded writer-session-id is uppercase (hand-edited/migrated/corrupted).
    content = (
        "session-queue-meta:\n"
        f"  writer-session-id: {writer_id_lower.upper()}\n"
    )
    writer_id = probe.extract_writer_session_id(content)
    assert writer_id is not None  # writer_known branch, not UNKNOWN

    exclude_names = {f"{reader_id}.jsonl"}
    exclude_names.add(f"{writer_id}.jsonl")
    result = probe.newer_session_transcripts(repo_dir, created_at, exclude_names)
    assert result == []  # writer's own transcript correctly excluded, not counted as stale


# ---------------------------------------------------------------------------
# newer_session_transcripts
# ---------------------------------------------------------------------------

def _slug_for(repo_dir):
    return "-" + repo_dir.strip("/").replace("/", "-")


def _make_transcripts_dir(tmp_path, repo_dir):
    slug = _slug_for(repo_dir)
    # Mirrors _patch_home's expanduser rewrite: "~" -> tmp_path/"claude_home", so
    # "~/.claude/projects" resolves to tmp_path/claude_home/.claude/projects.
    d = tmp_path / "claude_home" / ".claude" / "projects" / slug
    d.mkdir(parents=True)
    return d


def _touch_with_mtime(path, dt):
    path.write_text("{}\n")
    ts = dt.timestamp()
    os.utime(str(path), (ts, ts))


def _patch_home(monkeypatch, tmp_path):
    monkeypatch.setattr(os.path, "expanduser",
                         lambda p: p.replace("~", str(tmp_path / "claude_home")))


def test_healthy_steady_state_zero_stale_sessions(monkeypatch, tmp_path):
    """§2b writer-known=true, count=0: the writer's own transcript, present with an mtime AFTER
    the capture (real — /lore-close keeps writing through later steps), and the reading
    session's transcript, must both be excluded, leaving zero. This is the case two prior
    review rounds got wrong — the single most important assertion in this file."""
    repo_dir = "/home/d-tuned/agent-rig"
    _patch_home(monkeypatch, tmp_path)
    d = _make_transcripts_dir(tmp_path, repo_dir)

    created_at = datetime(2026, 8, 13, 5, 14, 48, tzinfo=timezone.utc)
    writer_id = "0098cb1e-1cb7-4656-b821-69d5367a6b8e"
    reader_id = "9c760bae-3c48-44c4-bbca-a39fd1981c68"

    # Writer's transcript: mtime 16 minutes AFTER created_at (finishing Steps 5-7).
    _touch_with_mtime(d / f"{writer_id}.jsonl", created_at + timedelta(minutes=16))
    # Reading session's own transcript: also newer (session start writes it).
    _touch_with_mtime(d / f"{reader_id}.jsonl", created_at + timedelta(minutes=20))

    exclude_names = {f"{reader_id}.jsonl", f"{writer_id}.jsonl"}
    result = probe.newer_session_transcripts(repo_dir, created_at, exclude_names)
    assert result == []


def test_genuine_third_newer_session_is_counted_and_identified(monkeypatch, tmp_path):
    """§2b writer-known=true, count=N>0: a genuine third session (neither writer nor reader),
    newer than the capture, must be counted and its name/mtime reported."""
    repo_dir = "/home/d-tuned/agent-rig"
    _patch_home(monkeypatch, tmp_path)
    d = _make_transcripts_dir(tmp_path, repo_dir)

    created_at = datetime(2026, 8, 13, 5, 14, 48, tzinfo=timezone.utc)
    writer_id = "0098cb1e-1cb7-4656-b821-69d5367a6b8e"
    reader_id = "9c760bae-3c48-44c4-bbca-a39fd1981c68"
    unclosed_id = "7920ea8c-0000-4000-8000-000000000000"

    _touch_with_mtime(d / f"{writer_id}.jsonl", created_at + timedelta(minutes=16))
    _touch_with_mtime(d / f"{reader_id}.jsonl", created_at + timedelta(minutes=20))
    _touch_with_mtime(d / f"{unclosed_id}.jsonl", created_at + timedelta(hours=2))

    exclude_names = {f"{reader_id}.jsonl", f"{writer_id}.jsonl"}
    result = probe.newer_session_transcripts(repo_dir, created_at, exclude_names)
    assert len(result) == 1
    assert result[0][0] == f"{unclosed_id}.jsonl"
    assert result[0][1] > created_at


def test_older_transcript_not_counted(monkeypatch, tmp_path):
    """A transcript with mtime BEFORE created_at must not be counted (sanity check on the
    comparison direction, adjacent to the primary staleness assertions above)."""
    repo_dir = "/home/d-tuned/agent-rig"
    _patch_home(monkeypatch, tmp_path)
    d = _make_transcripts_dir(tmp_path, repo_dir)

    created_at = datetime(2026, 8, 13, 5, 14, 48, tzinfo=timezone.utc)
    old_id = "aaaaaaaa-0000-4000-8000-000000000000"
    _touch_with_mtime(d / f"{old_id}.jsonl", created_at - timedelta(hours=1))

    result = probe.newer_session_transcripts(repo_dir, created_at, set())
    assert result == []


def test_subagent_transcripts_never_counted(monkeypatch, tmp_path):
    """§2b/architecture §1b: sub-agent dispatches write to
    '<session-id>/subagents/agent-<hash>.jsonl', one level deeper than top-level
    '<session-id>.jsonl'. The scan is non-recursive (os.listdir, not os.walk) — a nested
    sub-agent transcript, even with a newer mtime, must never be counted."""
    repo_dir = "/home/d-tuned/agent-rig"
    _patch_home(monkeypatch, tmp_path)
    d = _make_transcripts_dir(tmp_path, repo_dir)

    created_at = datetime(2026, 8, 13, 5, 14, 48, tzinfo=timezone.utc)
    main_session_id = "bbbbbbbb-0000-4000-8000-000000000000"
    subagent_dir = d / main_session_id / "subagents"
    subagent_dir.mkdir(parents=True)
    _touch_with_mtime(subagent_dir / "agent-deadbeef.jsonl", created_at + timedelta(hours=3))

    result = probe.newer_session_transcripts(repo_dir, created_at, set())
    assert result == []


# ---------------------------------------------------------------------------
# Plain assert-based runner (used if pytest is not installed)
# ---------------------------------------------------------------------------

def _run_without_pytest():
    import tempfile
    import types
    import inspect

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

    import pathlib

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
