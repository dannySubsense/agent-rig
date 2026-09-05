# Requirements: Unsourced-Threshold Provenance Hook

## Summary
A `PreToolUse` hook (`Edit`/`Write`), extending the existing, Frank-forge-gate-PASSED incumbent
`domain-boundary-provenance` hook (`.claude/hooks/domain-boundary-provenance.sh` +
`scripts/domain_boundary_provenance_probe.py`, LOCKED spec
`docs/tooling/domain-boundary-provenance-hook.md`) rather than a new hook, that flags any numeric
or boolean literal used in code as a threshold, cap, limit, cutoff, retry count, or budget when it
lacks, at or adjacent to its definition, a citation, a named-owner `PROVISIONAL — unvalidated`
marker, or removal — regardless of whether the value was defined locally or crossed an ownership
boundary. Per DDR-0014's 2026-09-05 amendment (spec-of-record), the domain-crossing precondition
is dropped entirely; it is one flagged case among all threshold-shaped literals, not a trigger
condition. The incumbent's existing manifest-gated cross-domain pass is left untouched — this
sprint adds a new, additive same-file/local-threshold detection pass composed into the same
wrapper/probe invocation, per `02-ARCHITECTURE.md` §1–§3. This sprint builds the hook in agent-rig
only; retrofit into `gap-lens-dilution-filter` or other repos is separate follow-on work
(Interview Q1).

## User Stories

**US-1**
As a repo maintainer running Claude Code sessions,
I want a `PreToolUse` hook (composed into the incumbent domain-boundary-provenance hook's existing
invocation) that scans proposed `Edit`/`Write` content for threshold-shaped literals lacking a
citation, PROVISIONAL tag, or removal,
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
I want the new local-threshold pass to fail open on any internal error and log to the same
append-only track-record log the incumbent already writes to, consistent with the incumbent
domain-boundary-provenance hook's wrapper shape (which is itself a reuse of
`first-turn-contract-enforcement`'s wrapper shape — a two-generations-removed reuse, not a direct
one),
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
- [ ] Given a code change introducing a numeric or boolean literal that matches the detection rule
      for "threshold-shaped" (rule finalized in `02-ARCHITECTURE.md` §2 — two shape-based
      syntactic contexts only, Python-only, no name-gating; see that section for the exact
      contexts and exclusions), when the hook runs, then the hook flags the literal if no citation,
      PROVISIONAL-with-owner tag, or evidence of removal is present at or adjacent to its
      definition.
- [ ] Given a threshold-shaped literal that already carries a citation or a PROVISIONAL tag
      naming a human owner, when the hook runs, then it does not flag that literal.
- [ ] Given a literal that does not match the threshold-shaped detection rule (e.g. a loop bound
      or array index, per Architecture §2's own exclusions), when the hook runs, then it is not
      flagged.
- [ ] The new local-threshold detection pass fires identically regardless of whether the literal
      was defined locally in the same file/module or read/imported from elsewhere — no code path
      in this pass conditions flagging on a domain-crossing or import check. This applies only to
      the new local-threshold pass; the incumbent's existing manifest-gated cross-domain pass is
      unmodified and continues to run its own, separate, domain-crossing-based check unchanged
      (per `02-ARCHITECTURE.md` §1, §3).

**US-2**
- [ ] Given the hook is newly wired live in this repo, when it runs, then it defaults to
      `log_only` mode (writes findings to the track-record log as `decision: "flag"`, does not
      block the session) — this mode gate applies to both the incumbent's cross-domain pass and
      the new local-threshold pass identically, since neither has run against live traffic before
      this sprint.
- [ ] Given a repo owner has explicitly configured the hook to `blocking` mode, when it runs and
      finds an unresolved flagged literal (from either pass), then the Edit/Write tool call is
      denied (`decision: "deny"`, the same `PreToolUse` block payload the incumbent's cross-domain
      pass already uses — not a session-ending action; this hook has no `Stop` trigger).
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

## Detection Rule Pointer

The detection rule for "threshold-shaped literal" (previously an open architecture-level design
question in this document) is finalized in `02-ARCHITECTURE.md` §2 (revised per benchmark audit,
2026-09-05): two shape-based syntactic contexts only (comparison operand, slice/truncation
argument) — the name-gated default-kwarg/assignment context was removed, measured to produce both
false negatives (8/10 candidate words never fire in this repo) and false positives (substring
matches inside unrelated identifiers). Detection is Python-only, AST-based, with explicit
exclusions: `range()` bounds (a Python language fact, cited to the language reference, not a
benchmarked value), non-slice indexing, test/fixture paths, and the literal set `{0, 1, -1, 2}`
(NOT YET BENCHMARKED — ships with a fully-specified executable validation plan in Architecture §2;
not to be treated as validated until that plan runs). This document does not restate that rule's
substance — see Architecture §2 for the authoritative definition and disposition of every
constant.

The incumbent's existing manifest-gated cross-domain check (schema, trigger, scan surface,
`DOMAIN-BOUNDARY:` marker) is untouched by this sprint — see `02-ARCHITECTURE.md` §1. Only the new
same-file/local-threshold detection pass is new work.

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Literal is a loop bound, array index, or other non-threshold numeric use | Not flagged — excluded by the detection rule's own scope (threshold/cap/limit/cutoff/retry-count/budget only, per Architecture §2's exclusions) |
| Literal already has a citation, but the citation link/reference is broken or wrong | Not flagged by this hook — correctness of citations is `benchmark`'s/Frank's/a human's job, not this check's |
| Literal is defined in the same file/module with no import involved | Flagged the same as any cross-boundary literal if it otherwise matches the new local-threshold detection rule — domain-crossing is not a precondition for this new pass |
| Hook's internal scan exceeds its timeout or throws an exception | Fail open — session not blocked, error appended to track-record log |
| Repo has hook newly wired live with pre-existing unlabeled magic numbers throughout | All matching literals flagged in `log_only` mode; no blocking until repo owner explicitly promotes to `blocking` after triage |
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
- NOT: enforcing a hard latency/performance SLA on the scan — best-effort, same posture as the
  incumbent hook's own wrapper (Interview Q3).
