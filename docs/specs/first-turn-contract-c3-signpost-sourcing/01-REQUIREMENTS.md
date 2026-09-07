# Requirements: first-turn-contract-c3-signpost-sourcing

## Summary
Change `check_c3_violation` in `scripts/first_turn_contract_probe.py` to source claim subjects
from the Signpost section (in addition to the existing Pillar-sourced extraction), so an empty
or evasive Pillar section can no longer silently pass C3 via the presence-only fallback.

## User Stories

**Story 1**
As a session reviewer relying on the first-turn contract probe,
I want C3 to check tool-call evidence against the claims actually asserted in the Signpost,
so that a Pillar section that names nothing (empty, vague, or an honest "not yet verified")
cannot silently pass unverified claims.

**Story 2**
As a session reviewer relying on the first-turn contract probe,
I want a Pillar that verifies only some of the Signpost's claims to still be caught by C3,
so that partial, silently-incomplete verification is flagged rather than passed.

**Story 3**
As a maintainer of the first-turn contract probe,
I want the existing Pillar-sourced subject extraction and both prior C3 test suites to keep
passing unchanged,
so that this fix doesn't regress previously-hardened behavior.

**Story 4**
As a maintainer responding to an enforcement-mechanism defect (issue #27),
I want a regression test that reproduces the exact original evasion
("Pillar: none yet — nothing independently checked this session" plus an unrelated qualifying
tool call),
so that this specific blind spot cannot silently reopen.

## Acceptance Criteria

**Story 1**
- [ ] Given a turn where `pillar_idx is not None` and the Pillar section contains no extractable
      subjects, when the Signpost section contains at least one extractable subject (branch name,
      commit SHA, PR/issue/decision ID, or file path), then C3 fires unless a qualifying tool call
      matching that subject exists earlier in the turn.
- [ ] Given the issue #27 reproduction case (empty/evasive Pillar text, an unrelated qualifying
      tool call present, a Signpost with at least one real subject), then C3 raises a violation
      (previously a false PASS).
- [ ] Given a Pillar section with no extractable subjects and a Signpost section that also has no
      extractable subjects, then C3 does not fire on subject-matching grounds (nothing to check).

**Story 2**
- [ ] Given a Signpost asserting two or more distinct subjects, when a qualifying tool call
      matches only one of them, then C3 fires citing the unmatched Signpost subject(s).
- [ ] Given a Signpost asserting two or more distinct subjects, when qualifying tool calls match
      all of them, then C3 does not fire on subject-matching grounds.

**Story 3**
- [ ] Given a Pillar section that itself names a subject not present in the Signpost, when a
      qualifying tool call matches that Pillar-only subject, then C3 does not fire for it (existing
      Pillar-sourced behavior preserved).
- [ ] All tests in the existing `first-turn-contract-c3-claim-matching` suite pass unchanged after
      this change.
- [ ] All tests in the existing `first-turn-contract-c3-path-query-boundary-matching` suite pass
      unchanged after this change.

**Story 4**
- [ ] A new regression test exists that reproduces the exact issue #27 scenario verbatim (the
      literal "Pillar: none yet — nothing independently checked this session" text plus an
      unrelated qualifying tool call) and asserts C3 raises a violation.
- [ ] The new regression test fails against the pre-fix code path and passes against the post-fix
      code path (demonstrating it actually exercises the fixed gap).

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Pillar section absent entirely (`pillar_idx is None`) | C3 does not run at all — precondition unchanged from current behavior. |
| Pillar empty/evasive, Signpost has zero extractable subjects | C3 does not fire on subject-matching grounds — nothing to check, per Design Decision in INTAKE.md. |
| Pillar empty/evasive, Signpost has one or more extractable subjects, no qualifying tool call anywhere in the turn | C3 fires — this is the core gap being closed. |
| Pillar names a subject the Signpost never raised | That Pillar-only subject is still checked exactly as today (Pillar-sourced extraction is additive, not replaced). |
| Signpost raises subjects using a format not yet covered by extraction patterns (e.g. an unusual ID format) | Out of scope for guaranteed detection in v1; extraction patterns are engineering detail for Architecture, sourced from real Signpost examples in this repo's transcripts — not required to be exhaustive. |
| Signpost and Pillar both name the same subject, one qualifying tool call matches it | Counts as satisfied for both sourcing paths — no double-counting requirement, single match suffices. |
| Multiple qualifying tool calls, only one Signpost subject | Any one matching call satisfies that subject (existing matching semantics, not first-turn-contract-c3-signpost-sourcing's addition). |

## Out of Scope

- NOT: Changes to C1 (Signpost-before-Pillar ordering) logic.
- NOT: Changes to C2 (forbidden third section) logic.
- NOT: New hook or script file — this is a change within the existing `check_c3_violation` and its
  helpers in `scripts/first_turn_contract_probe.py`.
- NOT: Changes to first-turn-only scope of the contract probe.
- NOT: Fuzzy or similarity-based subject matching — v1 remains exact substring/token containment,
  consistent with the parent C3 sprint's own non-goals.
- NOT: Replacing Pillar-sourced subject extraction — Signpost-sourced subjects supplement it.
- Deferred: Exhaustive coverage of every possible Signpost subject format; extraction patterns are
  scoped to what's needed against real examples from this repo's transcripts, not a formal grammar.
- NOT: Propagating this fix to the other repos on `HOOK-DEPLOYMENT-ROSTER.md` also running
  `first_turn_contract_probe.py` — scope is agent-rig only; propagation is separate follow-up work
  tracked as its own issue after this sprint ships.

## Constraints

- Must: Source claim subjects from the Signpost section in addition to Pillar-sourced extraction.
- Must: Require a qualifying tool call for every Signpost-sourced subject, independent of what
  Pillar's own prose says.
- Must: Preserve existing behavior when `pillar_idx is None` (C3 does not run).
- Must: Add a regression test reproducing the exact issue #27 evasion verbatim.
- Must: Keep both existing C3 test suites (`first-turn-contract-c3-claim-matching`,
  `first-turn-contract-c3-path-query-boundary-matching`) passing unchanged.
- Must: Run Frank's spec-gate and forge-gate Cold (unbriefed dispatch, isolated detached checkout)
  per `docs/ISSUE-RUNBOOK.md`'s classification of this as an enforcement-mechanism defect.
- Must not: Add fuzzy/similarity matching in v1.
- Must not: Touch C1 or C2 logic, add a new hook/script file, or change first-turn-only scope.
- Assumes: An empty-subject Signpost genuinely means there is nothing checkable to require —
  treated as correct behavior, not a residual gap. If this assumption is wrong (some empty-looking
  Signposts still imply an obligation), the fix's core premise changes.
- Assumes: Real Signpost text in this repo's transcripts is representative enough to design
  extraction patterns against, without needing a formal exhaustive grammar.
