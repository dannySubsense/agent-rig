# Requirements: Unsourced-Threshold Provenance Hook

## Summary
A Stop-hook, sibling in shape to `first-turn-contract-enforcement`, that flags any numeric or
boolean literal used in code as a threshold, cap, limit, cutoff, retry count, or budget when it
lacks, at or adjacent to its definition, a citation, a named-owner `PROVISIONAL — unvalidated`
marker, or removal — regardless of whether the value was defined locally or crossed an ownership
boundary. Per DDR-0014's 2026-09-05 amendment (spec-of-record), the domain-crossing precondition
is dropped entirely; it is one flagged case among all threshold-shaped literals, not a trigger
condition. This sprint builds the hook in agent-rig only; retrofit into
`gap-lens-dilution-filter` or other repos is separate follow-on work (Interview Q1).

## User Stories

**US-1**
As a repo maintainer running Claude Code sessions,
I want a Stop-hook that scans changed code for threshold-shaped literals lacking a citation,
PROVISIONAL tag, or removal,
so that unsourced numbers (PROMOTED DEFAULT per `~/.claude/CLAUDE.md` rule 1) are caught
mechanically instead of depending on someone remembering to run `benchmark` or an audit.

**US-2**
As a repo maintainer,
I want the hook to run in `log_only` mode first, with promotion to `blocking` a separate later
per-repo decision,
so that widening the check's surface (dropping the domain-crossing precondition surfaces every
pre-existing same-file magic number too) doesn't immediately block unrelated work before triage.

**US-3**
As a repo maintainer,
I want the hook to fail open on any internal error and keep an append-only track-record log,
consistent with `first-turn-contract-enforcement`'s wrapper shape,
so that a bug in the check itself never blocks a session, and every run (pass, flag, or error) is
auditable after the fact.

**US-4**
As a repo maintainer,
I want the check to verify only presence/absence of a citation, PROVISIONAL tag, or removal — not
judge whether an existing citation is actually correct,
so that soundness judgment stays the job of `benchmark`, Frank, and a human, per DDR-0014's own
"What it is not" boundary.

## Acceptance Criteria

**US-1**
- [ ] Given a code change introducing a numeric or boolean literal that matches the detection
      rule for "threshold-shaped" (rule to be finalized at architecture time per Open Question 1
      below), when the Stop-hook runs, then the hook flags the literal if no citation,
      PROVISIONAL-with-owner tag, or evidence of removal is present at or adjacent to its
      definition.
- [ ] Given a threshold-shaped literal that already carries a citation or a PROVISIONAL tag
      naming a human owner, when the hook runs, then it does not flag that literal.
