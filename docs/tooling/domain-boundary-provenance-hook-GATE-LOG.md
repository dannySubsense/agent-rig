# Gate Log: domain-boundary-provenance-hook

## Spec Gate
Counter: 3/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-08-22 | FAIL | Layer 1 FAIL: F1 (blocking) §5 vs §6 define Edit scan surface two incompatible ways (proximity-window content vs. full resolved post-edit content); F2 (blocking) grandfathered-match behavior undefined — full-file scan denies edits on pre-existing uncited matches the edit never touched, no v1 answer given; F3 (minor) glob semantics named ambiguously (fnmatch vs pathlib.match). Layer 2 PASS, non-PROVISIONAL (NORTHSTAR.md Established, non-DRAFT). | .gate-snapshots/domain-boundary-provenance-hook/spec/attempt-1/ |
| 2 | 2026-08-22 | FRANK: PASS (Layer 1 + Layer 2, non-PROVISIONAL); ORCHESTRATOR OVERRIDE: not advanced to Step 9 | Frank's attempt-2 PASS verdict verbatim (F1/F2/F3 all confirmed genuinely resolved, no stragglers, 2 minor non-blocking nits noted). **Orchestrator's own independent review (required on every PASS, not perfunctory) found a real, unflagged gap**: §4 defines `pipelineConfigGlobs` as repo-root-relative; §6 step 3 says "resolve the file path being written (`tool_input.file_path`)" against those globs but never states the normalization step (stripping `$CLAUDE_PROJECT_DIR`/cwd prefix from the real, absolute `tool_input.file_path` Claude Code's PreToolUse envelope carries) needed before `fnmatch.fnmatch()` can ever match. Unaddressed, this makes the hook silently inert on real absolute paths while appearing correct against self-authored (already-relative) fixtures — same class of defect as F1/F2 (unstated core-logic assumption), failing in the silent-allow direction. Treated as blocking, same as a FAIL — routed to @architect for fix, Frank re-invoked for attempt 3 (final). | .gate-snapshots/domain-boundary-provenance-hook/spec/attempt-2/ |
| 3-supp | 2026-08-22 | PASS (supplementary, post-approval-request) | Danny objected at Step 9 review to deferring the PreToolUse deny-schema question to forge, citing this repo's own precedent (first-turn-contract-enforcement resolved an identical unknown at spec time via live capture, not forge). Orchestrator ran a real live test in-session: throwaway PreToolUse hook, real Write call, genuine block observed with the hook's own reason string surfaced by the harness. Confirmed shape: top-level `{"decision": "block", "reason": "<text>"}`, same as Stop. Also independently confirmed `tool_input.file_path` is genuinely absolute (backs §6 step 3's normalization fix). Cleanup verified clean (`git status --porcelain`). @architect folded the confirmed finding into §3/§7/§12, removing all deferral language for this item. Frank verified independently — sibling-hook shape claim checked against the real file, not the doc's citation; scope honestly limited to `Write`, `Edit` explicitly named untested. PASS. | n/a (targeted revision, not a snapshot-worthy full-doc attempt) |
| 3 | 2026-08-22 | PASS (final) | Layer 1 PASS: §6 step 3 rewritten with explicit normalization algorithm (`os.path.realpath` both sides, `os.path.commonpath` containment check, prefix-strip, POSIX conversion), edge case (path outside repo root → allow) stated explicitly, sibling-hook non-transfer claim independently verified true against real files (`first_turn_contract_probe.py:29`, `first-turn-contract.sh:10` — script-location resolution, wrong mechanism for a target-repo-resolving hook), AC7 gained the exact fixture pair that would have caught the original gap. Convergence: SHRINKING (3 findings → 1 → 0, each attempt's diff targeted and complete). Layer 2 PASS, non-PROVISIONAL, unchanged. Orchestrator's own final independent read (§4/§6/AC7 re-verified directly) found no further issues — concurs with Frank's PASS. | .gate-snapshots/domain-boundary-provenance-hook/spec/attempt-2/ (pre-fix) |

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]

## Forge Gate
Counter: 0/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]
