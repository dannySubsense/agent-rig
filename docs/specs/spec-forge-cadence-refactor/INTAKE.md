# Intake Spec: Spec/Forge Cadence Refactor

**Status**: APPROVED (2026-07-15, Danny)
**Author**: wright
**Date**: 2026-07-14
**No DDR** — per Danny: DDR is not always required, but Intake always is before spec. This sprint skips DDR by his direction.

---

## Problem Statement

The `spec-orchestration` and `forge` packages (vendored here as `spec-orchestration-03242026/` and `forge-03252026/`) have three gaps that keep producing the same failure shape:

1. **CADENCE.md / INVARIANTS.md are optional in practice.** `forge-start.md`'s "Load Governance" step reads them "if exists" — nothing stops forge from starting without them. Danny: "this is often missed."
2. **No North Star check anywhere.** Neither package checks a finished spec or implementation against a durable project intent or sprint intent. Nothing catches drift.
3. **Frank isn't wired into forge at all**, and where he is used (spec review, ad hoc), his verdict isn't a hard loop condition — nothing currently forces re-work until he's green, and his prose has grown long/ceremonious relative to what a fast-moving loop needs.

This is the same failure shape as the gap-lens-dilution-filter postmortem (`docs/research/findings/POSTMORTEM-2026-07-13-SOURCE-TRUNCATION.md`, referenced in `agents/frank.md`): work proceeded past gates that existed but weren't load-bearing. Danny wants gates that cannot be silently skipped.

---

## What Exists Today

- **Spec (`spec-orchestration-03242026/commands/spec-start.md`):** 5-doc sequence (Requirements → Architecture → UI Spec → Roadmap → Review), each agent-delegated and file-existence-verified. Step 1 "INTAKE" is informal — "clarify the feature request with human if needed," not a real gated doc. `@requirements-analyst`'s own skill (`skills/requirements-extraction/SKILL.md`) has a "Step 2: Conduct Clarifying Interview" (3–5 questions, mandatory unless intake notes are pre-approved) — this is the closest existing thing to an Interview stage, but it's folded into requirements extraction, not a standalone stage, and it's scoped to filling requirements gaps, not probing latency/unseen angles generally.
- **Forge (`forge-03252026/commands/forge-start.md`):** Loads `CLAUDE.md`, `docs/INVARIANTS.md`, `docs/CADENCE.md` at session start. Only `docs/CADENCE.md` is literally marked "(if exists)" in the file (line 18) — `docs/INVARIANTS.md` carries no such marker, but neither file has any HALT-if-missing check anywhere in this doc, so both are equally optional in practice regardless of wording. QC loop uses `@qc-agent` (opus, mechanical/spec-compliance) as the deep-review step; Frank is not referenced anywhere in this file.
- **Frank (`agents/frank.md`, this repo, transferred 2026-07-14 per DDR-013):** Already carries the postmortem-driven 5 non-negotiable pre-checks and PASS/FAIL/HALT verdict tier. Verdict structure is a ~30-line template with pre-checks, gut reaction, risk, conditions, verdict, fixes. Not currently invoked by either package's orchestrator as a binding loop condition.
- **Historical precedent for Intake docs** (real files found, not reconstructed): whole-project intakes (e.g. `gap-lens-dilution-filter/docs/specs/dilution-short-filter/INTAKE.md`) and sprint/slice-level intakes within an ongoing project (e.g. `agent-lore/docs/specs/agent-integration/INTAKE-slice-6.1-automated-relay-trigger.md` — Problem Statement / What Exists Today / What Is Missing / Constraints / Acceptance Criteria / What the Spec Team Needs to Decide / Insertion into Forge Sequence). This Intake follows that slice-level shape.
- **North Star model**: conceived 2026-07-13 (LORE doc `48592a70`), routed to Lumen, status draft/track-only — never built. Danny separately said he'd hand over a retrofit doc for the *project-level* North Star (created at `/new-project` time). That doc has not arrived yet. This sprint's scope is the *sprint-level* North Star plus the gating mechanics; how it reconciles with the project-level doc is an open question below.

