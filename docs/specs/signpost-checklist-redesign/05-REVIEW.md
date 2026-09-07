# Spec Review: Signpost Checklist Redesign

**SUPERSEDED (2026-09-07).** This document is the editorial pre-Frank review (iteration 2 of 2)
and is frozen at that point — its "NOT READY" verdict and gap list below are historical, not
current. Every gap it names (G-A, G-C, G-E, G-G, G-H, G-I) was fixed before Frank's binding
spec-gate ran. Frank's own binding spec-gate verdicts (attempt 1: FAIL, attempt 2: FAIL, with
findings and fixes) are the actual current state of record — see `PROGRESS.md`'s `## Spec Gate`
table, not this file, for what's outstanding now.

**Iteration:** 2 of 2 (max). Full re-review of all four docs, not a diff check.
**Docs reviewed:** `01-REQUIREMENTS.md`, `02-ARCHITECTURE.md`, `03-UI-SPEC.md` (N/A — no UI),
`04-ROADMAP.md`.

---

## Prior-Iteration Fix Verification

| Prior item | Claimed fix | Landed? | Evidence |
|---|---|---|---|
| Stray leaked tags (x2) | Manually removed | Yes | Full-doc-set sweep clean (see Formatting Sweep) |
| G-1 hook vs agent authorship | 02 §1a | Yes | 02 §1a; §6 pattern "Agent authors, hook verifies"; 01 US-1 rewritten to agent-authorship with the Stop-hook rationale; 01 Constraints "Must not: Have the hook author… row text" |
| G-2 verified/unverified both legal, non-blocking | 02 §5.3 / §5.4 rule 2 | Yes | 02 §5.3 two-form forced syntax; §5.4 rule 2 "never itself a FAIL"; 01 US-2 AC3 + Constraint "exactly two forced literal status values" |
| G-4 / R-3 missing Signpost heading fails closed | 02 §5.4 rule 0 | Yes, in 02 + 01 — **not in 04** (see G-A) | 02 §5.4 rule 0, §4 `evaluate_checklist(signpost_heading_present)`, `EvaluationResult.signpost_heading_absent`, §6 anti-pattern; 01 Edge Cases row + Constraint "Must: Fail closed" |
| G-5b whitespace symmetry | 02 §5.4 comparison note | Yes | 02 §5.4: `.strip()` "applied symmetrically on the Signpost-line and Pillar-row-label side" |
| G-6 no delivery mechanism for forced syntax | 04 Slice 5 | Yes, with stale wording (G-C) | 04 Slice 5, Dependency Map row, Sequence Rule 3, Slice 6 depends-on 5 |

Five of six fixes landed cleanly and consistently. G-4's fix landed in requirements and
architecture but was **not propagated into the roadmap** — that is the one substantive item this
pass raises.

---

## Formatting Sweep (full doc set, re-run)

- Leaked tags / stray XML-ish artifacts: **none found** in 01, 02, 03, 04.
- Placeholder tokens (`TODO`, `TBD`, `FIXME`, `{{…}}`, `[insert …]`, skill-template stubs like
  `[what's missing]`): **none found** in 01, 02, 03, 04.
- Fenced code blocks: all fences paired and terminated (02 has three blocks — schema, row-syntax,
  regex — all closed; 01/03/04 contain none).
- Tables: all header/separator rows well-formed; no truncated trailing sections.
- Cross-doc citation headers present in 02, 03, 04.

---

## Requirements Completeness (01)

- Summary present and clear.
- All five user stories in As-a/I-want/so-that form; each has acceptance criteria.
- Edge-case table populated (3 rows, incl. the new heading-absent row).
- Out of Scope non-empty (7 items + 1 deferred).
- Constraints concrete (Must / Must-not / Assumes, all testable).

### Requirements Gaps

