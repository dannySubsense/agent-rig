#!/usr/bin/env python3
"""PreToolUse hook — domain-boundary provenance check (probe core).

Reads `PreToolUse` stdin JSON (`tool_name`, `tool_input`, `cwd`) and decides whether an
`Edit`/`Write` call may proceed, per the 8-step procedure in
docs/tooling/domain-boundary-provenance-hook.md §6:

  1. Non-Edit/Write tool_name -> allow.
  2. Load `<repo>/docs/tooling/domain-boundary-manifest.json` (repo root =
     `$CLAUDE_PROJECT_DIR`); absent/unreadable/schema-invalid -> allow.
  3. Normalize `tool_input.file_path` (an ABSOLUTE path, confirmed by live capture) to a
     repo-root-relative, POSIX-style path before any glob match; a path outside the repo
     root -> allow (file_in_scope: false), never a glob-match attempt. No match against
     `pipelineConfigGlobs` -> allow (file_in_scope: false).
  4. Scan surface is `tool_input.content` (Write) or `tool_input.new_string` (Edit) only —
     never the on-disk file, never an `old_string`->`new_string` resolution.
  5-7. Scan for `externalSourceIdentifiers` matches; each match must have a
     `DOMAIN-BOUNDARY: <non-empty>` marker line within a 5-line window (§5) in the SAME
     scan surface. Any unmarked match -> deny.
  8. Deny reason lists every unmarked match (file, line, identifier) + remediation.

Emits the deny shape Claude Code's `PreToolUse` hook understands (live-verified,
2026-08-22: top-level `{"decision": "block", "reason": ...}`), or nothing (silence means
allow) — see docs/tooling/domain-boundary-provenance-hook.md §3/§7. Appends one entry per
invocation to the gitignored track-record log (§7's TrackRecordEntry shape).

Pure function of stdin. No LORE access, no network. Never blocks on its own failure — any
exception here is caught and treated as an allow, with a `probe_error` track-record entry
(the wrapper's own timeout/non-zero-exit fail-open is the outer guarantee; this is this
probe's inner one, per first_turn_contract_probe.py's convention).
"""

import ast
import fnmatch
import json
import os
import re
import sys
import textwrap
from datetime import datetime, timezone
from typing import TypedDict

TRACK_RECORD_RELATIVE_PATH = os.path.join(
    "docs", "tooling", "domain-boundary-provenance-track-record.jsonl"
)
MANIFEST_RELATIVE_PATH = os.path.join("docs", "tooling", "domain-boundary-manifest.json")
MODE_CONFIG_RELATIVE_PATH = os.path.join("docs", "tooling", "domain-boundary-mode.json")

# §5 — the citation marker; a qualifying line has this literal string followed by
# non-whitespace content on the same line.
MARKER = "DOMAIN-BOUNDARY:"
_MARKER_RE = re.compile(re.escape(MARKER) + r"\s*(\S.*)?$")

# THRESHOLD-PROVENANCE: docs/research/domain-boundary-hook-benchmark/results.md §5
# §5 measures comment-to-assignment proximity generically (rule c/d, any name-bound
# constant, not marker-specific): 100% of commented assignments land within 2 lines.
# This window (5) is a superset of that measured range for the `DOMAIN-BOUNDARY:`
# marker context.
PROXIMITY_WINDOW = 5

# §4 — the new check's citation marker; a qualifying line has this literal string followed
# by non-whitespace content on the same line. Distinct marker from `DOMAIN-BOUNDARY:` above.
THRESHOLD_MARKER = "THRESHOLD-PROVENANCE:"
_THRESHOLD_MARKER_RE = re.compile(re.escape(THRESHOLD_MARKER) + r"\s*(\S.*)?$")

# §4 — citation form: file-path-shaped token, URL, or DDR-NNNN reference. This is the only
# acceptance form — no named-owner alternative exists (Danny's ruling: no owner-name
# acceptance path of any kind, for any constant, ever; see Architecture §4).
_THRESHOLD_CITATION_RE = re.compile(
    r"[\w./-]+\.(?:py|md|json|ts|tsx|sh)\b" r"|https?://\S+" r"|DDR-\d+"
)


