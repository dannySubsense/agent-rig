# Progress: spec-forge-cadence-refactor

## Status: COMPLETE — forge-gate PASSED (attempt 2/3), Layer 2 PROVISIONAL (project North Star DRAFT)

## Slices
- [x] Slice 1: spec-orchestration-07152026 Scaffold + New Templates — COMPLETE (2026-07-15)
- [x] Slice 2: Interview Mechanism Artifacts — COMPLETE (2026-07-15)
- [x] Slice 3: requirements-extraction Skill Edit — COMPLETE (2026-07-15)
- [x] Slice 4: spec-start.md Rewrite — COMPLETE (2026-07-15)
- [x] Slice 5: spec-orchestration install.sh + README — COMPLETE (2026-07-15)
- [x] Slice 6: forge-07152026 Scaffold — COMPLETE (2026-07-15)
- [x] Slice 7: forge-start.md Rewrite — COMPLETE (2026-07-15)
- [x] Slice 8: forge install.sh + QUICKSTART/README — COMPLETE (2026-07-15)
- [x] Slice 9: Frank Prose Trim (source edit) — COMPLETE (2026-07-15), Danny-approved
- [x] Slice 10: Frank Redeploy (sync) — COMPLETE (2026-07-15)
- [x] Slice 11: Execute install.sh Against Live ~/.claude — COMPLETE (2026-07-15)
- [x] Slice 12: One-Time Propagation Sweep — COMPLETE (2026-07-15), 4/4 checks PASS
- [x] Slice 13: Archive Old Packages — COMPLETE (2026-07-15)

## Current
All 13 slices complete. Forge-gate attempt 1: FAIL (2 blocking findings, both independently verified by wright, not just Frank's report):
- F1: spec-orchestration-07152026/install.sh had no template-install loop — ~/.claude/templates/ never received the 4 new templates. Root cause: forge's installer had the loop, spec-orchestration's never did.
- F2: deployed ~/.claude/commands/spec-start.md + forge-start.md referenced spec-orchestration-07152026/... as repo-local paths for interview-conduct skill + all 3 templates — unresolvable in any other consumer repo.
Both fixed, both installers re-run, both re-verified directly against live ~/.claude before re-invoking Frank. Minor: INTAKE.md Status line also updated to literal "APPROVED" format. Attempt 2 in progress.

Note: attempt-1 snapshot at .gate-snapshots/forge/attempt-1/ was taken AFTER fixes were applied (sequencing error) — doesn't capture the true failing state. Documented honestly in that directory's SEQUENCING-NOTE.md rather than silently mislabeled. Actual attempt-1 failure state is fully documented in conversation history instead.

Persona question resolved: attempt 2 confirmed running the trimmed definition (self-referential fingerprint — describes its own trim, which pre-trim Frank couldn't). Attempt 1's provenance stays unconfirmed but no longer matters.

## Forge-Gate Attempt 2 — PASS
- Layer 1: PASS — F1/F2 fixed at the source (package == deployed, byte-identical), re-verified independently by Frank against live files.
- Layer 2: PASS — PROVISIONAL (docs/NORTH-STAR.md Status: DRAFT). Re-run once Lumen's wholesale swap lands.
- Non-blocking notes on record: attempt-1 snapshot sequencing error (moot, loop didn't reach attempt 3); this sprint ships GATE-LOG.md's mandate without producing its own (consistent with old-cadence self-execution per INTAKE's own bootstrap note) — cosmetic dogfooding asymmetry, not a package defect.

Sprint COMPLETE. All 13 slices + forge-gate PASS. Remaining: Danny's call on final commit (chosen cadence: one commit at sprint end).
Last updated: 2026-07-15

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|

## Notes
- No `docs/INVARIANTS.md` or `docs/CADENCE.md` exist in this repo — running under current (pre-trim) `forge-start.md`'s "if exists" behavior, per `INTAKE.md`'s own Sequencing note. Fixing this exact gap is Slice 7's job (forge-start.md rewrite), not a precondition for this sprint's own execution.
- Slice 9/10 boundary is a hard manual gate — Danny must explicitly approve the Slice 9 diff before Slice 10 (redeploy) runs. Not delegable to Frank (he's the subject of the change).
- Slices 1-5 (spec-orchestration) and 6-8 (forge) have no file overlap; could parallelize, but running sequentially for this session's clarity.
