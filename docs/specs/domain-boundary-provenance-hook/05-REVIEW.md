# Spec Review: Unsourced-Threshold Provenance Hook

**Status**: COMPLETE — review performed, 2 critical gaps documented (human decides)
**Date**: 2026-09-05
**Reviewer**: spec-reviewer (independent)
**Documents reviewed** (versions on disk at commit `e39f941`): `INTAKE.md`, `INTERVIEW.md`,
`NORTH-STAR.md`, `01-REQUIREMENTS.md`, `02-ARCHITECTURE.md`, `04-ROADMAP.md`
**Evidence reviewed**: `docs/research/domain-boundary-hook-benchmark/{scan_thresholds.py,results.md,candidates.jsonl}`
**Live source cross-checked**: `scripts/domain_boundary_provenance_probe.py`,
`.claude/hooks/domain-boundary-provenance.sh`, `docs/tooling/domain-boundary-provenance-hook.md`,
`/home/d-tuned/projects/gap-lens-dilution-filter/research/gates/measure_oq5_residue.py`

This document supersedes the prior `05-REVIEW.md` in full. Prior review content (G-1…G-9) is
treated as history; where the current docs cite those IDs, they are cited as history here too.

---

## 0. Primary Check — Is the Recall Claim Real?

This was the single most important check, and it is the one two prior passes skipped. Method: the
review environment for this pass has no shell, so the script was **not executed**; the claim was
verified by (a) reading `scan_thresholds.py`'s detection logic line by line, (b) tracing each
incident's actual source construct through that logic, (c) corroborating against the committed
`candidates.jsonl` raw row, and (d) confirming the incident source line exists in the live file.
That is stated plainly so the ceiling of this verification is visible.

### 0.1 Is `scan_thresholds.py` a real, runnable script?

**Yes.** It is a 555-line executable Python module with a `main()` under
`if __name__ == "__main__"`. It defines the corpus in code (`CORPUS_ROOTS`), walks it, parses each
file with `ast`, emits `results.md` and `candidates.jsonl` by writing them from computed values
(every number in `results.md` is interpolated from a variable — verified by matching the f-strings
at script L462-L502 against the rendered tables in `results.md` §3/§4/§5). It is not decorative,
and `results.md` is not hand-writable without also faking `candidates.jsonl`.

Notably, its own docstring (L8-L13) names the prior audit's numbers — 84.7%, 32.5%, 76ms — as
**not reproducible**, and records Frank's cold re-run values (96.9%, 0%, 377ms). This matters for
G-3 below.

### 0.2 Trace: why rules (a) and (b) score 0/2

`Candidate.rules()` (L125-L132) is the only place rule membership is assigned:

- `context == "comparison"` → `{a,b,c,d}`
- `context == "slice_trunc"` → `{b,c,d}`
- assignment contexts → `{c,d}` if `is_upper` else `{c}`

Both incidents are produced **only** by `scan_assignments()` (L246-L261), which emits
`assign_module` / `assign_class`. Neither `visit_Compare` nor `visit_Subscript`/`visit_Call` can
produce them. Therefore rules (a) and (b) cannot generate either incident as a candidate at all.
`recall_check()` further filters `hits` by `target_name`, and only assignment candidates carry a
`target_name` — so the miss is structural, not a scoring artifact.

**0/2 for rules (a) and (b) is VERIFIED as a structural property of the rule definitions, not an
assertion.** Architecture §0.2's root-cause statement ("rule (b) has no assignment-detection path
at all") is exactly correct.

### 0.3 Trace: I1 `_HEAD_BYTES = 65_536`

- Live source confirmed: `research/gates/measure_oq5_residue.py:69` → `_HEAD_BYTES = 65_536`.
- Module-level `ast.Assign`, single `ast.Name` target → `handle(tree.body, "assign_module")`
  (L261) → `_add(stmt.value, "assign_module", target_name="_HEAD_BYTES")`.
- `literal_value` accepts `ast.Constant` int → ok.
- `is_upper_name("_HEAD_BYTES")`: `lstrip("_")` → `"HEAD_BYTES"`, `.upper() == itself`, has alpha
  → **True** → `rules()` = `{c, d}`.
- `net_flagged()`: `65536 ∉ {0,1,-1,2}`; path parts `("research","gates")` contain no test
  component and stem is not `test_*` → **True**.
- **Independently corroborated** by `candidates.jsonl` L869, which records exactly:
  `line 69, context assign_module, target_name _HEAD_BYTES, is_upper true, net_flagged true,
  rules ["c","d"]`.

**I1: (c) PASS, (d) PASS, (a)/(b) MISS — VERIFIED.**

### 0.4 Trace: I2 `filing_text_max_bytes: int = 512_000`

- Class-body `ast.AnnAssign` with `ast.Name` target and non-None value → the `elif` at L256-L258
  inside `handle(stmt.body, "assign_class")` (reached via the `ClassDef` branch at L259-L260).
