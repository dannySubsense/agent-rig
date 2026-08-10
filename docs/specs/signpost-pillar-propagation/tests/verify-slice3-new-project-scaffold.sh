#!/usr/bin/env bash
# Verification script for Slice 3: `new-project.md` Scaffolds Components 1-3
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 3 Tests list).
#
# Extracts the fenced content blocks embedded in commands/new-project.md
# Step 6.5 and checks them against the reference/ source-of-record files and
# the roadmap's other structural requirements. Does NOT execute a live
# /new-project bootstrap (no InputBundle/agent session available standalone)
# — per the roadmap's first Test item, this is the documented manual-trace
# fallback: it verifies the exact bytes new-project.md would write, and the
# staged-file wiring, without requiring a full dry run.
#
# Usage: bash verify-slice3-new-project-scaffold.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CMD_FILE="$REPO_ROOT/commands/new-project.md"
REF_PY="$REPO_ROOT/reference/session_probe.py"
REF_SH="$REPO_ROOT/reference/session-start-probe.sh"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$CMD_FILE" ]; then
  echo "FAIL: $CMD_FILE not found"
  exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# --- Check 1: extract embedded scripts/session_probe.py block, byte-diff vs reference ---
# Block is the ```python ... ``` fence immediately after "Substep 6.5.1"
awk '
  /^```python$/ { if (found) next; capture=1; next }
  capture && /^```$/ { capture=0; found=1; next }
  capture { print }
' "$CMD_FILE" > "$TMPDIR/embedded_session_probe.py"

if [ -s "$TMPDIR/embedded_session_probe.py" ] && diff -q "$REF_PY" "$TMPDIR/embedded_session_probe.py" >/dev/null 2>&1; then
  pass "embedded scripts/session_probe.py block is byte-identical to reference/session_probe.py"
else
  fail "embedded scripts/session_probe.py block differs from reference/session_probe.py (or block not found)"
  diff "$REF_PY" "$TMPDIR/embedded_session_probe.py" 2>&1 | head -20
fi

# --- Check 2: extract embedded .claude/hooks/session-start-probe.sh block, byte-diff vs reference ---
# The file contains an earlier, unrelated ```bash fence (predates this slice), so anchor
# extraction on the marker line that introduces this specific block, then capture the
# next ```bash ... ``` fence after that line (mirrors Check 1's targeted approach).
MARKER_LINE="$(grep -n 'Write the following content, verbatim, to `\.claude/hooks/session-start-probe\.sh`' "$CMD_FILE" | head -1 | cut -d: -f1)"
if [ -n "${MARKER_LINE:-}" ]; then
  tail -n "+$MARKER_LINE" "$CMD_FILE" | awk '
    /^```bash$/ { if (found) next; capture=1; next }
    capture && /^```$/ { capture=0; found=1; next }
    capture { print }
  ' > "$TMPDIR/embedded_session_start_probe.sh"
else
  : > "$TMPDIR/embedded_session_start_probe.sh"
fi

if [ -s "$TMPDIR/embedded_session_start_probe.sh" ] && diff -q "$REF_SH" "$TMPDIR/embedded_session_start_probe.sh" >/dev/null 2>&1; then
  pass "embedded .claude/hooks/session-start-probe.sh block is byte-identical to reference/session-start-probe.sh"
else
  fail "embedded .claude/hooks/session-start-probe.sh block differs from reference/session-start-probe.sh (or block not found)"
  diff "$REF_SH" "$TMPDIR/embedded_session_start_probe.sh" 2>&1 | head -20
fi

# --- Check 3: extract embedded .claude/settings.json block, validate JSON + SessionStart matcher ---
awk '
  /^```json$/ { capture=1; next }
  capture && /^```$/ { capture=0; found=1; next }
  capture { print }
' "$CMD_FILE" > "$TMPDIR/embedded_settings.json"

if [ -s "$TMPDIR/embedded_settings.json" ] && python3 -c "
import json, sys
with open('$TMPDIR/embedded_settings.json') as f:
    data = json.load(f)
matchers = [h.get('matcher') for h in data.get('hooks', {}).get('SessionStart', [])]
assert 'startup|resume|clear' in matchers, f'matcher not found, got {matchers}'
" 2>"$TMPDIR/settings_err.txt"; then
  pass "embedded .claude/settings.json is valid JSON with SessionStart matcher 'startup|resume|clear'"
else
  fail "embedded .claude/settings.json is invalid or missing the SessionStart matcher block"
  cat "$TMPDIR/settings_err.txt" 2>/dev/null
fi

# --- Check 4: Step 12 staged-files list includes all three new files ---
if grep -A5 '^Stage exactly these' "$CMD_FILE" | grep -q 'scripts/session_probe.py' \
   && grep -A5 '^Stage exactly these' "$CMD_FILE" | grep -q '\.claude/hooks/session-start-probe\.sh' \
   && grep -A5 '^Stage exactly these' "$CMD_FILE" | grep -q '\.claude/settings\.json'; then
  pass "Step 12 prose + git add command include all three new files"
else
  fail "Step 12 git add command missing one or more of the three new files"
fi

# --- Check 5: Fixed Decision Table's "Bootstrap staged files" row includes all three ---
DECISION_ROW="$(grep '| Bootstrap staged files |' "$CMD_FILE")"
if echo "$DECISION_ROW" | grep -q 'scripts/session_probe.py' \
   && echo "$DECISION_ROW" | grep -q '\.claude/hooks/session-start-probe\.sh' \
   && echo "$DECISION_ROW" | grep -q '\.claude/settings\.json'; then
  pass "Fixed Decision Table's Bootstrap staged files row includes all three new files"
else
  fail "Fixed Decision Table's Bootstrap staged files row missing one or more of the three new files"
fi

# --- Check 6: Step 12 count and Fixed Decision Table stay consistent (8 items each) ---
STAGE_LINE="$(grep '^git add ' "$CMD_FILE")"
# count whitespace-separated tokens after "git add"
STAGE_COUNT="$(echo "$STAGE_LINE" | sed 's/^git add //' | wc -w)"
# Exclude the trailing parenthetical (explanatory text, not a staged file — e.g.
# "(path is variable — `<InputBundle.projectId>` is resolved at runtime)") before counting.
DECISION_COUNT="$(echo "$DECISION_ROW" | sed 's/(path is variable.*$//' | grep -o '`[^`]*`' | wc -l)"
if [ "$STAGE_COUNT" = "8" ] && [ "$DECISION_COUNT" = "8" ]; then
  pass "Step 12 git add (8 items) and Fixed Decision Table (8 items) are count-consistent"
else
  fail "staged-file count mismatch: git add has $STAGE_COUNT items, Fixed Decision Table lists $DECISION_COUNT items"
fi

# --- Check 7: no unresolved placeholder tokens in any of the three embedded blocks ---
for f in "$TMPDIR/embedded_session_probe.py" "$TMPDIR/embedded_session_start_probe.sh" "$TMPDIR/embedded_settings.json"; do
  if [ -f "$f" ] && grep -qE '<[A-Z][A-Z0-9-]*>' "$f"; then
    fail "unresolved placeholder token found in $(basename "$f")"
  fi
done
pass "no unresolved placeholder tokens in the three embedded blocks (if not already flagged above)"

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
