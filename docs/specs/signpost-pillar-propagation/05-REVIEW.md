# Spec Review: Signpost→Pillar Propagation

**Status**: PASS — F1 and F2 fixed and independently re-verified 2026-08-08 (see addendum below). Ready for Frank's gate.

**Addendum (2026-08-08, post-pass-3):** F1 fixed — 02's Citation Constraints §1 now enumerates Components 4, 5, 6, 7, 8 (verified: line 65); 04's Slices 4 and 7 each carry the caveat-1 Done-When item (verified). F2 fixed — 04 Slice 1's checked item now accurately describes `ALPHA-REPORT-REVIEW.md`'s real structure (8 directly-verified claims, could-not-verify list, one global `SAFE TO CITE` verdict + 2 caveats — no per-item table). Separately, Frank's blind consistency review (no briefing) caught a defect this document's three passes did not: 02 and 04 cited department-os's live file paths as the probe/hook reference implementation, and department-os's checked-out branch had since moved, making those citations dead. Fixed by pulling the proven artifacts directly into agent-rig's own `reference/session_probe.py` and `reference/session-start-probe.sh` — verified standalone, zero dependency on any consumer repo. 02 and 04 updated accordingly; Slice 2 marked satisfied.
**Reviewer**: spec-reviewer (independent of Wright)
**Date**: 2026-08-08
**Pass**: 3 (final pre-gate re-review)
**Docs reviewed**: `01-REQUIREMENTS.md`, `02-ARCHITECTURE.md`, `04-ROADMAP.md`, plus
`INTAKE.md`, `INTERVIEW.md`, `NORTH-STAR.md`, `ALPHA-REPORT-REVIEW.md` as context.
**No `03-UI-SPEC.md`**: correct — this sprint ships no UI surface. Not counted as a gap.

---

## Part A — Verification of Pass-2 Defects (N1–N8)

Each verified by reading current doc text, not by trusting the fix reports.

| # | Defect (pass 2) | Current state | Verdict |
|---|---|---|---|
| N1 | Stale Frank/Wright text in 02 Component 10 | 02 L41 now reads "reviewer is Frank only, not Wright — doer=checker avoidance, since Wright authored this propagation architecture". Matches 01 US-9 AC1 and Constraint L152. 02's US-9 Gate section (L425-426) says the same. | **RESOLVED** |
| N2 | Slice-number drift between 01 and 04 | 01 L113 ("Slices 1-9 complete + Slice 10 pilot `market_data`; Slices 11/12 = 7 named projects, non-blocking") is now byte-consistent with 04's Slice Overview, Forge-Closability note (L79-82), and Sequence Rule 7. Roster names match in all three places. | **RESOLVED** |
| N3 | `timeout=15` conflict between 02 and 04 | 02 L115-119 drops the inner kwarg outright (outer `timeout 5` is sole enforcement); 02 API Contract `_run()` docstring (L199-202) matches; 04 Slice 2 note (L169-171) says "drop … not comment it out or leave it dormant" and Slice 2 Done-When L193 verifies by reading the file. No residual `timeout=15` anywhere as a live value. | **RESOLVED** |
| N4 | Frank's two caveats never propagated as enforceable constraints | Now three-layer: 01 Cross-cutting ACs L114/L115 + Constraints L153/L154; 02 new "Citation Constraints (per Component 10 / US-9 Gate)" section L55-89; 04 Slice 1 note L117-126 + Slice 5 Done-When L339-341 + Slice 6 Done-When L384-389. Caveat text traces to `ALPHA-REPORT-REVIEW.md` L36-39 accurately. | **RESOLVED — but see F1: propagation is incomplete on Components 4 and 7** |
| N5 | Slice 1 Done-When pre-checked before its condition could be true | 04 L132-138: the forward-looking item is removed from Slice 1's Done-When, replaced by an explicit note, and re-homed unchecked on Slice 2 (L197), Slice 5 (L342), Slice 6 (L390). | **RESOLVED** (a related overstatement remains — see F2) |
| N6 | Slice 2 dependency stated inconsistently | Now identical in all four places: Overview table L61 "1 (existence only)", Dependency Map L35-36, Slice 2 Depends On L148-149, Sequence Rule 2 L616-622. | **RESOLVED** |
| N7 | Frank's 0.7s measurement unused | 04 Slice 2 L172-175 cites it as a Pillar-level corroboration of the 5s PROVISIONAL budget (~7x headroom) and Done-When L195-196 requires both figures in any code comment. | **RESOLVED** |
| N8 | No byte-equality test between staged reference and scaffolded output | 04 Slice 3 Tests L253-257 adds the two `diff` checks with explicit "byte-identical, not merely based on" language; Done-When L264 mirrors it. | **RESOLVED** |

**8 of 8 pass-2 defects confirmed fixed in current text.**

