# Requirements: Signpost Checklist Redesign

## Traceability
Project North Star bullet this sprint serves: Purpose — "the DDR → Intake/Interview → spec →
forge cadence, QC/judgment gates like Frank" — this sprint hardens the verification-honesty
mechanism that gates first-turn session behavior, one of the cross-cutting orchestration
mechanics Agent Rig exists to develop centrally.
Project North Star status at gate time: Established (non-DRAFT).

## Summary

Replace the archived first-turn-contract C1/C2/C3 free-form Pillar-prose mechanism with a row-based
checklist: each Signpost claim line is copied verbatim into a Pillar-section checklist row, and each
row must carry a real, tool-call-backed verification status before the turn passes the Stop-hook
gate.

## Propagation Scope (this sprint: agent-rig only)

Per `docs/specs/agent-rig-ddrs/HOOK-DEPLOYMENT-ROSTER.md`, the archived Stop-hook C3 contract
(`first_turn_contract_probe.py` / `first-turn-contract.sh`) is currently live in nine other repos:
`market_data`, `department-os`, `electric-blue`, `gap-lens-dilution`,
`gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, and
`runtime/agent-lore`. Agent-rig's own copy was already unwired (commit `a44f1d5`) — this sprint
builds a replacement for agent-rig specifically: agent-rig's own
`.claude/settings.json` (Slice 6) and the forced Pillar syntax delivered via agent-rig's
(gitignored, local-only) `CLAUDE.md` (Slice 5). The other nine repos on the roster are not touched
by this sprint and continue running the archived first-turn-contract mechanism unchanged; nothing
in this sprint's implementation modifies, disables, or depends on their copies of it.

This mirrors how the archived mechanism itself was originally piloted in agent-rig before any
retrofit-roster rollout to other repos (per the roster's 2026-08-28 batch note). Redeploying this
redesign to the other nine repos is future, separate work — scoping or planning that propagation is
explicitly out of scope for this sprint (see Out of Scope below).

## User Stories

### US-1: Verbatim row authorship from Signpost, verified by the hook
As the agent being gated,
I want to copy each Signpost claim line verbatim into my own Pillar-section checklist row,
so that row labels are observed text, never an inferred or normalized paraphrase, and the hook
can verify (not author) each row against the real Signpost lines and real tool-call evidence.

A Stop-hook can only block or allow a turn already emitted — it cannot write into the agent's
own reply. Row authorship is therefore always the agent's act; the hook's role is limited to
reading the rows the agent already wrote and checking each row's label against the Signpost
line it claims to satisfy, and each row's status against real transcript evidence (US-2, US-3).

### US-2: Per-row tool-call-backed verification
As the hook mechanism,
I want to require a real, tool-call-backed status (`verified`/`unverified` + evidence) for every
row the agent wrote,
so that an agent cannot self-report completion without a real tool call standing behind it.

### US-3: Mechanical FAIL on missing/unbacked rows
As the hook mechanism,
I want to FAIL the turn when any Signpost row is missing from the Pillar checklist or lacks
tool-call-backed evidence,
so that the failure is mechanically detectable rather than inferred from free-form prose.

### US-4: Revise-and-resubmit on FAIL
As the agent being gated,
I want to revise my Pillar section to add the missing row or evidence and resubmit,
so that I can correct a FAIL without a retry-count ceiling blocking legitimate correction.

### US-5: Unchanged trigger surface
As the operator (Danny),
I want this mechanism to trigger on the exact same surface as the archived first-turn-contract
mechanism (Stop-hook, first reply of session only, gated on session-queue briefing marker
presence, `stop_hook_active` bypass unchanged),
so that scope does not silently expand beyond what was explicitly decided.

**Known limitation (accepted 2026-09-07, Danny):** the inherited first-turn detection
(`first_turn = len(assistant_text_indices) <= 1`, from the archived probe) has a real gap — any
assistant text emitted before the first tool call in turn 1 causes the mechanism to treat the
actual first reply as "turn 2+" and skip it entirely. Measured against the 10 most recent real
agent-rig transcripts: 1 of 10 already triggers this bypass. Tested against this sprint's North
Star intent (closing evasion channels) and accepted as a known, documented, non-blocking
limitation rather than redesigned now — this repo's separate no-preamble Stop-hook already trends
the underlying cause downward, and this sprint's validation model is live use with feedback, not
solving every inherited gap before shipping. Revisit only if the real-world rate rises or a
concrete incident traces to it.

## Acceptance Criteria

**US-1**
- [ ] Given a Signpost section with N claim lines, when the agent writes its Pillar section, then
  the agent's reply contains one checklist row per Signpost line, each row's label being the
  verbatim text of its corresponding Signpost line (no paraphrase, truncation, or normalization).
- [ ] Given a Signpost line changes between turns, when the agent writes that turn's Pillar
  section, then the row label the agent writes matches that turn's Signpost line verbatim.
- [ ] Given the agent's Pillar rows, when the hook evaluates the turn, then the hook only reads
  and checks the rows already present in the agent's reply — it never inserts, generates, or
  modifies a row itself.

**US-2**
- [ ] Given a checklist row, when the agent marks it with status `verified`, then the row's status
  must be accompanied by evidence traceable to an actual tool call in the transcript (not a cited
  file:line/command-output asserted without a corresponding tool-call entry).
- [ ] Given a row's evidence claims a tool call that does not exist in the transcript, when the
  hook evaluates the row, then the row is treated as unbacked (fails, does not pass on the
  strength of the claim alone).
- [ ] Given a row the agent has not verified, when the agent writes that row, then the row's
  status is the forced literal `unverified`, and the hook never penalizes an honestly-disclosed
  `unverified` status on its own.

**US-3**
- [ ] Given any Signpost row is absent from the Pillar checklist, when the hook evaluates the
  turn, then the result is FAIL.
- [ ] Given any present row's status is `verified` but lacks tool-call-backed evidence, when the
  hook evaluates the turn, then the result is FAIL.
- [ ] Given a Pillar row's label matches no real Signpost line, when the hook evaluates the turn,
  then that row is still evaluated for backing (never silently skipped) and is additionally
  flagged as unmatched.
- [ ] Given all Signpost rows are present, each matched to exactly one row, and each row's status
  is either `unverified` or a transcript-verified `verified`, when the hook evaluates the turn,
  then the result is PASS.

**US-4**
- [ ] Given a FAIL, when the agent adds the missing row or evidence and resubmits, then the hook
  re-evaluates without consulting or incrementing any retry counter.
- [ ] Given repeated FAILs on the same turn, when re-evaluated, then no attempt ceiling blocks
  further revision (distinct from Frank's separate 3-attempt-counter gate).

**US-5**
- [ ] Given a session's first reply with the session-queue briefing marker present, when the
  Stop-hook fires, then the checklist mechanism activates.
- [ ] Given `stop_hook_active` is set, when the Stop-hook fires, then the mechanism bypasses,
  identical to the archived mechanism's behavior.
- [ ] Given the reply is not the first reply of the session (per the inherited detection,
  including its known limitation above), or the briefing marker is absent, when the Stop-hook
  fires, then the mechanism does not activate.

## Edge Cases

| Case | Expected Behavior |
|------|-------------------|
| Signpost section is empty (heading present, zero claim lines, zero non-blank content) | Zero checklist rows required; no FAIL solely for absence of rows when there is nothing to verify. |
| Signpost heading absent entirely (on a turn this mechanism is gated on) | Fail-closed: the hook blocks the turn. Confirmed 2026-09-07 (Danny): this diverges from the archived mechanism's own permissive behavior (which allowed this case), and the divergence was tested against this sprint's North Star intent and confirmed as correct, not inherited. |
| Signpost heading present, non-blank content, zero list-item lines parsed (e.g. claims written as prose, including prose trailing on the heading line itself) | Fail-closed: treated as malformed claims, not "nothing to verify" — distinct from the truly-empty case above. |
| A Pillar line does not match the forced row syntax | Flagged as a violation directly (stray prose), not merely inferred through a missing-row report. |
| A Pillar row's label matches no real Signpost line | Row is still evaluated for real tool-call backing and is additionally flagged as unmatched — never silently ignored. |
| Signpost line is identical to a prior turn's line | Treated as its own verbatim row for this turn; no dedup logic — dedup was not requested and would be speculative scope. |

No further edge cases are added beyond what the Intake/Interview record grounds — per YAGNI
discipline carried forward from the Interview, speculative edge-case coverage (malformed input
fuzzing, multi-session state, concurrent hook invocations, etc.) is out of scope unless a real
need surfaces.

## Out of Scope

- NOT: Any retry-count/attempt-ceiling logic on this hook's FAIL path (that belongs solely to
  Frank's spec/forge-gate, per Intake's explicit FAIL Behavior section).
- NOT: Cross-referencing or reasoning about concepts inferred from free-form prose — the entire
  point of this redesign is to eliminate inferred-concept checking in favor of observed text and
  real tool calls.
- NOT: A broadened trigger surface (e.g., every reply, not just first reply; sessions without the
  briefing marker). Trigger surface is 1:1 inherited from the archived mechanism, including its
  known first-turn-detection limitation (see US-5).
- NOT: Building or validating new pattern-matching logic against self-written fixtures. If new
  matching logic is needed, it must be validated against real transcript data
  (`~/.claude/projects/*/*.jsonl`).
- NOT: An elaborate pre-ship test corpus. Validation is Danny's live daily use with feedback,
  per the Interview's Q1 answer.
- NOT: Propagating this redesign to any repo besides agent-rig. Per
  `HOOK-DEPLOYMENT-ROSTER.md`, the archived first-turn-contract mechanism is currently live in nine
  other repos (`market_data`, `department-os`, `electric-blue`, `gap-lens-dilution`,
  `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`,
  `runtime/agent-lore`) — this sprint does not touch, break, or plan the rollout of the redesign to
  any of them; they keep running the archived mechanism as-is. Scoping that propagation is a
  separate, later sprint's work, not this one's.
- Deferred: Row-key normalization/truncation scheme — resolved as verbatim-only for this build;
  revisit only if a real failure mode surfaces in live use.
- Deferred: A separate propagation sprint to redeploy this redesign to the other nine roster repos.
- Deferred: Redesigning the inherited first-turn-detection boundary to close its known 1-in-10
  bypass (see US-5's Known Limitation) — accepted, not fixed, this sprint.

## Constraints

- Must: Copy Signpost claim lines verbatim as checklist row labels — no inference, paraphrase, or
  normalization. This is always the agent's act (US-1); the hook never authors a row.
- Must: Require tool-call-backed evidence per row, verified against actual transcript tool-call
  entries — self-report (a cited file:line/command-output asserted without a corresponding real
  tool call) does not satisfy the requirement.
- Must: Represent each row's verification state as one of exactly two forced literal status
  values, `verified` or `unverified` — no boolean flag, no third state, no free-form disclosure
  text standing in for status.
- Must: Preserve the archived first-turn-contract mechanism's exact trigger surface — Stop-hook,
  first reply of session only, gated on session-queue briefing marker presence, `stop_hook_active`
  bypass unchanged — including its known first-turn-detection limitation (US-5), accepted as-is.
- Must: Fail closed (block) when the Signpost heading is entirely absent, or present with
  non-blank content but zero parsed claim lines, on a turn this mechanism is gated on.
- Must: Evaluate every parsed Pillar row for real tool-call backing, including a row whose label
  matches no Signpost line — no conforming row escapes evaluation.
- Must: Scope this sprint's implementation to agent-rig only (Slice 5's forced Pillar syntax via
  agent-rig's own gitignored `CLAUDE.md`, Slice 6's wiring of agent-rig's own
  `.claude/settings.json`) — do not modify any other roster repo's settings, hook files, or
  CLAUDE.md.
- Must: Document, for the agent, the active transcript self-lookup step required to cite a real
  `tool_use_id` — this is not automatically visible in a normal reply.
- Must not: Introduce a retry-count/attempt-ceiling loop on this mechanism's own FAIL path.
- Must not: Reintroduce free-form prose sections in the Pillar section that an evasion could hide
  in.
- Must not: Have the hook author, generate, or otherwise write row text into the agent's reply —
  a Stop-hook can only read an already-emitted reply and block or allow it.
- Must not: Modify, disable, or otherwise affect the archived first-turn-contract mechanism as it
  continues running, unchanged, in the other nine roster repos.
- Assumes: The Signpost section format (claim lines the hook can parse) remains structurally
  stable — if Signpost's own format changes shape, this mechanism's row-parsing/verification step
  would need re-validation.
- Assumes: This sprint's scope is agent-rig only; the archived first-turn-contract mechanism
  remains the live mechanism in the other nine roster repos until a separate, later sprint
  propagates this redesign to them. No other consumer of the Signpost/Pillar convention within
  agent-rig itself exists in the record — that "no other consumer" claim is scoped to agent-rig,
  not to the roster as a whole.
