#!/usr/bin/env bash
# Verification script for Slice 8: Retrofit Procedure Doc
# (docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 8 Tests/Done-When lists).
#
# Checks RETROFIT-PROCEDURE.md: all six cutover steps present, RetrofitAuditRecord schema
# block present, explicit non-import/no-symlink/no-submodule statement present, the
# practice-only-vs-probe-hook ordering rule stated, no unresolved placeholder tokens, and a
# spot-check sample of key phrases for verbatim match against 02-ARCHITECTURE.md's
# "Per-Project Cutover Procedure (Component 9, RETROFIT-PROCEDURE.md)" section — matching
# Slice 3/4/5/6/7 script precedent (direct text-pattern checks, not a diff tool).
#
# Usage: bash verify-slice8-retrofit-procedure.sh
# Exit 0 = all checks pass. Exit 1 = at least one check failed (see output).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
SPEC_DIR="$REPO_ROOT/docs/specs/signpost-pillar-propagation"
RETROFIT_FILE="$SPEC_DIR/RETROFIT-PROCEDURE.md"
ARCH_FILE="$SPEC_DIR/02-ARCHITECTURE.md"

FAIL=0
pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }

if [ ! -f "$RETROFIT_FILE" ]; then
  echo "FAIL: $RETROFIT_FILE not found"
  exit 1
fi

if [ ! -f "$ARCH_FILE" ]; then
  echo "FAIL: $ARCH_FILE not found (needed for verbatim spot-check)"
  exit 1
fi

# --- Check 1: all six procedure steps present ---
declare -a STEP_LABELS=(
  "Blast-radius audit"
  "Install"
  "Remove"
  "Trace-verify"
  "Dispatch an independent, unbriefed Frank gate"
  "Record"
)
MISSING_STEPS=""
for label in "${STEP_LABELS[@]}"; do
  if ! grep -qiE "$label" "$RETROFIT_FILE"; then
    MISSING_STEPS="$MISSING_STEPS|$label"
  fi
done
if [ -z "$MISSING_STEPS" ]; then
  pass "all six cutover procedure steps are present (blast-radius audit -> install -> remove -> trace-verify -> dispatch unbriefed Frank gate -> record)"
else
  fail "missing procedure step(s): $MISSING_STEPS"
fi

# --- Check 2: RetrofitAuditRecord schema block present ---
if grep -q "interface RetrofitAuditRecord" "$RETROFIT_FILE"; then
  pass "'RetrofitAuditRecord' TypeScript-shape schema block is present"
else
  fail "'interface RetrofitAuditRecord' schema block not found"
fi

# Schema fields spot-check — all fields from architecture's schema should appear.
declare -a SCHEMA_FIELDS=(
  "project:"
  "residentAgent:"
  "blastRadius:"
  "docReferences:"
  "scriptCallSites:"
  "priorVariantPaths:"
  "cutoverComplete:"
  "priorVariantRemoved:"
  "frankGateVerdict:"
  "frankGateUnbriefed:"
  "traceVerification:"
)
MISSING_FIELDS=""
for field in "${SCHEMA_FIELDS[@]}"; do
  if ! grep -qF "$field" "$RETROFIT_FILE"; then
    MISSING_FIELDS="$MISSING_FIELDS $field"
  fi
done
if [ -z "$MISSING_FIELDS" ]; then
  pass "all RetrofitAuditRecord schema fields are present in the doc"
else
  fail "missing RetrofitAuditRecord schema field(s):$MISSING_FIELDS"
fi

# --- Check 3: explicit non-import/no-symlink/no-submodule statement present ---
if grep -qiE 'no symlink.*no submodule|not imported as a dependency' "$RETROFIT_FILE"; then
  pass "explicit non-import/no-symlink/no-submodule statement is present"
else
  fail "no explicit statement disclaiming symlink/submodule import found"
fi

