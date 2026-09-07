# Roadmap: first-turn-contract-c3-signpost-sourcing

## REDESIGN (2026-09-07, supersedes the slices below)

See `02-ARCHITECTURE.md`'s "REDESIGN" section. The Signpost-sourcing slices below were never
executed against the abandoned design (only the extension-allowlist deletion and the new
`_pillar_admits_unverified` check were actually implemented, directly, in
`scripts/first_turn_contract_probe.py` + `reference/`). Actual work done, as a single slice:
add `_PILLAR_ADMITS_UNVERIFIED_RE` + `_pillar_admits_unverified` + a `check_c3_violation`
branch that returns an `("admission", matched_text)` sentinel + a `build_reason` branch wording
it distinctly. Verified: literal issue #27 text triggers it; a real verified-Pillar fixture does
not false-trigger; 2/18 real Signpost sections would trigger it if misapplied there (confirming
Pillar-only scoping matters); all 32 pre-existing tests pass unchanged. Everything below this
note describes the abandoned design; kept for history only.

## Dependency Map

| Unit | Depends On |
|------|------------|
| `_extract_section_text` (new helper) | existing inline Pillar-slicing logic in `run()` |
| `_BARE_SHA_RE`/`_looks_like_sha`, `_DECISION_ID_RE` (new patterns) | none — additive to `_extract_claim_subjects` |
| `_extract_claim_subjects` (modified — additive `"sha"`/`"decision_id"` types) | new patterns above |
| `run()` call-site update (compute `signpost_section_text`, pass 5th arg) | `_extract_section_text` |
| `check_c3_violation` signature + union-of-subjects logic | `_extract_section_text` (indirectly, via `run()` supplying `signpost_section_text`), `_extract_claim_subjects` (modified, reused) |
| `reference/first_turn_contract_probe.py` mirror updates | every `scripts/first_turn_contract_probe.py` edit, same commit |
| Existing suite regression check (`c3-claim-matching`, `c3-path-query-boundary-matching`) | `check_c3_violation` change, `run()` call-site update, mirror kept in sync |
| Story 4 regression test (issue #27 repro) | `check_c3_violation` change, `run()` call-site update |
| Dedup test (G4) | `check_c3_violation` union/dedup logic |
| Frank Cold gate (spec + forge) | all code + test slices complete |

No circular dependencies — this is a linear chain: helper+patterns → mirror → call-site → core
logic → tests (incl. dedup + regression) → gate.

## Slice Overview

| Slice | Goal | Depends On | Files |
|-------|------|------------|-------|
| 1 | Extract `_extract_section_text` helper from existing inline Pillar-slicing logic, with `run()` still calling it only for Pillar (no behavior change); mirror into `reference/` | — | `scripts/first_turn_contract_probe.py`, `reference/first_turn_contract_probe.py` |
| 2 | Add `_BARE_SHA_RE`/`_looks_like_sha`/`_DECISION_ID_RE` patterns; extend `_extract_claim_subjects` with `"sha"`/`"decision_id"` types; add `signpost_section_text` parameter to `check_c3_violation`; compute union-of-subjects (Pillar ∪ Signpost, deduped); update `run()` call site to pass both section texts; mirror into `reference/` | Slice 1 | `scripts/first_turn_contract_probe.py`, `reference/first_turn_contract_probe.py` |
| 3 | Regression proof: issue #27 reproduction test (Story 4) — named, standalone, not folded into general tests, with concrete fail-then-pass procedure | Slice 2 | `tests/test_first_turn_contract_probe.py`, `PROGRESS.md` |
| 4 | Confirm existing suites (`first-turn-contract-c3-claim-matching`, `first-turn-contract-c3-path-query-boundary-matching`) and new Story 1/2/3 acceptance-criteria coverage pass unchanged/added; add dedup test (G4); verify `reference/` mirror byte-identity | Slice 2, 3 | `tests/test_first_turn_contract_probe.py` |
| 5 | Frank Cold gate (forge) — isolated detached checkout, unbriefed dispatch, per `docs/ISSUE-RUNBOOK.md` enforcement-mechanism-defect procedure | Slice 1–4 | — (review only, no source files) |

## Slice Detail

### Slice 1: Extract `_extract_section_text` helper

**Goal:** Pull the existing inline Pillar-section-slicing loop in `run()` out into a standalone
`_extract_section_text(text, section_idx)` function, with `run()` updated to call it for Pillar
only. Zero behavior change — pure refactor, verifiable by existing suites still passing untouched.
Mirror the identical edit into `reference/first_turn_contract_probe.py` in the same commit.

**Depends On:** —

**Files:**
- `scripts/first_turn_contract_probe.py` — modify (extract function, update `run()`'s Pillar call site)
- `reference/first_turn_contract_probe.py` — modify identically, same commit (G1)

**Implementation Notes:**
- Signature per 02-ARCHITECTURE.md: `_extract_section_text(text: str, section_idx: int | None) -> str | None`.
- Must return `None` when `section_idx is None` — no exception path.
- Do not touch `_extract_claim_subjects`, `_extract_tool_target`, `_subject_matches_target`, `_collect_qualifying_tool_calls`, C1/C2 logic, or the hook wrapper.

**Tests:**
- [ ] Both existing suites (`first-turn-contract-c3-claim-matching`, `first-turn-contract-c3-path-query-boundary-matching`) pass unchanged — this slice must not alter observable behavior.
- [ ] Direct unit assertion: `_extract_section_text(text, None) is None` (closes G17 — this path is untouched by the existing suites and is load-bearing for `run()`'s `signpost_idx is None` handling).
- [ ] `test_reference_copy_matches_executed_copy` passes (mirror byte-identical).

**Done When:**
- [ ] `_extract_section_text` exists and is used for Pillar slicing in `run()`.
- [ ] No inline Pillar-slicing loop remains duplicated elsewhere.
- [ ] `reference/first_turn_contract_probe.py` is updated identically, in the same commit.
- [ ] Both existing C3 suites pass with zero modification to their fixtures/assertions.

---

### Slice 2: New extraction patterns + Signpost-sourced subject union in `check_c3_violation`

**Goal:** Add two new, narrowly-scoped extraction patterns — `_BARE_SHA_RE`/`_looks_like_sha`
(digit-leading bare hex SHAs) and `_DECISION_ID_RE` (hyphenated decision/issue IDs) — to
`_extract_claim_subjects`, emitting new `"sha"` and `"decision_id"` subject types alongside the
existing four. Branch names and `#`-style PR references need **no new pattern** — verified in
02-ARCHITECTURE.md as already covered by `_FILE_PATH_RE` and `_PR_NUMBER_RE` respectively. Then add
the `signpost_section_text` 5th positional parameter to `check_c3_violation`; compute the deduped
union of `_extract_claim_subjects(pillar_section_text)` and
`_extract_claim_subjects(signpost_section_text)`; check that union against qualifying tool-call
targets. Preserve the presence-only fallback when the union is empty. Update `run()` to compute
`signpost_section_text` via `_extract_section_text(last_assistant_message, signpost_idx)` and pass
it as the new argument. Mirror every edit into `reference/first_turn_contract_probe.py` in the same
commit.

**Depends On:** Slice 1

**Files:**
- `scripts/first_turn_contract_probe.py` — modify (`_BARE_SHA_RE`/`_looks_like_sha`, `_DECISION_ID_RE`, `_extract_claim_subjects` body, `check_c3_violation` signature + body, `run()` call site)
- `reference/first_turn_contract_probe.py` — modify identically, same commit (G1)

**Implementation Notes:**
- New patterns scan raw section text directly (not only inside backtick spans), per Architecture's rationale — Signpost prose is free-flowing, not backtick-constrained.
- `_looks_like_sha` requires the fullmatch on `_BARE_SHA_RE` (7-40 hex chars, cited: SHA-1 digest length and git's `core.abbrev` documented *minimum* short-SHA length — see 02-ARCHITECTURE.md, G16) *and* at least one digit *and* not an all-digit run, to exclude both plain alphabetic hex-look-alike words at or above the length bound (e.g. "deadbeef" — see G14 on why a shorter word like "cafe"/"deed" does not actually exercise this guard) and numeric dates/counts (e.g. "20260907", "1234567") — closes G11.
- `_DECISION_ID_RE` has no length bounds on its prefix or digit run (bounds deleted per G10 — unsourced, unnecessary). It is distinct from `_PR_NUMBER_RE`'s `PR #12`/`#12` shapes (already covered, and this repo's only attested way of referencing issues/PRs) — it targets hyphenated tokens like `DDR-006`. `_looks_like_decision_id` gates extraction on an **allowlist**, `_DECISION_ID_PREFIX_ALLOWLIST = {"DDR"}`, sourced from this repo's actual DDR file-naming convention (`docs/specs/agent-rig-ddrs/DDR-NNN-slug.md`) rather than a denylist of excluded prose — this closes G11, G11-R, and G13 together: an allowlist over a finite, self-attested set structurally cannot false-positive on arbitrary prose (`SHA-1`, `Rule-1`, `Story-4`, `AC-1`, `Python-3`, `UTF-8`, `COVID-19`, `Slice-2`, `Layer-1` are all excluded because their prefix isn't `DDR`, not because each was individually anticipated).
- Do **not** add a redundant branch-name-specific pattern — `_FILE_PATH_RE`'s existing slash-branch coverage already reaches this shape (verified directly against the compiled regex in 02-ARCHITECTURE.md).
- `_subject_matches_target` requires no change — new types fall through to its existing generic fallback (substring containment).
- Dedup key is `(subject_type, value)` — identical to `_extract_claim_subjects`'s own existing key. Do not invent a new subject_type or dedup key beyond `"sha"`/`"decision_id"` (per Architecture's Anti-Patterns).
- New parameter goes last (5th positional) per Architecture's API contract — do not insert between existing params.
- `signpost_section_text` may be `None`/empty — treated as zero subjects via `_extract_claim_subjects`'s existing empty-input guard; no special-casing needed in `check_c3_violation` or `run()`.
- `pillar_idx is None` precondition (C3 does not run at all) must remain untouched.

**Tests:**
- [ ] Unit/fixture test: bare digit-leading SHA in Signpost text is extracted as `subject_type="sha"`.
- [ ] Unit/fixture test: hyphenated decision ID (`DDR-006`, this repo's actual attested prefix) in Signpost text is extracted as `subject_type="decision_id"`.
- [ ] Negative test (closes G14 — corrects a prior test of this name that was non-discriminating): an alphabetic hex-look-alike word of **at least 7 characters** (`"deadbeef"`) in Signpost text is NOT extracted as `subject_type="sha"`. This targets the `any(c.isdigit())` guard specifically — a shorter word (`"cafe"`, `"deed"`, both ≤4 chars) fails `_BARE_SHA_RE`'s `{7,` length bound before that guard is ever reached, so it does not test the digit guard at all; do not substitute a short word here.
- [ ] Negative test (closes G11): a purely numeric run (`"20260907"` date-shaped, `"1234567"` count-shaped) in Signpost text is NOT extracted as `subject_type="sha"`. This targets the `not token.isdigit()` guard.
- [ ] Negative test (closes G11-R/G13 — replaces the prior denylist-only negative test): a prose `Word-N` token whose prefix is **not** in `_DECISION_ID_PREFIX_ALLOWLIST` — cover both a previously-denylisted example (`"UTF-8"`) and, more importantly, a token the old denylist would have missed (`"SHA-1"`, `"Rule-1"`) — is NOT extracted as `subject_type="decision_id"`. This targets the allowlist-membership guard itself, not any specific excluded word, so it remains valid even if more real prefixes are added later.
- [ ] Unit/fixture test: empty Pillar + nonempty Signpost subject + no qualifying tool call → C3 fires (Story 1 / AC1).
- [ ] Unit/fixture test: empty Pillar + empty Signpost (both zero extractable subjects) → C3 does not fire on subject-matching grounds (Story 1 / AC3, presence-only fallback preserved).
- [ ] Unit/fixture test: Signpost asserts 2+ subjects, only one matched by a qualifying tool call → C3 fires citing the unmatched subject(s) (Story 2 / AC1).
- [ ] Unit/fixture test: Signpost asserts 2+ subjects, all matched → C3 does not fire (Story 2 / AC2).
- [ ] Unit/fixture test: Pillar names a subject not in Signpost, matched by a qualifying tool call → C3 does not fire for it (Story 3 / AC1, existing Pillar-sourced behavior preserved).
- [ ] Dedup test (closes G4): Pillar and Signpost both name the identical subject (same `(subject_type, value)`, e.g. the same file path quoted in both sections), with exactly one qualifying tool call matching it. Asserts `check_c3_violation` treats it as satisfied by that single match — no violation raised for that subject, and it is not double-counted or double-required.
- [ ] `test_reference_copy_matches_executed_copy` passes (mirror byte-identical).

**Done When:**
- [ ] `_BARE_SHA_RE`/`_looks_like_sha` and `_DECISION_ID_RE` exist and are wired into `_extract_claim_subjects` as additive `"sha"`/`"decision_id"` subject types.
- [ ] `check_c3_violation` accepts and uses `signpost_section_text` as specified.
- [ ] `run()` computes and passes `signpost_section_text` at the call site.
- [ ] `reference/first_turn_contract_probe.py` is updated identically, in the same commit.
- [ ] All fixture tests above (including the dedup test) pass.
- [ ] `pillar_idx is None` guard clause is byte-for-byte unchanged.

---

### Slice 3: Issue #27 regression proof (Story 4) — named, standalone

**Goal:** Add a single, explicitly named regression test that reproduces the exact issue #27
evasion verbatim: a fixture transcript whose last assistant message contains a Pillar section with
the literal text `"Pillar: none yet — nothing independently checked this session"` (yielding zero
Pillar subjects) plus a Signpost section carrying at least one real extractable subject, plus one
qualifying tool call earlier in the turn that targets something unrelated to that Signpost subject.
Assert `check_c3_violation` (via `run()`'s block decision) returns a violation. This is its own
slice per `docs/ISSUE-RUNBOOK.md`'s requirement that this proof artifact not be folded into a
general test-addition slice.

**Depends On:** Slice 2

**Files:**
- `tests/test_first_turn_contract_probe.py` — modify (add one new, clearly named test: `test_c3_signpost_sourcing_catches_issue_27_evasion`)
- `PROGRESS.md` — record the fail-then-pass verification outputs (see Done When)

**Implementation Notes:**
- Pillar text must be the literal string from the issue, not a paraphrase.
- The qualifying tool call must be real (matches `_collect_qualifying_tool_calls`'s existing criteria) but must target something unrelated to the Signpost's real subject — this is what previously caused the false PASS under presence-only fallback.
- Fail-then-pass verification is an auditable two-checkout procedure (closes G5-R and G15), not a temporary revert. The new test does not exist at the parent SHA (it's authored in this same slice), so running pytest directly against a parent-SHA worktree collects zero tests — that is a collection error, not evidence the defect existed. **Independently re-verified (G15):** copying only the new test function orphans the module-level helpers it needs (`_load_probe`, `_queue_marker_record`, `_assistant_text_record`, `_tool_use_record_with_input`, `_tool_result_record`, `_write_transcript`, `_run_probe`, `_decision`, `_signpost_then_pillar`, plus its `importlib`/`io`/`json`/`os`/`sys`/`redirect_stdout` imports) and produces a `NameError`/`ImportError`; calling `check_c3_violation` directly instead of through `run()` raises `TypeError` against the pre-fix 4-param signature. Neither is the assertion failure the proof requires. Corrected mechanic:
  1. `git worktree add` a detached checkout of the parent commit SHA — the commit immediately before this sprint's `check_c3_violation`/`run()` changes land.
  2. Copy the **entire** `tests/test_first_turn_contract_probe.py` file (not just the one new function) into that parent-SHA worktree, so every module-level helper/import it needs resolves — do not hand-pick a subset.
  3. Run only the new test from inside the parent-SHA worktree, importing `scripts/first_turn_contract_probe.py` from that worktree's own copy (the pre-fix code), and driving it through `run()`'s stdin-in/stdout-out contract (the same route every other test in this file already uses) — never by calling `check_c3_violation` directly with a fixed positional-argument count.
  4. **Guard before treating the output as evidence:** if anything other than an `AssertionError` from the new test itself is raised (`NameError`, `ImportError`, `TypeError`, or a collection error), the setup is wrong — fix it and re-run before drawing any conclusion. **Expected, valid result: an ASSERTION FAILURE** (the presence-only fallback wrongly reports no violation). Record the failing assertion output verbatim.
  5. Run the real, committed test (in its real location, `tests/test_first_turn_contract_probe.py`) against the fixed commit in the normal working tree; record the passing output verbatim.
  6. Record both outputs in `PROGRESS.md` for this slice, noting explicitly that step 4's output was an assertion failure and not a collection/import/type error.

**Tests:**
- [ ] New test exists, named distinctly (not merged into an existing parametrized case).
- [ ] Copied test produces an ASSERTION FAILURE (not a collection/import error) when run against the parent-SHA detached worktree checkout, output recorded verbatim in `PROGRESS.md`.
- [ ] Real (committed) test passes against the fixed commit in the working tree, output recorded verbatim in `PROGRESS.md`.

**Done When:**
- [ ] Test reproduces the issue #27 scenario verbatim (exact Pillar string, unrelated qualifying tool call, real Signpost subject).
- [ ] Fail-then-pass verification followed the exact procedure above (`git worktree add` of the parent SHA, test copied into that worktree with import pointed at its own pre-fix probe copy, verbatim ASSERTION FAILURE output; verbatim passing output from the real committed test on the fixed commit) and both outputs are recorded in `PROGRESS.md`, with the assertion-failure-vs-collection-error distinction noted explicitly.
- [ ] Test is committed as a permanent, standalone regression test (not removed after verification).

---

### Slice 4: Full regression confirmation across both existing suites

**Goal:** Run both pre-existing C3 suites (`first-turn-contract-c3-claim-matching`,
`first-turn-contract-c3-path-query-boundary-matching`) in full against the post-Slice-2/3 code and
confirm zero modifications were needed to their fixtures or assertions. Confirm every Story 1–3
acceptance criterion in 01-REQUIREMENTS.md is covered by an existing or newly-added test (cross-
reference against Slice 2's fixture tests, including the dedup test — this slice is verification,
not new test authorship beyond closing any gap found). Confirm `reference/first_turn_contract_probe.py`
remains byte-identical to `scripts/first_turn_contract_probe.py` across all of this sprint's edits.

**Depends On:** Slice 2, Slice 3

**Files:**
- `tests/test_first_turn_contract_probe.py` — verify only; modify only if a genuine AC gap is found (should not be needed if Slice 2 was done per spec)

**Implementation Notes:**
- This slice exists to catch the case where Slice 2's fixture tests satisfy the *behavior* but an AC in 01-REQUIREMENTS.md wasn't explicitly checked — walk the AC list line by line against actual test names/assertions, not from memory.
- Edge case row "Pillar empty/evasive, Signpost has zero extractable subjects" (no fire) must have an explicit test, distinct from the issue #27 repro (which has a nonempty Signpost).
- Out of scope per 01-REQUIREMENTS.md's Out-of-Scope section (no propagation of these changes to any other repo) — verification here is scoped to this repo only.

**Tests:**
- [ ] Both existing suites run and pass with zero fixture/assertion changes.
- [ ] Every Story 1, 2, 3 acceptance criterion in 01-REQUIREMENTS.md is traceable to a specific passing test.
- [ ] `test_reference_copy_matches_executed_copy` passes.

**Done When:**
- [ ] Full test run (existing suites + new Slice 2/3 tests, including the dedup test) is green.
- [ ] AC-to-test traceability is written down (e.g. in PROGRESS.md) for the forge-gate reviewer.
- [ ] `reference/first_turn_contract_probe.py` confirmed byte-identical to `scripts/first_turn_contract_probe.py`.

---

### Slice 5: Frank Cold gate (forge)

**Goal:** Dispatch Frank's binding forge-gate Cold — unbriefed dispatch (repo + SHA + parent SHA +
verdict-required only, no file list/scope narration), isolated detached checkout of the exact SHA —
per `docs/ISSUE-RUNBOOK.md`'s classification of this sprint as an enforcement-mechanism defect and
this repo's CLAUDE.md binding-gate policy.

**Depends On:** Slice 1, 2, 3, 4 (all code and tests complete and committed)

**Files:** None (review-only; no source files touched by this slice itself)

**Implementation Notes:**
- Verify both Cold-Gate halves before dispatch: no file list/scope hint in the prompt, and dispatch points at an isolated detached worktree of the exact SHA — never the live repo root, even if clean.
- Verdict is binding — PASS/FAIL/HALT, no conditional pass, no manual override.

**Tests:** N/A (gate dispatch, not code)

**Done When:**
- [ ] Cold-gate compliance checklist (unbriefed + isolated checkout) confirmed before dispatch.
- [ ] Frank's verdict recorded (PASS/FAIL/HALT) in PROGRESS.md or GATE-LOG.md.
- [ ] If FAIL/HALT, loop back to the relevant slice — do not proceed to PR.

## Sequence Rules

1. Complete each slice fully (including its Done-When checklist) before starting the next.
2. No partial slice work — Slice 3 (the named regression proof) must not be merged into or
   shortcut by Slice 4's verification pass.
3. Every slice that edits `scripts/first_turn_contract_probe.py` must apply the identical edit to
   `reference/first_turn_contract_probe.py` in the same commit — no slice is done otherwise (G1).
4. If blocked at any slice → HALT, do not skip ahead to a later slice.
5. Each slice's tests must pass before proceeding to the next slice.
6. No new slices without human approval.
7. Slice 5 (Frank Cold gate) is binding — its verdict is not overridable, and a FAIL/HALT sends
   the loop back to the failing slice, not to a workaround.

## Deferred (Not This Roadmap)

- Propagation of these changes to any other repo (01-REQUIREMENTS.md's Out-of-Scope section, not a numbered gap) — explicitly out of scope.
- Fuzzy/similarity-based subject matching — explicitly out of scope per 01-REQUIREMENTS.md and the
  parent C3 sprint's own non-goals.
- Any further extraction pattern beyond `_BARE_SHA_RE`/`_looks_like_sha` and `_DECISION_ID_RE` —
  branch names and `#`-style PR refs are already covered by existing patterns (verified in
  02-ARCHITECTURE.md); a future sourced example these two new patterns still miss is its own
  follow-up, per 01-REQUIREMENTS.md's edge-case table allowance.
- Changes to C1 (Signpost-before-Pillar ordering) or C2 (forbidden third section) logic.
- Resolution of the pre-existing `_FILE_EXTENSION_ALLOWLIST` PROVISIONAL/self-owned status — out of
  scope per INTAKE, recorded but not resolved by this sprint.
- Any new hook or script file, or changes to first-turn-only scope of the contract probe.
