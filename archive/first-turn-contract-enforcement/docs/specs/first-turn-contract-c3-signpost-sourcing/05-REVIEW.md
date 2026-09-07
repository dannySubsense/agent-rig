# Spec Review: first-turn-contract-c3-signpost-sourcing (iteration 3 — supersedes iteration 2)

**Reviewer**: @spec-reviewer (independent)
**Date**: 2026-09-07
**Docs reviewed**: 01-REQUIREMENTS.md, 02-ARCHITECTURE.md, 03-UI-SPEC.md, 04-ROADMAP.md
**Independently re-verified against**: `scripts/first_turn_contract_probe.py` (lines 255–433,
501–651), `tests/test_first_turn_contract_probe.py` (module-level helpers at lines 44–170, 386;
`test_reference_copy_matches_executed_copy` at line 872)

**Status**: COMPLETE — not HALTED. Two of the three iteration-2 blockers (G10, G12) are **closed
and independently verified**. G11 is **partially closed**. Four items block readiness for Frank's
binding spec-gate: G11-R (residual false-positive class), G14 (a negative test that proves
nothing), G15 (Slice 3 still not executable as written, for a *different* reason than G5-R), and
G13 (a new unsourced non-numeric constant).

---

## Method note

Every claim below was re-derived by tracing candidate strings through the pattern and predicate
definitions as literally written in 02-ARCHITECTURE.md, against the live branch order of
`_extract_claim_subjects` (lines 304–357). The fix pass's own summary of what it fixed was not
accepted as evidence of anything. Helper dependencies for Slice 3 were enumerated by reading the
actual test file, not inferred.

---

## Part A — Verification of iteration-2 blockers

| Gap (iter 2) | Claimed fix | Independent verdict |
|---|---|---|
| **G10** — six unsourced numeric constants (`7`, `40`, `2`, `6`, `1`, `4`) | SHA bounds cited inline; decision-ID bounds deleted | **CLOSED — verified.** 02 line 58 is now `\b[0-9a-fA-F]{7,40}\b` with the citation carried in the comment (lines 51–57) *and* in 02's "Constant sourcing (G10)" prose (lines 43–48) and 04 Slice 2 note (line 86). 02 line 74 is now `\b([A-Za-z]+-\d+)\b` — the `{2,6}`/`{1,4}` bounds are **actually deleted, not relabeled**; grepping the revised docs finds no surviving occurrence of either quantifier. The disposition chosen (delete rather than source) is the correct one under the Unasked Judgment rule and is explicitly reasoned as such. See G16 for one wording imprecision in the `7` citation — non-blocking. |
| **G11** — false-positive class, untested | `not token.isdigit()` guard; `_DECISION_ID_PROSE_EXCLUSIONS` denylist; five negative test items in Slice 2 | **PARTIALLY CLOSED.** The all-digit guard is correct and constant-free (trace below). The decision-ID denylist mechanism works for the four tokens it names but is structurally incomplete (G11-R/G13). One of the two new negative test items is non-discriminating (G14). |
| **G12** — `_looks_like_sha`'s `fullmatch` looked like dead code | 02 adds a "Wiring clarification (G12)" paragraph (lines 104–112) | **CLOSED.** It now states explicitly that `_looks_like_sha` is applied per token from a per-token sweep (so `fullmatch` is the filtering step, not a no-op) while `_looks_like_decision_id` is applied to `finditer` match objects, and warns implementers not to assume one uniform wiring. That is the ambiguity, named. |
| **G5-R** — Slice 3 fail-half produces a collection error | Procedure rewritten as worktree + copy-the-test-function into a standalone file | **NOT CLOSED — see G15.** The *collection-error* failure mode G5-R named is addressed and the "must be an assertion failure" guard is now stated in both 02 (line 331) and 04 (line 142). But the copy instruction as written ("copy **only** the new test function — not the whole file") produces a `NameError`/import error for a different reason the procedure does not anticipate. |

