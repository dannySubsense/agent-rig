# Progress: signpost-checklist-redesign

## Status: IN_PROGRESS

## Slices
Build order per 04-ROADMAP.md's Dependency Map (not file order — Sequence Rule 1):
- [x] Slice 1: Data Schemas + New Verbatim Parsers — COMPLETE (2026-09-07, commit `2d51db0`, unpushed). One real QC FAIL found and fixed (markup-styled heading stripping), re-verified PASS.
- [x] Slice 2: Reused Trigger-Surface / Tool-Call-Collection Functions — COMPLETE (2026-09-07). One real regression found and fixed mid-slice: consolidating Slice 1's local `_strip_leading_markup()` onto the real imported `strip_leading_markup()` broke 8 of Slice 1's own tests; code-executor's "unaffected" claim was wrong, caught by orchestrator independently re-running tests, fixed by test-writer. QC PASS (AST-diffed against archived source, not trusted from report). **Carry-forward, do not lose:** the archived probe's real-corpus fixture tests (`first_turn_contract_corpus.json`) all drive `main()`, which doesn't exist until Slice 4 — QC flagged that Slice 4 must pick up this real-transcript re-run obligation (§9 / roadmap Slice 2 Tests item 1), not silently drop it.
- [x] Slice 3: `evaluate_checklist` + `build_reason` Evaluation Core — COMPLETE (2026-09-07, commit `4f94213`). Rule-5 evaluation-order ambiguity (flagged at spec approval) resolved in `02-ARCHITECTURE.md` before this slice began. QC independently traced and confirmed the ordering with a concrete counter-intuitive test case (source-earlier unmatched row still flagged over a source-later matched row). No regressions this slice — 44/44 including all prior slices' tests.
- [x] Slice 4: `run()`/`main()` Wiring, Stdin Contract, Track-Record Log — COMPLETE (2026-09-07, commit `079009b`). Slice 2's real-corpus fixture carry-forward resolved: assessed and confirmed non-transferable (old prose-format corpus, zero row-syntax matches) — stays live as Slice 7's obligation instead, not silently dropped. One real test bug found and fixed (rule-0 track-record test wrongly expected non-empty violations). One real QC FAIL found and fixed directly (new track-record log missing from `.gitignore`). 56/56 tests passing.
- [x] Slice 5: Agent-Facing Syntax Delivery — COMPLETE (2026-09-07). Both channels (CLAUDE.md, `build_reason()`) confirmed byte-identical grammar and identical transcript-self-lookup instruction, read side by side by QC not trusted from report. 63/63 tests passing. **Non-blocking advisory logged, not fixed:** two `CLAUDE_MD_PATH`-dependent tests raise `ValueError` rather than skip on a fresh clone lacking `CLAUDE.md` (it's gitignored) — optional per roadmap Tests item 5, revisit in a later slice if it becomes a real problem.
- [ ] Slice 6: Hook Wrapper Script + Settings Wiring
- [ ] Slice 7: Real-Transcript Validation of New Parsers
- [ ] **Frank binding forge-gate** — PENDING, runs once after all slices above are checked off.

## Current
Slice: 5
Step: @code-executor
Last updated: 2026-09-07

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| scripts/signpost_checklist_probe.py (Slice 1, QC) | 1 | Label-strip regex doesn't tolerate markdown markup or pre-colon qualifier text before `Signpost:`/`Pillar:`, unlike the archived heading detector Slice 2 will reuse — real-form headings (`## Signpost: ...`, `**Pillar:** ...`) silently drop trailing content instead of being parsed, reopening the exact evasion rule 0a/1b were built to close. |
| tests/test_signpost_checklist_probe.py (Slice 2 consolidation regression) | 1 | Slice 2's code-executor removed Slice 1's local `_strip_leading_markup()` in favor of the real imported `strip_leading_markup()`, but claimed "existing tests unaffected" without verifying — 8/17 tests broke on `AttributeError: no attribute '_strip_leading_markup'`. Caught by orchestrator independently re-running tests before proceeding, not by the reporting agent. |
| tests/test_signpost_checklist_probe.py (Slice 4, `test_track_record_written_on_block_path_matches_new_schema`) | 1 | Test bug, not implementation: asserted non-empty `violations` for a rule-0 (no-Signpost-heading) block path, but §5.4 rule 0 explicitly produces empty `violations` with `signpost_heading_absent=True` signaling the block instead — Slice 3's own rule-0 test already established this fact. |

## Spec Gate
Counter: 3/3 — PASS, all 7 Carried Conditions CLOSED (2026-09-07)

Closure record: (1) North Star sign-off — Danny reviewed the full document, rejected both drafted
sections, authored Thesis and Objective himself verbatim; NORTH-STAR.md further reduced to just
those two fields at Danny's explicit instruction, nothing else, "don't touch it again." Traceability
content relocated to 01-REQUIREMENTS.md so Frank's Layer 2 check still has a source. (2)
HOOK-DEPLOYMENT-ROSTER.md agent-rig row corrected to "Unwired 2026-09-07 (a44f1d5)". (3)
INTERVIEW.md:11 corrected to nine other repos. (4) 02-ARCHITECTURE.md §9 and 04-ROADMAP.md's Slice
2 residual "reused unchanged/copied unmodified" phrasing corrected to name the §5.1a additive
change. (5) RowViolation gained `line_text: Optional[str]` for stray_prose, rule 1b updated to
populate it. (6) 01-REQUIREMENTS.md:17-19 sentence fragment fixed. (7) attempt-3/ snapshot
captured. Ready for Step 9 (Human Approval) — full artifact set + Frank's three verdicts.

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-09-07 | FAIL | F1: false "byte-identical reuse" claim — `_collect_qualifying_tool_calls` drops `tool_use_id` today, rule 4 has nothing to check. F2: SC3 (no free-form evasion hiding spot) not met — prose-only Signpost and stray Pillar prose both silently allowed. F3: rule 0 misattributes its citation to the archived postmortem; ALLOW4 in that same flow contradicts it — real scope decision needs Danny's explicit call. F4: Slice 3 rule-count/test gap, stray tag in 01-REQUIREMENTS.md:149. Layer 2 FAIL: 9-consumer HOOK-DEPLOYMENT-ROSTER contradicts 01's "no other consumer" claim, propagation left undefined. Q-3 (tool_use_id citability) empirically resolved NO by Frank (1/11,124 real occurrences) — orchestrator's own resolution of this same question, made without opening real data, was wrong. | .gate-snapshots/spec/attempt-1/ |
| 2 | 2026-09-07 | FAIL | F1/F3/F4 from attempt 1 confirmed resolved. F2 partially resolved (0a/1b added) but three evasion channels remained open: heading-line trailing prose (F2a), Pillar-heading-line ambiguity (F2b), unmatched rows never evaluated (F2c). F5 (new): Q-3's transcript-lookup step was noted in architecture but never delivered in Slice 5 — agent could not produce a real `verified` row as written. F6 (new): inherited first-turn detection has a real, measured bypass (1/10 real transcripts). F7 (new): 01-REQUIREMENTS.md falsely claimed the archived mechanism live in agent-rig too (ten repos) — actually nine others, agent-rig already unwired. F8: 05-REVIEW.md never re-run, self-contradicted the current state. Layer 1 FAIL (F2), Layer 2 FAIL (F7). Two items required Danny's explicit call before attempt 3: F6 disposition, rule 0's ALLOW4 divergence. Resolved same session via North-Star-orientation judgment (not a literal rule lookup) — both confirmed: rule 0 stays strict (points at mission), F6 accepted as documented known limitation (ship, don't redesign now). All fixes (F2a/b/c, F5, F6 disposition, F7, F8) applied; a real defect also found and fixed in the same pass — the F7 dispatch had silently truncated 01-REQUIREMENTS.md from 181 to 20 lines, losing all User Stories/AC/Edge Cases/Constraints; restored from this session's own prior full read. | (not captured before fix — see note below) |
| 3 | 2026-09-07 | **PASS** | Layer 1 PASS, Layer 2 PASS. Convergence: SHRINKING (attempt 1: 4 findings + Layer 2 fail; attempt 2: 3 closed, 4 new; attempt 3: all 8 closed on substance, 6 doc-consistency residues + 1 governance item remain as Carried Conditions). All attempt-1/2 findings verified resolved against actual file contents, not summaries. 7 Carried Conditions issued (none block the PASS, all must be copied here before close-out): (1) NORTH-STAR.md SC4/Traceability edited by orchestrator on a Locked doc mid-gate with no recorded Danny sign-off — **RESOLVED same session**: Danny reviewed the full document himself, rejected the orchestrator's Declared Intent draft as task-list-shaped rather than thesis, rejected Success Criteria 1-3 as spec-vocabulary-shaped, then authored the Thesis and Objective himself verbatim, approved, "don't touch it again." (2) HOOK-DEPLOYMENT-ROSTER.md agent-rig row stale ("Live", should be "Unwired a44f1d5") — pending. (3) INTERVIEW.md:11 still says "ten repos" — pending. (4) 02-ARCHITECTURE.md §9 + 04-ROADMAP.md residual "reused unchanged/byte-identical" phrasing — pending. (5) RowViolation missing a payload field for stray_prose (`line_text`) — pending. (6) 01-REQUIREMENTS.md:17-19 sentence fragment from the truncation restoration — pending. (7) No attempt-2/3 snapshot captured — pending. | .gate-snapshots/spec/attempt-1/ only |

