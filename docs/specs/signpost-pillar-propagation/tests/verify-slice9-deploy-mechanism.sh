#!/usr/bin/env bash
# Slice 9 (Deploy Mechanism) regression check.
#
# Verifies the four source-of-record files at the agent-rig repo root are
# byte-identical to their deployed copies under ~/.claude/. Re-runnable at
# any time to catch deploy drift (source edited but not redeployed, or
# deploy target hand-edited directly).
#
# Source: docs/specs/signpost-pillar-propagation/04-ROADMAP.md, Slice 9
# ("Tests" section — this script is those four diff checks).
#
# Exit 0: all four diffs empty (byte-identical).
# Exit 1: at least one diff produced output or a file was missing.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CLAUDE_HOME="${HOME}/.claude"

FAIL=0

check_diff() {
  local label="$1"
  local source="$2"
  local target="$3"

  if [ ! -f "$source" ]; then
    echo "FAIL: $label — source missing: $source"
    FAIL=1
    return
  fi
  if [ ! -f "$target" ]; then
    echo "FAIL: $label — deploy target missing: $target"
    FAIL=1
    return
  fi

  local diff_output
  diff_output="$(diff "$source" "$target")"
  if [ -n "$diff_output" ]; then
    echo "FAIL: $label — diff produced output (not byte-identical):"
    echo "$diff_output"
    FAIL=1
  else
    echo "PASS: $label — byte-identical"
  fi
}

check_diff \
  "HOMELAB-CLAUDE.md.template" \
  "${REPO_ROOT}/HOMELAB-CLAUDE.md.template" \
  "${CLAUDE_HOME}/templates/HOMELAB-CLAUDE.md.template"

check_diff \
  "MAP-NOT-ROUTE-BRIEFING.md.template" \
  "${REPO_ROOT}/MAP-NOT-ROUTE-BRIEFING.md.template" \
  "${CLAUDE_HOME}/templates/MAP-NOT-ROUTE-BRIEFING.md.template"

check_diff \
  "ASSERT-CONVENTION.md.template" \
  "${REPO_ROOT}/ASSERT-CONVENTION.md.template" \
  "${CLAUDE_HOME}/templates/ASSERT-CONVENTION.md.template"

check_diff \
  "commands/new-project.md" \
  "${REPO_ROOT}/commands/new-project.md" \
  "${CLAUDE_HOME}/commands/new-project.md"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "RESULT: PASS — all four deploy targets byte-identical to source-of-record."
  exit 0
else
  echo "RESULT: FAIL — deploy drift detected (see above)."
  exit 1
fi
