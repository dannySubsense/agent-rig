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

import fnmatch
import json
import os
import re
import sys
from datetime import datetime, timezone

TRACK_RECORD_RELATIVE_PATH = os.path.join(
    "docs", "tooling", "domain-boundary-provenance-track-record.jsonl"
)
MANIFEST_RELATIVE_PATH = os.path.join("docs", "tooling", "domain-boundary-manifest.json")

# §5 — the citation marker; a qualifying line has this literal string followed by
# non-whitespace content on the same line.
MARKER = "DOMAIN-BOUNDARY:"
_MARKER_RE = re.compile(re.escape(MARKER) + r"\s*(\S.*)?$")

# §5 — PROVISIONAL, owner: wright. Proximity window (lines) above/below a match, inclusive.
PROXIMITY_WINDOW = 5


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
    """§5/§6 step 6 — search the PROVISIONAL 5-line window (inclusive, above and below)
    around `match_line_idx`, within `lines` (the scan surface's own lines), for a
    `DOMAIN-BOUNDARY:` marker line with non-empty trailing content."""
    start = max(0, match_line_idx - PROXIMITY_WINDOW)
    end = min(len(lines) - 1, match_line_idx + PROXIMITY_WINDOW)
    for idx in range(start, end + 1):
        m = _MARKER_RE.search(lines[idx])
        if m and m.group(1) and m.group(1).strip():
            return True
    return False


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
    manifest_status,
    file_in_scope,
    matches_found,
    matches_cited,
    decision,
    reason,
    probe_error,
):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "tool_name": tool_name,
        "file_path": file_path,
        "manifest_status": manifest_status,
        "file_in_scope": file_in_scope,
        "matches_found": matches_found,
        "matches_cited": matches_cited,
        "decision": decision,
        "reason": reason,
        "probe_error": probe_error,
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


def run(stdin_data):
    session_id = stdin_data.get("session_id")
    tool_name = stdin_data.get("tool_name")
    tool_input = stdin_data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    project_dir = get_project_dir(stdin_data)

    # §6 step 1.
    if tool_name not in ("Edit", "Write"):
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                None,
                "absent_or_invalid",
                None,
                None,
                None,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    raw_file_path = tool_input.get("file_path")

    # §6 step 2.
    manifest, manifest_status = load_manifest(project_dir)
    if manifest is None:
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                raw_file_path,
                "absent_or_invalid",
                None,
                None,
                None,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    # §6 step 3.
    relative_path, in_repo = normalize_file_path(project_dir, raw_file_path)
    if not in_repo:
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                raw_file_path,
                "matched",
                False,
                None,
                None,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    globs = manifest.get("pipelineConfigGlobs") or []
    if not match_globs(relative_path, globs):
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                relative_path,
                "matched",
                False,
                None,
                None,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    # §6 step 4.
    scan_surface = get_scan_surface(tool_name, tool_input)
    if not scan_surface:
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                relative_path,
                "matched",
                True,
                0,
                0,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    # §6 steps 5-7.
    identifiers = manifest.get("externalSourceIdentifiers") or []
    matches = find_identifier_matches(scan_surface, identifiers)
    if not matches:
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                relative_path,
                "matched",
                True,
                0,
                0,
                "allow",
                None,
                None,
            ),
        )
        emit_allow()
        return

    lines = scan_surface.split("\n")
    unmarked = [
        (idx, identifier)
        for idx, identifier in matches
        if not has_qualifying_marker_in_window(lines, idx)
    ]

    if unmarked:
        reason = build_deny_reason(relative_path, unmarked)
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id,
                tool_name,
                relative_path,
                "matched",
                True,
                len(matches),
                len(matches) - len(unmarked),
                "deny",
                reason,
                None,
            ),
        )
        emit_block(reason)
        return

    write_track_record(
        project_dir,
        build_track_record_entry(
            session_id,
            tool_name,
            relative_path,
            "matched",
            True,
            len(matches),
            len(matches),
            "allow",
            None,
            None,
        ),
    )
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
                "absent_or_invalid",
                None,
                None,
                None,
                "probe_error",
                None,
                f"{exc.__class__.__name__}: {exc}",
            ),
        )
        emit_allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