| ID | Gap | Impact |
|---|---|---|
| G-B | Heading-absent fail-closed behavior appears only in the Edge Cases table and Constraints, with no acceptance criterion under US-3 (the "mechanical FAIL" story). Every other FAIL condition has a Given/When/Then AC. | Low. Behavior is unambiguous and fully specified in 02 §5.4 rule 0; the missing AC is a testability/symmetry gap, not a design gap — the forge slice test can be written from the edge-case row. Not approval-blocking. |
| G-D | Architecture §5.4 rule 5 (a `tool_use_id` may back at most one row) has no corresponding requirement or AC. Architecture flags this itself as "beyond the literal ACs" and offers deletion. | Low. Self-flagged and reversible; needs a human keep/delete call (see Open Questions Q-1), not a doc fix. |

No requirement is ambiguous or self-contradictory. Vocabulary is aligned across all three docs
(`verified` / `unverified` forced literals, no residual boolean/third-state language).

---

## Architecture Completeness (02)

Schemas are real Python (`dataclass`, typed fields), not pseudocode; function contracts are
complete signatures with documented return semantics; patterns each carry a rationale; integration
points named with concrete paths. Deleted-machinery list (§5.2) is explicit, which makes the
"don't resurrect the inferred-subject matcher" constraint mechanically checkable in forge.

### Requirements → Architecture Coverage

| Requirement | Architecture Coverage | Status |
|---|---|---|
| US-1 verbatim row authorship by agent, hook verifies | §1a; §5.3 group-2 exact equality; §4 `extract_signpost_lines` | OK |
| US-2 per-row tool-call-backed verification | §5.3 forced suffix syntax; §5.4 rules 2–4 | OK |
| US-3 mechanical FAIL on missing/unbacked | §5.4 rules 0–5; no inference anywhere | OK |
| US-4 revise-and-resubmit, no retry ceiling | §5 stateless pure function; no counter in `EvaluationResult` or track-record schema | OK |
| US-5 unchanged trigger surface | §5.1 reused byte-identical; `run()` ordering fixed | OK |
| Edge: empty Signpost (heading present) | §5.4 final paragraph | OK |
| Edge: Signpost heading absent | §5.4 rule 0 fail-closed | OK |
| Edge: repeated line across turns | §5 stateless, no dedup | OK |
| Constraint: two forced literal statuses only | §5.3 `_PILLAR_ROW_RE`, exactly-one-suffix rule | OK |
| Constraint: no hook-authored rows | §1a; `PillarRow` docstring | OK |

### Architecture Gaps

| ID | Gap | Impact |
|---|---|---|
| G-E | §5.4 rule 6 requires "exactly one matching row" per Signpost line, but no rule defines behavior when **two or more** Pillar rows carry the identical label (e.g. one `(unverified)` and one `(verified: …)`). Rules 1–5 iterate per Signpost line and find "rows" (plural) without specifying which one is evaluated or whether multiplicity is itself a violation. | Medium. An agent could emit both forms of the same row; current text does not determine block/allow. Fixable with one sentence (e.g. "more than one matching row → treat as a violation" or "all matching rows must independently satisfy rules 2–5"). Not implementation-blocking (forge can pick a reading), but it is exactly the kind of undefined multiplicity a gaming agent finds. Flagged for human decision. |
| G-F | `EvaluationResult.violations` is annotated `list` with the element type only in a comment (`# list[RowViolation]`), while sibling fields are precisely typed. Cosmetic inconsistency in an otherwise valid schema. | Negligible. |

---

## UI Coverage (03)

`03-UI-SPEC.md` correctly declares N/A with a stated rationale (Stop-hook, stdin/stdout JSON, no
screens). No user story in 01 implies a UI surface — US-1/US-4 concern an agent's own reply text,
US-5 concerns the operator's trigger surface, not an interface. **N/A is appropriate and complete.**

---

## Roadmap Completeness (04)

Seven slices, concrete file paths, per-slice Depends-On / Tests / Done-When, explicit sequence
rules and a Deferred list. Dependency map is acyclic (schemas → parsers/reuse → eval core → syntax
delivery → wiring → hook → real-data validation).

