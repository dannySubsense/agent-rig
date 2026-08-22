#!/usr/bin/env bash
# PreToolUse — domain-boundary provenance check (wrapper).
# Captures stdin, replays it to scripts/domain_boundary_provenance_probe.py under a bounded
# timeout, validates the output shape, and fails open on every failure mode. A PreToolUse hook
# whose only power is to block must, on any error, emit nothing — see
# docs/tooling/domain-boundary-provenance-hook.md §6/§9.
# Structurally identical to .claude/hooks/first-turn-contract.sh — this repo's established
# wrapper/probe shape, reused verbatim (spec §11).
set -uo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR" || exit 0

# §6 step 2/3 rely on $CLAUDE_PROJECT_DIR to locate the target repo's manifest and to resolve
# tool_input.file_path against the correct repo root. The probe falls back to stdin's `cwd` or
# os.getcwd() if the env var is unset, but that fallback is a silent-allow convenience for
# ad-hoc/manual invocation only — a real installed hook must not rely on it. Guarantee the env
# var is set for this invocation: if Claude Code did not already set it, default it to this
# wrapper's own resolved repo root (agent-rig, since that's the only repo this hook is
# installed in per this sprint's scope, spec §2).
export CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$REPO_DIR}"

STDIN_FILE="$(mktemp)"
STDOUT_FILE="$(mktemp)"
STDERR_FILE="$(mktemp)"
trap 'rm -f "$STDIN_FILE" "$STDOUT_FILE" "$STDERR_FILE"' EXIT

# Capture the hook's stdin (session_id, tool_name, tool_input, cwd, etc.) and replay it to the
# probe.
cat >"$STDIN_FILE"

# Write a probe_error TrackRecordEntry (spec §7 exact schema) ourselves, for any path where the
# probe did not get the chance to write its own — non-zero exit, timeout kill, not-executable,
# or output that doesn't validate as JSON/shape (which means it never reached emit_block/
# emit_allow either). On a clean exit-0 run the probe's own run()/main() already wrote a line
# (allow, deny, or its own probe_error) — this function must not run on that path, or it would
# double-log. Never lets a failure here affect the wrapper's own exit code.
write_probe_error() {
  local cause="$1"
  python3 - "$CLAUDE_PROJECT_DIR" "$STDIN_FILE" "$cause" <<'PYEOF' || true
import json
import os
import sys
from datetime import datetime, timezone

project_dir, stdin_path, cause = sys.argv[1], sys.argv[2], sys.argv[3]
track_record_path = os.path.join(
    project_dir, "docs", "tooling", "domain-boundary-provenance-track-record.jsonl"
)

session_id = None
tool_name = None
file_path = None
try:
    with open(stdin_path) as f:
        data = json.loads(f.read())
    if isinstance(data, dict):
        session_id = data.get("session_id")
        tool_name = data.get("tool_name")
        tool_input = data.get("tool_input")
        if isinstance(tool_input, dict):
            file_path = tool_input.get("file_path")
except Exception:
    pass

entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "session_id": session_id,
    "tool_name": tool_name,
    "file_path": file_path,
    "manifest_status": "absent_or_invalid",
    "file_in_scope": None,
    "matches_found": None,
    "matches_cited": None,
    "decision": "probe_error",
    "reason": None,
    "probe_error": cause,
}
try:
    os.makedirs(os.path.dirname(track_record_path), exist_ok=True)
    with open(track_record_path, "a") as fh:
        fh.write(json.dumps(entry) + "\n")
except Exception:
    pass
PYEOF
}

# PROVISIONAL — owner: wright. 5s budget, reused as a starting value from
# first-turn-contract.sh's own measured-and-cited 5s bound, but NOT itself measured for this
# probe (this probe does manifest file I/O the sibling probe does not). Forge must measure this
# probe's actual runtime against representative manifest sizes before this value is treated as
# settled — see docs/tooling/domain-boundary-provenance-hook.md §6's timeout note.
PROBE_EXIT=0
timeout 5 "$REPO_DIR/scripts/domain_boundary_provenance_probe.py" <"$STDIN_FILE" >"$STDOUT_FILE" 2>"$STDERR_FILE" || PROBE_EXIT=$?

OUT="$(cat "$STDOUT_FILE")"

# Validate stdout is either empty (allow), or valid JSON matching DomainBoundaryHookOutput's
# shape: decision === "block" with a non-empty string reason. Anything else — non-JSON, a
# decision value other than "block", "block" with no reason, non-zero probe exit, timeout — is
# probe failure -> fail open (emit nothing, exit 0). Spec §6/§9.
if [ "$PROBE_EXIT" -eq 124 ] || [ "$PROBE_EXIT" -eq 137 ]; then
  write_probe_error "timeout: probe killed after 5s"
  exit 0
fi

if [ "$PROBE_EXIT" -ne 0 ]; then
  ERR="$(cat "$STDERR_FILE")"
  write_probe_error "non-zero exit ${PROBE_EXIT}: ${ERR:-(no stderr)}"
  exit 0
fi

if [ -z "$OUT" ]; then
  # Empty stdout on a clean exit is an explicit allow — the probe already wrote its own
  # track-record line (run()'s allow branches, spec §6). Nothing more to log here.
  exit 0
fi

RESULT="$(printf '%s' "$OUT" | python3 -c '
import json, sys

raw = sys.stdin.read()
try:
    data = json.loads(raw)
except Exception:
    sys.exit(1)

# Allow: {} or any dict with no "decision" key.
if isinstance(data, dict) and "decision" not in data:
    sys.exit(0)

if not isinstance(data, dict):
    sys.exit(1)

if data.get("decision") != "block":
    sys.exit(1)

reason = data.get("reason")
if not isinstance(reason, str) or not reason.strip():
    sys.exit(1)

# Valid block: print it back out unchanged for the wrapper to relay.
print(json.dumps({"decision": "block", "reason": reason}))
sys.exit(0)
' 2>/dev/null)"
VALIDATE_EXIT=$?

if [ "$VALIDATE_EXIT" -ne 0 ]; then
  # This branch assumes the probe did not already write its own track-record line for this
  # invocation. That assumption holds today because the shipped probe has exactly one stdout
  # write (emit_block's print, valid by construction) and emit_allow prints nothing — so a
  # clean exit with malformed stdout cannot currently coexist with a prior write_track_record
  # call. Same caveat as the sibling wrapper's equivalent branch: not a guarantee this code
  # enforces, bounded consequence unchanged (no effect on the block/allow decision reaching
  # Claude Code; this path never emits anything).
  write_probe_error "malformed probe stdout (exit 0, invalid shape): ${OUT}"
  exit 0
fi

if [ -n "$RESULT" ]; then
  # Clean exit-0 deny: the probe already wrote its own "deny" track-record line before printing
  # this. Do not write a second entry.
  printf '%s' "$RESULT"
fi
exit 0