- `is_upper_name("filing_text_max_bytes")` → `"filing_text_max_bytes".upper() != itself` →
  **False** → `rules()` = `{c}` only. **This is why (d) misses I2** — verified as a direct
  consequence of the case restriction, exactly as Architecture §2 and §10 state.
- `net_flagged()`: `512000 ∉ {0,1,-1,2}`; path `research/pipeline/config.py` has no test component
  → True.

**I2: (c) PASS, (d) MISS, (a)/(b) MISS — VERIFIED by logic trace.** Weaker than I1: I2 has no
`candidates.jsonl` row (it is deleted at HEAD and recovered via
`git -C <gap-lens-dilution-filter> show 7d9fdf5:research/pipeline/config.py`, L340-L343), so the
only corroboration available inside agent-rig is the trace plus `results.md` §4's rendered row. See
G-9.

### 0.5 Verdict on the primary check

The recall table in Architecture §2 (a 0/2, b 0/2, c 2/2, d 1/2) **matches `results.md` §4
exactly** and **matches the traced logic exactly**. Architecture does not paraphrase the evidence
in a way that drifts from it. The adopted rule (c) is the only candidate that clears the
disqualifying ground-truth test. **The core correction this sprint made is sound.**

Two caveats recorded as risks rather than gaps (R-1, R-2): the rule was selected *after* seeing
both incidents, so 2/2 is a fit to an n=2 test set, not a held-out result; and `results.md` §6
explicitly declines to pick a winner, which means the "adopt (c)" step is an architecture judgment
resting on the recall column alone — correctly attributed as such in Architecture §2.

---

## 1. Requirements Completeness (01)

- [x] Summary present and clear
- [x] User stories in "As a… I want… so that…" form (US-1…US-4)
- [x] Every user story has acceptance criteria
- [x] Edge cases table populated (9 rows)
- [x] Out of Scope non-empty (6 entries + 1 deferred)
- [x] Constraints concrete

### Requirements Gaps

| Gap | Impact |
|-----|--------|
| No user story or AC covers the `THRESHOLD-PROVENANCE:` marker itself. The marker is introduced entirely in Architecture §4; Requirements only mentions it inside the "Assumes:" bullet at the end of Constraints. | The user-facing contract of the whole check ("what must I write to satisfy it") has no requirement to trace to. Roadmap Slice 4 is therefore architecture-traced only. Low severity — it is specified, just in the wrong document — but it means no AC fails if the marker string changes. |
| US-2 AC2 describes the `blocking` path in detail, but no AC covers what a repo owner must do to *promote* to blocking, and Architecture §3's reconciliation names a data condition ("false-positive rate low enough") that no requirement or roadmap slice produces. | Promotion is out of scope this sprint (correctly), but the exit criterion for `log_only` is stated only in prose in Architecture §3, unowned and unmeasured. Acceptable as-shipped; noted so it is not later mistaken for a defined gate. |

---

## 2. Architecture Completeness (02)

- [x] Every requirement has architecture coverage (table below)
- [x] Schemas are real, not pseudocode (§6 TypeScript interfaces, §7 Python signatures + TypedDicts)
- [x] Patterns justified (§10, each with a rationale row)
- [x] Integration points documented (§11, five entries, including a corrected F2 entry)

### Requirements → Architecture Coverage

| Requirement | Architecture Coverage | Status |
|---|---|---|
| US-1 (scan Edit/Write for uncited threshold literals) | §2 detection rule (3 contexts), §7 `detect_threshold_literals`, §3 composition | ⚠️ — covered in design, but see G-1: the scan surface §1/§7 actually operate on is not the population the rule was measured against |
| US-1 AC4 (module/class-level named assignment flagged) | §2 context 3, §7 `context: "assign_module_or_class"` | ✅ |
| US-1 AC5 (no domain-crossing precondition in the new pass) | §3 "No manifest coupling"; §7 `run_local_threshold_pass` gated on `.py` + non-test path only | ✅ |
| US-2 (`log_only` first, `blocking` opt-in) | §5 `DomainBoundaryModeConfig`, fail-safe default, §3 `combine()` downgrade | ✅ |
| US-2 AC3 (never ships blocking) | §5 committed `{"schemaVersion":1,"mode":"log_only"}` | ✅ |
| US-3 (fail-open + append-only log) | §7 syntax-error→`[]`; §5.1 timeout; §6 `probe_error` in decision union | ✅ |
| US-3 (every run logged) | §3 single `write_track_record(combined)` per invocation | ✅ |
| US-4 (presence-only, no soundness judgment) | §8 G-4 row (deferred to Roadmap Slice 9 grep test) | ✅ |
| Requirements Edge Case: "PROVISIONAL tag without a named owner → treated as absent, flagged" | §4 v1 citation rule — **marker presence only** | ❌ — **direct contradiction, G-2** |
| Constraint: every constant carries a citation or named-owner PROVISIONAL | §2 (`results.md` §3/§4), §4/§7 (`results.md` §5) | ⚠️ — holds for the detection constants; fails for §5.1's timing figures (G-3) |

