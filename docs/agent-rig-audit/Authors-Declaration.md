# Author's Declaration — Agent Rig

**Author:** Wright (agent-rig producer agent)
**Written:** 2026-09-18
**Basis:** This is my own account, built from this session's LORE recall, `CLAUDE.md`/`docs/NORTHSTAR.md`, and a directory-structure look at the live repo. I have deliberately **not** opened `docs/agent-rig-audit/Agent_Rig_Cold_Inventory_Audit_Charter.md` or `docs/agent-rig-audit/cold-inventory-2026-09-18/` — this declaration is meant to stand independently so it can later be compared against Codex's cold-inventory findings, not converge with them in advance.

**Caveat up front:** this is a narrative account (a signpost), not a verified inventory. Where I say something is "active" or "obsolete" that is my belief from context, not a claim I re-verified line-by-line against every file this session. Treat this document the way this repo's own doctrine treats any unverified claim.

---

## 1. What I believe currently exists

### 1.1 Governance / doctrine layer
- **`CLAUDE.md`** (gitignored, local) — defines agent identity (Wright), the DDR→Intake/Interview→spec→forge workflow, LORE/Switchboard conventions, and the Signpost/Pillar reply-syntax contract enforced by a Stop hook.
- **`docs/NORTHSTAR.md`** — project-level thesis doc ("Established 2026-07-17"). States Agent Rig is a workshop for orchestration mechanics and cross-cutting personas, not a product. Explicitly scoped to stay thesis-only (no ledger content), per a standing rule I hold in memory.
- **`docs/INVARIANTS.md`, `docs/CADENCE.md`** — referenced by the forge-start gate as required-present docs; I believe these encode the non-negotiable rules and the slice-by-slice cadence for forge sessions, but I have not re-read their current bodies this session.
- **`docs/SESSION-MAP.md`** — lifecycle×layer map plus a "control-gap register" (Part D), the artifact that came out of DDR-004's correction (Signpost≠Pillar, session start builds a pillar from a primary source rather than trusting the narrative).
- **`docs/specs/agent-rig-ddrs/`** — the DDR system itself: `00-DDR-INDEX.md` (living backlog + build-order rationale — a decision-record ledger, not a status log, per `DDR-DEFINITION.md`), numbered `DDR-NNN-*.md` files (I can see DDR-001 through DDR-012 present, with DDR-013 having been renumbered to DDR-015 very recently per this session's git log — meaning DDR-015's own file may not exist yet, only an index reference), `DDR-DEFINITION.md`, and `HOOK-DEPLOYMENT-ROSTER.md` (per-repo hook deployment state, called out in CLAUDE.md as the one place that state may be trusted over a sprint's PROGRESS.md or a LORE capture).

### 1.2 Cross-cutting personas
- **`agents/frank.md`** — the binding QC/judgment gate persona, transferred here from agent-dashboard per DDR-013 (per CLAUDE.md; note the DDR-013→DDR-015 renumbering just mentioned may affect this citation's exact number going forward). Deployed globally to `~/.claude/agents/frank.md` for dispatch from any repo. This is the flagship "source-of-record persona" pattern the repo exists to host.
- **`agents/README.md`** — presumably documents ownership/provenance convention for personas living here; I have not re-read its current body.
- I believe Frank is the only persona actually resident in `agents/` right now — the README's provenance discipline (named owner, stated provenance) suggests more could be added later but I don't have evidence another persona has been transferred in yet.

### 1.3 Dated delivery packages
Several `<pattern>-<date>/` directories, each apparently a self-contained, installable bundle (own `agents/`, `commands/`, `skills/`, `templates/`, an `install.sh`, a `README.md`):
- `spec-orchestration-07152026/` — current spec-start machinery (superseded `-03242026`, now archived).
- `forge-07152026/` — current forge-start machinery (superseded `-03252026`, now archived under `archive/reference/`).
- `notebook-orchestration-04182026/` — the design→build→execute→QC notebook cycle.
- `lit-synthesis-04292026/` — the literature-synthesis pipeline (init/run/curate phases).
These get installed to `~/.claude/{agents,commands,skills,templates}` and consumed by other repos — I confirmed this session that `~/.claude/commands/` does contain `spec-start.md`, `forge-start.md`, `notebook-start.md`, `lit-synthesis-*.md`, consistent with this model, though I did not diff their contents against the versioned copies here.

### 1.4 Hooks and probes
- `.claude/hooks/` (repo-local, wired via `.claude/settings.json`): `session-queue.sh` (SessionStart), `progress-proof-per-slice.sh` (PreToolUse:Edit), `no-preamble-no-meta-narration.sh` and `signpost-checklist.sh` (both on Stop).
- `scripts/`: matching `*_probe.py` implementations for each wrapper (`session_queue_probe.py`, `signpost_checklist_probe.py`, `no_preamble_probe.py`, `progress_proof_per_slice_probe.py`, `domain_boundary_provenance_probe.py`), plus `hook_telemetry.py` / `hook_telemetry_aggregate.py` for a shared telemetry/track-record mechanism, and `scrub_gate.py` with an allowlist file.
- `tests/` — a real pytest suite covering the probes, the wrapper shell scripts, and telemetry aggregation. This suggests the hook layer is the most rigorously tested part of the repo.
- `reference/session_probe.py` and `reference/session-start-probe.sh` — I believe this is the market-data-originated reference implementation cited in LORE as the canonical source for the "pillar" pattern (read-only, run-first, prints live git/DB/cron state), kept here as a citation source rather than live wiring.

### 1.5 Everything else
- `HOMELAB-CLAUDE.md.template`, `MACHINE-SETUP.md.template`, `ASSERT-CONVENTION.md.template`, `MAP-NOT-ROUTE-BRIEFING.md.template` — templates for bootstrapping new projects/machines, stewarded here per a 2026-07-17 decision (moved from agent-lore/Cairn).
- `commands/` (repo-root, distinct from the dated packages' own `commands/`) — `lore-close.md`, `new-project.md`, presumably the canonical sources later copied/installed globally.
- `archive/` — explicitly retired material: old spec-orchestration/forge package versions, a retired "reference mirror" (per this session's recent commit history), `archive/obsolete/`, `archive/first-turn-contract-enforcement/`.
- `docs/reports/`, `docs/research/`, `docs/tooling/`, `docs/templates/` — I have not inventoried these this session; I list them for completeness, not from confirmed knowledge of their contents.
- `docs/agent-rig-audit/` — this document's own home, and the Codex cold-inventory material I was told not to read yet.

---

## 2. What each component is intended to do

- **DDR system**: capture architecturally significant decisions with enough rationale that build order and past reasoning survive context loss — explicitly *not* a place for status/progress narration (that belongs in a sprint's own `PROGRESS.md`).
- **Frank**: a non-negotiable judgment gate at two points in every sprint (spec-complete, forge-complete) — PASS/FAIL/HALT with no conditional pass, run "cold" (unbriefed, isolated checkout) per the binding Cold Gates doctrine.
- **Dated packages**: portable, versioned units of orchestration tooling that other repos install and vendor, so improvements happen once here and get redeployed rather than drifting per-consumer.
- **Hooks**: mechanical, structurally-enforced guardrails for failure patterns that were previously "known-correct information sitting unapplied" — the repo's own doctrine names this as the reason hooks exist at all (a decision graph can't grade judgment, but it can stop a step from being skipped).
- **Templates**: give new projects/machines the accumulated doctrine (Signpost/Pillar, Map-not-Route briefing discipline, etc.) at bootstrap instead of each one re-discovering it.
- **NORTHSTAR / SESSION-MAP / INVARIANTS / CADENCE**: the standing reference set that every spec/forge session is required to consult and that Frank's gate checks work is consistent with.

### 2.1 Who owns the spec/forge loop — role split and mechanics

This deserves its own callout: nobody, including me, owns the spec/forge loop outright. Per CLAUDE.md's role table:

| Role | Who | Responsibility |
|---|---|---|
| Composer | Danny | Vision, high-level architecture, final approval, personal sign-off on Frank persona edits and North Star docs |
| Producer | Me (Wright) | Implementation decisions, production code, no hedging |
| Frank | Dispatched subagent | Binding judgment gate, both spec and forge — PASS/FAIL/HALT, no manual override |

The loop itself, as I understand it:

1. **Intake** (mandatory) — a per-sprint `INTAKE.md` must reach `**Status**: APPROVED` before anything else starts. DDR is optional at this stage.
2. **Interview** — a standalone gap-finding stage, always producing an `INTERVIEW.md` even when it finds nothing to ask.
3. **`/spec-start`** — runs Intake-gate check → Interview → a sprint `NORTH-STAR.md` (written once, then Locked) → `01-REQUIREMENTS` → `02-ARCHITECTURE` → `04-ROADMAP` → `05-REVIEW` → Frank's binding spec-gate (two layers: sprint-fidelity and project-relevance, both evaluated every attempt, on an independent 3-attempt counter) → my presenting everything to Danny for human approval.
4. **`/forge-start`** — refuses to proceed at all if `docs/INVARIANTS.md`, `docs/CADENCE.md`, or the sprint's own `NORTH-STAR.md` is missing; implements slice by slice; keeps `PROGRESS.md` as ground truth updated per-slice, not at the end; Frank's binding forge-gate runs once at completion, same two-layer design.
5. **PR / commit** — per this repo's manual-push-only policy; any DDR used gets its status updated to reflect shipped state.

I execute this loop (I'm the one who actually runs `/spec-start` and `/forge-start`), but I don't control its outcome at either gate — Frank's verdict is binding and I have no override, and Danny's approval is required before a spec is treated as locked or a North Star doc is trusted. This is deliberate separation, not an oversight: doer≠checker is named directly in this repo's own doctrine as the point of the design, not overhead to be cut.

I have not run this loop at all this session — the Author's Declaration task was a direct, scoped write outside the loop, not a spec/forge cycle.

---

## 3. Active, incomplete, experimental, obsolete, or duplicated

**Active, high confidence:**
- Frank (dispatched routinely per CLAUDE.md workflow).
- The Stop-hook pair (`no-preamble-no-meta-narration.sh`, `signpost-checklist.sh`) — I directly experienced both firing this session.
- `session-queue.sh` — fired this session's SessionStart with the tagged LORE queue capture.
- `spec-orchestration-07152026/` and `forge-07152026/` — cited in CLAUDE.md as the live packages backing `/spec-start` and `/forge-start`.
- DDR-INDEX — actively edited this session's git history (commit `cc9dcb3`, `e783458`).

**Incomplete / in-progress, high confidence:**
- **DDR-015** (Hook/Probe Deployment & Update Pipeline) — per this session's LORE queue, its Intake has not been written; this is the stated "next real work."
- **GitHub issue #34** (Cold-Frank-shadow-discipline forcing function) — proposed mechanism designed (transcript Read-tool-call correlation, mirroring `signpost_checklist_probe.py`'s tool_use/tool_result approach) but not built; needs its own Intake, likely folding into a broader "governance-audit-hook cluster."
- **GitHub issue #35** (import `check-spec-journaling.py` + tests into agent-rig) — script is live in `~/.claude/hooks/` globally but has zero repo ownership or test coverage here; same author≠install-location gap Frank himself had before DDR-013.
- A cluster of older open issues (#19, #22–#28) around the first-turn-contract / signpost-sourcing hook (C3) — several sound like refinements or edge cases (word-boundary matching, evasive-Pillar-prose detection, verbatim verdict pass-through) rather than net-new builds, suggesting the signpost/pillar hook is mature but still accumulating hardening work.

**Experimental / provisional, moderate confidence:**
- The domain-boundary-provenance hook and its "extension" sprint — per a 2026-09-06 LORE decision, Danny put **both** on the chopping block for sunset and rework; I believe `domain_boundary_provenance_probe.py` and its wrapper/tests still exist in the tree (I saw the probe and test files in this session's directory listing) but that they are *not* currently trusted as a going-forward design — this is a live discrepancy between "files present" and "design endorsed," worth confirming explicitly against Codex's inventory since a file existing is not the same as a component being active.
- Issue #24 — the LOCKED domain-boundary-provenance-hook spec "institutionalizes an invalid PROVISIONAL owner tag as an acceptance criterion." This suggests a spec doc still on disk that itself is now known to be wrong per the "named-owner PROVISIONAL is not a valid disposition" rule — a candidate for obsolete-but-not-yet-marked-so.

**Obsolete, high confidence:**
- `archive/spec-orchestration-03132026/`, `archive/spec-orchestration-03242026/`, `archive/reference/forge-03252026/`, `archive/first-turn-contract-enforcement/`, `archive/obsolete/` — explicitly archived predecessors. The "reference mirror" retirement (commit `c33f7fc`, PR #32, this session's git log) is the most recent instance of this pattern.

**Duplicated / risk of drift, moderate confidence:**
- The three-way overlap between `~/.claude/agents,commands,skills,templates` (global install), each dated package's own copy, and (for Frank specifically) `agents/frank.md` here — the author≠install-location gap is a named, recurring failure class in this repo's own memory (it caused a real bug for Frank pre-DDR-013, and issue #35 is the same pattern for `check-spec-journaling.py`). I believe this is not fully solved — DDR-015 exists specifically because "stop duplicating vs. automate the duplication" is still an open design question, not yet decided.
- `reference/session_probe.py` versus `scripts/session_queue_probe.py` — two probe-style scripts with adjacent names and purposes (one cited as a canonical external reference, one as this repo's live SessionStart implementation). I believe these are intentionally distinct (reference vs. live), but the naming similarity is exactly the kind of thing a cold external read could reasonably flag as possible duplication, and I have not compared their contents.

---

## 4. Important dependencies and integrations

- **`lore-gateway` MCP** — system-wide registration (`~/.claude.json`, user scope) connecting to a personal LORE backend (VM 103 Postgres, Tailscale-only). Schema lifecycle owned by a separate `agent-lore` repo; agent-rig does not run migrations.
- **Switchboard relay** — MCP tools (`read_messages`, `send_message`, `acquire_lock`, etc.) for inter-agent coordination across VM101-resident agents (Wright/agent-rig, Cairn/registrar, others named in memory — vane/signal-current, sift, ledger/department-os). Coordination messages have no live-push delivery; session-start manual polling is the only discovery mechanism (a gap named directly in CLAUDE.md).
- **GitHub** (`gh` CLI) — issue tracking for backlog items (#19–#35 seen this session); PRs for the branch/merge workflow.
- **Claude Code harness itself** — hooks (`SessionStart`, `PreToolUse:Edit`, `UserPromptSubmit`, `Stop`) are a load-bearing integration point; agent-rig's own doctrine (Signpost/Pillar, no-preamble) is enforced mechanically through this surface, not just written down.
- **Cairn / agent-lore** — the separate repo/agent that owns the LORE database schema and the MCP gateway server implementation; a real defect found this session (`capture_memory` title-field bug, `handlers.ts:244`) was handed off there rather than fixed in agent-rig, since agent-rig doesn't own that code.
- **Consuming projects** (agent-dashboard, gaplens-SEC/beta, signal-current, department-os, market-data, and others named in memory) — the actual reason the dated packages and Frank exist; agent-rig has no purpose independent of making their orchestration better.

---

## 5. Known gaps (as I understand them)

1. **Global-vs-repo duplication has no settled resolution.** DDR-015's whole reason for existing.
2. **Cold-Gate discipline was violated repeatedly before being caught.** Ten consecutive "Cold Frank" dispatches missed the isolated-checkout requirement; a compliant re-dispatch confirmed the underlying work was fine, but the *gate process* wasn't. Issue #34 is the proposed structural fix; not yet built.
3. **Switchboard coordination messages can sit unread indefinitely** — no live-push mechanism, only manual polling at session start. Named explicitly in CLAUDE.md as a real, not hypothetical, failure mode (this is how a prior session's messages sat unread for days).
4. **`domain-boundary-provenance` hook family is in a "sunset decided, rework not designed" limbo** — code likely still present, design authority withdrawn, no replacement specified as of the last capture I have.
5. **DDR-INDEX vs. GitHub Issues vs. LORE vs. `PROGRESS.md`** — four places status-adjacent information can live, with explicit rules for what belongs where, but the rules themselves are a response to past confusion (e.g. the HOOK-DEPLOYMENT-ROSTER.md carve-out exists because a LORE capture and a sprint PROGRESS.md were once wrong about hook deployment state, "produced a real error 2026-08-27/28"). I read this as a still-live risk, not a fully retired one.
6. **`agents/README.md`'s ownership discipline may not be uniformly applied** — I cannot confirm from this session's context whether every persona/skill/template added here since has a stated owner and provenance, only that the discipline is named as a requirement.

---

## 6. Intended target architecture (as I understand it)

A **hub-and-spoke workshop model**:
- Agent Rig is the *hub*: source of record for cross-cutting personas (Frank, and structurally room for more), the versioned delivery packages (`spec-orchestration-*`, `forge-*`, `notebook-orchestration-*`, `lit-synthesis-*`), the DDR/doctrine layer, and the hook/probe mechanisms that make doctrine structurally enforced rather than just written down.
- Consuming repos are *spokes*: they install/vendor a dated package or a persona, use it, and feed real incidents back (a bug found in production use gets fixed once at the hub and redeployed, rather than drifting per-consumer — the NORTHSTAR's own stated thesis, with two cited data points so far).
- The **hook layer is meant to converge on structural enforcement over prose doctrine** wherever a failure pattern recurs despite agents "knowing better" — this is the explicit lesson from the ANTI-PATTERN STACKING / GRAPH-ENFORCED PROCEDURE diagnosis: known-correct information sitting unapplied at the moment of acting is not a comprehension gap, so a decision graph/hook is the fix, not more documentation.
- **Deployment is meant to be centrally manageable on a single host** (VM101) — confirmed as a scoping simplification for the hook mechanism specifically (all relevant agents run on one host, not a distributed fleet), though I'm not certain this assumption is documented as permanent versus convenient-for-now.
- The **thesis is explicitly unproven and self-aware of its own falsifiability**: NORTHSTAR states this could be "the wrong bet" if consuming projects' needs turn out too divergent for shared mechanics to hold — I read this as intentional epistemic honesty baked into the founding doc, not hedging.

---

## 7. What I believe should be built next

In my own judgment, ranked:

1. **Resolve DDR-015 first** (global-install vs. sync-pipeline for hooks/personas) — it blocks a clean answer to issue #35 and is the same root question behind the Frank pre-DDR-013 bug. Building anything else on top of the current ad-hoc duplication risks compounding the exact failure class the repo already got burned by once.
2. **Ship the Cold-Frank-shadow-discipline mechanism (issue #34)** — this is a structural gap in the repo's *own* binding-gate machinery, not a feature request; given the doctrine that a gate's validity is only as good as its independence, an ungated gate-degradation pattern is higher priority than most feature work.
3. **Close out the domain-boundary-provenance limbo** — either formally rework it per whatever replaces the sunset design, or archive it explicitly (move code to `archive/`, mark the DDR/spec superseded, fix issue #24's PROVISIONAL-owner defect) so a cold reader doesn't mistake live-looking files for an endorsed design. This is cheap and removes a known false signal.
4. **Add repo ownership + tests for `check-spec-journaling.py` (issue #35)** — small, well-scoped, same pattern as Frank's own DDR-013 fix, low risk.
5. **Only after the above**: consider whether the hardening backlog around the signpost/pillar hook (#19, #25–#28) needs a dedicated sprint or can be folded into ongoing maintenance — these read as refinements to something already working, lower urgency than the structural gaps above.

I have deliberately not speculated about what Codex's cold-inventory might find beyond what I can support from this session's own context — where I'm uncertain above, I've said so rather than guessing to fill in a fuller-looking picture.