def read_stdin():
    """Best-effort stdin JSON parse. Absence or malformed stdin must not crash the probe;
    the caller treats a resulting empty dict as "nothing to check", which allows."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def get_project_dir(stdin_data):
    """Repo root per §6 step 3: `$CLAUDE_PROJECT_DIR`, falling back to stdin's `cwd` if the
    env var is unset (e.g. local manual invocation) — the env var is the documented,
    authoritative source; `cwd` is a best-effort fallback only."""
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return env_dir
    cwd = stdin_data.get("cwd")
    if isinstance(cwd, str) and cwd:
        return cwd
    return os.getcwd()


def load_manifest(project_dir):
    """§6 step 2 — load and minimally schema-validate the manifest. Returns (manifest_dict,
    status) where status is "matched" (valid manifest loaded) or "absent_or_invalid"."""
    manifest_path = os.path.join(project_dir, MANIFEST_RELATIVE_PATH)
    try:
        with open(manifest_path, "r") as fh:
            raw = fh.read()
    except Exception:
        return None, "absent_or_invalid"
    try:
        data = json.loads(raw)
    except Exception:
        return None, "absent_or_invalid"
    if not validate_manifest_shape(data):
        return None, "absent_or_invalid"
    return data, "matched"


def validate_manifest_shape(data):
    """Minimal structural check against §4's schema (stdlib only, per §10): schemaVersion
    == 1, pipelineConfigGlobs and externalSourceIdentifiers both present as lists of
    strings."""
    if not isinstance(data, dict):
        return False
    if data.get("schemaVersion") != 1:
        return False
    globs = data.get("pipelineConfigGlobs")
    identifiers = data.get("externalSourceIdentifiers")
    if not isinstance(globs, list) or not all(isinstance(g, str) for g in globs):
        return False
    if not isinstance(identifiers, list) or not all(isinstance(i, str) for i in identifiers):
        return False
    return True


def load_mode_config(project_dir):
    """§5 — load the mode config, sibling to the manifest, same discovery convention
    (relative to `project_dir`, itself resolved from `$CLAUDE_PROJECT_DIR` by
    `get_project_dir`). Fail-safe default: any absence, read failure, or schema-invalid
    content -> "log_only" (an uninstalled/unconfigured mode file must never default to
    blocking). Only a valid `{"schemaVersion": 1, "mode": "blocking"}` yields "blocking"."""
    mode_path = os.path.join(project_dir, MODE_CONFIG_RELATIVE_PATH)
    try:
        with open(mode_path, "r") as fh:
            raw = fh.read()
    except Exception:
        return "log_only"
    try:
        data = json.loads(raw)
    except Exception:
        return "log_only"
    if not isinstance(data, dict):
        return "log_only"
    if data.get("schemaVersion") != 1:
        return "log_only"
    mode = data.get("mode")
    if mode not in ("log_only", "blocking"):
        return "log_only"
    return mode


def normalize_file_path(project_dir, file_path):
    """§6 step 3 — resolve both `project_dir` and `file_path` via `os.path.realpath`,
    verify containment via `os.path.commonpath`, then strip the prefix and convert to
    POSIX separators. Returns (relative_posix_path, in_repo: bool). `relative_posix_path`
    is None when `in_repo` is False."""
    if not isinstance(file_path, str) or not file_path:
        return None, False
    resolved_root = os.path.realpath(project_dir)
    resolved_file = os.path.realpath(file_path)
    try:
        common = os.path.commonpath([resolved_root, resolved_file])
    except ValueError:
        # Different drives/roots (non-POSIX) — never under the repo root.
        return None, False
    if common != resolved_root:
        return None, False
    relative = os.path.relpath(resolved_file, resolved_root)
    relative_posix = relative.replace(os.sep, "/")
    return relative_posix, True


def match_globs(relative_posix_path, globs):
    """§4/§6 step 3 — `fnmatch.fnmatch()` only; `*` crosses path separators, `**` has no
    special recursive meaning."""
    for pattern in globs:
        if fnmatch.fnmatch(relative_posix_path, pattern):
            return True
    return False


def get_scan_surface(tool_name, tool_input):
    """§6 step 4 — `tool_input.content` (Write) or `tool_input.new_string` (Edit), taken
    as-is. Never the on-disk file, never an old_string->new_string resolution. Absent/empty
    new_string on an Edit -> "" (matches_found: 0)."""
    if tool_name == "Write":
        content = tool_input.get("content")
    elif tool_name == "Edit":
        content = tool_input.get("new_string")
    else:
        content = None
    if not isinstance(content, str):
        return ""
    return content


def compile_identifier_matcher(identifier):
    """§4 — an identifier entry is a literal substring, or a `re:`-prefixed Python regex
    (case-sensitive). Returns a callable(line) -> bool. A malformed regex is treated as
    never-matching rather than crashing the probe (fail-open posture)."""
    if identifier.startswith("re:"):
        pattern_text = identifier[len("re:") :]
        try:
            compiled = re.compile(pattern_text)
        except re.error:
            return lambda line: False
        return lambda line: compiled.search(line) is not None
    return lambda line: identifier in line


def find_identifier_matches(scan_surface, identifiers):
    """§6 steps 5-6 — scan `scan_surface` line-by-line for any `externalSourceIdentifiers`
    match. Returns a list of (line_index, identifier) tuples, one per matching
    (line, identifier) pair."""
    if not scan_surface or not identifiers:
        return []
    lines = scan_surface.split("\n")
    matchers = [(identifier, compile_identifier_matcher(identifier)) for identifier in identifiers]
    matches = []
    for line_idx, line in enumerate(lines):
        for identifier, matcher in matchers:
            try:
                if matcher(line):
                    matches.append((line_idx, identifier))
            except Exception:
                continue
    return matches


def has_qualifying_marker_in_window(lines, match_line_idx):
    """§5/§6 step 6 — search the 5-line window (inclusive, above and below)
    around `match_line_idx`, within `lines` (the scan surface's own lines), for a
    `DOMAIN-BOUNDARY:` marker line with non-empty trailing content."""
    start = max(0, match_line_idx - PROXIMITY_WINDOW)
    end = min(len(lines) - 1, match_line_idx + PROXIMITY_WINDOW)
    for idx in range(start, end + 1):
        m = _MARKER_RE.search(lines[idx])
        if m and m.group(1) and m.group(1).strip():
            return True
    return False


def _threshold_marker_satisfies(trailing_content):
    """§4 G-2 resolution — trailing content after `THRESHOLD-PROVENANCE:` satisfies the
    check only if it matches the citation form (file path, URL, or DDR-NNNN reference).
    Bare presence (e.g. `PROVISIONAL` or `TODO` alone) does not satisfy, and no
    named-owner alternative exists — owner-name acceptance was removed entirely per
    Danny's ruling (Architecture §4)."""
    return bool(_THRESHOLD_CITATION_RE.search(trailing_content))


def _threshold_marker_on_line(line: str) -> bool:
    """True if `line` carries a qualifying `THRESHOLD-PROVENANCE:` marker (citation-form
    content, per `_threshold_marker_satisfies`)."""
    m = _THRESHOLD_MARKER_RE.search(line)
    if not m or not m.group(1) or not m.group(1).strip():
        return False
    return _threshold_marker_satisfies(m.group(1))


def has_threshold_provenance_marker(lines: list[str], match_line_idx: int) -> bool:
    """Same-line-or-contiguous-block-above rule (Architecture §4, corrected 2026-09-06 —
    replaces the deleted `PROXIMITY_WINDOW_THRESHOLD` fixed symmetric ±2-line window).
    Distinct marker string and a distinct scan rule from the incumbent's
    `has_qualifying_marker_in_window` (same-line-only against `DOMAIN-BOUNDARY:`, no block
    scan at all). This function does not read or depend on the incumbent's
    `PROXIMITY_WINDOW`.

    Recognizes a citation for the flagged literal at `match_line_idx` if and only if a
    qualifying `THRESHOLD-PROVENANCE:` marker is found in either of:
      1. The same line as the flagged literal (a trailing same-line comment).
      2. The contiguous comment block immediately above the literal's line: scanning
         upward from `match_line_idx - 1`, a blank line is scanned through (continues the
         block), a comment line (`#...`) is part of the block and is checked for the
         marker, and the first line that is neither blank nor a comment terminates the
         scan. No maximum block length and no fixed distance cutoff — this matches
         `scan_thresholds.py`'s `_preceding_comment`
         (docs/research/domain-boundary-hook-benchmark/scan_thresholds.py:210-225) exactly,
         not approximately. There is no "below" direction — a marker appearing only below
         the flagged literal does not satisfy the check.

    Per Architecture §4's G-2 resolution: marker presence alone is NOT sufficient — a
    found `THRESHOLD-PROVENANCE:` line must also carry citation-form content (checked by
    `_threshold_marker_on_line`). A bare `THRESHOLD-PROVENANCE: PROVISIONAL` or `...: TODO`
    with no citation is treated as absent, per 01-REQUIREMENTS.md's Edge Case row. No
    named-owner acceptance path exists, per Danny's ruling that no owner-name acceptance
    path is valid, for any constant, ever — see Architecture §4."""
    if match_line_idx < 0 or match_line_idx >= len(lines):
        return False
    if _threshold_marker_on_line(lines[match_line_idx]):
        return True
    idx = match_line_idx - 1
    while idx >= 0:
        stripped = lines[idx].strip()
        if stripped == "":
            idx -= 1
            continue
        if stripped.startswith("#"):
            if _threshold_marker_on_line(lines[idx]):
                return True
            idx -= 1
            continue
        break
    return False


TEST_PATH_COMPONENTS = {"test", "tests", "fixtures"}

# Filename patterns matched in addition to the path-component check above, since a
# component-only check misses `test_foo.py`/`foo_test.py` at repo root (no matching path
# component) and `conftest.py` anywhere.
_TEST_FILENAME_RE = re.compile(r"^(test_.*|.*_test|conftest)\.py$")

_COMPARISON_OPS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)
# Narrowed 2026-09-06: `rjust`, `zfill`, `truncate`, `read`, `head` had no citation and
# no corpus evidence they ever fire — removed rather than kept as unverified guesses.
# `ljust` is kept as a design choice, NOT because it has a corpus hit — it doesn't
# (candidates.jsonl has zero `ljust` matches; its only reference anywhere in this doc
# set is one illustrative example in Architecture §2, and `ljust` pads rather than
# truncates, so even that example is imprecise). Slice syntax (`x[:n]`) is detected
# separately via `_walk_comparison_and_slice_contexts`'s `ast.Subscript`/`ast.Slice`
# handling, not via this set. This is a narrowing to only the members either measured
# or explicitly named in the architecture doc; `ljust`'s presence is not itself
# evidence-backed and should not be cited as if it were.
_TRUNCATION_METHODS = {"ljust"}