---

## What Is Missing

1. A **mandatory Intake gate** before spec starts, in both packages' orchestration commands — not just spec-orchestration's own future use of Intake, but as the general rule for any future spec sprint in any project using these packages.
2. A **standalone Interview stage** — a short (not exhaustive), YAGNI-bounded interview of Danny by an agent, probing latency and angles the Intake didn't cover. Distinct from, and replacing, the existing embedded "clarifying interview" in requirements-extraction — that instruction is dead ceremony (see below), not a working mechanism. Danny may **pass on the interview**; resolved 2026-07-15 — see open question #2 below for the stand-in mechanism.

   **CONFIRMED 2026-07-15 (Danny, first live Interview pass — `docs/specs/spec-forge-cadence-refactor/INTERVIEW.md`):** building the actual Interview-stage mechanism (command/skill + orchestrator wiring + HALT-relay-reinvoke pattern) is in scope for this sprint, not deferred. Question generation is **hybrid** — seed questions from a gap-diff against the approved Intake (and against conversation that already happened, not just the static doc text), plus adaptive follow-ups when an answer surfaces something new. Stopping rule is loop-until-dry (5-7 as a soft anchor, not a hard bound), not a fixed question count. No 03-UI-SPEC for this sprint (no user-facing UI, matches the electric-blue precedent). Exact mechanism (gap-diff algorithm, stopping heuristic) is `02-ARCHITECTURE.md`'s job to formalize.

   **Confirmed defect, not hypothetical:** `requirements-extraction/SKILL.md` Step 2 says "MANDATORY... interview the human... wait for answers before proceeding." Danny confirms this has never actually happened to him. Root cause: `@requirements-analyst` runs as an isolated subagent dispatch (via the Agent tool) — it has no live channel back to the human, it returns one final text block and terminates. `spec-start.md`'s orchestration sequence has no branch for "agent returned pending questions for the human" — it only checks the output file exists and moves on. So the subagent either silently skips the instruction or fabricates plausible answers to satisfy its own gate. The instruction has no teeth. This is the same failure shape as the CADENCE/INVARIANTS "if exists" gap: a gate that exists in prose but isn't load-bearing.

   **Design implication:** the new Interview stage must run somewhere with a real channel to Danny — either inline in the orchestrating session itself (the orchestrator asks directly, turn by turn, the way this Intake review is happening right now), or, if delegated to a subagent, the subagent must return its question list to the orchestrator, which then HALTs, relays the real questions to Danny, waits for his actual replies, and re-invokes with those answers appended. Silent fabrication is not an acceptable fallback under any design. Remove Step 2 from `requirements-extraction/SKILL.md` once the dedicated stage replaces it — leaving both would recreate the same silent-ceremony problem in a different spot.
3. A **sprint-local North Star doc** — separate artifact from the project North Star, scoped to one spec sprint. **RESOLVED 2026-07-15 (Danny agreed):** authored once, as a new template in `spec-orchestration`'s standard doc sequence (alongside Intake/Interview, ahead of or alongside Requirements). Forge's Frank-gate reads that same artifact — no separate forge-side template. One artifact, one authoring point; avoids two templates needing to stay in sync for what is the same document.
4. **Frank as the binding final spec gate** — checks the finished spec against sprint North Star + project North Star. Verdict is binding: FAIL/HALT loops back with no conditional pass, no exceptions. Spec sequence loops (Intake → Interview → draft → Frank) until green.
5. **Mandatory CADENCE.md/INVARIANTS.md creation** before forge begins — a hard gate in `forge-start.md`, not an "if exists" read.
6. **Frank wired into forge as the same binding loop-gate**, same no-exceptions rule as spec.
7. **Frank's prose trimmed** — YAGNI applied to his own verdict format and mandate prose. Character/pre-checks/HALT conditions stay; ceremony goes. **The trim must also define how it reaches actual dispatch**: `agent-rig/agents/frank.md` (source-of-record per DDR-013) and `~/.claude/agents/frank.md` (global dispatch location, what `subagent_type: frank` actually runs) are identical today — but nothing currently names a sync/redeploy step. Without one, this sprint could edit the source file, go fully green on "prose measurably shorter," and every live Frank dispatch keeps running the old prose indefinitely. This needs an explicit step, not an assumption.
8. **YAGNI applied explicitly** in the Interview question set, spec content itself, and forge implementation — not just as a general code-review nit.

