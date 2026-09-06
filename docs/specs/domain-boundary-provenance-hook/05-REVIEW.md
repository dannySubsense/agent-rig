# Spec Review: Unsourced-Threshold Provenance Hook (Pass 4 — pre-Cycle-2 verification)

**Status**: COMPLETE (not a HALT) — 0 CRITICAL, 2 HIGH, 3 MEDIUM, 2 LOW
**Date**: 2026-09-05
**Reviewer**: @spec-reviewer (independent)
**Scope**: verification pass against working-tree state at commit `e7223e9`, targeting the two
attempt-4 fixes (F1 exclusion-set deletion, F2 regex fix) plus an unscoped hostile sweep.
Prior passes' clean objectives (three detection contexts, `PROXIMITY_WINDOW_THRESHOLD = 2` as a
value, fragment-shaped 9/9 recall, out-of-scope boundary, citation-or-deletion-only marker rule —
corrected from the original owner-or-citation framing per Danny's 2026-09-06 ruling) were
re-read and show **no regression**; they are not re-litigated except where the exclusion deletion
demonstrably changed their basis (M-1).
**Docs/artifacts read**: INTAKE, INTERVIEW, NORTH-STAR, 01, 02, 04, PROGRESS, `results.md`,
`results-fragment-shaped.md`, plus direct reads of `scan_thresholds.py`, `scan_fragments.py`,
`candidates.jsonl`, `scripts/domain_boundary_provenance_probe.py`.

**STALE/SUPERSEDED (2026-09-06):** this review's references to `PROXIMITY_WINDOW_THRESHOLD = 2`
as the adopted, current design — including the "retain the window" recommendation at M-1 below —
are superseded by `02-ARCHITECTURE.md` §4, following a real Frank forge-gate FAIL that found the
symmetric window checked the wrong thing. The constant was deleted; a same-line-or-contiguous-
comment-block-above rule (no fixed window) was adopted instead. Text below is left unedited as a
historical review record.

---

## 1. Targeted Objectives — Verdicts

| # | Objective | Verdict | Evidence |
|---|---|---|---|
| 1 | `{0,1,-1,2}` fully removed from all spec docs, nothing treats it as active, no replacement constant | **PASS** | grep across `docs/`: every hit in 01/02/04 is an explicit REMOVED/historical framing. 01 L128-133, L208-210; 02 L268, L290-334, L778-780, L943-946; 04 L134-135, L175-179, L258, L511, L624, L672. No filter replaced it — no new constant introduced. |
| 2 | §0.1 rule-1 restatement accurate (two dispositions, no invented third) | **PASS** | 02 L42-53: names exactly (a) citation, (b) deletion; explicitly deletes the "executable benchmarking plan" third option and names its only load-bearing use. Corrected from three dispositions to two per Danny's 2026-09-06 ruling, which removed named-human-owner PROVISIONAL as a valid option — this evidence line previously named a third disposition that no longer exists in the live architecture doc. |
| 3 | Volume increase handled consistently; no stale "excluded" assertion | **PASS** | 04 Slice 3 test L185-187 is direction-reversed ("Literals `0, 1, -1, 2` ARE flagged"); Slice 9 L511 says "no fixture should assert it"; Slice 12 L623-625 removes the deferred benchmarking plan; Deferred L672-674 marks it REMOVED-not-deferred. No surviving "is excluded" assertion in any spec doc. |
| 4 | Regex fix real in `scan_thresholds.py`; doc's claim about it matches reality | **PASS (code) / FAIL (evidence-doc consistency — see H-1)** | `scan_thresholds.py:276-279` = `(-?\d[\d_]*(?:\.\d[\d_]*)?\|True\|False)`, float-inclusive as §2.1 describes. Value-parse branch L320 is `float(raw) if "." in raw else int(raw)` — the silent-drop bug named in §2.1 is genuinely fixed, not just the pattern. |
| 5 | PROGRESS.md Cycle 1/2 framing internally consistent | **PARTIAL — see M-2** | Attempts 1-4 preserved; Cycle 2 counter 0/3 present; but the Post-HALT note still asserts the counter question is unresolved. |
| 6 | Unscoped hostile sweep | **2 HIGH, 3 MEDIUM, 2 LOW below** | |

