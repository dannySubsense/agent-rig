# DDR-005 — Context Ratio Inversion and the Work-Order Protocol

**Status**: DRAFT
**Author**: wright (recording Danny's diagnosis, 2026-08-14)
**Date**: 2026-08-14
**Scope**: cross-project — agent-rig authors it; it is intended to be addressed across all homelab
projects, not adopted here alone.

---

## 0. Provenance and standing

This DDR records a diagnosis Danny delivered directly on 2026-08-14, at the end of a session that
is itself the primary evidence for it. The four sections below are his analysis. They are recorded
here substantially as given, because the value is in the diagnosis and a producer's rewrite of it
would be exactly the kind of narration §1 identifies as the problem.

Two of the four points are about **his** behaviour as much as the agent's. Those are kept in, not
softened — a DDR that recorded only the agent's half would misstate the mechanism.

---

## 1. The context ratio is inverted — 90% conduct, 10% work definition

An agent's standing context (`CLAUDE.md` plus ~20 memory files) is almost entirely about *how to
talk, verify, capture, and defer* — accumulated from past failures. The actual work is one line in
a session capture.

**An agent optimizes for what dominates its context.** So the corpus gets what it rewards:
verification narration, exception notes, memory logging, careful hedging. **Theatrics of rigor.**
Meanwhile the real objective — e.g. "backfill true listing dates into `symbol_history`" — is a
single sentence buried in a LORE capture.

**The fix is a ratio inversion, in three moves:**

1. A **short `CLAUDE.md` with five hard rules.** Not a curated library of past lessons.
2. A **`WORKPLAN.md` in the repo** stating the current objective, the ordered tasks, and a
   definition-of-done for each.
3. **Conduct enforcement moves into hooks and scripts, and the prose versions are deleted.** Not
   supplemented — deleted. The probe work already specced (DDR-0009 in `market_data`; agent-rig's
   own DDR-004 / `signpost-pillar-propagation` / `first-turn-contract-enforcement` are the same
   family) is the mechanism half.

> **Rules that live as exhortations get performed; rules that live as failing checks get
> satisfied.**

That sentence is the whole DDR. Everything else is application.

## 2. Give work orders, not open questions

"Where are we at," "what needs doing," "does this need to be fixed" are **status questions**. They
produce status answers, and each one restarts the assess → report → recommend loop.

What produces work is a **work order**:

> "Fix `symbol_history.start_date`. Done means: real listing dates for >95% of symbols, pre-2018
> `daily_universe` rebuilt, invariant check added. Decide the details yourself. Report when done or
> blocked."

Its properties, which are the specification:

- **One message.**
- **One definition of done**, stated in checkable terms.
- **Decision authority explicitly delegated** ("decide the details yourself").
- **Two legitimate exits only**: done, or blocked.

Danny's own note, recorded because it is half the mechanism: *"Today you never issued one of those;
I never earned one either — but the format matters independently."*

## 3. Resolve forks immediately, or delegate them explicitly

An open micro-decision left hanging has exactly two outcomes, both bad: the agent **stalls**
(asks), or **ships past** the human.

The rule: say **"your call"** or **give the answer** — in the same breath as the fork appearing.
Never leave one open. A fork that neither party closes is not neutral; it is a defect that will be
resolved later by whoever is less careful about it.

## 4. Do not litigate conduct mid-task

Every conduct correction in the 2026-08-14 session was **fair**. Each one also **flipped the session
into introspection for about three turns, and the work stopped every time.**

- If the agent misbehaves mid-task: **one line — "wrong, keep going"** — and hold the retrospective
  until after the deliverable exists.
- A session can produce work or produce self-examination. That session produced almost entirely the
  latter, and Danny followed the agent into it every time instead of finishing something.

This is the failure mode §1 predicts: a context dominated by conduct rules makes conduct the most
available thing to discuss, for both parties.

---

## 5. The test Danny specified

Not a hypothetical — the named falsifiable trial for whether any of this works:

> The `symbol_history` acquisition step needs no DB, no decisions beyond "go," and has a checkable
> output (a staging file plus a coverage report). **Issue it as a work order — next session or right
> now — and judge the agent on whether the file exists.**

Judgment criterion: **does the file exist.** Not whether the report was well-reasoned, the
verification was thorough, or the capture was written.

---

## 6. Relationship to existing work

- **Supersedes in spirit, does not replace**: the backlog item *"Template tier: no-hedge GATE
  (value → triggerable check)"* in `00-DDR-INDEX.md`. That item identified the same
  exhortation-vs-check distinction for one rule; this DDR generalizes it to the whole corpus and
  adds the ratio argument. Fold that item into this DDR rather than building it separately.
- **Same family as**: DDR-002 (gate-bypass — arbitrageable instruction → structural gate), DDR-004
  (session-start signpost→pillar binding), the backlog's *"Cadence hardening"* and *"Prevention
  layer"* items. Every member of that family says the same thing from a different angle: an
  instruction that must be remembered is not a control.
- **Direct precedent, and a caution**: `signpost-pillar-propagation` Slice 11 was DROPPED for this
  exact reason — prose in `CLAUDE.md` is a *description* of a mechanism, not the mechanism.
  Note that on 2026-08-14 the producer nonetheless answered a live behavioural failure by writing
  *more prose* into an injected FOOTER, inside the sprint that dropped Slice 11. The pull toward
  the prose fix survives knowing better, which is why §1's third move says **delete**, not
  supplement.

## 7. Open questions (stated, not assumed)

1. **Which five rules?** §1 says "five hard rules" — the number is Danny's and is a deliberate
   forcing constraint, not a measurement. Which five, and what happens to the ~20 memory files that
   do not survive the cut, is undecided.
2. **Is `WORKPLAN.md` per-repo, and who writes it** — the human, the agent, or the spec loop's
   existing `PROGRESS.md` renamed and re-scoped? Note agent-rig already has `PROGRESS.md` as
   declared sprint ground truth; these may be the same artifact.
3. **What conduct is actually mechanizable.** §1 assumes the prose can be deleted because hooks
   replace it. Some of it can be (ordering, forbidden sections, tool-call presence — see
   `first-turn-contract-enforcement`). Some plainly cannot. The deletion is safe only for the part
   that a failing check can carry, and that partition has not been drawn.
4. **Rollout order across the 8+ homelab repos**, and whether the ratio inversion ships as a
   template change, a per-repo pass, or both.

## 8. Not yet decided

This is a DRAFT DDR recording a diagnosis. It proposes no implementation, and nothing in it is
approved. Next step per the project workflow is Danny's review, then Intake if it proceeds.
