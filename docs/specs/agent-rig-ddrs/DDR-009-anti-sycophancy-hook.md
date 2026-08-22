# DDR-009 — Anti-Sycophancy Hook (Position-Reversal-Without-Verification)

**Status**: DRAFT
**Author**: wright (recording an agreed design direction, 2026-08-22)
**Date**: 2026-08-22
**Scope**: cross-project in intent, same family as `first-turn-contract-enforcement`.

---

## 0. Provenance

Motivated by a live near-miss this session: a shared transcript from another agent (alpha, on a
different project) whose second reply, under a leading question from its user, produced
confident-sounding requoted claims without visibly re-opening the transcript to re-verify them —
the same failure shape `first-turn-contract-enforcement`'s C3 check already catches, but only on
the *first* turn of a queue-injected session. This is a general version of that same gap.

Explicitly distinct from DDR-007 (no-preamble/no-meta-narration), raised the same session and
initially proposed as a possible merge — kept separate per DDR-007 §4 Q3: this hook triggers on
*position reversal under pressure*, DDR-007 on *narration density regardless of position*.
Conflating them risks one check's tuning fighting the other's false-positive rate.

## 1. The mechanism, two parts

Per the `github.com/Glitch-Cat-Club/prompt-router-starter` review this session, the same pre/post
pairing as that repo's `router.py`/`gate.py`:

1. **3a — Pre-generation (UserPromptSubmit).** Detect a prompt shape that looks like a correction
   or leading question aimed at a prior agent claim (e.g. "did you actually do X," "I thought you
   said Y," a direct contradiction of something the agent stated earlier in the transcript). Inject
   a required response frame before the model drafts anything: state the prior claim verbatim, name
   what specifically is being challenged, and require re-verification before conceding or reversing.
2. **3b — Post-generation (Stop).** Extend `first-turn-contract-enforcement`'s C3 pattern beyond
   turn one: if a reply reverses or reaffirms a position the agent previously stated in the
   transcript, and no fresh tool call appears between the original statement and the reversal,
   block and force a redo — same shape as the existing C3 violation type, generalized to any turn.

Recommend building both — 3a reduces how often 3b has to fire, and 3b is the actual backstop that
makes the rule real rather than advisory (DDR-005 §1's governing thesis, same as every hook in this
family).

## 2. What this explicitly does not do

Does not judge whether the reversed position is *correct* — only whether it was re-verified before
being asserted. Same structural limit `first-turn-contract-enforcement` §1 already states for C3:
proves a tool call occurred, not that it targeted the specific claim being reversed. A general
"detect agreeable/sycophantic answers" hook was explicitly rejected this session as not
mechanizable (semantic judgment, not a deterministic check) — this DDR is the narrower, real thing:
detecting an *unverified* reversal, not an *insincere* one.

## 3. Open questions

1. **Detecting "position reversal" in a transcript generically.** `first-turn-contract-enforcement`
   has a narrow, well-defined target (Signpost/Pillar headings). This hook's target — "the agent
   changed or reaffirmed a prior stated position" — is fuzzier and needs a concrete detection design
   before Intake, likely keyed on the user's prompt shape (3a's trigger) rather than trying to parse
   semantic reversal directly out of the reply.
2. **3a's prompt-shape classifier.** Needs its own design pass — `router.py`'s scored-signal
   approach is the closest precedent, but that repo's signals were tuned for output-style routing,
   not correction-detection; likely needs its own signal set.
3. **Interaction with DDR-007.** Both hooks may end up sharing Stop-hook infrastructure (the wrapper
   pattern, track-record log) even though the checks themselves stay separate — confirm at spec
   time whether they share one Stop hook dispatching two independent checks, or run as two
   registered hooks.

## 4. Next step

Intake, per this repo's standard workflow. Sequenced fourth in the current build order (after
DDR-006, DDR-008, DDR-007), per Danny's 2026-08-22 approval — least-designed of the four real
candidates, and benefits from the prior three's Stop-hook infrastructure being proven first.

---

## References

- `docs/specs/first-turn-contract-enforcement/` — the C3 pattern this generalizes, and its stated
  structural limit (proves tool-call occurrence, not claim-targeting)
- `docs/specs/agent-rig-ddrs/DDR-007-no-preamble-no-meta-narration-hook.md` — sibling hook, kept
  separate per its own §4 Q3
- `github.com/Glitch-Cat-Club/prompt-router-starter` — `router.py`/`gate.py` pre/post pairing precedent