**Independent verification of the one new number (856).** 02 §2 L267-274 states 856 was
"re-derived directly from `candidates.jsonl`" and not re-run. I did not take that on trust and did
not use the same route: `results.md` §3's own committed table gives rule (c) total 2173,
test/fixture-path exclusion 1317, `range()` exclusion 0 — 2173 − 1317 = **856**, exactly. The
figure is reproducible from the committed evidence by a second, independent path. No finding.

---

## 2. Findings

### H-1 (HIGH) — the F2 doc↔script mismatch was fixed in one script and left in the other's output prose

`scan_fragments.py` imports the regex from `scan_thresholds.py` (L45-47), so its **detector** is
now float-inclusive too. But three artifacts still assert the old integer/boolean-only pattern as
current:

- `scan_fragments.py:133` — the F1 case comment: "§2.1's regex matches `(-?\d[\d_]*|True|False)`
  — integers and bools only — so a float is expected to MISS."
- `scan_fragments.py:252` — a hardcoded `A(...)` line that **emits** into §5 of any regenerated
  `results-fragment-shaped.md`: "The regex fallback matches integers and booleans only —
  `(-?\d[\d_]*|True|False)` per §2.1."
- `results-fragment-shaped.md:196-200` (committed) — the same claim, plus §2's `F1 — MISS` row and
  §3's `F1 ... 0/1` recall row, which the fixed detector no longer reproduces.

**Why this is the same defect class Frank's F2 named, one layer over**: a committed evidence
artifact states, by value, a detector shape that the shipped detector no longer has. Anyone
re-running `scan_fragments.py` today gets a results file whose §5 prose contradicts its own §3
table. Architecture §2.1 L208-210 discloses that the F1 *rerun* is open — it does **not** disclose
that the committed fragment results doc and the fragment script's own prose emitters now state a
false thing about the pattern. A cold reviewer who checks script-vs-doc (which attempt 4 did
explicitly) will land here.
**Fix (cheap, no rerun required)**: update `scan_fragments.py` L133/L252 prose to the fixed
pattern and reframe F1 as "expected PASS, not yet re-run", and add a dated stale-notice header to
`results-fragment-shaped.md` §5 pointing at 02 §2.1's fix note.

### H-2 (HIGH) — the sole citation for the only live timing number points at a deleted file

`02-ARCHITECTURE.md` §5.1 (L629, L640) and §13 (L978-979) cite **`GATE-LOG.md` attempt 3** as the
source for the 377ms `ast.parse` figure — "377ms is the disposition, cited to `GATE-LOG.md`
attempt 3". `GATE-LOG.md` **no longer exists** anywhere in this sprint directory (glob: no match);
it was consolidated into `PROGRESS.md` on 2026-09-05 per PROGRESS L5. The number itself survives
(PROGRESS.md Spec Gate, Cycle 1 attempt 3 row), so this is a broken citation path, not an
unsourced number — but it is a citation-by-path to a file a checker cannot open, in a document
whose entire subject is citation discipline. **Fix**: repoint both references to
`PROGRESS.md` → Spec Gate → Cycle 1 → attempt 3.

### M-1 (MEDIUM) — `PROXIMITY_WINDOW_THRESHOLD = 2`'s cited population was measured *with* the now-deleted exclusion applied

**STALE/SUPERSEDED (2026-09-06):** `PROXIMITY_WINDOW_THRESHOLD = 2` and this finding's "the window
is retained" recommendation are superseded by `02-ARCHITECTURE.md` §4 (constant deleted,
contiguous-comment-block-above rule adopted instead, following a real Frank forge-gate FAIL that
found the symmetric window checked the wrong thing). Left unedited below as a historical review
record.

