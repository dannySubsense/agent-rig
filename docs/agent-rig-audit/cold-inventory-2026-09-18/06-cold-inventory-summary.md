# Cold inventory summary

## What Agent Rig demonstrably is

At committed HEAD `cc9dcb3310f3415b9b6658d3cb8f90014a9bbe55`, Agent Rig is a 408-file Git workshop containing four dated Claude prompt bundles, cross-cutting commands/personas/templates, five project hook wrappers, nine primary Python scripts, a Git/GitHub scrub gate, tests, specifications, archives, and review snapshots. It is not a standalone application or service. Most orchestration behavior is encoded as Markdown commands, agent roles, and skills interpreted by an external Claude Code runtime; mechanical controls live in shell/Python hooks and Git automation.

Local `main` and live remote `main` are aligned at the same full SHA. The tracked working tree is clean. The sole untracked file is the audit charter itself. No fetch or repository mutation occurred.

## What appears operational

- Dated bundle installation is concretely implemented, and most compared `~/.claude` runtime files are byte-identical to HEAD.
- Repo-local Claude settings actively route SessionStart, PreToolUse, UserPromptSubmit, and Stop events to local wrappers/probes.
- Signpost, no-preamble, progress-proof, and domain-boundary ignored logs contain 2,284 total local events; the general aggregator covers 2,115 events across three of those hooks.
- The signpost and no-preamble current logs reached the audit date, and a Claude process had this repository as cwd.
- The local scrub pre-commit hook is enabled, the same scanner is wired in GitHub Actions, and an all-tracked scan passed.
- 208 Python cases passed with one LORE-derived fixture case deliberately excluded. The domain wrapper passed 15/15 isolated tests.

These observations establish concrete local use, not full end-to-end correctness of the prompt orchestrators.

## Partial, local-only, disconnected, or unverified

- Spec, Forge, Notebook, Lit Synthesis, `/new-project`, `/lore-close`, relay, and Frank gates are present but were not safely executable under a read-only audit. Their binding sequences remain **Present — unverified** as runtime workflows.
- Notebook execution is locally blocked because Jupyter is absent.
- Installed Frank, lore-close, and two Spec templates differ from HEAD, so the active runtime is not fully reproducible from the commit.
- Progress-proof is partial: it does not intercept `Write`, allows completion without proof, accepts nonallowlisted proof as manual/unverified, and its isolated wrapper error-telemetry suite failed 6/15 cases.
- No-preamble detection is currently `log_only`; it is advisory, not blocking enforcement.
- Domain-boundary provenance is disconnected locally: no settings route, no manifest, no global copy, and no log activity after 2026-09-06.
- Telemetry database persistence is a no-op. JSONL logs are ignored, local-only, and the aggregator omits the domain log.
- Session queue depends on a local secret-bearing `.env`, external Postgres/LORE, psycopg2, and transcript layout; these were not exercised before freeze.
- Three worktree registrations are prunable, three local remote-tracking refs are absent from the live remote, and two local feature branches are one commit ahead of their live upstream tips.

## Most consequential gaps and contradictions

1. The progress-proof hook can execute edit-authored shell commands after weak prefix matching, yet it does not actually require proof for completion.
2. The scrub gate prints detected values and ignores Git subprocess failure status, creating both disclosure and fail-open risks in a security control.
3. Claimed source-of-record assets differ from installed runtime copies, including the shared Frank persona; Notebook and cross-cutting Frank also collide at one destination.
4. “Binding” orchestration gates are instruction-layer contracts rather than a repository-enforced state machine. The mechanical hooks cover narrower surfaces and mostly fail open.
5. Signpost verification confirms the existence of a cited tool call, not that the call supports the associated claim.
6. Documentation disagrees with the current Forge command on whether missing governance files halt or are authored.
7. CI runs the scrub gate but does not run the repository's Python/wrapper test suites.

## Confidence and limitations

Confidence is **high** for Git identity, tree contents, local/remote main alignment, settings routes, source logic, installed byte comparisons, runtime-log counts, and test outcomes. Confidence is **moderate** for maturity classifications because actual Claude orchestration runs, external integrations, and author intent were excluded. Assertions about consequence from `shell=True`, prefix checks, and fail-open branches are explicitly implementation inferences grounded in cited code.

The build-idea index, LORE, author/orchestrator narrative, prior architectural summaries, and external comparison systems were not consulted. Secret-bearing configuration values were not inspected or exposed. The report does not recommend a target architecture or implement fixes.

**This Phase 1 cold inventory was frozen before any author/index/LORE reconciliation.** Its next permitted analytical step is a separate Phase 2 reconciliation that preserves these findings unchanged.

