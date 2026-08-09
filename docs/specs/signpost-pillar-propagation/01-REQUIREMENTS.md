# Requirements: Signpost→Pillar Propagation

## Summary
Propagate DDR-004's session-start ground-truth-probe concept, and five additional mechanisms surfaced by alpha's market-data handoff report, out of agent-rig into the homelab's shared bootstrap artifacts (`new-project`, `HOMELAB-CLAUDE.md.template`) and, once finalized, retrofit them into a named roster of existing projects — replacing project-local drifting variants rather than coexisting with them.

## User Stories

### US-1: Generalized probe hook scaffolded into new projects
As a homelab agent starting a brand-new project,
I want a generalized ground-truth probe hook scaffolded automatically by `/new-project`,
so that every new project gets the SessionStart-verification capability DDR-004 proved, without hand-copying it.

### US-2: Probe runs before memory/doc consultation, fails loud
As an agent in a probed session,
I want the probe to run before any memory/doc is consulted, and to inject its own error into `additionalContext` if it fails,
so that I never silently skip ground-truth verification or proceed on a broken probe without knowing it.

### US-3: Probe hook is self-disclaiming
As an agent in a probed session,
I want the probe's injected context to explicitly state it is NOT LORE/memory priming and to name the still-pending priming step,
so that I don't pattern-match "context already loaded" and skip mandatory LORE priming (the department-os incident, LORE capture `312c594f`).

### US-4: Signpost/Pillar labeled session-start summary
As an agent reporting session-start state,
I want my first-turn summary to separate **Signpost:** (unverified inherited claims) from **Pillar:** (independently checked this session, with method named),
so that stale or unverified claims are never asserted as if they were checked (proven twice live in department-os).

### US-5: Map-not-route briefing convention
As an agent briefing an auditor or reviewer,
I want a documented, checkable convention that supplies objective + architecture + what's claimed while structurally omitting my own checklist/method,
so that the reviewer isn't capped at my own blind spots (reconciled against DDR-INDEX backlog item 25, not duplicated).

### US-6: Verification lines required on durable captures
As an agent writing a durable LORE capture,
I want `Verification:` / `Re-verify with:` lines required by capture guidance,
so that future sessions know how to re-check a claim rather than trusting it indefinitely.

### US-7: Fail-closed assert convention for load-bearing couplings
As an agent relying on a known coupling between two components,
I want a documented `assert_*.py` fail-closed pattern (non-zero exit, refuses to pass on indeterminate input),
so that a broken coupling is caught immediately rather than silently tolerated.

### US-8: Sentinel/observability pattern documented
As an agent designing a control that depends on a signal,
I want the "success and failure must produce different bytes" principle documented, with alpha's F3 lesson (a signal nobody reads is not a control) stated explicitly,
so that I don't build observability that nothing consumes.

### US-9: Alpha's report independently reviewed before being cited as settled
As the sprint's producer,
I want alpha's DRAFT/unreviewed handoff report to receive independent review by Frank (not by me, the sprint's producer — I authored the specs that cite the report, so doer≠checker requires a non-producer reviewer),
so that its recommendations aren't propagated into shared artifacts as settled doctrine before being checked.

### US-10: Per-project retrofit with independent Frank gate
As a resident agent of an existing project on the retrofit roster (`market_data`, `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore`),
I want to audit my own project's blast radius, cut over from any project-local probe variant to the canonical implementation, and pass my own independently dispatched, unbriefed (map-not-route) Frank gate,
so that my project's cutover is verified as its own checkable unit, not assumed correct because the sprint-level spec passed once.

## Acceptance Criteria

### US-1
- [ ] Given a new project scaffolded via `/new-project`, when scaffolding completes, then a generalized (non-market-data-specific) ground-truth probe hook is present and wired into SessionStart.
- [ ] The reference implementation generalized is department-os's `.claude/hooks/session-start-probe.sh` (2026-08-07), not the torn-down VM101 throwaway.

### US-2
- [ ] Given a session start, when the probe hook fires, then it executes before any memory/doc-loading step in the session-start sequence.
- [ ] Given the probe hook errors (e.g., git command fails, LORE gateway unreachable), when the error occurs, then the literal error is injected into `additionalContext` (e.g., "probe failed: <error>") rather than the hook failing silently.

