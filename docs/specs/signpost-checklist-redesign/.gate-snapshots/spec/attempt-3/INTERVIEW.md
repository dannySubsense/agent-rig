# Interview: signpost-checklist-redesign
**Status**: Complete
**Mechanism**: Inline
**Date**: 2026-09-07

## Seed Questions (gap-diff)
| # | Category | Question | Answer | Assumed? |
|---|---|---|---|---|
| 1 | testing/rollback | How is this validated pre-ship, and what's the rollback if it also breaks on real usage? | No elaborate test corpus required — Danny tests it daily in live use and reports back. Rollback: unwire the hook and discuss, same pattern as the prior mechanism's archival. | no |
| 2 | non-functional | Does this replace the archived first-turn-contract mechanism 1:1 in trigger scope? | Yes — same Stop-hook trigger surface (first reply of session only, gated on session-queue briefing marker present, `stop_hook_active` bypass unchanged). Already decided in the prior session's archive record; re-confirmed here after rebuilding the mental model against `archive/first-turn-contract-enforcement/ARCHIVE-NOTE.md` and the relevant LORE captures, not asked as a new open question. | no |
| 3 | downstream impact | Does anything besides the archived mechanism depend on the Signpost/Pillar convention this redesign touches, and what is this sprint's deployment scope? | Corrected during spec-gate remediation (2026-09-07): `docs/specs/agent-rig-ddrs/HOOK-DEPLOYMENT-ROSTER.md` shows the archived first-turn-contract mechanism (`first_turn_contract_probe.py`) is currently live in nine other repos — `market_data`, `department-os`, `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore` — agent-rig's own copy was already unwired (commit `a44f1d5`). The original "no other consumer found in the record" answer was wrong — it conflated "no other consumer of the Signpost/Pillar convention within agent-rig" (true) with "no other repo runs the mechanism this sprint replaces" (false). This sprint's actual, and always-intended, scope is agent-rig only: it replaces the mechanism in agent-rig (Slice 5's CLAUDE.md-delivered Pillar syntax, Slice 6's agent-rig `.claude/settings.json` wiring) and does not touch, modify, or plan propagation to the other nine roster repos, which keep running the archived mechanism unchanged. Redeploying this redesign to them is separate, future work, not scoped here — mirroring how the archived mechanism itself was originally piloted in agent-rig before any retrofit-roster rollout. | no |
| 4 | edge cases | Is "tool-call-backed status per row" self-reported or does it require cross-referencing actual transcript tool-call entries? | No self-report. Real tool-call-backed evidence, per Cause's own words in the prior session's decision record — this was already decided, not an open design question. | no |

## Adaptive Follow-ups
| Triggered by | Question | Answer |
|---|---|---|
| Q1 | none — Danny redirected to a standing correction: the orchestrator had not rebuilt its mental model from the actual relevant record (archive + LORE) before re-asking Q2/Q4, which the record already answered | Mental model rebuilt against `archive/first-turn-contract-enforcement/ARCHIVE-NOTE.md`, its embedded mermaid decision flow, and 5 directly relevant LORE captures (session-close 0aa5f435, self-certification lesson 6faeba43, REACTOR-AS-GATEKEEPER retraction edc4052f, control-or-observe principle 28a7280d, Cold Frank queue a983f154) before answering Q2-Q4 above |
| Q3 (spec-gate remediation, 2026-09-07) | Frank's Layer 2 attempt-1 FAIL flagged Q3's original answer ("no other consumer exists in the record") as contradicted by `HOOK-DEPLOYMENT-ROSTER.md`, which lists nine other repos running the archived mechanism. Was the original answer wrong, and what's the real scope? | Yes, the original answer was wrong as stated — it read "no other consumer of the Signpost/Pillar convention" as equivalent to "no other repo runs the archived mechanism," which the roster contradicts. Corrected: nine other repos (`market_data`, `department-os`, `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore`) currently run the archived first-turn-contract mechanism and are unaffected by this sprint. This sprint's scope was always agent-rig-only in practice (Slice 6 only ever wired agent-rig's own settings.json) — that narrow scope is now stated explicitly in 01-REQUIREMENTS.md rather than left implicit inside an incorrect "no other consumer" claim. |

## Stopping Rationale
Danny closed the Interview directly after the corrected mental-model rebuild and answers above.
Q3 was reopened once, during spec-gate remediation on 2026-09-07, to correct a factual error
against `HOOK-DEPLOYMENT-ROSTER.md`; no other seed questions or adaptive follow-ups pending.

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
- Deployment scope: this sprint replaces the archived mechanism in agent-rig only. The other nine
  repos on `HOOK-DEPLOYMENT-ROSTER.md` continue running the archived first-turn-contract mechanism
  unchanged; propagating this redesign to them is separate, future work, not scoped here.
