# Progress: unsourced-threshold-provenance-hook (domain-boundary-provenance-hook)

## Status: IN_PROGRESS

## Slices
- [x] Slice 1: Extract `run_cross_domain_pass()` — COMPLETE (2026-09-05, commit `3a5de4e`). QC found one FAIL (missing PassResult TypedDict), fixed and re-verified PASS. 162/162 tests passing.
- [x] Slice 2: Mode Config Loader — COMPLETE (2026-09-05, commit `baa2261`). QC found one FAIL (missing schemaVersion validation), fixed and re-verified PASS. 171/171 tests passing.
- [x] Slice 3: `detect_threshold_literals()` — COMPLETE (2026-09-05, commit `dcbd346`). QC found one FAIL (missing type annotations), fixed and re-verified PASS. 2/2 real-incident recall confirmed by direct execution. 186/186 tests passing.
- [x] Slice 4: `has_threshold_provenance_marker()` — COMPLETE (2026-09-05, commit `b21fd11`). Real bug found (N/A owner regex bypass) + annotation fix, both re-verified PASS. 202/202 tests passing.
- [x] Slice 5: `run_local_threshold_pass()` — COMPLETE (2026-09-05, commit `b05bd46`). Clean PASS, no fix cycle. No-manifest-coupling and mode-no-op verified by direct execution. 209/209 tests passing.
- [x] Slice 6: `combine()` — COMPLETE (2026-09-05, commit `e090723`). Real bug found (signature drift causing "violation in None") + mode fail-safe hardening, both re-verified PASS. F1 named regression test (Frank attempt-1 finding) + blocking-mode companion confirmed real. 217/217 tests passing.
- [ ] Slice 7: `TrackRecordEntry` Schema Migration + `run()` Restructure — IN_PROGRESS
- [ ] Slice 8: Wrapper Updates — PENDING
- [ ] Slice 9: Test Corpus Additions — PENDING
- [ ] Slice 10: Live Wiring — PENDING
- [ ] Slice 11: Documentation — PENDING
- [ ] Slice 12: End-to-End Verification — PENDING
- [ ] **Frank binding forge-gate** — PENDING. Runs once, only after every slice above is checked
      off. Do not set `Status: COMPLETE` before this line is checked and its verdict is
      transcribed into this file's `## Forge Gate` section — "all slices done" is not "sprint done."

## Current
Slice: 7
Step: @code-executor
Last updated: 2026-09-05

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| test_threshold_marker_placeholder_owner_* (Slice 4) | 1 | `owner: N/A` captured as `"N"` (regex char class excluded `/`), not blocklisted — FIXED, verified, 202/202 passing under pytest |

## Notes
- 2026-09-05: `tests/test_domain_boundary_provenance_probe.py` has a legacy standalone `__main__`
  test runner alongside its pytest-collected tests. The standalone runner doesn't support pytest
  fixtures (`tmp_path`), so 12 fixture-using tests (all pre-existing, from Slices 1-2, not Slice 4)
  fail under `python3 tests/test_domain_boundary_provenance_probe.py` direct invocation with
  "list index out of range" — while the same tests pass under `pytest`. This is a pre-existing
  dual-runner inconsistency, not a regression. Pytest is this repo's actual test framework (used
  to verify every slice so far); treating pytest's 202/202 as authoritative. Not fixed in this
  slice — flagging as a known gap, not blocking.

## Spec Gate

Migrated from GATE-LOG.md, 2026-09-05, per the GATE-LOG→PROGRESS.md consolidation (Danny + ledger).

**Cycle authorization note (2026-09-05):** Danny explicitly authorized (this session, via direct instruction) closing out the original 3-attempt cycle below — which ended in a THRASHING HALT at attempt 3, then received a substantive redesign (detection rule fixed against committed benchmark evidence) — and starting a new gate cycle for the redesigned detection rule. This is authorized because the redesign is substantively different work, not a retry of the same design (see the attempt-4 findings and the redesign summary in the Post-HALT note below). This closes the gap both attempt 3's THRASHING finding and attempt 4's F4 flagged: continuing to add attempts to the same counter after a HALT, without recorded human authorization, makes the attempt-limit mechanism decorative.

