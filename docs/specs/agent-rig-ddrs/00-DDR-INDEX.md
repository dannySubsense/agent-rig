# DDR Index — Agent Rig

| # | Title | Status |
|---|-------|--------|

---

## Backlog (not yet a DDR)

Ideas surfaced during other work, worth preserving but not yet written up as a DDR. Promote to a numbered DDR above before spec'ing.

- **Frank's-Lessons cross-project LORE initiative** — proposed 2026-07-15 (Danny), during spec-forge-cadence-refactor Intake discussion of Frank's prose trim. Idea: the "why" behind a Frank verdict (root-cause reasoning, especially on FAIL/HALT) is the most valuable part of his output and shouldn't live only inside one sprint's verdict doc — capture it as a standalone lesson-learned entry, likely under a shared `projectId` (e.g. `franks-lessons`) so any project's Frank dispatch can search and benefit from lessons learned in *any* other project, not just its own. Needs its own DDR: schema for a lesson entry, capture trigger (every FAIL/HALT? Danny's call?), how Frank/other agents query it, relationship to per-project LORE captures. Not in scope for spec-forge-cadence-refactor.
- **Stale `senior-qc` reference in `~/.claude/commands/security-loop.md`** — flagged 2026-07-15 by Frank during the spec-forge-cadence-refactor spec gate (`security-loop.md:89` cites the already-archived `senior-qc` skill, predates this sprint). Confirmed pre-existing and out of scope for this sprint's `.claude` propagation sweep (which only covers spec-orchestration/forge/Frank references). Needs a small standalone fix — update the reference to whatever superseded `senior-qc` (Frank's own `subagent_type: frank` dispatch, per DDR-013).
