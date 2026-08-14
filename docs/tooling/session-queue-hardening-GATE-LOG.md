# GATE-LOG — session-queue-hardening (lite)

Spec: `docs/tooling/session-queue-hardening.md` (LOCKED).
Implementation: `docs/tooling/session-queue-hardening-PROGRESS.md`.

## Spec Gate

| Attempt | Date | Verdict | Findings Summary |
|---|---|---|---|
| 1 | 2026-08-13 | **PASS** | Design authored by `@architect` (not the producer — three of the four prior defects in this predicate were the producer's, each time revised by the same author). Frank verified the load-bearing claim himself rather than accepting it: `$CLAUDE_CODE_SESSION_ID` exists and matches the transcript filename across all 7 top-level transcripts. He then closed a gap the design did not enumerate — whether a **resumed** session gets a new id while the env var holds the old one, which would have been this predicate's fourth relocation of the same bug. Tested empirically: resume reports the same id and appends to the same file; compaction likewise. Identity guarantee holds for fresh, child, compacted and resumed sessions. Layer 1 pass, Layer 2 pass (not PROVISIONAL — `docs/NORTHSTAR.md` Established 2026-07-17, non-DRAFT). His summary of why it is a real fix rather than another patch: *the mechanism is not the env var, it is the epistemic split — compute a count only when the writer is known by exact identity, otherwise say UNKNOWN and say why.* Disclosures: the env var is undocumented (induction from one install; re-verify after upgrades), and his own resume test bumped transcript `45e3ed27…`'s mtime, which will read as staleness until the next close — his artifact, not real. |

Human approval: Danny, 2026-08-13.

---

## Forge Gate

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-08-13 | **FAIL** | Not a code defect — Frank verified the mechanism sound (writer/reader fit, legacy row → UNKNOWN, healthy steady state → 0). FAIL on **integrity of the record**. (a) The "locked spec carries a factual error" note was itself false: the spec's §4 row 3 correctly said the hook needed no stdin change, because a child run as `OUT="$(timeout 5 ./child)"` inherits fd 0 and reads the caller's stdin. Frank tested it; the orchestrator independently reproduced it. The false claim originated in QC, was relayed by the implementer, and was written by the orchestrator into PROGRESS.md, commit `420c858`'s message, **and this gate's own briefing** — three parties, one unverified source, nobody ran the ten-second experiment. Had the gate passed, the sanctioned next step was amending a locked, human-approved spec to agree with the error. Frank: *"manufacturing an error in a source-of-truth and stamping it at a gate."* (b) Spec §6.3 set a committed test as a done-condition; the slice was marked complete with no such artifact. Layer 2 passed. | `.gate-snapshots/session-queue-hardening/forge/attempt-1/` |
| 2 | 2026-08-13 | **PASS** | Both attempt-1 grounds cured at the root, verified in primary artifacts: the retraction in PROGRESS.md names the shared-well shape that produced the error rather than just deleting the sentence; `21f3bb1` (amended from `420c858`) carries "THE SPEC WAS RIGHT / the locked spec is NOT to be amended"; `tests/test_session_queue_probe.py` exists and passes. Frank re-ran the suite himself under both runners, diffed the attempt-1 snapshot himself, and byte-compared both probe copies and repo-vs-installed `lore-close.md` himself — nothing rests on the implementers' account. Snapshot diff is exactly what was claimed and nothing else. On the "green against itself" concern the briefing raised: the uppercase test is no longer a regex-only tautology — it places a real lowercase file on disk, feeds an uppercase capture value, and asserts through `newer_session_transcripts` that the writer is excluded. Layer 1 pass (every §4 row implemented as specified). Layer 2 pass, **not PROVISIONAL**. | — (PASS) |

Convergence judgment (attempt 3 only): N/A — PASS on attempt 2. Attempt 1→2 was a genuine
fix-and-retry on defects of record integrity, not a criterion change.

**Orchestrator independent re-derivation (attempt 2): AGREES — no independent FAIL found.**
Re-derived from the artifacts, not from Frank's summary: ran the 15-test suite myself (15 passed);
`cmp` confirmed both probe copies byte-identical and repo `commands/lore-close.md` byte-identical to
the installed `~/.claude/commands/lore-close.md`; confirmed the uppercase fix sits at the single
extraction choke point (`reference/session_queue_probe.py:63`, `match.group(1).lower()`) rather than
at a call site — the difference between fixing a bug and fixing one caller; and ran the probe live,
confirming it emits `STALENESS UNKNOWN` (correct for today's legacy row), the `DISCREPANCY` block,
and `PROVENANCE`, with `hookEventName == "SessionStart"`.

### Residual limits, carried forward rather than closed

1. **Never observed firing in a real session.** Every check to date — mine, Frank's, every
   implementer's — has been manual invocation or a synthetic harness. This is the last unmet
   done-condition and it is the actual acceptance test.
2. **The writer-known path cannot fire until this ships.** No LORE row can carry `writer-session-id`
   before `/lore-close` writes one. Chicken-and-egg, not a skipped check; the absent-field case
   degrades to the honest UNKNOWN branch, which was observed live.
3. **`45e3ed27…`'s bumped mtime** will surface as one false stale entry on the first real
   writer-known run. Reviewer's test artifact.
4. `CLAUDE_CODE_SESSION_ID` is undocumented; "present in every session" is induction from one
   install and version. Re-verify after Claude Code upgrades. Safe only because absence degrades to
   UNKNOWN, never a wrong count.
5. Spec §6.2's *suggested* "only sees this machine's install" trailing note is not in the emitted
   text. Phrased as a suggestion in an open-questions section, so not a done-condition — a two-line
   improvement worth taking eventually.

### Lineage, recorded because the pattern is the point

Six review rounds across this artifact and its spec; five FAILs; **every defect caught externally,
none self-caught**, and three of them in this one staleness predicate. That is why the design was
handed to `@architect` and the slices to separate implementers rather than authored by the producer
who kept revising the same sentence. The uppercase-id defect is the sharpest instance: two prior
reviewers each saw it and judged it comment-worthy rather than fixable, and its original test
**passed while the bug was live** — it asserted on the regex and never touched the exclusion path.
A green test constraining code against itself rather than against reality, which is this project's
founding failure mode reproduced in miniature.
