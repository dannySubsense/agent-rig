# Intake Spec: Signpost→Pillar Propagation

**Status**: APPROVED (2026-08-08, Danny)
**Author**: wright
**Date**: 2026-08-07
**DDR**: Extends DDR-004 (`docs/specs/agent-rig-ddrs/DDR-004-*`, status DRAFT, Frank PASS attempt 3 both layers FIRM, code-merged unpushed at 0784d2c). This Intake does not re-litigate DDR-004's concept; it scopes the work to (a) actually propagate it beyond agent-rig and (b) fold in concrete mechanisms surfaced independently by another project since DDR-004 was gated.

**Amendment, 2026-08-21 (Danny/Wright, live in-session — pilot site correction). APPROVED by Danny 2026-08-21.** This document's original text (below, unedited) names department-os as the proven "prove in one project" pilot. That is now stale and was verified wrong this session, not merely reworded: `department-os` on `main` has none of the mechanism live — the probe scripts and `.claude/settings.json` wiring exist only on an unmerged branch (`session-start-hook`), and that branch carries the older, unlabeled `session_probe.py`, with no Stop-hook contract enforcement at all. Meanwhile **agent-rig itself** has both halves merged to `main`, wired, and live-firing: `scripts/session_queue_probe.py` (SessionStart, Signpost/Pillar-labeled injection) plus `.claude/hooks/first-turn-contract.sh` → `scripts/first_turn_contract_probe.py` (Stop, mechanically enforces label order/presence/tool-call backing). Verified against the live track record (`docs/tooling/first-turn-contract-track-record.jsonl`), which shows real blocks — not just fixtures — including a genuine C3 violation caught 2026-08-18. **The soak/pilot site is realigned to agent-rig, effective this session.** Every reference below to department-os as the proven pilot (What Is Missing §7, AC bullets under "Piloted and live-verified... in department-os" and "The department-os hook built 2026-08-07... should be the actual reference implementation") should be read as superseded by this amendment: agent-rig's `session_queue_probe.py` + `first_turn_contract_probe.py` pair is the reference implementation and the proof site, not department-os's unmerged branch. Retrofit-roster projects (§7's target list) are downstream of *this* repo's artifact, not department-os's.

---

## Problem Statement

DDR-004 established the "signpost, not pillar" concept and proved the core mechanism (SessionStart hook → context injection, live on VM101) — but it has never left agent-rig. Confirmed directly this session (`grep -il "signpost\|pillar"` against `~/.claude/commands/new-project.md`, `~/.claude/templates/HOMELAB-CLAUDE.md.template`, `~/.claude/templates/MACHINE-SETUP.md.template`): zero matches. Trigger: Danny started a new project, asked the new agent about the protocol, and it had no idea what he meant — the mechanism is real but confined to one repo.

This is the same failure shape alpha's handoff report (`/home/d-tuned/market_data/docs/reports/HANDOFF-2026-08-07-verify-before-assert-what-actually-works.md`) names in their own project: their DDR-0009 is "PROPOSED/QUEUED... a plan, not a mechanism," never installed. Two independent projects converged on the same lesson: a doctrine that exists only as a document in one repo is a signpost pointing at nothing, and copying an unfinished plan into a second repo just duplicates the gap instead of closing it.

Separately, alpha's report — read and verified in full this session — extends DDR-004's scope. DDR-004 specified the probe-before-memory ordering mechanism. Alpha's four real incidents (2026-06-29 through 2026-08-07, one costing 17 days and a burned execution window) show that mechanism alone is necessary but not sufficient: the same prose rule was actively cited mid-session and still violated. Alpha's report supplies additional mechanisms not in DDR-004's original scope (see below).

---

## What Exists Today

