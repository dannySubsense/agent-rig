# Interview: signpost-checklist-redesign
**Status**: Complete
**Mechanism**: Inline
**Date**: 2026-09-07

## Seed Questions (gap-diff)
| # | Category | Question | Answer | Assumed? |
|---|---|---|---|---|
| 1 | testing/rollback | How is this validated pre-ship, and what's the rollback if it also breaks on real usage? | No elaborate test corpus required — Danny tests it daily in live use and reports back. Rollback: unwire the hook and discuss, same pattern as the prior mechanism's archival. | no |
| 2 | non-functional | Does this replace the archived first-turn-contract mechanism 1:1 in trigger scope? | Yes — same Stop-hook trigger surface (first reply of session only, gated on session-queue briefing marker present, `stop_hook_active` bypass unchanged). Already decided in the prior session's archive record; re-confirmed here after rebuilding the mental model against `archive/first-turn-contract-enforcement/ARCHIVE-NOTE.md` and the relevant LORE captures, not asked as a new open question. | no |
| 3 | downstream impact | Does anything besides the archived mechanism depend on the Signpost/Pillar convention this redesign touches? | No other consumer found in the record — the archived mechanism was the sole consumer. This redesign replaces it in that same role. | no |
| 4 | edge cases | Is "tool-call-backed status per row" self-reported or does it require cross-referencing actual transcript tool-call entries? | No self-report. Real tool-call-backed evidence, per Cause's own words in the prior session's decision record — this was already decided, not an open design question. | no |

## Adaptive Follow-ups
| Triggered by | Question | Answer |
|---|---|---|
| Q1 | none — Danny redirected to a standing correction: the orchestrator had not rebuilt its mental model from the actual relevant record (archive + LORE) before re-asking Q2/Q4, which the record already answered | Mental model rebuilt against `archive/first-turn-contract-enforcement/ARCHIVE-NOTE.md`, its embedded mermaid decision flow, and 5 directly relevant LORE captures (session-close 0aa5f435, self-certification lesson 6faeba43, REACTOR-AS-GATEKEEPER retraction edc4052f, control-or-observe principle 28a7280d, Cold Frank queue a983f154) before answering Q2-Q4 above |

## Stopping Rationale
Danny closed the Interview directly after the corrected mental-model rebuild and answers above.
No further seed questions or adaptive follow-ups pending.

## Standing Constraints Carried Forward (not gap-diff items, recorded for the record)
- YAGNI discipline on edge cases: any edge case the downstream spec team (@requirements-analyst,
  @architect, etc.) surfaces must justify itself against actual need before being added to scope —
  no speculative edge-case coverage.
- Any new pattern/matching logic built for this redesign must be validated against real transcript
  data (`~/.claude/projects/*/*.jsonl`), never a self-written fixture — the self-certification
  failure from the prior sprint (6faeba43) applies directly here.
- Trigger scope inherits the archived mechanism's exact surface: Stop-hook, first reply of session
  only, gated on session-queue briefing marker presence, `stop_hook_active` bypass unchanged —
  unless a later step in this sequence surfaces a reason to change it (which would be a HALT to
  Danny, not a silent scope change).
