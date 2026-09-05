# Spec Review: Unsourced-Threshold Provenance Hook (Pass 3 — narrow verification)

**Status**: COMPLETE (not a HALT) — 1 HIGH internal contradiction, 3 MEDIUM, 2 LOW
**Date**: 2026-09-05
**Reviewer**: @spec-reviewer (independent)
**Scope**: narrow, skeptical verification pass against commit `859531d`. Prior passes' clean
objectives (three detection contexts, `PROXIMITY_WINDOW_THRESHOLD = 2`, out-of-scope boundary,
`{0,1,-1,2}` disposition honesty) were re-read this pass and show **no regression** — they are
not re-litigated below.
**Docs read in full**: INTAKE, INTERVIEW, NORTH-STAR, 01, 02, 04, `results.md`,
`results-fragment-shaped.md`, plus direct reads of `scan_thresholds.py`, `scan_fragments.py`,
`domain_boundary_provenance_probe.py`, `domain-boundary-provenance.sh`.

---

## Objective 1 — Does §2.1's discharge language match `results-fragment-shaped.md`?

**Mostly yes. The headline number is accurate; one adjacent corroboration claim is not.**

| Architecture §2.1 claim | Evidence file | Verdict |
|---|---|---|
| "9/9 PASS across both ground-truth incidents" | §3 recall table: GROUND TRUTH (I1+I2 only) 9 cases, 9 PASS | ✅ Accurate |
| "I1: 3/3, I2: 6/6" | §3 table, exact match | ✅ Accurate |
| "covering single-line, multi-context, and the worst case" | §2 matrix cases `I1-a`…`I2-f` | ✅ Accurate |
| "worst case … recovered via strategy 2 (dedent-retry) or strategy 3 (regex fallback) depending on exact slice boundaries" | `I2-a` (the case labelled "worst case") ran **strategy 2** only; strategy 3 ran on `I2-e`/`I2-f` | ⚠️ Imprecise, not false (L-1) |
| "real execution against fragments sliced live from the working tree and from `git show 7d9fdf5:…`" | §2 preamble states exactly this | ✅ Accurate |
| "corroborated by a **byte-identical corpus regression** (same file referenced above)" | **No such regression appears anywhere in `results-fragment-shaped.md`** (§1–§5 contain: rationale, fragment matrix, recall, strategy attribution, non-establishments). Grep of the whole benchmark directory for `byte-identical` / `corpus regression` / `regress` returns **zero matches** | ❌ **M-1 — unsupported citation** |
| "F1 excluded from ground truth" handling | §3 note + §5 bullet 2, consistent | ✅ Accurate |

The 9/9 figure and its scope claim survive verification. The "byte-identical corpus regression"
clause does not — it is an uncited assertion attached to a cited one, and a cold reviewer reading
the referenced file will not find it. Same clause is repeated in §13's G-1 bullet.

## Objective 2 — Is the "contexts 1/2 not covered, no fallback by design" caveat consistent?

**Inside `02-ARCHITECTURE.md`: yes, and stated four times consistently** (§2.1 robustness table,
§2.1 "Scope of what was confirmed", §7 `detect_threshold_literals` docstring, §13 G-1 bullet).
`results-fragment-shaped.md` §5 says the same. **Nothing overstates contexts 1/2.** No finding.

Two adjacent weaknesses, neither an overstatement:
- The caveat exists **only** in `02-ARCHITECTURE.md`. `01-REQUIREMENTS.md` and `04-ROADMAP.md`
  describe all three contexts symmetrically with no note that two of them silently yield nothing
  on an unparsable fragment (L-2). Requirements US-1 AC1/AC3 and the Edge Cases table read as if
  all three contexts fire equally at the real scan surface.
- The one place the doc set *does* diverge on fallback is in the **opposite** direction — see M-2
  below, where §2 flatly denies a fallback exists at all.

## Objective 3 — Is the float-regex fix honestly flagged as unbenchmarked?