---

## Part B — New Findings Introduced or Left by This Round

### F1 (MEDIUM — recommend fixing before the gate). Caveat-1 propagation is narrower in 02/04 than 01 requires.

01's Cross-cutting AC (L114) names **five** items as practice-only that must never be implied to be
mechanically enforced: US-4 (Signpost/Pillar), US-5 (map-not-route), US-6 (capture schema), US-7
(assert doc), US-8 (sentinel doc). Constraint L153 repeats "US-4 through US-8."

But:
- 02's Citation Constraints §1 (L65-66) binds only **Components 5, 6, 8** — Component 4 (US-4) and
  Component 7 (US-6) are absent from the enumerated list.
- 04 carries the caveat as a Done-When item only on **Slice 5** and **Slice 6**. **Slice 4** (US-4,
  L298-300) and **Slice 7** (US-6, L418-419) carry no such check.

Effect: an AC in 01 has no architectural binding and no roadmap verification point for two of the
five items it names. This is a requirements→architecture→roadmap coverage break, exactly the class
of gap Frank's own caveat 1 exists to prevent, and it was introduced by the N4 fix itself
(partial propagation of a constraint about incomplete propagation).

**Fix (small):** add Components 4 and 7 to 02's Citation Constraints §1 enumeration, and add the
same one-line Done-When item already present on Slices 5/6 to Slices 4 and 7.

### F2 (MEDIUM). Slice 1's checked `[x]` test overstates what `ALPHA-REPORT-REVIEW.md` actually contains.

04 L129-130 marks complete: "`ALPHA-REPORT-REVIEW.md` exists and **names every recommendation this
sprint draws from the handoff report, with an explicit per-item verdict.**" L112-113 repeats this as
"Per-recommendation outcome (pass/concerns/rejected) for every item … is recorded in that artifact."

The artifact does not do this. It contains a numbered list of **8 claims Frank verified directly**, a
**3-item "could NOT verify"** list, and a single global verdict (`SAFE TO CITE` + 2 caveats) with one
collective sentence (L41) covering the four propagated mechanisms. There is no per-recommendation
verdict table. The substance is adequate — every propagated mechanism is covered collectively and the
"could NOT verify" residue demonstrably does not intersect them — but the checked box asserts a
document structure that isn't there. This is the same failure shape as N5 (a `[x]` whose stated
condition isn't demonstrably true), and it is the one place in the doc set where a claim is asserted
rather than verified against the artifact.

**Fix:** reword to match reality, e.g. "`ALPHA-REPORT-REVIEW.md` exists, records a global verdict
(`SAFE TO CITE`) with two mandatory caveats, and its 'could NOT verify directly' list contains no item
this sprint propagates." Then re-check. Same edit applies to L112-113.

### F3 (LOW). `RETROFIT-PROCEDURE.md` has no distribution path to the resident agents who must run it.

02 Component 9 and 04 Slice 8 place it at `docs/specs/signpost-pillar-propagation/RETROFIT-PROCEDURE.md`
— agent-rig-local, explicitly *not* deployed to `~/.claude/` (Slice 9 deploys four other files) and
explicitly not importable by symlink/submodule (02 L442). How a resident agent in `sonic-store`
obtains it is unstated. Probably fine in practice (absolute path on the same host), but Slices 10-12
depend on an artifact with no defined hand-off mechanism, in a sprint whose thesis is
"documented ≠ installed."

### F4 (LOW, 4 instances). Directional cross-reference errors in 02.

- L69-70 "this document's Pattern choice … — Patterns table **above**" — the Patterns table is at
  L250, *below* Citation Constraints (L55).
- L434 "see 'Citation Constraints …' **below**" — that section is at L55, *above* L434.
- L468-469 "deploy … is Component 11 (see Deploy Mechanism **below**)" — Deploy Mechanism is L370,
  *above* Integration Points (L453).
- L73 "as an existing or retrofit-item-6 mechanism" is garbled; "retrofit item 6" is Frank's own
  parenthetical label, not a mechanism class.

Cosmetic, but Citation Constraints is the section Frank will read most closely, and two of the four
are inside or pointing at it.

### F5 (LOW). 04 Slice 9's D1 parenthetical (L472-475) is self-negating.

"…created (new file at deploy target; omitted only if D1 is later revisited to bundle into
`HOMELAB-CLAUDE.md.template` instead — not expected, since D1 is already resolved as
combined-file-as-Component-6/8, distinct from the D1 caveat this sentence flags for completeness)."
D1 is resolved (L73-77). Delete the hedge; it reads as an unresolved decision that isn't one.

### F6 (LOW). `reference/` staging directory exists only in 04.