### Architecture → Roadmap Coverage

| Architecture component | Slice | Status |
|---|---|---|
| §3 dataclasses | Slice 1 | OK |
| `extract_signpost_lines` / `extract_pillar_rows` / `parse_checklist_row_line` (§4, §5.3) | Slice 1 | OK |
| §5.1 reused trigger-surface + tool-call collection | Slice 2 | OK |
| §5.2 deleted machinery (must NOT be copied) | Slice 2 grep check | OK |
| §5.4 rules 1–6 (`evaluate_checklist`) | Slice 3 | OK |
| **§5.4 rule 0 — heading-absent fail-closed** | **none** | **Gap (G-A)** |
| `build_reason` | Slice 3 (draft) + Slice 5 (content) | OK |
| Agent-facing forced syntax delivery | Slice 5 | OK |
| `run()`/`main()`, gating order, track-record log | Slice 4 | OK |
| Hook wrapper + `.claude/settings.json` (§8) | Slice 6 | OK |
| §9 real-transcript validation | Slice 7 | OK |

### Roadmap Gaps

| ID | Gap | Impact |
|---|---|---|
| **G-A** | **Rule 0 is absent from the roadmap.** Slice 3's Goal says "architecture §5.4, rules 1–6"; its Implementation Notes say "all six rules"; no test covers heading-absent → block; no slice mentions the `signpost_heading_present` parameter of `evaluate_checklist` (§4) or the `signpost_heading_absent` field of `EvaluationResult` (§3); Slice 4 never states that `run()` must compute and pass `signpost_heading_present`; Slice 5's `build_reason()` requirements never mention rule 0's distinct reason string (§4 `build_reason` requires it). | **High — the one approval-blocking item.** The G-4/R-3 fail-closed fix landed in 01 and 02 but the roadmap still describes the pre-fix design. A forge run following 04 literally would implement a probe with no rule 0, i.e. reopen the no-Signpost bypass, and every Done-When would still pass green because no test covers it. This is a silent-regression shape: the checklist looks complete because it was written against the earlier architecture. |
| G-C | Slice 5 (Depends-On and Implementation Notes) still speaks of G-2 as unlanded — "the parallel architecture fix," "any other status the architecture amendment settles on," "If the parallel architecture fix (G-2) has not yet landed when this slice is reached, HALT and wait." Sequence Rule 5 repeats it. G-2 has landed (02 §5.3/§5.4 rule 2 are final). | Medium. Not wrong, but stale: it leaves the row vocabulary described as open in the one slice whose job is to document it precisely, and arms a HALT condition that can no longer be evaluated meaningfully. Should be replaced with the settled vocabulary (`verified` / `unverified`) quoted from §5.3. |
| G-G | Slice 5's first test names a `"unbacked_id"` violation kind. No such kind exists — §3 `RowViolation.kind` is one of `"missing"`, `"false_claim"`, `"duplicate_id"`. | Low-Medium. A test written against a non-existent enum value will either be silently rewritten in forge or fail confusingly. One-word fix (`"false_claim"`). |
| G-H | Document ordering: slices appear in file order 1, 2, 3, **5**, 4, 6, 7, while Sequence Rule 1 says "complete each slice fully before starting the next." Dependency Map and per-slice Depends-On are unambiguous (5 depends on 3; 4 depends on 1–3; 6 depends on 4 and 5), so no real cycle or contradiction — but "the next" is ambiguous against reading order. | Low. Either reorder the sections or restate Rule 1 as "in dependency order per the Dependency Map." |
| G-I | Header note says "Slices 1–6 below, renumbered" while the roadmap contains seven slices. | Negligible. |

No circular dependencies. No missing Done-When. All file paths concrete.

---