### Cycle 1 (attempts 1-4, ended: redesign + fixes applied)

Counter: 3/3 (exhausted, HALT — see Convergence judgment below; attempt 4 was a cold re-check against the post-redesign state, not part of the original counted cycle)

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-09-05 | FAIL | Layer 1 FAIL (Layer 2 PASS, non-PROVISIONAL). F1 (blocking): `log_only` mode gate silently makes the incumbent's LOCKED deny behavior conditional, but LOCKED spec §6/AC4 and Roadmap Slice 11 still say the cross-domain pass's deny is unconditional/must-not-contradict — undocumented contradiction. F2 (blocking): Architecture §11 cites `docs/tooling/domain-boundary-manifest.json` as an existing integration point; that file doesn't exist and never has. F3 (non-blocking): stale "5 corrections owed" language when all 5 are already applied. F4 (non-blocking): DDR-006, DDR-INDEX row 006, HOOK-DEPLOYMENT-ROSTER.md, and INTAKE.md all describe the incumbent's state differently and all are wrong in some way. F5 (observation only): context-2 name-gate is substring not word-boundary (`cap` fires on `escape`/`capture`) — PROVISIONAL, no action required this gate. | `.gate-snapshots/spec/attempt-1/` |

| 2 | 2026-09-05 | PASS | Layer 1 PASS, Layer 2 PASS (non-PROVISIONAL). Attempt 1's two blocking findings (F1 mode-gate/LOCKED-doc contradiction, F2 false manifest-file claim) both confirmed resolved against live source. 4 carried conditions (non-blocking, must land before docs treated as locked / before forge-start): (1) DDR-006 + DDR-INDEX row 006 conflate spec-gate 3/3 with forge-gate attempt count — fix wording; (2) Roadmap HALT Check still has stale "not silently patched" paragraph contradicting Architecture §12's "Applied" status; (3) 01-REQUIREMENTS US-2 AC2 describes an impossible "session-ending action blocked" outcome — this is a PreToolUse hook, fix to "Edit/Write tool call denied"; (4) Architecture §11's LOCKED-doc bullet doesn't mention the mode-gated deny semantics §5 points to it for — add the clause. | `.gate-snapshots/spec/attempt-1/` (attempt 2 made no snapshot-worthy FAIL; INTERVIEW/NORTH-STAR/01-REQUIREMENTS/05-REVIEW confirmed byte-identical to attempt 1's snapshot) |

| 3 | 2026-09-05 | FAIL (COLD, no scope brief — repo+SHA+verdict-required only) | Layer 1 FAIL, Layer 2 PASS non-PROVISIONAL. F1 (blocking, root cause): §2's post-attempt-2 redesign removed the name-gated assignment context entirely to eliminate measured false positives — this also eliminated the hook's ability to flag a NAMED CONSTANT (e.g. `_HEAD_BYTES = 65_536`), which is the exact shape of both source incidents (WHO byte-cap, OQ-5 floor) and the literal text of NORTH-STAR's declared intent ("at its point of definition"). Live scan: 32 candidates, 31 excluded by `{0,1,-1,2}`, 1 survivor. F2 (blocking): none of the benchmark's cited measurements (84.7%, 32.5%, 76ms) are reproducible from a committed script/corpus — Frank's own re-run got materially different numbers (96.9%, 0% at distance 4-5, 377ms) in the direction that makes the exclusion set MORE dangerous, not less. F3 (blocking): `PROXIMITY_WINDOW = 5` reused with its `owner: wright` tag still live in the actual code (probe.py:50), declared "resolved, no tag needed" on the strength of F2's unreproducible number. F4 (blocking, contradiction): Requirements/Roadmap require a named-owner PROVISIONAL to satisfy the citation check; Architecture's own example marker has no owner and Roadmap Slice 4 says presence-only. Two Sections of the same doc set specify incompatible behavior for the same code path. | `.gate-snapshots/spec/attempt-1/` (attempt-2's PASS was superseded by a post-PASS §2 rewrite the gate never re-verified until this cold attempt) |

