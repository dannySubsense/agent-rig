# Hook Deployment Roster

**Purpose**: a live-state record of which repo has which hook, verified how and when — not a
narrative log. This exists because the alternative (inferring deployment state from a sprint's
`PROGRESS.md` or a LORE capture) produced a real error 2026-08-27/28: agent-rig believed
`market_data`'s Stop-hook C3 contract predated two bug fixes and needed updating, when it had
never been installed there at all — the only record was a 2026-08-12 note about a *different*
component (the SessionStart probe), read as if it covered both.

**Rule**: a cell in this table is only as good as its verification method. "Confirmed by reading
`settings.json` + testing the wrapper" is a fact. "Per PROGRESS.md" is a claim that needs
re-checking before you rely on it — mark it as such, don't upgrade it silently.

**Maintenance**: update this table at the moment a hook is installed/removed/updated in any repo —
same discipline as `PROGRESS.md`, not a periodic audit. If a cell hasn't been re-verified in a
while and something depends on it, re-check live rather than trusting the date.

---

| Repo | SessionStart probe (`session_probe.py`) | Stop-hook C3 contract (`first_turn_contract_probe.py`) | Other hooks | Last verified |
|---|---|---|---|---|
| `agent-rig` | Live (`scripts/session_queue_probe.py`) | Live — includes claim-matching (PR #20) + boundary-matching (PR #21) fixes | `no-preamble-no-meta-narration.sh` (DDR-007), `domain-boundary-provenance` (DDR-006), `progress-proof-per-slice` (DDR-008) | 2026-08-28, direct file read + track-record inspection (this session) |
| `market_data` | Live (`scripts/session_probe.py`, installed 2026-08-12, Slice 10 pilot) | Live — installed 2026-08-28 (this session), current version (post PR #20/#21), smoke-tested via real invocation path, one track-record entry confirmed | None known | 2026-08-28, direct file read on disk + live smoke test (this session) |
| `department-os` | Unmerged (branch `session-start-hook`) — NOT live on `main` | Not installed | — | 2026-08-21, confirmed absent via `find` (per DDR-004 index history, itself unverified this session — re-check before relying on it) |
| `electric-blue` | Not installed | Live — installed 2026-08-28, current version (post PR #20/#21), smoke-tested, settings.json created fresh (had none) | — | 2026-08-28, direct file write + smoke test (this session) |
| `gap-lens-dilution` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, merged into existing (empty) hooks dict | — | 2026-08-28, direct file write + smoke test (this session) |
| `gap-lens-dilution-filter` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, merged alongside existing `PreToolUse` hook (untouched) | `PreToolUse` (pre-existing, unrelated) | 2026-08-28, direct file write + smoke test (this session) |
| `ask-edgar-repo` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, settings.json created fresh | — | 2026-08-28, direct file write + smoke test (this session) |
| `sonic-store` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, settings.json created fresh | — | 2026-08-28, direct file write + smoke test (this session) |
| `quant-foundry` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, settings.json created fresh | — | 2026-08-28, direct file write + smoke test (this session) |
| `runtime/agent-lore` | Not installed | Live — installed 2026-08-28, current version, smoke-tested, settings.json created fresh | — | 2026-08-28, direct file write + smoke test (this session) |

**Note on this batch (2026-08-28):** these 7 installs, plus `market_data`, were done directly by
agent-rig (wright) reaching into each repo's filesystem — not via each resident agent running
`RETROFIT-PROCEDURE.md`'s own six-step cutover (no blast-radius audit, no independent Frank gate
per repo, no `RetrofitAuditRecord` capture). Danny explicitly authorized this direct-deploy
approach after confirming market_data's install went cleanly. None of these repos got the SessionStart
probe (Components 4/7) — only the Stop-hook C3 contract. Each resident agent should be notified
this landed in their repo, since they didn't do the deploying themselves.

**Verification method key**:
- "Direct file read" = actually opened the file/`settings.json` this session.
- "Smoke test" = ran the hook via its real invocation path and confirmed output/track-record.
- "Per PROGRESS.md"/"per LORE" = inherited from a document, not independently checked — treat as a
  signpost, re-verify before depending on it (same discipline as session-start checks generally).
