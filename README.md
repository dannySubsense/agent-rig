# Agent Rig

**A workshop for multi-agent orchestration.** Frameworks get assembled, tuned, and refined here before they're relied on elsewhere — the cadence, the judgment gates, and the agent personas that other repos install and vendor.

Agent Rig is a workshop, not a product. The work here exists so that *other* projects get sharper, more reliable orchestration tooling — not to ship a standalone application of its own. It is also the openly-shared reference implementation of one private homelab; see [Homelab surface](#homelab-surface) for what that means and doesn't.

---

## What's here

### Orchestration frameworks (dated packages)

Each is a self-contained bundle of Claude Code **skills, agents, commands, and templates**, with its own `README.md` and an `install.sh` that deploys it into `~/.claude/`. They're dated snapshots — the date in the directory name is the version.

| Package | What it orchestrates |
|---|---|
| [`spec-orchestration-07152026/`](spec-orchestration-07152026/) | Turning a vague feature request into approved spec docs — Intake → Interview → requirements → architecture → roadmap → review, gated by Frank. |
| [`forge-07152026/`](forge-07152026/) | Implementing an approved spec slice by slice through a build–test–verify loop, gated by Frank. |
| [`notebook-orchestration-04182026/`](notebook-orchestration-04182026/) | Building a research/validation Jupyter notebook through a design → build → execute → QC cycle. |
| [`lit-synthesis-04292026/`](lit-synthesis-04292026/) | A per-paper synthesis pipeline over a PDF corpus — governance docs, then a resumable synthesis-and-scoring loop. |

### Cross-cutting agent personas — [`agents/`](agents/)

Personas dispatched across many projects, not scoped to one. Source-of-record lives here; they deploy to `~/.claude/agents/<name>.md` for global dispatch (author ≠ install location). First resident: **Frank**, a risk-averse QC judgment gate that returns PASS / FAIL / HALT verdicts rather than suggestions.

### Bootstrap tooling — [`commands/`](commands/)

`/new-project` — bootstraps a new homelab project end to end (identity, `CLAUDE.md`, git/GitHub, first commit). Source-of-record here; deploys to `~/.claude/commands/`.

---

## How the work is run

Every substantial change follows the same loop the packages themselves implement:

**(optional DDR) → Intake → Interview → `/spec-start` → `/forge-start` → Frank gate → commit.**

Decisions that shape the repo are recorded as **DDRs** in [`docs/specs/agent-rig-ddrs/`](docs/specs/agent-rig-ddrs/) — start with the [index](docs/specs/agent-rig-ddrs/00-DDR-INDEX.md). The project's charter is [`docs/NORTHSTAR.md`](docs/NORTHSTAR.md).

Frank's gate is **binding** (PASS/FAIL/HALT, no manual override) and independent numeric constants must cite a source — the same integrity discipline the frameworks enforce for their consumers.

---

## Using a framework

Each package is independent. From a package directory:

```bash
./install.sh      # deploys that package's skills/agents/commands/templates into ~/.claude/
```

Then invoke its command (e.g. `/spec-start`, `/forge-start`, `/notebook-start`) from any project. See each package's own `README.md` / `QUICKSTART.md` for specifics — they are the authoritative usage docs.

---

## Homelab surface

This repo is public, and it is also the reference implementation of one private homelab. Those two facts are kept deliberately apart:

- **The frameworks are the shareable part** — domain-agnostic by construction.
- **Homelab-specific values are never hardcoded in tracked files.** Templates carry placeholders (e.g. `<LORE_DB_HOST>`, `<AGENT-NAME>`), resolved at bootstrap from a local, non-public source. A project's own `CLAUDE.md` is gitignored.
- **Internal decision records** (DDRs) are kept as an honest trail; they narrate one homelab's choices and are reference, not instructions for yours.

If you adopt a framework, treat the homelab-specific paths, hosts, and agent names as *examples* — substitute your own.

---

## Status & license

An evolving workshop, not a released product. Packages are dated snapshots; expect them to change and to be superseded by later-dated ones.

> **License:** _none declared yet._ Until a `LICENSE` file is added, all rights are reserved by default — treat the code as source-available reference, not licensed for reuse. (A license is planned; see the DDR backlog.)
