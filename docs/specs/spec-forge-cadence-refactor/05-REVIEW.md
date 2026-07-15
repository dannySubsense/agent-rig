# Spec Review: Spec/Forge Cadence Refactor

**Status**: Complete — independent re-review (v3, post-reconciliation)
**Author**: spec-reviewer (dispatched by wright)
**Date**: 2026-07-15
**Reviewed**: `INTAKE.md`, `INTERVIEW.md`, `01-REQUIREMENTS.md` (12 US / **46 ACs** — see note), `02-ARCHITECTURE.md` (12 components / 6 schemas), `04-ROADMAP.md` (13 slices)
**No `03-UI-SPEC.md`**: confirmed correct — no user-facing UI this sprint. Not a gap.

**This is the third fresh pass.** After my v2 re-review, the coordinator reported all four v2 findings (F1-F4) addressed. I re-verified all three docs from scratch and grepped every term that lagged in prior cycles (`2-3 sentences`, `~6`, `≥40%`, `manifest-diff`, bare `Fix}`, component counts, `PROVISIONAL`, `Fix/Next-step`). **All four findings are genuinely resolved and — this time — consistently rippled across 01, 02, and 04.** One trivial residual remains (an AC-count citation), described below; it is a one-line doc-hygiene fix, not a blocker.

---

## Verdict

**READY FOR FORGE — clean.**

Plainly: this is clean. All 46 ACs have architecture coverage, all 12 components land in a slice, no out-of-scope item reintroduced, and the cross-document consistency that lagged through two prior cycles now holds on every term I checked. The only thing I found is a stale AC-count citation in the roadmap's Inputs line (45 → should be 46, a direct artifact of the F4 fix adding a 10th AC to US5). I am not inflating it into a finding it isn't: it changes no behavior, blocks nothing, and can be fixed in one line whenever convenient.

---

## Independent Verification — v2 Findings Now Resolved

| v2 finding | Re-verified in current docs | Status |
|---|---|---|
| F1 — "2-3 sentences" survived in roadmap Slice 9 | `04:248` now reads "no sentence-count target, this is an editorial judgment call (… dropped the earlier unsourced '2-3 sentences' figure)." The only remaining occurrence of the string is inside that explanatory note about what was removed — no live instruction. Matches `02:442`. | **Resolved** |
| F2 — roadmap said "Fix" not "Fix/Next-step" | `04` Slice 9 now uses `Fix/Next-step` at the goal (`04:239`), the literal header (`04:252`: `Fix/Next-step (FAIL/HALT only):`), and the done-when (`04:258`, greps for that exact string). No bare `{…, Verdict, Fix}` remains anywhere in 01/02/04. Consistent with `01:105`, `02:147/435`. | **Resolved** |
| F3 — Layer-1/2-every-attempt, PROVISIONAL, NORTH-STAR-at-approval not in roadmap done-when | Slice 4 now carries all three as concrete implementation notes (`04:147-148`) and as three distinct checkable done-when items (`04:155-157`). Slice 7 mirrors them for the forge-gate (`04:209, 215-216`). | **Resolved** |
| F4 — DRAFT→PROVISIONAL was architecture-only, unratified, no AC | Danny ratified it; `01` now carries it as an explicit US5 AC (`01:73`, including the note that it applies to this sprint's own DRAFT-`docs/NORTH-STAR.md` forge-completion gate) and an Edge Cases row (`01:159`). Consistent with `02:88/91/135/261/271`. | **Resolved (ratified + AC'd)** |

Cross-checked the whole PROVISIONAL chain end-to-end: requirements AC (`01:73`) → edge case (`01:159`) → NORTH-STAR schema status line (`02:88`) → Frank-gate OBJECTIVE (`02:261`) → orchestrator PASS branch carry-through (`02:271`) → spec-gate done-when (`04:156`) → forge-gate done-when (`04:216`). All seven agree, including that a PROVISIONAL pass still counts as PASS (non-blocking) with the tag carried through to human approval and re-run when the project North Star reaches non-DRAFT. No contradictions.

---

## Remaining Residual (trivial)

| # | Item | Location | Severity |
|---|---|---|---|
| N1 | The F4 fix added a 10th AC to US5, so the true total is **46 ACs**, but the roadmap's Inputs line still cites "45 ACs." (Requirements and architecture headers cite no AC count, so this is the only stale spot.) | `04-ROADMAP.md:6` | Trivial doc-hygiene — one-line fix, no behavioral impact |

This is the same count-drift-after-an-edit pattern as the earlier 11→12 component fix — surfaced here only because it recurred, not because it matters on its own. Recommend the planner update `04:6` to "46 ACs" (or drop the number). It does not gate forge.

---

## Coverage (re-confirmed)

**Requirements → Architecture:** all 46 ACs map. US5's 10 ACs (including the new PROVISIONAL AC) are covered by the Frank binding-gate contract, the NORTH-STAR schema, GATE-LOG, snapshots, and the independent re-derivation algorithm. US1-US4, US6-US12 unchanged from v2 and still fully covered. The manifest-diff cut continues to *strengthen* US11/US12 traceability rather than leave a hole (no file is removed/renamed this sprint, so overwrite-only install + the one-time grep sweep genuinely satisfies "not additive-only").

**Architecture → Roadmap:** all 12 components in a slice; count consistent at 12 across `02` table, `04:6/8` header, and both `04` coverage tables. Dependency map acyclic; live/stateful slices 10-13 correctly serialized; every slice has a concrete non-prose Done-When.