### US-3
- [ ] Given the probe hook injects context, when that context is read, then it contains an explicit statement that it is not LORE/memory priming and does not satisfy that requirement.
- [ ] The injected context names the still-pending priming step explicitly (not implied).

### US-4
- [ ] Given a first-turn session-start summary, when state is reported, then every claim is labeled either **Signpost:** or **Pillar:**, never left unlabeled or blended.
- [ ] **Pillar:**-labeled claims state the verification method used this session.
- [ ] Documented as a checkable requirement in the propagated Session Start Behaviour template (not just department-os-local).

### US-5
- [ ] Given a checker/reviewer briefing is produced under this convention, when inspected, then it contains objective, architecture, and what's-claimed sections.
- [ ] Given the same briefing, when inspected, then it structurally omits the briefing author's own checklist/method/suspicions.
- [ ] Scope is explicitly reconciled against DDR-INDEX backlog item 25 in the architecture doc — documented as either folded-in or kept-separate, not silently absorbed.

### US-6
- [ ] Given a durable LORE capture is written per this repo's (or a template's) Capture Behaviour guidance, when the capture is inspected, then it contains a `Verification:` line and a `Re-verify with:` line.
- [ ] "Durable capture" is defined concretely as: any LORE capture whose `documentType` is one of {`decision`, `discovery`, `halt`, `review`} and whose `status` is `locked` — as distinct from ephemeral/draft captures (`status: draft`, or `documentType` values not in that set), which are not required to carry `Verification:`/`Re-verify with:` lines.
- [ ] Guidance is present in this repo's CLAUDE.md Capture Behaviour section and/or a propagated template equivalent.

### US-7
- [ ] Given a documented load-bearing coupling, when an `assert_*.py` script for it is written per this convention, then it exits non-zero on any indeterminate input rather than passing.
- [ ] A worked example exists, referencing alpha's `assert_gate_date_coupling.py` as the pattern.
- [ ] Documentation states the convention applies "when a coupling is known," not as a blanket mandate on all code.

### US-8
- [ ] Given the sentinel/observability pattern doc, when read, then it states the "success and failure must produce different bytes" principle explicitly.
- [ ] The doc states alpha's F3 lesson (a signal nobody reads is not a control) explicitly, not merely implied.

