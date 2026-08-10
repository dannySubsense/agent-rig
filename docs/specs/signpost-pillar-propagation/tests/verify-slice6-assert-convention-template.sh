#!/usr/bin/env bash
# Verification script for Slice 6: Assert-Convention + Sentinel Pattern Combined Doc
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 6 Tests/Done-When lists).
#
# Checks ASSERT-CONVENTION.md.template's scope-boundary statement, sentinel principles
# (literal sentences), DDR-0009/hook-enforcement labeling, Section 2.5 citation labeling
# (or absence), HOMELAB-CLAUDE.md.template's cross-reference, and absence of unresolved
# placeholder tokens — all via direct text-pattern checks, matching Slice 3/4/5 script
# precedent.
#
# Usage: bash verify-slice6-assert-convention-template.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
AC_FILE="$REPO_ROOT/ASSERT-CONVENTION.md.template"
HOMELAB_FILE="$REPO_ROOT/HOMELAB-CLAUDE.md.template"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$AC_FILE" ]; then
  echo "FAIL: $AC_FILE not found"
  exit 1
fi
if [ ! -f "$HOMELAB_FILE" ]; then
  echo "FAIL: $HOMELAB_FILE not found"
  exit 1
fi

# --- Check 1: assert-convention section states its scope boundary explicitly ---
if grep -qi 'when a coupling is known' "$AC_FILE"; then
  pass "assert-convention section explicitly states the scope boundary ('when a coupling is known')"
else
  fail "assert-convention section does not explicitly state the scope boundary ('when a coupling is known')"
fi

# --- Check 2: sentinel section states both required principles as literal sentences ---
if grep -qi 'success and failure must produce different bytes' "$AC_FILE"; then
  pass "sentinel section states 'success and failure must produce different bytes' as a literal sentence"
else
  fail "sentinel section is missing the literal sentence 'success and failure must produce different bytes'"
fi

if grep -qi 'a signal nobody reads is not a control' "$AC_FILE"; then
  pass "sentinel section states 'a signal nobody reads is not a control' as a literal sentence"
else
  fail "sentinel section is missing the literal sentence 'a signal nobody reads is not a control'"
fi

# --- Check 3: no content implies DDR-0009/hook-based enforcement exists ---
# Any mention of DDR-0009 must be labeled PROPOSED/QUEUED or practice-only/no-hook language.
if grep -qi 'DDR-0009' "$AC_FILE"; then
  if grep -qi 'PROPOSED / QUEUED' "$AC_FILE" \
     && grep -qi 'practice-only' "$AC_FILE" \
     && grep -qiE 'no hook' "$AC_FILE"; then
    pass "DDR-0009/hook-enforcement mention is explicitly labeled PROPOSED/QUEUED and practice-only"
  else
    fail "DDR-0009 is mentioned but not clearly labeled PROPOSED/QUEUED, practice-only, or 'no hook' language"
  fi
else
  fail "expected DDR-0009 enforcement caveat not found (roadmap Slice 6 requires this caveat if hook enforcement is referenced)"
fi

# No claim that either convention IS mechanically/automatically enforced.
RISKY_HITS="$(grep -inE 'automatically enforc|enforced by a hook|hook enforces|mechanically enforc' "$AC_FILE" | grep -viE 'no.{0,40}(hook|automated|mechanically|enforc)')"
if [ -z "$RISKY_HITS" ]; then
  pass "no risky phrasing implying either convention is mechanically/automatically enforced"
else
  fail "risky phrasing found implying automated enforcement exists: $RISKY_HITS"
fi

# --- Check 4: Section 2.5 citation, if present, is labeled heuristic-not-established ---
# A sentence that mentions "Section 2.5" only to explicitly DENY citing/drawing on it
# (e.g. "does not cite ... Section 2.5") is a disclaimer, not a citation, and satisfies
# the absence branch even though the raw string "section 2.5" appears in the file.
SECTION25_LINES="$(grep -inE 'section 2\.5|repetition as a? ?diagnostic instrument' "$AC_FILE")"
if [ -n "$SECTION25_LINES" ]; then
  NON_DISCLAIMER_LINES="$(echo "$SECTION25_LINES" | grep -viE "does not cite|doesn't cite|not cit(e|ing)|out of scope")"
  if [ -z "$NON_DISCLAIMER_LINES" ]; then
    pass "Section 2.5 ('repetition as diagnostic instrument') is mentioned only in an explicit disclaimer (does not cite it) — requirement satisfied by absence"
  elif grep -qi 'heuristic, not an\? established pattern' "$AC_FILE"; then
    pass "Section 2.5 ('repetition as diagnostic instrument') is cited and labeled 'heuristic, not established pattern'"
  else
    fail "Section 2.5 is cited but not labeled 'heuristic, not established pattern'"
  fi
else
  pass "Section 2.5 ('repetition as diagnostic instrument') is not cited at all — requirement satisfied by absence"
fi

# --- Check 5: HOMELAB-CLAUDE.md.template cross-references the new template ---
if grep -q 'ASSERT-CONVENTION.md.template' "$HOMELAB_FILE"; then
  pass "HOMELAB-CLAUDE.md.template contains a cross-reference to ASSERT-CONVENTION.md.template"
else
  fail "HOMELAB-CLAUDE.md.template does not cross-reference ASSERT-CONVENTION.md.template"
fi

# --- Check 6: no unresolved/stray placeholder tokens remain in either file ---
# Intentional template-substitution tokens (project-scoping) are excluded from the
# "unresolved" check, matching Slice 4/5 script precedent.
STRAY_AC="$(grep -oE '<[A-Z][A-Z0-9-]*>' "$AC_FILE" | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
STRAY_HOMELAB_SECTION="$(grep -n 'ASSERT-CONVENTION.md.template' "$HOMELAB_FILE" | grep -oE '<[A-Z][A-Z0-9-]*>' | sort -u | grep -vE '^<(PROJECT-ID|AGENT-NAME)>$')"
if [ -z "$STRAY_AC" ] && [ -z "$STRAY_HOMELAB_SECTION" ]; then
  pass "no unresolved/stray placeholder tokens remain (only intentional <PROJECT-ID>/<AGENT-NAME> template tokens, if any, are present)"
else
  fail "unresolved placeholder token(s) found: AC=[$STRAY_AC] HOMELAB=[$STRAY_HOMELAB_SECTION]"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
