# Progress: first-turn-contract-enforcement

## Status: COMPLETE — Frank binding forge-gate PASS, both layers, no PROVISIONAL

Spec: `docs/tooling/first-turn-contract-enforcement.md` (LOCKED, Danny 2026-08-14)
Gate log: `docs/tooling/first-turn-contract-enforcement-GATE-LOG.md` (Spec Gate PASS attempt 2/3)
Mode: forge-lite. No `04-ROADMAP.md` — slices derived from the spec's §11 acceptance criteria.

## Slices

- [x] **Slice 1: Probe core** — COMPLETE 2026-08-14 (QC PASS on re-review). — `scripts/first_turn_contract_probe.py`. Stdin parsing; §5.1 gating
      (queue-injection detection via the `HEADER` marker, first-turn determination,
      `stop_hook_active` unconditional allow); C1, C2, C3 predicates; track-record entry write (§6).
      Covers AC 1, 2, 3, 6, 8 (schema half).
- [x] **Slice 2: Wrapper, wiring, drift guard** — COMPLETE 2026-08-14 (QC PASS on re-review). — `.claude/hooks/first-turn-contract.sh`;
      fail-open on every probe failure mode; output-shape validation; `reference/` mirror + drift
      test; `.gitignore` entry; `.claude/settings.json` `Stop` wiring **last**, per AC 9 (the §7
      evidence standard must exist before the hook is flipped live — it does).
      Covers AC 5, 7, 8 (ignored-not-dirty half), 9.
- [x] **Slice 3: Live demonstration** — COMPLETE 2026-08-14, new session `04a0945a-52f3-4af6-ac11-e57fb147a731`.
      Track-record entry `2026-08-14T13:52:26.567430+00:00`: `session_id: 04a0945a-...`,
      `queue_injected: true`, `first_turn: true`, `decision: "allow"`, `violations: []`. First
      harness Stop event where the queue was injected AND the turn was scored as first-turn —
      C1/C2/C3 executed against a real transcript, not the fixture, and the reading agent's actual
      Signpost-then-Pillar turn (this session's prior turn) passed with zero violations.
      Covers AC 4 (live half), 10.
- [x] **Frank binding forge-gate** — PASS, both layers, no PROVISIONAL. See
      `first-turn-contract-enforcement-GATE-LOG.md` `## Forge Gate` for the verbatim verdict.

## Current

Slice: 3 — COMPLETE. Frank binding forge-gate PASS (both layers, no PROVISIONAL). All done-conditions
met; sprint ready for PR review / merge.
Step: Forge-gate verdict transcribed to GATE-LOG.md.
Last updated: 2026-08-14

## Fix Attempts

| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| — | — | — |

## Notes

- **Branch decision:** this work is being cut from `feature/session-queue-injection`, not from
  `main`. The spec's §5.1 queue-injection predicate keys on the literal `HEADER` string in
  `scripts/session_queue_probe.py`, and both that probe and the rewritten `FOOTER` this hook
  enforces exist **only on that unmerged branch**. A branch cut from `main` would carry a spec
  referencing code that isn't there.
- **Deferred, tracked here so it is not lost:** `session-queue-hardening`'s FOOTER repair is still
  open at N=0 live fires. Slice 3's live session is the natural point to close it — one real
  SessionStart fire with the first-turn output checked against the contract satisfies both that
  sprint's standing instruction and this sprint's AC 4.

## Slice 1 — record

**QC FAIL then PASS.** First QC review found a blocking defect: the queue-injection marker lives in
a `type: "attachment"` record (`attachment.content`, no `message` key), and `extract_texts` read
only `message.content`. `queue_injected` was `False` on any real transcript, so C1/C2/C3 and block
emission were **unreachable in production** — the hook was inert, and failed silently, logging
`queue_injected: false` allows. §7's "zero false positives" bar would have been trivially satisfied
by a mechanism that never fires.

All 12 tests were green because every one routed through a synthetic `_queue_marker_record()`
emitting `{"type":"user","message":{...}}` — a shape that does not occur for queue injection. This
is the spec's own §10 anti-pattern (a predicate that cannot fire against real data while every test
passes), reproduced one layer over from where it was written down. Third occurrence of this class
in this repo.

Fixed on both halves: `extract_texts` now unions `_extract_message_texts` and
`_extract_attachment_texts` (`content`/`stdout`, string and list shapes); and
`tests/fixtures/real_transcript_turn1.jsonl` was added — 8 records lifted verbatim from the real
session transcript, structure preserved, payloads redacted (public repo). Three tests drive it
directly, including a negative control with the marker record stripped, proving detection keys on
the marker rather than on the file existing.

**Verified by execution, not inspection:** real transcript truncated to the true end of turn 1
blocks the known C1 violation end-to-end (previously: empty stdout, allow); `pytest tests/` 34
passed, fallback 15/15; **mutation test** — `_extract_attachment_texts` replaced with `return []`
→ 8 failed, restored → 34 passed, so the suite detects this specific regression rather than merely
covering the path. QC re-derived all of it against the unredacted transcript independently.

**Process note worth keeping:** the orchestrator's first mutation attempt targeted the wrong
function signature, applied nothing, and returned green — one step from being reported as "the
tests still miss it." Caught only by confirming the mutation was present in the file before
trusting the result. Verify the instrument changed before believing what it measures.

**Residual, named not fixed (QC):** all 34 tests derive their record shape from one host and one
Claude Code version. If the transcript shape changes they move together and stay green while the
hook goes inert again. §12 requires re-verification at version change; nothing in Slice 1 guards
it, and Slice 1's spec does not ask it to.