### Architecture Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| **G-1: The benchmark measured whole `.py` files; the hook scans `tool_input.new_string` fragments.** `get_scan_surface` (live probe L150-L162, reused verbatim per §1) returns the raw `new_string` for an `Edit` — a fragment, not a module. §7 specifies `ast.parse(scan_surface)` with `SyntaxError → return []`. An `Edit` whose `new_string` is an indented class-body line (exactly I2's shape, `filing_text_max_bytes: int = 512_000` inside a dataclass) raises `IndentationError` (a `SyntaxError` subclass) and is silently dropped. Even when it parses, context 3 requires `Module`/`ClassDef` body scope, which a bare fragment only satisfies for the module-level case. | **CRITICAL** | The 2/2 recall result was measured on the 445-file whole-file corpus. It does not transfer to the hook's actual input population without a separate measurement. I1's shape survives (a module-level `NAME = <lit>` fragment parses standalone); I2's shape plausibly does not. This is the same class of defect the sprint is correcting — evidence drawn from a different population than the instrument consumes — one layer down. No document names it. |
| **G-2: The named-owner requirement is not implemented.** `INTAKE.md`'s amended Problem Statement (spec-of-record) requires "an explicit `PROVISIONAL — unvalidated` marker **naming a human owner**." `01-REQUIREMENTS.md` carries this in US-1 AC2 ("PROVISIONAL tag naming a human owner"), the Edge Cases table ("A PROVISIONAL tag but does not name a human owner → treated as absent — flagged"), and NORTH-STAR's Declared Intent. Architecture §4's v1 citation rule is **marker string + non-whitespace content, nothing more**, and Roadmap Slice 4 states it explicitly: "this function only checks marker presence within the window, not which of the three satisfying forms is used." | **CRITICAL** | `# THRESHOLD-PROVENANCE: TODO` satisfies the shipped check and violates the spec-of-record. This is Frank's F4 restated, not reconciled — see §5 below for the full disposition. It also makes Roadmap internally contradictory: Slice 9 requires a fixture for "the unowned-PROVISIONAL-treated-as-absent edge case," which Slice 4's own specified behavior makes unimplementable. |
| **G-3: §5.1's `ast.parse` timing figures are the discredited numbers.** §5.1 asserts ~8ms and ~76ms, "Measured 2026-09-05, reproducible via `python3 -c ...`". `scan_thresholds.py`'s own docstring (L8-L13) names **76ms** as one of the three numbers from the prior audit that "were NOT reproducible… Frank's cold re-run got materially different values (96.9%, 0%, **377ms**)." No committed artifact backs the 8ms/76ms pair; the one committed artifact contradicts it by name. | **HIGH** | The conclusion (timing ≪ 5000ms) survives even at Frank's 377ms, so the *decision* is not at risk — but a number the committed evidence explicitly flags as unreproducible is still carried in this doc as "measured, reproducible." That is precisely the residue this correction pass was supposed to sweep. Per CLAUDE.md's "one bad number → audit the whole set," it should not have survived. |
| G-5: §2 cites "this document's task brief" as the source for the "60-70%" range characterisation. | MEDIUM | A task brief is not path-addressable or reproducible. The table immediately above it *is* correctly cited to `results.md` §3, so the fix is to delete the sentence, not to source it. |
| G-7: §12 items 7 and 8 state the Requirements and Roadmap corrections are "NOT yet applied — reported for separate routing." Both **have** since been applied (verified: Requirements' Detection Rule Pointer and Roadmap Slice 3 both describe three contexts). | LOW | §12's status column is now false. It reads as an open action item that is actually closed; a forge agent following §12 would go looking for uncorrected drift that does not exist. |
| G-8: §0.1 asserts "no constant in this document rests on a self-assigned or unassigned `owner:` tag," while §5.1 quotes the incumbent wrapper's own `PROVISIONAL — owner: wright` self-assigned tag and §11 routes it to Danny. | LOW | Not a contradiction in substance (the wrapper's tag is out of file-touch scope and correctly reported outward), but §0.1's absolute phrasing overstates. Wording only. |
| G-9: I2's recall depends on `git show 7d9fdf5:research/pipeline/config.py` in a **different repo**. If that history is rewritten, or the repo is absent, `recall_check()` sets status `UNAVAILABLE — recall NOT measured` (L353-L354) and I2 silently becomes a MISS column for every rule. | LOW | Correctly and honestly handled by the script (it reports rather than guesses). Recorded so a future re-run that shows `d`/`c` both at 1/2 is read as "evidence unavailable," not "rule changed." |

---

## 3. UI Spec (03)

