# Sprint North Star: signpost-pillar-propagation
**Status**: Locked
**Date**: 2026-08-08

## Declared Intent
Give every homelab project — not just agent-rig — a working, verified session-start mechanism that distinguishes what a session merely *inherited* from memory (the signpost) from what it has *independently verified this session* (the pillar), and retire the project-local, drifting variants of this idea that already exist in place of it.

## In Scope / Out of Scope
See `01-REQUIREMENTS.md` Out of Scope once authored.

## Success Criteria (Layer 1 — fidelity)
- `new-project`/`HOMELAB-CLAUDE.md.template` scaffold a generalized ground-truth probe hook, self-disclaiming (does not claim to satisfy LORE priming), fail-loud on error, wired to fire before memory/doc consultation.
- The Signpost/Pillar labeled-summary convention (proven twice in department-os) is a documented, checkable requirement in the propagated Session Start Behaviour template.
- Map-not-route briefing convention, `assert_*.py` fail-closed pattern, and `Verification:`/`Re-verify with:` capture-schema lines are documented per the Intake's acceptance criteria.
- Existing project-local probe variants (Cairn's, beta's) are targeted for full replacement, each via its own per-project blast-radius audit, resident-agent ownership, and independent unbriefed Frank gate at cutover — not a uniform sweep, not indefinite coexistence.
- No mechanism ships in a DDR-0009-like "documented but not installed" state — each item is either fully working and live-verified (by tool-call trace, not response-text plausibility) or explicitly marked pilot-only with a named owner.

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: **Thesis** — "Orchestration mechanics... are worth developing and hardening in one dedicated place rather than each consuming project inventing and drifting its own copy independently," citing the Frank-transfer (DDR-013) and forge-start.md bug-fix-redeployed-everywhere precedents as the pattern this sprint repeats for session-start verification. Also serves **Drift check** item 3 in reverse — the failure being corrected is exactly "a cross-cutting persona or package changes but its propagation/redeploy to already-vendored consumers is left undefined or silently skipped" (DDR-004 itself, undeployed for weeks).
Project North Star status at gate time: non-DRAFT (`docs/NORTHSTAR.md`, Established 2026-07-17) → normal binding Layer 2 PASS/FAIL, no PROVISIONAL tag.
