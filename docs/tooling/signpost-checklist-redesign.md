# Signpost Checklist Redesign — Tooling Doc

**Status**: LIVE in agent-rig (wired 2026-09-07, Slice 6, commit `079009b` area). Frank binding
forge-gate PASS, attempt 2/3, 2026-09-07 (`docs/specs/signpost-checklist-redesign/PROGRESS.md`).
As of this doc, the gated path has zero real `first_turn:true` executions — all 19/19 live audit
log entries recorded so far are `first_turn:false` (allow) — and Slice 7's real-transcript
validation of the new parsers against a genuine `first_turn:true` reply remains an open, tracked
obligation (forge Carried Condition (1)), not a completed one.
**Spec of record**: `docs/specs/signpost-checklist-redesign/02-ARCHITECTURE.md` (design, all 11
evaluation rules) and `01-REQUIREMENTS.md` (user stories, scope, propagation boundary). This
document does not restate either — read them directly for rationale and edge-case reasoning.
**Replaces**: `archive/first-turn-contract-enforcement/` (its C1/C2/C3 inferred-subject-matching
mechanism was the source of that mechanism's repeated FAILs and is not reused — see
`02-ARCHITECTURE.md` §5.2).

---

## 1. What this is

A `Stop`-hook that gates the first reply of a queue-injected agent-rig session: the agent must
copy each `Signpost:` claim line verbatim into a matching `Pillar:`-section checklist row, citing
either a real transcript `tool_use_id` or the forced literal `unverified`. The hook mechanically
verifies those rows against real transcript data — it never infers what a claim's free-form prose
*means*, only whether the forced, controlled syntax and cited IDs check out.

**Agent-facing row syntax** (exact grammar, what to write) lives in this repo's (gitignored)
`CLAUDE.md`, under "Signpost/Pillar Checklist Row Syntax" — that section is the source of truth
for how to author a row and is not duplicated here.

## 2. Components

| Component | Responsibility | Location |
|---|---|---|
| `scripts/signpost_checklist_probe.py` | Probe core: Stop-hook stdin → block/allow, by parsing and verifying the Pillar rows the agent already wrote. | `scripts/signpost_checklist_probe.py` |
| `.claude/hooks/signpost-checklist.sh` | Wrapper: captures stdin, invokes the probe under a bounded timeout, fails open on any wrapper-level error. | `.claude/hooks/signpost-checklist.sh` |
| `.claude/settings.json` `Stop` entry | Wires the wrapper into the `Stop` event (agent-rig only), alongside the existing `no-preamble-no-meta-narration.sh` entry. | `.claude/settings.json` |
| Track-record log | Append-only, gitignored, per-invocation audit log (block/allow, violated rows, probe error). | `docs/tooling/signpost-checklist-track-record.jsonl` |

## 3. Division of responsibility (agent authors, hook verifies)

A `Stop` hook can only block or allow a turn already emitted — it cannot write into the agent's
own reply. Every checklist row is therefore authored by the agent; the hook's entire job is to
read the reply already produced and check it: does every Signpost line have a matching row, is
each row's declared status honest, and where a row claims verification, is that claim backed by a
real `tool_use_id` found in the transcript. See `02-ARCHITECTURE.md` §1a.

## 4. Forced row syntax (summary only — CLAUDE.md is the source of truth)

```
- [x] <verbatim Signpost line text> (verified: tool_use_id=<id>)
- [ ] <verbatim Signpost line text> (unverified)
```

Row labels are matched by exact string equality against the Signpost line they claim to satisfy —
no paraphrase or fuzzy matching. `(unverified)` is a forced literal, honest-disclosure path and is
never itself a violation. A `tool_use_id` must be a real ID the agent looked up directly in its own
session transcript (an active lookup step, not something already visible in context) — a
fabricated-looking ID will not match anything in `qualifying_calls` and is treated as an unbacked,
false claim. Full grammar and the mandatory transcript self-lookup procedure: this repo's
`CLAUDE.md`, "Signpost/Pillar Checklist Row Syntax."

## 5. Evaluation rules (mechanical, no inferred concepts)

Every check is one of: exact string equality (row label vs. Signpost line), membership in a small
forced vocabulary (`- [ ]` / `- [x]`, the exact suffix syntax, the literal `unverified`), or an
existence lookup against real transcript structure (`tool_use_id` present in a completed tool
call). Full rule set (11 rules, including fail-closed handling of an absent or malformed Signpost
section, duplicate-label/duplicate-ID handling, and unmatched-row handling) is `02-ARCHITECTURE.md`
§5.4 — summarized here only to orient a reader, not restated in full:

- **Rule 0 / 0a** — no Signpost heading, or a heading with non-blank content but zero parsed claim
  lines, both fail closed (block). This is a deliberate divergence from the archived mechanism,
  which allowed a no-Pillar/no-Signpost turn.
- **Rules 1–5** — per Signpost line: missing row, duplicate-label row, stray (non-conforming)
  Pillar-section prose, an `unverified` row (always allowed), a `verified` row with no real backing
  tool call, and a `verified` row whose `tool_use_id` was already claimed by an earlier row in the
  same evaluation, are each their own distinct violation kind.
- **Rule 6** — every Signpost line matched exactly once, each row honestly `unverified` or a
  uniquely-claimed transcript-verified `verified` → allow.
- **Rule 7** — a Pillar row matching no Signpost line is never silently ignored; it is still
  checked for real backing and separately flagged as unmatched.

## 6. Trigger surface (unchanged from the archived mechanism)

Same surface, reused verbatim per `02-ARCHITECTURE.md` §5.1: `Stop` event, only the first reply of
a session, only when the session-queue briefing marker was injected, `stop_hook_active` bypasses
unconditionally. **Known limitation, accepted (2026-09-07, Danny), not fixed this sprint**: the
inherited first-turn detection has a measured gap — 1 of the 10 most recent real agent-rig
transcripts (US-5) — where assistant text emitted before the first tool call in turn 1 causes the
real first reply to be treated as turn 2+ and skipped. See `01-REQUIREMENTS.md` US-5 for the full
acceptance and rationale. **Also note:** as of this doc, the live audit log has zero real
`first_turn:true` executions (19/19 entries are `first_turn:false`/allow) — Slice 7's
real-transcript validation of this trigger surface and the new parsers remains an open, tracked
obligation, not a completed one.

## 7. What this tool does NOT get authority over

- **Whether a cited tool call actually verifies the specific claim it's attached to.** This
  mechanism proves a real, non-`TodoWrite` tool call happened and its ID matches what's cited — it
  does not judge relevance of that evidence to the claim. (Deliberately not rebuilt — see
  `02-ARCHITECTURE.md` §6 anti-patterns.)
- **Other repos.** Per `01-REQUIREMENTS.md`'s Propagation Scope, the archived first-turn-contract
  mechanism remains live, unmodified, in nine other repos on the deployment roster
  (`docs/specs/agent-rig-ddrs/HOOK-DEPLOYMENT-ROSTER.md`). This sprint touches agent-rig only;
  propagating this redesign elsewhere is separate, future, unscoped work.
- **Frank's binding spec/forge gates.** This hook runs at `Stop`, inside a session; it has no gate
  authority and is not a substitute for either.

## 8. Dependencies

Python standard library only (`re`, `json`, `os`, `sys`, `dataclasses`, `datetime`) — no new
third-party dependency, matching the archived probe's footprint.
