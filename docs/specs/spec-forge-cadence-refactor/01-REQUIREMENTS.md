# Requirements: Spec/Forge Cadence Refactor

**Status**: Draft — extracted from `INTAKE.md` and `INTERVIEW.md` (both FINAL, all decisions locked)
**Author**: requirements-analyst (dispatched by wright)
**Date**: 2026-07-15
**Interview**: Already conducted and closed (`INTERVIEW.md`, 2026-07-15). This document does not re-open it; Step 2 of this skill's own clarifying-interview was intentionally skipped for this run per orchestration instruction.

---

## Summary

`spec-orchestration` and `forge` (vendored as `spec-orchestration-03242026/` and `forge-03252026/`) have three gates that exist in prose but aren't load-bearing: CADENCE/INVARIANTS are read "if exists," nothing checks a finished spec or implementation against a durable project or sprint intent, and Frank's verdict isn't a binding loop condition anywhere. This refactor builds a mandatory Intake gate, a standalone Interview stage (replacing the dead-ceremony embedded interview in `requirements-extraction`), a sprint-local North Star doc, and wires Frank in as a binding, no-exceptions gate (with a two-layer North Star check) for both spec and forge — while trimming Frank's prose to a concrete structural target and propagating the whole framework to every consumer via a `~/.claude` global sweep. Output lands as new dated packages (`spec-orchestration-07152026/`, `forge-07152026/`); the current dated packages are archived as-is, and already-archived `-03132026` packages are untouched.

The "users" of this refactor are the spec/forge orchestration commands, Frank, and Danny as the human gate-holder — there is no end-user-facing UI in this sprint (confirmed, Interview Q2).

---

## User Stories

### US1 — Mandatory Intake Gate
As the spec orchestrator (`spec-start` or successor),
I want to HALT if no approved Intake doc exists for the sprint,
so that no spec sprint proceeds on an ungated, unapproved problem statement.

**Acceptance Criteria**
- [ ] Given a spec sprint invocation with no approved `INTAKE.md` present for that sprint, when `spec-start` (or successor) runs, then it HALTs before generating any downstream doc (Requirements, Architecture, etc.).
- [ ] Given an approved Intake doc exists, `spec-start` proceeds without requiring a DDR — DDR stays optional; Intake is the only mandatory pre-spec gate.
- [ ] This mandatory-Intake rule applies to every project using `spec-orchestration` going forward, not just this sprint's own run — it is a workflow rule change, not a one-off.

### US2 — Standalone Interview Stage
As the spec orchestration doc sequence,
I want a dedicated Interview stage distinct from `requirements-extraction`'s embedded interview,
so that questions the Intake didn't cover reach Danny through a real channel and block on his actual reply, rather than being silently skipped or fabricated.

**Acceptance Criteria**
- [ ] Interview stage exists as its own step/artifact in the doc sequence (not folded into `01-REQUIREMENTS`).
- [ ] Question generation is hybrid: seed questions from a gap-diff against the approved Intake **and** against conversation that already resolved items live (not just the static Intake text), plus adaptive follow-ups when an answer surfaces something new.
- [ ] Stopping rule is loop-until-dry (5-7 as a soft anchor, not a hard bound); the loop stops after 1-2 consecutive exchanges that surface nothing new, and does not pad toward the anchor.
- [ ] Interview questions demonstrably reach Danny and block on his real reply — verified by walkthrough of the actual mechanism (inline orchestrator turn, or subagent HALT-relay-reinvoke), not asserted in prose.
- [ ] If a subagent conducts the Interview, it returns its question list to the orchestrator, which HALTs, relays the real questions to Danny, waits for his actual replies, and re-invokes with those answers appended — silent fabrication is never an acceptable fallback under any design.
- [ ] Interview questions and answers are captured as a durable artifact (e.g. `INTERVIEW.md`), not left to conversation history alone.
- [ ] Danny may pass on participating; when he does, the stand-in reuses whichever model is already conducting the interview (no separate lightweight/fixed-persona model tier), and each stand-in answer is stamped `ASSUMED — Danny did not answer; based on [rationale]`, with `[rationale]` citing the specific industry pattern/framework precedent it rests on — a bare `ASSUMED` flag with no rationale is not acceptable.
- [ ] The Interview question set demonstrates explicit YAGNI pressure (targets generic blind-spot categories — testing/rollback, non-functional constraints, downstream impact, unresolved edge cases — rather than a fixed checklist padded to a count).