- NOT: replacing, retiring, or redesigning the incumbent `domain-boundary-provenance` hook or its
  LOCKED spec doc (`docs/tooling/domain-boundary-provenance-hook.md`) — the incumbent's
  manifest-gated cross-domain check, schema, trigger surface, and marker are extended in-place
  (same wrapper/probe file, composed invocation), not replaced or retired; no new/second hook is
  created.
- Deferred: any survey of a full retrofit roster beyond `gap-lens-dilution-filter` as "obvious
  first target" — that survey, if needed, is follow-on work per the existing retrofit-roster
  pattern (`signpost-pillar-propagation`).

## Constraints

- Must: implement the amended check definition exactly as stated in DDR-0014's "Amendment,
  2026-09-05" section (spec-of-record) — no reintroduction of a domain-crossing precondition in
  any requirement, detection branch, or acceptance criterion of the new local-threshold pass.
- Must: extend the incumbent `domain-boundary-provenance` hook's existing wrapper/probe files in
  place (`.claude/hooks/domain-boundary-provenance.sh`,
  `scripts/domain_boundary_provenance_probe.py`) rather than building a new hook — this is a
  two-generations-removed reuse of `first-turn-contract-enforcement`'s wrapper shape (bounded
  timeout, fail-open on internal error, append-only track-record log), inherited via the
  incumbent hook, which already reused that shape directly; this sprint reuses it a second time,
  through the incumbent, not from `first-turn-contract.sh` itself.
- Must: leave the incumbent's manifest-gated cross-domain check (schema, trigger, scan surface,
  `DOMAIN-BOUNDARY:` marker, decision logic) untouched — only the new same-file/local-threshold
  detection pass is new work; the cross-domain pass is reused as-is per `02-ARCHITECTURE.md` §1.
- Must: ship `log_only` as the default/initial mode in every installation; `blocking` is opt-in
  and per-repo, never bundled into initial install. This applies to both the incumbent's
  cross-domain pass and the new local-threshold pass, since neither has run against live traffic
  before this sprint.
- Must: every predetermined constant this sprint's own code introduces carries a citable
  precedent or an explicit PROVISIONAL tag with a named owner — no exception for the hook's own
  artifacts, per this repo's Decision Discipline.
- Must not: implement or imply a soundness/correctness judgment on existing citations within this
  check's logic or output.
- Must not: expand this sprint's scope to include retrofit work into other repos.
- Must not: create a new/second hook registration or process for the local-threshold check — it
  composes into the incumbent's single `PreToolUse` invocation (`02-ARCHITECTURE.md` §3).
- Assumes: the existing PROVISIONAL-tag convention (this repo's Decision Discipline) is reusable
  as part of the citation format — `02-ARCHITECTURE.md` §4 resolves this by introducing a new
  `THRESHOLD-PROVENANCE:` marker (distinct from the incumbent's `DOMAIN-BOUNDARY:` and from bare
  `PROVISIONAL`) that recognizes a named-owner PROVISIONAL tag as one of its satisfying forms; this
  is an architecture-level finding, not a requirements gap.
</content>