### Independent trace of the new exclusion logic

Traced against the predicate definitions at 02 lines 58–85, using the exact examples iteration 2
named.

| Candidate | Trace | Excluded? | Doc's claim |
|---|---|---|---|
| `20260907` (date-like all-digit) | `_BARE_SHA_RE.fullmatch` ✅ (8 hex chars) → `any(c.isdigit())` ✅ → `not token.isdigit()` → `"20260907".isdigit()` is `True` → predicate returns `False` | **Yes — correctly excluded** | Correct |
| `1234567` (count-shaped) | same path; `.isdigit()` `True` → `False` | **Yes** | Correct |
| `deadbeef` (alphabetic hex word, ≥7) | fullmatch ✅ → `any(isdigit)` `False` → `False` | **Yes** | Correct — this is the case the digit guard actually earns |
| `cafe`, `bad`, `deed` (the words 02 and 04 both name) | fullmatch **fails** — 3–4 chars, below the `{7,` lower bound. The digit predicate is never reached. | Yes, but **by the length bound, not by the mechanism the docs credit** | **02 lines 54–56 and 04 line 86 both misattribute the exclusion.** Consequence in G14. |
| `UTF-8` | `_DECISION_ID_RE` matches; prefix `UTF` → in `_DECISION_ID_PROSE_EXCLUSIONS` → excluded | **Yes** | Correct |
| `COVID-19`, `Slice-2`, `Layer-1` | prefixes `COVID`/`SLICE`/`LAYER` all in set → excluded | **Yes** | Correct |
| `SHA-1` | matches `\b([A-Za-z]+-\d+)\b`; prefix `SHA` **not** in the exclusion set → **extracted as `("decision_id", "SHA-1")`** | **No — false positive survives** | Unclaimed. See G11-R. |
| `Rule-1`, `Story-4`, `AC-1`, `Python-3`, `Figure-2` | same — prefixes absent from the set → extracted | **No** | Unclaimed |

**Verdict:** the SHA half of G11 is genuinely closed for the numeric case; the decision-ID half is
closed only for the four tokens someone happened to think of.

---

## Part B — Blocking items for iteration 3

