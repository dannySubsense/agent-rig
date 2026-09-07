# Sprint North Star: signpost-checklist-redesign
**Status**: Locked
**Date**: 2026-09-07

## Declared Intent
Replace the archived first-turn-contract mechanism's approach to verification-honesty checking.
Instead of inferring a concept ("did this admit non-verification") from open Pillar prose, copy
each Signpost line verbatim into a checklist row and require a real, tool-call-backed status per
row. The mechanism checks only words it controls or observes — never words it must infer.

## In Scope / Out of Scope
See `01-REQUIREMENTS.md` Out of Scope, once written.

## Success Criteria (Layer 1 — fidelity)
- Every Signpost claim line becomes a checklist row, copied verbatim (observed text, not
  inferred).
- Every row's status is backed by a real tool-call, not self-report.
- No free-form section exists where a verification evasion can hide (the specific failure mode
  that killed the archived mechanism's C2 check).
- Trigger scope matches the archived mechanism exactly: Stop-hook, first reply of session only,
  gated on session-queue briefing marker presence, `stop_hook_active` bypass unchanged — unless a
  later step surfaces a reason to diverge, which is a HALT to Danny, not a silent change.

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: Purpose — "the DDR → Intake/Interview → spec →
forge cadence, QC/judgment gates like Frank" — this sprint hardens the verification-honesty
mechanism that gates first-turn session behavior, one of the cross-cutting orchestration
mechanics Agent Rig exists to develop centrally.
Project North Star status at gate time: non-DRAFT ("Established") → normal binding PASS/FAIL, no
PROVISIONAL tag.
