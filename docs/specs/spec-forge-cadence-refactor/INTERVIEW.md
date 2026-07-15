# Interview: Spec/Forge Cadence Refactor

**Status**: Complete
**Author**: wright
**Date**: 2026-07-15
**Mechanism**: Bootstrapped manually, in-conversation (the dedicated Interview-stage tooling doesn't exist yet — building it is itself one of this sprint's deliverables, per Q1 below). Run as the direct, real-channel interview the Intake's own design implication requires: no delegation, no fabricated answers, questions asked and answered live.

---

## Questions and Answers

**Q1. Does this sprint build the actual standalone Interview-stage mechanism (new command/skill + orchestrator wiring, including the HALT-relay-reinvoke pattern for the subagent-delegated case), or just formalize the mandatory-Intake rule now and keep bootstrapping the Interview manually until a later sprint builds the tooling?**
**A:** Build it this sprint. Confirms "What Is Missing" #2 in the Intake is an in-scope deliverable, not deferred.

**Q2. Does this refactor produce a 03-UI-SPEC doc, or skip it?**
**A:** Skip — no user-facing UI, matches the electric-blue backend-seam precedent (03-UI-SPEC omitted as N/A).

**Q3. Bounded question count for the Interview stage template going forward?**
**A:** 5-7 as a soft anchor, not a strict bound — sprints may need more or less. Danny raised a follow-up design question here (see below) rather than just answering the number.

**Q4. Should this Interview's questions + answers be captured as a durable artifact, or is conversation history sufficient?**
**A:** Durable artifact — this document.

---

## Follow-up thread: predetermined vs. adaptive question generation

Danny's question, prompted by Q3: are Interview questions predetermined (derived mechanically from the DDR/Intake), or hybrid — predetermined seed questions but adaptive follow-ups when an answer surfaces something new?

**Resolved: hybrid.** Reasoning, confirmed by Danny:

- A gap well-understood enough to be a fixed checklist item would likely already be in the Intake's own "What Is Missing" / "Needs to Decide" sections. The Interview's actual job is catching what nobody thought to write down — unknown-unknowns, not known gaps. A rigid, non-adaptive list structurally can't do that.
- **Design**: seed questions generated from a gap-diff against the approved Intake, targeting generic blind-spot categories (testing/rollback approach, non-functional constraints, downstream impact, edge cases not already resolved) — plus adaptive follow-ups when an answer opens a new thread. This is exactly the pattern this conversation itself used throughout the Intake discussion (e.g. the propagation question led to an actual grep-verification and a follow-up, not blind acceptance).
- **Stopping rule**: loop-until-dry rather than a hard count — keep going while an answer generates a genuinely new follow-up thread; stop after 1-2 exchanges in a row that surface nothing new. 5-7 is a soft anchor, not a target to hit or pad toward.
- **Design note for the architect during `/spec-start`**: the seed-question generator must diff against what's *already been resolved through conversation* (this whole Intake-approval exchange resolved all 7 open questions live, adaptively), not just against the static Intake document text — otherwise the mechanism will re-ask settled ground. This entire Intake-approval conversation is itself evidence that most of an Interview's job can already happen organically before the dedicated stage even exists.

Danny confirmed this matches his intent.

---

## Handoff

All four seed answers and the hybrid-design resolution are inputs to `02-ARCHITECTURE.md` during `/spec-start` — the exact mechanism (gap-diff algorithm, stopping heuristic implementation, HALT-relay-reinvoke wiring for the subagent case) is architecture's job to formalize, not finalized here.

No further items raised. Interview stage closed pending Danny's final check before proceeding to `/spec-start`.
