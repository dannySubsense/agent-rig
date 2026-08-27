# Gate Log — first-turn-contract-c3-claim-matching

## Spec Gate

### Attempt 1 — 2026-08-27 — FAIL

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-c3-claim-matching SPEC.md (spec-gate, attempt 1/3)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [FAIL — the "12 C3 tests / 4 non-C3" count in both INTAKE and SPEC
  is false; actual file has 16 tests of which 3 are C3-specific]. Input [pass — I opened
  scripts/first_turn_contract_probe.py and tests/test_first_turn_contract_probe.py raw;
  SPEC §2's description of current check_c3_violation behavior is accurate, and §6's
  single-call-site claim is true (run(), line 383)]. Evidence independence [pass — I read
  the primary source and tests directly, not the spec's paraphrase].
- F1 (blocking): INTAKE ("12 C3-specific tests ... 16 tests total") and SPEC §5 ("existing
  16 tests (4 non-C3 + 12 C3)") assert a test inventory that does not exist. Actual:
  16 tests total, 3 C3-specific (test_ac3_pillar_with_zero_tool_calls_blocks_naming_c3,
  test_ac3_todowrite_only_transcript_still_violates_c3,
  test_ac3_qualifying_non_todowrite_tool_call_avoids_c3). The "4 non-C3" split is likewise
  fabricated. This is exactly the promoted-default shape: an unverified number cited as
  fact and then load-bearing in AC 7's regression contract.
- F2 (blocking): SPEC §3.2 says missing tool_use.input is "handled per §3.4" — but §3.4
  covers zero extracted claim subjects, not absent input on a qualifying call. The
  absent-input case (present in the existing test fixtures, whose tool_use blocks carry
  no input key at all) is unspecified. A qualifying call with no input must be defined:
  does it count as a non-matching target, or fall through somewhere? Right now the spec
  dangles.
- F3 (blocking-lite): §3.1's file-extension allowlist (.py, .md, .ts, .tsx, .json, .sh,
  .yml, .yaml) is a predetermined constant with no citation, no PROVISIONAL tag, no named
  owner. Not a numeric threshold — the spec's "no fabricated numbers" claim is technically
  true — but it is a cap on what counts as a file-path subject, and a claim about
  `pyproject.toml` or `Dockerfile` silently degrades to the presence-only fallback. Per
  repo rule it needs a PROVISIONAL tag with owner, or a stated rationale.
- Otherwise sound: the matching contract (§3.3, exact substring/basename, no thresholds)
  is honest and conservative; §3.4's explicit fallback is the right call; the behavior
  table (§4) is complete; open questions are genuinely deferred, not smuggled decisions.
- Layer 1: FAIL (F1–F3). Layer 2: PASS — hardening a shared cross-repo mechanism before
  retrofit is squarely the Northstar's workshop mandate (docs/NORTHSTAR.md, Established
  2026-07-17, not DRAFT — no PROVISIONAL stamp needed). Drift check clean.

Why:
F1: AC 7 and §5's regression contract are written against a test population that doesn't
exist. Anyone forging against this spec will "verify all 12 C3 tests pass" and report
success on a phantom inventory — the same certified-garbage mechanism this repo's global
rules exist to kill. The number was asserted in INTAKE, inherited by SPEC, and would have
been inherited by PROGRESS — a shared well, one attempt from being stamped.
F2: The one data-shape question the forge will hit on day one (tool_use with no input)
is pointed at a section that doesn't answer it. Matching semantics were explicitly the
reason this got a spec instead of being improvised during forge (INTAKE constraint 3);
leaving this case dangling defeats that purpose.
F3: An allowlist is a cutoff. Cutoffs get a source, a tag, or deletion — no fourth option.

Verdict: FAIL

Fix/Next-step:
1. INTAKE.md (Context §, line ~38) and SPEC.md §5: replace the 12-C3/4-non-C3 inventory
   with the verified one (16 tests, 3 C3-specific), and restate AC 7 against the real
   population. Sweep both docs for any other asserted counts while at it.
2. SPEC.md §3.2/§3.4: specify absent/malformed tool_use.input explicitly — recommend:
   treat as a qualifying call with an empty target (never matches a subject), which keeps
   the presence-only fallback's semantics intact for zero-subject sections. State it in
   its own numbered rule, not a cross-reference.
