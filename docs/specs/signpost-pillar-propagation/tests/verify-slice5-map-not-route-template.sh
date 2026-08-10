#!/usr/bin/env bash
# Verification script for Slice 5: Map-Not-Route Briefing Convention Template
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 5 Tests/Done-When lists).
#
# Checks MAP-NOT-ROUTE-BRIEFING.md.template's section structure, DDR-INDEX item 25
# reconciliation, DDR-0009/hook-enforcement labeling, HOMELAB-CLAUDE.md.template's
# cross-reference, and absence of unresolved placeholder tokens — all via direct
# text-pattern checks, matching Slice 3/4 script precedent.
#
# Usage: bash verify-slice5-map-not-route-template.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
MNR_FILE="$REPO_ROOT/MAP-NOT-ROUTE-BRIEFING.md.template"
HOMELAB_FILE="$REPO_ROOT/HOMELAB-CLAUDE.md.template"
DDR_INDEX="$REPO_ROOT/docs/specs/agent-rig-ddrs/00-DDR-INDEX.md"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$MNR_FILE" ]; then
  echo "FAIL: $MNR_FILE not found"
  exit 1
fi
if [ ! -f "$HOMELAB_FILE" ]; then
  echo "FAIL: $HOMELAB_FILE not found"
  exit 1
fi
if [ ! -f "$DDR_INDEX" ]; then
  echo "FAIL: $DDR_INDEX not found"
  exit 1
fi

# --- Check 1: exactly the three required sections present ---
if grep -qE '^## Objective$' "$MNR_FILE" \
   && grep -qE '^## Architecture$' "$MNR_FILE" \
   && grep -qE "^## What'?s Claimed$" "$MNR_FILE"; then
  pass "Objective, Architecture, and What's Claimed sections are all present"
else
  fail "one or more of the three required sections (Objective, Architecture, What's Claimed) is missing"
fi

# --- Check 2: no checklist/method/suspicions section (as an actual heading) ---
if grep -qE '^##+ .*(Checklist|Method|Suspicions)' "$MNR_FILE"; then
  fail "a checklist/method/suspicions section heading was found — should be structurally omitted"
else
  pass "no checklist/method/suspicions section heading present"
fi

# --- Check 3: preamble explicitly states the DDR-INDEX item 25 reconciliation ---
if grep -qi 'item 25' "$MNR_FILE" \
   && grep -qi 'kept separate' "$MNR_FILE" \
   && grep -qi 'prevention-layer' "$MNR_FILE" \
   && grep -qi 'detection-layer' "$MNR_FILE"; then
  pass "preamble explicitly states the DDR-INDEX item 25 reconciliation (kept-separate, prevention vs. detection framing)"
else
  fail "preamble does not explicitly state the DDR-INDEX item 25 reconciliation"
fi

# --- Check 4: any DDR-0009/hook-enforcement mention is labeled practice-only / not-yet-built ---
if grep -qi 'DDR-0009' "$MNR_FILE"; then
  if grep -qi 'PROPOSED / QUEUED' "$MNR_FILE" \
     && grep -qi 'no hook' "$MNR_FILE" \
     && grep -qi 'practice-only' "$MNR_FILE"; then
    pass "DDR-0009/hook-enforcement mention is explicitly labeled practice-only/not-yet-built"
  else
    fail "DDR-0009 is mentioned but not clearly labeled practice-only/not-yet-built (missing status, 'no hook', or 'practice-only' language)"
  fi
else
  fail "expected DDR-0009 enforcement caveat not found (roadmap Slice 5 Implementation Notes requires this caveat if hook enforcement is referenced)"
fi

# --- Check 4b: no claim that the convention IS mechanically enforced ---
RISKY_HITS="$(grep -inE 'automatically enforc|enforced by a hook|hook enforces|mechanically enforc' "$MNR_FILE" | grep -viE 'no.{0,40}(hook|automated|mechanically|enforc)')"
if [ -z "$RISKY_HITS" ]; then
  pass "no risky phrasing implying the convention is mechanically/automatically enforced"
else
  fail "risky phrasing found implying automated enforcement exists: $RISKY_HITS"
fi

# --- Check 5: HOMELAB-CLAUDE.md.template contains a cross-reference to the new template ---
if grep -q 'MAP-NOT-ROUTE-BRIEFING.md.template' "$HOMELAB_FILE"; then
  pass "HOMELAB-CLAUDE.md.template contains a cross-reference to MAP-NOT-ROUTE-BRIEFING.md.template"
else
  fail "HOMELAB-CLAUDE.md.template does not cross-reference MAP-NOT-ROUTE-BRIEFING.md.template"
fi

# --- Check 6: no unresolved/stray placeholder tokens remain in either file ---
# Intentional template-substitution tokens (project-scoping) are excluded from the
# "unresolved" check, matching Slice 4's script precedent.
STRAY_MNR="$(grep -oE '<[A-Z][A-Z0-9-]*>' "$MNR_FILE" | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
STRAY_HOMELAB_SECTION="$(grep -n 'MAP-NOT-ROUTE-BRIEFING.md.template' "$HOMELAB_FILE" | grep -oE '<[A-Z][A-Z0-9-]*>' | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
if [ -z "$STRAY_MNR" ] && [ -z "$STRAY_HOMELAB_SECTION" ]; then
  pass "no unresolved/stray placeholder tokens remain (only intentional <PROJECT-ID>/<AGENT-NAME> template tokens, if any, are present)"
else
  fail "unresolved placeholder token(s) found: MNR=[$STRAY_MNR] HOMELAB=[$STRAY_HOMELAB_SECTION]"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