**Carried to Slice 2:** `docs/tooling/first-turn-contract-track-record.jsonl` shows as untracked
until the `.gitignore` entry lands (§11 item 7). It must not ship without it.

## Slice 2 — record

**QC FAIL then PASS.** The wrapper failed open correctly on every mode tried, but wrote **no
track-record entry** on the three paths where the probe cannot write its own — timeout kill,
non-executable, truncated stdout. Measured: real probe +1, hung probe 0, non-executable 0.

Why that blocked: §3.4 step 4 and §6 both require it. Without it, a permission change, bad merge or
hang makes the hook permanently inert while the log accumulates clean allows and zero errors — and
§7's bar then reads a growing denominator with zero blocks and zero errors and passes its "zero
false positives" clause **on a dead hook.** Slice 1's silently-inert defect one layer up, with the
audit trail that would have exposed it being the missing piece.

Fixed via `write_probe_error()` on timeout (124/137), non-zero exit, and exit-0-malformed-shape.
Verified independently: all four paths now +1, no duplicates, and every emitted line's key set is
exactly equal to §6's `TrackRecordEntry`.

**The check that mattered most was the positive control**, not the fault injection: a wrapper that
swallowed everything would have passed all five fail-open tests while shipping a hook that never
blocks. A real C1 violation still emits `{"decision":"block",...}` through the wrapper unchanged.
Fail-open, not fail-always.

**5s timeout re-justified rather than inherited.** The value survives — QC measured this probe at
167ms on a 5.4 MB / 3203-record transcript, 85ms on 1.9 MB, ~30x headroom — but the borrowed
rationale did not transfer. `session-queue.sh` sets 5s so its *inner* 3s connect timeout fires
first and yields a real error instead of a silent kill; this probe has no inner timeout, so a kill
here is always the silent case. Comment now cites the measurement on this probe's own terms.
Promoted default caught before it set.

### Residuals carried, named not fixed

1. **`probe_error` lines write `queue_injected: false` / `first_turn: false` as facts when they are
   unknowns.** The direction is safe — those entries are excluded from §7's 10-entry denominator,
   so a hook dead for a whole session accrues zero propagation credit and cannot manufacture
   evidence. But **§7's reviewer must discriminate on `decision`, and must never read
   `queue_injected`/`first_turn` on an error line.** An error rate computed as
   `probe_errors / qualifying invocations` divides by a denominator that structurally excludes
   every error.
2. **The malformed-shape branch's assumption is unenforced.** A probe that writes its own line,
   then emits malformed stdout, then exits 0 produces two entries. Unreachable today — the shipped
   probe has exactly one stdout write, valid by construction — and the comment now states the
   assumption, why it holds, and the bounded consequence rather than asserting a guarantee the code
   does not have.
3. **An unreadable `transcript_path` is indistinguishable from "not queue-injected."** Both log
   `queue_injected: false` and allow. §5.1 specifies failing toward not-injected, so changing this
   is a spec amendment, not an implementation fix. QC concurred that carrying it is correct.

## Hook is LIVE — first harness-fired invocation observed

`.claude/settings.json` gained its `Stop` entry (wired by the orchestrator, not delegated; the
global `switchboard/relay-hook.js` entry is untouched — repo-local settings are additive). AC 9's
precondition held: §7's evidence standard existed in the locked spec before the flip.

Confirmed by attribution, not assumption — the log's first three entries carry `sid=qc2` (QC's
fault injections); the fourth carries the real session id:

```
2026-08-14T13:39:02  sid=cb179922-d422-4af4-91f9-329633de92b5  allow  qi=True  ft=False
```

Written by the harness on a real `Stop` event. **Updated at session close: four harness-fired
entries now, all carrying this session's id, one per turn** — the hook fires on every `Stop`, not
once by luck. It proves the wiring, marker detection against
harness-written data (the exact defect QC caught in Slice 1), correct turn-scoping, and the log
write — and `git status --porcelain` still shows no track-record entry, so `lore-close`'s `dirty:`
derivation survives.

**What it does NOT prove, stated plainly:** `first_turn: false` means C1/C2/C3 never ran. AC 4's
live half requires a *new* session where the queue is injected and the first turn is actually
checked. **Slice 3 is not closeable from inside this session.**


## Close-out 2026-08-14 — verified states

- **Slices 1 and 2: CODE-MERGED and pushed.** `git log` shows `e46c911` and `4169a0b` on
  `feature/first-turn-contract-enforcement`, `@{u}` == HEAD, PR #9 (draft, 14 commits).
- **The hook itself: LIVE.** Runtime probe, not inference — four entries in the track-record log
  carry this session's id (`cb179922-…`), written by the Claude Code harness on real `Stop` events
  across four separate turns. Marker detection works against harness-written transcript data
  (`queue_injected: true` every time), turn-scoping works (`first_turn: false`, correctly out of
  scope), and the log write works. `git status --porcelain` is empty, so the ignore rule holds and
  `lore-close`'s `dirty:` derivation is intact.
- **Slice 3: PENDING, and not closeable from inside this session.** Every live fire recorded
  `first_turn: false`, so C1/C2/C3 have never executed under the harness. AC 4's live half and
  AC 10 require a *new* session where the queue injects and the first turn is genuinely checked.

**Correction to an earlier claim in this session:** I twice described the sibling branch as sitting
at "18 unpushed commits." Both halves were wrong. `feature/session-queue-injection` is **6 ahead of
`main`** and fully pushed; the 18/22 figure was this branch's own count against `main`, misread as
the sibling's. Current: sibling 6 ahead of main, this branch 16 ahead of the sibling, 22 ahead of
main, 0 unpushed.
