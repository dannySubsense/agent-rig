#!/usr/bin/env python3
"""PreToolUse hook — PROGRESS.md proof-per-slice check (probe core).

Reads `PreToolUse` stdin JSON (`tool_name`, `tool_input`, `session_id`, `cwd`) and decides
whether an `Edit` call flipping a `PROGRESS.md` slice checkbox from `- [ ]` to `- [x]` may
proceed, per the identity-based matching procedure in
docs/tooling/progress-md-proof-per-slice-hook/SPEC.md §6 (redesigned 2026-08-23):

  1. Non-`Edit` tool_name -> allow.
  2. `tool_input.file_path` basename not matching `*PROGRESS.md` (fnmatch) -> allow.
  3. `old_string`/`new_string` absent -> allow.
  4. Extract candidate slice lines independently from `old_string` (`- [ ]` lines) and
     `new_string` (`- [x]` lines). Never compared by array index/position.
  4a. SLICE-ID matching pass (authoritative when a token is present and unique on both
      sides) — no mutation-deny path.
  5. Duplicate-description ambiguity check (per remaining pool) -> deny conservatively.
  6. Description-primary matching (C1 proof-unchanged / C2 proof-mutated), then
     proof-identity-secondary matching (always C2, description-mutated).
  7-11. No matched pairs -> allow. Each matched pair: extract PROOF: (opt-in), allowlist
      check (manual_unverified if not allowlisted), execute if allowlisted (verified_pass/
      verified_fail/verified_timeout). Any denied pair denies the whole edit; reasons
      concatenate.

Emits the deny shape Claude Code's `PreToolUse` hook understands: top-level
`{"decision": "block", "reason": ...}`, or nothing (silence means allow). Appends one entry
per invocation to the gitignored track-record log (§7's TrackRecordEntry shape).

Pure function of stdin plus the allowlist file and (for allowlisted commands only) shell
execution. Never blocks on its own failure — any exception here is caught and treated as an
allow, with a `probe_error` track-record entry (the wrapper's own timeout/non-zero-exit
fail-open is the outer guarantee; this is this probe's inner one).
"""

import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

TRACK_RECORD_RELATIVE_PATH = os.path.join(
    "docs", "tooling", "progress-proof-per-slice-track-record.jsonl"
)
ALLOWLIST_RELATIVE_PATH = os.path.join("docs", "tooling", "progress-proof-allowlist.json")

CHECKBOX_OPEN = "- [ ]"
CHECKBOX_DONE = "- [x]"
SEGMENT_SEP = " — "
PROOF_PREFIX = "PROOF:"
SLICE_ID_PREFIX = "SLICE-ID:"

# §6 — PROVISIONAL, owner: wright. Inner proof-command execution timeout, seconds.
INNER_TIMEOUT = 25

STDERR_TAIL_MAX = 2000

_uid_counter = [0]


def _next_uid():
    _uid_counter[0] += 1
    return _uid_counter[0]


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
    """Repo root: `$CLAUDE_PROJECT_DIR`, falling back to stdin's `cwd` if unset."""
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return env_dir
    cwd = stdin_data.get("cwd")
    if isinstance(cwd, str) and cwd:
        return cwd
    return os.getcwd()


def load_allowlist(project_dir):
    """§5/§6 step 9 — load and minimally validate the allowlist. Absent/unreadable/invalid
    -> empty list (every PROOF: command falls through to manual_unverified, same posture as
    "no manifest present" in the sibling hook)."""
    allowlist_path = os.path.join(project_dir, ALLOWLIST_RELATIVE_PATH)
    try:
        with open(allowlist_path, "r") as fh:
            raw = fh.read()
    except Exception:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    if not isinstance(data, dict):
        return []
    if data.get("schemaVersion") != 1:
        return []
    prefixes = data.get("allowedCommandPrefixes")
    if not isinstance(prefixes, list) or not all(isinstance(p, str) for p in prefixes):
        return []
    return prefixes


def is_allowlisted(command, prefixes):
    """§5 — exact-prefix match against the command's leading substring, after stripping
    leading/trailing whitespace from the full command."""
    stripped = command.strip()
    for prefix in prefixes:
        if stripped.startswith(prefix):
            return True
    return False


