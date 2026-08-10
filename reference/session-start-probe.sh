#!/usr/bin/env bash
# SessionStart hook — runs the ground-truth probe and injects its output as
# additionalContext BEFORE any memory/LORE priming happens. "Signpost, not
# pillar": this is the pillar half — see this project's CLAUDE.md and
# agent-rig docs/specs/agent-rig-ddrs/DDR-004-session-start-pillar-binding.md.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

PROBE_EXIT=0
PROBE_OUTPUT="$(timeout 5 "$REPO_DIR/scripts/session_probe.py" 2>&1)" || PROBE_EXIT=$?

if [ "$PROBE_EXIT" -eq 124 ]; then
  PROBE_OUTPUT="$PROBE_OUTPUT

PROBE OUTPUT INCOMPLETE — probe killed at 5s budget (exit 124); treat the above as partial, not ground truth."
elif [ "$PROBE_EXIT" -ne 0 ]; then
  PROBE_OUTPUT="$PROBE_OUTPUT

PROBE OUTPUT INCOMPLETE — probe exited with error (exit $PROBE_EXIT); treat the above as partial, not ground truth."
fi

python3 - "$PROBE_OUTPUT" <<'PYEOF'
import json
import sys

probe_output = sys.argv[1]
context = (
    "GROUND-TRUTH PROBE OUTPUT (script-generated git/docs state only — this "
    "is NOT memory priming and does NOT satisfy CLAUDE.md's Session Start "
    "Behaviour step). It reflects what is verifiably true right now about "
    "the repo; prior-session memory and docs are the signpost, this is the "
    "pillar you verify them against — but it does not replace them.\n\n"
    + probe_output
    + "\n\n"
    "ACTION REQUIRED BEFORE YOUR FIRST REPLY: call search_knowledge per "
    "CLAUDE.md's Session Start Behaviour section now, if you have not "
    "already done so this session. This probe output being present is not "
    "evidence that step happened — it is a separate, still-pending step."
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": context,
    }
}))
PYEOF
