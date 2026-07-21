# SESSION-MAP.md — Anatomy of a Claude Session (Homelab)

- **Status:** DRAFT v0.1 — pending Danny's review. Canonical once ratified.
- **Owner:** agent-rig (Wright) — stewards orchestration patterns + cross-cutting personas.
- **Author:** wright · **Date:** 2026-07-20
- **Purpose:** the single picture a Claude session and every DDR reconciles against — what governs a session, where each piece lives, whether it is a source-of-record or an instance, and where control is still leaking. Pattern-level: agent-rig (SoR) + global `~/.claude`, with known per-repo instances noted, not a full ecosystem file audit (that is a separate inventory pass).
- **How to use:** when a session-governing artifact changes, update the relevant cell here first, then the artifact. When a control gap closes (a DDR ships), move it from Part D to the body. This doc is a pillar — its cells are re-derived from primary artifacts, never relayed from a prior version's assertion.

---

## Part A — The Session Lifecycle (time axis)

### A1. Cold start (prime) — the signpost; then build the pillar
Run before responding to the first user message. The prime **is the signpost** — it orients (what changed, where to look). Before asserting anything it implies, **build the pillar: verify against the primary source** — read the document for a decision/spec claim, run the read-only probe for a live-state claim (see Part C).

| Step | Action | Consumer / SoR |
|---|---|---|
| LORE prime | `search_knowledge(projectId, minSimilarity 0.1)` | interim priming; to be replaced by agent-lore DDR-004 `PromptAssembler` |
| Switchboard | `read_messages({agent_id})` — once, at cold start only | coordination msgs have no live-push; manual poll is the only delivery |
| Git | `git fetch` + `rev-parse` both refs + status — **report only, never auto-merge/pull/push** | visibility check |
| [PROPOSED] SessionStart hook | runs the probes, injects raw ground truth into context | **agent-rig DDR-004** (Frank-PASS, unapproved) |

### A2. During the session (living practice)
| Practice | Trigger | SoR |
|---|---|---|
| Signpost→pillar (verify before assert) | every status claim/decision, all session long | Part C; source: `market_data` POSTMORTEM-2026-06-29 + `session_probe.py`; global CLAUDE.md Research-Data-Integrity |
| Ask-vs-Act / recommendation-not-menu | before any AskUserQuestion / decision | **agent-rig DDR-001** (ACCEPTED) |
| No-hedge gate | before ending a turn with a question | backlog → DDR (candidate) |
| Always-redispatch | orchestrator handing work to a sub-agent | **agent-rig DDR-002 §3.5** (shipped to HOMELAB template) |
| Capture-to-LORE | on any decision / deviation / HALT / discovery | project CLAUDE.md Capture Behaviour |
| Frank gate | at each major phase boundary (spec complete, forge complete) | binding, no override |
| [PROPOSED] PreToolUse gated-skill hook | dispatch of a gated skill | **agent-rig DDR-002 §3.1–3.4** (own sprint, unbuilt) |

### A3. Close
| Step | Action | SoR |
|---|---|---|
| `/lore-close` | reconcile status across layers, verify vs ground truth, capture terminal memory | global `~/.claude/commands/lore-close.md` |
| Push gate (Step 7) | reads repo git policy; surfaces unpushed, asks — never auto-pushes on `manual-push-only` | git-workflow layer (below) |

---

## Part B — Governing Layers (what axis)

| Layer | Source-of-record | Instances / where it also lives | Status |
|---|---|---|---|
| **Identity & memory** | project CLAUDE.md + global `~/.claude/CLAUDE.md` | LORE (per `projectId`), local file-memory (`~/.claude/projects/.../memory/`), Switchboard handle | live; 4 stores, no unified view |
| **Decision governance (DDRs)** | *each repo's own* `docs/specs/<repo>-ddrs/` | agent-rig `001–004`; agent-dashboard `001–014` (holds the transfer DDRs 013/014 agent-rig cites); gaplens `0002–0010` | live; **see Gap D1** |
| **Git workflow** | HOMELAB template `## Git Workflow` shape (agent-rig) | per-repo CLAUDE.md section; agent-dashboard `docs/GIT-WORKFLOW.md` (project-local protocol); forge Git-Flow-Determination; lore-close Step 7 | live; **see Gap D2** |
| **Orchestration loop** | agent-rig packages (`spec-orchestration-07152026/`, `forge-07152026/`) | installed at `~/.claude/{commands,agents,skills,templates}` (12 commands, frank+interview-conductor agents) | live; SoR≠install-location by design |
| **Enforcement (hooks/gates)** | agent-rig (host: VM101, single-host deployable) | **live:** `Stop` hook (switchboard relay), scrub gate (`.githooks/pre-commit` + CI). **proposed:** SessionStart (DDR-004), PreToolUse (DDR-002 §3.4) | mixed; **see Gap D3** |
| **Cross-cutting practice** | this doc + global CLAUDE.md | DDR-001, DDR-002, no-hedge/personal-signoff/research-integrity | principles exist; binding uneven; **see Gap D4** |