# --- Check 4: ordering rule stated (practice-only 4/5/7 immediate, probe-hook 1-3 wait for pilot PASS) ---
if grep -qiE 'Practice-only items.*proceed per-project immediately' "$RETROFIT_FILE" \
   && grep -qE '4, 5, 7|4, 5, and 7' "$RETROFIT_FILE" \
   && grep -qiE 'Probe-hook items.*wait for' "$RETROFIT_FILE" \
   && grep -qE '1-3|1, 2, 3|1, 2, and 3' "$RETROFIT_FILE" \
   && grep -qiE "pilot('|)s? Frank[- ]gate.*PASS|Frank gate.*PASS" "$RETROFIT_FILE"; then
  pass "ordering rule is stated (practice-only 4/5/7 immediate; probe-hook 1-3 wait for pilot Frank-gate PASS)"
else
  fail "ordering rule (practice-only 4/5/7 immediate vs probe-hook 1-3 wait for pilot Frank-gate PASS) not fully stated"
fi

# --- Check 5: no unresolved placeholder tokens remain ---
STRAY="$(grep -oE '<[A-Z][A-Z0-9-]*>' "$RETROFIT_FILE" | sort -u)"
if [ -z "$STRAY" ]; then
  pass "no unresolved placeholder tokens remain in RETROFIT-PROCEDURE.md"
else
  fail "unresolved placeholder token(s) found: $STRAY"
fi

# --- Check 6: spot-check verbatim match against architecture's six-step sequence ---
# Isolate architecture's "Per-Project Cutover Procedure" section (from its heading to the
# next '## ' heading or EOF).
ARCH_SECTION="$(awk '/^### Per-Project Cutover Procedure/{flag=1; print; next} /^## /{if (flag) exit} /^### /{if (flag && !/^### Per-Project Cutover Procedure/) exit} flag{print}' "$ARCH_FILE")"

if [ -z "$ARCH_SECTION" ]; then
  fail "could not isolate architecture's 'Per-Project Cutover Procedure' section for spot-check"
else
  # Sample key verbatim phrases (one per step) that should appear unparaphrased in both docs.
  declare -a SPOT_PHRASES=(
    "grep own repo for: prior probe-style variant script paths"
    "not a symlink or submodule reference back to agent-rig"
    "Full replacement, not coexistence"
    "not response-text plausibility"
    "map-not-route convention"
    "before declaring that"
  )
  # Markdown source hard-wraps at ~80-100 cols, so a sample phrase can legitimately span a line
  # break in the raw text (e.g. "...own repo — not\n   a symlink..."). grep -F matches within a
  # single line only, so collapse whitespace (including newlines) to single spaces before
  # searching — this makes the check robust to line-wrap position without weakening what it
  # actually verifies (the phrase's words still must appear contiguously, in order).
  ARCH_SECTION_FLAT="$(echo "$ARCH_SECTION" | tr '\n' ' ' | tr -s ' ')"
  RETROFIT_FLAT="$(tr '\n' ' ' < "$RETROFIT_FILE" | tr -s ' ')"
  DRIFT=""
  for phrase in "${SPOT_PHRASES[@]}"; do
    IN_ARCH="$(echo "$ARCH_SECTION_FLAT" | grep -cF "$phrase")"
    IN_RETROFIT="$(echo "$RETROFIT_FLAT" | grep -cF "$phrase")"
    if [ "$IN_ARCH" -eq 0 ]; then
      # Phrase not actually in architecture section — spot-check itself needs updating, not a doc drift.
      DRIFT="$DRIFT|SPOT-CHECK-STALE:'$phrase' not found in architecture section"
    elif [ "$IN_RETROFIT" -eq 0 ]; then
      DRIFT="$DRIFT|DRIFT:'$phrase' present in architecture but not verbatim in RETROFIT-PROCEDURE.md"
    fi
  done
  if [ -z "$DRIFT" ]; then
    pass "spot-checked key phrases from architecture's six-step sequence appear verbatim in RETROFIT-PROCEDURE.md (no drift detected)"
  else
    fail "verbatim spot-check issue(s): $DRIFT"
  fi
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "ONE OR MORE CHECKS FAILED"
  exit 1
fi