`results.md` §5 computes the comment-distance distribution over "assignment candidates (net of
exclusions): **185**" — and "net of exclusions" in that script includes `EXCLUDED_VALUES =
{0,1,-1,2}` (`scan_thresholds.py:97-98`). The adopted design no longer applies that filter, so the
live assignment-candidate population is strictly larger than the 185 the window was measured over.
02 §4 L482-485 nonetheless claims 2 lines "captures 100% of the real comment-to-constant distances
observed in this exact corpus."

The value is very likely still right (added candidates are small idiomatic literals, which are
less likely to carry citation comments, and 3-12 was empty across the whole capped scan), and the
failure direction is benign under `log_only`. But the *claim's scope* no longer matches the
*design's scope* — which is precisely the promoted-default shape this repo's rule 1 exists to
catch, and it is currently unstated. **Fix**: one sentence in §4 naming that the 185 denominator
was exclusion-filtered, that the shipped population is wider, and that the window is retained on
the 3-12-empty margin — or a cheap re-derivation from `candidates.jsonl` with the filter off.

### M-2 (MEDIUM) — PROGRESS.md contradicts itself on whether the cycle/counter question is resolved

- L7 (Cycle authorization note): Danny "explicitly authorized ... closing out the original
  3-attempt cycle ... and starting a new gate cycle."
- L29 item (3): "**RESOLVED 2026-09-05**".
- L25 (Post-HALT note), unedited: "Whether this counts as a new loop (counter reset) or a
  continuation of the same 3/3-exhausted loop **was never explicitly settled with Danny** before
  this attempt ran — flagged here as unresolved."

Same file, two live statements, opposite claims, on the one question the attempt-4 F4 process
finding was about. Objective 5 otherwise passes (attempts 1-4 preserved as history, Cycle 2 counter
present at 0/3). **Fix**: amend L25 to past tense with a forward pointer to L7.

### M-3 (MEDIUM) — the benchmark directory has no record of the deletion decision

`scan_thresholds.py:97` still reads "Existing exclusion: the literal values {0, 1, -1, 2} — NOT YET
BENCHMARKED per §2", and `results.md:160-161` still reads "remains unvalidated ... open for a human
decision." Both are accurate *as a record of that run* and the spec docs correctly frame the table
as historical — but a reader arriving at `docs/research/domain-boundary-hook-benchmark/` first (the
"check the input before the instrument" path) is told the exclusion is live and pending. **Fix**: a
2-line dated note at the top of `results.md` recording the 2026-09-05 deletion decision and
pointing at 02 §2. Do not edit the machine-generated body.

### L-1 (LOW) — Roadmap misattributes the incumbent `PROXIMITY_WINDOW = 5` to the wrapper file

`04-ROADMAP.md` Deferred, L678-681: "that constant sits in `.claude/hooks/domain-boundary-
provenance.sh`'s already-LOCKED ... sibling file territory." Verified by direct read:
`PROXIMITY_WINDOW = 5` is at **`scripts/domain_boundary_provenance_probe.py:51`**, which is also
what 02 §7/§8 and Slice 4 L227/L285 say. The roadmap's Deferred bullet is the only place naming the
wrong file. Cosmetic, but it is a file-touch-scope statement, so it should be exact.

### L-2 (LOW) — PROGRESS.md Forge Gate carries unfilled template placeholders

L42-44: `Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING` and
`Orchestrator independent re-derivation: AGREES | DISAGREES` sit below an empty Forge Gate table.
Harmless, but reads as an unfilled field rather than a template in a doc that is otherwise the
sprint's ground truth.

---

## 3. Requirements → Architecture Coverage

| Requirement | Architecture coverage | Status |
|---|---|---|
| US-1 (flag unmarked threshold-shaped literals) | §2 three contexts, §2.1 parse chain, §7 `detect_threshold_literals` | ✅ |
| US-1 AC (no domain-crossing precondition) | §3 "No manifest coupling"; §7 `run_local_threshold_pass` gated on `.py` + non-test only | ✅ |
| US-2 (`log_only` first) | §5 mode config, fail-safe default; §6 `mode` non-nullable | ✅ |
| US-3 (fail-open, append-only log) | §3 pseudocode, §6 schema, §5.1 timeout disposition | ✅ (timeout re-measurement open, §13, tracked) |
| US-4 (presence only, no soundness claim) | §4 marker rule; §8 G-4 → grep test | ✅ |
| Constraint: no literal-value exclusion | §2 disposition, §7 comment L778-780 | ✅ |

## 4. Architecture → Roadmap Coverage

Every §2-§7 component maps to exactly one slice; spot-checked `load_mode_config`→2,
`detect_threshold_literals`→3, `has_threshold_provenance_marker`→4, `combine`→6, schema→7, wrapper
mode-read→8, self-scan fixtures→9, wiring→10, addendum/roster→11, e2e→12. No circular dependencies.
Exclusion-removal is propagated into Slices 3, 9, 12 and Deferred. ✅ (one file-path error, L-1.)

## 5. Risks

| Risk | L | I | Mitigation |
|---|---|---|---|
| Fragment evidence doc read as current, stating a superseded pattern (H-1) | H | M | Fix prose + stale notice; rerun F1 when convenient |
| Window `2` over-claimed against a widened population (M-1) | M | L | Name the denominator change; `log_only` bounds cost |
| 856-candidate volume makes the `log_only` log unusably noisy in triage | M | M | Per-repo triage is already the explicit design; Slice 12 records observed volume |
| Precision still unmeasured at any scale | H | M | Named in §2/§13 and both results docs; not discharged |
| Broken `GATE-LOG.md` citation propagates into forge docs (H-2) | M | L | Repoint before approval |

## 6. Assumptions

| Assumption | Impact if wrong |
|---|---|
| Removing the value filter does not shift the 2-line comment-distance distribution | Window under-covers; some cited constants flagged anyway (noise, not miss) |
| `scan_fragments.py`'s imported (now-fixed) regex needs no rerun to remain trustworthy | F1's committed MISS row stays contradicted by the shipped code |
| 445-file corpus is representative of consuming repos | Volume/window figures shift on retrofit; §11 already states this is not stress-tested |

## 7. Open Questions

| Question | Status | Resolution |
|---|---|---|
| Is `results-fragment-shaped.md` regenerated (F1 rerun) before or after forge? | Open | Danny/Frank call; H-1's prose fix is required either way |
| Route for the incumbent's unmarked `PROXIMITY_WINDOW = 5` (same-sprint vs. follow-up) | Open | Danny — already surfaced in 02 §11, 04 Deferred |
| Does the timeout re-measurement (§5.1) block forge-start or land inside Slice 12? | Open | Currently written as a forge-tracked item, not a gate blocker |

## 8. Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [ ] Acceptance criteria testable — reviewer finds them testable as written
- [ ] Out of scope acceptable

### Architecture (02)
- [ ] Reviewed by human
- [ ] H-2 citation repointed (`GATE-LOG.md` → `PROGRESS.md`)
- [ ] M-1 window-denominator caveat added to §4

### Roadmap (04)
- [ ] Reviewed by human
- [ ] L-1 file path corrected in Deferred

### Evidence (`docs/research/domain-boundary-hook-benchmark/`)
- [ ] H-1 prose fixed in `scan_fragments.py` + stale notice in `results-fragment-shaped.md`
- [ ] M-3 deletion-decision note added to `results.md`

### Process (PROGRESS.md)
- [ ] M-2 Post-HALT note amended; L-2 placeholders cleared

### Overall
- [ ] Open questions routed
- [ ] Ready for Frank Cycle 2 attempt 1

---

*No HALT. The documents are mutually consistent on the sprint's substance; every finding above is a
stale statement or a citation path, all cheap to fix, none requiring a design change.*