**Yes. This is the cleanest part of the pass.** §2.1's fix paragraph opens "in direct response to a
measured gap, **not itself re-benchmarked**", labels its own no-new-false-positive argument as
"stated as reasoning rather than measurement", and closes by saying the F1 rerun against the fixed
pattern "remains open". §13's G-1 bullet repeats the caveat. Verified against source: the benchmark
script still carries the **pre-fix** pattern (`scan_thresholds.py` L278:
`r"(-?\d[\d_]*|True|False)\s*(?:#.*)?$"`), which corroborates that the fix is spec-only. No
overstatement found. ✅

One consequence is unflagged: because the fix is spec-only, `results-fragment-shaped.md` §5 now
asserts `"The regex fallback matches integers and booleans only — (-?\d[\d_]*|True|False) **per
§2.1**"` — attributing to §2.1 a pattern §2.1 no longer contains. The machine-generated evidence
file and the spec now disagree about what the spec says (M-3).

## Objective 4 — New drift from the last two correction passes

**M-2 (HIGH — the one a cold Frank will hit first).** `02-ARCHITECTURE.md` **L320** still reads, in
bold, as a standing design decision:

> **AST-based, Python-only, no regex fallback** — same posture as the prior pass

§2.1 (L161–189) specifies a per-line **regex fallback** as parse strategy 3, and §7's docstring,
§13, and Roadmap Slice 3 all implement it. This is a stale carry-forward the fragment-robustness
pass did not sweep. It is not merely awkward: it is the *same sentence shape* the prior review
already had to correct once, and it directly contradicts the fix that discharged this pass's
CRITICAL. Related, lower-severity echoes of the same unswept claim:

| Location | Text | Issue |
|---|---|---|
| `02-ARCHITECTURE.md` L320 | "no regex fallback" | **Contradicts §2.1** — must be scoped to "no regex fallback for contexts 1–2" |
| `02-ARCHITECTURE.md` §10 Patterns row "AST-based syntactic detection over regex" | no mention of strategy 3 | Understates shipped design |
| `01-REQUIREMENTS.md` L124 | "Detection is Python-only, **AST-based**." | Requirements never mentions the three-strategy chain or the regex path at all |
| `04-ROADMAP.md` Slice 3, Impl. Note 2 | "Syntax error on `ast.parse` → return `[]` (fail-open…)" | Unqualified; contradicted 11 lines later by the same slice's own fragment-robustness note. Slice 3's *test* list has it right |

**M-4 (§13 self-inconsistency).** §13 bullet 2 ("§2's assignment context") still reads: *"Not fully
resolved as open, per G-1 below — … the recall figure's applicability to the real scan surface is
**not yet** [established]."* §13 bullet 3 immediately below says G-1 is **RESOLVED for context 3**
with 9/9. Two consecutive bullets in the same open-items list give opposite dispositions of the
same question. Bullet 2 is stale from the pre-rerun revision.

**Cross-check of §13's open-items list against Requirements/Roadmap** (otherwise clean):