**Not applicable — no `03-UI-SPEC.md` exists and none is required.** `INTAKE.md` Mode explicitly
records "Full sequence run without UI-SPEC (Step 5 skipped, no UI/product surface either way)."
Verified: this sprint's only user-facing surfaces are a hook deny/flag `reason` string and a JSONL
log entry, both specified in Architecture §3/§6 and tested in Roadmap Slice 9. **Not a gap.**

---

## 4. Roadmap Completeness (04)

- [x] Every architecture component maps to exactly one slice (table below)
- [x] No circular dependencies (Dependency Map is a strict partial order; each row depends only on rows above)
- [x] Each slice has Done-When criteria
- [x] File paths concrete — every path verified to exist or to be precisely named as new

### Architecture → Roadmap Coverage

| Component (Arch §) | Slice | Status |
|---|---|---|
| `run_cross_domain_pass()` extraction (§3/§7) | 1 | ✅ |
| `load_mode_config()` + `domain-boundary-mode.json` (§5) | 2 | ✅ |
| `detect_threshold_literals()`, 3 contexts + exclusions (§2/§7) | 3 | ⚠️ — implementation notes are accurate to §2, but Slice 3 carries an unsourced number (G-4) and inherits G-1 |
| `has_threshold_provenance_marker()`, `PROXIMITY_WINDOW_THRESHOLD = 2` (§4/§7) | 4 | ❌ — contradicts Requirements on named-owner (G-2) |
| `run_local_threshold_pass()` (§7) | 5 | ✅ |
| `combine()` + `CombinedResult` (§3/§7) | 6 | ✅ |
| `TrackRecordEntry` migration + `run()` restructure (§6) | 7 | ✅ |
| Wrapper mode-config read, non-nullable `mode` (§6 G-5 resolution) | 8 | ✅ |
| Self-scan fixtures + G-4 grep test (§8/§13) | 9 | ⚠️ — requires a fixture (unowned-PROVISIONAL) that Slice 4's spec cannot satisfy (G-2) |
| `.claude/settings.json` wiring (§5/§11) | 10 | ✅ |
| LOCKED-doc addendum + roster row (§11) | 11 | ✅ |
| End-to-end `log_only` verification (§5) | 12 | ⚠️ — Done-When expects the `PROXIMITY_WINDOW` self-scan flag on a live `Edit`; per G-1 an `Edit` fragment may not reproduce it |
| `{0,1,-1,2}` labeling plan (§2 steps 1-5) | Deferred (explicit) | ✅ — correctly deferred, not silently closed |

### Roadmap Gaps

| Gap | Severity | Impact |
|-----|----------|--------|
| **G-4: Slice 3's implementation notes assert "measured 8/10 words never fire in this repo, plus 11 measured false positives"** for the discarded vocabulary gate. Neither number appears anywhere in `results.md`; `scan_thresholds.py` never implements a vocabulary gate, so it *cannot* have produced them. They originate in the discredited prior audit. Architecture §10 makes the same claim ("Benchmark-measured on two axes… 8/10 words never fire") in its Patterns table. | **HIGH** | Two bare, unreproducible numbers survived a correction pass whose entire premise was "every number cites a committed file." They support a decision (drop the vocabulary gate) that is independently justified by the recall table, so the decision stands — but the numbers must be deleted or re-derived, not left as prose assertions. |
| Slice 12's fourth Done-When ("at least one live run… surfaces a `flag`… expected to include the `PROXIMITY_WINDOW` self-scan finding") is stated as an expectation, not a required outcome, and per G-1 may not fire under `Edit`. | MEDIUM | A verification criterion that can pass vacuously. Should be pinned to a `Write` of the full probe file, or restated as a measurement rather than an expectation. |
| Slice 6's implementation note tells the implementer to resolve an ambiguity in Architecture §3 at code time ("if ambiguous, prefer always labeling… flag choice in code comment, not a spec deviation"). | LOW | Small, bounded, and honestly labeled — but it is a spec ambiguity being pushed into code. Architecture §3 does state the rule ("If either pass alone denies, that pass's reason is used unmodified"); the note should simply follow it. |

---

## 5. Targeted Checks (task objectives 2-7)

### 5.1 Objective 2 — Internal consistency across documents