- **DDR-004** (agent-rig): SessionStart ground-truth probe concept + hook substrate, proven live on VM101. Frank-gated PASS, both layers firm. Not yet spec'd (`/spec-start` was the queued next step from the 2026-07-21 session), not propagated anywhere.
- **`session_probe.py`** (market-data, `alpha`): the reference implementation DDR-004 was designed to generalize from. Runs before memory loads; ~3s; prints git/origin/table-freshness/recent-runs.
- **`~/.claude/commands/new-project.md`**, **`HOMELAB-CLAUDE.md.template`**, **`MACHINE-SETUP.md.template`**: bootstrap artifacts for every new homelab project. Verified this session: none reference signpost/pillar, probe-before-memory, or any of the mechanisms below.
- **Agent-rig's own Session Start Behaviour** (this repo's `CLAUDE.md`): the 3-check pattern (LORE / Switchboard / git) already exists here, and per DDR-INDEX backlog item ("Template tier: promote the 3-check session-start block," 2026-07-20, beta/gaplens-SEC) is already queued for template promotion but not yet done. This sprint should not duplicate that backlog item — coordinate/merge with it.
- **Alpha's handoff report** (`market_data/docs/reports/HANDOFF-2026-08-07-*.md`, DRAFT, unreviewed, self-flagged for independent review): supplies mechanisms DDR-004 does not currently cover — see "What Is Missing" below. Verified by direct read this session; not yet reviewed by Frank or Wright per the report's own request.
- **Related backlog item** (DDR-INDEX line 25, 2026-07-21, alpha/market-data thread `gaplens-prevention`): "Prevention layer: gap-lens pre-checks at the DOER + DISPATCHER layer, not just the checker" — overlaps substantially with alpha's §2.1 "map not route" briefing convention below. That backlog item frames it as prevention (stopping a bad assumption from being seeded); this Intake's scope is closer to propagation + detection tooling. Needs reconciling in architecture, not duplicating as two DDRs.

---

## What Is Missing

1. **DDR-004's own probe mechanism, propagated.** A `session_probe.py`-equivalent, generalized (not market-data-specific), scaffolded into `/new-project` and retrofittable into existing projects, with an explicit instruction that it runs before any memory/doc is consulted.
2. **Map-not-route checker-briefing convention** (alpha §2.1) — not in DDR-004's original scope. A briefing template supplying objective + architecture + where things live + what is claimed, structurally omitting the author's own checklist/method/suspicions. Alpha's highest-yield item, zero cost, caught a real defect (F1, live-vs-repo deployment gap) that a same-checklist briefing would have missed. Overlaps DDR-INDEX backlog item 25 — reconcile scope, don't duplicate.
3. **`assert_*.py` fail-closed convention** (alpha §2.2) for load-bearing couplings — non-zero exit, refuses to pass on indeterminate input. Not in DDR-004.
4. **Capture schema addition**: `Verification:` / `Re-verify with:` lines required on durable LORE captures (alpha §2.4). Not in DDR-004 — DDR-004 covers session-start reading, not capture-writing discipline.
5. **Silent-failure sentinel/observability pattern** (alpha §4): success and failure must produce different bytes; a signal nobody reads is not a control (alpha's F3 catch — writing a sentinel isn't enough if nothing consumes it).
6. **An "assumed vs verified" handoff marker** (alpha §5 item 5) — explicitly flagged by alpha as still-unclosed, cross-referencing the same `gaplens-prevention` thread as DDR-INDEX backlog item 25.
7. **Retrofit slice for existing projects** (2026-08-08, Danny; refined in Interview 2026-08-08 — see `INTERVIEW.md`) — department-os is now the "prove in one project" case alpha's §6 calls for: **[STALE — see 2026-08-21 amendment above. department-os's mechanism is unmerged/unlive; agent-rig is the actual proven pilot.]** working probe hook, a live incident (masking of mandatory LORE priming), the fix, and the Signpost/Pillar labeling convention, all live-verified via tool-call trace. Once this sprint's `new-project`-facing artifacts are finalized through architecture (not before — retrofitting off a pre-architecture version risks shipping N hand-copied variants instead of one canonical artifact, the exact fragmentation this sprint exists to fix), add an explicit forge-phase slice that retrofits the finalized reference implementation into existing projects.

   **This is a full-replacement cutover, not indefinite coexistence** — existing project-local probe-style variants (Cairn's Major Tom variant, beta/gaplens-SEC's) are meant to be replaced by the canonical implementation, not left running alongside it. **Not a uniform sweep**: each project's blast radius (doc references, existing script call-sites, project-specific variants) is individually evaluated before its own cutover — no one-size-fits-all propagation. Sanitization must be thorough, not additive-only (stale references left behind across docs is the specific failure mode to avoid, same shape as the spec-forge-cadence-refactor sprint's `.claude` global sweep requirement).

   **Ownership per project:** each project's own resident agent (Ledger, alpha, beta, Cairn, etc.) performs its own repo's audit/sanitization/cutover — not a centralized sweep by Wright/agent-rig. **Verification per project:** each project's cutover gets its own independently dispatched, unbriefed Frank gate (map-not-route — Frank receives objective/architecture, never the resident agent's own audit checklist) before that project's cutover is called done. agent-rig's own sprint-level Frank gate does not substitute for this — each cutover is its own checkable unit.

   **Failure mode for the probe itself:** fail loud. If the probe hook errors (e.g. git command fails, LORE gateway unreachable), inject the error itself into `additionalContext` so the agent sees it explicitly, rather than degrading silently — matches DDR-004 §6's stated bias against silent skip.

   Target list — DDR-INDEX's existing Decision Discipline backfill roster, reused rather than re-derived: `market_data`, `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore` (`api-doc-scraper` also on that list but flagged there for a separate stale-reference fix, not necessarily in scope here).

