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
- [x] Slice 3: Fixture corpus + live demonstration — COMPLETE 2026-08-23 (55/55 probe+corpus,
      15/15 wrapper, 2 rounds of QC — first FAIL was real: a fixture claimed to test AC7b's honest
      residual but actually tested a happy path). Both Carried Conditions resolved: timeout
      measurement (real pytest proof, ~2.1s median vs. 25s/30s budget, ~12x headroom) and Edit
      envelope live-verification (confirmed via throwaway hook; found and documented a previously
      unknown `replace_all` field, confirmed harmless to the probe, §7/§12 updated). Advisory,
      non-blocking: no raw capture payload artifact committed for the replace_all observation —
      cite this file if reproducibility is ever needed.
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
  3. **RESOLVED 2026-08-24.** Two-call cross-edit dodge — Danny decided: accept as residual, do not
     build cross-call state tracking. Same decision framework as the SLICE-ID-mutation case (item
     4 below): match effort to actual stakes (self-honesty, not adversarial security); don't spend
     more to close the easier gap than was spent on the harder one. Recorded in SPEC.md §12 item 1
     with full rationale.
  4. Next-revision items, non-blocking, from forge-gate PASS: `transitions_found` counts
     deny/ambiguous events beyond spec §6 step 11's literal allow-only definition (track-record
     semantics only); an empty `SLICE-ID:` token is accepted as a valid key (no bypass power).