### US3 — Retire the Embedded Clarifying Interview
As the `requirements-extraction` skill,
I want Step 2 ("Conduct Clarifying Interview") removed once the dedicated Interview stage (US2) replaces it,
so that the same instruction doesn't exist as dead ceremony in two places.

**Acceptance Criteria**
- [ ] Step 2 is removed from `requirements-extraction/SKILL.md` once the dedicated Interview stage is live and wired into the orchestrator.
- [ ] Until that removal ships, any requirements-extraction pass run under the new orchestration explicitly skips invoking Step 2 rather than silently running it or fabricating answers.

### US4 — Sprint North Star as a Shared Gating Artifact
As the spec orchestration doc sequence,
I want a sprint-local North Star doc authored once, as a standard template alongside Intake/Interview,
so that Frank's spec-gate and forge-gate can both check the same artifact for sprint fidelity without two templates needing to stay in sync.

**Acceptance Criteria**
- [ ] A sprint North Star doc is produced as part of the standard spec-orchestration doc sequence (ahead of or alongside `01-REQUIREMENTS`).
- [ ] Forge's Frank-gate reads that same sprint North Star artifact produced during spec — no separate forge-side template is authored.

### US5 — Frank as the Binding Spec Gate
As the spec orchestrator,
I want Frank's verdict on the finished spec to be a hard, no-exceptions loop condition with a two-layer North Star check,
so that no spec sprint can conditionally pass, silently proceed past a FAIL/HALT, or complete while off-mission at the project level.

**Acceptance Criteria**
- [ ] Frank's spec-gate verdict is enforced as a hard loop condition in the orchestrator, with no manual override path.
- [ ] Frank checks two independent, non-offsetting layers: Layer 1 (sprint North Star — fidelity: did the sprint do what it declared, with no silently skipped gates or promoted-default drift) and Layer 2 (project North Star — relevance: is the sprint's existence in service of the project, or a tangent/scope-creep/YAGNI violation). A Layer 1 PASS never offsets a Layer 2 FAIL, or vice versa.
- [ ] Layer 2 is checked by reading the finished artifact directly against the project North Star document itself — not by trusting the sprint North Star's own self-declared claim of alignment (checking a document's claim about itself with the same document is the SHARED WELL failure).
- [ ] If no project North Star document exists when the sprint reaches Frank's gate, Frank HALTs outright and asks for one to be minted — no interim-oracle fallback, no proceeding without it.
- [ ] Given the project North Star document exists but is status DRAFT, Layer 2 returns a PROVISIONAL PASS (not a HALT); given the document does not exist at all, Layer 2 HALTs as before; a PROVISIONAL PASS is re-run once the project North Star reaches non-DRAFT status. (Ratified by Danny; applies to this sprint's own forge-completion gate, since this sprint's own `docs/NORTH-STAR.md` is currently DRAFT.)
- [ ] The spec-gate loop carries its own independent 3-attempt counter (not a single count shared with forge).
- [ ] At attempt 3, Frank judges convergence (failures shrinking, static, or thrashing across iterations) rather than issuing a routine verdict; if progress looks real the loop continues, if stuck Frank HALTs into deep-diagnosis mode.
- [ ] Frank's deep-diagnosis output carries concrete evidence — which check/issue recurs, what each iteration's diff actually touched, shrinking/static/thrashing classification — not a narrative conclusion alone.
- [ ] The orchestrator independently re-derives Frank's stuck-loop diagnosis from the primary artifacts (actual diffs, check outputs, roadmap state) before surfacing it to Danny, rather than passing through Frank's summary unverified — verified by walkthrough of the actual mechanism, not asserted in prose.
- [ ] If the orchestrator's independent read disagrees with Frank's stuck-loop diagnosis, that disagreement escalates to Danny rather than either side unilaterally resolving it; Frank's PASS/FAIL/HALT on sprint quality stays binding regardless — only the stuck-loop process judgment is contestable.