04 Slice 2 introduces `reference/session_probe.py` and `reference/session-start-probe.sh` as an
agent-rig-local staging location with a stated rationale (reviewable diff independent of the
command-file edit). 02's Component 1/2 rows name only the scaffold-target paths. The roadmap justifies
the addition and Slice 3's byte-equality check (N8's fix) makes the two locations self-reconciling, so
this is acceptable roadmap-level detail — noted only so Frank doesn't read it as unsanctioned drift.

---

## Requirements → Architecture Coverage

| Requirement | Architecture Coverage | Status |
|---|---|---|
| US-1 probe hook scaffolded | Components 1, 2, 3; Integration Points (`new-project.md`) | ✅ |
| US-2 probe first, fails loud | Component 2; Hook output contract element 2; Patterns row 1 | ✅ |
| US-3 self-disclaiming | Component 2; `additionalContext` composition elements 1 & 4; Patterns row 2 | ✅ |
| US-4 Signpost/Pillar labeling | Component 4 (`HOMELAB-CLAUDE.md.template`) | ⚠️ covered, but excluded from Citation Constraints §1 (F1) |
| US-5 map-not-route | Component 5; Backlog Reconciliation (item 25 kept separate) | ✅ |
| US-6 capture verification lines | Component 7; `DurableCapture` schema | ⚠️ covered, but excluded from Citation Constraints §1 (F1) |
| US-7 assert convention | Component 6; `assert_*.py` API contract | ✅ |
| US-8 sentinel pattern | Component 8 (bundled with 6, rationale stated) | ✅ |
| US-9 alpha report reviewed by Frank | Component 10; US-9 Gate section; Citation Constraints | ✅ |
| US-10 per-project retrofit + own Frank gate | Component 9; Retrofit Mechanism; `RetrofitAuditRecord` | ✅ |
| CC: no DDR-0009 "documented not installed" state | Component 11 Deploy Mechanism + diff verification | ✅ |
| CC: every number sourced | Probe Runtime Budget (3s sourced, 5s PROVISIONAL/wright, 0.7s Frank-measured) | ✅ |
| CC: deployment verified by diff | Deploy Mechanism §Verification | ✅ |
| CC: forge closability | Not restated in 02; carried by 01 + 04 | ✅ (acceptable — sequencing, not architecture) |
| CC: caveat 1 (no implied enforcement) | Citation Constraints §1 | ⚠️ **F1** — covers 5/6/8 only, 01 names 4 and 7 too |
| CC: caveat 2 (§2.5 heuristic) | Citation Constraints §2 | ✅ |

## Architecture → Roadmap Coverage

| Component | Slice | Status |
|---|---|---|
| 1 `session_probe.py` generalized | 2 | ✅ |
| 2 hook wrapper | 2 | ✅ |
| 3 SessionStart wiring | 3 (D2 resolved: create, not merge) | ✅ |
| 4 Session Start Behaviour block | 4 | ⚠️ missing caveat-1 Done-When (F1) |
| 5 map-not-route template | 5 | ✅ |
| 6 assert convention | 6 (D1 resolved: combined file) | ✅ |
| 7 capture schema | 7 | ⚠️ missing caveat-1 Done-When (F1) |
| 8 sentinel pattern | 6 (bundled) | ✅ |
| 9 retrofit procedure | 8 | ⚠️ no distribution path (F3) |
| 10 alpha-report review record | 1 (already satisfied) | ⚠️ Done-When overstates artifact (F2) |
| 11 deploy mechanism | 9 | ✅ |
| Open item D1 | Resolved in 04 L73-77 | ✅ |
| Open item D2 | Resolved in 04 L7-24 (read `new-project.md` this session) | ✅ |
| Open item D3 (pilot project) | Slice 10 `market_data`, explicitly non-binding | ✅ |

**Dependency-cycle check:** none. Slice 1 is existence-only; 2-7 mutually independent; 8 and 9 both
gate on 3-7 and are parallel to each other; 10 requires 8+9; 11 requires 8+9 (not 10); 12 requires 10.
Acyclic and consistent between the Dependency Map, Slice Overview, and Sequence Rules.

---

## Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| A propagated template implies enforcement for US-4/US-6 that doesn't exist — the exact DDR-0009 trap | M | H | **F1 fix**: extend Citation Constraints §1 to Components 4/7 and add the Done-When to Slices 4/7 |
| 5s probe budget is PROVISIONAL and unmeasured on retrofit targets | M | L | Owner wright named; hook always exits 0, so a miss degrades to slow UX; replace after first scaffold + first retrofit trace |
| Roster of 8 resident agents never actually executes Slices 11/12; sprint closes and retrofit stalls indefinitely | M | M | Explicitly accepted as ongoing non-blocking state (01 L113, 04 L79-82). Accepted risk, not a defect — but there is no owner or review date on the residue |
| `RETROFIT-PROCEDURE.md` never reaches the agents who must run it | M | M | **F3** — define a hand-off (absolute path in the LORE capture, or deploy to `~/.claude/templates/`) |
| Frank's per-retrofit gates are dispatched by the same agent doing the work, briefed by that agent | M | M | Map-not-route briefing is specified and Frank's verdict is binding; residual risk that "unbriefed" is self-attested (`frankGateUnbriefed: boolean`) with no external check |
| `/new-project` re-run clobbers a hand-added `.claude/settings.json` | L | M | Slice 3 L225-227 specifies create-only with a pre-existence check |
| Reference and scaffolded probe copies drift apart | L | M | Closed by Slice 3's byte-equality diff (N8 fix) |

