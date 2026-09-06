# Sprint North Star: unsourced-threshold-provenance-hook (formerly domain-boundary-provenance-hook)
**Status**: Locked
**Date**: 2026-09-05

## Declared Intent
Extend the existing, Frank-forge-gate-PASSED `domain-boundary-provenance` PreToolUse hook
(`.claude/hooks/domain-boundary-provenance.sh` + `scripts/domain_boundary_provenance_probe.py`)
with a new same-file/local detection pass that mechanically flags any numeric or boolean literal
used as a threshold, cap, limit, cutoff, retry count, or budget that lacks a citation or removal
at its point of definition — regardless of whether the
value crossed a domain boundary between pipelines. The incumbent's manifest-gated cross-domain
check stays untouched; this is an extension, not a replacement. Traces to Intake's amended
Problem Statement (`INTAKE.md`, 2026-09-05 amendment): PROMOTED DEFAULT does not require a
boundary crossing, and the original domain-crossing-only trigger required an unoperationalizable
judgment call that this sprint drops in favor of a mechanically checkable rule.

## In Scope / Out of Scope
See `01-REQUIREMENTS.md` Out of Scope once written. Confirmed via Interview (`INTERVIEW.md` Q1):
this sprint is agent-rig build only — it does not execute retrofit into gap-lens-dilution-filter
or the wider repo roster; that is separate follow-on work.

## Success Criteria (Layer 1 — fidelity)
- A working PreToolUse extension to the incumbent `domain-boundary-provenance` hook, reusing its
  wrapper/probe split (itself already a reuse of `first-turn-contract-enforcement`'s shape —
  bounded timeout, fail-open on internal error, append-only track-record log) rather than
  redesigning it or building a second hook (Interview Q2, Architecture §12 correction, Danny
  wording approval 2026-09-05).
- A concrete, checkable detection rule for "threshold-shaped literal" is specified and
  implemented — not deferred as "configurable" or "finalized at implementation time."
- The check verifies citation/PROVISIONAL-tag/removal presence only — it does not judge whether
  an existing citation is actually sound (that stays `benchmark`'s, Frank's, and a human's job),
  per DDR-0014's own "What it is not" and the amendment's unchanged inheritance of that limit.
- Rollout ships `log_only` first; promotion to `blocking` is a separate, later, per-repo decision
  — never bundled into initial install (Interview Q2, DDR-0014 amendment's Rollout section).
- No hard latency bound required — best-effort, same posture as the precedent hook (Interview Q3).
- Every predetermined constant this sprint itself introduces (e.g. any internal limit the hook's
  own code uses) carries a citable precedent or explicit PROVISIONAL tag — no exception to this
  repo's Decision Discipline for the sprint's own artifacts.

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: `docs/NORTHSTAR.md` Thesis — "Orchestration
mechanics — cadence, gates, agent personas — are worth developing and hardening in one dedicated
place rather than each consuming project inventing and drifting its own copy independently." This
sprint is exactly that: a cross-project mechanization of `~/.claude/CLAUDE.md` rule 1 (unsourced
numbers), built once in agent-rig per DDR-0014's explicit ownership split (spec-of-record in
gap-lens-dilution-filter, implementation owned here), for redeployment to any consuming repo
rather than each repo inventing its own version. Also serves the Non-goals boundary in reverse —
this sprint does NOT solve a problem specific to one consuming repo; it generalizes a pattern two
repos (gap-lens-dilution-filter, market_data/DDR-010's adjacent shape) have already independently
hit.
Project North Star status at gate time: `docs/NORTHSTAR.md` carries no literal `Status:` field —
it is described as "Established" (2026-07-17) and Danny-confirmed per this repo's `CLAUDE.md`, not
`DRAFT`. Frank should verify this directly against the file rather than accept this
characterization — if Frank's own read finds it effectively non-DRAFT, Layer 2 is a normal
binding PASS/FAIL with no PROVISIONAL tag; if Frank judges the absence of an explicit Status line
itself warrants DRAFT-equivalent treatment, the PROVISIONAL rule applies instead.
