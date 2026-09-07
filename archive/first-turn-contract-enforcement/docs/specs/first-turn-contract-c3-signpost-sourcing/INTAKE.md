# Intake: first-turn-contract-c3-signpost-sourcing

**Status**: Approved

**Date**: 2026-09-07
**Author**: wright

---

## Problem Statement

`check_c3_violation` in `scripts/first_turn_contract_probe.py` extracts the claim subjects it
checks against qualifying tool calls from the **Pillar** section's own text
(`_extract_claim_subjects(pillar_section_text)`). When the Pillar section contains no
extractable subjects (no backticked tokens, file paths, PR numbers, or quoted queries) — which
happens whenever a Pillar section is empty, vague, or openly admits non-verification (e.g.
"Pillar: none yet — nothing independently checked this session") — the check silently passes via
a documented "presence-only fallback": any qualifying tool call anywhere earlier in the turn
satisfies C3, regardless of whether it verified anything the Signpost actually claimed.

This means the one check whose entire purpose is enforcing "a Pillar heading means the claims
under it were verified" cannot catch the exact case of a Pillar section that honestly states
those claims were *not* verified. Found live in an agent-rig session, 2026-09-06/07 (filed as
GitHub issue #27), while reviewing an example session-close report.

## Context

C3 was added by the `first-turn-contract-c3-claim-matching` sprint (2026-08-27, LOCKED spec,
Frank PASS) to upgrade the original presence-only check into a subject-matching check — see
`docs/tooling/first-turn-contract-c3-claim-matching/SPEC.md` §1: "This spec upgrades it to check
that a qualifying tool call's **target** matches the **subject of the specific Pillar claim**
being asserted." That sprint deliberately sourced subjects from the Pillar text, treating Pillar
as the "here's what I checked" restatement to police, and treating the presence-only fallback as
safe *because* it assumed a real Pillar section would always name something checkable.

Issue #27 disproves that assumption: nothing requires Pillar to name anything at all, and a
session can satisfy the letter of "write a Pillar heading" while writing prose that names zero
subjects — deliberately, evasively, or just honestly ("not yet verified"). The proposed direction
(recorded in the issue) is to source claim subjects from the **Signpost** section instead — the
Signpost is the injected/asserted claim list (branch names, commit SHAs, PR numbers, decision
IDs) that Pillar is supposed to verify, and it exists independent of what Pillar's own prose
says. This closes two gaps: (1) an empty/evasive Pillar can no longer pass via the fallback,
because subjects now come from a source outside Pillar's control; (2) a Pillar that verifies only
some Signpost claims and silently drops others becomes catchable too, since every Signpost-
sourced subject needs its own matching tool call.

This is enforcement-mechanism code — the same class of change `docs/ISSUE-RUNBOOK.md` (written
this same session) requires Cold Frank for at both spec and forge gates, plus a mandatory
regression test reproducing the exact original evasion.

## Capability Gaps This Sprint Closes

- C3's subject-sourcing currently has a documented, provable blind spot (the presence-only
  fallback triggered by an empty-subject Pillar section) that lets a completely unverified Pillar
  claim pass silently. This sprint closes that gap by changing where subjects are sourced from.
- No existing regression test proves this specific evasion is caught — this sprint adds one.

## Constraints

- Scope is limited to `check_c3_violation` and its subject-sourcing/extraction helpers in
  `scripts/first_turn_contract_probe.py`. Does **not** touch C1 (Signpost-before-Pillar ordering)
  or C2 (forbidden third section) logic, does not add a new hook or script file, does not change
  the first-turn-only scope, does not add fuzzy/similarity matching (v1 remains exact
  substring/token containment, consistent with the parent C3 sprint's own non-goals).
- Must not regress any currently-passing case in the existing `first-turn-contract-c3-claim-matching`
  and `first-turn-contract-c3-path-query-boundary-matching` test suites — both prior C3-hardening
  sprints' test coverage must still pass after this change.
- Per `docs/ISSUE-RUNBOOK.md`: this is classified an **enforcement-mechanism defect** — Frank's
  spec-gate and forge-gate for this sprint both run Cold (unbriefed dispatch, isolated detached
  checkout), and forge must include a regression test reproducing the exact issue #27 evasion
  ("Pillar: none yet — nothing independently checked this session" with an unrelated qualifying
  tool call present, previously a false PASS).
- Full `/spec-start` sequence, not `--lite` — this changes matching/detection logic, which the
  runbook and this session's own prior decision both require full mode for.

## Design Decisions (resolved at Intake, no Interview needed)

- **Signpost-sourced subjects supplement, not replace, Pillar-sourced subjects.** The Signpost is
  the list of claims that need checking; the Pillar is built by checking that list. Every subject
  the Signpost raises must have a matching qualifying tool call somewhere in the turn — that's
  the actual fix. Pillar-sourced extraction stays as-is on top of that: if Pillar names something
  the Signpost didn't (an agent's own follow-on check), it's still checked exactly as today.
- **An empty-subject Signpost means there's nothing to require a tool call for — not a fallback
  hole.** If the Signpost genuinely raised zero checkable claims, C3 has nothing to demand
  verification of and simply doesn't fire on that basis. This isn't a gap; it's the correct
  behavior when there's nothing to check.
- **Scope is unchanged: this only applies where a Pillar heading exists** (`pillar_idx is not
  None`), same precondition C3 already has. Nothing about sourcing subjects from Signpost instead
  of/in addition to Pillar changes when the check runs, only what it checks against.
- **Extraction patterns get whatever's needed to actually pull real subjects out of real Signpost
  text** — branch names, commit SHAs, decision/issue IDs, file paths — engineering detail for
  Architecture to work out against real Signpost examples from this repo's own transcripts, not a
  decision that needs to wait on approval.

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates
`spec-start` Step 0. Anything else — missing file, `DRAFT`, `REJECTED`, or the Status line absent
entirely — is a HALT before any downstream doc generation.