3. SPEC.md §3.1: tag the extension allowlist PROVISIONAL with a named owner (Danny or
   wright) or add a one-line rationale for the chosen set; note the degradation path
   (unlisted extension → presence-only fallback) so it's a documented behavior, not a
   silent gap.
Route to: @wright (spec author)
═══════════════════════════════════════════════════════════════════
```

### Attempt 2 — 2026-08-27 — FAIL

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-c3-claim-matching SPEC.md (spec-gate, attempt 2/3)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [FAIL — one instance of the fabricated test inventory survives, see
  F1-residual]. Input [pass — re-verified raw: tests file is 623 lines, 16 tests, exactly
  3 C3-specific (lines 299/316/338); check_c3_violation source (lines 251-291) matches
  SPEC §2; single call site at run() line 383 confirmed; test fixture _tool_use_record
  (line 96-100) constructs tool_use with no input key, confirming SPEC §3.2's claim].
  Evidence independence [pass — verified against primary files, not the fix-pass summary].
- F1-residual (blocking): INTAKE.md Constraints bullet 2 (lines 52-53) still reads "Must
  not regress the 4 existing passing tests ... or the 12 existing C3 tests". The Context
  section (lines 39-40) and SPEC §5/AC 7 were corrected to the verified 16/3-C3/13-non-C3
  inventory, but the Constraints bullet — the binding regression contract in the APPROVED
  gating document — kept the phantom numbers. Attempt-1 Fix step 1 explicitly said "sweep
  both docs for any other asserted counts"; the sweep missed one.
- F2: FIXED. SPEC §3.2 now carries its own numbered rule: absent/None tool_use.input →
  empty-string target, never matches a non-empty subject, still counts toward §3.4's
  presence-only fallback, explicitly distinguished from §3.4's zero-subject case. Verified
  against the fixture shape it cites. Good.
- F3: FIXED. §3.1's extension allowlist is tagged PROVISIONAL with owner (wright), a real
  rationale, and a documented degradation path (unlisted extension → not extracted →
  folds into §3.4). No other uncited cutoffs found on the fresh pass.
- Fresh full-document pass: matching contract (§3.3), behavior table (§4), integration
  boundary (§6), and open questions (§7) are sound; no new findings.
- Layer 1: FAIL (F1-residual only). Layer 2: PASS — docs/NORTHSTAR.md is Established
  2026-07-17, not DRAFT (no PROVISIONAL stamp); hardening the shared C3 mechanism before
  cross-repo retrofit is squarely the workshop mandate; drift check clean.

Why:
F1-residual: this is the exact shared-well shape, one hop later. SPEC's regression
contract is now correct, but INTAKE — the APPROVED document that gates the sprint —
still asserts "12 existing C3 tests" in its Constraints. A forge or reviewer reading the
constraint as written will look for 12 C3 tests that do not exist, or worse, treat the
discrepancy as SPEC drifting from its parent. A partial sweep is how one corrected copy
and one stale copy end up disagreeing in the record, which is worse than two consistent
wrong ones — now the docs contradict each other. Everything else in both documents is
now honest and verifiable; this is a one-line fix, but a binding constraint with a
fabricated number does not pass, full stop.

Verdict: FAIL

Fix/Next-step:
1. INTAKE.md Constraints bullet 2 (lines 52-53): replace "the 4 existing passing tests
   (C1/C2 and the non-C3 cases) or the 12 existing C3 tests" with the verified inventory
   — "the 13 existing non-C3 tests or the 3 existing C3 tests" (16 total). Then grep both
   docs for \b(4|12)\b near "test" to confirm zero remaining instances before resubmit.
Route to: @wright (spec author)
═══════════════════════════════════════════════════════════════════
```

