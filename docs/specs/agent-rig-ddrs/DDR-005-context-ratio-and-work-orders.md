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

---

## 9. Producer position (wright, 2026-08-14) — recorded because a single-source DDR is the thing this family of DDRs argues against

§§1–5 are Danny's diagnosis, transcribed. A document that contained only that would be a
single-source artifact reviewed by nobody — which every other DDR in this family (002, 004,
cadence-hardening, prevention-layer) exists to warn against. This section is the second source. It
agrees with most of it and dissents from one part.

**§2 (work orders) — strongest item, endorsed without qualification, and the cheapest.** Nothing to
build; it changes on the next message. The 2026-08-14 session is the control group: it opened with
"Howdy! Cold session start", contained no objective at all, and produced fourteen commits of
scaffolding around a defect nobody had asked for. Defensible work — but the agent chose it.

**§3 (close every fork) — endorsed; it is a corollary of §2 and binds the agent harder than the
human.** The agent-side form is concrete and unilaterally adoptable: before ending a turn with a
question, state the answer you would give if forced; if an answer exists, that *is* the decision —
make it and delete the question. This is the existing "no-hedge GATE" backlog item (§6), and it is
the rule the producer broke most often in the session that produced this DDR.

**§4 (no mid-task conduct litigation) — endorsed, with one carve-out.** The retrospective pattern
cost that session hours. But Frank's gates are also mid-task conduct litigation, and they are why
two live-breaking defects were caught that day. The difference is **shape, not subject**: a gate
emits a verdict and a routed fix; a conversational correction emits three turns of prose and no
artifact. Keep the gates; cap the conversational form at Danny's one line.

**§1 — half endorsed, half dissented.**

`WORKPLAN.md` and the move of mechanizable conduct into hooks: endorsed. **The instruction to
*delete* the prose versions is dissented from as stated**, on two grounds.

1. **The causal claim is confounded.** The conduct corpus did not crowd out the work on 2026-08-14
   — there was no work in the slot to crowd out. That predicts a different primary fix: the missing
   objective is the disease and the conduct volume is a symptom filling a vacuum. `WORKPLAN.md`
   alone may resolve most of the observed effect, which would leave the deletion unjustified by its
   own evidence.
2. **The corpus caught both real defects that day.** "Verify, don't relay" is why the producer
   grepped the installed binary instead of accepting a docs-consulting agent's answer — which
   caught a false claim that `stop_hook_active` does not exist. And the founding postmortem's
   promoted-default framing is the exact vocabulary Frank used to name F1, the producer's own error
   (`first-turn-contract-enforcement-GATE-LOG.md`, attempt 1). The corpus is not pure overhead; it
   is load-bearing.

Its actual defect is that it is **undifferentiated** — ~20 files at equal weight, no priority, no
trigger conditions. That is a different problem from being too large, and it has a different fix.

**Recommendation:** the five hard rules should be *precisely the ones that cannot be mechanized*.
Everything mechanizable becomes a failing check and is deleted **on replacement, per rule — never
as a batch.** Deleting before §7 Q3's partition is drawn permanently loses the unmechanizable half,
which is where both of that day's saves came from, and deletion is the one move in this DDR that
cannot be undone once it is wrong. The producer further recommends that the partition be drawn by
someone other than the producer, whose behaviour the rules constrain.

**Sequencing recommendation:** §2 and §3 start immediately at zero cost. `WORKPLAN.md` next, as a
small build. Deletion last, gated on the partition.

**Correction to §5's named test.** The `symbol_history` acquisition step belongs to `alpha`
(`market_data`), not to this repo — agent-rig cannot run it without violating the repo-lane rule,
and the point was the pattern, not that task (Danny, confirming). An in-lane equivalent with the
same properties — no decisions needed beyond "go", checkable output — is already queued:

> "Build the first-turn-contract probe. Done means: `scripts/first_turn_contract_probe.py` exists,
> tests pass against the real corpus fixtures, the track-record log writes an entry. Decide the
> details yourself. Report when done or blocked."

The judgment criterion is unchanged and is the whole point: **does the file exist.**

---

## 10. Related research (2026-08-21, updated same day — findings complete)

External research plan and completed findings: `docs/research/ddr-005-context-ratio/` (`RESEARCH-PLAN.md`,
`FINDINGS.md`). Scoped to gather citable evidence (Anthropic's own docs, academic literature,
practitioner community, other agent frameworks) bearing on §1's ratio-inversion claim and §7's open
questions, before this DRAFT advances further — per this repo's Decision Discipline, "best practice"
claims need a source, not just this session's diagnosis. Kept as a separate document rather than
folded into this DDR, for the same reason §9 gives for existing at all: a single-source diagnosis
reviewed by nobody is the failure this family of DDRs warns against.

**Findings summary** (`FINDINGS.md` §1): the evidence corroborates the core mechanism (large,
conduct-heavy standing context degrades instruction adherence generally, not just conduct compliance)
and strongly corroborates moves (1) short standing files and (3) mechanize-into-hooks — Anthropic's
own docs state bloated CLAUDE.md files cause instructions to be ignored, and Claude Code's hooks
system is exactly the "rules that live as failing checks get satisfied" mechanism §1 proposes.
**Not corroborated**: the specific ~90/10 ratio number and the "theatrics of rigor" causal story —
no source anywhere measures a conduct-vs-task ratio; that framing is original to this DDR, not
literature-derived. **Complicates §9's dissent in both directions**: one community source reports no
measurable adherence difference from 25–500 lines (undercuts the "length causes degradation" causal
claim, reframes brevity as a cost argument); one academic benchmark found system-prompt *removal*
causes universal multi-turn performance degradation (supports "the corpus is load-bearing," some
support for the producer's anti-deletion position). §7's four open questions remain largely
unaddressed by external evidence — see `FINDINGS.md` §4 for the per-question breakdown; question 4
(delete-on-replacement vs. all-at-once) was explicitly searched for and confirmed absent from the
literature, so it stays a judgment call this repo has to make without outside precedent.
