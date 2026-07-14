# agents/

Cross-cutting agent personas authored and stewarded by agent-rig — distinct from the
package-internal `agents/` directories inside the vendored `forge-03252026/`,
`lit-synthesis-04292026/`, and `spec-orchestration-03242026/` packages, which hold
agents scoped to that one package.

Author≠install-location, same pattern as `/new-project` (DDR-001): the file here is
the source of record; it deploys to `~/.claude/agents/<name>.md` for global dispatch
via `Agent({subagent_type: "<name>"})` from any project. Edit here, then redeploy —
don't edit the installed copy directly.

## Residents

| Agent | Model | Role | Transferred from |
|---|---|---|---|
| [`frank`](frank.md) | fable | Judgment-gate QC persona — spec/implementation/notebook review, PASS/FAIL/HALT verdicts | agent-dashboard, DDR-013 (2026-07-14) |
