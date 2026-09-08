#!/usr/bin/env bash
# Stop — Signpost/Pillar checklist enforcement (wrapper).
# Captures stdin, replays it to scripts/signpost_checklist_probe.py under a bounded timeout,
# validates the output shape, and fails open on every failure mode. Structurally identical to
# .claude/hooks/no-preamble-no-meta-narration.sh (see
# docs/specs/signpost-checklist-redesign/02-ARCHITECTURE.md §8 — wrapper shape reused verbatim,
# not redesigned).
set -uo pipefail
REPO_DIR="$(pwd)"
cd "$REPO_DIR" || exit 0

STDIN_FILE="$(mktemp)"
STDOUT_FILE="$(mktemp)"
STDERR_FILE="$(mktemp)"
trap 'rm -f "$STDIN_FILE" "$STDOUT_FILE" "$STDERR_FILE"' EXIT

# Capture the hook's stdin (session_id, stop_hook_active, last_assistant_message, etc.)
# and replay it to the probe.
cat >"$STDIN_FILE"

# Write a probe_error TrackRecordEntry ourselves, for any path where the probe did not get
# the chance to write its own — non-zero exit, timeout kill, not-executable, or output that
# doesn't validate as JSON/shape (which means it never reached emit_block/emit_allow either).
# On a clean exit-0 run the probe's own main()/run() already wrote a line — this function
# must not run on that path. Never lets a failure here affect the wrapper's own exit code.
write_probe_error() {
  local cause="$1"
  python3 - "$REPO_DIR" "$STDIN_FILE" "$cause" <<'PYEOF' || true
import json
import os
import sys

repo_dir, stdin_path, cause = sys.argv[1], sys.argv[2], sys.argv[3]

sys.path.insert(0, os.path.join(repo_dir, "scripts"))
from hook_telemetry import write_telemetry_event

track_record_path = os.environ.get(
    "SIGNPOST_TRACK_RECORD_PATH",
    os.path.join(repo_dir, "docs", "tooling", "signpost-checklist-track-record.jsonl"),
)

session_id = None
stop_hook_active = False
try:
    with open(stdin_path) as f:
        data = json.loads(f.read())
    if isinstance(data, dict):
        session_id = data.get("session_id")
        stop_hook_active = bool(data.get("stop_hook_active", False))
except Exception:
    pass

write_telemetry_event(
    hook_name="signpost-checklist",
    jsonl_path=track_record_path,
    session_id=session_id,
    decision="probe_error",
    reason=None,
    probe_error=cause,
    payload={
        "stop_hook_active": stop_hook_active,
        "queue_injected": False,
        "first_turn": False,
    },
)
PYEOF
}

# Resolve the probe path: prefer the repo-local copy (agent-rig's own case, zero change
# in behavior), fall back to the global install location (~/.claude/scripts/) when this
# wrapper is deployed to a project that doesn't carry its own scripts/ copy.
PROBE_PATH="$REPO_DIR/scripts/signpost_checklist_probe.py"
if [ ! -f "$PROBE_PATH" ]; then
  PROBE_PATH="$HOME/.claude/scripts/signpost_checklist_probe.py"
fi

# Tell the probe which project it's actually running against — required whenever the
# probe is not physically inside the repo it serves (the global-install case above).
export SIGNPOST_REPO_DIR="$REPO_DIR"

# 5s budget — measured 2026-09-07: 0.31s wall time, 50 MB RSS against the largest real
# transcript on this host (13.4 MB, out of 72 files scanned), giving ~16x headroom against
# the 5s bound.
PROBE_EXIT=0
timeout 5 "$PROBE_PATH" <"$STDIN_FILE" >"$STDOUT_FILE" 2>"$STDERR_FILE" || PROBE_EXIT=$?

OUT="$(cat "$STDOUT_FILE")"

# Validate stdout is either empty/"{}" (allow), or valid JSON matching the decision
# protocol's shape: decision === "block" with a non-empty string reason. Anything else —
# non-JSON, a decision value other than "block", "block" with no reason, non-zero probe
# exit, timeout — is probe failure -> fail open (emit nothing, exit 0).
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
  # track-record line. Nothing more to log here.
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
  # This branch assumes the probe did not already write its own track-record line for
  # this invocation.
  write_probe_error "malformed probe stdout (exit 0, invalid shape): ${OUT}"
  exit 0
fi

if [ -n "$RESULT" ]; then
  # Clean exit-0 block: the probe already wrote its own "block" track-record line before
  # printing this. Do not write a second entry.
  printf '%s' "$RESULT"
fi
exit 0
