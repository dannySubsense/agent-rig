#!/usr/bin/env bash
# SessionStart — inject the last session's queue from LORE, labeled as a signpost.
# Never blocks session start: always exits 0, reports its own failure in-context.
set -uo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR" || exit 0

STDOUT_FILE="$(mktemp)"
STDERR_FILE="$(mktemp)"
trap 'rm -f "$STDOUT_FILE" "$STDERR_FILE"' EXIT

PROBE_EXIT=0
timeout 5 "$REPO_DIR/scripts/session_queue_probe.py" >"$STDOUT_FILE" 2>"$STDERR_FILE" || PROBE_EXIT=$?

OUT="$(cat "$STDOUT_FILE")"
ERR="$(cat "$STDERR_FILE")"

if [ "$PROBE_EXIT" -eq 0 ] && [ -n "$OUT" ] && printf '%s' "$OUT" | python3 -c 'import json,sys; json.loads(sys.stdin.read())' >/dev/null 2>&1; then
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
