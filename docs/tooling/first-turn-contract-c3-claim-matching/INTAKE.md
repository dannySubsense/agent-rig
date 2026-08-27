# Intake: first-turn-contract-c3-claim-matching

**Status**: APPROVED

**Date**: 2026-08-27
**Author**: wright

---

## Problem Statement

`check_c3_violation` in `scripts/first_turn_contract_probe.py` (part of the DDR-004
Signpost/Pillar first-turn contract, Stop hook) checks only whether *any* qualifying tool
call (a completed, non-`TodoWrite` `tool_use`/`tool_result` pair) occurred before a turn
that asserts a `**Pillar:**` section. It does not check that the tool call's target
(file path, PR number, command, query) matches the specific claim being asserted in that
Pillar section. A turn can make several Pillar claims, back only one with a real check,
and still pass C3 as long as any qualifying call happened anywhere earlier in that turn's
preceding transcript — including a call left over from an unrelated earlier claim.

This defeats the purpose of C3: it is meant to prove a Pillar claim was actually verified,
not merely that verification activity of some kind happened during the turn.

## Context

Surfaced 2026-08-21 during the `signpost-pillar-propagation` sprint (DDR-004), alongside a
live example: another agent (alpha), under a leading question, produced confident
re-quoted claims mid-session without visibly re-opening the transcript to verify them —
a failure C3 as currently written would not catch, since any earlier qualifying tool call
in that session satisfies the presence check. Logged at the time as a future hardening
item, not blocking DDR-004's ACCEPTED status (`00-DDR-INDEX.md` row 004).

Raised again 2026-08-27 when Danny asked whether the mechanism was ready to retrofit to
other repos. Decision that session: fix C3 first, rather than retrofit with the gap
documented as a caveat in each target repo — propagating an unfixed gap N times is not
mitigation.

The fix is scoped to one existing function in one existing file, already covered by 3
C3-specific tests in `tests/test_first_turn_contract_probe.py` (623 lines, 16 tests
total, 13 non-C3). No new hook, no new file, no change to `.claude/settings.json` wiring.

## Capability Gaps This Sprint Closes

- **Claim-to-tool-call matching**: `check_c3_violation` must correlate a Pillar claim's
  subject against the tool call(s) that back it, not merely confirm a qualifying tool
  call exists somewhere earlier in the turn.

## Constraints

- No new hook, no new script file, no new settings.json wiring — this is a fix inside
  `first_turn_contract_probe.py`'s existing C3 logic.
- Must not regress the 13 existing non-C3 passing tests (C1/C2 and other cases) or the 3
  existing C3 tests without an explicit, reviewed reason for each changed expectation.
- Matching semantics are a real design decision (exact path/PR/query string match vs.
  fuzzy match vs. per-claim-type rules) and belong in the spec document, not improvised
  during forge.
- Any predetermined threshold or matching rule needs a citable rationale or an explicit
  PROVISIONAL tag with a named owner — no fabricated numbers.

## Open Questions

- What counts as a "claim subject" for matching purposes — is it limited to file paths
  and identifiers explicitly quoted near the Pillar heading, or does it need to parse
  free-text claims more generally?
- Should the fix change C3's violation *reason* string to say what a stronger check
  would have needed (for track-record diagnostic value), even where the weaker check
  still passes?
- Does this fix change DDR-004's own status line (currently ACCEPTED with the gap noted)
  once merged, and does the sprint's own PROGRESS/GATE-LOG need to reference DDR-004
  explicitly as the parent decision record?

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates
`spec-start --lite` Step 0.