---

## Constraints

- Do not propagate DDR-0009-style unfinished plans. Per alpha's own retrofit ranking (§6), items 1–3 below are zero/low-cost practice-and-schema changes with no engineering dependency; items 4–6 are medium-to-high effort and alpha explicitly recommends proving them in one project before propagating further. This sprint should ship 1–3 broadly and treat 4–6 as designed-but-piloted-in-one-place-first, not shipped everywhere simultaneously.
- Must reconcile with, not duplicate, two existing DDR-INDEX backlog items: "promote the 3-check session-start block" (2026-07-20) and "prevention layer: gap-lens pre-checks at doer+dispatcher" (2026-07-21). Architecture phase decides whether these fold into this sprint or stay separate — do not silently absorb scope without saying so.
- Alpha's report is DRAFT/unreviewed and self-flagged for independent review (Frank or Wright) before being treated as settled guidance. This Intake treats it as a strong, verified-provenance input — not yet as ratified doctrine. Frank review of the report itself (not just this sprint's spec) may be a prerequisite gate, not just this sprint's own spec-gate.
- Per this repo's Decision Discipline: every predetermined number (e.g. probe runtime budget, interview-question caps if any apply here) needs a citable precedent or PROVISIONAL tag — alpha's report already cites concrete precedents (~3s probe runtime, 4 incidents, 17-day detection latency) which should carry forward, not be re-derived from nothing.
- Manual-push-only stays in force; this sprint's commits don't auto-push.

---

## Acceptance Criteria (intake-level — spec team to formalize)