### Attempt 3 — 2026-08-27 — PASS

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-c3-claim-matching SPEC.md (spec-gate, attempt 3/3)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [pass — every asserted count re-verified from scratch against
  tests/test_first_turn_contract_probe.py: 623 lines, 16 tests, exactly 3 C3-specific
  (test_ac3_* at lines 299/316/338), 13 non-C3; INTAKE lines 39-40 and 52-53 and SPEC
  §5/AC 7 now all state 16/3/13 consistently; the sole remaining cutoff (§3.1 extension
  allowlist) carries PROVISIONAL + owner wright + rationale + degradation path]. Input
  [pass — re-opened scripts/first_turn_contract_probe.py raw: C3_EXCLUDED_TOOLS={"TodoWrite"}
  (line 39), check_c3_violation at 251, single call site at run() line 383, all matching
  SPEC §2/§6]. Evidence independence [pass — grepped and read primary files myself; did
  not rely on the fix-pass report or my own prior attempt summaries].
- F1-residual: FIXED. INTAKE Constraints bullet 2 now reads "the 13 existing non-C3
  passing tests ... or the 3 existing C3 tests". Grepped both docs for \b(4|12)\b — every
  remaining hit is a section number (§3.4, §4) or line-wrap artifact, zero test-count
  instances. F2 and F3 remain fixed as verified at attempt 2.
