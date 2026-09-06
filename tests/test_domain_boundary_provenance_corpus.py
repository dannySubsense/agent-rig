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
        manifest_to_write = MANIFEST_FIXTURE
        if "manifest_globs_override" in case:
            manifest_to_write = dict(MANIFEST_FIXTURE)
            manifest_to_write["pipelineConfigGlobs"] = case["manifest_globs_override"]
        (manifest_dir / "domain-boundary-manifest.json").write_text(json.dumps(manifest_to_write))

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

    if case.get("content_source") == "self_probe_source":
        with open(PROBE_PATH, "r") as fh:
            resolved_content = fh.read()
    else:
        resolved_content = case.get("content", "")

    tool_input = {"file_path": file_path}
    tool_name = case["tool_name"]
    if tool_name == "Write":
        tool_input["content"] = resolved_content
    elif tool_name == "Edit":
        tool_input["new_string"] = case.get("new_string", resolved_content)

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
    """Since Slice 7, track-record entries nest cross_domain/local_threshold fields
    (Architecture §6) rather than exposing them at the top level, and an unmarked match only
    ever resolves to a stdout "block" under mode == "blocking" — under the default
    (unconfigured) log_only mode it downgrades to a silent "flag" (Architecture §3's F1
    behavior change). This corpus runs with no domain-boundary-mode.json present, so every
    case exercises log_only: expected "deny" decisions in the fixture were downgraded to
    "flag" accordingly, and only a literal "deny" here would assert a stdout block."""
    expect = case["expect"]
    entry = entries[-1]
    cross_domain = entry["cross_domain"]
    local_threshold = entry["local_threshold"]
    if expect["decision"] == "deny":
        assert stdout_text != "", f"{case['id']}: expected a block decision on stdout"
        decision = json.loads(stdout_text)
        assert decision["decision"] == "block", case["id"]
    else:
        assert stdout_text == "", f"{case['id']}: expected silent allow, got {stdout_text!r}"
    assert entry["decision"] == expect["decision"], case["id"]
    if "manifest_status" in expect:
        assert cross_domain["manifest_status"] == expect["manifest_status"], case["id"]
    if "file_in_scope" in expect:
        assert cross_domain["file_in_scope"] == expect["file_in_scope"], case["id"]
    if "matches_found" in expect:
        assert cross_domain["matches_found"] == expect["matches_found"], case["id"]
    if "matches_cited" in expect:
        assert cross_domain["matches_cited"] == expect["matches_cited"], case["id"]
    # Slice 9 — local_threshold (Slices 4-7) corpus-level assertions.
    if "local_threshold_file_scanned" in expect:
        assert (
            local_threshold["file_scanned"] == expect["local_threshold_file_scanned"]
        ), case["id"]
    if "local_threshold_matches_found" in expect:
        assert (
            local_threshold["matches_found"] == expect["local_threshold_matches_found"]
        ), case["id"]
    if "local_threshold_matches_cited" in expect:
        assert (
            local_threshold["matches_cited"] == expect["local_threshold_matches_cited"]
        ), case["id"]
    if "local_threshold_matches_found_min" in expect:
        assert (
            local_threshold["matches_found"] >= expect["local_threshold_matches_found_min"]
        ), case["id"]
    if "local_threshold_has_unmarked" in expect:
        has_unmarked = (
            local_threshold["matches_found"] is not None
            and local_threshold["matches_cited"] is not None
            and local_threshold["matches_found"] > local_threshold["matches_cited"]
        )
        assert has_unmarked == expect["local_threshold_has_unmarked"], case["id"]


if HAVE_PYTEST:
    @pytest.mark.parametrize("case", CORPUS["cases"], ids=[c["id"] for c in CORPUS["cases"]])
    def test_corpus_case(monkeypatch, tmp_path, case):
        stdout_text, entries = _run_case(monkeypatch, tmp_path, case)
        _assert_case(case, stdout_text, entries)

    def test_self_scan_does_not_flag_proximity_window_threshold():
        """Corpus-level (end-to-end through detect_threshold_literals, the same function
        run_local_threshold_pass() calls internally) confirmation that
        `PROXIMITY_WINDOW_THRESHOLD = 2` is NOT flagged as unmarked (its own
        THRESHOLD-PROVENANCE: citation satisfies the check), against the real, current probe
        source (not a duplicated literal snapshot). The incumbent `PROXIMITY_WINDOW = 5`
        constant this test previously also checked was removed entirely (benchmark-verified
        unsourced number; the `DOMAIN-BOUNDARY:` check is now same-line-only, no window
        constant exists to self-scan)."""
        with open(PROBE_PATH, "r") as fh:
            source = fh.read()
        lines = source.split("\n")
        flags = probe.detect_threshold_literals(PROBE_PATH, source)
        new_flag = next(
            f
            for f in flags
            if f["context"] == "assign_module_or_class"
            and f["literal_repr"] == "2"
            and "PROXIMITY_WINDOW_THRESHOLD" in lines[f["line_index"]]
        )
        assert probe.has_threshold_provenance_marker(lines, new_flag["line_index"]) is True


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
