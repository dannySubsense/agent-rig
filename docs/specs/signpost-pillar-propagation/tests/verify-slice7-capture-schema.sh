#!/usr/bin/env bash
# Verification script for Slice 7: Capture Schema Addition (Verification:/Re-verify with:)
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 7 Tests/Done-When lists).
#
# Checks HOMELAB-CLAUDE.md.template's ## Capture Behaviour section: requires the
# `Verification:` and `Re-verify with:` lines, labels the schema as practice-only/
# discipline-based (not hook-enforced/automated), and contains no unresolved placeholder
# tokens — via direct text-pattern checks, matching Slice 3/4/5/6 script precedent.
#
# Usage: bash verify-slice7-capture-schema.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
HOMELAB_FILE="$REPO_ROOT/HOMELAB-CLAUDE.md.template"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$HOMELAB_FILE" ]; then
  echo "FAIL: $HOMELAB_FILE not found"
  exit 1
fi

# Isolate the Capture Behaviour section (from its heading to the next '## ' heading or EOF).
SECTION="$(awk '/^## Capture Behaviour/{flag=1; print; next} /^## /{if (flag) exit} flag{print}' "$HOMELAB_FILE")"

if [ -z "$SECTION" ]; then
  echo "FAIL: '## Capture Behaviour' section not found in $HOMELAB_FILE"
  exit 1
fi

# --- Check 1: Verification: stated as a required line ---
if echo "$SECTION" | grep -qE '`Verification:`'; then
  pass "'Verification:' line is present in the Capture Behaviour section"
else
  fail "'Verification:' line is missing from the Capture Behaviour section"
fi

# --- Check 2: Re-verify with: stated as a required line ---
if echo "$SECTION" | grep -qE '`Re-verify with:`'; then
  pass "'Re-verify with:' line is present in the Capture Behaviour section"
else
  fail "'Re-verify with:' line is missing from the Capture Behaviour section"
fi

# Both lines must be framed as required, not optional. This is a two-sided check, not just
# absence-of-"(optional)": also require an affirmative "must"/"required" statement governing
# the two lines, so a future edit that silently drops the affirmative language (without adding
# "(optional)") still fails this check.
MARKED_OPTIONAL="$(echo "$SECTION" | grep -E '`Verification:`.*\(optional\)|`Re-verify with:`.*\(optional\)')"
HAS_MUST_LANGUAGE="$(echo "$SECTION" | grep -iE 'must (also )?include|required|must include')"
if [ -n "$MARKED_OPTIONAL" ]; then
  fail "'Verification:' or 'Re-verify with:' is marked (optional) — roadmap requires both as required lines"
elif [ -z "$HAS_MUST_LANGUAGE" ]; then
  fail "no affirmative 'must'/'required' language found governing 'Verification:'/'Re-verify with:' — absence of '(optional)' alone is not sufficient evidence of a requirement"
else
  pass "'Verification:'/'Re-verify with:' are affirmatively stated as required (not merely un-marked as optional)"
fi

# --- Check 3: no content implies hook-enforced/automated validation ---
# The section must explicitly disclaim automated enforcement (practice-only/discipline-based).
if echo "$SECTION" | grep -qiE 'not a schema field enforced by LORE|not an automated gate|no hook or tool currently validates|by discipline'; then
  pass "section explicitly labels the schema as practice-only/discipline-based, not hook-enforced"
else
  fail "section does not explicitly disclaim hook-based/automated enforcement of Verification/Re-verify with"
fi

# No claim that the lines ARE automatically/mechanically validated.
RISKY_HITS="$(echo "$SECTION" | grep -inE 'automatically validat|enforced by (a )?hook|hook (validates|enforces)|mechanically enforc' | grep -viE 'not (a |an )?(automated|hook|mechanically)|no hook')"
if [ -z "$RISKY_HITS" ]; then
  pass "no risky phrasing implying Verification:/Re-verify with: are automatically/mechanically enforced"
else
  fail "risky phrasing found implying automated enforcement exists: $RISKY_HITS"
fi

# --- Check 4: no unresolved placeholder tokens remain (excluding intentional template tokens) ---
STRAY="$(echo "$SECTION" | grep -oE '<[A-Z][A-Z0-9-]*>' | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
if [ -z "$STRAY" ]; then
  pass "no unresolved/stray placeholder tokens remain in the Capture Behaviour section (only intentional <PROJECT-ID>/<AGENT-NAME> tokens, if any, are present)"
else
  fail "unresolved placeholder token(s) found in the Capture Behaviour section: $STRAY"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