## Assumptions

| Assumption | Impact if Wrong |
|---|---|
| department-os's `session_probe.py`/hook is already domain-neutral, so Slice 2 is confirmation not rewriting | Slice 2 is materially larger than scoped; Slice 3 slips |
| DDR-014's manual `cp` + `diff` deploy pattern remains the homelab norm | Slice 9's mechanism is wrong; deploy is unverified |
| The retrofit roster is stable and reused as-is from DDR-INDEX | Roster churn invalidates Slices 11/12 scope |
| `frankGateUnbriefed: true` is honestly self-reported by each resident agent | The per-project gate's independence is nominal |
| Danny's Intake Q1 approval (fold DDR-004 into this sprint) holds | US-1/2/3 must be split into a separate spec |

## Open Questions

| Question | Status | Resolution |
|---|---|---|
| Who owns and reviews the Slices 11/12 residue after forge-close, and by when? | Open | Needs a named owner + revisit date, or explicit "no owner, tracked passively" |
| How does `RETROFIT-PROCEDURE.md` reach the 8 resident agents (F3)? | Open | Human/Wright decision: absolute-path reference vs. deploy to `~/.claude/templates/` |
| Should the 5s PROVISIONAL budget be replaced by a measured number before Slice 12 rather than "after first retrofit"? | Open | Low stakes (non-blocking hook); flagging only because it is the sprint's one unsourced constant |

---

## Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [x] All 10 user stories carry acceptance criteria; edge-case table populated (12 rows); out-of-scope non-empty (9 items); constraints concrete
- [x] Both Frank caveats present as Cross-cutting ACs and as Constraints
- [ ] Out of scope acceptable (notably: full roster completion excluded from sprint close)

### Architecture (02)
- [x] Every requirement has a component; Coverage Check table present and accurate
- [x] Schemas are concrete TypeScript / Python signatures, not pseudocode
- [x] Every number sourced, PROVISIONAL-tagged with owner, or deleted (`timeout=15` deleted)
- [x] **F1 fix applied** (Citation Constraints §1 extended to Components 4 and 7 — verified)
- [x] Reference implementation decoupled from department-os's live path; agent-rig's own `reference/` is now source-of-record (fixes the dead-path defect Frank's blind review caught)
- [ ] F4 cross-reference directions corrected (low severity, not blocking)
- [ ] Reviewed by human

### UI Spec (03)
- [x] N/A — no user-facing surface in this sprint

### Roadmap (04)
- [x] Every component mapped to a slice; no circular dependencies; concrete file paths throughout
- [x] D1 and D2 resolved with stated evidence; D3 explicitly non-binding
- [x] **F2 fix applied** (Slice 1 test reworded to match `ALPHA-REPORT-REVIEW.md`'s actual structure — verified)
- [x] F1 Done-When items added to Slices 4 and 7 (verified)
- [x] Slice 2 marked satisfied — `reference/` artifacts exist in agent-rig, verified standalone
- [ ] Reviewed by human

### Overall
- [x] F1 and F2 fixed and independently re-verified
- [x] All risks have mitigations or are explicitly accepted
- [ ] Open questions dispositioned (3 open, none blocking)
- [ ] Ready for implementation (pending human approval)

---

## Verdict

The doc set is **structurally sound and internally consistent**. All 8 pass-2 defects are genuinely
fixed in the current text — verified by reading, not by report. Requirements→architecture→roadmap
coverage is complete except at one seam (F1), the dependency graph is acyclic and stated identically
in all three places it appears, and the sprint's own anti-pattern (documented-but-not-installed) is
closed by Component 11 / Slice 9 with a diff-verified Done-When.

**Not blocking, but should be fixed before the gate:** F1 (a Cross-cutting AC in 01 with no
architectural binding and no roadmap check for 2 of the 5 items it names) and F2 (a checked `[x]`
asserting a property the referenced artifact does not have). F1 is the more serious of the two — it
is a partial propagation of the very constraint that forbids partial propagation, and it is the kind
of thing Frank found last time. F3–F6 are low severity and can ship as-is.

No HALT conditions. No fundamental inconsistency between documents.