Convergence judgment (attempt 3): **SHRINKING** — see attempt 3 row above for evidence.
Deep-diagnosis evidence: attempt 1 → 2: 3 of 4 substantive findings (F1/F3/F4) closed, F2 partial. attempt 2 → 3: all 8 cumulative findings (F1-F8) closed on substance; only doc-consistency residue and one governance item remain, none reopening a prior substantive finding.
Orchestrator independent re-derivation: AGREES — re-read all attempt 1/2 findings against current file contents myself before each re-dispatch; the SHRINKING classification matches what I observed independently, not just Frank's own claim.

## Step 9: Human Approval — APPROVED (2026-09-07, Danny)

Full artifact set + Frank's three spec-gate verdicts approved. Alongside approval, a supplementary
consistency exercise ran (not part of the gate): a "Pillar Verdict Flow" diagram
(`verdict-flow-diagram.html`, published as an Artifact) was drawn fresh from `02-ARCHITECTURE.md`
alone, then reviewed by a non-gating Cold Frank opinion pass. That pass found the diagram's first
draft topologically wrong — it drew Rule 7 (unmatched-row check) as an independent parallel sweep,
when `04-ROADMAP.md` Slice 3 specifies it as a residue pass run strictly *after* the per-line
matching loop. Diagram corrected and republished to match.

**RESOLVED (2026-09-07, before Slice 3):** Rule 5's "earlier" is evaluation order, not
source/reply order — spelled out explicitly now in `02-ARCHITECTURE.md` §5.4 rule 5 (main-loop
rows evaluated before rule-7 residue-pass rows). Not escalated to Danny — resolvable directly from
the spec's own existing wording ("in this evaluation"), which already implied this reading.

## Forge Gate
Counter: 0/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]
