# Gate Log: unsourced-threshold-provenance-hook (domain-boundary-provenance-hook)

## Spec Gate
Counter: 3/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-09-05 | FAIL | Layer 1 FAIL (Layer 2 PASS, non-PROVISIONAL). F1 (blocking): `log_only` mode gate silently makes the incumbent's LOCKED deny behavior conditional, but LOCKED spec §6/AC4 and Roadmap Slice 11 still say the cross-domain pass's deny is unconditional/must-not-contradict — undocumented contradiction. F2 (blocking): Architecture §11 cites `docs/tooling/domain-boundary-manifest.json` as an existing integration point; that file doesn't exist and never has. F3 (non-blocking): stale "5 corrections owed" language when all 5 are already applied. F4 (non-blocking): DDR-006, DDR-INDEX row 006, HOOK-DEPLOYMENT-ROSTER.md, and INTAKE.md all describe the incumbent's state differently and all are wrong in some way. F5 (observation only): context-2 name-gate is substring not word-boundary (`cap` fires on `escape`/`capture`) — PROVISIONAL, no action required this gate. | `.gate-snapshots/spec/attempt-1/` |

| 2 | 2026-09-05 | PASS | Layer 1 PASS, Layer 2 PASS (non-PROVISIONAL). Attempt 1's two blocking findings (F1 mode-gate/LOCKED-doc contradiction, F2 false manifest-file claim) both confirmed resolved against live source. 4 carried conditions (non-blocking, must land before docs treated as locked / before forge-start): (1) DDR-006 + DDR-INDEX row 006 conflate spec-gate 3/3 with forge-gate attempt count — fix wording; (2) Roadmap HALT Check still has stale "not silently patched" paragraph contradicting Architecture §12's "Applied" status; (3) 01-REQUIREMENTS US-2 AC2 describes an impossible "session-ending action blocked" outcome — this is a PreToolUse hook, fix to "Edit/Write tool call denied"; (4) Architecture §11's LOCKED-doc bullet doesn't mention the mode-gated deny semantics §5 points to it for — add the clause. | `.gate-snapshots/spec/attempt-1/` (attempt 2 made no snapshot-worthy FAIL; INTERVIEW/NORTH-STAR/01-REQUIREMENTS/05-REVIEW confirmed byte-identical to attempt 1's snapshot) |

| 3 | 2026-09-05 | FAIL (COLD, no scope brief — repo+SHA+verdict-required only) | Layer 1 FAIL, Layer 2 PASS non-PROVISIONAL. F1 (blocking, root cause): §2's post-attempt-2 redesign removed the name-gated assignment context entirely to eliminate measured false positives — this also eliminated the hook's ability to flag a NAMED CONSTANT (e.g. `_HEAD_BYTES = 65_536`), which is the exact shape of both source incidents (WHO byte-cap, OQ-5 floor) and the literal text of NORTH-STAR's declared intent ("at its point of definition"). Live scan: 32 candidates, 31 excluded by `{0,1,-1,2}`, 1 survivor. F2 (blocking): none of the benchmark's cited measurements (84.7%, 32.5%, 76ms) are reproducible from a committed script/corpus — Frank's own re-run got materially different numbers (96.9%, 0% at distance 4-5, 377ms) in the direction that makes the exclusion set MORE dangerous, not less. F3 (blocking): `PROXIMITY_WINDOW = 5` reused with its `owner: wright` tag still live in the actual code (probe.py:50), declared "resolved, no tag needed" on the strength of F2's unreproducible number. F4 (blocking, contradiction): Requirements/Roadmap require a named-owner PROVISIONAL to satisfy the citation check; Architecture's own example marker has no owner and Roadmap Slice 4 says presence-only. Two Sections of the same doc set specify incompatible behavior for the same code path. | `.gate-snapshots/spec/attempt-1/` (attempt-2's PASS was superseded by a post-PASS §2 rewrite the gate never re-verified until this cold attempt) |

Convergence judgment (attempt 3 only): THRASHING
Deep-diagnosis evidence: Direct diff of `.gate-snapshots/spec/attempt-1/02-ARCHITECTURE.md` §2 against current HEAD §2 confirms Frank's diagnosis: attempt 1's design had a name-gated assignment context (context 2) capable of seeing named constants, imperfectly. The benchmark-driven correction (post-attempt-2-PASS, pre-attempt-3) deleted that context entirely to resolve measured false positives, without checking whether doing so preserved the hook's ability to detect the incident shape it exists to catch. No individual attempt's fix "recurred" — each attempt's problems are new, introduced by the previous attempt's own fix. This is regression-via-uncoordinated-correction, not oscillation between the same two states.
Orchestrator independent re-derivation: AGREES — confirmed via direct file diff, not by re-reading Frank's summary. Escalating to Danny: attempt budget (3/3) exhausted, no manual override exists, Frank's FAIL verdict is binding.

## Forge Gate
Counter: 0/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]
