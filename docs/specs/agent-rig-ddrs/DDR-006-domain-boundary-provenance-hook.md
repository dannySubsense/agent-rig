# DDR-006 — Domain-Boundary Provenance Hook (implementation-side record)

**Status**: DRAFT — ownership accepted, not yet spec'd/forged
**Author**: wright
**Date**: 2026-08-22
**Scope**: cross-project — implemented and stewarded in agent-rig, run against any homelab
pipeline that reads a constant/cap/flag across a domain boundary.

---

## 0. Relationship to gap-lens-dilution-filter DDR-0014

**This is a short, implementation-side record, not a restatement.** The spec, both source
incidents, the rationale, and the ownership split are all recorded once, in
`gap-lens-dilution-filter/docs/DDR/DDR-0014-DOMAIN-BOUNDARY-PROVENANCE-CHECK.md` (originally
`docs/decisions/`, renamed to `docs/DDR/` same session; commit `eca45d2`, authored by
beta/gaplens-SEC, **Status: Accepted, Danny, 2026-08-22**). Do not duplicate that content here —
per DDR-0014's own §"Decision", two copies of the same decision is the cross-project shape of the
exact defect its `universe_membership.py` precedent exists to prevent (one rule, drifting across
multiple restatements). Read DDR-0014 directly for: the WHO byte-cap incident (2026-07-13
postmortem), the OQ-5 borrowed market-cap-floor incident (2026-08-20/22), the proposed check's
exact shape, and what the check explicitly does *not* do (judge whether a cited rationale is
sound — that stays `benchmark`'s and Frank's job).

**Ownership split** (agreed over Switchboard thread `hook-patterns-vs-prose-conduct`,
2026-08-22, wright ↔ beta, confirmed by Danny): DDR-0014 is the spec of record. Agent-rig owns
the build — this DDR tracks that build, since the mechanism is cross-project by design and
agent-rig already stewards the Stop-hook / first-turn-contract reference implementation this
extends.

## 1. What this DDR tracks

The implementation of DDR-0014's check: a hook-shaped presence/absence + citation verification —
for any numeric constant, cap, threshold, or boolean flag a pipeline reads from outside its own
config/spec (a shared DB column, an imported module's constant, an inherited default), the
consuming pipeline's own docs/spec must cite *why that value is correct for this use*. Absence of
that citation is a flagged finding.

Per DDR-0014 §"Consequences" and §"Alternatives considered": this is complementary to, not a
replacement for, the `benchmark` agent (which judges whether an *existing* citation is actually
good) — this hook only closes the "no citation at all" gap, unattended, without needing an agent
dispatch to be remembered.

## 2. Not yet decided (open, per this DDR's DRAFT status)

- **Hook event and trigger surface.** Candidates: PreToolUse (on Edit/Write to pipeline
  config/data files), a pre-commit-style check, or a scheduled/on-demand scan. Needs the same
  design rigor `first-turn-contract-enforcement` went through (Frank spec-gate, live-verified
  field/event claims, not assumed) before implementation.
- **What counts as "outside this pipeline's own config/spec."** DDR-0014 gives two clear positive
  examples (a DB column owned by a different domain; an imported module's constant) but the
  general detection rule — how the hook tells a cross-boundary read from a normal same-repo
  import — is not yet specified.
- **What counts as a valid citation**, and where it must live (inline comment, a docs file, a
  structured tag) — needs a decision, likely reusing this repo's existing PROVISIONAL-tag
  convention (CLAUDE.md Decision Discipline) rather than inventing a new one.
- **Rollout scope**: which repos this runs against first. gap-lens-dilution-filter is the origin
  and an obvious first target; beyond that follows this repo's existing retrofit-roster pattern
  (`signpost-pillar-propagation`'s target list) rather than a fresh survey.
- **Sequencing against DDR-005.** This hook is one concrete instance of DDR-005's general thesis
  (mechanize conduct, don't leave it as prose) — worth building as DDR-005's first real test case
  rather than a separate track, per DDR-005 §5's own named-test framing.

## 3. Next step

Intake, per this repo's standard workflow (Intake mandatory before spec). Not yet written.

---

## References

- `gap-lens-dilution-filter/docs/DDR/DDR-0014-DOMAIN-BOUNDARY-PROVENANCE-CHECK.md` (Accepted, commit `eca45d2`) — the spec of record
- `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — the general thesis this is one instance of
- `docs/specs/first-turn-contract-enforcement/` — the Stop-hook reference implementation this extends
- `~/.claude/CLAUDE.md` — Research Data Integrity rules 1–3, PROMOTED DEFAULT → SHARED WELL → CERTIFIED GARBAGE doctrine
- Switchboard thread `hook-patterns-vs-prose-conduct`, 2026-08-22