Convergence judgment (attempt 3 only): THRASHING
Deep-diagnosis evidence: Direct diff of `.gate-snapshots/spec/attempt-1/02-ARCHITECTURE.md` §2 against current HEAD §2 confirms Frank's diagnosis: attempt 1's design had a name-gated assignment context (context 2) capable of seeing named constants, imperfectly. The benchmark-driven correction (post-attempt-2-PASS, pre-attempt-3) deleted that context entirely to resolve measured false positives, without checking whether doing so preserved the hook's ability to detect the incident shape it exists to catch. No individual attempt's fix "recurred" — each attempt's problems are new, introduced by the previous attempt's own fix. This is regression-via-uncoordinated-correction, not oscillation between the same two states.
Orchestrator independent re-derivation: AGREES — confirmed via direct file diff, not by re-reading Frank's summary. Escalating to Danny: attempt budget (3/3) exhausted, no manual override exists, Frank's FAIL verdict is binding.

**Post-HALT note:** Danny directed a targeted fix (delete the design regression, not the whole sprint), applying DDR-001's decision matrix. A `benchmark` agent produced committed, re-runnable evidence (`docs/research/domain-boundary-hook-benchmark/`) adopting a measured detection rule (2/2 recall on both real incidents, later re-validated at realistic fragment shapes, 9/9). Multiple correction+re-review cycles followed (see commits `95276ec`..`7d6a9f5`). A fresh cold Frank spec-gate was then run against SHA `7d6a9f5` — logged below as attempt 4. **Whether this counted as a new loop (counter reset) or a continuation of the same 3/3-exhausted loop was not explicitly settled with Danny before this attempt ran — per Frank's own attempt-3 F4 finding that this exact gap makes the counter decorative if not addressed. Resolved after the fact: see "Cycle authorization note" above, where Danny explicitly authorized closing Cycle 1 and starting Cycle 2 for the redesigned detection rule.**

| 4 | 2026-09-05 | FAIL (COLD, no scope brief, SHA `7d6a9f5`) | Layer 1 FAIL, Layer 2 PASS non-PROVISIONAL. F1 (blocking): `02-ARCHITECTURE.md` §0.1 quietly rewrote the binding unsourced-number rule to add a third valid disposition ("a fully-stated executable benchmarking plan") not present in `~/.claude/CLAUDE.md` rule 1 — the `{0,1,-1,2}` exclusion set (60.5% of all candidates, the single highest-leverage constant in the design) has neither a real citation nor a named human owner, riding on this invented option. F2 (blocking, cheap): the shipped regex fallback pattern was widened to match floats in the doc, but the committed script (`scan_thresholds.py`) still has the old integer/boolean-only pattern — doc and evidence describe two different detectors. F3 (non-blocking): one stale sentence about which parse strategy handles the worst-case fragment. F4 (process): this attempt itself — GATE-LOG.md said `3/3, THRASHING, HALT` with no recorded authorization to run a 4th attempt. F5 (carried, out of this sprint's file scope): incumbent's `PROXIMITY_WINDOW = 5` still tagged `owner: wright` (invalid, self-assigned) at `scripts/domain_boundary_provenance_probe.py:50-51`. | none taken — GATE-LOG→PROGRESS.md consolidation superseded the snapshot-before-retry step for this attempt |

**Open, unresolved as of this migration:** (1) F1 — **RESOLVED 2026-09-05**: `{0,1,-1,2}` exclusion set deleted entirely from `02-ARCHITECTURE.md`/`01-REQUIREMENTS.md`/`04-ROADMAP.md` (Danny's decision — ship unfiltered under `log_only`); §0.1's invented fourth rule-1 disposition also deleted. (2) F2 — **RESOLVED 2026-09-05**: `scan_thresholds.py`'s regex fallback pattern fixed to match floats (and its value-parsing branch fixed to not silently drop a matched float); whole-corpus re-run confirmed `results.md`/`candidates.jsonl` unchanged (regex fallback never fires on a whole file in this corpus), and a direct function-level test confirms the fixed pattern now matches a float fragment the old pattern missed. (3) The counter/authorization question F4 raises — **RESOLVED 2026-09-05**: see "Cycle authorization note" above — Danny explicitly authorized closing Cycle 1 and starting Cycle 2 for the redesigned detection rule, this session.

### Cycle 2 (post-redesign, starting now)

Counter: 0/3 (Cycle 2)

## Forge Gate

Counter: 0/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]
