# Interview: unsourced-threshold-provenance-hook (domain-boundary-provenance-hook)
**Status**: Complete
**Mechanism**: Inline
**Date**: 2026-09-05

## Seed Questions (gap-diff)
| # | Category | Question | Answer | Assumed? |
|---|---|---|---|---|
| 1 | downstream impact | Sprint scope: does this sprint also execute the first retrofit into gap-lens-dilution-filter, or is it agent-rig build only? | Agent-rig build only. Retrofit into gap-lens-dilution-filter and the rest of the roster is separate follow-on work, same pattern as signpost-pillar-propagation's Slice 12. | no |
| 2 | testing/rollback | What test/rollback plan should the spec require for this hook before it goes live anywhere? | Same as `first-turn-contract-enforcement`: fail-open on internal error, append-only track record, `log_only` soak before `blocking`. No new pattern to design. | no |
| 3 | non-functional constraints | Is there a performance/latency bound the literal-scanning check must meet? | No hard bound — best-effort, same posture as `first-turn-contract-enforcement` (which has no stated latency SLA). No new number invented. | no |

## Adaptive Follow-ups
| Triggered by | Question | Answer |
|---|---|---|
| (none) | (all three answers confirmed existing precedent rather than opening new threads) | — |

## Stopping Rationale
2 consecutive non-generative exchanges after Q2 (Q2 and Q3 both confirmed "reuse the
first-turn-contract-enforcement precedent, no new design" with no new thread opened) — stopped at
3 of the 5-7 anchor. Edge-case detail (the threshold-shaped-literal detection rule itself, Open
Question 1 in `INTAKE.md`) was deliberately not interviewed here — it's an architecture-time design
comparison per the Intake's own Open Questions, not a gap Interview should resolve by asking Danny
to pick a detection strategy blind.