## Identified Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Forge implements from 04 alone and omits rule 0, reopening the no-Signpost bypass, with a fully green checklist. | H (if G-A unfixed) | H | Fix G-A: add rule 0 to Slice 3's scope, add a heading-absent test, add `signpost_heading_present` plumbing to Slice 4, add rule-0 reason text to Slice 5. |
| R-2 | Forced row syntax never reaches the agent in other repos — `CLAUDE.md` is gitignored and repo-local; the self-teaching block reason only reaches an agent that already hit the hook. | M | M | Accepted and bounded: 04's Deferred list explicitly scopes delivery to these two channels for this repo's operating pattern. Surfaced for the human as an accepted limitation, not a defect. |
| R-3 | Every first turn blocks until the agent learns the syntax; the first-block experience is the teaching moment. | M | M | Slice 5's self-teaching `build_reason()` + Slice 6 ordering after Slice 5. Residual: a block is still a block on the very first turn of a fresh repo. |
| R-4 | Duplicate-label rows (G-E) leave evaluation undefined; an agent could pair `(unverified)` with `(verified: …)` on the same label. | M | M | Resolve G-E with one explicit rule before forge. |
| R-5 | Slice 7 cannot run: the new checklist format does not exist in real transcripts until the hook has been live, so real-data validation trails the ship. | H | M | Slice 7 already handles this honestly ("zero real transcripts is itself the finding; do not fabricate"). Accepted; note that ship happens before validation completes. |
| R-6 | Signpost section format drifts (01's stated Assumes), silently breaking `extract_signpost_lines`. | L | M | Documented assumption; Slice 7 real-data check is the detector. No monitoring beyond that. |
| R-7 | Copy-not-import of §5.1 functions from `archive/` forks battle-tested code; the archived copy is now a second source of truth that can drift. | L | M | Slice 2 mandates copy-unmodified + behavior-parity tests. Residual drift risk accepted (archive is frozen). |
| R-8 | `tool_use_id` uniqueness (rule 5) may reject legitimate cases where one tool call genuinely backs two claims. | L | L | Architecture pre-authorizes deletion of rule 5 if judged out of scope (Q-1). |

---

## Assumptions

| # | Assumption | Impact if Wrong |
|---|---|---|
| A-1 | Signpost claim lines are markdown list items (`-`/`*`/`+`/`N.`); prose continuation lines are not claims. | Multi-line or prose-form claims silently produce zero rows required — a bypass. |
| A-2 | `tool_use_id` values are stable, unique, and present in the transcript at the time the Stop-hook fires for the current turn. | Verified rows fail spuriously; every gated turn blocks. |
| A-3 | The archived probe's §5.1 functions are correct and their behavior is genuinely unchanged by the copy. | US-5's "unchanged trigger surface" claim is unverified; Slice 2's parity tests are the only check, and the archive may have no such tests. |
| A-4 | The archived `first-turn-contract.sh` Stop-hook entry is already unwired. | Slice 6 may double-wire two hooks. Slice 6 already instructs verifying this against the live file rather than assuming — good. |
| A-5 | Agents will reproduce the forced syntax exactly once documented in `CLAUDE.md`. | First-turn blocks become routine rather than exceptional. |
| A-6 | Checkbox glyph/status-suffix mismatch (`[x]` + `(unverified)`) is acceptable to ignore. | Explicitly accepted in 02 §5.3 as a known low-severity out-of-scope gap. |
| A-7 | The agent has read access to its own `tool_use_id` values while composing the reply. | If not, the `verified` path is unwritable in practice and every row degrades to `unverified` — which would make the mechanism non-blocking but also nearly meaningless. **This assumption is load-bearing and untested in the doc set.** |

---

## Open Questions

| # | Question | Status | Resolution needed from |
|---|---|---|---|
| Q-1 | Keep or delete §5.4 rule 5 (duplicate `tool_use_id`)? Architecture flags it as beyond the literal ACs and pre-authorizes deletion; no requirement covers it. | Open | Human (Danny). Carried from iteration 1, still unresolved. |
| Q-2 | (G-E) What happens when two Pillar rows share the same label? Block, or evaluate all matches? | Open | Human decision, then one sentence in 02 §5.4. New this iteration. |
| Q-3 | (A-7) Can the authoring agent actually obtain its own `tool_use_id` values at compose time? If not, the `verified` path is inert. | Open | Empirical check before forge — this is the single highest-leverage unknown in the design. Carried from iteration 1. |
| Q-4 | Is `CLAUDE.md`-only delivery (gitignored, repo-local) acceptable, given this mechanism may run in other repos? | Open — 04's Deferred list asserts sufficiency, but that is the spec asserting its own adequacy. | Human (Danny). Carried from iteration 1. |
| Q-5 | Does the mechanism ship before Slice 7's real-data validation can possibly run (R-5)? Is shipping-then-validating acceptable here? | Open | Human (Danny). Carried from iteration 1. |
| Q-6 | Should a heading-absent FAIL get its own acceptance criterion under US-3 (G-B), or is the Edge Cases row sufficient for forge test derivation? | Open | Human (low stakes). |

---

## Approval Blockers

**This is iteration 2 of a 2-iteration maximum. The following routes to human review, not a third
auto-fix round.**

1. **G-A (roadmap missing rule 0)** — the only gap I would call approval-blocking on its own. The
   architecture and requirements now specify a fail-closed rule that the implementation plan does
   not mention anywhere, in any slice, in any test, in any function signature. Forging from 04 as
   written produces the pre-fix design with a green checklist.
2. **G-C + G-G (stale/incorrect Slice 5 text)** — should be corrected in the same pass as G-A;
   both are small, mechanical edits, but G-C leaves the row vocabulary described as unsettled in
   the slice whose entire job is to document it exactly.
3. **G-E / Q-2 (duplicate-label rows undefined)** — needs a human call, then one sentence.

Everything else (G-B, G-D, G-F, G-H, G-I) is low-severity and can be accepted as-is or swept in
alongside the above.

---

## Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [ ] Acceptance criteria are testable
- [ ] Out of scope is acceptable
- [ ] Decision on G-B (heading-absent AC under US-3)

### Architecture (02)
- [ ] Reviewed by human
- [ ] Patterns are appropriate (esp. agent-authors/hook-verifies, fail-open vs. rule-0 fail-closed)
- [ ] Schemas are correct
- [ ] Decision on Q-1 (keep/delete rule 5)
- [ ] Decision on Q-2 / G-E (duplicate-label rows)

### UI Spec (03)
- [x] N/A confirmed — no UI surface exists for a Stop-hook mechanism
- [ ] Human concurs with N/A

### Roadmap (04)
- [ ] Reviewed by human
- [ ] **G-A fixed: rule 0 present in Slice 3 scope + tests, Slice 4 plumbing, Slice 5 reason text**
- [ ] G-C fixed: Slice 5 stale G-2 language replaced with settled `verified`/`unverified` vocabulary
- [ ] G-G fixed: `"unbacked_id"` → `"false_claim"`
- [ ] Sequence is correct (G-H reading-order ambiguity accepted or fixed)
- [ ] Slices are appropriately sized

### Overall
- [ ] Q-1 through Q-6 resolved or explicitly accepted as open
- [ ] R-1 mitigated (this is G-A)
- [ ] R-2, R-3, R-5 accepted as known limitations
- [ ] Q-3 (A-7, `tool_use_id` availability at compose time) checked empirically before forge
- [ ] Ready for implementation

---

## Verdict

**NOT READY for approval as written.** Five of six prior-iteration fixes landed correctly and
consistently; the doc set is materially stronger than iteration 1 (9 gaps → 6 substantive plus 3
negligible, formatting sweep clean). But the G-4 fail-closed fix propagated to 01 and 02 and not to
04, which is the highest-consequence gap in the set precisely because it is invisible to the
roadmap's own Done-When checks. Route to human: fix G-A (plus G-C, G-G) and rule on Q-1/Q-2.
