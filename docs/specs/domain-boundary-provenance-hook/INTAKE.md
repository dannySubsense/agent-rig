# Intake: domain-boundary-provenance-hook

**Status**: APPROVED (2026-08-22, Danny)

**Date**: 2026-08-22
**Author**: wright
**Mode**: spec-lite (recommended) — same shape as `first-turn-contract-enforcement`
(`docs/specs/first-turn-contract-enforcement/INTAKE.md`): one blocking checker script/hook, no UI,
no product surface, no multi-stakeholder scope. Requirements/UI-spec/roadmap layering is skipped
because there's no UI to spec and the build is too small to split across three documents; Frank's
binding gate and human approval are NOT skipped. Danny's call to confirm or override at approval.
**DDR**: `docs/specs/agent-rig-ddrs/DDR-006-domain-boundary-provenance-hook.md`

---

## Problem Statement

A numeric constant, cap, threshold, or boolean flag can be correct and load-bearing in the system
it was born in, cross into a different pipeline uninspected, and never be re-justified at the new
site. Two real, costly incidents in `gap-lens-dilution-filter` share this exact shape: a byte cap
written as a memory guard for one pipeline was inherited by the WHO extractor, whose entire job was
reading the bytes it cut (2026-07-13 postmortem, 99 days void); and a market-cap floor computed by
`market_data` for its own domain was silently carried into `gap-lens-dilution-filter`'s research-
population inclusion criterion, dropping exactly the issuers where the hypothesized effect should
be strongest (OQ-5, found 2026-08-20, ruled/removed 2026-08-22).

This sprint builds the mechanism to catch the *next* instance before it reaches that cost: for any
constant/cap/flag a pipeline reads from outside its own config/spec, require a citation at the
consuming site for why that value is correct for that use. Absence of citation is a flagged
finding, not a silent pass.

## Context

- **Spec of record**: `gap-lens-dilution-filter` DDR-0014 (`docs/DDR/DDR-0014-DOMAIN-BOUNDARY-
  PROVENANCE-CHECK.md`, commit `eca45d2`, Status: **Accepted**, Danny, 2026-08-22). This Intake does
  not restate DDR-0014's incidents or rationale — read it directly. This sprint builds the
  implementation DDR-0014 assigns to agent-rig.
- **agent-rig-side DDR**: `docs/specs/agent-rig-ddrs/DDR-006-domain-boundary-provenance-hook.md` —
  the short implementation-side record this Intake formalizes into a spec.
- **Reference implementation pattern**: `github.com/Glitch-Cat-Club/prompt-router-starter`'s
  `gate.py` (Stop hook) — allowlisted proof commands run against a claim, non-allowlisted items
  stamped `manual` and never block. This sprint reuses the *shape* (allowlist + explicit
  non-blocking fallback for anything outside it), not that repo's code directly.
- **Existing infrastructure to reuse**: `docs/specs/first-turn-contract-enforcement/` — the
  Stop-hook wrapper pattern (bounded timeout, fail-open on any internal error, append-only
  track-record log). This sprint's hook should be a sibling wrapper, not a redesign of that shape.
- **Precedent in-repo for "one source, not many"**: DDR-0014 itself cites
  `gap-lens-dilution-filter/research/pipeline/universe_membership.py`'s
  `test_no_second_membership_implementation_exists` guard as the closest existing analogue — a
  failing test enforcing single-ownership of a piece of logic. This sprint generalizes that from
  "one definition per repo" to "one justified value per domain crossing."