# §2.1 strategy 3 — per-line regex fallback, context 3 (module/class-level assignment)
# ONLY. Whole-line match: an optionally type-annotated `NAME = <numeric/bool literal>`,
# trailing comment permitted. Contexts 1-2 have no regex fallback (fail-open by design).
_FRAGMENT_ASSIGN_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*[\w.\[\], ]+)?\s*=\s*"
    r"(-?\d[\d_]*(?:\.\d[\d_]*)?|True|False)\s*(?:#.*)?$"
)


class FlaggedLiteral(TypedDict):
    line_index: int  # 0-based, within scan_surface
    context: str  # "comparison" | "slice_truncation" | "assign_module_or_class"
    literal_repr: str  # e.g. "50000", "True"


def _is_test_or_fixture_path(file_path):
    """§2 exclusion — any `test`/`tests`/`fixtures` path component (checked component-wise
    on the POSIX-normalized path, not a bare substring match), OR a filename matching
    `test_*.py`/`*_test.py`/`conftest.py` — the component-only check misses a test file at
    repo root (e.g. `test_foo.py`, no matching path component) and `conftest.py`."""
    if not isinstance(file_path, str) or not file_path:
        return False
    normalized = file_path.replace(os.sep, "/")
    components = normalized.split("/")
    if any(component in TEST_PATH_COMPONENTS for component in components):
        return True
    basename = components[-1]
    return bool(_TEST_FILENAME_RE.match(basename))


