# Progress: domain-boundary-provenance-hook

## Status: IN_PROGRESS

## Slices
- [x] Slice 1: Probe core — COMPLETE 2026-08-22 (17/17 tests, QC PASS, non-binding Frank check PASS) — `scripts/domain_boundary_provenance_probe.py` (manifest loading/schema validation, path normalization, scan-surface/citation-window detection, track-record writing; AC1-AC7)
- [x] Slice 2: Wrapper, wiring, manifest schema — COMPLETE 2026-08-22 (15/15 wrapper tests, 17/17 probe regression, QC PASS). Wrapper/schema/gitignore only — NOT wired into `.claude/settings.json` (deliberately deferred, separate decision).
- [ ] Slice 3: Self-test fixture corpus + live demonstration — `tests/fixtures/domain_boundary_manifest_fixture.json`, `tests/fixtures/domain_boundary_corpus.json`, real fired-hook demonstration (AC7, AC8)
- [ ] **Frank binding forge-gate** — PENDING. Runs once, only after every slice above is checked off. Do not set Status: COMPLETE before this line is checked and its verdict is transcribed into GATE-LOG.md's `## Forge Gate` section.

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