| Gap | Detail | Impact |
|---|---|---|
| **G11-R (blocking) — the prose-exclusion denylist cannot be completed, and its first miss is a token this doc set itself uses.** | `_DECISION_ID_PROSE_EXCLUSIONS = {"UTF","COVID","ISO","IEEE","SLICE","LAYER"}` is a denylist over an open set (all English/technical `Word-N` prose). Traced above: `SHA-1` — a term written repeatedly in 02-ARCHITECTURE.md's own new comment block, and a plausible Signpost token — is extracted as a decision-ID subject and would demand a matching qualifying tool call. So would `Rule-1`, `Story-4`, `AC-1`, `Python-3`. | Same user-visible failure mode iteration 2 flagged (C3 over-fires → blocking Stop hook rejects a legitimate turn), one layer down. **The load-bearing question was not asked: does a denylist need to exist?** The complement is an *allowlist* of decision prefixes this repo actually uses (`DDR`, `ISSUE`, `PR` — sourced from `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` and this repo's issue naming, i.e. citable rather than invented), which structurally cannot false-positive on arbitrary prose and shrinks the pattern to exactly the cases INTAKE DD4 asked for. Recommend replacing, not extending. |
| **G13 (blocking) — `_DECISION_ID_PROSE_EXCLUSIONS` is itself an unsourced constant.** | It is not numeric, so it escaped the G10 sweep, but it is a predetermined value set in an enforcement path with no citable source. 02 lines 77–80 offer a prose rationale ("named technical standards … this sprint's own internal spec vocabulary") — and the governing rule states plainly that a comment asserting a rationale is not a source. `ISO` and `IEEE` in particular have no stated provenance at all: no example of either appearing in a Signpost is given. | Exactly the shape the fix pass just cleared from `_BARE_SHA_RE`/`_DECISION_ID_RE`, reintroduced in the fix for those same patterns. Resolving G11-R by switching to a repo-sourced prefix allowlist also resolves this — one change closes both. Extending the denylist does not. |
| **G14 (blocking) — Slice 2's alphabetic-hex negative test is non-discriminating.** | 04 line 98: *"a purely alphabetic hex-like word (`\"cafe\"`, `\"deed\"`) in Signpost text is NOT extracted as `subject_type=\"sha\"`"*. Both are ≤4 chars and fail `_BARE_SHA_RE`'s `{7,` lower bound before `any(c.isdigit())` is evaluated. The test passes green while exercising none of the logic it is written to protect; deleting the digit guard entirely would leave it green. | A test that cannot fail for the reason it claims is the "green tests measure internal consistency" trap in miniature. Fix is one word: use an alphabetic hex word of ≥7 characters (`deadbeef`, `defaced`, `beadface`). 02 lines 54–56 and 04 line 86 must be corrected in the same pass, since both currently state a false mechanism. |
| **G15 (blocking) — Slice 3's revised procedure still does not execute, for a new reason.** | 04 step 2 (line 141) / 02 step 2 (lines 325–327): *"Copy only the new test function … not the whole `tests/test_first_turn_contract_probe.py` file — into a standalone test file."* Verified against the live test file: any test of this shape depends on module-level helpers `_load_probe` (44), `_queue_marker_record` (64), `_assistant_text_record` (88), `_tool_use_record_with_input` (104), `_tool_result_record` (120), `_write_transcript` (128), `_run_probe` (136), `_decision` (155), `_signpost_then_pillar` (386), plus the `importlib`/`io`/`json`/`os`/`sys`/`redirect_stdout` imports (22–27). Copying the function alone yields `NameError` at run time (or an import error) — **precisely the outcome step 3 warns is invalid evidence, produced by step 2's own instruction.** | The proof artifact for the sprint's headline defect still cannot be produced by following the spec. Fix: step 2 must read "copy the new test function **together with the module-level helpers and imports it references**" (enumerate them, or copy the whole file and deselect — either is fine, name one). **Second, unstated requirement:** the copied test must drive `run()`'s stdin/transcript path, not call `check_c3_violation` directly — the pre-fix signature (line 501) takes 4 parameters, so a direct 5-arg call raises `TypeError`, again an error rather than the required assertion failure. 02's Integration Points already implies the `run()` route ("via `run()`'s block decision", line 309) but the fail-then-pass procedure never states it as a constraint. |

### Non-blocking

| Gap | Detail |
|---|---|
| **G16 (minor)** — the `7` citation is imprecise. `core.abbrev` has defaulted to `auto` (scaling with object count) since git 2.11; `7` is its documented **minimum**, not its default. The number is still genuinely sourced and the bound is still correct — reword 02 line 53 / 04 line 86 from "defaults to a 7-character abbreviated SHA" to "has a documented minimum abbreviation length of 7 characters." |
| **G17 (minor)** — `_extract_section_text(text, None) → None` is a stated Slice 1 Done-When (04 line 48) and load-bearing for the `signpost_idx is None` path (02 lines 240–245, and an explicit Anti-Pattern at 02 lines 270–273), but no Slice 1 test item asserts it. Slice 1's only tests are "existing suites pass," which never reach the helper with `None`. One direct assertion closes it. |
| **G18 (cosmetic, carried)** — 03-UI-SPEC.md is now current (it names both new patterns and the `reference/` mirror), so iteration 2's staleness note is resolved. No action. |
| **G6/G7 residue (carried, unchanged)** — the other-repo propagation follow-up still names no issue number or owner; `_FILE_EXTENSION_ALLOWLIST`'s self-owned PROVISIONAL status is recorded (02 lines 282–289) but undisposed. Both correctly out of scope; both still need Danny. |

### Independent sweep (not derived from the fix pass's own sweep)

