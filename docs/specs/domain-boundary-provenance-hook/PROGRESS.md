# Progress: unsourced-threshold-provenance-hook (domain-boundary-provenance-hook)

## Status: IN_PROGRESS (all 12 slices complete, awaiting Frank binding forge-gate)

## Slices
- [x] Slice 1: Extract `run_cross_domain_pass()` — COMPLETE (2026-09-05, commit `3a5de4e`). QC found one FAIL (missing PassResult TypedDict), fixed and re-verified PASS. 162/162 tests passing.
- [x] Slice 2: Mode Config Loader — COMPLETE (2026-09-05, commit `baa2261`). QC found one FAIL (missing schemaVersion validation), fixed and re-verified PASS. 171/171 tests passing.
- [x] Slice 3: `detect_threshold_literals()` — COMPLETE (2026-09-05, commit `dcbd346`). QC found one FAIL (missing type annotations), fixed and re-verified PASS. 2/2 real-incident recall confirmed by direct execution. 186/186 tests passing.
- [x] Slice 4: `has_threshold_provenance_marker()` — COMPLETE (2026-09-05, commit `b21fd11`). Real bug found (N/A owner regex bypass) + annotation fix, both re-verified PASS. 202/202 tests passing.
- [x] Slice 5: `run_local_threshold_pass()` — COMPLETE (2026-09-05, commit `b05bd46`). Clean PASS, no fix cycle. No-manifest-coupling and mode-no-op verified by direct execution. 209/209 tests passing.
- [x] Slice 6: `combine()` — COMPLETE (2026-09-05, commit `e090723`). Real bug found (signature drift causing "violation in None") + mode fail-safe hardening, both re-verified PASS. F1 named regression test (Frank attempt-1 finding) + blocking-mode companion confirmed real. 217/217 tests passing.
- [x] Slice 7: `TrackRecordEntry` Schema Migration + `run()` Restructure — COMPLETE (2026-09-05, commit `09e2569`). 19 test failures diagnosed as stale expectations/wrong fixtures (not implementation bugs), fixed and QC-verified by direct execution — no weakened assertions. Both passes + combine() now genuinely wired into run(). 222/222 tests passing.
- [x] Slice 8: Wrapper Updates — COMPLETE (2026-09-05, commit `56da5f4`). Real bug found (hidden `head` dependency in grep/sed fallback) + fixed, QC-verified byte-for-byte fail-safe parity with Python. 25/25 wrapper tests, 222/222 Python tests passing.
- [x] Slice 9: Test Corpus Additions — COMPLETE (2026-09-05, commit `51c6d8c`). Soundness-language check took 3 fix iterations (own independent verification caught 2 real regressions the fix reports missed) before correct redesign (exclude docstrings/comments, scan only reason-message strings). Adversarial final QC confirmed real mutations still caught. 236/236 tests, 25/25 wrapper tests passing.
- [x] Slice 10: Live Wiring — COMPLETE (2026-09-05, commit `b57d9f1`). Wiring correctness fully verified by direct execution (exit 0, no block, correct schema). Live Claude-Code-triggered fire deferred to Slice 12/next fresh session — settings.json hooks load at session start, structurally can't fire in this same session. 261/261 tests passing.
- [x] Slice 11: Documentation — COMPLETE (2026-09-05, commit `3a2f7cc`). LOCKED doc §2-§10 verified byte-identical, addendum traced word-by-word against real code and confirmed accurate, roster row correctly separates wired-status from verification claim.
- [x] Slice 12: End-to-End Verification — COMPLETE (2026-09-05, commit `7e22e41`). Real live-fire evidence found and verified: this session's own Edit calls fired the hook post-Slice-10 with zero restart, disproving Slice 10's session-restart assumption. Runtime measured (median 1.15ms). Findings captured in Architecture §14. All 12 slices now complete.
- [ ] **Frank binding forge-gate** — PENDING, invoking cold (repo+SHA+verdict-required only). Runs once, only after every slice above is checked
      off. Do not set `Status: COMPLETE` before this line is checked and its verdict is
      transcribed into this file's `## Forge Gate` section — "all slices done" is not "sprint done."

