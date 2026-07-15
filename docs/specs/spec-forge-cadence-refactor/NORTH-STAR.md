# Sprint North Star: spec-forge-cadence-refactor
**Status**: Locked (set once Interview closed, 2026-07-15; not re-edited during the doc sequence — any need to change this mid-flight escalates to Danny, it does not get silently redefined)
**Date**: 2026-07-15

## Declared Intent
Make the gates that already exist in `spec-orchestration`/`forge`/Frank's prose actually load-bearing, so a sprint can no longer proceed past a gate that exists only in words. Three specific gaps drive this: CADENCE/INVARIANTS read "if exists" with no HALT; nothing checks a finished spec or implementation against a durable sprint or project intent; Frank's verdict isn't a binding loop condition anywhere it's used, and his prose has grown too heavy for a fast-moving loop.

## In Scope / Out of Scope
See `01-REQUIREMENTS.md` Out of Scope section — not restated here.

## Success Criteria (Layer 1 — fidelity)
- Every one of `01-REQUIREMENTS.md`'s 46 ACs is implemented and independently verifiable (diff/grep/dry-run/Danny's review — no slice closes on a prose read alone, per `04-ROADMAP.md`'s own stated verification discipline).
- Mandatory Intake gate, standalone Interview stage, sprint North Star template, and binding two-layer Frank gate all exist as load-bearing mechanisms in the new `spec-orchestration-07152026`/`forge-07152026` packages — not just documented intent.
- Frank's prose trim conforms to the structural target (four-section verdict, zero pre-check/HALT substance loss, condensation checked against the disposition table) — no numeric proxy substituted for that structural check.
- The `~/.claude` propagation sweep is grep-verified subtractive, not additive-only — old references actually gone, confirmed, not assumed.
- No unsourced numeric constant survives anywhere in the shipped artifacts — every number present traces to a cited precedent, a Danny-ratified decision, or is deleted (the standard this sprint's own spec-gate loop was itself held to).

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: `docs/NORTH-STAR.md` Mission — "Agent Rig is a workshop... assemble, tune, and refine multi-agent orchestration patterns — DDR → spec → forge cadence, QC gates, judgment gates like Frank — before they're relied on elsewhere"; In Scope — "Designing, testing, and revising orchestration mechanics themselves (spec-orchestration, forge, the DDR/Intake/Interview/Frank-gate loop)," "Owning and evolving cross-cutting agent personas (`agents/`, e.g. Frank)... with a defined sync/redeploy path," "Producing dated, versioned packages... with old versions archived rather than edited in place," and "Documenting and hardening the rules that make gates load-bearing (not just present in prose) — the direct lesson of the gap-lens-dilution-filter postmortem."
Project North Star status at gate time: DRAFT → Layer 2 verdict is **PROVISIONAL PASS**, to be re-run once `docs/NORTH-STAR.md` reaches non-DRAFT status (per Lumen's wholesale-swap delivery — no fixed date, re-run triggers on that swap landing, per Danny's ratified rule).
