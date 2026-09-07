# Sprint North Star: first-turn-contract-c3-signpost-sourcing
**Status**: Locked
**Date**: 2026-09-07

## Declared Intent
Make C3's subject requirement come from what the Signpost actually claimed, not from what the
Pillar section chose to restate — so an empty, vague, or self-admittedly-unverified Pillar can no
longer pass silently just because it names nothing for the checker to disagree with.

## In Scope / Out of Scope
See 01-REQUIREMENTS.md Out of Scope. (Summary for orientation only: `check_c3_violation` and its
subject-extraction helpers in `scripts/first_turn_contract_probe.py`; C1, C2, the hook wrapper,
and fuzzy/similarity matching are explicitly untouched.)

## Success Criteria (Layer 1 — fidelity)
- A Pillar section with zero extractable subjects, where the Signpost raised one or more real
  subjects, now fails C3 unless each Signpost-raised subject has a matching qualifying tool call.
- A Pillar section that still names its own subjects (today's behavior) continues to be checked
  exactly as before — no regression on the existing `first-turn-contract-c3-claim-matching` and
  `first-turn-contract-c3-path-query-boundary-matching` suites.
- A Signpost with zero extractable subjects imposes no new requirement (not a new fallback hole
  in the opposite direction).
- A regression test exists that reproduces the exact issue #27 evasion ("Pillar: none yet —
  nothing independently checked this session" with an unrelated qualifying tool call present)
  and proves it now fails where it previously passed.
- Frank's spec-gate and forge-gate for this sprint both ran Cold, per `docs/ISSUE-RUNBOOK.md`'s
  enforcement-mechanism-defect classification.

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: `docs/NORTHSTAR.md` Purpose — "the DDR →
Intake/Interview → spec → forge cadence, QC/judgment gates like Frank, and the dated packages...
that other projects install and vendor" is exactly what `first-turn-contract.sh`'s C1/C2/C3
checks are: a QC/judgment-gate mechanism hardened here and relied on by every session in this
repo. Also serves the Drift check's implicit standard: a gate mechanism with a known, provable
hole is itself a form of drift from "hardened in one dedicated place" if left unfixed.
Project North Star status at gate time: non-DRAFT (`docs/NORTHSTAR.md` carries no `Status: DRAFT`
line; it states "Established: 2026-07-17") — normal binding PASS/FAIL, no PROVISIONAL tag.