| Item | Requirements | Architecture | Roadmap | Verdict |
|---|---|---|---|---|
| Three detection contexts (comparison / slice-truncation / module-class named assignment, no vocabulary or case gate) | Summary, US-1 AC1+AC4, Detection Rule Pointer, Edge Cases | §2, §7 `FlaggedLiteral.context`, §10 | Dependency Map, Slice 3 goal + notes + tests, HALT Check | ✅ **CONSISTENT** — no drift, all three name the same three contexts in the same terms |
| `PROXIMITY_WINDOW_THRESHOLD = 2` | Constraints + final Assumes bullet (cites `results.md` §5) | §4 decision, §7 constant + inline citation, §10 | Dependency Map, Slices 4, 9 | ✅ **CONSISTENT** — same value, same citation, all three state it is a *new* constant, not a reuse |
| Self-scan resolution: incumbent's `PROXIMITY_WINDOW = 5` **IS** flagged (not moot) | (silent — not mentioned) | §8 G-9 row, §11, §13 | Slice 4 notes + test, Slice 9 fixture + Done-When, Slice 12, Deferred | ✅ **CONSISTENT** — direction reversal is carried correctly everywhere it appears; Requirements' silence is acceptable (it is an architecture-level consequence) |
| Live-source check | — | — | — | ✅ `PROXIMITY_WINDOW = 5` confirmed at `scripts/domain_boundary_provenance_probe.py:51`, module-level `NAME = <int>`, no `THRESHOLD-PROVENANCE:` comment anywhere in the file. Under rule (c) it is a genuine unmarked match. The finding is real, not theoretical. |
| Named-owner PROVISIONAL | Required (AC2, Edge Case) | Not required (§4 presence-only) | Not required (Slice 4) **but** required (Slice 9 fixture) | ❌ **INCONSISTENT — G-2** |

### 5.2 Objective 3 — Any surviving "no assignment is ever flagged" / two-context claims?

**No, in the current documents.** Full-text search across all six docs found:

- `01-REQUIREMENTS.md` L119/L121 — "two-context-only rule… measured recall 0/2 under the
  two-context rule, 2/2 under the corrected three-context rule." This is **historical narrative
  describing the discarded rule**, correctly framed and correctly attributed to `results.md` §4.
  Not a live claim. ✅
- `02-ARCHITECTURE.md` L760/L766 (§12 items 7-8) — quotes the old "two shape-based syntactic
  contexts" text as something needing correction. Historical, but its *status* is stale (G-7).
- `04-ROADMAP.md` L656/L672 — same historical framing. ✅
- `02-ARCHITECTURE.md` L151 "never flagged" / L602 "not flagged" / `04-ROADMAP.md` L171-L172 —
  these refer to the **exclusion set and syntax-error fail-open**, not to assignments. ✅
- `.gate-snapshots/spec/attempt-1/` contains the old two-context text. These are gate archives, not
  spec documents. Correct to leave untouched. ✅

**No document makes a live claim that assignments are exempt.** Objective 3 clears.

### 5.3 Objective 4 — Is the `{0,1,-1,2}` disposition still honest?

**Yes — this is the strongest-handled item in the doc set.** Verified against `results.md` §6,
which states verbatim: "The `{0,1,-1,2}` exclusion set remains unvalidated — this run measures its
SHARE, which is its leverage, not its correctness."

- Architecture §2 reproduces the leverage table cited to `results.md` §3 (60.5% under rule (c)),
  states in bold "**Leverage is now measured. Correctness is not,**" quotes `results.md` §6
  directly, explicitly supersedes the old unreproducible 84.7% figure **and says it was measured
  under the wrong rule**, and carries a 5-step executable validation plan with a concrete exclusion
  threshold (precision < 5%) and a named data source (`candidates.jsonl`).
- Architecture §13 carries it as an open item: "correctness (precision) still NOT YET BENCHMARKED."
- `01-REQUIREMENTS.md` Detection Rule Pointer: "NOT YET BENCHMARKED for precision… not to be
  treated as validated until that plan runs."
- Roadmap Slice 3 notes repeat it; Roadmap **Deferred** lists running the plan as explicitly out of
  scope.

**No silent upgrade to "resolved." Disposition is honest in all four places, with a concrete next
step and a named artifact to draw the sample from.** ✅

### 5.4 Objective 5 — Frank's F4 (citation-marker owner) — is it reconciled?

**NO. It is restated with the same ambiguity, in a form that now actively contradicts itself.** This
is G-2 and is the review's second critical finding.

The governing rule is not in dispute. `INTAKE.md`'s amended Problem Statement (spec-of-record, via
gap-lens-dilution-filter DDR-0014 §Amendment) requires a marker "naming a human owner." Danny's
separate 2026-09-05 ruling makes self-assigned or unassigned ownership invalid. Architecture §0.1
even acknowledges the ruling by name: "no constant in this document rests on a self-assigned or
unassigned `owner:` tag."

But the ruling is applied only to **the spec's own constants** — it is never applied to **the check
the spec builds**. Trace the three answers:

1. `01-REQUIREMENTS.md` US-1 AC2: does not flag a tag "naming a human owner." Edge Cases: a tag that
   "does not name a human owner" is "**treated as absent — flagged**." → **owner required.**
2. `02-ARCHITECTURE.md` §4 "v1 citation rule for the new check": "A citation is a comment line
   containing the literal marker `THRESHOLD-PROVENANCE:` (case-sensitive, exact string) followed by
   **non-whitespace content on the same line**." §4's third bullet describes option (b) as "an
   explicit PROVISIONAL disposition **naming what would validate it**" — a different thing from
   naming an owner. → **owner not required.**
