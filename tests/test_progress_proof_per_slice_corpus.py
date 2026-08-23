"""Corpus-driven tests for scripts/progress_proof_per_slice_probe.py — Slice 3.

Runs tests/fixtures/progress_proof_corpus.json (paired with
tests/fixtures/progress_proof_manifest_fixture.json) against the real probe entry point,
probe.main() — never against internals in isolation. Complements
tests/test_progress_proof_per_slice_probe.py's inline fixtures with the file-based corpus §6's
component table names as a deliverable (Self-test fixture corpus row), covering at minimum every
case AC7/AC7a/AC7b/AC11 name for this slice's forge contract.

Runnable two ways:
    pytest tests/test_progress_proof_per_slice_corpus.py
    python3 tests/test_progress_proof_per_slice_corpus.py
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
FIXTURES_DIR = os.path.join(REPO_ROOT, "tests", "fixtures")
CORPUS_PATH = os.path.join(FIXTURES_DIR, "progress_proof_corpus.json")
MANIFEST_FIXTURE_PATH = os.path.join(FIXTURES_DIR, "progress_proof_manifest_fixture.json")


def _load_probe():
    spec = importlib.util.spec_from_file_location("progress_proof_per_slice_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()

with open(CORPUS_PATH) as fh:
    CORPUS = json.load(fh)

with open(MANIFEST_FIXTURE_PATH) as fh:
    MANIFEST_FIXTURE = json.load(fh)


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


def _write_dummy_script(project_dir, name, kind):
    """Generate a real, executable python3 dummy script for a placeholder's proof_command_kind.
    kind: "pass" (exit 0), "fail" (exit 1), "timeout" (sleeps 5s, longer than any override)."""
    scripts_dir = project_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    path = scripts_dir / name
    if kind == "pass":
        path.write_text("import sys\nsys.exit(0)\n")
    elif kind == "fail":
        path.write_text("import sys\nsys.exit(1)\n")
    elif kind == "timeout":
        path.write_text("import time\nimport sys\ntime.sleep(5)\nsys.exit(0)\n")
    else:
        raise ValueError(f"unknown proof_command_kind {kind!r}")
    return f"python3 scripts/{name}"


def _substitute_placeholders(text, case, project_dir):
    if text is None:
        return text
    if "{CMD_OLD}" in text or "{CMD_NEW}" in text:
        old_cmd = _write_dummy_script(
            project_dir, f"{case['id']}_old.py", case["proof_command_kind_old"]
        )
        new_cmd = _write_dummy_script(
            project_dir, f"{case['id']}_new.py", case["proof_command_kind_new"]
        )
        text = text.replace("{CMD_OLD}", old_cmd).replace("{CMD_NEW}", new_cmd)
    if "{CMD_PASS}" in text or "{CMD_FAIL}" in text:
        # Two distinct, fixed-kind commands used unchanged on both old and new sides -- for
        # cases with multiple independent transitions in one edit, not a mutation-pattern pair.
        pass_cmd = _write_dummy_script(project_dir, f"{case['id']}_pass.py", "pass")
        fail_cmd = _write_dummy_script(project_dir, f"{case['id']}_fail.py", "fail")
        text = text.replace("{CMD_PASS}", pass_cmd).replace("{CMD_FAIL}", fail_cmd)
    if "{CMD}" in text:
        kind = case.get("proof_command_kind")
        cmd = _write_dummy_script(project_dir, f"{case['id']}.py", kind)
        text = text.replace("{CMD}", cmd)
    return text


def _run_case(monkeypatch, project_dir, case):
    if case.get("write_allowlist", True):
        allowlist_dir = project_dir / "docs" / "tooling"
        allowlist_dir.mkdir(parents=True, exist_ok=True)
        (allowlist_dir / "progress-proof-allowlist.json").write_text(
            json.dumps(MANIFEST_FIXTURE)
        )

    old_string = _substitute_placeholders(case.get("old_string"), case, project_dir)
    new_string = _substitute_placeholders(case.get("new_string"), case, project_dir)

    if "inner_timeout_override" in case:
        monkeypatch.setattr(probe, "INNER_TIMEOUT", case["inner_timeout_override"])

    file_path_rel = case.get("file_path", os.path.join("docs", "specs", "sprint", "PROGRESS.md"))
    target = project_dir / file_path_rel
    target.parent.mkdir(parents=True, exist_ok=True)

    stdin_data = {
        "session_id": f"corpus-{case['id']}",
        "tool_name": case.get("tool_name", "Edit"),
        "tool_input": {
            "file_path": str(target),
            "old_string": old_string,
            "new_string": new_string,
        },
        "cwd": str(project_dir),
    }

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_dir))
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(stdin_data)))
    buf = io.StringIO()
    with redirect_stdout(buf):
        probe.main()
    stdout_text = buf.getvalue().strip()
    entries = _read_entries(project_dir)
    return stdout_text, entries


def _assert_case(case, stdout_text, entries):
    expect = case["expect"]
    entry = entries[-1]
    if expect["decision"] == "deny":
        assert stdout_text != "", f"{case['id']}: expected a block decision on stdout"
        decision = json.loads(stdout_text)
        assert decision["decision"] == "block", case["id"]
    else:
        assert stdout_text == "", f"{case['id']}: expected silent allow, got {stdout_text!r}"
    assert entry["decision"] == expect["decision"], case["id"]
    for key in (
        "transitions_found", "transitions_verified", "matched_by", "proof_status",
        "file_in_scope",
    ):
        if key in expect:
            assert entry[key] == expect[key], f"{case['id']}: {key} mismatch (entry={entry})"


if HAVE_PYTEST:
    @pytest.mark.parametrize("case", CORPUS["cases"], ids=[c["id"] for c in CORPUS["cases"]])
    def test_corpus_case(monkeypatch, tmp_path, case):
        stdout_text, entries = _run_case(monkeypatch, tmp_path, case)
        _assert_case(case, stdout_text, entries)


def _run_without_pytest():
    import tempfile
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

    passed = 0
    failures = []
    for case in CORPUS["cases"]:
        mp = FakeMonkeypatch()
        tmp_dir_ctx = tempfile.TemporaryDirectory()
        try:
            tmp_path = pathlib.Path(tmp_dir_ctx.name)
            stdout_text, entries = _run_case(mp, tmp_path, case)
            _assert_case(case, stdout_text, entries)
            passed += 1
            print(f"PASS {case['id']}")
        except Exception as exc:  # noqa: BLE001
            failures.append((case["id"], exc))
            print(f"FAIL {case['id']}: {exc}")
        finally:
            mp.undo()
            tmp_dir_ctx.cleanup()

    print(f"\n{passed}/{len(CORPUS['cases'])} passed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    _run_without_pytest()
