# Progress: first-turn-contract-enforcement

## Status: IN_PROGRESS

Spec: `docs/tooling/first-turn-contract-enforcement.md` (LOCKED, Danny 2026-08-14)
Gate log: `docs/tooling/first-turn-contract-enforcement-GATE-LOG.md` (Spec Gate PASS attempt 2/3)
Mode: forge-lite. No `04-ROADMAP.md` — slices derived from the spec's §11 acceptance criteria.

## Slices

- [x] **Slice 1: Probe core** — COMPLETE 2026-08-14 (QC PASS on re-review). — `scripts/first_turn_contract_probe.py`. Stdin parsing; §5.1 gating
      (queue-injection detection via the `HEADER` marker, first-turn determination,
      `stop_hook_active` unconditional allow); C1, C2, C3 predicates; track-record entry write (§6).
      Covers AC 1, 2, 3, 6, 8 (schema half).
- [ ] **Slice 2: Wrapper, wiring, drift guard** — `.claude/hooks/first-turn-contract.sh`;
      fail-open on every probe failure mode; output-shape validation; `reference/` mirror + drift
      test; `.gitignore` entry; `.claude/settings.json` `Stop` wiring **last**, per AC 9 (the §7
      evidence standard must exist before the hook is flipped live — it does).
      Covers AC 5, 7, 8 (ignored-not-dirty half), 9.
- [ ] **Slice 3: Live demonstration** — the part no harness can do. AC 4 requires a compliant turn
      to pass *on a real live session, not the fixture alone*, and AC 10 requires every criterion
      be demonstrated by an executed check. This is its own slice because the sibling sprint's
      entire lesson is that running the script is not the same as the harness running it.
      Covers AC 4 (live half), 10.

## Current

Slice: 2 — Wrapper, wiring, drift guard
Step: Slice 1 stamped APPROVED; dispatching Slice 2
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
