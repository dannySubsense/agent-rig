# Progress: signpost-pillar-propagation

## Status: COMPLETE (forge-gate PASS attempt 2/3; post-gate blind-audit finding fixed and independently re-verified twice — see GATE-LOG.md; PR #4 merged to main, commit `1a7dd01`, 2026-08-10. Slices 10-12 track separately as non-blocking ongoing work — see Forge-closability note below.)

## Branch
`feature/signpost-pillar-propagation` (created from `main` @ `74c20ed`, 2026-08-09)

## Slices
- [x] Slice 1: Independent review of alpha's handoff report (US-9 gate) — COMPLETE (already satisfied; `ALPHA-REPORT-REVIEW.md` produced by an independent Frank dispatch, verdict SAFE TO CITE, 2 mandatory caveats)
- [x] Slice 2: Generalized probe script + hook wrapper (reference artifacts) — COMPLETE (`reference/session_probe.py`, `reference/session-start-probe.sh`, written directly in agent-rig 2026-08-08, verified standalone with zero department-os dependency, `timeout=15` dropped, no project-specific strings)
- [x] Slice 3: `new-project.md` scaffolds Components 1-3 — COMPLETE (2026-08-09; QC round 1 FAIL caught missing live-trace evidence + undocumented/incorrect rollback wording; both fixed; QC round 2 ran its own independent scratch trace, PASS; commit `2bf3068`)
- [x] Slice 4: Session Start Behaviour template (Signpost:/Pillar: + 3-check block) — COMPLETE
- [x] Slice 5: Map-not-route briefing convention template — COMPLETE (Frank map-not-route QC gate PASS; commit `d284917`)
- [x] Slice 6: Assert-convention + sentinel pattern combined doc — COMPLETE (Frank map-not-route QC gate PASS; test-script fix applied for §2.5 negation-detection bug in verify-slice6 Check 4; commit `6510710`)
- [x] Slice 7: Capture schema addition — COMPLETE (Frank map-not-route QC gate PASS; post-PASS test-strengthening fix applied to verify-slice7-capture-schema.sh Check on required-language detection)
- [x] Slice 8: Retrofit procedure doc — COMPLETE (Frank map-not-route QC gate PASS; self-fixed line-wrap spot-check bug in verify-slice8-retrofit-procedure.sh Check 7)
- [x] Slice 9: Deploy Mechanism (copy to `~/.claude/`) — COMPLETE (Frank map-not-route QC gate PASS; all four deploy targets independently diffed byte-identical by both Wright and Frank separately)
- [x] Slice 10: Retrofit pilot (`market_data`) — COMPLETE 2026-08-12 (alpha; Frank gate PASS round 2, round 1 FAIL). Commit `32bf3fe` in market_data; RetrofitAuditRecord LORE `e1226c84-168a-4121-a790-f09823e695c8`; trace `docs/reports/retrofit-2026-08-12/`. Canonical Components 1-3 byte-identical to `reference/`; project DB/cron logic correctly layered as a separate script per API Contracts, not merged into the canonical probe. Surfaced two procedure defects (exec bit, trace location) — both fixed in PR #5 `7a99d8f`. Caveat: market_data gitignores `CLAUDE.md`, so this pilot does NOT demonstrate Components 4/7.
- [~] Slice 11: Retrofit rollout, practice-only items (remaining roster) — **DROPPED 2026-08-12 (Danny).** Not deferred, not partial: prose-in-CLAUDE.md is a description of the mechanism, not the mechanism. C4 delivered as text is a document that must be remembered; C4 delivered as the SessionStart hook fires whether anyone remembers or not. "Zero engineering cost" was the tell — it meant zero mechanism. Slice 12's hook carries the session-start prime instead. `market_data` (alpha) and `gap-lens-dilution-filter` (beta, declined-pending-mechanism) both reached this independently. Known limit: the hook can put the signpost→pillar sequence in front of an agent before its first reply; it cannot make anyone label their turns. That remains a habit no hook enforces.
- [ ] Slice 12: Retrofit rollout, probe-hook items (remaining roster) — IN PROGRESS (unblocked 2026-08-12 by PR #5 `7a99d8f`: retrofit-procedure exec-bit step 2a + in-repo trace location; released to alpha via Switchboard). Scope correction: 7 greenfield installs, not 7 cutovers — only `market_data` is retrofitted (roster audit `docs/reports/roster-gitignore-audit-2026-08-12.md`).

**Forge-closability**: Slices 1-9 = sprint closable (fully within agent-rig's control). Slices 10-12
(retrofit pilot + remaining-roster rollout) track as ongoing, non-blocking work — this sprint's own
forge-gate does not wait on `market_data`'s (Slice 10) own Frank gate to reach PASS (per Danny,
2026-08-09: the retrofit is generic enough not to force a ceremonious cross-repo dependency).

## Current
Slice: 12
Step: Slice 12 released to alpha 2026-08-12 after PR #5 merged; awaiting per-repo execution across 7 greenfield installs. Slice 11 DROPPED 2026-08-12 (Danny) — superseded by Slice 12's hook. Slice 12 is the remaining work.
Last updated: 2026-08-12

Note: Slice 10 (retrofit pilot) targets `market_data`, a different repo — this forge session's per-slice implementation work in agent-rig itself may be substantially complete after this commit.

Commits so far: `1727a6c` (spec doc set), `dc7aeb5` (Slices 1-2 artifacts), `2bf3068` (Slice 3), `15600b8` (Slice 4), `d284917` (Slice 5), `6510710` (Slice 6), `e353f2b` (Slice 7), `e813604` (Slice 8) — all on `feature/signpost-pillar-propagation`, verified independently.

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
