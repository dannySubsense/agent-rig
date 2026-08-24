#!/usr/bin/env python3
"""UserPromptSubmit — no-preamble / no-meta-narration reminder injection.

Fires once per user turn, before the model generates its response. Emits
`hookSpecificOutput.additionalContext` (the same field `session_queue_probe.py`
already uses for its own `SessionStart` injection) containing a fixed, literal
reminder string (§6.1 of docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md).

Advisory injection only — `UserPromptSubmit`'s `additionalContext` has no
block/deny semantics; it only adds text to context. No detection logic here,
pure static injection.
"""

import json
import sys

REMINDER_TEXT = (
    "NO-PREAMBLE REMINDER — do not open with intent-announcement, stall, or "
    "self-narration (\"I'll...\", \"Let me...\", \"I think I should...\", \"To be "
    "honest...\"). Start with the substantive action or the concrete answer. A "
    "Stop-hook check inspects this turn for exactly this pattern "
    "(docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md)."
)


def emit(context_text):
    """UserPromptSubmit hooks communicate by printing this JSON shape on stdout."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context_text,
        }
    }))


def main():
    # Pure static injection — no stdin parsing needed, no failure mode possible.
    try:
        sys.stdin.read()
    except Exception:
        pass
    emit(REMINDER_TEXT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