| §13 open item | Requirements | Roadmap | Status |
|---|---|---|---|
| `{0,1,-1,2}` precision unvalidated | L125–128 states "NOT YET BENCHMARKED", plan pointer | Slice 3 note; Deferred item | ✅ Consistent |
| Assignment context (c) adopted | Detection Rule Pointer + US-1 AC4 + Edge Case row | Slice 3 goal/tests | ✅ Consistent |
| G-1 fragment robustness | **Silent** | Slice 3 impl-note + 2 named regression tests | ⚠️ L-2 |
| G-2 owner-required marker | AC2 + Edge Case row | Slices 4 & 9, 4 named regression tests | ✅ Consistent |
| `range()` exclusion removed | L128–131 | Slice 3 note ("dead code, not implemented") | ✅ Consistent |
| `PROXIMITY_WINDOW_THRESHOLD = 2` | Constraints + Assumes | Slices 4 & 9 | ✅ Consistent |
| §5.1 timeout re-measurement | Out of Scope: no latency SLA | Slice 12 test ("runtime recorded") | ✅ Consistent |
| G-4 vocabulary figures deleted | not restated (correct) | Slice 3 note | ✅ Consistent |
| G-9 self-scan: `PROXIMITY_WINDOW = 5` IS flagged | Edge Case row (hook's own constants) | Slices 4, 9 tests + Deferred routing item | ✅ Consistent |
| G-5 `mode` non-nullable | US-2/US-3 ACs | Slice 8 Done-When | ✅ Consistent |
| Float-regex fix unbenchmarked | **Silent** | **Silent** | ⚠️ L-3 (arch-only; acceptable, but Slice 3 has no float test case) |

## Objective 5 — Cold-Frank exposure

Ranked by what a hostile, unscoped reviewer catches first:

1. **M-2 (L320).** A bolded, unqualified "no regex fallback" in the same document that specifies a
   regex fallback. Single highest-probability gate finding this pass.
2. **M-1.** The one number-adjacent claim in §2.1 that is *not* in the cited file. This doc set is
   being judged on citation discipline; an uncited corroboration clause riding alongside a
   correctly-cited 9/9 is exactly the shape a source-axis reviewer looks for.
3. **M-4.** Two adjacent §13 bullets contradicting each other on the same resolved question.
4. **M-3.** Evidence file attributes a superseded regex to §2.1; nothing on the file's face marks
   it as a pre-fix run.
5. **L-2.** Requirements/Roadmap carry no contexts-1/2 degradation caveat.

Everything else read clean: `results.md` corpus (445 files, 10 roots, "Missing corpus roots: none"),
the recall table, the 60.5% share table, the §5 proximity distribution, the marker rule's mirroring
across 02/01/04, the `mode` fail-safe default, and the LOCKED-doc behavior-change disclosure (§3/§5/
§11 + Slice 11's revised addendum rule + Slice 6's named `test_cross_domain_pass_flag_under_log_only`).

---

## Gaps

| ID | Sev | Gap | Impact | Requested fix |
|---|---|---|---|---|
| M-2 | **HIGH** | `02-ARCHITECTURE.md` L320 asserts "no regex fallback"; §2.1 specifies one | Direct self-contradiction on the fix that discharged this pass's CRITICAL | Rewrite L320 as "AST-first, Python-only; regex fallback **only** for context 3 per §2.1 — contexts 1–2 have none". Sweep §10's pattern row, `01-REQUIREMENTS.md` L124, and `04-ROADMAP.md` Slice 3 impl-note 2 in the same edit |
| M-1 | MED | "corroborated by a byte-identical corpus regression" (§2.1, repeated in §13) is unsupported — zero matches in the benchmark directory | An uncited claim inside the sprint's most-scrutinised discharge paragraph | Either commit the regression artifact and cite it by path, or delete the clause. Do not soften it |
| M-3 | MED | `results-fragment-shaped.md` §5 cites `(-?\d[\d_]*\|True\|False)` "per §2.1"; §2.1 no longer contains that pattern | Machine-generated evidence and spec disagree about the spec's own content | Add a dated "pre-float-fix run" note where §2.1 cites the file (the file itself is machine-generated — do not hand-edit) |
| M-4 | MED | §13 bullet 2 says fragment applicability "not yet" established; bullet 3 says RESOLVED for context 3 | Self-contradicting open-items list | Rewrite bullet 2 to defer to bullet 3 |
| L-1 | LOW | §2.1: worst case "recovered via strategy 2 or 3"; `I2-a` used strategy 2 | Imprecision in an otherwise exact citation | State strategy 2 for `I2-a`; cite `I2-e`/`I2-f` for strategy 3 |
| L-2 | LOW | Contexts-1/2 no-fallback caveat appears only in `02-ARCHITECTURE.md` | Requirements/Roadmap read as if all 3 contexts are fragment-robust | One sentence in `01-REQUIREMENTS.md` Detection Rule Pointer; one line in Roadmap Slice 3 |
| L-3 | LOW | No float-literal test case in Slice 3 despite the §2.1 regex widening | The fix ships untested and unbenchmarked | Add a Slice 3 test: float assignment on the regex-fallback path IS flagged |

## Risks

| Risk | L | I | Mitigation |
|---|---|---|---|
| M-2 read as a live design decision by an implementer → strategy 3 never built → I2's real shape missed at the real scan surface | M | **H** | Fix M-2 before the gate; Slice 3's two named fragment regression tests are the backstop |
| Float fix ships on reasoning, not measurement (CLAUDE.md rule 1 territory) | M | M | Honestly flagged in §2.1/§13; add L-3's test; rerun `scan_fragments.py` post-implementation |
| `{0,1,-1,2}` precision unvalidated → real threshold at those values unflagged | M | M | Named risk, executable plan, `log_only` bounds cost |
| Contexts 1–2 silently yield nothing on unparsable fragments → unmeasured recall loss | M | M | Accepted by design and stated; Slice 12 track-record data is the observation path |
| §5.1's 377ms is a borrowed cold-re-run figure, not this doc's measurement | L | L | Conclusion (5s adequate) holds at 7.5% of budget; re-measurement tracked in §13 + Slice 12 |
| Benchmark corpus drift changes cited volume/window numbers | L | L | §11 names this; margins (100%@2, 9/9) are wide |

## Assumptions

| Assumption | Impact if wrong |
|---|---|
| `results-fragment-shaped.md` is the pre-float-fix run (inferred from `scan_thresholds.py` L278 still carrying the old pattern) | If the script was fixed post-generation, the file is stale in a second, undisclosed way |
| Real `Edit` `new_string` fragments resemble the 9 sliced shapes tested | Recall at the real surface differs from 9/9 |
| Contexts 1–2's silent-miss cost is acceptable under `log_only` | Unmeasured false negatives accumulate unnoticed |

## Open Questions

| Question | Status | Needs |
|---|---|---|
| Does the "byte-identical corpus regression" artifact exist and, if so, where? | Open | Author (wright) — path, or delete the clause |
| Route the `PROXIMITY_WINDOW = 5` self-scan finding: same-sprint file touch, or separate pass? | Open | Danny (already surfaced in §11/§13/Deferred) |
| Rerun `scan_fragments.py` against the widened float regex before or after forge? | Open | Danny |

## Approval Checklist

### 01-REQUIREMENTS
- [ ] Human-reviewed; ACs testable; Out of Scope acceptable
- [ ] L124 "AST-based" scoped for the regex fallback (M-2)
- [ ] Contexts-1/2 fragment caveat added (L-2)

### 02-ARCHITECTURE
- [ ] Human-reviewed
- [ ] **L320 "no regex fallback" corrected (M-2, HIGH)**
- [ ] "byte-identical corpus regression" cited or deleted (M-1)
- [ ] §13 bullet 2 reconciled with bullet 3 (M-4)
- [ ] §2.1 worst-case strategy attribution corrected (L-1); pre-fix-run note added (M-3)

### 03-UI-SPEC
- [x] N/A — non-interactive `PreToolUse` hook, no UI surface. Deliberate, not a gap

### 04-ROADMAP
- [ ] Human-reviewed; sequence and slice sizing accepted
- [ ] Slice 3 impl-note 2 (`return []`) qualified (M-2); float test added (L-3)

### Overall
- [ ] All open questions resolved
- [ ] All risks accepted or mitigated
- [ ] Ready for Frank's binding spec-gate

---

**Verdict**: no HALT. Requirements → Architecture → Roadmap coverage is complete and traceable, and
the 9/9 fragment-recall discharge is real and accurately numbered. The doc set is **not yet** ready
for a cold gate: M-2 is a bolded self-contradiction on the exact fix under review, and M-1 is an
uncited claim sitting inside the cited paragraph. Fix M-1/M-2/M-4 (and preferably M-3, L-1/L-2/L-3
in the same sweep) before submitting.
