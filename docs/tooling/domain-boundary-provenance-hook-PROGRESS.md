# Progress: domain-boundary-provenance-hook

## Status: IN_PROGRESS

## Slices
- [ ] Slice 1: Probe core — `scripts/domain_boundary_provenance_probe.py` (manifest loading/schema validation, path normalization, scan-surface/citation-window detection, track-record writing; AC1-AC7)
- [ ] Slice 2: Wrapper, wiring, manifest schema — `.claude/hooks/domain-boundary-provenance.sh`, `docs/tooling/domain-boundary-manifest.schema.json`, `.claude/settings.json` PreToolUse entry (AC5, AC6)
- [ ] Slice 3: Self-test fixture corpus + live demonstration — `tests/fixtures/domain_boundary_manifest_fixture.json`, `tests/fixtures/domain_boundary_corpus.json`, real fired-hook demonstration (AC7, AC8)
- [ ] **Frank binding forge-gate** — PENDING. Runs once, only after every slice above is checked off. Do not set Status: COMPLETE before this line is checked and its verdict is transcribed into GATE-LOG.md's `## Forge Gate` section.

## Current
Slice: 1
Step: @code-executor
Last updated: 2026-08-22

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|

## Notes
- Branch: `feature/domain-boundary-provenance-hook`, draft PR #11.
- Spec: `docs/tooling/domain-boundary-provenance-hook.md` (LOCKED).
- Slicing derived from the spec's own component table (§6) and AC list (§8), following
  `first-turn-contract-enforcement`'s precedent shape (probe core → wrapper/wiring → live
  demonstration), same architecture family.