## Current
Slice: 12
Step: verification (no new agent role — end-to-end check)
Last updated: 2026-09-05

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| test_threshold_marker_placeholder_owner_* (Slice 4) | 1 | `owner: N/A` captured as `"N"` (regex char class excluded `/`), not blocklisted — FIXED, verified, 202/202 passing under pytest |
| 19 tests (Slice 7, run() restructure) | 1 | Not an implementation bug: stale `decision` expectations on .py fixtures that now correctly trip the new local-threshold pass (e.g. `EXTERNAL_CAP_V1 = 5` in src/app.py), plus 2 tests using .json fixture paths where .py was needed to exercise local-threshold at all. Routed to @test-writer for per-case diagnosis, not blanket fix. |
| wrapper jq-fallback test (Slice 8) | 1 | grep/sed fallback secretly depends on `head`, not available in test sandbox — resolved to `log_only` instead of `blocking` (fail-safe worked, but the fallback tier itself is fragile). Fix: remove `head` dependency, use pure grep/sed. |
| soundness-language grep test (Slice 9) | 3 | Attempt 1: under-sensitive. Attempt 2's `\bvalid\b` too broad+too narrow, corrected to `\bvalidated\b`. Attempt 3: independently re-ran and found `\bverified\b` ALSO too broad — trips on legitimate "live-verified" in the module docstring. Bare word-boundary matching against arbitrary source strings is the wrong approach; redesigning to scan only reason-message-shaped strings, or require proximity to a citation/soundness-relevant noun. |

## Notes
- 2026-09-05, Slice 10: `.claude/settings.json`'s hook config is loaded at session start.
  This session added the new PreToolUse entry mid-session, so this session's own tool
  dispatch will never pick it up. QC proved the wrapper/probe behave correctly on a real
  payload via direct invocation (wiring shape, JSON validity, and execution all verified),
  but the "a live Claude Code Edit/Write call triggers the hook" Done-When item can only be
  confirmed from a FRESH session in this repo, after this session ends. Slice 12
  (End-to-End Verification) covers this same requirement — deferring final live-trigger
  confirmation there / to the next fresh session, not treating it as a Slice 10 blocker
  since the underlying code is proven correct.
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

### Cycle 2 (post-redesign)

Counter: 1/3 (Cycle 2)

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-09-05 | PASS | Layer 1 PASS, Layer 2 PASS (non-PROVISIONAL). Frank, SHA `5362942`. 3 carried conditions, all confirmed landed against live file content (2026-09-05/06): (1) DDR-006/DDR-INDEX gate-attempt-count wording conflating spec-gate 3/3 with forge-gate attempt count — landed, confirmed by commit history fixing this same session as the PASS; (2) `04-ROADMAP.md`'s "HALT Check" section's stale "not silently patched" paragraph contradicting Architecture §12's "Applied" status — landed, current "HALT Check" section reads clean with no such paragraph; (3) `02-ARCHITECTURE.md` §11's LOCKED-doc bullet missing the mode-gated-deny clause — landed, current §11 explicitly states the `log_only`-vs-`blocking` deny semantics for the LOCKED doc's §6 step 6/AC4 text. | none taken |

## Forge Gate

Counter: 3/3

**⚠️ CAVEAT — no independently-checkable artifacts back attempts 1 and 2.** Independent QC
(2026-09-06) confirmed: no `.gate-snapshots/forge/` directory exists anywhere in this repo. The
only snapshot directory for this sprint is `.gate-snapshots/spec/attempt-1/`. There is no forge
attempt-1 or attempt-2 snapshot, no verdict file, and no GATE-LOG entry. The rows below rest
entirely on the orchestrating agent's own commit messages (commits `f8a887a` and `a25157f`) —
same author, not independent evidence, and not verifiable by anyone else after the fact. The SHAs
themselves are real and in the correct order, so the attempts happened in some form, but the
FAIL/HALT verdict text below has zero artifact-level backing. This is a known gap against this
project's own gate-snapshot procedure — it is being stated plainly here, not papered over with
retroactively-manufactured snapshot directories, which would be worse than the gap itself. The
Snapshot column's prior "created retroactively" claim for attempt 2 was itself inaccurate — no
such directory was ever created; it is corrected below to reflect that.

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-09-05/06 | FAIL | Cold Frank, SHA `f8a887a`. F1 (blocking): wrapper `timeout` PROVISIONAL-owner tag invalid, no committed measurement. F2 (blocking): `01-REQUIREMENTS.md`/roadmap Slice 12 checked complete against a test never actually run — no real Claude-Code-triggered `.py` scan existed in the log; §14 cited timing figures ("60ms/140ms") that appear nowhere in the doc set. F3 (blocking): `PROXIMITY_WINDOW = 5` self-assigned `owner: wright` tag, invalid per Danny's ruling. F4 (non-blocking): stale test-path exclusion set vs. benchmark's, zero-row impact. This attempt's findings drove the fix that became commit `08deb2d` — that fix overreached and deleted the incumbent's `PROXIMITY_WINDOW` mechanism outright, which was itself wrong and is the subject of attempt 2. | **none exists.** No `.gate-snapshots/forge/attempt-1/` was ever created. This row is a retroactive narrative record only, sourced from commit `f8a887a`'s own commit message (same author, not independently verifiable) — not from a snapshot or verdict file. |
| 2 | 2026-09-06 | HALT | Cold Frank, SHA `dda9a89`. F1/F3 (blocking): commit `08deb2d` deleted the incumbent's `PROXIMITY_WINDOW = 5` and its window-based `has_qualifying_marker_in_window` logic, plus the tests proving it — a scope violation, since the Locked North Star explicitly says the incumbent stays untouched. F2 (blocking, HALT-triggering): North Star/`01-REQUIREMENTS.md` still described a named-owner PROVISIONAL tag as a valid satisfying form while the shipped code no longer accepted one — an unresolved divergence between two rulings Frank could not adjudicate himself. F4 (blocking): this exact forge-gate attempt-1 finding/fix cycle went unlogged (see attempt 1's row, added retroactively). F5 (non-blocking): `_TRUNCATION_METHODS`'s comment falsely claimed `ljust` had a corpus citation. F6 (non-blocking): PROGRESS/Roadmap Done-When items asserted obligations (owner-satisfies tests, old test counts) that `08deb2d` had already deleted. | **none exists.** No `.gate-snapshots/forge/attempt-2/` was ever created — a prior version of this row incorrectly claimed one had been "created retroactively"; that claim was false and is corrected here. This row is a retroactive narrative record only, sourced from commit `a25157f`'s own commit message (same author, not independently verifiable) — not from a snapshot or verdict file. |