- **Numeric constants across all four revised docs:** `7` and `40` (both cited, G16 wording aside)
  are the only predetermined numbers in a data/enforcement path. `{2,6}`/`{1,4}` are gone. No
  others found — includes slice numbers, line-number references, and version strings, none of
  which are enforcement parameters. **G10's sweep holds.**
- **Non-numeric predetermined constants:** one found that the numeric sweep structurally could not
  catch — `_DECISION_ID_PROSE_EXCLUSIONS` (G13). This is the sweep's own blind spot: it was scoped
  to numbers, and the defect landed in a set literal.
- **New extraction/matching logic lacking a negative test:** `_looks_like_sha` — covered, but one
  of two negative tests is non-discriminating (G14). `_looks_like_decision_id` — covered for
  denylisted prefixes only; **no test exists for a non-denylisted prose `Word-N` token**, which is
  exactly where G11-R lives, so the current test set would ship the defect green.
  `_extract_section_text` — no negative test for `None` (G17). `check_c3_violation`'s union/dedup —
  covered (G4 test). `_subject_matches_target` — unchanged, verified: the generic fallback at lines
  430–433 (`subject_value in target_text or target_text in subject_value`) does receive
  `"sha"`/`"decision_id"` since neither is special-cased above it. 02's claim of "no change
  required" is **correct**.

---

## Cross-reference tables

### Requirements → Architecture Coverage

