# Gate Log — first-turn-contract-c3-path-query-boundary-matching

## Spec Gate

### Attempt 1 — 2026-08-27 — Frank

═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — SPEC.md, first-turn-contract-c3-path-query-boundary-matching (spec-gate, attempt 1)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise PASS — no new constants; `/` and `\w` reuse verified against
  real source (`_WORD_TOKEN_RE = re.compile(r"[A-Za-z_]\w*")` is at line 292 exactly
  as claimed; `os.path.basename` usage confirmed). Input PASS — I read the merged
  `scripts/first_turn_contract_probe.py` myself, not the spec's description of it;
  line refs 392 (`def _subject_matches_target`), 419 (the bidirectional `in` check),
  398 (pr branch), 304 (`_extract_claim_subjects`) all verified accurate. Evidence
  independence PASS — my verification is against primary source and test files, not
  the spec's self-claims.
- Current-behavior description: accurate. The shared path/command/query substring
  branch and the path basename fallback exist exactly as described.
- §2 walkthroughs: both re-derived by hand and correct. AC6 case: `["scripts","foo.py"]`
  is a component-suffix of the 6-element absolute split → True. Gap case: `["c3.py"]`
  vs `["scripts","legacy_c3.pyx"]` fails both suffix and prefix → correctly rejected,
  where old rule's `"c3.py" in "scripts/legacy_c3.pyx"` was True.
- §3 walkthroughs: both correct. `(?<!\w)c3(?!\w)` fails against `c3matching-helper`
  (adjacent `m` is `\w`); `claim matching` with space-adjacent edges matches. The claim
  that internal spaces survive because lookarounds only guard the outer edges is
  correct regex semantics.
- §4 command decision: genuinely reasoned, not asserted — two distinct arguments
  (no legitimate-truncation requirement, materially smaller collision surface), no
  invented threshold or cutoff, and an explicit trigger for revisiting (observed
  incident → its own sprint). This is a decision, not a deferral dressed as one.
- §5 behavior table: all 9 rows re-derived; old/new results correct, including row 4
  (component check fails, basename fallback catches it) and row 9 (`"pr list"` is a
  substring of `"unrelated pr list-view thing"` — match preserved by design).
- AC1–AC8: each testable as a direct `_subject_matches_target` assertion or an
  existing-test regression check; no redundancy (AC7/AC8 cover distinct branches:
  suffix alignment vs basename fallback). AC3's named test
  `test_c3_matching_ac6_absolute_vs_relative_path_basename_match_allows` exists at
  tests/test_first_turn_contract_probe.py:577. AC6's pr/identifier tests exist
  (ac4, ac4a x2, ac7).
- Inherited factual claims verified: intake's "26 tests" — actual count 26. Intake's
  "290+ real entries" — actual 340 lines in the track-record jsonl. No fabricated
  numbers found in either doc.
- Minor, non-blocking: (a) `if not shorter: return False` in `_path_components_align`
  is dead code — `str.split("/")` never returns an empty list; (b) INTAKE.md line 41
  says "second sprint in the family" while this is the third (claim-matching was
  itself second) — cosmetic provenance slip, doesn't mislead about anything
  load-bearing; (c) prefix alignment will rarely fire against absolute targets
  (leading `""` component), but the suffix check and basename fallback cover the
  legitimate cases, so this is a benign false-negative direction, not a collision.
- Layer 1: PASS — SPEC.md is internally sound, lock-ready, and faithful to INTAKE.md's
  problem statement; all three intake open questions are explicitly resolved (§2, §4, §9).
- Layer 2: PASS — docs/NORTHSTAR.md exists, Established 2026-07-17 (not DRAFT), and
  hardening the first-turn-contract probe's matching correctness is squarely in the
  workshop's stated lane of refining orchestration tooling other repos rely on. No
  PROVISIONAL tag needed.

Why:
The spec's central risk was the same one that bit this family before — a plausible
description of current behavior or a walkthrough that doesn't survive contact with the
real source. I re-derived every line reference, every walkthrough, and every behavior-
table row against the merged file and the real test suite rather than trusting the
spec's account, and they all hold. The design itself is conservative in the right
direction: component-list alignment cannot land mid-component by construction, the
lookaround rule tightens only the outer edges so partial phrases survive, and the one
place the spec declines to act (`command`) is justified by absence of both a
demonstrated mechanism and a truncation requirement — the correct bar, given this
sprint itself exists because a mechanism was demonstrated elsewhere. The minor items
are cosmetic and none change behavior or mislead a reader.

Verdict: PASS

Fix/Next-step: none required — no carried conditions. (The three minor items above are
noted for the forge author's awareness; none is a condition of this PASS.)
Route to: @wright (proceed to lock and forge)
═══════════════════════════════════════════════════════════════════