### US-9
- [ ] Given alpha's handoff report, when this sprint's propagated artifacts cite its recommendations, then the report has received independent review by Frank beforehand — not by Wright (the sprint's producer, who authored the specs citing the report) and not by this document's own reviewer.
- [ ] The review is recorded in its own artifact, `ALPHA-REPORT-REVIEW.md`, distinct from and not satisfied by `05-REVIEW.md` (this sprint's spec-completeness review, which reviews the requirements/architecture/roadmap doc set, not alpha's report) — the two artifacts must not collide.
- [ ] Review outcome (pass/concerns/rejected items) is recorded in `ALPHA-REPORT-REVIEW.md` before the report's items are treated as settled guidance in shipped artifacts.

### US-10
- [ ] Given a project on the retrofit roster, when its cutover is performed, then the audit/sanitization is performed by that project's own resident agent, not a centralized agent-rig sweep.
- [ ] Given a project's cutover, when it is evaluated for scope, then its own blast radius (doc references, script call-sites, project-specific variants) is individually assessed — no uniform, one-size-fits-all sweep applied.
- [ ] Given a project's cutover is claimed complete, when checked, then any prior project-local probe variant (e.g., Cairn's Major Tom variant, beta/gaplens-SEC's) has been removed, not left coexisting.
- [ ] Given a project's cutover, when it is called done, then it has passed its own independently dispatched, unbriefed (map-not-route) Frank gate — the sprint-level agent-rig Frank gate does not substitute.
- [ ] Given a project's cutover, when verified, then verification is by live tool-call trace (e.g., `--output-format stream-json`, grep for actual tool invocation), not by response-text plausibility alone.
- [ ] Retrofit ordering across the roster follows alpha's §6 yield ranking, in three tiers: (1) practice-only items — Signpost/Pillar labeling (US-4), map-not-route briefing (US-5), capture schema (US-6) — roll out to every roster project first, at zero engineering cost, once each resident agent runs its own audit; (2) probe-hook rollout (US-1/US-2/US-3) is piloted in exactly one retrofit-roster project before broader propagation; (3) assert-convention and sentinel-pattern documentation (US-7, US-8) propagate to all roster projects alongside tier 1, but *application* — writing an actual `assert_*.py` for a project's own known coupling — happens per-project, on that project's own timeline, only "when a coupling is known."

### Cross-cutting
- [ ] No mechanism in this sprint ships into `new-project`/templates in a DDR-0009-like "documented but not installed" state: each item is either fully working and live-verified by tool-call trace, or explicitly marked pilot-only with a named owner.
- [ ] Every predetermined number carried into propagated artifacts (e.g., ~3s probe runtime budget, 4-incidents/17-day-latency precedent) is sourced to alpha's report's citations, not re-derived from nothing, or is PROVISIONAL-tagged with a named owner.
- [ ] **Deployment is verified, not asserted.** Every edited artifact (commands, templates) that this sprint modifies in agent-rig (source-of-record) is actually synced to `~/.claude/{commands,templates}/`, per the DDR-014 deploy pattern, and that sync is verified by diffing the deployed file against the agent-rig source — a byte-identical (or intentionally-reconciled) match, not a claim that the sync happened. This closes the exact "documented but not installed" failure mode (DDR-0009) this sprint exists to prevent.
- [ ] **Sprint forge-phase closability.** The forge phase is closable when Slices 1-9 are complete and the retrofit pilot (Slice 10, `market_data`) reaches its own PASS on an independently dispatched, unbriefed Frank gate. The remaining roster items (Slices 11/12, covering `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore`) are explicitly not blocking — they track as ongoing, per-project work owned by each project's own resident agent, and the sprint is called done without waiting on full roster completion.
- [ ] **No implied enforcement where none exists (Frank's `ALPHA-REPORT-REVIEW.md` caveat 1).** No artifact propagated by this sprint presents hook-based/automated enforcement (e.g., DDR-0009-style) as an existing/live mechanism where it is not actually installed and verified. The practice-only conventions this sprint propagates — Signpost/Pillar labeling (US-4), map-not-route briefing (US-5), capture schema (US-6), assert-convention documentation (US-7), sentinel-pattern documentation (US-8) — are explicitly labeled as conventions/practices to be followed, never implied to be automatically or mechanically enforced.
- [ ] **§2.5 cited as heuristic, not established pattern (Frank's `ALPHA-REPORT-REVIEW.md` caveat 2).** Any propagated artifact that cites alpha's report §2.5 ("repetition as a diagnostic instrument") labels it explicitly as a heuristic, not an established pattern — N=1, accidental discovery, self-acknowledged by the report itself — and never presents it as a proven technique.

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Probe hook's git command fails | Inject "probe failed: <error>" into `additionalContext`; no silent skip |
| LORE gateway unreachable during probe | Inject the specific unreachability error into `additionalContext`; agent proceeds aware of the gap |
| Agent pattern-matches probe output as memory priming | Prevented by US-3's self-disclaiming text; if it still happens post-mitigation, treated as its own new incident, not proof the mitigation failed on first observation |
| A propagated hook masks priming in a different (non-department-os) repo | No standing ongoing monitor; each retrofit is trace-verified once at cutover time; a later regression is its own new incident |
| Existing project has its own probe-style variant with unknown blast radius | Resident agent performs individual blast-radius audit before cutover; not assumed safe to swap uniformly |
| Session-start summary has no unverifiable claims at all (everything checked) | All claims still explicitly labeled **Pillar:**; omission of **Signpost:** section is acceptable only when genuinely empty, not a default |
| `assert_*.py` convention applied to a coupling that isn't actually load-bearing | Out of convention's stated scope ("when a coupling is known") — not to be mandated blanket-wide |
| Alpha's report review (US-9) surfaces a rejected or unverified recommendation | That item is not propagated into shared artifacts; sprint proceeds with the remaining reviewed items |
| Retrofit roster project (`api-doc-scraper`) flagged for separate stale-reference fix | Explicitly out of this sprint's retrofit scope, per Intake note |
| Deployed artifact under `~/.claude/{commands,templates}/` diverges from agent-rig source at verification time | Deployment AC fails; re-sync from source-of-record before the sprint can claim the artifact deployed |
| Roster items (Slices 11/12) not yet started when Slices 1-9 + pilot PASS | Sprint is still closable; remaining roster items tracked as ongoing, not treated as blocking debt |

## Out of Scope

- NOT: DDR-004's own `/spec-start` re-litigation as a separate spec — per Danny's approved recommendation, this sprint's spec absorbs DDR-004's probe architecture rather than DDR-004 being spec'd twice.
- NOT: A centralized, agent-rig-run sweep across all retrofit-roster projects — each project's own resident agent owns its own audit/cutover.
- NOT: Indefinite coexistence of project-local probe variants alongside the canonical hook — full replacement is the stated goal, not a parallel-running option.
- NOT: A standing/ongoing monitoring system watching for probe-masking regressions after cutover — each retrofit gets one trace-verification at cutover time; regressions are handled as new incidents if/when they occur.
- Deferred: Items 4-6 of the Intake's "What Is Missing" list (capture-schema, assert convention, sentinel pattern, assumed-vs-verified marker) shipping broadly — these are piloted-in-one-place-first per alpha's §6 ranking, not shipped everywhere in this sprint.
- Deferred: `api-doc-scraper`'s stale-reference fix — tracked separately, not bundled into this sprint's retrofit slice.
- Deferred: Resolution of DDR-INDEX backlog item "prevention layer: gap-lens pre-checks at doer+dispatcher" as a folded-in item — Intake's recommendation is to keep it a separate DDR; architecture confirms.
- NOT: Setting a hard numeric probe-runtime-budget ceiling at the requirements stage — left to architecture per Interview Q2, informed by alpha's ~3s precedent.
- NOT: This document defining architecture, hook implementation details, deployment sequencing, or UI/output formatting for the probe or briefing artifacts — those are architecture/roadmap phase responsibilities.
- NOT: Full retrofit-roster completion (Slices 11/12, 7 of 8 non-pilot projects) as a condition of sprint close — see Cross-cutting AC on forge-phase closability.

## Constraints

- Must: Reuse department-os's `.claude/hooks/session-start-probe.sh` (2026-08-07) as the reference implementation to generalize from — not the torn-down VM101 throwaway, which has no surviving artifact.
- Must: Every propagated cutover pass its own independently dispatched, unbriefed (map-not-route) Frank gate before being called done; the sprint-level Frank gate does not substitute.
- Must: Verify claimed-complete states (probe working, priming not skipped, variant removed, artifact deployed) by live tool-call trace or diff, never by response-text plausibility alone.
- Must: Sanitize thoroughly on cutover — remove stale doc/script references, not just add the new artifact alongside old ones.
- Must: US-9's review of alpha's report is performed by Frank, recorded in its own artifact (`ALPHA-REPORT-REVIEW.md`), not by Wright and not folded into `05-REVIEW.md`.
- Must: Practice-only conventions propagated by this sprint (US-4 through US-8) are labeled as conventions/practices, never as automated or hook-enforced mechanisms where no such enforcement exists (per Frank's `ALPHA-REPORT-REVIEW.md` caveat 1).
- Must: Any artifact citing alpha's report §2.5 ("repetition as a diagnostic instrument") labels it a heuristic, not an established pattern (per Frank's `ALPHA-REPORT-REVIEW.md` caveat 2).
- Must not: Ship any mechanism into `new-project`/templates in a "documented but not installed" (DDR-0009-like) state — every edited artifact must be deployed to `~/.claude/{commands,templates}/` and that deployment diff-verified.
- Must not: Apply a uniform, one-size-fits-all propagation script across the retrofit roster — each project's blast radius is individually assessed.
- Must not: Cite alpha's report's recommendations as settled guidance in shipped artifacts before its independent review (US-9, by Frank) completes.
- Assumes: Danny's approval of Intake open question 1 (combining DDR-004's spec into this sprint) holds through architecture — if reversed, probe-hook requirements (US-1, US-2, US-3) would need to be split out.
- Assumes: The retrofit roster (market_data, electric-blue, gap-lens-dilution, gap-lens-dilution-filter, ask-edgar-repo, sonic-store, quant-foundry, runtime/agent-lore) is stable and reused as-is from DDR-INDEX's existing backfill list, not re-derived.
- Assumes: Manual-push-only policy stays in force; no requirement in this document implies auto-push behavior.