def parse_segments(rest_text):
    """Parse the text following the checkbox marker into (description, slice_id,
    proof_segment) per §4. `rest_text` has already had the checkbox marker stripped."""
    rest_text = rest_text.strip()
    segments = rest_text.split(SEGMENT_SEP)
    description = segments[0].strip() if segments else ""
    n = len(segments)
    proof_segment = None
    proof_index = None
    if n > 0:
        last = segments[-1].strip()
        if last.startswith(PROOF_PREFIX):
            proof_segment = last
            proof_index = n - 1
    slice_id = None
    for i, seg in enumerate(segments):
        if i == 0:
            continue
        if proof_index is not None and i == proof_index:
            continue
        s = seg.strip()
        if s.startswith(SLICE_ID_PREFIX):
            slice_id = s[len(SLICE_ID_PREFIX):].strip()
    return description, slice_id, proof_segment


def extract_candidates(text, checkbox_marker):
    """§6 step 4 — extract candidate slice lines from `text` (either `old_string` or
    `new_string`) whose stripped content starts with `checkbox_marker`. Each candidate:
    {uid, description, slice_id, proof_segment, full_line}."""
    candidates = []
    if not isinstance(text, str):
        return candidates
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped.startswith(checkbox_marker):
            continue
        rest = stripped[len(checkbox_marker):]
        description, slice_id, proof_segment = parse_segments(rest)
        candidates.append(
            {
                "uid": _next_uid(),
                "description": description,
                "slice_id": slice_id,
                "proof_segment": proof_segment,
                "full_line": line,
            }
        )
    return candidates


def group_by(candidates, key):
    groups = {}
    for c in candidates:
        k = c.get(key)
        if k is None:
            continue
        groups.setdefault(k, []).append(c)
    return groups


def remove_candidate(pool, candidate):
    for i, c in enumerate(pool):
        if c["uid"] == candidate["uid"]:
            del pool[i]
            return


def extract_proof_command(proof_segment):
    """Extract the trailing command text (trimmed) after the `PROOF:` marker."""
    if proof_segment is None:
        return None
    return proof_segment[len(PROOF_PREFIX):].strip()