### US6 — Mandatory CADENCE/INVARIANTS Gate Before Forge
As the forge orchestrator (`forge-start` or successor),
I want to HALT if `docs/CADENCE.md` or `docs/INVARIANTS.md` don't exist,
so that forge never begins implementation delegation without governance docs actually present.

**Acceptance Criteria**
- [ ] `forge-start` (or successor) HALTs if either `CADENCE.md` or `INVARIANTS.md` is missing, before any implementation delegation — replacing the current "if exists" / no-HALT-check behavior for both files equally.
- [ ] Forge cadence changes demonstrate explicit YAGNI pressure — the gate is added without incidental new ceremony.

### US7 — Frank as the Binding Forge Gate
As the forge orchestrator,
I want Frank's verdict on the implementation to be the same hard, no-exceptions loop condition used in spec,
so that forge cannot silently accept work that fails Frank's gate.

**Acceptance Criteria**
- [ ] Frank's forge-gate verdict is enforced as a hard loop condition, same no-exceptions rule as the spec-gate (US5).
- [ ] The forge-gate loop carries its own independent 3-attempt counter, separate from the spec-gate's counter.
- [ ] The same convergence-judgment-at-attempt-3 and deep-diagnosis behavior defined for the spec-gate (US5) applies identically to the forge-gate.

### US8 — Frank's Prose Trim
As Frank (the QC gate agent),
I want my verdict template and mandate prose trimmed to a concrete structural target,
so that fast-moving loops aren't slowed by ceremony while the load-bearing substance is unchanged.

**Acceptance Criteria**
- [ ] Frank's verdict conforms to exactly `{Findings, Why, Verdict, Fix/Next-step}` — Fix/Next-step required only on FAIL/HALT — with no prose outside those four sections (no restated context, hedging preamble, decorative framing, repeated summaries). Verified against a real verdict example, not asserted in prose.
- [ ] Frank's five non-negotiable pre-checks (premise, input, evidence independence, standing authority to widen scope, do-not-cite-isn't-a-stop) survive the trim untouched in substance.
- [ ] Frank's verdict template and mandate prose are measurably shorter than before the trim, with pre-checks/HALT conditions unchanged in substance.
- [ ] Danny personally reviews the `agents/frank.md` diff to confirm pre-check substance is preserved — this review is not delegated to Frank himself, since he is the subject of the change (avoids doer-adjacent-to-checker).

### US9 — Frank Source-to-Dispatch Sync
As the framework maintainer,
I want an explicit sync/redeploy step from `agent-rig/agents/frank.md` (source-of-record) to `~/.claude/agents/frank.md` (global dispatch location),
so that the prose trim actually reaches every live `subagent_type: frank` dispatch, not just the source file.

**Acceptance Criteria**
- [ ] A sync/redeploy step from `agent-rig/agents/frank.md` to `~/.claude/agents/frank.md` is explicit (a named step, not assumed) and is actually run this sprint.
- [ ] The sync is verified by diff (the two files match post-sync), not assumed to match.
- [ ] The redeploy does not change the existing `subagent_type: frank` invocation signature/contract for any existing consumer (gap-lens-dilution-filter, d-code, sonic-store, agent-dashboard).

### US10 — New Dated Packages, Old Ones Archived
As the framework maintainer,
I want this sprint's output to land as newly dated `spec-orchestration`/`forge` package folders with the prior ones archived,
so that the existing dated-snapshot versioning convention is preserved and already-archived packages remain untouched.

