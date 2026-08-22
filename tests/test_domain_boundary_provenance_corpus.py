"""Corpus-driven tests for scripts/domain_boundary_provenance_probe.py — Slice 3.

Runs tests/fixtures/domain_boundary_corpus.json (paired with
tests/fixtures/domain_boundary_manifest_fixture.json) against the real probe entry point,
`probe.main()` — never against internals in isolation. Complements
tests/test_domain_boundary_provenance_probe.py's Slice 1 inline fixtures with the file-based
corpus §6's component table names as a deliverable, and adds the distance-5 PROXIMITY_WINDOW
boundary case Slice 1/2 QC found untested.

Runnable two ways:
    pytest tests/test_domain_boundary_provenance_corpus.py
    python3 tests/test_domain_boundary_provenance_corpus.py
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
PROBE_PATH = os.path.join(REPO_ROOT, "scripts", "domain_boundary_provenance_probe.py")
FIXTURES_DIR = os.path.join(REPO_ROOT, "tests", "fixtures")
CORPUS_PATH = os.path.join(FIXTURES_DIR, "domain_boundary_corpus.json")
MANIFEST_FIXTURE_PATH = os.path.join(FIXTURES_DIR, "domain_boundary_manifest_fixture.json")


def _load_probe():
    spec = importlib.util.spec_from_file_location("domain_boundary_provenance_probe", PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()

with open(CORPUS_PATH) as fh:
    CORPUS = json.load(fh)

with open(MANIFEST_FIXTURE_PATH) as fh:
    MANIFEST_FIXTURE = json.load(fh)


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


def _run_case(monkeypatch, project_dir, case):
    if case.get("use_manifest", True):
        manifest_dir = project_dir / "docs" / "tooling"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "domain-boundary-manifest.json").write_text(json.dumps(MANIFEST_FIXTURE))

    if case.get("is_absolute_outside_root"):
        outside_root = project_dir.parent / "outside_project"
        target = outside_root / case["file_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        file_path = str(target)
    elif case.get("is_absolute"):
        target = project_dir / case["file_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        file_path = str(target)
        assert os.path.isabs(file_path)
    else:
        target = project_dir / case["file_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        file_path = str(target)

    tool_input = {"file_path": file_path}
    tool_name = case["tool_name"]
    if tool_name == "Write":
        tool_input["content"] = case.get("content", "")
    elif tool_name == "Edit":
        tool_input["new_string"] = case.get("new_string", "")

    stdin_data = {
        "session_id": f"corpus-{case['id']}",
        "tool_name": tool_name,
        "tool_input": tool_input,
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
    if "manifest_status" in expect:
        assert entry["manifest_status"] == expect["manifest_status"], case["id"]
    if "file_in_scope" in expect:
        assert entry["file_in_scope"] == expect["file_in_scope"], case["id"]
    if "matches_found" in expect:
        assert entry["matches_found"] == expect["matches_found"], case["id"]
    if "matches_cited" in expect:
        assert entry["matches_cited"] == expect["matches_cited"], case["id"]


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
