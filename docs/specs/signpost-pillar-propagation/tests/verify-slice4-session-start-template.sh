#!/usr/bin/env bash
# Verification script for Slice 4: Session Start Behaviour Template —
# Signpost:/Pillar: + 3-Check Block
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 4 Tests/Done-When lists).
#
# Checks the `## Session Start Behaviour` section of HOMELAB-CLAUDE.md.template
# directly (text-pattern checks), plus the DDR-INDEX backlog resolution. Does NOT
# invoke live bootstrap/InputBundle-substitution tooling — per the roadmap's first
# Slice 4 Test item ("template renders with no broken cross-references"), that
# requires actual bootstrap tooling this script doesn't have access to; per Slice
# 3's precedent, it is documented below as a manual-trace item rather than
# fabricated here.
#
# MANUAL-TRACE ITEM (not automated by this script):
#   - "Template renders (placeholder-substitution dry run against a fresh
#     InputBundle) with no broken cross-references." Verify by hand: run
#     /new-project (or trace an existing bootstrap) and confirm
#     HOMELAB-CLAUDE.md.template's Session Start Behaviour section renders with
#     <PROJECT-ID>/<AGENT-NAME> resolved and no dangling cross-reference.
#
# Usage: bash verify-slice4-session-start-template.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
TEMPLATE_FILE="$REPO_ROOT/HOMELAB-CLAUDE.md.template"
DDR_INDEX="$REPO_ROOT/docs/specs/agent-rig-ddrs/00-DDR-INDEX.md"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "FAIL: $TEMPLATE_FILE not found"
  exit 1
fi
if [ ! -f "$DDR_INDEX" ]; then
  echo "FAIL: $DDR_INDEX not found"
  exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# --- Extract the `## Session Start Behaviour` section (up to the next `## ` heading) ---
awk '
  /^## Session Start Behaviour$/ { capture=1; print; next }
  capture && /^## / { capture=0 }
  capture { print }
' "$TEMPLATE_FILE" > "$TMPDIR/section.md"

if [ ! -s "$TMPDIR/section.md" ]; then
  echo "FAIL: could not extract '## Session Start Behaviour' section from $TEMPLATE_FILE"
  exit 1
fi

# --- Check 1: both the 3-check block and the Signpost:/Pillar: convention are
#     present in the same section ---
if grep -q '### 1\. Check LORE' "$TMPDIR/section.md" \
   && grep -q '### 2\. Check Switchboard' "$TMPDIR/section.md" \
   && grep -q '### 3\. Check git' "$TMPDIR/section.md" \
   && grep -qE '\*\*Signpost:\*\*' "$TMPDIR/section.md" \
   && grep -qE '\*\*Pillar:\*\*' "$TMPDIR/section.md"; then
  pass "3-check block (LORE/Switchboard/git) and Signpost:/Pillar: convention are both present in the Session Start Behaviour section"
else
  fail "3-check block and/or Signpost:/Pillar: convention missing from the Session Start Behaviour section"
fi

# --- Check 2: Switchboard once-at-cold-start-only property explicitly stated ---
if grep -qi 'once at cold start' "$TMPDIR/section.md" \
   && grep -qi 'do not repeat it on compaction or mid-session' "$TMPDIR/section.md"; then
  pass "Switchboard cold-start-only property is explicitly stated (not compaction/mid-session)"
else
  fail "Switchboard cold-start-only property is not explicitly stated"
fi

# --- Check 3: Pillar:-labeled claims documented as requiring a stated verification method ---
if grep -qi 'stated with its' "$TMPDIR/section.md" \
   && grep -qi 'verification method' "$TMPDIR/section.md"; then
  pass "Pillar:-labeled claims are documented as requiring a stated verification method"
else
  fail "Pillar:-labeled claims are not documented as requiring a stated verification method"
fi

# --- Check 4: no unresolved placeholder tokens remain in the edited section ---
# Placeholders here are project-scoping tokens (e.g. <PROJECT-ID>, <AGENT-NAME>)
# that are intentional (this is a *.template file substituted at bootstrap time) —
# so the "unresolved" check targets malformed/stray tokens outside the two known,
# intentional template tokens, not the presence of template tokens themselves.
STRAY_TOKENS="$(grep -oE '<[A-Z][A-Z0-9-]*>' "$TMPDIR/section.md" | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
if [ -z "$STRAY_TOKENS" ]; then
  pass "no unresolved/stray placeholder tokens remain in the edited section (only the intentional <PROJECT-ID>/<AGENT-NAME> template tokens are present)"
else
  fail "unresolved placeholder token(s) found in the edited section: $STRAY_TOKENS"
fi

# --- Check 5: labeling convention text does NOT claim/imply hook-based/automated
#     enforcement exists for it (Frank's mandatory caveat) ---
# Risky phrasing: asserting the hook or the labeling convention is itself enforced,
# a gate, mandatory-and-checked, or automatic. The section is allowed to *mention*
# the hook script as optional infrastructure, but must not claim it (or the
# Signpost:/Pillar: convention) is mechanically enforced.
RISKY_HITS="$(grep -inE 'automatically enforc|enforced by|is a gate|hook enforces|mechanically enforc' "$TMPDIR/section.md" | grep -viE 'not.{0,40}(enforced|a gate)|neither.{0,40}(gate|enforc)')"
if [ -z "$RISKY_HITS" ]; then
  pass "no risky phrasing implying hook-based/automated enforcement of the labeling convention"
else
  fail "risky phrasing found implying automated enforcement exists: $RISKY_HITS"
fi

# --- Check 5b: explicit disclaimer present distinguishing the hook (if present) from
#     the practice-only labeling convention, and stating neither is a gate ---
if grep -qi 'distinct, separate mechanism' "$TMPDIR/section.md" \
   && grep -qi 'practice-only' "$TMPDIR/section.md" \
   && grep -qi 'neither one is a gate' "$TMPDIR/section.md"; then
  pass "hook mechanism is explicitly distinguished from the practice-only labeling convention, with 'not a gate' stated"
else
  fail "missing explicit distinction between the hook mechanism and the practice-only labeling convention (or missing 'not a gate' statement)"
fi

# --- Check 6: DDR-INDEX's 3-check promotion backlog item marked RESOLVED with
#     cross-reference to this slice ---
if grep -A5 'Template tier: promote the 3-check session-start block' "$DDR_INDEX" \
   | grep -q 'RESOLVED 2026-08-09' \
   && grep -A5 'Template tier: promote the 3-check session-start block' "$DDR_INDEX" \
   | grep -qi 'signpost-pillar-propagation Slice 4'; then
  pass "DDR-INDEX's 3-check promotion backlog item is marked RESOLVED with a cross-reference to Slice 4"
else
  fail "DDR-INDEX's 3-check promotion backlog item is not marked RESOLVED with a Slice 4 cross-reference"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
