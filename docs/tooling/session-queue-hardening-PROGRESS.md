# Progress: session-queue-hardening (lite)

## Status: COMPLETE — Frank binding forge-gate PASS (attempt 2 of 3, both layers, no PROVISIONAL); orchestrator independent re-derivation AGREES. See GATE-LOG.md. FOOTER repair observed firing live and compliant 2026-08-14 (see "FOOTER repair — CLOSED" below) — all done-conditions met.

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
Step: SESSION CLOSED 2026-08-13. Branch pushed (`@{u}` == HEAD), NOT merged to main — Danny
declined a PR as ceremony for work already reviewed three times. LORE closure capture
`2e117448-c898-472e-a89c-b7621640edca`, which supersedes the stale 2026-07-21 queue row
`85ce19a5`.

**First capture ever written carrying `writer-session-id`** — verified end-to-end after writing:
the probe's parser extracts `9c760bae-…` from the live row. Until now no such row existed, so every
run necessarily landed in UNKNOWN. Next session is the first that can exercise the writer-known
branch.

REMAINS UNMET: the hook has never been observed firing in a real session. State is CODE-MERGED,
deliberately not LIVE.
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

---

## Defect repair 2026-08-14 — first live fire of the hook

The hook fired in a real session for the first time (observed as SessionStart `additionalContext`;
tag resolution to `2e117448` correct, writer-known staleness branch fired for the first time ever,
predicted false `45e3ed27` entry did not appear, LORE priming not masked). The sprint's last unmet
done-condition is met. Two defects surfaced *because* it fired.

- **FOOTER was a labelling rule, not a work rule — FIXED.** Prior text: "label what you took as
  `Signpost:` and label separately as `Pillar:`". It specified no order, set no completeness bar,
  and forbade no third bucket. The reading agent led with Pillar and closed with a "not yet
  verified this session" list, twice — both fully compliant with that wording. The instruction
  produced the behaviour the sprint exists to prevent, and did so on its first live run.

  New FOOTER mandates a numbered pre-reply sequence (1. SIGNPOST orient → 2. PILLAR open the
  sources, "now, not after you report"), mandates that report order explicitly ("Reversing the
  order reports conclusions before their evidence and is wrong even when every fact in it is
  right"), and states "There is no third section" — an unchecked claim is unfinished work, not a
  finding, and the only exit is a BLOCKER naming what would unblock it, never a to-do.

- **The test suite was validating a file the harness never executes — FIXED.** `tests/` loaded
  `reference/session_queue_probe.py`; `.claude/hooks/session-queue.sh` runs
  `scripts/session_queue_probe.py`. The two were byte-identical, so all 15 tests passed and the
  gap was invisible. Last session's "pytest 15 passed" therefore did not cover the shipped
  artifact, and the FOOTER — the single string the entire mechanism exists to deliver — had no
  test at all. That is how a defective instruction cleared a binding Frank gate.

  Tests now load `scripts/`. §4 requires the two copies be kept identical "per existing
  convention — confirm identical after edit, do not let the two drift"; that manual check is now
  mechanical (`test_reference_copy_matches_executed_copy`). The duplication is retained, not
  removed: §4 is locked and human-approved, and `reference/` is the spec'd propagation
  source-of-record convention (`commands/new-project.md:494`, signpost-pillar-propagation Slices
  2/3). A guarded copy honours the locked spec; deleting it would amend one unilaterally.

Three FOOTER-contract tests added (order, no-third-section, verify-before-report). Suite: 19
passed under `pytest` and 19/19 under the fallback runner. The drift guard was proven to fail by
appending a byte to `reference/` (1 failed), then restored to green — not assumed to work.

Stale citation, not corrected: `session-queue-hardening-GATE-LOG.md:30` cites
`reference/session_queue_probe.py:63` for the `.lower()` choke point. The line lives in both
copies; the GATE-LOG is a historical record of what Frank saw and is not rewritten after the fact.

### FOOTER repair — CLOSED 2026-08-14, session `04a0945a-52f3-4af6-ac11-e57fb147a731`

First live fire post-fix, and the reading agent's actual first-turn reply complied: `Signpost:`
section led (queue claims restated as claims), `Pillar:` section followed with the method that
checked each one (git commands, file reads, track-record reads, switchboard/LORE queries listed
inline), and the one open item (whether *this* session's own Stop event would register
`first_turn: true`) was stated as an explicit BLOCKER naming what was missing — not folded into a
"not yet verified" list. Independently corroborated by the mechanism itself: the same turn's
Stop-hook track-record entry (`2026-08-14T13:52:26.567430+00:00`) recorded `decision: "allow"`,
`violations: []` — the probe's own C1/C2/C3 check of that exact turn agreed with the manual read.
Two independent measurements (human-legible compliance + probe verdict) agree. N=1 live fire,
behaviour matches the hypothesis. This closes the sprint's last open done-condition.

<details><summary>Prior state (superseded by the above)</summary>

The new FOOTER is a hypothesis about how a reading agent responds to it. **N=0 live fires
post-fix.** The three FOOTER tests pin the *string*, not the *behaviour* — they prevent the wording
regressing, and that is all they do. Citing "19 passed" as evidence the defect is fixed would be
the founding-postmortem error again: a green count measuring internal consistency, not validity.

What actually closes this: the next SessionStart fire in this repo, with the reading agent's
first-turn output captured and checked against the contract — Signpost section first, Pillar
section second with methods, no third section. Until that observation exists, the repair is
built-and-gated, not proven.

(Frank, forge-gate on `ae3fa0d`, 2026-08-14 — raised as a limit he required stated plainly.)

</details>
