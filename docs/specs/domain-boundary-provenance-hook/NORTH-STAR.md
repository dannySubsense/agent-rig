# Sprint North Star: unsourced-threshold-provenance-hook

**Status**: DRAFT — Rewritten 2026-09-06 to thesis-only form per Danny's ruling — awaiting
raw-diff review before re-Locking
**Date**: 2026-09-06 (rewrite; originally 2026-09-05)

## Thesis

Unsourced, threshold-shaped constants — the PROMOTED DEFAULT pattern, where an engineering value
silently becomes a scientific or safety-bearing parameter — are dangerous precisely because they
are invisible until something downstream depends on them being correct. Detecting them cannot
depend on a human remembering to look: it needs a mechanical check that runs at the moment a
constant is written, independent of whether that constant ever crosses a boundary between systems
or stays local to the file it was born in. A boundary crossing is one way this failure mode shows
up, not the defining condition for it.

## Objective

Extend this project's existing provenance-checking machinery so that it also catches
threshold-shaped constants that never leave their own file or module — closing the gap where a
check scoped only to cross-system boundaries misses the more common case of a constant that does
its damage without ever being exported anywhere.

## Scope Boundary, in Principle

- This work extends already-hardened, already-shipped tooling rather than standing up a second,
  parallel mechanism. Duplicating provenance-checking infrastructure would fragment the one place
  this kind of check should live and drift the two copies apart over time.
- This generalizes a pattern that has already surfaced independently in more than one consuming
  project, rather than solving a problem specific to a single repo. Building it once, here, and
  making it available for reuse is the point — not re-deriving the same mechanism per repo.
- Rollout of any new check into live enforcement is a gradual, per-repo decision, not a
  first-install default — a newly-widened check surfaces a large volume of pre-existing findings
  that need human triage before it is safe to treat as a gate.

## Traceability

This sprint serves the project North Star's thesis (`docs/NORTHSTAR.md`): orchestration mechanics
— cadence, gates, checks — are worth developing and hardening once, in this dedicated project,
rather than each consuming project inventing and drifting its own copy. This is a direct
mechanization of this repo's own binding rule against unsourced numbers (`~/.claude/CLAUDE.md`
rule 1), built here for redeployment elsewhere rather than reinvented per repo.

## Non-Goals

- Judging whether an existing citation is factually or scientifically sound — that remains a job
  for dedicated sourcing review and human judgment, not a mechanical presence check.
- Retrofitting this capability into other repos as part of this sprint — this sprint is the
  capability's home, not its full rollout.
