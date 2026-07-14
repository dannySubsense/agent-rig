# Intake Spec: Spec/Forge Cadence Refactor

**Status**: Intake — requires full spec before build
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
2. A **standalone Interview stage** — a short (not exhaustive), YAGNI-bounded interview of Danny by an agent, probing latency and angles the Intake didn't cover. Distinct from, and replacing, the existing embedded "clarifying interview" in requirements-extraction — that instruction is dead ceremony (see below), not a working mechanism.

   **Confirmed defect, not hypothetical:** `requirements-extraction/SKILL.md` Step 2 says "MANDATORY... interview the human... wait for answers before proceeding." Danny confirms this has never actually happened to him. Root cause: `@requirements-analyst` runs as an isolated subagent dispatch (via the Agent tool) — it has no live channel back to the human, it returns one final text block and terminates. `spec-start.md`'s orchestration sequence has no branch for "agent returned pending questions for the human" — it only checks the output file exists and moves on. So the subagent either silently skips the instruction or fabricates plausible answers to satisfy its own gate. The instruction has no teeth. This is the same failure shape as the CADENCE/INVARIANTS "if exists" gap: a gate that exists in prose but isn't load-bearing.

   **Design implication:** the new Interview stage must run somewhere with a real channel to Danny — either inline in the orchestrating session itself (the orchestrator asks directly, turn by turn, the way this Intake review is happening right now), or, if delegated to a subagent, the subagent must return its question list to the orchestrator, which then HALTs, relays the real questions to Danny, waits for his actual replies, and re-invokes with those answers appended. Silent fabrication is not an acceptable fallback under any design. Remove Step 2 from `requirements-extraction/SKILL.md` once the dedicated stage replaces it — leaving both would recreate the same silent-ceremony problem in a different spot.
3. A **sprint-local North Star doc** — separate artifact from the project North Star, scoped to one spec sprint.
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
- [ ] Danny personally reviews the `agents/frank.md` diff to confirm pre-check substance is preserved — not delegated to Frank himself, since he's the subject of the change (avoids doer-adjacent-to-checker)
- [ ] Sync/redeploy step from `agent-rig/agents/frank.md` (source) to `~/.claude/agents/frank.md` (dispatch) is explicit and actually run — verified by diff, not assumed
- [ ] Interview question set, spec template, and forge cadence all show explicit YAGNI pressure (not just a stated principle)

---

## What the Spec Team Needs to Decide

1. **Package versioning**: this repo's existing convention is dated snapshot directories (`forge-03252026` superseding `archive/reference/forge-03132026`, same for spec-orchestration). Does this refactor follow that pattern (new `forge-<date>/`, `spec-orchestration-<date>/`, old ones archived), or edit in place now that these are tracked in git and dated-folder versioning is redundant with commit history?
2. **Interview stage ownership**: new dedicated agent, or promote/expand the existing embedded interview in `requirements-analyst`? Where does YAGNI-bounding on question count actually live (a hard cap, or judgment)?
3. **Sprint North Star vs. project North Star**: exact schema for each, and how Frank checks both without one becoming a rubber stamp of the other. Resolved 2026-07-14: Lumen is actively writing the project-level North Star doc now — this sprint does not block on it. Proceeds in parallel; treat Lumen's output as an interface contract (schema + location) that this sprint's Frank-gate design consumes once available, not something this sprint re-derives. Coordinate via Switchboard before finalizing Frank's project-North-Star check so the two don't diverge.
4. **Loop termination**: "no conditions, no exceptions" on Frank's gate — needs an explicit non-infinite-loop mechanism (existing packages use a "3 fix attempts then HALT to human" pattern elsewhere; does Frank's gate use the same, or does "no exceptions" mean literally no attempt cap and it HALTs to Danny instead of ever silently passing)?
5. **Frank prose trim — how much is "too long"?** Needs a concrete target (e.g. verdict template line count) rather than a vibe, so the spec-reviewer/Frank himself can check the trim against a real criterion.
6. Does this refactor also touch the already-archived `archive/spec-orchestration-03132026` / `archive/reference/forge-03132026`, or are those correctly left alone as historical record?
7. **Propagation to already-vendored consumers**: `gap-lens-dilution-filter`, `d-code`, `sonic-store`, and `agent-dashboard` all currently depend on `spec-orchestration`/`forge`/Frank as they exist today. Does this refactor propagate to them, and if so how/when? Confirmed fact, not hypothetical: `gap-lens-dilution-filter/notebook-orchestration-04182026/agents/frank.md` has **already diverged** from canonical `agents/frank.md` — diffed directly, not assumed — with legitimate project-specific additions (its own gate references, project caveats like RC-17/UNRESOLVABLE rows). If this sprint's prose trim never reaches that duplicate, the drift widens further with no defined mechanism to reconcile it.

---

## Sequencing

This Intake is itself the first real exercise of "Intake always required before spec." Next action, in order:

1. Danny reads and approves this INTAKE.md (his standing role per this doc's own rule).
2. Interview stage — since the new dedicated Interview stage doesn't exist yet, this first pass uses a direct, short interview conducted in-conversation (bootstrapping the rule with the tool we have, not blocked on the tool this sprint builds).
3. Full spec via this repo's `/spec-start` (or a lightly adapted version, since spec-orchestration itself is partly the subject of the spec).
4. Frank gate on the spec (current Frank, pre-trim — the trim is an output of this sprint, not a precondition for reviewing it).
5. Forge, using whatever CADENCE/INVARIANTS-gating exists today until this sprint replaces it.

**Next action**: Danny approves or sends back this INTAKE.
