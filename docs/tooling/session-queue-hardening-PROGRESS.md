# Progress: session-queue-hardening (lite)

## Status: IN_PROGRESS

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
Step: Frank binding forge-gate
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
- **Locked spec carries a factual error (QC, Slice 2).** §4 row 3 states
  `.claude/hooks/session-queue.sh` needs "No change... it already passes stdin through unmodified."
  False: the wrapper did not pass stdin at all before this work. Without the `STDIN_FILE` replay
  edit, §2b's reader self-exclusion cannot function. The change is required, correct, and in-scope
  in substance — but the spec's premise about it is wrong and should be reconciled rather than left
  to mislead the next reader. Surfaced at the forge gate, not silently patched.
- Edge noted by QC, not fixed: the writer-id regex is case-insensitive, so a hand-edited uppercase
  UUID would build an exclude filename that won't match the lowercase file on disk. Unreachable via
  the writer (the env var is verbatim the filename); worth a comment only.
- Prior lineage on this predicate: five review rounds, four FAILs, every defect caught externally,
  three of them in this same staleness predicate. The current design was authored by @architect,
  not by the producer, for that reason.
