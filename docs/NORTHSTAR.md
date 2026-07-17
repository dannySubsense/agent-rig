# Northstar — Agent Rig

**Established:** 2026-07-17 · **Last reviewed:** 2026-07-17

## Purpose
Agent Rig exists to assemble, tune, and refine multi-agent orchestration patterns and cross-cutting agent personas before they're relied on elsewhere — the DDR → Intake/Interview → spec → forge cadence, QC/judgment gates like Frank, and the dated packages (`spec-orchestration-<date>/`, `forge-<date>/`) that other projects install and vendor. It's a workshop, not a product: work here exists so other repos get sharper, more reliable orchestration tooling, not to ship a standalone application of its own.

## Thesis
Orchestration mechanics — cadence, gates, agent personas — are worth developing and hardening in one dedicated place rather than each consuming project inventing and drifting its own copy independently. Two data points so far, not a proven case: Frank's transfer (DDR-013), now versioned centrally instead of drifting per-consumer; and, this session, a real bug in `forge-start.md`'s branch/commit handling (found via a live incident in agent-dashboard) fixed once here and redeployed everywhere, instead of silently diverging per-repo the way it already had. This is the wrong bet if consuming projects' orchestration needs turn out too divergent for shared mechanics to hold — if every project ends up needing bespoke cadence/gate logic anyway regardless, a central workshop adds indirection without earning it.

## Non-goals
Single-project business logic — a pattern that only makes sense for one consuming repo's domain belongs in that repo, not here. Being a production deployment target beyond what's needed to develop/test the packages and personas it owns. Owning an agent persona genuinely scoped to one project's concerns. Re-deriving decisions that belong to a consuming project's own architecture. Accumulating shared skills/templates/tooling without the same curation discipline already applied to `agents/` (named owner, README entry, stated provenance) — breadth of scope is not an excuse to drop that discipline.

## Drift check
A sprint here is off-Northstar if: (1) it solves a problem specific to one consuming repo instead of the shared mechanism; (2) it adds generality, configuration, or abstraction beyond what any real, named consumer asked for; (3) a cross-cutting persona or package changes but its propagation/redeploy to already-vendored consumers is left undefined or silently skipped; (4) a shared skill, template, or convention gets added here without an owner, a README entry, or stated provenance.