---

## Constraints

- Frank's five non-negotiable pre-checks (premise, input, evidence independence, standing authority to widen scope, do-not-cite-isn't-a-stop) are load-bearing and must survive the prose trim untouched in substance.
- No breaking change for existing consumers of `subagent_type: frank` dispatch (gap-lens-dilution-filter, d-code, sonic-store, agent-dashboard) — trimming prose and adding a binding-loop duty must not change how he's invoked.
- DDR stays optional generally; Intake is mandatory before any spec sprint, in every project using these packages going forward — this is a rule change to the packages' own documented workflow, not a one-off for this sprint.
- Must not silently break `spec-orchestration-03242026`/`forge-03252026` for any project currently depending on them as vendored/installed — need to establish whether this refactor edits those packages in place or produces new versioned copies (see open questions).
- Interview pass-option (if Danny opts out) must use whichever model is already conducting the interview — no separate lightweight/fixed-persona model tier introduced for this path (Fable's Frank precedent does not apply here; different job — approximating Danny's judgment, not a fixed judgment gate). Stand-in answers must be stamped `ASSUMED — Danny did not answer; based on [rationale]`, where `[rationale]` cites the industry pattern/framework precedent the assumption rests on. A bare "assumed" flag with no rationale is not acceptable — it gives Frank's gate nothing to evaluate risk against. Expected to be rarely invoked.

---

## Acceptance Criteria (intake-level — spec team to formalize)

- [ ] `spec-start` (or successor) HALTs if no approved Intake doc exists for the sprint
- [ ] Interview stage exists as its own step, distinct from requirements-extraction's embedded interview, with a bounded question count
- [ ] Interview questions demonstrably reach Danny and block on his real reply — verified by walkthrough of the actual mechanism (inline orchestrator turn, or subagent HALT-relay-reinvoke), not asserted in prose
- [ ] Step 2 ("Conduct Clarifying Interview") removed from `requirements-extraction/SKILL.md` once the dedicated stage replaces it
- [ ] Sprint North Star doc is produced and referenced by Frank's spec-gate check
- [ ] Frank's spec-gate verdict is enforced as a hard loop condition in the orchestrator (no manual override path)
- [ ] `forge-start` (or successor) HALTs if CADENCE.md/INVARIANTS.md don't exist, before any implementation delegation
- [ ] Frank's forge-gate verdict is enforced as a hard loop condition, same as spec
- [ ] Frank's verdict template and mandate prose measurably shorter, pre-checks/HALT conditions unchanged in substance
- [ ] Frank's verdict conforms to exactly {Findings, Why, Verdict, Fix (FAIL/HALT only)} — no prose outside those sections — verified against a real verdict example, not asserted in prose
- [ ] New dated packages use MMDDYYYY (e.g. `spec-orchestration-07152026`), consistent with existing folder-naming convention; already-archived `03132026` packages are untouched
- [ ] `~/.claude` global folder sweep is thorough, not additive-only — grep-verified that old command/skill/agent references are gone, not just that new ones were added
- [ ] Danny personally reviews the `agents/frank.md` diff to confirm pre-check substance is preserved — not delegated to Frank himself, since he's the subject of the change (avoids doer-adjacent-to-checker)
- [ ] Sync/redeploy step from `agent-rig/agents/frank.md` (source) to `~/.claude/agents/frank.md` (dispatch) is explicit and actually run — verified by diff, not assumed
- [ ] Interview question set, spec template, and forge cadence all show explicit YAGNI pressure (not just a stated principle)
- [ ] Interview pass-option stand-in answers are stamped `ASSUMED` with a cited rationale (not a bare flag), and use the same model already conducting the interview (no separate stand-in model tier) — verified by example, not asserted in prose
- [ ] Frank's project-North-Star check (Layer 2) reads the finished artifact directly against the project North Star document — not against the sprint North Star's own claim of alignment — and HALTs if no project North Star document exists, rather than proceeding without one
- [ ] Spec-gate and forge-gate loops each enforce their own independent 3-attempt counter; at loop 3 Frank judges convergence (shrinking/static/thrashing) rather than issuing a routine verdict, and HALTs into deep-diagnosis (with concrete evidence, not narrative alone) if stuck
- [ ] Orchestrator independently re-derives Frank's stuck-loop diagnosis from primary artifacts before surfacing to Danny — verified by walkthrough of the actual mechanism, not asserted in prose