- [ ] `new-project` command/template scaffolds a generalized ground-truth probe, wired to run before any memory/doc consultation
- [ ] Session Start Behaviour requires the first-turn state summary to be explicitly labeled **Signpost:** (unverified LORE/memory claims) vs. **Pillar:** (what was independently checked this session, by what method) — never blended into one undifferentiated status report. Piloted and live-verified twice in department-os 2026-08-07 (real headless sessions, tool-call traced): caught an unprompted self-correction (agent flagged "2 commits ahead of origin" as contradicting a stale signpost claim of "everything pushed") and correctly withheld unverified claims (repo visibility) rather than asserting them. Ship this pattern first — it is now proven, not hypothetical, and is the cheapest item in this whole list. **[STALE — see 2026-08-21 amendment above. The current live proof is agent-rig's own `session_queue_probe.py` + Stop-hook contract pair, not this department-os pilot.]**
- [ ] Any probe-hook's injected context is explicitly self-disclaiming — states plainly that it is NOT memory/LORE priming and does not satisfy that separate requirement, with a directive naming the still-pending step. Required because of a live incident this session (LORE capture `312c594f`, department-os): an earlier, undisclaimed probe-hook version caused the agent to skip mandatory LORE priming twice, having pattern-matched "context already loaded" from the probe's own framing. Verify by tool-call trace (`--output-format stream-json`, grep for the actual `search_knowledge` invocation), never by response-text plausibility alone — the same incident showed plausible-sounding text can mask a missing tool call.
- [ ] Map-not-route briefing convention is a documented, checkable pattern in the propagated templates — reconciled explicitly against DDR-INDEX backlog item 25, not duplicated
- [ ] LORE capture guidance (this repo's CLAUDE.md Capture Behaviour section, and/or a template equivalent) requires `Verification:`/`Re-verify with:` lines on durable captures
- [ ] `assert_*.py` fail-closed convention is documented with a worked example (alpha's `assert_gate_date_coupling.py` as reference), scoped to "when a coupling is known," not mandated everywhere
- [ ] Sentinel/observability pattern is documented with the "success and failure must produce different bytes" principle and alpha's F3 lesson (a signal nobody reads is not a control) stated explicitly
- [ ] Alpha's handoff report receives the independent review it requests (Frank and/or Wright) before its recommendations are cited as settled in the propagated artifacts
- [ ] DDR-004's proven *capability* (SessionStart hook→context-injection, confirmed live on VM101) is reused, not re-litigated — note the VM101 test itself was a throwaway, torn down after proving the capability, so there is no surviving hook artifact from it to copy. The department-os hook built 2026-08-07 (`.claude/hooks/session-start-probe.sh`) is the first real reusable artifact and should be the actual reference implementation this sprint generalizes from, per this repo's own Decision Discipline. **[STALE — see 2026-08-21 amendment above. `department-os/.claude/hooks/session-start-probe.sh` exists only on an unmerged branch, no Stop-hook enforcement. The actual reference implementation is agent-rig's merged, live pair: `scripts/session_queue_probe.py` + `.claude/hooks/first-turn-contract.sh`/`scripts/first_turn_contract_probe.py`.]**
- [ ] Retrofit-to-existing-projects ordering matches alpha's yield ranking (§6): practice-only items first, unproven-mechanism items last
- [ ] No mechanism ships into `new-project`/templates in a DDR-0009-like unfinished state — each propagated item is either fully working or explicitly marked pilot-only with a named owner

---

## What the Spec Team Needs to Decide

1. Does this sprint fold in DDR-004's own `/spec-start` (still queued, never started), or does DDR-004 spec separately first and this sprint consumes its output? Given DDR-004 is the probe half and this Intake is probe-plus-five-more-mechanisms, running them as one combined spec avoids re-doing the probe architecture twice — but risks scope bloat. Recommend combining, given DDR-004's own next step was already "/spec-start" and nothing has changed structurally since — but this needs Danny's call.
2. Reconciliation with DDR-INDEX backlog items 25 (prevention layer) and the 3-check session-start promotion — separate DDRs, or absorbed here? Recommend absorbing the 3-check promotion (small, already-drafted-elsewhere) and keeping the prevention-layer item separate (it's framed as doer-layer prevention, a different architectural surface than propagation/detection tooling covered here) — Danny's call.
3. Does alpha's report get its independent review (Frank/Wright) as a gate before this Intake is approved, or in parallel during architecture? Recommend in parallel — the report's core claims (DDR-0009 status, script existence) were already filesystem-verified by alpha per their Provenance section, and this Intake's own scope doesn't depend on unverified parts of the report.

---

## Sequencing

1. Danny reviews and approves (or sends back) this INTAKE.
2. Resolve open question 1 (fold DDR-004's `/spec-start` in or run separately) before Interview.
3. Interview (inline, per this repo's standard cadence).
4. `/spec-start` → Frank binding spec-gate → human approval → `/forge-start`.

**Next action**: Danny approves or sends back this INTAKE.