| Requirement | Architecture Coverage | Status |
|---|---|---|
| Story 1 / AC1 (all four named subject types extractable) | `_FILE_PATH_RE` (path + branch), `_PR_NUMBER_RE` (`#n`), `_BARE_SHA_RE`, `_DECISION_ID_RE` | ✅ re-verified by direct trace |
| Story 1 / AC2 (issue #27 repro fires) | Deduped union + Slice 3 fixture | ✅ |
| Story 1 / AC3 (both empty → no fire) | Presence-only fallback preserved on empty union | ✅ |
| Story 2 / AC1–AC2 | Per-subject check; unmatched list to unchanged `build_reason` | ✅ |
| Story 3 / AC1–AC3 | Pillar extraction unchanged; union additive; no direct `check_c3_violation` calls in tests | ✅ re-verified |
| Story 4 / AC1 (named standalone regression test) | Slice 3 | ✅ |
| Story 4 / AC2 (fails pre-fix, passes post-fix) | Slice 3 worktree procedure | ❌ **G15** — still not executable |
| Edge case: same subject both sections counts once | Dedup key `(subject_type, value)`; Slice 2 dedup test | ✅ |
| *(new patterns' own correctness — false positives)* | `_looks_like_sha` ✅ / `_looks_like_decision_id` ⚠️ | ❌ **G11-R, G13** |

### Requirements → UI Coverage

| User Story | Screen/Flow | Status |
|---|---|---|
| Stories 1–4 | None — confirmed absence of UI surface | ✅ N/A, correctly justified and now current |

### Architecture → Roadmap Coverage

| Component | Slice | Status |
|---|---|---|
| `_extract_section_text` | Slice 1 | ⚠️ G17 (None-case untested) |
| `_BARE_SHA_RE`/`_looks_like_sha` | Slice 2 | ⚠️ G14 (weak negative test) |
| `_DECISION_ID_RE`/`_looks_like_decision_id`/`_DECISION_ID_PROSE_EXCLUSIONS` | Slice 2 | ❌ G11-R, G13 |
| `_extract_claim_subjects` new types + wiring (G12 clarification) | Slice 2 | ✅ |
| `check_c3_violation` signature + union/dedup | Slice 2 | ✅ |
| `run()` call site | Slice 2 | ✅ |
| `reference/` mirror | Slices 1, 2, 4 + Sequence Rule 3 | ✅ |
| Issue #27 regression test | Slice 3 | ❌ G15 |
| Dedup test | Slice 2 | ✅ |
| Prior-suite regression confirmation | Slice 4 | ✅ |
| Cold forge gate (both halves named) | Slice 5 | ✅ |
| Cold **spec** gate | orchestrator-level, not a slice | ⚠️ carried — outside the roadmap by design; flagged so it is not lost |

---

## Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `_DECISION_ID_RE` over-fires on prose (`SHA-1`, `Rule-1`, `Story-4`) → C3 blocks a legitimate session | **M–H** | **H** — user-visible, on a blocking Stop hook, shipped green | Close G11-R: replace the denylist with a repo-sourced prefix allowlist (`DDR`/`ISSUE`/`PR`); add a negative test for a *non*-listed `Word-N` token |
| The denylist is extended token-by-token as false positives surface in production | **M** | **M** | Same fix — an allowlist has no such tail |
| G14's green-but-inert negative test is read as proof the SHA exclusion works | **H** if unfixed | **M** | Use a ≥7-char alphabetic hex word; correct the two docs that misstate the mechanism |
| Slice 3's fail-half errors out and the error is rationalized as "close enough" | **H** if run as written | **H** — the regression proof becomes theater | Close G15: copy helpers+imports too; require the test to drive `run()`; require an assertion failure |
| `_FILE_EXTENSION_ALLOWLIST` (self-owned PROVISIONAL) governs a second input source | **M** | **M** | Recorded, not resolved; needs Danny (cite / delete / redesign). Branch-name path bypasses it (line 341), so blast radius is limited to dotted-extension tokens |
| Spec Cold gate run non-cold (live repo root) | **L–M** | **H** | Check both halves at dispatch — note this sprint directory now holds three iterations' worth of findings, exactly the leak isolation exists to prevent |

---

## Assumptions

| Assumption | Impact if Wrong |
|---|---|
| An empty-subject Signpost means nothing checkable (01, from INTAKE DD2) | Core premise changes. "Empty" now means empty to six patterns |
| Bare SHAs / decision IDs appear unbackticked in Signpost prose, justifying a raw-text sweep | If they are reliably backticked, the raw sweep buys nothing and only adds the G11-R false positives. **Still unmeasured** — no Signpost sample count is given anywhere in the doc set |
| `_DECISION_ID_PROSE_EXCLUSIONS`'s six entries are the prose tokens that matter | **Independently falsified** — `SHA-1` alone breaks it (G11-R) |
| No test calls `check_c3_violation` directly → 5th positional param safe | **Re-verified true** (grep returns only a fixture payload string) |
| Existing Pillar slicing is heading-inclusive, stops at next heading | **Re-verified true** (lines 640–648) |
| A copied-out test function is self-contained | **Independently falsified** — nine module-level helpers required (G15) |

---

## Open Questions

| Question | Status | Resolution |
|---|---|---|
| Does a prose *denylist* need to exist at all, or should `_DECISION_ID_RE` use a repo-sourced prefix allowlist? | **Open — blocking** | Ask the judgment question before extending the list. An allowlist (`DDR`, `ISSUE`, `PR`, cited to `00-DDR-INDEX.md`) closes G11-R and G13 together |
| What sources `ISO` and `IEEE` in the exclusion set — has either ever appeared in a Signpost? | **Open — blocking (G13)** | Cite an actual occurrence or delete the entries; moot if the allowlist replaces the mechanism |
| Which alphabetic hex word does the SHA negative test use? | **Open — blocking (G14)** | Must be ≥7 chars, or the test never reaches the digit guard |
| What exactly gets copied into the parent-SHA worktree, and does the test drive `run()` or `check_c3_violation`? | **Open — blocking (G15)** | Enumerate helpers + imports; require the `run()` stdin path |
| Disposition for `_FILE_EXTENSION_ALLOWLIST` | **Open — needs Danny** | Self-named PROVISIONAL owner is not a valid disposition. Out of scope by INTAKE — surfaced, not smuggled |
| Owner and issue number for the other-repo propagation follow-up | Open — low stakes | Named in neither 01 nor 04 |
| Should spec docs carry review-gap IDs (`(G1)`, `closes G11`) inline? | Open — cosmetic | A Cold gate reading only the spec set sees unresolvable cross-references. `01-REQUIREMENTS.md G6` in 04 Slice 4 remains a mis-citation — 01 has no G6 |

---

## Approval Checklist

### Requirements (01)
- [x] Acceptance criteria testable and achievable by the architecture
- [x] Out of Scope explicit on other-repo propagation
- [ ] Reviewed by human

### Architecture (02)
- [x] `reference/` mirror accounted for
- [x] Extraction-pattern disposition re-derived and independently re-verified
- [x] Numeric constants cited or deleted (**G10 closed — verified, bounds actually removed**)
- [x] `_looks_like_sha` wiring stated unambiguously (**G12 closed**)
- [x] All-digit false-positive class excluded, constant-free (**half of G11 closed**)
- [ ] Decision-ID prose false positives structurally addressed (**G11-R blocking**)
- [ ] `_DECISION_ID_PROSE_EXCLUSIONS` sourced or replaced (**G13 blocking**)
- [ ] `cafe`/`deed` exclusion mechanism stated correctly (**G14**)
- [ ] `core.abbrev` citation reworded to "documented minimum" (G16)
- [ ] Reviewed by human

### UI Spec (03)
- [x] No UI surface — confirmed absence, correctly documented and current
- [ ] Reviewed by human

### Roadmap (04)
- [x] `reference/` in Files + Done-When for every code-editing slice
- [x] Dedup edge-case test present
- [x] Negative tests added for the all-digit and denylisted-prose cases
- [ ] Negative test for a *non*-denylisted `Word-N` token (**G11-R blocking**)
- [ ] Alphabetic-hex negative test uses a ≥7-char word (**G14 blocking**)
- [ ] Slice 3 procedure made executable — helpers/imports + `run()` route (**G15 blocking**)
- [ ] `_extract_section_text(text, None)` assertion in Slice 1 (G17)
- [ ] Reviewed by human

### Overall
- [ ] Four blocking items closed (G11-R, G13, G14, G15)
- [x] All risks have stated mitigations
- [ ] Cold spec-gate dispatch verified on **both** halves before Frank runs
- [ ] Ready for implementation

---

## Reviewer's Bottom Line

G10 and G12 are closed properly, and G10 in particular was closed the right way: the decision-ID
bounds were **deleted**, not renamed or PROVISIONAL-tagged, with the judgment question ("does this
number need to exist") asked and answered before reaching for a citation. That is the doctrine
working as intended, and it is verified here against the bytes, not the summary.

The remaining four blockers share one shape, and it is worth naming plainly: the fix pass answered
each iteration-2 finding at the exact granularity it was written, and stopped there. Told to
exclude "a date-like all-digit string, an alphabetic hex word, a `Word-N` prose token," it produced
a mechanism that handles those three literal strings — and a denylist whose first unlisted member,
`SHA-1`, appears in the fix's own comment block; and a negative test using words too short to
reach the guard they are meant to test. Told the fail-then-pass procedure was unexecutable because
the test does not exist at the parent SHA, it fixed that reason and introduced another (nine
module-level helpers the copied function needs).

None of this is careless work — it is a fix pass optimizing against the review's wording rather
than the review's problem. The corrective is the same one the repo's own doctrine gives: for
G11-R/G13, ask whether the denylist should exist before extending it; a `DDR`/`ISSUE`/`PR`
allowlist sourced from this repo's own DDR index cannot false-positive on prose at all, and closes
both gaps with less machinery.

**Not ready for Frank's binding spec-gate.** The four blockers are small — one mechanism swap, two
test corrections, one procedure amendment — but three of them are live false-positive or
false-evidence paths in a hook that blocks sessions, and shipping them green is the specific
outcome this review exists to prevent.
