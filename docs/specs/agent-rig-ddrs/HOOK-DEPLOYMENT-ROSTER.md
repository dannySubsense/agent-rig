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
| `agent-rig` | Live (`scripts/session_queue_probe.py`) | Live — includes claim-matching (PR #20) + boundary-matching (PR #21) fixes | Yes, on `main` | `no-preamble-no-meta-narration.sh` (DDR-007), `domain-boundary-provenance` (DDR-006) — **built, wired, `log_only`** (`PreToolUse` entry live in `.claude/settings.json`, `docs/tooling/domain-boundary-mode.json` set to `log_only`, per the `domain-boundary-provenance-hook` extension sprint), `progress-proof-per-slice` (DDR-008) | 2026-09-05, direct file read (`.claude/settings.json` + `.claude/hooks/`) |
| `market_data` | Live (`scripts/session_probe.py`, installed 2026-08-12, Slice 10 pilot) | Live on disk, current version, smoke-tested at install | **No** — `.claude/settings.json` modified-uncommitted, `.claude/hooks/first-turn-contract.sh` + `scripts/first_turn_contract_probe.py` untracked | None known | 2026-09-05, `git status --porcelain -uall` (this session) |
| `department-os` | Unmerged (branch `session-start-hook`) — NOT live on `main` | Live on disk, current version, smoke-tested (exit 0) | **No** — committed on feature branch `adopt-first-turn-contract-probe` (`b4fb114`, PR #9 opened) but `b4fb114` is NOT an ancestor of `origin/main` | — | 2026-09-05, `git merge-base --is-ancestor b4fb114 origin/main` → false (this session) |
| `electric-blue` | Not installed | Live on disk, current version, smoke-tested at install | **No** — `scripts/first_turn_contract_probe.py` + track-record file untracked | — | 2026-09-05, `git status --porcelain -uall` (this session) |
| `gap-lens-dilution` | Not installed | Live on disk, current version, smoke-tested at install | **No** — `scripts/first_turn_contract_probe.py` untracked | — | 2026-09-05, `git status --porcelain -uall` (this session) |
| `gap-lens-dilution-filter` | Not installed | Live on disk, current version, smoke-tested at install | **No** — `.claude/settings.json` modified-uncommitted, hook script + track-record untracked | `PreToolUse` (pre-existing, unrelated) | 2026-09-05, `git status --porcelain -uall` (this session) |
| `ask-edgar-repo` | Not installed | Live on disk, current version, smoke-tested at install | **No** — all hook files untracked | — | 2026-09-05, `git status --porcelain -uall` (this session) |
| `sonic-store` | Not installed | Live on disk, current version, smoke-tested at install | **No** — all hook files untracked | — | 2026-09-05, `git status --porcelain -uall` (this session) |
| `quant-foundry` | Not installed | Live on disk, current version, smoke-tested at install | **No** — all hook files untracked | — | 2026-09-05, `git status --porcelain -uall` (this session) |
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