**Acceptance Criteria**
- [ ] New packages are created as `spec-orchestration-07152026/` and `forge-07152026/` (MMDDYYYY convention, matching existing string-sortable folder naming).
- [ ] The current `spec-orchestration-03242026/` and `forge-03252026/` packages are archived as-is, matching existing precedent (`archive/spec-orchestration-03132026`, `archive/reference/forge-03132026`).
- [ ] Already-archived `archive/spec-orchestration-03132026` and `archive/reference/forge-03132026` are left untouched by this sprint.

### US11 — Global `~/.claude` Sweep for Propagation
As the shared dispatch surface (`~/.claude`),
I want a thorough sweep replacing old command/skill/agent references with the new framework,
so that every consumer resolving `subagent_type: frank`, `/spec-start`, or `/forge-start` automatically picks up the new gates without per-repo changes.

**Acceptance Criteria**
- [ ] The `~/.claude` global folder sweep is thorough, not additive-only: grep-verified that old command/skill/agent references (stale paths to `spec-orchestration-03242026`/`forge-03252026`, pre-trim Frank prose, pre-Interview-stage skill references) are gone, not just that new references were added.
- [ ] Propagation happens at the `~/.claude` global surface only — no changes are made inside individual consumer repos (gap-lens-dilution-filter, d-code, sonic-store, agent-dashboard) as part of this sprint.
- [ ] The known local divergent copy (`gap-lens-dilution-filter/notebook-orchestration-04182026/agents/frank.md`) is left untouched by this sprint's sweep; reconciliation is explicitly gap-lens's own call, already communicated via the Switchboard message sent to their agent (beta).

### US12 — YAGNI Pressure Across the Refactor
As the sprint deliverable set (Interview template, spec template, forge cadence),
I want explicit, demonstrable YAGNI pressure applied rather than a stated principle alone,
so that none of the new gates or docs accumulate ceremony that repeats the CADENCE/INVARIANTS "optional in practice" failure shape in a new form.

**Acceptance Criteria**
- [ ] Interview question set demonstrates YAGNI pressure (bounded by loop-until-dry, not padded to a fixed count) — see also US2.
- [ ] Spec doc template (Intake / Interview / sprint North Star / Requirements / Architecture / Roadmap / Review, no `03-UI-SPEC` this sprint) demonstrates YAGNI pressure — no doc or section added without a stated purpose tied to a named gap in the Intake's "What Is Missing."
- [ ] Forge cadence changes demonstrate YAGNI pressure — the CADENCE/INVARIANTS gate and Frank binding-loop wiring are added without incidental new ceremony — see also US6.

---

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Danny opts out of participating in the Interview | Same model already conducting the interview generates stand-in answers, each stamped `ASSUMED — Danny did not answer; based on [rationale]` citing a specific precedent; a bare flag with no rationale is rejected. |
| Interview mechanism has no live relay path back to Danny | Orchestrator HALTs rather than fabricating answers or silently skipping the stage. |
| Project North Star document does not exist when a sprint reaches Frank's gate | Frank HALTs outright and requests one be minted; no interim-oracle fallback, no proceeding without it. |
| Project North Star document exists but is status DRAFT | Layer 2 returns a PROVISIONAL PASS, not a HALT; re-run once the document reaches non-DRAFT status. |
| Sprint is internally flawless (Layer 1 PASS) but off-mission at the project level | Overall verdict is FAIL/HALT; Layer 2 failure is never offset by a Layer 1 pass. |
| Spec-gate or forge-gate loop reaches its 3rd attempt without a clean PASS | Frank judges convergence (shrinking/static/thrashing) instead of a routine verdict; continues if progress is real, HALTs into deep-diagnosis with concrete evidence if stuck. |
| Orchestrator's independent stuck-loop re-derivation disagrees with Frank's diagnosis | Disagreement escalates to Danny; neither side unilaterally resolves it. Frank's underlying quality verdict stays binding regardless. |
| `forge-start` invoked with CADENCE.md or INVARIANTS.md missing (either or both) | HALT before any implementation delegation, regardless of which of the two is missing. |
| A consuming repo (e.g. d-code, sonic-store, agent-dashboard) has no local Frank/spec-orchestration/forge divergence | Picks up the new trimmed Frank and gates automatically via the `~/.claude` global sweep; no repo-level change needed or made. |
| A consuming repo (gap-lens-dilution-filter) already has a locally diverged `frank.md` copy | Left untouched by this sprint's sweep; reconciliation is that project's own call, already flagged via Switchboard. |
| Interview follow-up thread stops surfacing new information | Stop after 1-2 consecutive exchanges that generate nothing new, even below the 5-7 soft anchor; do not pad toward the anchor. |
| A spec sprint is started with no approved Intake doc present | `spec-start` (or successor) HALTs before generating any downstream doc. |