---

## Part C — The Living Practice: Signpost, not pillar

Not a phase — a discipline that runs from cold start through close. A **sequence**, not an either/or.

- **Signpost** = the narrative you're handed — prior-session LORE, git position, recorded progress, a teammate's paraphrase, a summary. It **orients**: tells you where to look and what changed. Necessary and legitimate. But it records past *conclusions*, not what is true right now.
- **Pillar** = the ground truth, **built by verifying the signpost against the primary source.** Two forms: **read the document** for a claim about a decision/spec/history; **run the read-only probe** (`git rev-parse`, a freshness query, a gate self-check) for a claim about live system state. A document says what was true when written; a probe says what is true now.
- **The rule (source: `market_data` POSTMORTEM-2026-06-29 §4.2 + `session_probe.py`):** *"memory tells you where to look; the pillar tells you what is actually true right now."* The disease is **narrative knowledge, not ground-truth knowledge** — priming on a story and filling gaps with inference. The cure is **traceability, not more documentation**: every claim traced to a file/line/query you can re-run. *"Do not take its word for anything."*
- **Objective:** no confident decision or claim reaches Danny without verification against the primary source. Internal-consistency ≠ validity — green tests, gates, seals, and LORE captures all measure consistency, never truth; never cite one as proof.
- **Enforcement trajectory:** today a principle (arbitrageable) → DDR-004 binds it to the SessionStart prime (adopting the existing `session_probe.py` pattern) so verification is not optional at the one place it silently was.

---

## Part D — Control-Gap Register (feeds DDRs)

| # | Gap | Evidence | Disposition |
|---|---|---|---|
| **D1** | **DDR numbering + location is unnamespaced and divergent.** 3-digit (agent-rig, agent-dashboard) vs 4-digit (gaplens); per-repo namespaces collide semantically (three repos each have a "DDR-001"); gaplens has a real **duplicate `DDR-0008`**; transfer DDRs live in the surrendering repo's dir, so agent-rig "DDR-013/014" are physically in agent-dashboard. No ecosystem convention for numbering, width, or where a cross-cutting DDR lives. | this session's `ls` across the three DDR dirs | **DDR candidate** |
| **D2** | **Git workflow conflates policy with protocol; local docs override global tooling.** Policy (per-repo mode) and protocol (branch→slice→commit→PR sequencing) share one filename; agent-dashboard's `GIT-WORKFLOW.md` explicitly "wins over global `/forge-start`" — a repo-local patch around under-specified shared tooling. Forge's Git-Flow-Determination is binary (no feature-branch-no-PR mode). | §66 of agent-dashboard `GIT-WORKFLOW.md`; forge-start `Git Flow Determination` | **DDR-005 candidate** (this session) |
| **D3** | **Hook enforcement is half-built with no registry.** Two hooks live (`Stop`, scrub gate), two proposed (SessionStart DDR-004, PreToolUse DDR-002 §3.4); no single place enumerates what hooks exist, what they gate, and their deploy state. | `~/.claude/settings.json` holds only `Stop` | folds into DDR-002 §3.3 registry + DDR-004 |
| **D4** | **Principles exist but binding-to-mechanism is uneven.** Pillar, no-hedge, ask-vs-act, always-redispatch are all real; only some are bound to a harness mechanism, the rest rely on agent judgment (which demonstrably fails — see DDR-004's motivating incident). | DDR-004 §1 | DDR-004 (pillar); no-hedge backlog item |

---

## Part E — Ownership Summary

- **agent-rig (Wright)** owns the *source-of-record* for: orchestration packages, Frank + shared personas, HOMELAB/MACHINE-SETUP templates, `/new-project`, the session-start pattern, and this map. Per-repo files are instances, never sources.
- **Each repo** owns its own git *policy* (declared in its CLAUDE.md section) and its own DDRs.
- **agent-lore** owns LORE schema/lifecycle and the future `PromptAssembler`.
- **Danny (Composer)** ratifies this map, North Star docs, and identity-artifact edits personally.
