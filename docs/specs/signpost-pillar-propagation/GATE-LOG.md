# Gate Log: signpost-pillar-propagation

## Spec Gate
Counter: 1/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-08-08 | PASS | Layer 1 PASS (all 5 sprint North Star success criteria have concrete slice coverage). Layer 2 PASS, firm, no PROVISIONAL (docs/NORTHSTAR.md non-DRAFT, Established 2026-07-17; sprint matches project Thesis exactly — third data point after DDR-013/forge-start-fix — and corrects Drift-check item 3). Pre-checks all pass: premise (5s budget PROVISIONAL/owner wright, bracketed by two cited measurements), input (Frank opened raw sources directly — session_probe.py, assert_gate_date_coupling.py, new-project.md, re-ran the founding grep against current state), evidence independence (ALPHA-REPORT-REVIEW.md produced by a separate independent Frank dispatch; Layer 2 read docs/NORTHSTAR.md directly, not the sprint doc's self-claim). Verified pass-3 fixes (F1/F2) against current text, not the fix report. Residual non-blocking: RETROFIT-PROCEDURE.md hand-off path to resident agents deferred to forge (has a downstream catch); 05-REVIEW.md's own Status line/checkboxes were stale relative to the applied fixes at verdict time (cosmetic). Orchestrator (Wright) independently re-verified slice-numbering consistency, the timeout=15 resolution, and Citation Constraints' 5-component enumeration directly against file content — agrees with Frank's PASS, no independent FAIL found. | .gate-snapshots/spec/attempt-1/ (not created — PASS on attempt 1, no retry needed) |

Convergence judgment (attempt 3 only): N/A — PASS on attempt 1.
Deep-diagnosis evidence: N/A
Orchestrator independent re-derivation: AGREES — see Findings Summary above for the specific claims independently re-verified (slice numbering, timeout=15 resolution, Citation Constraints component scope).

## Forge Gate
Counter: 1/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-08-09 | FAIL | Not a content defect — Slices 1-9 artifacts independently verified sound (deploy diffs re-checked byte-identical, no unsourced constants, Layer 2 firm PASS on project NORTHSTAR). FAIL is on the sprint's own stated closability criterion (01-REQUIREMENTS.md:113): "Slices 1-9 done AND Slice 10 (market_data pilot) reaches its own PASS." Slice 10 was relayed to alpha via Switchboard (map, not route) this session but not yet executed/reported. Frank: "dispatched" is a signpost, "PASS" is the pillar — gate does not pass on signposts. No rework needed in agent-rig; hold gate open pending Slice 10. | .gate-snapshots/forge/attempt-1/ |
| 2 | 2026-08-09 | PASS | Danny reviewed attempt 1's FAIL and rejected the underlying closability criterion itself as unnecessary ceremony — agent-rig's own forge-gate should not depend on another repo's agent completing work on their own timeline. Requirements/Roadmap/PROGRESS.md amended (commit `db452ad`): closability now requires only Slices 1-9; Slices 10-12 explicitly non-blocking, tracked separately. Frank verified the amendment in the live files and the raw diff (not a summary), confirmed it traces to Danny's own git identity (not self-approved by the doer), re-sampled Slices 1-9 artifacts (still sound, deploy still byte-identical), and checked whether NORTH-STAR.md needed mid-flight amendment per CADENCE's escalation rule — it didn't, since the rejected criterion was never encoded there. Layer 1 PASS, Layer 2 PASS firm (no PROVISIONAL). One stale cross-doc note (PROGRESS.md said Slice 10 "not yet dispatched" when GATE-LOG already recorded it as relayed) — fixed same pass. Orchestrator (Wright) independently re-verified all four deploy diffs still byte-identical — agrees with Frank's PASS, no independent FAIL found. | .gate-snapshots/forge/attempt-1/ (attempt 2 required no new snapshot — no artifact content changed, only the closability criterion in spec docs) |

Convergence judgment (attempt 3 only): N/A — PASS on attempt 2. Attempt 1→2 was not a fix-and-retry cycle on a defect; it was a legitimate criterion correction by the human composer between attempts.
Deep-diagnosis evidence: N/A
Orchestrator independent re-derivation: AGREES — re-read the amended 01-REQUIREMENTS.md/04-ROADMAP.md/PROGRESS.md closability language directly, re-diffed all four Slice 9 deploy targets myself, confirms Frank's attempt-2 findings.

**Post-gate finding (2026-08-10, after forge-gate attempt 2 PASS, before PR #4 review):** a fully blind independent audit (no briefing, no map, no checklist — dispatched per Danny's explicit request as the terminal check before his own review) executed the actual shipped artifacts rather than reading them, and found one real defect: `reference/session-start-probe.sh`'s `timeout 5 ... || true` silently swallowed exit 124, injecting partial probe output into `additionalContext` as if it were complete ground truth — no truncation marker. Exactly the shared-well/silent-discard failure class this sprint's own doctrine (and the project's founding postmortem) warns against.

Fixed in commit `883ae91`: exit status now captured and branched; a "PROBE OUTPUT INCOMPLETE" marker is appended on timeout (124) or any nonzero exit. Applied to `reference/session-start-probe.sh`, the embedded copy in `commands/new-project.md`, and redeployed to `~/.claude/commands/new-project.md` — all three re-verified byte-identical. `02-ARCHITECTURE.md`'s "degrades to slow UX" rationale corrected to match the new behavior. Full 7/7 test suite re-run, no regression.

The fix was independently re-verified twice: once by Frank via live execution (forced an actual timeout and an actual nonzero exit against the real script, confirmed the marker fires in both cases) immediately after the fix landed, and again during a second, fully blind comprehensive review of PR #4 itself (2026-08-10) — which re-executed the hook live in a scratch repo and re-diffed every deploy target independently, arriving at PASS without reference to the first verification. This second blind review flagged that this specific post-gate fix had not yet been recorded in this log (a paper-trail gap, not a content defect) — this entry closes that gap.

Orchestrator independent re-derivation: AGREES — this fix, and both independent verifications of it, were confirmed directly against file content and live execution output by Wright before this entry was written, not taken from either Frank dispatch's summary alone.

---

## Process Gate — Slice 11 proportionality (2026-08-12)

**Not a spec or forge gate.** An independent Frank dispatch judging the sprint's own *rollout
machinery*, triggered by Danny, who judged the Slice 11 rollout over-ceremonious and holding up
other agents' work.

| Dispatch | Date | Verdict | Findings Summary |
|---|---|---|---|
| Process gate, map-not-route briefing (objective + doc locations + what was claimed; Wright's diagnosis and proposed cuts explicitly withheld) | 2026-08-12 | **FAIL** for Slice 11; Slice 12 correctly sized | Slice 11's per-repo binding Frank gate, blast-radius grep, and structured audit record were promoted defaults: controls written for the *cutover* case (US-10 — replacing live executable code with unknown call-sites) inherited by a slice that pastes prose into a file 6 of 8 roster repos do not track. Two findings the orchestrator had not reached independently: (a) **a gate cannot verify a habit** — C4/C5/C7 are followed or not in future sessions, not at install time, so a gate can only confirm text presence and tracked status, which the resident agent self-checks; in the 6 untracked repos a binding PASS would stamp a machine-local, unversioned, unreviewable edit. (b) **Seven "independent unbriefed" gates reading the same already-gated template is one review run seven times** — their unanimity would prove nothing the sprint-level gate did not, an anti-circularity control specified on the wrong axis. Also found step 1's grep redundant with the roster audit. |

**Record provenance — read this before citing the entry.** This entry is **reconstructed by Wright
(orchestrator) from the dispatch result**, written after PR #7 was opened. There is no LORE capture
of the dispatch and no `.gate-snapshots/` directory for it — the dispatch was made in-session and
its transcript is not a durable artifact. The verdict summarized above is therefore **not
independently re-openable** from this repo; a future reader who needs to audit it must re-run an
equivalent dispatch rather than read the original.

This gap was itself caught by a second independent Frank gate (PR #7 review, 2026-08-12), which
correctly refused to accept a binding requirements amendment justified by a verdict with no record —
"a signpost cited as a pillar, in the very doc set that propagates that distinction." Recorded here
rather than silently fixed, because the failure is more useful than the correction: the orchestrator
relaxed a binding control and cited unreadable evidence for it, in a sprint whose entire subject is
not doing that.

**What the verdict authorized** (implemented in PR #7): cut `SLICE-11-INSTRUCTIONS.md` step 1
(blast-radius grep) and step 6 (per-repo Frank gate); drop `frankGateVerdict`,
`frankGateUnbriefed`, `preExistingContent` from the completion record; keep step 0 (tracking
decision), the content steps, the step-5 self-check, a three-field report, and a slimmed LORE
capture; add a secrets/machine-local-path self-attestation for agents who choose to track their
`CLAUDE.md`. **The Slice 12 gate is untouched** — executable artifacts, real blast radius, two live
defects already caught.

**Requirements amendment authorization:** Danny, in-session, 2026-08-12 — US-10 AC4 scoped to
tier 2/3 executable work, tier-1 practice-only explicitly exempt. Asserted in-text here; his own
merge of PR #7 is the traceable sign-off, matching how PRs #5 and #6 were authorized.

Orchestrator independent re-derivation: **AGREES on the substance, and separately re-verified the
factual predicates rather than accepting them** — the 6/8 untracked figure re-run across all 8 repos
with `command grep` (shell `grep` is blind to gitignored files when recursive); the "no Session Start
Behaviour section" finding for `ask-edgar-repo`, `sonic-store`, `runtime/agent-lore` re-confirmed by
direct-path read; `market_data`'s Slice 11 completion (`9159ffd`, `split-to-docs`) confirmed in that
repo. The reconstruction gap above is recorded as a real defect in this log's own evidence chain,
not as a formality.
