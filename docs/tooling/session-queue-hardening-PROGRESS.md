# Progress: session-queue-hardening (lite)

## Status: IN_PROGRESS

## Spec
`docs/tooling/session-queue-hardening.md` — Status LOCKED (Frank binding spec-gate PASS
2026-08-13, both layers; human approval Danny 2026-08-13).

## Slices
- [ ] Slice 1: `/lore-close` Step 4 writes `session-queue-meta:` block with `writer-session-id` — PENDING
- [ ] Slice 2: probe parses the block; three-way staleness branch (known/N=0, known/N>0, UNKNOWN) — PENDING

Slice split rationale (lite mode requires the orchestrator to state this before Slice 1): writer-side
and reader-side are independently verifiable. Slice 1 can be checked by running `/lore-close`'s
capture step and reading the block; Slice 2 by feeding the probe a capture with and without it.
Splitting further would be artificial; combining them would make a failure ambiguous between writer
and reader.

## Current
Slice: 1
Step: @code-executor
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
- Prior lineage on this predicate: five review rounds, four FAILs, every defect caught externally,
  three of them in this same staleness predicate. The current design was authored by @architect,
  not by the producer, for that reason.