def _literal_value_and_repr(node):
    """Numeric/bool literal, including unary +/-. Returns (value, repr_str, ok)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, bool)):
        return node.value, repr(node.value), True
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, (ast.USub, ast.UAdd))
        and isinstance(node.operand, ast.Constant)
        and isinstance(node.operand.value, (int, float))
        and not isinstance(node.operand.value, bool)
    ):
        value = node.operand.value
        if isinstance(node.op, ast.USub):
            value = -value
        return value, repr(value), True
    return None, None, False


def _walk_comparison_and_slice_contexts(tree):
    """Contexts 1-2 (§2): comparison operand, slice/truncation argument. Extracted via
    `ast.walk` over an already-parsed tree — strategies 1/2 only (no regex fallback for
    these two contexts, per §2.1's robustness table)."""
    flagged = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and any(
            isinstance(op, _COMPARISON_OPS) for op in node.ops
        ):
            for operand in [node.left, *node.comparators]:
                value, value_repr, ok = _literal_value_and_repr(operand)
                if ok and not isinstance(value, bool):
                    flagged.append((operand.lineno - 1, "comparison", value_repr))
        elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            for part in (node.slice.lower, node.slice.upper, node.slice.step):
                if part is None:
                    continue
                value, value_repr, ok = _literal_value_and_repr(part)
                if ok and not isinstance(value, bool):
                    flagged.append((part.lineno - 1, "slice_truncation", value_repr))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _TRUNCATION_METHODS:
                for arg in node.args:
                    value, value_repr, ok = _literal_value_and_repr(arg)
                    if ok and not isinstance(value, bool):
                        flagged.append((arg.lineno - 1, "slice_truncation", value_repr))
    return flagged


def _walk_assignment_context(tree):
    """Context 3 (§2): module-level or class-level `NAME = <literal>` /
    `NAME: T = <literal>`, numeric or boolean, no vocabulary gate, no case restriction.
    Pure-shape rule — module/class body scope only, never inside a function body."""
    flagged = []

    def handle(body):
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        value, value_repr, ok = _literal_value_and_repr(stmt.value)
                        if ok:
                            flagged.append(
                                (stmt.value.lineno - 1, "assign_module_or_class", value_repr)
                            )
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                if stmt.value is not None:
                    value, value_repr, ok = _literal_value_and_repr(stmt.value)
                    if ok:
                        flagged.append(
                            (stmt.value.lineno - 1, "assign_module_or_class", value_repr)
                        )
            elif isinstance(stmt, ast.ClassDef):
                handle(stmt.body)

    handle(tree.body)
    return flagged


def _regex_fallback_assignment_context(scan_surface):
    """§2.1 strategy 3 — per-line regex fallback, context 3 only. Used only once both
    `ast.parse(scan_surface)` and the dedent retry raise `SyntaxError`."""
    flagged = []
    for idx, line in enumerate(scan_surface.split("\n")):
        match = _FRAGMENT_ASSIGN_RE.match(line)
        if not match:
            continue
        raw = match.group(2)
        if raw == "True":
            value_repr = "True"
        elif raw == "False":
            value_repr = "False"
        else:
            try:
                value_repr = repr(float(raw)) if "." in raw else repr(int(raw))
            except ValueError:
                continue
        flagged.append((idx, "assign_module_or_class", value_repr))
    return flagged


def detect_threshold_literals(file_path: str, scan_surface: str) -> list[FlaggedLiteral]:
    """AD-1 detection (Architecture §2/§2.1) — three shape-based contexts: comparison
    operand, slice/truncation argument, and module/class-level named assignment (any
    target name, no vocabulary or case gate). `file_path` is used only for the
    test/fixture path exclusion — never read from disk; operates on `scan_surface` text
    only.

    Parsing (§2.1, fragment-robust, not a single `ast.parse` call):
      1. `ast.parse(scan_surface)`.
      2. On `IndentationError` only: retry `ast.parse(textwrap.dedent(scan_surface))`.
      3. On any remaining `SyntaxError`: fall back to a per-line regex scan for context 3
         (module/class-level assignment) ONLY — contexts 1-2 have no regex fallback and
         yield no candidates for an unparsable fragment (fail-open).

    No literal-value exclusion set exists in this design (removed 2026-09-05, §2
    disposition) — all threshold-shaped literals from all three contexts, including
    0/1/-1/2, are flagged unfiltered.
    """
    if _is_test_or_fixture_path(file_path):
        return []
    if not scan_surface:
        return []

    tree = None
    try:
        tree = ast.parse(scan_surface)
    except IndentationError:
        try:
            tree = ast.parse(textwrap.dedent(scan_surface))
        except SyntaxError:
            tree = None
    except SyntaxError:
        tree = None

    if tree is not None:
        raw_flags = _walk_comparison_and_slice_contexts(tree)
        raw_flags += _walk_assignment_context(tree)
    else:
        raw_flags = _regex_fallback_assignment_context(scan_surface)

    flagged = [
        FlaggedLiteral(line_index=line_index, context=context, literal_repr=literal_repr)
        for line_index, context, literal_repr in raw_flags
    ]
    return flagged


def write_track_record(project_dir, entry):
    track_record_path = os.path.join(project_dir, TRACK_RECORD_RELATIVE_PATH)
    try:
        os.makedirs(os.path.dirname(track_record_path), exist_ok=True)
        with open(track_record_path, "a") as fh:
            fh.write(json.dumps(entry) + "\n")
    except Exception:
        # The track record is an audit trail, not a gate — a write failure here must not
        # change or block the probe's decision to Claude Code.
        pass


def build_track_record_entry(
    session_id,
    tool_name,
    file_path,
    mode,
    cross_domain,
    local_threshold,
    decision,
    reason,
    probe_error,
):
    """Architecture §6 — nested `cross_domain`/`local_threshold` shape (breaking, clean
    cutover migration, Slice 7). `cross_domain` and `local_threshold` are already-shaped
    dicts (see `_cross_domain_entry`/`_local_threshold_entry` and their `_default_*`
    counterparts below), not `PassResult`s — callers build the entry-shaped dict first."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "tool_name": tool_name,
        "file_path": file_path,
        "mode": mode,
        "cross_domain": cross_domain,
        "local_threshold": local_threshold,
        "decision": decision,
        "reason": reason,
        "probe_error": probe_error,
    }


def _cross_domain_entry(result):
    """Maps a `run_cross_domain_pass` `PassResult` to §6's `cross_domain` nested shape."""
    detail = result["detail"]
    return {
        "manifest_status": detail["manifest_status"],
        "file_in_scope": detail["file_in_scope"],
        "matches_found": result["matches_found"],
        "matches_cited": result["matches_cited"],
    }


def _local_threshold_entry(result):
    """Maps a `run_local_threshold_pass` `PassResult` to §6's `local_threshold` nested
    shape."""
    detail = result["detail"]
    return {
        "file_scanned": detail["file_scanned"],
        "matches_found": result["matches_found"],
        "matches_cited": result["matches_cited"],
    }


def _default_cross_domain_entry():
    """§6 nested defaults for invocations where the cross-domain pass never ran (early
    non-Edit/Write allow, probe_error)."""
    return {
        "manifest_status": "absent_or_invalid",
        "file_in_scope": None,
        "matches_found": None,
        "matches_cited": None,
    }


def _default_local_threshold_entry():
    """§6 nested defaults for invocations where the local-threshold pass never ran (early
    non-Edit/Write allow, probe_error)."""
    return {
        "file_scanned": False,
        "matches_found": None,
        "matches_cited": None,
    }


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def emit_allow():
    # Silence-means-allow, same convention as the sibling probe.
    pass


def build_deny_reason(file_path, unmarked_matches):
    """§6 step 8 — reason lists every unmarked identifier match (file, line, matched
    identifier) and the exact remediation."""
    lines_desc = ", ".join(
        f'line {idx + 1} (matched "{identifier}")' for idx, identifier in unmarked_matches
    )
    return (
        f"Domain-boundary provenance violation in {file_path}: "
        f"{lines_desc} — no qualifying `DOMAIN-BOUNDARY:` marker within {PROXIMITY_WINDOW} "
        f"lines. Add a `DOMAIN-BOUNDARY: <rationale>` comment within {PROXIMITY_WINDOW} "
        f"lines of the flagged read."
    )


class PassResult(TypedDict):
    ran: bool
    matches_found: int | None
    matches_cited: int | None
    unmarked: list[tuple[int, str]]
    detail: dict


def run_cross_domain_pass(project_dir, tool_input, scan_surface) -> PassResult:
    """Incumbent's existing steps 2-7 (manifest load, normalize, glob match, identifier scan,
    DOMAIN-BOUNDARY: window check), extracted verbatim into a function, no logic change.

    Returns a PassResult dict: `ran`, `matches_found`, `matches_cited`, `unmarked`, `detail`.
    `detail` carries the incumbent's own per-step track-record fields (`manifest_status`,
    `file_in_scope`, `relative_path`) so callers can reconstruct the exact prior track-record
    entry shape.
    """
    raw_file_path = tool_input.get("file_path")

    # §6 step 2.
    manifest, manifest_status = load_manifest(project_dir)
    if manifest is None:
        return {
            "ran": False,
            "matches_found": None,
            "matches_cited": None,
            "unmarked": [],
            "detail": {
                "manifest_status": "absent_or_invalid",
                "file_in_scope": None,
                "relative_path": raw_file_path,
            },
        }

    # §6 step 3.
    relative_path, in_repo = normalize_file_path(project_dir, raw_file_path)
    if not in_repo:
        return {
            "ran": False,
            "matches_found": None,
            "matches_cited": None,
            "unmarked": [],
            "detail": {
                "manifest_status": "matched",
                "file_in_scope": False,
                "relative_path": raw_file_path,
            },
        }

    globs = manifest.get("pipelineConfigGlobs") or []
    if not match_globs(relative_path, globs):
        return {
            "ran": False,
            "matches_found": None,
            "matches_cited": None,
            "unmarked": [],
            "detail": {
                "manifest_status": "matched",
                "file_in_scope": False,
                "relative_path": relative_path,
            },
        }

    # §6 step 4.
    if not scan_surface:
        return {
            "ran": True,
            "matches_found": 0,
            "matches_cited": 0,
            "unmarked": [],
            "detail": {
                "manifest_status": "matched",
                "file_in_scope": True,
                "relative_path": relative_path,
            },
        }

    # §6 steps 5-7.
    identifiers = manifest.get("externalSourceIdentifiers") or []
    matches = find_identifier_matches(scan_surface, identifiers)
    if not matches:
        return {
            "ran": True,
            "matches_found": 0,
            "matches_cited": 0,
            "unmarked": [],
            "detail": {
                "manifest_status": "matched",
                "file_in_scope": True,
                "relative_path": relative_path,
            },
        }

    lines = scan_surface.split("\n")
    unmarked = [
        (idx, identifier)
        for idx, identifier in matches
        if not has_qualifying_marker_in_window(lines, idx)
    ]

    return {
        "ran": True,
        "matches_found": len(matches),
        "matches_cited": len(matches) - len(unmarked),
        "unmarked": unmarked,
        "detail": {
            "manifest_status": "matched",
            "file_in_scope": True,
            "relative_path": relative_path,
        },
    }


def run_local_threshold_pass(tool_name, raw_file_path, scan_surface, mode) -> PassResult:
    """New (Architecture §7). Gated on: `raw_file_path` ends with `.py`, and no path
    component is test/tests/fixtures (§2 exclusion). Not gated by manifest presence.

    Composes `detect_threshold_literals` (§2/§2.1) with `has_threshold_provenance_marker`
    (§4) to determine which flagged literals are cited and which are not. `mode` is
    accepted per the §7 signature but is not consulted here — the mode-based deny->flag
    downgrade happens only in `combine()` (Slice 6), per Architecture §3's pseudocode.
    """
    if not isinstance(raw_file_path, str) or not raw_file_path.endswith(".py"):
        return {
            "ran": False,
            "matches_found": None,
            "matches_cited": None,
            "unmarked": [],
            "detail": {"file_scanned": False, "file_path": raw_file_path},
        }

    if _is_test_or_fixture_path(raw_file_path):
        return {
            "ran": False,
            "matches_found": None,
            "matches_cited": None,
            "unmarked": [],
            "detail": {"file_scanned": False, "file_path": raw_file_path},
        }

    flagged = detect_threshold_literals(raw_file_path, scan_surface)
    if not flagged:
        return {
            "ran": True,
            "matches_found": 0,
            "matches_cited": 0,
            "unmarked": [],
            "detail": {"file_scanned": True, "file_path": raw_file_path},
        }

    lines = scan_surface.split("\n")
    unmarked = [
        (literal["line_index"], literal["literal_repr"])
        for literal in flagged
        if not has_threshold_provenance_marker(lines, literal["line_index"])
    ]

    return {
        "ran": True,
        "matches_found": len(flagged),
        "matches_cited": len(flagged) - len(unmarked),
        "unmarked": unmarked,
        "detail": {"file_scanned": True, "file_path": raw_file_path},
    }


def build_local_threshold_deny_reason(file_path, unmarked_matches):
    """Local-threshold-pass analog of `build_deny_reason` (§7) — reason lists every unmarked
    threshold-shaped literal (line, literal text) and the exact remediation."""
    lines_desc = ", ".join(
        f'line {idx + 1} (literal "{literal_repr}")' for idx, literal_repr in unmarked_matches
    )
    return (
        f"Threshold-provenance violation in {file_path}: {lines_desc} — no qualifying "
        f"`THRESHOLD-PROVENANCE:` marker with a citation on the flagged literal's own line "
        f"or in the contiguous comment block immediately above it. Add a "
        f"`THRESHOLD-PROVENANCE: <file path, URL, or DDR-NNNN citation>` comment on that "
        f"line or directly above the flagged literal."
    )


class CombinedResult(TypedDict):
    decision: str  # "allow" | "flag" | "deny"
    reason: str | None


def combine(cross_domain: PassResult, local_threshold: PassResult, mode: str) -> CombinedResult:
    """Architecture §3's combination rule.

    `mode="log_only"`: any pass that would otherwise deny (has unmarked matches) is downgraded
    to a track-record `decision: "flag"` entry; the `PreToolUse` call always emits allow
    (nothing) — this is the F1 behavior change (Frank spec-gate attempt 1): the incumbent's
    LOCKED doc's unconditional cross-domain "deny" now only actually denies under
    `mode == "blocking"`.

    `mode="blocking"`: denies if EITHER pass has unmarked matches. If both passes deny, the
    `reason` string concatenates both, each clearly labeled (`[domain-boundary]` /
    `[threshold-provenance]`) so remediation is unambiguous about which marker is missing
    where. If only one pass denies, that pass's reason is used — labeled for consistency with
    the two-pass-deny case, rather than switching format based on how many passes fired
    (Architecture §3's own note: "flag choice in code comment, not a spec deviation" when the
    exact wording is ambiguous between labeled/unlabeled for the single-deny case).
    """
    cross_domain_denies = bool(cross_domain.get("unmarked"))
    local_threshold_denies = bool(local_threshold.get("unmarked"))

    if not cross_domain_denies and not local_threshold_denies:
        return {"decision": "allow", "reason": None}

    # Fail-safe default (QC advisory): any mode other than exactly "blocking" — including
    # unrecognized/typo'd values — is treated as "log_only", not the blocking branch.
    if mode != "blocking":
        return {"decision": "flag", "reason": None}

    # mode == "blocking" from here.
    reasons = []
    if cross_domain_denies:
        cd_file_path = cross_domain.get("detail", {}).get("relative_path")
        cd_reason = build_deny_reason(cd_file_path, cross_domain["unmarked"])
        reasons.append(f"[domain-boundary] {cd_reason}")
    if local_threshold_denies:
        lt_file_path = local_threshold.get("detail", {}).get("file_path")
        lt_reason = build_local_threshold_deny_reason(lt_file_path, local_threshold["unmarked"])
        reasons.append(f"[threshold-provenance] {lt_reason}")

    return {"decision": "deny", "reason": "\n".join(reasons)}


def run(stdin_data):
    """Architecture §3's restructured procedure (Slice 7): extract tool_name/tool_input/
    project_dir -> early-allow on non-Edit/Write -> get_scan_surface (unchanged) -> both
    passes -> combine() -> single write_track_record(combined) -> emit. `mode` is read
    once, here, via `load_mode_config()`, and passed as a plain argument into `combine()` —
    it is not re-read anywhere else (Architecture §8's disposition of G-7)."""
    session_id = stdin_data.get("session_id")
    tool_name = stdin_data.get("tool_name")
    tool_input = stdin_data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    project_dir = get_project_dir(stdin_data)
    mode = load_mode_config(project_dir)

    # §6 step 1 (incumbent doc) / Architecture §3 pseudocode.
    if tool_name not in ("Edit", "Write"):
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                None,
                mode,
                _default_cross_domain_entry(),
                _default_local_threshold_entry(),
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    raw_file_path = tool_input.get("file_path")

    # Scan surface computed once, reused by both passes (unchanged helper).
    scan_surface = get_scan_surface(tool_name, tool_input)

    cross_domain_result = run_cross_domain_pass(project_dir, tool_input, scan_surface)
    local_threshold_result = run_local_threshold_pass(tool_name, raw_file_path, scan_surface, mode)

    combined = combine(cross_domain_result, local_threshold_result, mode)

    cd_detail = cross_domain_result["detail"]
    relative_path = cd_detail.get("relative_path")
    file_path = relative_path if relative_path is not None else raw_file_path

    write_track_record(
        project_dir,
        build_track_record_entry(
            session_id,
            tool_name,
            file_path,
            mode,
            _cross_domain_entry(cross_domain_result),
            _local_threshold_entry(local_threshold_result),
            combined["decision"],
            combined["reason"],
            None,
        ),
    )

    if combined["decision"] == "deny":
        emit_block(combined["reason"])
    else:
        emit_allow()


def main():
    stdin_data = read_stdin()
    try:
        run(stdin_data)
    except Exception as exc:  # noqa: BLE001 — this probe must never crash into a block
        project_dir = get_project_dir(stdin_data)
        write_track_record(
            project_dir,
            build_track_record_entry(
                stdin_data.get("session_id"),
                stdin_data.get("tool_name"),
                None,
                load_mode_config(project_dir),
                _default_cross_domain_entry(),
                _default_local_threshold_entry(),
                "probe_error",
                None,
                f"{exc.__class__.__name__}: {exc}",
            ),
        )
        emit_allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
