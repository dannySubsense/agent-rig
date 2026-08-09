# Progress: signpost-pillar-propagation

## Status: IN_PROGRESS

## Branch
`feature/signpost-pillar-propagation` (created from `main` @ `74c20ed`, 2026-08-09)

## Slices
- [x] Slice 1: Independent review of alpha's handoff report (US-9 gate) — COMPLETE (already satisfied; `ALPHA-REPORT-REVIEW.md` produced by an independent Frank dispatch, verdict SAFE TO CITE, 2 mandatory caveats)
- [x] Slice 2: Generalized probe script + hook wrapper (reference artifacts) — COMPLETE (`reference/session_probe.py`, `reference/session-start-probe.sh`, written directly in agent-rig 2026-08-08, verified standalone with zero department-os dependency, `timeout=15` dropped, no project-specific strings)
- [x] Slice 3: `new-project.md` scaffolds Components 1-3 — COMPLETE (2026-08-09; QC round 1 FAIL caught missing live-trace evidence + undocumented/incorrect rollback wording; both fixed; QC round 2 ran its own independent scratch trace, PASS; commit `2bf3068`)
- [x] Slice 4: Session Start Behaviour template (Signpost:/Pillar: + 3-check block) — COMPLETE
- [x] Slice 5: Map-not-route briefing convention template — COMPLETE (Frank map-not-route QC gate PASS; commit `d284917`)
- [x] Slice 6: Assert-convention + sentinel pattern combined doc — COMPLETE (Frank map-not-route QC gate PASS; test-script fix applied for §2.5 negation-detection bug in verify-slice6 Check 4; commit `6510710`)
- [ ] Slice 7: Capture schema addition — PENDING
- [ ] Slice 8: Retrofit procedure doc — PENDING
- [ ] Slice 9: Deploy Mechanism (copy to `~/.claude/`) — PENDING
- [ ] Slice 10: Retrofit pilot (`market_data`) — PENDING, non-blocking for sprint close
- [ ] Slice 11: Retrofit rollout, practice-only items (remaining roster) — PENDING, non-blocking for sprint close
- [ ] Slice 12: Retrofit rollout, probe-hook items (remaining roster) — PENDING, non-blocking for sprint close

**Forge-closability**: Slices 1-9 + Slice 10 (pilot) PASS = sprint closable. Slices 11/12 track as ongoing, non-blocking.

## Current
Slice: 7
Step: not yet dispatched
Last updated: 2026-08-09

Commits so far: `1727a6c` (spec doc set), `dc7aeb5` (Slices 1-2 artifacts), `2bf3068` (Slice 3), `15600b8` (Slice 4), `d284917` (Slice 5), `6510710` (Slice 6) — all on `feature/signpost-pillar-propagation`, verified independently.

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| verify-slice3-new-project-scaffold.sh Check 2 | 1 | Test-script bug (not implementation): awk's "capture first \`\`\`bash block" guard grabbed the wrong block — an unrelated \`\`\`bash fence exists at commands/new-project.md:429, before the real hook block at :578. Manually re-verified implementation is byte-identical via precise line-range extraction. |
| verify-slice3-new-project-scaffold.sh Check 6 | 1 | Test-script bug (not implementation): backtick-span count includes the Decision Table row's explanatory parenthetical \`<InputBundle.projectId>\`, inflating count to 9 vs. the real 8 files. Both git add and Decision Table row independently confirmed to list the same 8 items. |
| verify-slice6-assert-convention-template.sh Check 4 | 1 | Test-script bug (not implementation): naive grep for "section 2.5" matches the template's own disclaimer sentence ("does not cite the source doctrine's Section 2.5"), which mentions the section only to explicitly deny citing it. Roadmap's Done-When is satisfied by non-citation; implementation correct. |

## Notes
- docs/INVARIANTS.md and docs/CADENCE.md authored this session (forge-start governance step), confirmed by Danny, committed to `main` (74c20ed) before this feature branch was cut.
- Real incident this session: working directory drifted to a stray branch (`forge-start-lite-mode`) left checked out by an earlier subagent — caught, resolved, returned to `main` before branching. See LORE capture `aab41baf`.
