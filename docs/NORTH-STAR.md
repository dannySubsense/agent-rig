# Agent Rig — Project North Star

**Status**: DRAFT — awaiting Danny's review
**Author**: wright
**Date**: 2026-07-15
**Scope**: project-level (durable, not sprint-scoped). Distinct from each sprint's own North Star doc, which lives under `docs/specs/<sprint-slug>/` and is checked against this one, not a replacement for it.

**Interface note**: Lumen (agent-dashboard) owns the global North Star anchor template for all projects — confirmed by Danny 2026-07-15: this doc is a placeholder written ahead of that template, to be **swapped out wholesale** once Lumen's version is delivered, not merged or reconciled piecemeal. Content below is agent-rig's working draft in the meantime, and doubles as a real test case for Lumen's schema once it lands. Don't block this sprint's Frank-gate design on its arrival.

---

## Mission

Agent Rig is a workshop, not a product. It exists to assemble, tune, and refine multi-agent orchestration patterns — DDR → spec → forge cadence, QC gates, judgment gates like Frank — before they're relied on elsewhere, and to be the source-of-record home for cross-cutting agent personas (dispatched sub-agents used across multiple projects, not scoped to one). Work here is done so that *other* projects get sharper tools, not to ship a standalone application.

## In Scope

- Designing, testing, and revising orchestration mechanics themselves (spec-orchestration, forge, the DDR/Intake/Interview/Frank-gate loop).
- Owning and evolving cross-cutting agent personas (`agents/`, e.g. Frank) — development, testing, and stewardship, with a defined sync/redeploy path to their global dispatch location.
- Producing dated, versioned packages (`spec-orchestration-<date>/`, `forge-<date>/`) that other projects vendor/install, with old versions archived rather than edited in place.
- Documenting and hardening the rules that make gates load-bearing (not just present in prose) — the direct lesson of the gap-lens-dilution-filter postmortem.

## Out of Scope (explicit non-goals)

- Single-project business logic. If a pattern only makes sense for one consuming repo's domain, it belongs in that repo, not here.
- Being a production deployment target itself, beyond what's needed to develop/test the packages and personas it owns.
- Owning an agent persona that is genuinely scoped to one project's concerns — that agent lives in its own repo, not `agents/`.
- Re-deriving decisions that belong to a consuming project (e.g. a specific repo's own architecture choices) — agent-rig's job is the shared mechanism, not every project's use of it.

## Success Criteria — what "served the mission" looks like

A sprint here is on-mission when its output is something *other* work can pick up and rely on:

- An orchestration-pattern change that measurably closes a gap already seen to bite in practice (a real failure, not a hypothetical) — the same evidentiary bar the global Research Data Integrity rules set for any claimed number, applied here to any claimed process fix.
- A cross-cutting agent change (e.g. Frank's prose trim) that ships with its sync/redeploy step actually run, not assumed — so every live consumer gets it, not just the source file.
- A new dated package version that existing vendored consumers can adopt without a silent breaking change, or with an explicit, communicated migration path if one is unavoidable.

## Drift Smells — Frank's Layer 2 checklist

When Frank checks a finished sprint against *this* doc (not against the sprint's own North Star — see the layered-check design in the cadence-refactor Intake), these are the concrete smells to look for, not just a vibe check:

- The sprint solved a problem specific to one consuming repo instead of the shared mechanism (scope leak out of agent-rig's lane).
- The sprint added generality, configuration, or abstraction beyond what any real, named consumer asked for (YAGNI violation dressed as "flexibility").
- A cross-cutting persona or package changed but its propagation to already-vendored consumers was left undefined or silently skipped.
- The sprint's own stated goal (its sprint North Star) doesn't trace back to anything in this doc's Mission/In-Scope sections — internally consistent but pointed at the wrong target.

If any of these are true, Frank's Layer 2 verdict is FAIL/HALT regardless of how clean the sprint's own internal execution was (Layer 1 passing does not offset Layer 2 failing).

## Non-Negotiables (inherited, not re-derived here)

- Global Research Data Integrity rules (`~/.claude/CLAUDE.md`) bind any work here that touches data, benchmarks, or claimed numeric thresholds.
- Frank's five non-negotiable pre-checks are load-bearing and must survive any prose trim untouched in substance.
- Push policy is manual-push-only; DDR is optional, Intake is mandatory before any spec sprint.

## Review

Danny reviews this doc directly — not delegated to Frank, since project intent is the Composer's call, not a QC judgment. Treat as draft until he confirms or amends it. Re-review whenever agent-rig's own charter changes materially (e.g. taking stewardship of a new cross-cutting persona, per the DDR-013 precedent).