**Fixes applied since attempt 2, before attempt 3:** incumbent `PROXIMITY_WINDOW`/`has_qualifying_marker_in_window` and its tests/corpus cases restored byte-identical to commit `09e2569` (commit `a25157f`); North Star/Requirements owner-tag language corrected to citation-or-removal only, per Danny's direct ruling 2026-09-06 (commit `ee422d6`); `_TRUNCATION_METHODS` comment corrected to stop claiming a false `ljust` citation. This section (F4) and the slice/Done-When rows below (F6) updated to match current live file state as part of this same fix pass.

| 3 | 2026-09-06 | FAIL | Cold Frank, SHA `5dd5caa`. F1 (blocking): wrapper `timeout 5` (.claude/hooks/domain-boundary-provenance.sh:137-148) unsourced — self-declares "NOT YET BENCHMARKED". F2 (blocking, required Danny): incumbent PROXIMITY_WINDOW=5 (scripts/domain_boundary_provenance_probe.py:54) still carries invalid `owner: wright` PROVISIONAL tag in shipped code; disposition on record was only a DDR-INDEX "idea" filing, not a Danny decision. F3 (blocking): doc set (04-ROADMAP.md, NORTH-STAR.md) still specified a named-owner acceptance form the shipped code and tests reject. F4 (non-blocking): PROGRESS.md's own honesty-caveat paragraph contained a false snapshot claim; a line-number citation error; a self-contradiction between two items. F5 (observation, no action): benchmark corpus totals drift naturally on regeneration since corpus repos are live checkouts; net-flagged/recall numbers unaffected. Layer 1: FAIL (F1-F3). Layer 2: PASS, non-PROVISIONAL. Cross-attempt classification: STATIC — the rule-1 findings (unsourced/invalid-owner constants) had not moved across three attempts, though process findings (fake verification, scope violations, stale claims) did shrink each round. Verdict: FAIL (attempt 3/3 — budget exhausted at the time, escalated to Danny; no override existed under the old rule). | none created for this attempt. |

Convergence judgment (attempt 3): STATIC
Deep-diagnosis evidence: rule-1 findings (unsourced/invalid-owner constants, F1-F3) recurred unchanged in shape across attempts; process-hygiene findings (fake verification, scope violations, stale claims) shrank each round.
Orchestrator independent re-derivation: AGREES.

**2026-09-06, Danny: the 3-attempt cycle/counter mechanism itself is removed, effective now.** Frank is invoked as needed until PASS — no further Cycle/attempt counting or budget tracking applies. This Counter and the Cycle 1 attempt history above are retained as historical record only.

**Progress since attempt 3 (commits `c1cc427`, `0d1cce1`):** wrapper `timeout 5` sourced via real benchmark (F1 addressed); incumbent `PROXIMITY_WINDOW` owner tag replaced with a real citation (F2 addressed); doc/code divergence on the named-owner acceptance form swept across the full doc set (F3 addressed).