- [ ] Given a literal that does not match the threshold-shaped detection rule (e.g. a loop bound
      or array index, per the detection rule's own exclusions), when the hook runs, then it is
      not flagged.
- [ ] The detection rule fires identically regardless of whether the literal was defined locally
      in the same file/module or read/imported from elsewhere — no code path in the hook
      conditions flagging on a domain-crossing or import check.

**US-2**
- [ ] Given the hook is newly installed in a repo, when it runs, then it defaults to `log_only`
      mode (writes findings to the track-record log, does not block the session).
- [ ] Given a repo owner has explicitly configured the hook to `blocking` mode, when it runs and
      finds an unresolved flagged literal, then the session-ending action is blocked.
- [ ] No repo's hook installation ships in `blocking` mode as its initial configuration.

**US-3**
- [ ] Given the hook's internal probe raises an error or exceeds its bounded timeout, when the
      hook runs, then the session is not blocked (fail-open) and the error is recorded in the
      track-record log.
- [ ] Given any hook run (pass, flag, or internal error), when it completes, then an entry is
      appended to the track-record log — no run is silently dropped.
- [ ] The track-record log is append-only; no code path in the hook truncates or overwrites prior
      entries.

**US-4**
- [ ] Given a literal carries a citation that is factually wrong or outdated, when the hook runs,
      then it does not flag that literal (presence of a citation is sufficient; correctness is
      out of scope for this check).
- [ ] No acceptance criterion, log message, or user-facing hook output in this build asserts or
      implies that a passing check means the cited value is scientifically or numerically sound.

## Architecture-Level Design Question (not resolved here)

**AD-1 — Detection rule for "threshold-shaped literal."** INTAKE.md Open Question 1 (amended
2026-09-05) is explicitly a design comparison, not a requirement this document can resolve without
prescribing implementation:
- Candidate approaches to be compared at architecture time: (a) a fixed set of syntactic contexts
  (comparison operands, default-kwarg names matching limit/cap/threshold/cutoff/retry/budget
  patterns, slice/truncation arguments), (b) a naming-convention heuristic, (c) an explicit
  per-file manifest.
- Requirement on the architecture doc: it must select and fully specify one concrete, checkable
  rule — Success Criteria (NORTH-STAR.md) explicitly forbids deferring this as "configurable" or
  "finalized at implementation time."
- Related open item carried forward, not requirements-blocking: citation format/location
  (INTAKE.md Open Question 2) likely reuses this repo's existing PROVISIONAL-tag convention, and
  trigger surface (Open Question 3 — PreToolUse vs. pre-commit-style vs. scheduled scan) needs the
  same live-verified design rigor as `first-turn-contract-enforcement`. Both are architecture-time
  decisions, not requirements decisions, and are noted here so 02-ARCHITECTURE.md does not treat
  them as already settled.

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Literal is a loop bound, array index, or other non-threshold numeric use | Not flagged — excluded by the detection rule's own scope (threshold/cap/limit/cutoff/retry-count/budget only) |
| Literal already has a citation, but the citation link/reference is broken or wrong | Not flagged by this hook — correctness of citations is `benchmark`'s/Frank's/a human's job, not this check's |
| Literal is defined in the same file/module with no import involved | Flagged the same as any cross-boundary literal if it otherwise matches the detection rule — domain-crossing is not a precondition |
| Hook's internal scan exceeds its timeout or throws an exception | Fail open — session not blocked, error appended to track-record log |
| Repo has hook newly installed with pre-existing unlabeled magic numbers throughout | All matching literals flagged in `log_only` mode; no blocking until repo owner explicitly promotes to `blocking` after triage |
| A PROVISIONAL tag exists but does not name a human owner | Treated as absent — flagged, since the amended check requires a *named-owner* PROVISIONAL marker, not a bare "TODO" or unowned tag |
| Threshold-shaped literal is removed entirely (e.g. inlined logic without a magic number) | Not flagged — removal is one of the three satisfying conditions |
| Hook's own code introduces an internal constant (e.g. a scan timeout value) | That constant itself must carry a citation or PROVISIONAL tag per this repo's Decision Discipline — no exception for the sprint's own artifacts |

## Out of Scope

- NOT: judging whether an existing citation is factually or scientifically correct (soundness
  judgment stays `benchmark`'s, Frank's, and a human's job — DDR-0014 "What it is not").
- NOT: retrofitting this check into `gap-lens-dilution-filter`, `market_data`, or any other
  consuming repo as part of this sprint — agent-rig build only (Interview Q1).
- NOT: promoting any repo's hook installation to `blocking` mode as part of this sprint's initial
  install — `log_only` first is the shipped default; promotion is a separate later per-repo
  decision.
- NOT: solving DDR-010 (Gate Assertion-Coverage Check, `market_data`, still DRAFT) — a related
  family member, explicitly not this sprint's concern beyond flagging the overlap risk to
  architecture.
- NOT: enforcing a hard latency/performance SLA on the scan — best-effort, same posture as
  `first-turn-contract-enforcement` (Interview Q3).
- Deferred: any survey of a full retrofit roster beyond `gap-lens-dilution-filter` as "obvious
  first target" — that survey, if needed, is follow-on work per the existing retrofit-roster
  pattern (`signpost-pillar-propagation`).

## Constraints

- Must: implement the amended check definition exactly as stated in DDR-0014's "Amendment,
  2026-09-05" section (spec-of-record) — no reintroduction of a domain-crossing precondition in
  any requirement, detection branch, or acceptance criterion.
- Must: reuse `first-turn-contract-enforcement`'s wrapper shape (bounded timeout, fail-open on
  internal error, append-only track-record log) rather than redesigning that infrastructure.
- Must: ship `log_only` as the default/initial mode in every installation; `blocking` is opt-in
  and per-repo, never bundled into initial install.
- Must: every predetermined constant this sprint's own code introduces carries a citable
  precedent or an explicit PROVISIONAL tag with a named owner — no exception for the hook's own
  artifacts, per this repo's Decision Discipline.
- Must not: implement or imply a soundness/correctness judgment on existing citations within this
  check's logic or output.
- Must not: expand this sprint's scope to include retrofit work into other repos.
- Assumes: the architecture-time detection-rule comparison (AD-1) will converge on exactly one
  concrete rule before implementation begins — if it cannot, that is a HALT condition for
  02-ARCHITECTURE.md, not something requirements can pre-decide.
- Assumes: the existing PROVISIONAL-tag convention (this repo's Decision Discipline) is reusable
  as the citation format without modification — flagged as not yet confirmed sufficient
  (INTAKE.md item 3); if architecture finds it insufficient, that is an architecture-level
  finding, not a requirements gap.
