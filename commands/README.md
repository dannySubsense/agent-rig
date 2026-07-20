# commands/

Cross-cutting slash-command skills authored and stewarded by agent-rig — ecosystem-wide
tooling distributed to every project, distinct from the package-internal skills that ship
inside the vendored `forge-07152026/`, `spec-orchestration-07152026/`, and
`notebook-orchestration-04182026/` packages.

Author≠install-location, same pattern as `agents/` and Frank (DDR-013): the file here is
the source of record; it deploys to `~/.claude/commands/<name>.md` for global invocation
via `/<name>` from any project. Edit here, then redeploy — don't edit the installed copy
directly.

## Residents

| Command | Role | Transferred from |
|---|---|---|
| [`new-project`](new-project.md) | Bootstrap a new homelab project — agent identity, CLAUDE.md, git/GitHub, LORE capture, Northstar draft | agent-dashboard, DDR-014 (2026-07-17) |

## Related templates

Companion assets that moved with `/new-project` under DDR-014 but live in their conventional
homes rather than here:

- **`docs/templates/NORTHSTAR-RETROFIT.md`** — procedure for retrofitting a Northstar onto an
  existing project. Distributed under agent-rig stewardship.
- **`HOMELAB-CLAUDE.md.template`** — the CLAUDE.md master `/new-project` distributes at bootstrap
  (stewardship moved to agent-rig 2026-07-17, recorded in DDR-014 §3.1).

## Upstream references (not forked into this repo)

The Northstar document's canonical **four-section shape** (Purpose / Thesis / Non-goals /
Drift check) is owned by **agent-dashboard `DDR-012 §3.1`**, which both `NORTHSTAR-RETROFIT.md`
and `/new-project` treat as the sole source of truth. That decision record stays in
agent-dashboard (decision records don't migrate — same precedent as DDR-013). It is referenced
in place, deliberately **not** copied here: a second copy of a schema is a drift hazard, and one
source of truth is the whole point of DDR-012's design. The `NorthstarDocument` TypeScript
interface in agent-dashboard's `project-bootstrap-v2/02-ARCHITECTURE.md` §2 is spec-implementation
detail, not the canonical shape, and likewise stays put.