**Scope boundaries:** all seven exclusions intact (03-UI-SPEC, `/new-project` wiring, gap-lens reconciliation, `franks-lessons`, project-North-Star authoring, `-03132026` archives, and the newly-deferred subtractive-install mechanism). The `security-loop.md` → archived `senior-qc` item remains correctly out of scope in both `02` and `04:314`.

---

## Identified Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | DRAFT→PROVISIONAL means this sprint's own Layer 2 (against DRAFT `docs/NORTH-STAR.md`) is a *provisional* pass — weaker relevance assurance until Lumen's template lands and the gate is re-run. | M | M | Designed, not silent: PROVISIONAL tag + carry-through to human approval + mandatory re-run (`01:73`, `02:271`). Now a ratified AC, so Danny has consciously accepted it. |
| R2 | Self-referential execution: this spec is gated by **pre-trim Frank**, which lacks the Layer 1/2, PROVISIONAL, and convergence logic this sprint adds — so the new gate is never validated against itself before shipping. | M | M | Unavoidable bootstrap (Intake Sequencing). Optional confidence check: re-gate these docs under trimmed Frank after Slice 10. |
| R3 | `security-loop.md`'s stale `senior-qc` reference stays live in `~/.claude` while the sprint advertises a "thorough sweep." | L | L | Log as a tracked backlog/DDR follow-up (Q1 below). |
| R4 | The count/number-drift-after-edit pattern has now appeared four times across the review cycles (11→12 components, ≥40%, manifest survivals, and now 45→46 ACs). | L | L | Cheap systemic guard: after any doc edit that changes a countable set, re-run the cross-doc number sweep. N1 is the only open instance and is trivial. |

v2's manifest-related risks stay resolved/moot (component cut).

---

## Assumptions (unchanged, still holding)

| # | Assumption | Impact if Wrong |
|---|---|---|
| A1 | Lumen's project North Star template replaces `docs/NORTH-STAR.md` wholesale; consumed as schema+location. | If Lumen's schema diverges from the `docs/NORTH-STAR.md`-at-that-path interface, Layer 2 breaks for every consumer until reconciled. Coordinate via Switchboard before finalizing. |
| A2 | `~/.claude` sweep reaches all four consumers; only gap-lens carries a local copy (grep-verified). | An unlisted local copy would keep old gates. Compensated by grep verification. |
| A3 | This repo IS the install source; `~/.claude` currently byte-identical to vendored packages. | If drifted, overwrite could clobber a local change. Slice 11/12 diffs are the check. |
| A4 | No file is removed/renamed this sprint, so overwrite-only install needs no subtractive step. | Confirmed from the package layout. If a later edit drops a file, the Slice 12 grep sweep is the catch until the deferred subtractive mechanism is built. |
| A5 | Pre-trim Frank is an adequate gate for this spec (Intake Sequencing). | If it misses what the new logic would catch, the spec ships unvalidated by its own new standard (R2). |

---

## Open Questions (standing human-gate acknowledgments — none are defects)

| # | Question | Status | Needs |
|---|---|---|---|
| Q1 | Log `security-loop.md`'s stale `senior-qc` reference as a tracked backlog/DDR follow-up, rather than only an in-doc observation? | Open | Danny's call |
| Q2 | Accept shipping this spec gated by pre-trim Frank without the sprint's own new gate logic validating it (R2, bootstrap)? | Open | Danny's conscious acceptance |

The v2 PROVISIONAL-ratification question is **resolved** — Danny ratified it and it is now an explicit AC. The v1 manifest-diff scope question is **resolved** — cut.

---

## Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [x] 46/46 ACs testable
- [x] Out of scope explicit and non-empty
- [x] PROVISIONAL rule ratified and captured as an AC (`01:73`) + edge case (`01:159`)

### Architecture (02)
- [x] Every AC has architecture coverage (46/46)
- [x] Schemas concrete; anti-patterns named; manifest-diff scope-creep cut
- [x] Frank fixes 1-4 verified present and rippled
- [ ] Reviewed by human

### UI Spec (03)
- [x] N/A — no user-facing UI (confirmed, not a gap)

### Roadmap (04)
- [x] All 12 components in a slice; acyclic; live slices serialized
- [x] Slice 9 reconciled (Fix/Next-step label + de-numbered prose-trim) — verified
- [x] Slice 4/7 done-when carry Layer-1/2-every-attempt, PROVISIONAL, and NORTH-STAR-at-approval — verified
- [ ] Optional one-line fix: update AC count 45 → 46 (`04:6`) — N1, non-blocking
- [ ] Reviewed by human

### Overall
- [x] All prior findings (F1-F4) resolved and verified
- [x] All risks have mitigations
- [ ] Q1-Q2 acknowledged by Danny at his gate
- [ ] Danny consciously accepts the pre-trim-Frank self-gate bootstrap (R2)

---

## Summary for the Frank Gate

Three review cycles in, the docs have converged. Every substantive finding from v1 and v2 is closed and — verified independently this pass — consistently reflected across requirements, architecture, and roadmap, including the full PROVISIONAL chain end-to-end and the Frank verdict label. The reconciliation lag that produced repeat findings in earlier cycles is gone; the sole residual is a trivial "45 vs 46 ACs" citation in the roadmap's Inputs line, which changes nothing and is a one-line fix. This is READY FOR FORGE. The only items left for Danny are two standing acknowledgments (log the pre-existing `security-loop.md` staleness as a follow-up; consciously accept that this sprint is bootstrap-gated by pre-trim Frank) — neither is a defect in the spec.