---

## What the Spec Team Needs to Decide

1. **Package versioning**: this repo's existing convention is dated snapshot directories (`forge-03252026` superseding `archive/reference/forge-03132026`, same for spec-orchestration). Does this refactor follow that pattern (new `forge-<date>/`, `spec-orchestration-<date>/`, old ones archived), or edit in place now that these are tracked in git and dated-folder versioning is redundant with commit history? **RESOLVED 2026-07-15 (Danny):** follow the existing dated-folder convention. Archive `spec-orchestration-03242026/` and `forge-03252026/` as-is (same pattern already used for `archive/spec-orchestration-03132026` / `archive/reference/forge-03132026`); this sprint's output lands as new dated folders (`spec-orchestration-<date>/`, `forge-<date>/`).
2. **Interview stage ownership**: new dedicated agent, or promote/expand the existing embedded interview in `requirements-analyst`? Where does YAGNI-bounding on question count actually live (a hard cap, or judgment)? **Partially resolved 2026-07-15:** whether the Interview stage runs inline-in-orchestrator vs. as a delegated subagent — and which model conducts it when Danny *does* participate — remains an architecture decision, deferred to `02-ARCHITECTURE.md`. What is resolved is the **pass-option mechanism**: if Danny opts out, the stand-in reuses whichever model is already conducting the interview (no separate/lighter model tier for this rare path — Fable's Frank precedent is a fixed judgment-gate persona, a different job from approximating Danny's own best-practice reasoning). Stand-in answers are stamped `ASSUMED — Danny did not answer; based on [rationale]`, with the rationale citing the industry pattern/framework precedent — a bare flag with no rationale is insufficient.
3. **Sprint North Star vs. project North Star**: exact schema for each, and how Frank checks both without one becoming a rubber stamp of the other. Resolved 2026-07-14: Lumen is actively writing the project-level North Star doc now — this sprint does not block on it. Proceeds in parallel; treat Lumen's output as an interface contract (schema + location) that this sprint's Frank-gate design consumes once available, not something this sprint re-derives. Coordinate via Switchboard before finalizing Frank's project-North-Star check so the two don't diverge.

   **RESOLVED 2026-07-15 (mechanism):** the two checks are a layered determination, not one collapsed check — two distinct failure modes:
   - **Layer 1 (sprint North Star — fidelity):** did the sprint do what it declared it would, faithfully, with no silently skipped gates or promoted-default drift? This is the gap-lens-dilution-filter lesson directly, already baked into Frank's five pre-checks.
   - **Layer 2 (project North Star — relevance):** even if Layer 1 passes cleanly, is the sprint's *existence* in service of the project — or is it a tangent, scope creep, or solving something nobody needed (YAGNI)? Layer 1 cannot catch this; a sprint can be internally flawless and still be the wrong sprint.

   Critically, Layer 2 must be checked by re-reading the finished artifact directly against the **project North Star document itself** — not by trusting the sprint North Star's own self-declared claim of alignment. Checking a document's claim about itself with the same document is the SHARED WELL failure from the gap-lens postmortem (one source, checked twice, agreeing with itself). Both layers must independently PASS; neither offsets the other — a sprint that's faithful to its own sprint North Star (Layer 1 PASS) but off-mission at the project level (Layer 2 FAIL) still gets a FAIL/HALT verdict overall.

   **Missing-doc behavior:** Frank HALTs outright if the project North Star document does not exist when a sprint reaches its gate, and asks for one to be minted. No interim-oracle fallback, no proceeding without it.

   Agent-rig's own project North Star has been drafted per this resolution — `docs/NORTH-STAR.md`, status DRAFT. **Confirmed 2026-07-15 (Danny):** Lumen owns the global North Star anchor template for all projects (not agent-rig) — `docs/NORTH-STAR.md` is a placeholder, to be **swapped out wholesale** once Lumen's template is delivered, not reconciled/merged piecemeal. `/new-project` bootstrap wiring for project-North-Star creation is out of this sprint's scope (Problem Statement scopes this refactor to spec-orchestration/forge/Frank only) — that's Lumen's/`/new-project`'s territory.
