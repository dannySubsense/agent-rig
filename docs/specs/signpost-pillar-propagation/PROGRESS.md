# Progress: signpost-pillar-propagation

## Status: IN_PROGRESS

## Branch
`feature/signpost-pillar-propagation` (created from `main` @ `74c20ed`, 2026-08-09)

## Slices
- [x] Slice 1: Independent review of alpha's handoff report (US-9 gate) — COMPLETE (already satisfied; `ALPHA-REPORT-REVIEW.md` produced by an independent Frank dispatch, verdict SAFE TO CITE, 2 mandatory caveats)
- [x] Slice 2: Generalized probe script + hook wrapper (reference artifacts) — COMPLETE (`reference/session_probe.py`, `reference/session-start-probe.sh`, written directly in agent-rig 2026-08-08, verified standalone with zero department-os dependency, `timeout=15` dropped, no project-specific strings)
- [ ] Slice 3: `new-project.md` scaffolds Components 1-3 — PENDING
- [ ] Slice 4: Session Start Behaviour template (Signpost:/Pillar: + 3-check block) — PENDING
- [ ] Slice 5: Map-not-route briefing convention template — PENDING
- [ ] Slice 6: Assert-convention + sentinel pattern combined doc — PENDING
- [ ] Slice 7: Capture schema addition — PENDING
- [ ] Slice 8: Retrofit procedure doc — PENDING
- [ ] Slice 9: Deploy Mechanism (copy to `~/.claude/`) — PENDING
- [ ] Slice 10: Retrofit pilot (`market_data`) — PENDING, non-blocking for sprint close
- [ ] Slice 11: Retrofit rollout, practice-only items (remaining roster) — PENDING, non-blocking for sprint close
- [ ] Slice 12: Retrofit rollout, probe-hook items (remaining roster) — PENDING, non-blocking for sprint close

**Forge-closability**: Slices 1-9 + Slice 10 (pilot) PASS = sprint closable. Slices 11/12 track as ongoing, non-blocking.

## Current
Slice: 3
Step: not yet dispatched
Last updated: 2026-08-09

## Fix Attempts
| Test/File | Attempts | Last Error |
|-----------|----------|------------|

## Notes
- docs/INVARIANTS.md and docs/CADENCE.md authored this session (forge-start governance step), confirmed by Danny, committed to `main` (74c20ed) before this feature branch was cut.
- Real incident this session: working directory drifted to a stray branch (`forge-start-lite-mode`) left checked out by an earlier subagent — caught, resolved, returned to `main` before branching. See LORE capture `aab41baf`.
