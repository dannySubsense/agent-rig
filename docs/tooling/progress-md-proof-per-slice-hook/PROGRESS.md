# Progress: progress-md-proof-per-slice-hook

## Status: IN_PROGRESS

## Slices
- [x] Slice 1: Probe core — COMPLETE 2026-08-23 (34/34 tests, QC PASS). Identity-based matching
      (SLICE-ID primary, description/PROOF fallback) implemented per the current, redesigned §6 —
      not the earlier positional design superseded during spec review. Two non-blocking QC notes:
      `transitions_found` counts denials too (only defined for allow branch in spec); empty
      `SLICE-ID:` token accepted as a valid key (no bypass power granted, worth a guard later).
- [x] Slice 2: Wrapper, allowlist, wiring prep — COMPLETE 2026-08-23 (15/15 wrapper tests, 34/34
      probe regression, QC PASS). `$CLAUDE_PROJECT_DIR` guarantee correct on first pass this time
      (sibling hook's Slice 2 bug not repeated). NOT wired into `.claude/settings.json` — deliberate.
- [ ] Slice 3: Fixture corpus + live demonstration — full AC suite as reusable fixtures, real
      fired-wrapper demonstration (the sibling's Slice 3 caught a real exec-bit bug this way).
- [ ] **Frank binding forge-gate** — PENDING. Runs once, after every slice above is checked off.
      Do not set Status: COMPLETE before this line is checked and its verdict is transcribed into
      GATE-LOG.md's `## Forge Gate` section.

## Current
Slice: 3
Step: @code-executor
Last updated: 2026-08-23

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|

## Notes
- Branch: `feature/progress-md-proof-per-slice-hook`, draft PR #13.
- Spec: `docs/tooling/progress-md-proof-per-slice-hook/SPEC.md` (LOCKED) — went through 7 rounds of
  post-approval gate revision (mutation-bypass closure, identity-matching redesign, SLICE-ID
  addition) before reaching final PASS; see GATE-LOG.md for the full history.
- Two Carried Conditions from the spec-gate PASS, per `agents/frank.md`'s new rule — must be
  addressed before this sprint is treated as fully closed:
  1. PROVISIONAL constants (allowlist content, 25s inner / 30s outer timeouts) — forge must measure
     against real proof commands before treated as settled.
  2. `Edit`-specific PreToolUse envelope shape — never live-verified (only `Write` was, for the
     sibling hook). Must confirm via the same throwaway-hook live-capture method before wiring
     anything live.
  3. Open decision for Danny at forge kickoff, not yet decided: the two-call cross-edit dodge —
     accept as residual (same reasoning as the SLICE-ID-mutation case) or close it.