4. **Loop termination**: "no conditions, no exceptions" on Frank's gate — needs an explicit non-infinite-loop mechanism (existing packages use a "3 fix attempts then HALT to human" pattern elsewhere; does Frank's gate use the same, or does "no exceptions" mean literally no attempt cap and it HALTs to Danny instead of ever silently passing)?

   **RESOLVED 2026-07-15:** spec-gate and forge-gate loops each carry their own independent 3-attempt counter (not one global count across the sprint) — matches the existing "3 fix attempts then HALT to human" precedent already used elsewhere. At loop 3, Frank explicitly judges convergence rather than issuing a routine verdict: if progress looks real (failures shrinking, recurring issues trending toward editorial/surface-level rather than substantive), the loop continues; if it looks stuck (the same substantive issue recurring unchanged, or thrashing across different files each pass), Frank HALTs into deep-diagnosis mode.

   Frank's deep-diagnosis output must carry concrete evidence — which check/issue is recurring, what each iteration's diff actually touched, shrinking vs. static vs. thrashing pattern — not a narrative conclusion alone. The orchestrator must then independently verify that diagnosis against the same primary artifacts (the actual diffs/check outputs/roadmap state) before surfacing to Danny — re-deriving the conclusion itself, not re-reading Frank's summary a second time ("pillar not signpost": the orchestrator is the agent owner responsible for what reaches Danny, not a pass-through messenger). If the orchestrator's independent read disagrees with Frank's stuck-loop diagnosis, that disagreement itself escalates to Danny rather than either side unilaterally resolving it — Frank's PASS/FAIL/HALT on sprint *quality* stays binding per the existing no-exceptions rule, but the stuck-loop diagnosis is a process judgment, not a content gate, so it doesn't get the same unilateral authority.

   No separate counting track for editorial-only vs. substantive iterations — folding severity into the existing convergence read (above) covers it without a second mechanism.
