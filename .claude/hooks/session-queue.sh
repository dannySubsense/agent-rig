#!/usr/bin/env bash
# SessionStart — inject the last session's queue from LORE, labeled as a signpost.
# Never blocks session start: always exits 0, reports its own failure in-context.
set -uo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR" || exit 0

STDIN_FILE="$(mktemp)"
STDOUT_FILE="$(mktemp)"
STDERR_FILE="$(mktemp)"
trap 'rm -f "$STDIN_FILE" "$STDOUT_FILE" "$STDERR_FILE"' EXIT

# Capture the hook's stdin (session_id, transcript_path, etc.) and replay it to the probe —
# the probe needs transcript_path/session_id to self-exclude the current session from its
# staleness scan (INTAKE §S2).
cat >"$STDIN_FILE"

# PROVISIONAL — owner: wright. 5s budget for one Tailscale Postgres round trip (connect +
# query), not sourced from a benchmark; the probe's own internal connect timeout
# (TIMEOUT_SECONDS=3 in session_queue_probe.py) is deliberately shorter so it fires first
# and produces a real psycopg2 error instead of this outer kill preempting it silently.
PROBE_EXIT=0
timeout 5 "$REPO_DIR/scripts/session_queue_probe.py" <"$STDIN_FILE" >"$STDOUT_FILE" 2>"$STDERR_FILE" || PROBE_EXIT=$?

OUT="$(cat "$STDOUT_FILE")"
ERR="$(cat "$STDERR_FILE")"

# Validate not just "parses as JSON" but "is the right shape" — a valid-but-wrong payload
# (e.g. `123`, or JSON missing hookSpecificOutput.hookEventName) must not pass through
# silently as if it were a real injection.
if [ "$PROBE_EXIT" -eq 0 ] && [ -n "$OUT" ] && printf '%s' "$OUT" | python3 -c '
import json, sys
data = json.loads(sys.stdin.read())
event = data.get("hookSpecificOutput", {}).get("hookEventName") if isinstance(data, dict) else None
sys.exit(0 if event == "SessionStart" else 1)
' >/dev/null 2>&1; then
  printf '%s' "$OUT"
  exit 0
fi

python3 - "$PROBE_EXIT" "$OUT" "$ERR" <<'PYEOF'
import json
import sys

probe_exit, out, err = sys.argv[1], sys.argv[2], sys.argv[3]

message = (
    "SESSION QUEUE UNAVAILABLE — the queue probe failed or produced invalid output "
    f"(exit {probe_exit}). No queue was loaded. This is NOT evidence that nothing is "
    "queued; check LORE manually before proceeding."
)
if err.strip():
    message += f"\n\nCaptured stderr:\n{err.strip()}"
if out.strip():
    message += f"\n\nCaptured stdout (did not validate as JSON):\n{out.strip()}"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": message,
    }
}))
PYEOF
exit 0
