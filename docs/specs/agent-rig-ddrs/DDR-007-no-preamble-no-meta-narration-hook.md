# DDR-007 — No-Preamble / No-Meta-Narration Response Hook

**Status**: DRAFT
**Author**: wright (recording Danny's diagnosis + a jointly distilled pattern spec, 2026-08-22)
**Date**: 2026-08-22
**Scope**: cross-project in intent — agent-rig authors and stewards it as a hook mechanism, same
family as `first-turn-contract-enforcement` and DDR-006.

---

## 0. Provenance

Raised live in-session, 2026-08-22, as part of the same conversation that produced DDR-006:
Danny's question was whether a hook could strip "declarative, throat-clearing, red-carpet,
'here's what I'm about to tell you' language" and keep replies "show, don't tell," in plain
language. First pass treated this as partly a literary-quality question (not mechanizable) and
partly a preamble-blocklist question (mechanizable). Danny corrected the framing with a concrete
illustrative example: a hypothetical reply that spends several sentences on honesty/ownership/
self-narration ("I want to tell the honest answer," "I own this," "one thing I did find though,"
"but first I want to say") before ever stating the actual fact ("four things aren't closed"). His
point, exactly as given: reading all of that produces no substance. That reframes this as a
**structural** pattern, not a stylistic judgment call — closer to `first-turn-contract-
enforcement`'s C1/C2 (presence/absence of a pattern) than to any semantic quality check.

The specific example phrases were, in Danny's own words, "off the top of my head" — he asked for
the actual detection patterns to be distilled rather than relying on his own recall of examples.
§2 below is that distillation.

## 1. What this is not

Not a hook that judges writing quality, "good" prose, or literary "show don't tell" as a general
principle — that is a semantic/judgment call, same category this DDR family has repeatedly ruled
out (see DDR-005 §9's rejection of a general sycophancy-detector hook, and this same conversation's
rejection of a general "detect agreeable answers" hook). A hook cannot tell good abstract writing
from bad abstract writing. It can tell a sentence with no concrete content from one that has some.

## 2. The detection principle

**General rule**: flag any sentence whose grammatical subject is "I"/"we" and whose verb is an
internal or communicative act (*want, feel, own, should have, will, am going to, appreciate, hope,
believe*) **and** which contains no concrete noun — no file path, number, name, date, or status
word. A sentence about the world has substance in it by construction. A sentence about the
speaker's own state or intentions doesn't. This is the actual detector; the categories below are
labeled cases for building fixtures/tests against it, not an exhaustive phrase list to match
against (a fixed list drifts and is incomplete; the grammatical shape doesn't).

**Categories** (for fixture/test coverage, not the detector itself):

1. **Intent announcement** — states the upcoming action instead of doing it. *"I'm going to check
   the logs," "Let me look into that," "Here's what I'll do:"*
2. **Honesty/directness meta-commentary** — asserting the answer's own honesty as a value instead
   of just being direct. *"To be honest," "I want to give you a straight answer," "I'll be direct
   with you"*
3. **Ownership/apology as cushion, not as fact** — ownership language not fused to the specific
   fact in the same sentence. *"I own this," "that's on me," "I made a mistake"* used alone, vs.
   *"I misread the branch name on line 40"* (fine — that's substance, keep it).
4. **Stall-before-substance** — a sentence whose only job is delaying the next sentence. *"One
   thing I did find, though," "But first I want to say," "There's something worth mentioning
   here"*
5. **Praise/enthusiasm padding** — zero information content, social lubrication only. *"Great
   question!," "Happy to help," "I appreciate you flagging that"*
6. **Performative-effort narration** — narrates the act of trying instead of producing the result.
   *"I want to make sure I give this the rigor it deserves," "Let me think carefully about this"*
7. **Redundant question-restatement** — repeating the question back with no disambiguating value
   before answering it.
8. **Table-of-contents prose** — a sentence announcing that a list is coming, instead of just the
   list. Headers/bullets are fine; *"There are three things to cover here"* as a standalone
   sentence is not.
9. **Emotional-state narration** — stating an internal state instead of a fact. *"I'm frustrated
   that," "I'm glad," "I'm worried that"*
10. **Redundant framing markers** — *"Overall," "In summary," "Bottom line up front"* used as
    filler at both ends of a reply rather than as actual structure.

## 3. Two mechanisms, same build

Per the earlier conversation this session (prompted by reviewing `github.com/Glitch-Cat-Club/
prompt-router-starter` for DDR-005), two complementary hook points, same as that repo's own
`router.py`/`gate.py` pairing:

1. **Pre-generation (UserPromptSubmit)** — inject a standing style constraint before the model
   drafts a reply: no preamble, lead with the finding, plain sentences. Precedent: `router.py`'s
   skin-injection mechanism, generically — a standing injection rather than their conditional
   prompt-shape scoring.
2. **Post-generation (Stop)** — pattern-match the drafted reply against §2's detection principle;
   block and force a rewrite on a match, same shape as `first-turn-contract-enforcement`'s C1/C2.

Recommend building both, not choosing one — pre-generation framing reduces how often the
post-generation gate has to fire, and the gate is the actual backstop that makes the rule real
rather than advisory, per this whole DDR family's shared thesis (DDR-005 §1: "rules that live as
exhortations get performed; rules that live as failing checks get satisfied").

## 4. Open questions

1. **False-positive risk on category 3 (ownership/apology).** A genuine, substantive admission of
   error ("I misread line 40, here's the fix") must not be blocked just because it contains
   ownership language — the detector's "no concrete noun" clause is what should protect this case,
   but it needs real fixture coverage before trusting it.
2. **Blocking vs. flagging.** `first-turn-contract-enforcement` blocks outright on C1-C3 because
   those are close to unambiguous (a heading either precedes another or doesn't). This detector is
   fuzzier — worth deciding whether a match blocks-and-forces-rewrite or only annotates/logs for a
   softer rollout, at least initially.
3. **Relationship to DDR-005's anti-sycophancy hook (3a/3b) discussed same session.** Related but
   distinct: anti-sycophancy is about *position reversal without re-verification*; this is about
   *narration density regardless of position*. Likely two separate checks sharing the same Stop
   hook infrastructure, not one merged check — needs confirming at spec time, not assumed here.

## 5. Next step

Intake, per this repo's standard workflow. Not yet written.

---

## References

- `docs/specs/first-turn-contract-enforcement/` — the Stop-hook reference implementation this extends
- `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — the general thesis this is one instance of
- `docs/specs/agent-rig-ddrs/DDR-006-domain-boundary-provenance-hook.md` — sibling hook, same session, same family
- `github.com/Glitch-Cat-Club/prompt-router-starter` — design precedent for the pre/post hook pairing
