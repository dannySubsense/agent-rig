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

| Repo | SessionStart probe (`session_probe.py`) | Stop-hook C3 contract (`first_turn_contract_probe.py`) | Committed? | Other hooks | Last verified |
|---|---|---|---|---|---|
| `agent-rig` | Live (`scripts/session_queue_probe.py`) | Live — includes claim-matching (PR #20) + boundary-matching (PR #21) fixes | Yes, on `main` | `no-preamble-no-meta-narration.sh` (DDR-007), `domain-boundary-provenance` (DDR-006) — **SUNSET, TO BE REWORKED (Danny's decision, 2026-09-06) — do not build on or wire this further.** Was built, `log_only` mode, NOT live on `main` (`PreToolUse` entry only ever committed on `feature/domain-boundary-provenance-hook-extension` at `b57d9f1`; `main:.claude/settings.json` never had a `domain-boundary-provenance` entry). The `domain-boundary-provenance-hook-extension` sprint is sunset along with it. Branch `feature/domain-boundary-provenance-hook-extension` is GitHub-locked (`lock_branch: true` branch protection, read-only, applied 2026-09-06) — no further pushes possible; local copy retained as reference only. See DDR-INDEX row 006 and LORE decision `e87c3f20`. `progress-proof-per-slice` (DDR-008) | 2026-09-06, direct file read + `git show main:.claude/settings.json` + `git log --oneline -1 -- .claude/settings.json` |
| `market_data` | Live (`scripts/session_probe.py`, installed 2026-08-12, Slice 10 pilot) | Live, committed to `main` (`ddfc5d0`), smoke-tested (exit 0) | **Yes, on `main`, not pushed** | None known | 2026-09-06, direct commit + smoke test this session |
| `department-os` | Unmerged (branch `session-start-hook`) — NOT live on `main` | Live on disk, current version, smoke-tested (exit 0) | **No** — committed on feature branch `adopt-first-turn-contract-probe` (`b4fb114`, PR #9 opened) but `b4fb114` is NOT an ancestor of `origin/main`; repo currently checked out on `recovery/checkpoint-2-from-bfe41c4` with active archive/quarantine branches — **excluded from the 2026-09-06 commit batch, left to department-os's own resident agent given its unclear recovery state** | — | 2026-09-05, `git merge-base --is-ancestor b4fb114 origin/main` → false (this session) |
| `electric-blue` | Not installed | Live, committed to `main` (`1b8c945` + `78bcdbe` — `.claude/` is repo-wide gitignored, wiring force-added in a follow-up commit), smoke-tested (exit 0) | **Yes, on `main`, not pushed** | — | 2026-09-06, direct commit + smoke test this session |
| `gap-lens-dilution` | Not installed | Live, committed to `master` (`b092dc2` + `7f0f986` — same `.claude/`-gitignore-then-force-add pattern as electric-blue), smoke-tested (exit 0) | **Yes, on `master`, not pushed** | — | 2026-09-06, direct commit + smoke test this session |
| `gap-lens-dilution-filter` | Not installed | Live, committed on `feat/supply-event-extraction-ddr0007-0008` (`189a4c1`) — **not `main`**, the branch that happened to be checked out | **Yes, on that feature branch only, not pushed** | `PreToolUse` (pre-existing, unrelated) | 2026-09-06, direct commit + smoke test this session |
| `ask-edgar-repo` | Not installed | Live, committed to `master` (`40171e7`), smoke-tested (exit 0) | **Yes, on `master`, not pushed** | — | 2026-09-06, direct commit + smoke test this session |
| `sonic-store` | Not installed | Live, committed to `main` (`8f4ee83`), smoke-tested (exit 0) | **Yes, on `main`, not pushed** | — | 2026-09-06, direct commit + smoke test this session |
| `quant-foundry` | Not installed | Live, committed to `main` (`1831991`), smoke-tested (exit 0) | **Yes, on `main`, not pushed** | — | 2026-09-06, direct commit + smoke test this session |
| `runtime/agent-lore` | Not installed | Live, current version, smoke-tested | **Yes, merged to `main`** (`9fa9b1a`, PR #1) | — | 2026-09-05, `git log`/`git branch --show-current` (this session) |

**Note on this batch (2026-08-28):** these 7 installs, plus `market_data`, were done directly by
agent-rig (wright) reaching into each repo's filesystem — not via each resident agent running
`RETROFIT-PROCEDURE.md`'s own six-step cutover (no blast-radius audit, no independent Frank gate
per repo, no `RetrofitAuditRecord` capture). Danny explicitly authorized this direct-deploy
approach after confirming market_data's install went cleanly. None of these repos got the SessionStart
probe (Components 4/7) — only the Stop-hook C3 contract.

**Verification method key**:
- "Direct file read" = actually opened the file/`settings.json` this session.
- "Smoke test" = ran the hook via its real invocation path and confirmed output/track-record.
- "Per PROGRESS.md"/"per LORE" = inherited from a document, not independently checked — treat as a
  signpost, re-verify before depending on it (same discipline as session-start checks generally).
