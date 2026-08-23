# Intake: progress-md-proof-per-slice-hook

**Status**: APPROVED (2026-08-22, Danny)

**Date**: 2026-08-22
**Author**: wright
**Mode**: spec-lite (recommended) — same shape as `domain-boundary-provenance-hook` and
`first-turn-contract-enforcement`: one blocking checker script, no UI, no product surface, no
multi-stakeholder scope. Danny's call to confirm or override at approval.
**DDR**: `docs/specs/agent-rig-ddrs/DDR-008-progress-md-proof-per-slice-hook.md`

---

## Problem Statement

`PROGRESS.md` slice checkboxes are self-asserted by the agent marking them, not checked by
anything. A `[x] COMPLETE` mark is a claim, not a verified fact — the exact gap named in the
standing feedback memory `feedback_gate_not_substitutable_by_slice_checkboxes.md`. `WORKPLAN.md`
(DDR-005 §1 move 2) was proposed to fix this by adding a definition-of-done; approved disposition
(DDR-005, 2026-08-22) retired it as a separate file and folded its job into `PROGRESS.md` directly:
give each slice a proof command, and mechanically verify it before letting the checkbox stand.

## Context

- **Design precedent, same session**: `github.com/Glitch-Cat-Club/prompt-router-starter`'s
  `gate.py` — a contract/ledger of numbered requirements, each with a proof command; a Stop hook
  runs allowlisted proofs on a "done" claim and refuses a false one. Adopted pattern, not code.
- **Infrastructure to reuse directly**: `first-turn-contract-enforcement`'s Stop-hook wrapper shape
  (bounded timeout, fail-open, append-only track-record log) — `.claude/hooks/first-turn-
  contract.sh`, `scripts/first_turn_contract_probe.py`.
- **Sibling build, same cluster, same session**: `domain-boundary-provenance-hook` (DDR-006,
  merged) — same allowlist/manual-stamp split (allowlisted proof commands run and are trusted,
  anything else stamped `manual`, never blocks), same wrapper/probe pattern.
- **Governing thesis**: DDR-005 §1 — "rules that live as exhortations get performed; rules that
  live as failing checks get satisfied." This is DDR-005's own named first implementation slice.
- **Rollout status**: build-order 2nd in the hook-mechanization cluster (`00-DDR-INDEX.md`), per
  Danny's approved sequencing (2026-08-22) — no exception granted, standard one-at-a-time-with-soak
  policy applies once this ships.

## What Is Missing

1. **Proof-command syntax in `PROGRESS.md`'s existing slice-line format.** Not yet decided — inline
   per slice line, or a structured block per slice.
2. **A Stop hook that reads a slice's proof command(s) and runs it before allowing `[x]`.** Same
   allowlist convention as `domain-boundary-provenance-hook` — allowlisted commands run and are
   trusted; anything else stamped `manual`, never blocks.
3. **Clarity on relationship to `GATE-LOG.md`/Frank's own gate.** This hook checks mechanical
   slice-completion claims; Frank's gate is a judgment call on the whole sprint. Not the same
   mechanism — must be stated explicitly in the spec so one is never read as substituting for the
   other (same distinction this repo's own memory `feedback_gate_not_substitutable_by_slice_
   checkboxes.md` already draws for a human reader; this hook is the machine-enforced version of
   that same rule).

## Constraints

- **Reuse `first-turn-contract-enforcement`'s wrapper shape.** Bounded timeout, fail-open on any
  internal probe error, append-only track-record log — do not redesign this infrastructure, only
  the detection/proof logic specific to slice completion.
- **Presence/absence + command-result only — not a soundness judgment.** This hook verifies a
  claimed-complete slice's proof command actually passed. It does not judge whether the proof
  command itself is a good test of "done" — that stays human/Frank's job at spec-gate/forge-gate
  time, same carve-out `domain-boundary-provenance-hook` already established for its own citation
  check.
- **Does not replace Frank's binding gate or `GATE-LOG.md`.** Explicit non-goal, stated in the spec
  itself, not just this Intake.
- **Manual-push-only** stays in force.
- Every predetermined number/threshold this sprint introduces needs a citable precedent or an
  explicit PROVISIONAL tag, per this repo's Decision Discipline — no exception.

## Open Questions

1. **Proof-command placement/syntax in `PROGRESS.md`** — needs a concrete decision before
   architecture can be written.
2. **Allowlist scope** — reuse `first-turn-contract-enforcement`'s/`domain-boundary-provenance-
   hook`'s allowlist conventions, or define fresh ones for this hook.
3. **Trigger surface** — Stop hook (checking a claimed-complete slice at end of turn), or something
   keyed to the specific moment a `PROGRESS.md` edit marks a slice `[x]` (closer to a PreToolUse
   check on the `PROGRESS.md` edit itself, similar in shape to `domain-boundary-provenance-hook`'s
   trigger). Not yet decided — real design question, not a rubber stamp of the sibling's choice.
4. **Does this apply retroactively to already-`[x]`-marked slices in existing `PROGRESS.md` files**,
   or only to marks made after this hook exists? Affects whether any migration/backfill is needed.

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates `spec-start`
Step 0.