def run_proof_command(command, project_dir):
    """§6 step 10 — execute an allowlisted command. Returns
    (proof_status, stderr_tail_or_none, exit_code_or_none)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_dir,
            timeout=INNER_TIMEOUT,
            capture_output=True,
            text=True,
        )
    except subprocess.TimeoutExpired:
        return "verified_timeout", None, None
    except Exception as exc:  # command could not even be launched
        return "verified_fail", f"{exc.__class__.__name__}: {exc}"[:STDERR_TAIL_MAX], None
    if result.returncode == 0:
        return "verified_pass", None, 0
    stderr_tail = (result.stderr or "")[-STDERR_TAIL_MAX:]
    return "verified_fail", stderr_tail, result.returncode


def resolve_pair_proof(new_c, allowlist, project_dir):
    """§6 steps 8-10 for a single C1-eligible matched pair (slice_id match or description
    C1 match). Returns (proof_status_or_none, deny_reason_or_none, exit_code_or_none,
    stderr_tail_or_none)."""
    proof_segment = new_c["proof_segment"]
    if proof_segment is None:
        # §6 step 8 — opt-in, no PROOF: marker on the completed side -> allowed, no status.
        return None, None, None, None
    command = extract_proof_command(proof_segment)
    if not is_allowlisted(command, allowlist):
        return "manual_unverified", None, None, None
    proof_status, stderr_tail, exit_code = run_proof_command(command, project_dir)
    if proof_status == "verified_pass":
        return proof_status, None, exit_code, None
    if proof_status == "verified_timeout":
        reason = (
            f"Slice '{new_c['description']}': PROOF command timed out after "
            f"{INNER_TIMEOUT}s. line: {new_c['full_line']!r} cmd: {command!r}. "
            f"Fix the failing command, or don't mark this slice '[x]' yet."
        )
        return proof_status, reason, None, None
    reason = (
        f"Slice '{new_c['description']}': PROOF command failed. "
        f"line: {new_c['full_line']!r} cmd: {command!r} exit_code={exit_code} "
        f"stderr_tail: {stderr_tail!r}. Fix the failing command, or don't mark this slice "
        f"'[x]' yet."
    )
    return proof_status, reason, exit_code, stderr_tail


def decide(old_string, new_string, allowlist, project_dir):
    """§6 steps 4-11 — full identity-based matching + decision procedure. Returns a dict
    with transitions_found, transitions_verified, matched_by, proof_status, decision,
    reason."""
    old_candidates = extract_candidates(old_string, CHECKBOX_OPEN)
    new_candidates = extract_candidates(new_string, CHECKBOX_DONE)

    if not old_candidates and not new_candidates:
        return {
            "transitions_found": 0,
            "transitions_verified": 0,
            "matched_by": None,
            "proof_status": None,
            "decision": "allow",
            "reason": None,
        }

    old_pool = list(old_candidates)
    new_pool = list(new_candidates)

    events = []  # each: {"decision":..., "matched_by":..., "proof_status":..., "reason":...}

    # --- Step 4a: SLICE-ID matching pass ---
    old_id_groups = group_by(old_pool, "slice_id")
    new_id_groups = group_by(new_pool, "slice_id")
    all_tokens = set(old_id_groups) | set(new_id_groups)
    for token in sorted(all_tokens):
        olds = old_id_groups.get(token, [])
        news = new_id_groups.get(token, [])
        if not olds or not news:
            continue
        if len(olds) > 1 or len(news) > 1:
            reason = (
                f"SLICE-ID '{token}' is ambiguous: more than one slice line shares this "
                f"token in this edit. Make each slice's SLICE-ID unique before marking "
                f"either '[x]'."
            )
            events.append(
                {
                    "decision": "deny",
                    "matched_by": None,
                    "proof_status": "ambiguous_match_denied",
                    "reason": reason,
                }
            )
            for c in olds:
                remove_candidate(old_pool, c)
            for c in news:
                remove_candidate(new_pool, c)
            continue
        old_c, new_c = olds[0], news[0]
        proof_status, deny_reason, _exit_code, _stderr = resolve_pair_proof(
            new_c, allowlist, project_dir
        )
        if deny_reason is not None:
            events.append(
                {
                    "decision": "deny",
                    "matched_by": "slice_id",
                    "proof_status": proof_status,
                    "reason": deny_reason,
                }
            )
        else:
            events.append(
                {
                    "decision": "allow",
                    "matched_by": "slice_id",
                    "proof_status": proof_status,
                    "reason": None,
                }
            )
        remove_candidate(old_pool, old_c)
        remove_candidate(new_pool, new_c)

    # --- Step 5: duplicate-description ambiguity check (remaining pool) ---
    old_desc_groups = group_by(old_pool, "description")
    new_desc_groups = group_by(new_pool, "description")
    ambiguous_descs = set()
    for desc, olds in old_desc_groups.items():
        news = new_desc_groups.get(desc, [])
        if len(olds) > 1 and len(news) >= 1:
            ambiguous_descs.add(desc)
    for desc, news in new_desc_groups.items():
        olds = old_desc_groups.get(desc, [])
        if len(news) > 1 and len(olds) >= 1:
            ambiguous_descs.add(desc)

    for desc in sorted(ambiguous_descs):
        reason = (
            f"Description segment '{desc}' is ambiguous: more than one slice line shares "
            f"this description in this edit. Make each slice's description unique before "
            f"marking either '[x]'."
        )
        events.append(
            {
                "decision": "deny",
                "matched_by": None,
                "proof_status": "ambiguous_match_denied",
                "reason": reason,
            }
        )
        for c in old_desc_groups.get(desc, []):
            remove_candidate(old_pool, c)
        for c in new_desc_groups.get(desc, []):
            remove_candidate(new_pool, c)

    # --- Step 6: description-primary matching ---
    old_desc_groups = group_by(old_pool, "description")
    new_desc_groups = group_by(new_pool, "description")
    for desc, olds in list(old_desc_groups.items()):
        news = new_desc_groups.get(desc, [])
        if len(olds) != 1 or len(news) != 1:
            continue
        old_c, new_c = olds[0], news[0]
        old_proof = old_c["proof_segment"]
        new_proof = new_c["proof_segment"]
        if old_proof is None or old_proof == new_proof:
            # C1 — matching transition.
            proof_status, deny_reason, _exit_code, _stderr = resolve_pair_proof(
                new_c, allowlist, project_dir
            )
            if deny_reason is not None:
                events.append(
                    {
                        "decision": "deny",
                        "matched_by": "description",
                        "proof_status": proof_status,
                        "reason": deny_reason,
                    }
                )
            else:
                events.append(
                    {
                        "decision": "allow",
                        "matched_by": "description",
                        "proof_status": proof_status,
                        "reason": None,
                    }
                )
        else:
            # C2 — mismatched transition (PROOF changed or removed).
            reason = (
                f"Slice '{desc}': PROOF: segment altered or removed during completion "
                f"edit. Mark this slice complete in a separate edit from any proof-command "
                f"change."
            )
            events.append(
                {
                    "decision": "deny",
                    "matched_by": "description",
                    "proof_status": "mutation_denied",
                    "reason": reason,
                }
            )
        remove_candidate(old_pool, old_c)
        remove_candidate(new_pool, new_c)

    # --- Step 6 (continued): proof-identity secondary matching ---
    remaining_old_with_proof = [c for c in old_pool if c["proof_segment"] is not None]
    for old_c in remaining_old_with_proof:
        match = None
        for new_c in new_pool:
            if new_c["proof_segment"] == old_c["proof_segment"]:
                match = new_c
                break
        if match is None:
            continue
        command = extract_proof_command(old_c["proof_segment"])
        reason = (
            f"Slice '{old_c['description']}' (matched by unchanged PROOF: command "
            f"{command!r}): description segment altered during completion edit. Mark this "
            f"slice complete in a separate edit from any proof-command change."
        )
        events.append(
            {
                "decision": "deny",
                "matched_by": "proof_identity",
                "proof_status": "mutation_denied",
                "reason": reason,
            }
        )
        remove_candidate(old_pool, old_c)
        remove_candidate(new_pool, match)

    if not events:
        return {
            "transitions_found": 0,
            "transitions_verified": 0,
            "matched_by": None,
            "proof_status": None,
            "decision": "allow",
            "reason": None,
        }

    overall_decision = "deny" if any(e["decision"] == "deny" for e in events) else "allow"
    transitions_found = len(events)
    transitions_verified = sum(1 for e in events if e["proof_status"] == "verified_pass")
    reasons = [e["reason"] for e in events if e["reason"]]
    reason = " | ".join(reasons) if reasons else None
    last_event = events[-1]

    return {
        "transitions_found": transitions_found,
        "transitions_verified": transitions_verified,
        "matched_by": last_event["matched_by"],
        "proof_status": last_event["proof_status"],
        "decision": overall_decision,
        "reason": reason,
    }


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
    file_path,
    file_in_scope,
    transitions_found,
    transitions_verified,
    matched_by,
    proof_status,
    decision,
    reason,
    probe_error,
):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "file_path": file_path,
        "file_in_scope": file_in_scope,
        "transitions_found": transitions_found,
        "transitions_verified": transitions_verified,
        "matched_by": matched_by,
        "proof_status": proof_status,
        "decision": decision,
        "reason": reason,
        "probe_error": probe_error,
    }


def emit_block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def emit_allow():
    # Silence-means-allow, same convention as the sibling probe.
    pass


def run(stdin_data):
    session_id = stdin_data.get("session_id")
    tool_name = stdin_data.get("tool_name")
    tool_input = stdin_data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}
    project_dir = get_project_dir(stdin_data)

    # §6 step 1.
    if tool_name != "Edit":
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id, None, None, None, None, None, None, "allow", None, None
            ),
        )
        emit_allow()
        return

    raw_file_path = tool_input.get("file_path")

    # §6 step 2.
    basename = os.path.basename(raw_file_path) if isinstance(raw_file_path, str) else ""
    if not fnmatch.fnmatch(basename, "*PROGRESS.md"):
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id, raw_file_path, False, None, None, None, None, "allow", None, None
            ),
        )
        emit_allow()
        return

    # §6 step 3.
    old_string = tool_input.get("old_string")
    new_string = tool_input.get("new_string")
    if old_string is None or new_string is None:
        write_track_record(
            project_dir,
            build_track_record_entry(
                session_id, raw_file_path, True, None, None, None, None, "allow", None, None
            ),
        )
        emit_allow()
        return

    allowlist = load_allowlist(project_dir)

    # §6 steps 4-11.
    result = decide(old_string, new_string, allowlist, project_dir)

    write_track_record(
        project_dir,
        build_track_record_entry(
            session_id,
            raw_file_path,
            True,
            result["transitions_found"],
            result["transitions_verified"],
            result["matched_by"],
            result["proof_status"],
            result["decision"],
            result["reason"],
            None,
        ),
    )

    if result["decision"] == "deny":
        emit_block(result["reason"])
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
                None,
                None,
                None,
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