---

## Out of Scope

- NOT: `03-UI-SPEC` doc for this sprint — no user-facing UI (Interview Q2, matches electric-blue precedent).
- NOT: `/new-project` bootstrap wiring for project-North-Star creation — Lumen's / `/new-project`'s territory.
- NOT: Authoring or finalizing the project-level North Star schema/template itself — agent-rig's `docs/NORTH-STAR.md` is a placeholder pending Lumen's global template, to be swapped wholesale, not reconciled piecemeal, by this sprint.
- NOT: Reconciling gap-lens-dilution-filter's locally-diverged `agents/frank.md` copy — their own call; this sprint's full obligation there is the Switchboard message already sent to `beta`.
- NOT: The `franks-lessons` cross-project lessons-learned initiative — logged as a separate backlog item in `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md`, needs its own DDR before spec.
- NOT: Editing already-archived `archive/spec-orchestration-03132026` or `archive/reference/forge-03132026`.
- NOT: A separate lightweight/fixed-persona model tier for the Interview pass-option path (explicitly rejected — reuses whichever model is already conducting the interview).
- NOT: A separate counting track for editorial-only vs. substantive loop iterations (folded into the existing convergence read at attempt 3 instead).
- Deferred: Which model/persona conducts the Interview when Danny does participate, and whether it runs inline-in-orchestrator vs. delegated subagent — explicitly deferred to `02-ARCHITECTURE.md`.
- Deferred: The exact gap-diff algorithm and stopping-heuristic implementation for Interview question generation — architecture's job to formalize.

---

## Constraints

- Must: Frank's five non-negotiable pre-checks (premise, input, evidence independence, standing authority to widen scope, do-not-cite-isn't-a-stop) survive the prose trim untouched in substance.
- Must: Preserve the existing `subagent_type: frank` invocation signature/contract for all four current consumers (gap-lens-dilution-filter, d-code, sonic-store, agent-dashboard) — no breaking change to how Frank is invoked.
- Must: DDR remains optional; Intake becomes mandatory before any spec sprint, in every project using `spec-orchestration`/`forge` going forward — a workflow rule change, not a one-off for this sprint.
- Must: New package folders use MMDDYYYY naming, matching the existing string-sortable convention.
- Must: Interview pass-option stand-in answers use the same model already conducting the interview — no separate/lighter model tier introduced.
- Must not: Silently fabricate Interview answers under any design — if the mechanism cannot reach Danny, it HALTs rather than guessing.
- Must not: Offset a Layer 2 (project North Star / relevance) FAIL with a Layer 1 (sprint North Star / fidelity) PASS, or vice versa — both layers must independently PASS.
- Must not: Check Layer 2 by trusting the sprint North Star document's own self-declared claim of alignment — must re-read the finished artifact against the project North Star document itself (otherwise reproduces the SHARED WELL failure).
- Assumes: Lumen's project-level North Star template will eventually replace agent-rig's placeholder `docs/NORTH-STAR.md` wholesale; this sprint's Frank-gate design treats the project North Star as an interface contract (schema + location) to be consumed once available, not re-derived here.
- Assumes: Propagation via the `~/.claude` global sweep is sufficient to reach all current consumers, because none of them (except gap-lens-dilution-filter's already-flagged local copy) carry a repo-local Frank/spec-orchestration/forge copy today — verified by grep across all four named consumers, not assumed.