3. `04-ROADMAP.md` Slice 4: "A `THRESHOLD-PROVENANCE: PROVISIONAL — …` line is a valid, complete
   citation… this function **only checks marker presence** within the window, not which of the three
   satisfying forms is used (that distinction is not needed here; presence is presence)." →
   **owner not required, explicitly and deliberately.**

Then Roadmap Slice 9 requires a corpus fixture for "the unowned-PROVISIONAL-treated-as-absent edge
case (Requirements Edge Cases table)" — a test that Slice 4's own specification guarantees will
fail. A forge agent working slices in order will build Slice 4 to spec, then be unable to satisfy
Slice 9 without changing Slice 4.

**This is not a nitpick and not a wording issue.** The check's entire purpose is mechanizing
CLAUDE.md rule 1, whose option (b) is "an explicit `PROVISIONAL — unvalidated` marker **with a named
human owner**." As specified in Architecture §4, `# THRESHOLD-PROVENANCE: PROVISIONAL — TODO`
passes. The hook would certify exactly the unowned tag the ruling invalidates.

**Required before approval — a single explicit decision, recorded in Architecture §4 and mirrored
into Requirements and Roadmap Slice 4:** either (i) v1 requires an owner (define the machine-checkable
form — e.g. `PROVISIONAL — owner: <name>` — and update Slice 4's test list), or (ii) v1 is
presence-only, in which case Requirements' AC2 and Edge Case row must be corrected and the residual
gap named as a known limitation with a follow-up owner. **Do not leave both statements standing.**

### 5.5 Objective 6 — Does every constant cite a committed, path-addressable source?

| Constant | Cited to | Verified against source | Verdict |
|---|---|---|---|
| 3 detection contexts / rule (c) adopted | `results.md` §2, §4 | Rule (c) definition matches `results.md` §2 row and `Candidate.rules()` L125-L132; recall table matches §4 exactly | ✅ |
| 0/2, 0/2, 2/2, 1/2 recall | `results.md` §4 | Traced through script + `candidates.jsonl` L869 (see §0) | ✅ |
| `{0,1,-1,2}` share 60.5% (and 70.0/65.8/60.9) | `results.md` §3 | Matches `results.md` §3 table row-for-row | ✅ |
| 2173 total / 481 net flagged, 1922 under (b) | `results.md` §3 | Matches | ✅ |
| Context counts 1768 / 154 / 176 / 75 | `results.md` §3 | Matches | ✅ |
| `range()` exclusion fires 0 times → removed | `results.md` §3 | Matches; script L469 computes it from `all_cands`; structural argument independently correct (a `range()` arg is a `Call` arg, unreachable by all four rules) | ✅ |
| `PROXIMITY_WINDOW_THRESHOLD = 2`; 93.5% @1, 100.0% @2, 0 beyond | `results.md` §5 | Matches §5 rule (c) block exactly (58 @1, 4 @2, 185 candidates, 62 commented) | ✅ |
| 445-file corpus, 10 roots | `results.md` §1 | Matches; `CORPUS_ROOTS` defined in code; missing roots reported not guessed | ✅ |
| **`ast.parse` ~8ms / ~76ms (§5.1)** | "measured 2026-09-05", no artifact | **Contradicted by `scan_thresholds.py` L8-L13, which names 76ms as non-reproducible and records Frank's 377ms** | ❌ **G-3** |
| **Vocabulary gate: "8/10 words never fire", "11 measured false positives" (Arch §10, Roadmap Slice 3)** | none — bare assertion | Absent from `results.md`; script implements no vocabulary gate and cannot have produced these | ❌ **G-4** |
| "60-70%" range | "this document's task brief" | Not path-addressable | ⚠️ **G-5** |
| Incumbent `PROXIMITY_WINDOW = 5` | not re-justified (explicitly out of scope) | Confirmed at probe L51; §4 states plainly it was never measured against this corpus and is deliberately not imported | ✅ — correct handling |
| 5s probe timeout | §5.1 re-justification | Conclusion holds even at Frank's 377ms, but rests on G-3's numbers | ⚠️ |

**Two constants fail (G-3, G-4), one is weakly sourced (G-5). Every constant governing the
detection rule itself passes.** The failures are all residue from the discredited prior audit,
concentrated in §5.1 and the vocabulary-gate rationale — the two areas the correction pass did not
rewrite. Per CLAUDE.md ("one bad number found → audit the whole doc set"), the sweep was incomplete.

### 5.6 Objective 7 — Out-of-scope boundary

**Consistent across all six documents.** ✅

- agent-rig build only, no retrofit: `INTAKE.md` OQ4 → `INTERVIEW.md` Q1 answer → `NORTH-STAR.md`
  In/Out of Scope → `01-REQUIREMENTS.md` Summary + Out of Scope → `04-ROADMAP.md` Scope + Deferred.
  Same claim, same reason, no drift.
- Incumbent extended, not replaced: `NORTH-STAR.md` Declared Intent, Requirements Out of Scope
  bullet 6 + Constraints ("extend… in place… rather than building a new hook"), Architecture §0/§1
  ("Danny's decision (settled)"), Roadmap Scope ("No new/second hook") and Deferred (last bullet).
  Architecture §1's table is the authoritative unchanged/changed split and nothing downstream
  contradicts it.
- Verified against live source: the incumbent files exist, `get_scan_surface` is reused verbatim as
  §1 claims, and the LOCKED doc is real. Slice 11's "§2-§10 byte-identical" constraint is
  enforceable.
- One genuine tension, correctly surfaced rather than hidden: Architecture §3's reconciliation of
  the LOCKED doc's recorded rejection of unscoped blocking, and §3/§5's explicit naming of the
  behavior change to the LOCKED doc's AC4. Both are named, not absorbed by silence. Good practice.

---

## 6. Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **R-1: Benchmark population ≠ hook input population (G-1).** Recall measured on whole files; hook scans `Edit` fragments that may not parse or may lack module/class scope. | H | H | Before Slice 3 is accepted, add a measurement: run `detect_threshold_literals` against realistic `new_string` fragments (including an indented class-body assignment, I2's shape) and record recall. If fragment recall on I2's shape is 0, either de-indent-and-retry on `IndentationError`, or scope v1 honestly to `Write` + module-level `Edit` and name the limitation. |
| **R-2: Rule (c) is fit to an n=2 ground-truth set it was selected against.** No held-out incident exists. | H | M | Already partly mitigated: `results.md` §6 disclaims winner-picking, and Architecture §2 attributes adoption to a stated criterion (recall beats volume) rather than to the benchmark. Record explicitly in Architecture §2 that 2/2 is in-sample. |
| **R-3: 481 net-flagged candidates with unmeasured precision.** | H | M | `log_only` default (§5) converts this to a logging cost. The §2 labeling plan is the real mitigation; it is correctly deferred and named, not assumed away. |
| R-4: Unowned `PROVISIONAL` markers pass the check, certifying exactly what CLAUDE.md rule 1 forbids (G-2). | H | H | Resolve per §5.4 before approval. |
| R-5: Residual unreproducible numbers (G-3, G-4) get re-cited downstream as established. | M | M | Delete or re-derive both, then re-sweep. Any number not traceable to `results.md` or a re-runnable command should be removed. |
| R-6: `{0,1,-1,2}` exclusion hides a real unsourced threshold at one of those values. | M | M | Named as a known risk in Architecture §2 step 5 and §13. Accepted, documented, unresolved — correct posture. |
| R-7: Re-running `scan_thresholds.py` on a changed corpus shifts every cited number. | M | L | Architecture §11's benchmark bullet names this explicitly, including which conclusions are and are not expected to be robust. Well handled. |
| R-8: I2 recall depends on foreign-repo git history (G-9). | L | M | Script reports `UNAVAILABLE` rather than silently scoring MISS. Consider committing the recovered snippet as a fixture inside agent-rig. |
| R-9: Slice 1's "pure extraction, existing tests pass unmodified" is the only guard on the Frank-forge-gate-PASSED incumbent logic. | L | H | Sequence Rule 6 already isolates it. Adequate. |

---

## 7. Assumptions

| Assumption | Impact if Wrong |
|---|---|
| `results.md` and `candidates.jsonl` on disk are the genuine output of the committed `scan_thresholds.py` and have not been hand-edited. | If false, the entire evidence base is void. Partly checked: the numbers are consistent across `results.md` §3/§4/§5 and cross-corroborated by `candidates.jsonl` L869 for I1, and the script's f-string templates match the rendered output structurally. **Not fully verified — the script was not executed in this review** (no shell available). A re-run before approval would close this. |
| I2's constant exists at `7d9fdf5:research/pipeline/config.py` in gap-lens-dilution-filter as a class-body `AnnAssign`. | I2's 2/2 contribution is unverified and rule (d)'s 1/2 disadvantage may be wrong. Traced from `results.md` §4's rendered detail line (`line 47 ctx=assign_class value=512000 upper=False`), which is script-generated, but not independently opened. |
| An `Edit`'s `new_string` typically contains enough context to parse and to expose module/class scope. | **Assumed by the design and not stated anywhere.** This is R-1/G-1. |
| `log_only` makes flagged volume costless. | If the track-record log or triage burden becomes the bottleneck, the "volume is just a logging cost" argument in §2 weakens — though it never becomes a correctness problem. |
| The incumbent's cross-domain pass is behaviour-preserving under Slice 1's extraction. | Guarded by the unmodified pre-existing suite. Reasonable. |

---

## 8. Open Questions

| Question | Status | Resolution needed from |
|---|---|---|
| **Q-1 (G-2/F4): Does a `THRESHOLD-PROVENANCE: PROVISIONAL` marker require a named human owner in v1?** Requirements says yes; Architecture §4 and Roadmap Slice 4 say no; Roadmap Slice 9 requires a test that assumes yes. | **OPEN — blocking** | Danny. One answer, written into Architecture §4 and mirrored to Requirements AC2/Edge Cases and Roadmap Slices 4 and 9. |
| **Q-2 (G-1): Is the 2/2 recall claim valid against `Edit` fragments, or only whole files?** | **OPEN — blocking** | Measurement (a short fragment-level run), then a scope statement in Architecture §2. Not a judgment call — it is answerable. |
| **Q-3 (G-3/G-4): Do the §5.1 timing figures and the "8/10 words / 11 false positives" vocabulary claims get re-derived or deleted?** | OPEN | wright. Deletion is sufficient — neither number is load-bearing for a decision that the recall table does not already carry. |
| Q-4: Does the incumbent's `PROXIMITY_WINDOW = 5` get its `THRESHOLD-PROVENANCE:` comment this sprint or in a follow-up? | OPEN — correctly routed | Danny (Architecture §11, §13, Roadmap Deferred all route it outward rather than absorbing it). |
| Q-5: Should the recovered I2 snippet be committed into agent-rig as a fixture, to make recall verifiable without foreign-repo git history? | OPEN — advisory | wright. |
| Q-6: What track-record evidence threshold justifies promoting `log_only` → `blocking`, given the LOCKED doc's recorded rejection of unscoped blocking? | Deferred by design | Per-repo owner, later. Correctly out of scope; noted so it is not mistaken for a defined gate. |

---

## 9. Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [ ] Acceptance criteria are testable — **note:** US-1 AC2 and the unowned-PROVISIONAL Edge Case
      are not testable against the check as currently architected (Q-1)
- [ ] Out of scope is acceptable (agent-rig build only; Python-only; no blocking promotion)

### Architecture (02)
- [ ] Reviewed by human
- [ ] Detection rule (§2) accepted, **with** the in-sample-n=2 caveat recorded (R-2)
- [ ] **G-1 resolved** — fragment-vs-whole-file scan surface measured or scoped (Q-2)
- [ ] **G-2 resolved** — one answer on named-owner (Q-1)
- [ ] **G-3 resolved** — §5.1 timing figures deleted or re-derived against a committed artifact
- [ ] G-5 resolved — "task brief" citation removed
- [ ] G-7 resolved — §12 items 7-8 status corrected to Applied
- [ ] Schemas (§6, §7) correct

### UI Spec (03)
- [x] N/A — no UI surface; skip formally recorded in `INTAKE.md` Mode. No action required.

### Roadmap (04)
- [ ] Reviewed by human
- [ ] **G-4 resolved** — Slice 3's unsourced "8/10 words / 11 false positives" deleted or sourced
- [ ] Slice 4 and Slice 9 made mutually consistent (follows from Q-1)
- [ ] Slice 12's self-scan Done-When made non-vacuous (follows from Q-2)
- [ ] Sequence and slice sizing accepted

### Overall
- [ ] Q-1 and Q-2 (blocking) resolved
- [ ] Q-3 resolved; then a full re-sweep for any other number not traceable to `results.md`
- [ ] All risks have mitigations or are explicitly accepted
- [ ] Ready for implementation

---

## 10. Reviewer's Verdict

**The correction worked where it mattered most.** The 2/2 and 0/2 recall claims are real — verified
by tracing `scan_thresholds.py`'s logic, not by reading Architecture's prose about it. The
benchmark is a genuine, re-runnable artifact whose numbers Architecture §2/§4 cite accurately
rather than paraphrasing into drift. The three-context rule, the `PROXIMITY_WINDOW_THRESHOLD = 2`
value, the `range()` removal, the `{0,1,-1,2}` honest-non-resolution, and the reversed self-scan
finding are all internally consistent across Requirements, Architecture, and Roadmap. Objectives 2,
3, 4, and 7 clear cleanly.

**Two things must be fixed before this is implementable, and both are the same species of defect the
sprint exists to correct, one layer down:**

- **G-1** — the evidence was gathered on whole files; the instrument consumes edit fragments. The
  recall number is real for the population it was measured on and has not been shown to hold for the
  population the hook actually sees. This is the source-axis blind spot, restated.
- **G-2** — the check as specified would certify an unowned `PROVISIONAL` marker, which is exactly
  what the spec-of-record and Danny's 2026-09-05 ruling forbid. The requirement is stated in one
  document and contradicted in two others, with a fourth (Roadmap Slice 9) demanding a test that
  cannot pass.

**And one sweep was left incomplete:** G-3 and G-4 carry numbers from the audit that this whole pass
exists because it was discredited — including 76ms, which the committed script names by value as
non-reproducible. Neither number changes a decision, which is precisely why they survived. They
should still go.

**Not HALTed.** The documents are not fundamentally inconsistent and the architecture is
implementable; G-1 and G-2 are localized, precisely identified, and each answerable by one
measurement or one decision. Per the review skill's error handling, critical gaps are documented for
human decision rather than halting.