5. **Frank prose trim — how much is "too long"?** Needs a concrete target (e.g. verdict template line count) rather than a vibe, so the spec-reviewer/Frank himself can check the trim against a real criterion.

   **RESOLVED 2026-07-15 (Danny):** the target is structural, not a line count. A verdict must contain exactly: **Findings** (the what), **Why** (root-cause reasoning per finding — why it's wrong, not just that it is), **Verdict** (PASS/FAIL/HALT), and **Fix/Next-step** (required only on FAIL/HALT). Findings and Why are the load-bearing content and are explicitly *not* what gets cut. Anything outside those sections — restated context, hedging preamble, decorative framing, repeated summaries — is ceremony and goes. Checkable by scanning a real verdict for content outside the four sections, not a vibe read.

   **Follow-up initiative spun off (not in this sprint's scope):** Danny flagged that the "Why" in a Frank verdict is valuable enough to capture as a standalone lesson-learned, potentially cross-project (`projectId: franks-lessons` or similar), so any project's Frank dispatch benefits from lessons learned anywhere. Logged as a backlog idea in `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` — needs its own DDR before spec, deliberately not folded into this sprint.
6. Does this refactor also touch the already-archived `archive/spec-orchestration-03132026` / `archive/reference/forge-03132026`, or are those correctly left alone as historical record?

   **RESOLVED 2026-07-15 (Danny):** No — consistent with open question #1's resolution. Already-archived packages stay untouched as historical record; this sprint only archives the *current* `-03242026`/`-03252026` packages and produces new dated ones. New dated folders use **MMDDYYYY** (matches existing convention — keeps folder names chronologically string-sortable, e.g. today = `spec-orchestration-07152026` / `forge-07152026`, not `-15072026`).

7. **Propagation to already-vendored consumers**: `gap-lens-dilution-filter`, `d-code`, `sonic-store`, and `agent-dashboard` all currently depend on `spec-orchestration`/`forge`/Frank as they exist today. Does this refactor propagate to them, and if so how/when? Confirmed fact, not hypothetical: `gap-lens-dilution-filter/notebook-orchestration-04182026/agents/frank.md` has **already diverged** from canonical `agents/frank.md` — diffed directly, not assumed — with legitimate project-specific additions (its own gate references, project caveats like RC-17/UNRESOLVABLE rows). If this sprint's prose trim never reaches that duplicate, the drift widens further with no defined mechanism to reconcile it.

   **RESOLVED 2026-07-15 (Danny):** yes, propagation happens — but at the shared `~/.claude` global folder level, not by touching each consuming repo individually. Dispatch (`subagent_type: frank`, `/spec-start`, `/forge-start`) resolves through that single global surface, so swapping the new framework there propagates to every consumer automatically. This requires **a thorough sweep of `~/.claude`** — pull every old reference, confirm no legacy artifacts (stale command/skill/agent files, old path references) are left behind — not a lazy overwrite-only pass.

   **Verified 2026-07-15 (not assumed):** grepped all four named consumers for local `frank.md` copies. Confirmed: `gap-lens-dilution-filter/notebook-orchestration-04182026/agents/frank.md` is the **only** local divergent copy among the four — `d-code`, `sonic-store`, `agent-dashboard` have none.

   Repo-local divergent copies (gap-lens's) are **out of scope** for this sprint's `.claude` sweep — that reconciliation is gap-lens's own call, not this sprint's. Action taken: messaged `beta` (`gaplens-SEC`, gap-lens-dilution-filter's orchestrating agent — per Danny, role has since expanded beyond the registry's "SEC data domain" note) on Switchboard to audit their local Frank copy against the canonical trimmed version once it ships and decide whether/how to reconcile.

---

## Sequencing

This Intake is itself the first real exercise of "Intake always required before spec." Next action, in order:

1. Danny reads and approves this INTAKE.md (his standing role per this doc's own rule).
2. Interview stage — since the new dedicated Interview stage doesn't exist yet, this first pass uses a direct, short interview conducted in-conversation (bootstrapping the rule with the tool we have, not blocked on the tool this sprint builds).
3. Full spec via this repo's `/spec-start` (or a lightly adapted version, since spec-orchestration itself is partly the subject of the spec).
4. Frank gate on the spec (current Frank, pre-trim — the trim is an output of this sprint, not a precondition for reviewing it).
5. Forge, using whatever CADENCE/INVARIANTS-gating exists today until this sprint replaces it.

**Next action**: Danny approves or sends back this INTAKE.
