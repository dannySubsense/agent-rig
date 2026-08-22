# Progress: domain-boundary-provenance-hook

## Status: COMPLETE — Frank binding forge-gate PASS (both layers, non-PROVISIONAL, attempt 1/3), logged in GATE-LOG.md. Not wired into `.claude/settings.json` — separate, deliberate, unmade decision.

## Slices
- [x] Slice 1: Probe core — COMPLETE 2026-08-22 (17/17 tests, QC PASS, non-binding Frank check PASS) — `scripts/domain_boundary_provenance_probe.py` (manifest loading/schema validation, path normalization, scan-surface/citation-window detection, track-record writing; AC1-AC7)
- [x] Slice 2: Wrapper, wiring, manifest schema — COMPLETE 2026-08-22 (15/15 wrapper tests, 17/17 probe regression, QC PASS). Wrapper/schema/gitignore only — NOT wired into `.claude/settings.json` (deliberately deferred, separate decision).
- [x] Slice 3: Self-test fixture corpus + live demonstration — COMPLETE 2026-08-22 (27/27 probe+corpus, 15/15 wrapper, QC PASS). **Found and fixed a real bug**: probe script lacked its executable bit, so the wrapper had never successfully executed it — every real invocation would have silently fail-opened via exit 126. Fixed (chmod +x), re-verified independently by QC (reproduced the exit-126 failure, confirmed the fix, fired the real wrapper end-to-end for deny and allow). Timeout measured: ~60ms probe-only median, ~140ms wrapper end-to-end, 5s bound retained (>50x headroom).
- [x] **Frank binding forge-gate** — PASS, both layers, non-PROVISIONAL, attempt 1/3. Verdict in GATE-LOG.md's `## Forge Gate` section.

## Current
Slice: 3
Step: @code-executor
Last updated: 2026-08-22

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| test_domain_boundary_provenance_wrapper.sh (Test 5) | 1 | RESOLVED — test bug, not wrapper bug: test checked wrapper's own stderr for the probe's SET/UNSET message, but the wrapper only surfaces probe stderr via the track-record entry's probe_error field, never its own stderr. Test fixed to read the track-record file. 15/15 wrapper tests + 17/17 probe tests pass. |

## Notes
- Branch: `feature/domain-boundary-provenance-hook`, draft PR #11.
- Spec: `docs/tooling/domain-boundary-provenance-hook.md` (LOCKED).
- Slicing derived from the spec's own component table (§6) and AC list (§8), following
  `first-turn-contract-enforcement`'s precedent shape (probe core → wrapper/wiring → live
  demonstration), same architecture family.