- **Governing thesis**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` §1 —
  "rules that live as exhortations get performed; rules that live as failing checks get satisfied."
  This sprint is DDR-005's first concrete build in the hook-mechanization cluster's approved order
  (`00-DDR-INDEX.md`).
- **Rollout status**: build-order 1st in the cluster, and granted an explicit exception to the
  cluster's one-at-a-time-with-soak-period rollout policy (`00-DDR-INDEX.md`, 2026-08-22) —
  expedited due to beta's current, real need and potential complementary value to other projects
  (DDR-010's adjacent shape, `market_data`). The exception covers *this* build only: DDR-006 still
  runs and soaks alone before the next hook in the cluster goes **live** — only the *next* hook's
  spec/design work (DDR-008) may proceed in parallel, per that same decision.

## What Is Missing

1. **A hook that detects a cross-domain value read with no citation at the consuming site.**
   Currently nothing exists — the check is entirely a documented convention (CLAUDE.md Rule 1,
   the `benchmark` agent) that depends on someone remembering to run it. Both source incidents
   were caught by audit/measurement after the fact, not by anything running unattended.
2. **A definition of "outside this pipeline's own config/spec."** DDR-0014 gives two clear positive
   examples (a DB column owned by a different domain; an imported module's constant) but the
   general detection rule is not yet specified — this is the sprint's core design problem.
3. **A citation convention the hook checks against.** Likely reuses this repo's existing
   PROVISIONAL-tag convention (CLAUDE.md Decision Discipline) rather than inventing a new format,
   but that reuse is not yet confirmed as sufficient for this check's needs.
4. **A Stop-hook (or equivalent trigger) wired into `.claude/settings.json`**, sibling to
   `first-turn-contract.sh`, with its own track-record log per this repo's established pattern.
5. **A first retrofit target.** `gap-lens-dilution-filter` is the origin and the obvious first
   target per DDR-0014; beyond that, this repo's existing retrofit-roster pattern
   (`signpost-pillar-propagation`'s target list) applies rather than a fresh survey — but scope for
   *this* sprint (agent-rig build only, vs. also retrofitting `gap-lens-dilution-filter`) needs
   deciding.

## Constraints

- **Do not duplicate DDR-0014's content.** Per DDR-0014's own explicit instruction and DDR-006's
  own §0: this Intake, and everything downstream of it, cites DDR-0014 for the incidents and
  rationale rather than restating them. Two copies of the same decision is the cross-project shape
  of the defect `universe_membership.py`'s own precedent exists to prevent.
- **Presence/absence + citation only — not a soundness judgment.** Per DDR-0014 §"What it is not"
  and DDR-006 §1: this check verifies a citation exists, not that the citation is *correct*. Judging
  whether an existing citation is actually sound stays `benchmark`'s and Frank's job, and a human's.
  No acceptance criterion below may imply otherwise.
- **Reuse `first-turn-contract-enforcement`'s wrapper shape.** Bounded timeout, fail-open on any
  internal probe error, append-only track-record log — this sprint should not redesign that
  infrastructure, only the detection logic specific to domain-boundary crossings.
- **Manual-push-only** stays in force; this sprint's commits don't auto-push.
- **Expedited, not corner-cut.** The exception granted (see Context) is about sequencing relative to
  other hooks in the cluster, not about skipping Frank's binding gate, QC, or this repo's standard
  Intake→Interview→spec→forge cycle. Every predetermined number/threshold this sprint introduces
  still needs a citable precedent or an explicit PROVISIONAL tag, per this repo's Decision
  Discipline — no exception to that rule.

## Open Questions

1. **Detection rule for "outside this pipeline's own config/spec."** DDR-0014's two examples (DB
   column from another domain; imported module constant) are clear but not exhaustive — needs a
   general, checkable rule before architecture can be written. Candidate approaches (static import/
   reference analysis vs. an explicit manifest of "external sources" per pipeline) should be
   compared at spec time, not decided here.
2. **Citation format and location.** Inline comment, a docs file, or a structured tag — likely reuse
   the PROVISIONAL-tag convention, but not yet confirmed sufficient for a cross-domain-value use
   case specifically (vs. its original unsourced-number use case).
3. **Trigger surface.** PreToolUse (on Edit/Write to pipeline config/data files), a pre-commit-style
   check, or a scheduled/on-demand scan — needs the same design rigor
   `first-turn-contract-enforcement` went through (live-verified field/event claims, not assumed).
4. **Sprint scope**: agent-rig build only, or does this sprint also execute the first retrofit into
   `gap-lens-dilution-filter`? Affects sequencing and whether beta needs to be involved as a
   downstream reviewer before this sprint closes.
5. **Relationship to DDR-010** (Gate Assertion-Coverage Check, `market_data`, still DRAFT pending
   Danny's ruling on scope/sequencing) — same family, different member, not this sprint's concern
   to resolve, but worth flagging so architecture doesn't accidentally build overlapping tooling.

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates `spec-start`
Step 0.
