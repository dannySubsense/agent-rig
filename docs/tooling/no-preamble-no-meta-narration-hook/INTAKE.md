# Intake: no-preamble-no-meta-narration-hook

**Status**: APPROVED (2026-08-24, Danny)

**Date**: 2026-08-24
**Author**: wright
**Mode**: spec-lite (recommended) — same shape as `first-turn-contract-enforcement` and
`domain-boundary-provenance-hook`/`progress-md-proof-per-slice-hook`: one blocking checker
script/hook, no UI, no product surface, no multi-stakeholder scope. Requirements/UI-spec/roadmap
layering is skipped because there's no UI to spec and the build is too small to split across three
documents; Frank's binding gate and human approval are NOT skipped. Danny's call to confirm or
override at approval.
**DDR**: `docs/specs/agent-rig-ddrs/DDR-007-no-preamble-no-meta-narration-hook.md` (not yet
written — this Intake is being prepared ahead of that record; DDR-007 currently exists only as a
row in `00-DDR-INDEX.md`. Author the DDR stub alongside or immediately after this Intake, per this
repo's usual DDR-then-Intake ordering, unless Danny prefers Intake-first for this one.)

---

## Problem Statement

Agent responses in this ecosystem frequently substitute first-person meta-narration for
substance: intent announcements ("I'm going to..."), stall-before-substance openers, honesty/
ownership cushioning ("Let me be honest..."), praise padding, performative-effort narration
("Let me dig into this..."), and emotional-state narration. This is the same exhortation-vs-check
failure DDR-005 diagnosed generally (§1: "rules that live as exhortations get performed; rules
that live as failing checks get satisfied") — this ecosystem's session-level guidance (e.g. this
repo's own "Don't narrate your internal deliberation" instruction, and equivalents in every other
homelab project's `CLAUDE.md`) already asks for this directly, in prose, and it is not reliably
followed under pressure, the same way DDR-006's citation convention and DDR-008's `[x]` discipline
were not reliably followed as prose alone.

This sprint builds the mechanism to catch meta-narration before it reaches the user: a checkable,
non-exhortation-based detector, not a fixed phrase list, that flags a response substituting
first-person narration for concrete output.

## Context

- **DDR of record**: `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` row 007 — "Build order: 3rd" in
  the hook-mechanization cluster (DDR-005's instances). Not yet its own DDR document; see note
  above.
- **Governing thesis**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` §1 —
  same thesis DDR-006 and DDR-008 already mechanized. This is the cluster's third build.
- **Cluster rollout policy** (`00-DDR-INDEX.md`, Danny, 2026-08-22): ship one hook at a time, each
  gets a soak period before the next starts. DDR-006 and DDR-008 have both merged and are past
  their spec/build stage (DDR-006 merged PR #11, DDR-008 merged PR #13 and is live in agent-rig).
  This sprint is next in build order; soak-completion status of the prior two should be re-checked
  at Intake approval time, not assumed from this document.
- **Reference implementation pattern**: `github.com/Glitch-Cat-Club/prompt-router-starter`'s
  two-part shape (pre-generation `UserPromptSubmit` style injection + post-generation `Stop`-hook
  pattern block) — the same precedent DDR-007's index entry already names.
- **Existing infrastructure to reuse**: `docs/specs/first-turn-contract-enforcement/` and its
  built hook (`docs/tooling/first-turn-contract-enforcement.md` + wrapper) — the Stop-hook wrapper
  pattern (bounded timeout, fail-open on any internal error, append-only track-record log) this
  sprint's hook should sit alongside, not redesign. `docs/tooling/progress-md-proof-per-slice-hook/`
  is the most recent sibling build using the current Lite Mode File Layout (`docs/tooling/{tool}/`
  with `INTAKE.md`/`SPEC.md`/`GATE-LOG.md`/`PROGRESS.md` together) — this sprint follows that
  layout, not the older flat-filename-prefix convention `first-turn-contract-enforcement` and
  `domain-boundary-provenance-hook` used before the layout was formalized.
- **Detection rule already specified in the DDR-007 index entry** (not open, unlike DDR-006's
  detection-rule question at its own Intake stage): a grammatical rule — subject "I"/"we" +
  internal/communicative verb + no concrete noun in the same clause — not a fixed phrase list.
  This sprint's architecture stage still needs to make that rule concrete and testable (exact verb
  set, exact "concrete noun" test, clause boundary detection), but the *shape* of the rule is
  already decided, unlike DDR-006 where the detection-rule shape itself was the open question.
- **Split scope, DDR-011**: Danny asked whether this hook should also force plain language / block
  AI-slop jargon. Decision (2026-08-24, recorded in `00-DDR-INDEX.md` row 011): kept as a separate
  DDR, not folded in here, because the detection method differs (vocabulary/register-based vs. this
  hook's grammatical-structural rule) and mixing the two would make DDR-007's own false-positive
  rate unmeasurable during its observe/log-only soak. This sprint's scope is meta-narration
  detection only — plain-language/jargon detection is explicitly out of scope, tracked under
  DDR-011 instead.

## Capability Gaps This Sprint Closes

1. **A hook that detects first-person meta-narration substituting for substance.** Currently
   nothing exists — the check is entirely a documented convention (this repo's and every sibling
   project's `CLAUDE.md` prose) that depends on the model following it under pressure. No
   unattended mechanism exists.
2. **A concrete, testable grammatical rule.** The index entry names the shape (subject "I"/"we" +
   internal/communicative verb + no concrete noun = flag) but not the exact verb set, the exact
   "concrete noun" test, or how clause boundaries are detected in free-form assistant text. This is
   the sprint's core design problem, same role DDR-006's "what counts as outside this pipeline's
   own config/spec" question played for that sprint.
3. **The two-part trigger mechanism**, concretely specified: what the `UserPromptSubmit` style
   injection actually says, and what the `Stop`-hook pattern-block check actually inspects
   (`last_assistant_message`, per `first-turn-contract-enforcement`'s already-confirmed field name)
   and how it decides block vs. log-only.
4. **A rollout stance for the observe/log-only period** named in the DDR-007 index entry: what
   "false-positive rate measured low" means concretely (a number, or a qualitative bar) before
   promotion to blocking — this needs either a citable precedent or an explicit PROVISIONAL tag
   with a named owner, per this repo's Decision Discipline; it cannot be invented at spec time
   without one or the other.
5. **Wiring into `.claude/settings.json`**, sibling to `first-turn-contract.sh` and
   `progress-proof-per-slice.sh`, with its own track-record log per this repo's established
   pattern (append-only JSONL, same fields shape as the existing two hooks where applicable).

## Constraints

- **Reuse `first-turn-contract-enforcement`'s wrapper shape.** Bounded timeout, fail-open on any
  internal probe error, append-only track-record log — this sprint should not redesign that
  infrastructure, only the detection logic specific to meta-narration.
- **Grammatical rule, not a phrase list.** Per the DDR-007 index entry, explicitly: a fixed banned-
  phrase list is the wrong mechanism (trivially bypassed by rewording, and it's the mechanism
  DDR-011 was split out specifically to avoid conflating with this one). The detection logic must
  be structural.
- **Observe/log-only first.** Per the cluster's soak policy and the index entry: this hook starts
  non-blocking (log-only), promoted to blocking only once false-positive rate is measured and
  found low — the concrete threshold/bar for "low" is an open question below, not assumed.
- **Does not overlap DDR-011's scope.** No acceptance criterion in this sprint may test for
  jargon/plain-language violations — that stays DDR-011's, entirely separate detection method and
  separate hook.
- **Manual-push-only** stays in force; this sprint's commits don't auto-push.
- **Lite Mode File Layout.** All artifacts for this build live together under
  `docs/tooling/no-preamble-no-meta-narration-hook/` (`INTAKE.md`, `SPEC.md`, `GATE-LOG.md`,
  `PROGRESS.md`, `.gate-snapshots/`), not split across a `docs/specs/` sprint folder and a flat
  `docs/tooling/` filename prefix.
- **Every predetermined number/threshold still needs a citable precedent or an explicit
  PROVISIONAL tag** per this repo's Decision Discipline — including the false-positive-rate bar
  above and the "2 non-generative exchanges" style thresholds if this sprint reuses that pattern
  from elsewhere in the repo (it must be re-cited here, not silently inherited).

## Open Questions

1. **Exact grammatical rule.** Verb set for "internal/communicative verb" (e.g. "let me," "I'll,"
   "I think," "to be honest," "I want to make sure") — needs a defensible enumeration or a POS-
   pattern rule, not an ad hoc list masquerading as one. What counts as a "concrete noun" in the
   same clause that neutralizes the flag? Compare candidate approaches at spec time.
2. **False-positive threshold for promotion to blocking.** No number is proposed yet. Needs either
   a citable precedent (e.g. reuse `first-turn-contract-enforcement`'s own soak criterion, if one
   was recorded) or an explicit PROVISIONAL tag with Danny named as owner.
3. **Where meta-narration commonly appears vs. where narration is legitimate.** E.g. a HALT
   message, a genuine user-facing status update mid-long-running-task, or a direct answer to "what
   are you doing" are all first-person and should not be flagged — the rule needs to distinguish
   substance-bearing first-person statements from substance-substituting ones. This is the
   sprint's hardest design problem and should be treated with the same rigor
   `first-turn-contract-enforcement` gave its own field-verification work, not assumed.
4. **Relationship to `first-turn-contract-enforcement`'s existing C3-style checks.** That hook
   already inspects `last_assistant_message` for a different purpose (turn-one contract
   compliance). Does this sprint extend that hook, or ship a fully separate sibling hook? Affects
   whether this is new infrastructure or an extension of existing infrastructure.
5. **Sprint scope**: agent-rig build only (per the cluster's established pattern — DDR-006 and
   DDR-008 both built here first, retrofit elsewhere tracked separately), or does this sprint also
   define the retrofit roster? Follows the existing retrofit-roster pattern
   (`signpost-pillar-propagation`'s target list) rather than a fresh survey, per precedent.

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates `spec-start
--lite` Step 1.