- Fresh full Layer 1 pass on current state: §3 matching contract is internally consistent
  (§3.2's empty-target rule composes correctly with §3.3's "non-empty subject never
  matches empty string" and §3.4's zero-subject fallback); §4 behavior table covers all
  five subject/call/match combinations with no contradiction against §3; §5 ACs map to
  the table rows including the exact gap (row 3 = AC 2); §6's signature change is
  justified against the real single call site; §7 defers rather than smuggles decisions.
  Fidelity to Intake: all three intake open questions are addressed or explicitly carried
  (OQ2 answered in §4; OQ1/OQ3 carried to §7). No new findings.
- Layer 1: PASS. Layer 2: PASS — docs/NORTHSTAR.md is Established 2026-07-17 (not DRAFT,
  no PROVISIONAL stamp); hardening the shared first-turn-contract mechanism before
  cross-repo retrofit is the workshop mandate verbatim; drift check clean (fixes the
  shared mechanism, adds no unrequested generality).
- Loop classification (attempt 3): SHRINKING. Attempt 1: three substantive findings
  (F1 fabricated inventory, F2 unspecified absent-input case, F3 uncited allowlist).
  Attempt 2: one residual instance of F1 only, F2/F3 verified fixed. Attempt 3: zero.
  Same finding family monotonically decreasing, no new issue surfacing per attempt —
  the opposite of thrashing. Snapshot lineage: .gate-snapshots/spec/SPEC-attempt-1.md
  vs current SPEC.md confirms the diffs were the prescribed fixes, not churn.

Why:
The premise that failed attempts 1 and 2 — a fabricated test inventory acting as the
regression contract's population — is now fully purged from both documents, and the
corrected numbers are verified against the raw test file, not the fix-pass's claim of
having corrected them. The two design gaps (absent tool_use.input, uncited extension
allowlist) are resolved with explicit, conservative rules rather than hand-waving. The
spec is honest about what it defers, introduces no numeric thresholds, and its every
checkable claim about the source file checks out against the source file.

Verdict: PASS

Fix/Next-step: none — no carried conditions. Open questions in §7 are documented
deferrals owned by the spec, not conditions on this PASS.
═══════════════════════════════════════════════════════════════════
```

## Amendment Confirmation — 2026-08-27 — FAIL

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-c3-claim-matching SPEC.md (amendment confirmation)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [pass — amendment introduces zero new numeric constants,
  thresholds, or cutoffs; strictly-tightening claim verified line by line]. Input
  [pass — read the full current SPEC.md raw, not the amendment summary]. Evidence
  independence [pass — verified against the document itself, not Danny's or the
  orchestrator's description of it].
- Q1 require-all-subjects: implemented consistently. §3.3's violation rule ("at least
  one extracted claim subject has no matching call") and its "Equivalently: every
  extracted subject must match" restatement agree; §4's "Multiple subjects, partial
  match" row now says Violation; §5 AC5a tests the partial-coverage violation and AC5b
  the full-coverage pass. No half-application.
- Q2 identifier exact-match: correctly carved out. §3.3's new exception cites §3.1's
  Identifier/symbol row only; the whitespace/word-boundary-token rule for free-text
  targets (Bash command, json.dumps catch-all) is sound; file-path substring+basename
  and quoted-query substring rules are textually untouched; command-string subjects
  (§3.1 "Command / gh reference" fallback) correctly remain outside the carve-out.
  AC7 tests the exact collision shape (check_c3 vs check_c3_violation).
- Q3 §7 consistency: clean. Entry 2 records OQ2/Issue #18 as resolved-closed; entry 4
  records #19 narrowed to file-paths/quoted-queries with the identifier portion closed;
  no orphaned require-any or undifferentiated word-boundary language survives anywhere
  in §3, §4, or §5.
- Q4 no new constants: confirmed — the closing "no numeric threshold" claim still holds.
- Q5 fresh-eyes finding — F-A1 (blocking): §5's preamble now reads "All existing 16
  tests ... must continue passing except where a listed AC below explicitly says an
  existing test's *expectation* changes (the 'multiple subjects, partial match' case
  flips from Pass to Violation under require-all-subjects — see AC 5)." No such
  existing test exists. The 3 existing C3 tests are presence-only (verified at
  attempts 1–3); the Pass→Violation flip is of this spec's own former AC5, not of any
  test in the shipped suite. AC8 says the opposite and is correct: "all existing C1/C2
  tests and the 13 non-C3 tests pass unmodified." The preamble's carve-out and AC8
  directly contradict each other.

Why:
F-A1 is the exact failure family that burned attempts 1 and 2: an assertion about the
existing test population that the test population does not support, sitting inside the
binding regression contract. A forge reading the preamble as written will hunt for an
existing partial-match test to flip — it doesn't exist — or, worse, treat AC8's
"unmodified" as the drifted claim. Two contradictory statements in one AC section is
worse than one wrong one. Everything else in the amendment is genuinely
strictly-tightening, internally consistent, and honest; this is a one-line fix, but a
regression contract that contradicts itself does not pass.

Verdict: FAIL

Fix/Next-step:
1. SPEC.md §5 preamble: delete the "except where a listed AC below explicitly says an
   existing test's expectation changes..." carve-out. Replace with: all 16 existing
   tests must continue passing unmodified (consistent with AC8); the require-all flip
   changes only this spec's own AC5 relative to its pre-amendment draft, not any
   shipped test. Resubmit for confirmation.
Route to: @wright (spec author)
═══════════════════════════════════════════════════════════════════
```

## Amendment Confirmation (re-check) — 2026-08-27 — PASS

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-c3-claim-matching SPEC.md (amendment confirmation, re-check of F-A1)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [pass — the fix asserts a test-population fact (16 tests, none
  multi-subject) already verified from the raw test file at attempts 1-3; no new numbers
  introduced]. Input [pass — read the full current SPEC.md raw, not the fix summary].
  Evidence independence [pass — verified against the document itself].
- F-A1: FIXED. §5's preamble now states all 16 existing tests (13 non-C3 + 3 C3) must
  continue passing unmodified, correctly notes none exercise multi-subject Pillar claims,
  and explicitly attributes the Pass→Violation flip to this spec's own earlier draft AC5
  text, not any shipped test. This is exactly the prescribed fix and it now agrees with
  AC8 ("pass unmodified") and with §4's behavior table.
- Scoped sweep for residuals: no other passage in the document asserts or implies an
  existing test's expectation changes. §4's "Multiple subjects, partial match" paragraph
  defines new behavior tested by new ACs 5a/5b; the Amendment header (lines 10-15) and
  §7 entries 2/4 are consistent with the corrected preamble. The contradiction is gone,
  and the edit introduced no new claim, constant, or inconsistency.

Why:
The single blocking finding was a self-contradicting regression contract — a preamble
carve-out claiming a phantom existing test flips, against AC8's correct "unmodified."
The replacement text removes the carve-out, states the true population fact, and names
what actually flipped (the spec's own draft text). A forge reading §5 now gets one
consistent instruction: 16 existing tests unmodified, new tests per ACs 1-8. Handling
this as a direct factual correction rather than a re-delegated design change was the
right call — nothing about the design moved.

Verdict: PASS

Fix/Next-step: none — no carried conditions. F-A1 closed; the amendment stands as
confirmed strictly-tightening and internally consistent.
═══════════════════════════════════════════════════════════════════
```
