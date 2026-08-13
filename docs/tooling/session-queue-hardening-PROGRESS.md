# Progress: session-queue-hardening (lite)

## Status: IN_PROGRESS — forge-gate attempt 2

## Spec
`docs/tooling/session-queue-hardening.md` — Status LOCKED (Frank binding spec-gate PASS
2026-08-13, both layers; human approval Danny 2026-08-13).

## Slices
- [x] Slice 1: `/lore-close` Step 4 writes `session-queue-meta:` block with `writer-session-id` — COMPLETE (`84844d3`; QC PASS, verified against a committed sibling fork in d-code since no baseline existed)
- [x] Slice 2: probe parses the block; three-way staleness branch (known/N=0, known/N>0, UNKNOWN) — COMPLETE (QC PASS; writer/reader fit verified end-to-end against Slice 1's exact emitted text; healthy steady state confirmed = 0, the case both prior rounds got wrong)

Slice split rationale (lite mode requires the orchestrator to state this before Slice 1): writer-side
and reader-side are independently verifiable. Slice 1 can be checked by running `/lore-close`'s
capture step and reading the block; Slice 2 by feeding the probe a capture with and without it.
Splitting further would be artificial; combining them would make a failure ambiguous between writer
and reader.

## Current
Slice: 2 of 2 complete
Step: Frank binding forge-gate, attempt 2 (attempt 1 FAIL — see GATE-LOG)
Last updated: 2026-08-13

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|

## Notes
- Git flow: PR/feature-branch. Branch `feature/session-queue-injection` already exists (commit
  `85194cb`). Manual-push-only per `CLAUDE.md` — slice commits land locally, nothing pushes without
  Danny's explicit approval.
- Carry-ins from the spec-gate, to reach the forge gate (Frank's disclosures, 2026-08-13):
  1. `CLAUDE_CODE_SESSION_ID` is an **undocumented** env var; "present in every session" is
     induction from one install/version. Re-verify after Claude Code upgrades. Safe only because
     absence degrades to the honest UNKNOWN branch, never a wrong count.
  2. Frank's own resume test bumped the mtime of transcript
     `45e3ed27-5b97-4cd5-ac4c-7196e957a253.jsonl` to 2026-08-13. Until the next `/lore-close`
     writes a fresh queue, the probe will list that session as having run since — **that is a test
     artifact, not real staleness.** Do not treat it as a defect during verification.
  3. Spec §6.3: malformed `writer-session-id` values fall into the UNKNOWN branch, but no test case
     exists yet. Slice 2 must cover it.
- `docs/specs/session-queue-hardening/INTAKE.md` §S2 is **superseded** by the locked spec. Flag at
  the forge gate.
- **RETRACTED — the "locked spec carries a factual error" note was itself false.** This file
  previously claimed spec §4 row 3 was wrong to say the hook needed no change because it "already
  passes stdin through unmodified." **The spec was correct.** A child run as
  `OUT="$(timeout 5 ./child 2>...)"` with no stdin redirect inherits fd 0 and reads the hook's stdin
  normally — verified empirically twice: by Frank at the forge gate, and independently by the
  orchestrator reproducing the old wrapper's exact structure (child received the full JSON payload).
  The `STDIN_FILE` replay is therefore an **out-of-spec robustness hardening** — explicit rather
  than inherited, protecting against a future wrapper edit that consumes stdin — not a required fix,
  and **the locked spec must NOT be amended.**

  Provenance of the error, recorded because the shape matters more than the fact: QC asserted it,
  the implementer relayed it, the orchestrator wrote it into this file, into commit `420c858`'s
  message, and into the forge-gate briefing. Three parties, one unverified source, and nobody ran
  the ten-second experiment. Had the gate passed, the sanctioned next step was to "reconcile" a
  locked, human-approved spec to match a false finding — manufacturing an error in a source of
  truth and stamping it. This is the shared-well failure from the project's founding postmortem,
  executed by the sprint whose subject is not doing that.

  Commit `420c858`'s message carries the same false claim ("without which reader self-exclusion
  cannot function at all"). Branch is unpushed; whether to amend the message or leave this
  retraction as the correction is Danny's call. The correction must be in the record before merge.
- **Uppercase writer-id defect — FOUND by the new tests, FIXED, and covered.** The regex is
  case-insensitive, so an uppercase writer-session-id parsed fine and was returned verbatim, while
  `main()` built the exclusion filename as `f"{writer_id}.jsonl"` against lowercase files on disk.
  Result: `writer_known` went True — the *confident* branch — a count was computed, and the writer's
  own transcript was never excluded. That silently reinstated the round-2 bug for that input shape,
  and did so while asserting a number instead of falling back to honest UNKNOWN. Unreachable via the
  normal writer (the env var is verbatim the lowercase filename) but live for a hand-edited,
  migrated, or corrupted capture.

  Fixed by normalizing at the single extraction choke point (`match.group(1).lower()`), not at the
  filename-build site, so no current or future caller can forget it. Proven by before/after:
  stashed the fix, ran the new downstream test, it FAILED; restored, it PASSED.

  Note the shape: QC and the test-writer both saw this and both called it comment-worthy rather than
  fixable, and the original uppercase test PASSED while the bug was live — it asserted on the regex
  and never touched the exclusion path. A green test measuring internal consistency instead of
  validity, which is the founding-postmortem failure exactly. The suite now exercises the downstream
  path.
- Prior lineage on this predicate: five review rounds, four FAILs, every defect caught externally,
  three of them in this same staleness predicate. The current design was authored by @architect,
  not by the producer, for that reason.
