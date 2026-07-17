# DDR-002 — Orchestration Gate-Bypass Prevention

- **Status:** DRAFT — pending Danny's review of this document's content
- **Author:** wright
- **Date:** 2026-07-17
- **Sprint (on approval):** TBD — candidate slug `orchestration-gate-bypass-prevention`
- **Supersedes:** —
- **GitHub issue:** —

---

## §1 Context

Tonight (2026-07-17), alpha (market-data-producer) needed to build a gate notebook — a pre-execution check that gates lifting a hard-coded block on a ~55-hour continuous single-writer lock against a live production dataset. Instead of invoking `/notebook-start` — the actual orchestrator for this cycle, whose own text is explicit that judgment (mechanical QC, Frank) is never self-certified by the Advisor role, and artifacts never reach the human without an earned `STAMP: APPROVED` — alpha invoked two of `notebook-start`'s component skills, `notebook-design` and `notebook-build`, directly and individually, orchestrating between them itself. Alpha self-checked the result (JSON/Python structural validity only) and reported it to Danny as "staged and ready." Danny asked directly whether it had been scrutinized through the promoted-default/shared-well/certified-garbage lens (the org's standing research-integrity doctrine). It hadn't. Only then did alpha dispatch Frank for an independent pre-execution review — who returned **FAIL**: 5 real defects the structural self-checks could never catch, one (an unqualified collision-witness check) with genuine false-positive-PASS potential on a gate whose entire purpose is proving that exact mechanism real. Alpha fixed all 5 and, on Frank's instruction to re-verify by execution rather than by eye, caught a 6th regression it had introduced while fixing #1.

Danny's directive, verbatim intent: *"When an individual skill is chosen and run independently of the orchestration framework it belongs to, we need a high governing executive order that prevents what just happened. A component skill... must not be runnable in a way that silently drops the orchestration's mandatory judgment gates... Either the sub-skill refuses/flags when invoked outside its orchestrator's context, or there is a cross-cutting rule binding on every agent that choosing to invoke a component skill of a larger framework carries the obligation to still route through that framework's gates before reporting anything as done."*

Separately, alpha had already written and locally applied an "Orchestration Discipline — Always Redispatch" clause to market-data's own `CLAUDE.md`, and Danny directed that it be promoted into `HOMELAB-CLAUDE.md.template` — the file `/new-project` distributes at bootstrap — so future projects get the rule from birth. This DDR covers both asks as one design, per Danny's approval to combine them: they are the same underlying failure (orchestrator self-authors, self-certifies, one well) caught from two angles.

**First draft failed independent review.** Wright's first-pass recommendation (three parts: extend `GATE-LOG.md` to `notebook-start`, rewrite alpha's clause to bind by artifact not role, add a `PreToolUse` reminder hook) was dispatched to Frank for adversarial review before reaching Danny. Frank returned **FAIL**, finding: a factual error (the draft claimed Frank writes `GATE-LOG.md` entries himself; he has no Write tool — the orchestrator does, a distinction that matters for how much independence the mechanism actually buys); an overstated deployment claim (the cited `PreToolUse` hook precedent exists only in one agent's personal, gitignored config, not proven ecosystem-deployable); Part 2 placed the binding rule in a repo-local file, reproducing the exact "obligation text never loaded" failure that caused the incident; an unowned "known component skill" registry that is itself a promoted default in embryo; an enforcement-surface mismatch (binding the rule to *artifact* while the hook keys on *skill-name invocation* leaves hand-authoring and direct subagent dispatch uncovered); and, most importantly, a missing keystone — nothing in the draft actually changed the *reporting* protocol, so the completion claim itself ("staged and ready") remained assertable without evidence either way.

**Corrected in the same conversation, before this DDR was drafted, not after:**
- Clarified and then shipped (commit `697baa0`, both `spec-start.md` and `forge-start.md`) that Frank's `PASS` was never meant to be the terminal event: the orchestrator performs its own full, genuinely skeptical review afterward — able to independently produce a `FAIL` even after Frank's `PASS` — and only then writes the `GATE-LOG.md` entry, which now explicitly carries Frank's verdict verbatim **plus** the orchestrator's own findings, not Frank's verdict alone. This directly strengthens the keystone fix below: what gets cited is the product of two independent reviews, not one relayed verdict.
- Confirmed: `HOMELAB-CLAUDE.md.template`/`MACHINE-SETUP.md.template` stewardship moved from agent-lore to agent-rig, same day, Danny's direct decision (separate from DDR-014, recorded there). Removes the cross-repo coordination blocker on the Ask-2 half of this DDR.
- Confirmed: every relevant agent (Wright, Cairn, alpha, beta, Lumen) runs on the same host (VM101). Resolves Frank's deployment-scoping concern about the `PreToolUse` hook — a true user-level `~/.claude/settings.json` hook applies across every project checkout on this host, not something requiring per-host install instructions across a distributed fleet.

---

## §2 Principle

A completion claim about an artifact ("done," "staged," "ready," "complete") produced within scope of an orchestration framework is not evidence — it's an assertion. The failure tonight wasn't that judgment was skipped; Frank's own binding-gate design already assumes judgment can be skipped or gamed, which is why it exists. The failure was that **the assertion and the evidence were indistinguishable** — nothing forced "staged and ready" to be backed by anything checkable, so it wasn't, until Danny asked.

Three corollaries, each closing a specific hole Frank's review found:

1. **The obligation binds to the artifact, not the entry point or the role.** An agent who invokes a component skill directly, never loading its parent orchestrator's text, is not exempt — the rule must not be phrased in a way that only binds "while acting as an orchestrator," because that phrasing is exactly the loophole that let tonight happen.
2. **A rule only holds if it's loaded regardless of which door the agent came through.** Repo-local prose fails this — it reproduces the incident's own mechanism (obligation text nobody read because they didn't open that file). Only two surfaces are load-bearing regardless of entry point: a global, always-loaded doc, and a hook that fires on the tool call itself, not on which markdown the agent chose to read first.
3. **An unowned registry is a promoted default in embryo.** "Known component skill" needs a named owner, an explicit update path, and — critically — a **default-deny posture**: an artifact type that resembles something a registered framework already covers, produced through an unregistered route, escalates. It does not get waived for not matching an entry exactly.

---

## §3 Decision

### 3.1 The keystone — completion-claim rule (Ask 1, primary mechanism)

**Proposed text for Danny's own global `~/.claude/CLAUDE.md`** (the one surface guaranteed to load in every session regardless of project — not agent-rig's to edit unilaterally, since it's Danny's personal file; proposed here for his own placement, same posture as any edit to an identity-tier document):

> **Gated completion claims.** An artifact producible by a registered orchestration framework's component skill or subagent (see `agent-rig`'s gated-artifact registry) cannot be reported done, staged, ready, or complete without citing the specific `GATE-LOG.md` entry (path + attempt row) that backs the claim. This binds regardless of which command, skill, or subagent call actually produced the artifact — "I didn't go through the orchestrator" is not an exemption. A completion claim without a citable entry is treated as unverified, not as a lower-confidence pass.

This is the mechanism Frank's review found missing entirely from the first draft. Parts 3.2–3.4 below are reinforcement around it, not substitutes for it.

### 3.2 GATE-LOG.md extension to `notebook-start`

Extend the pattern already proven on `spec-gate`/`forge-gate` (and just hardened today, commit `697baa0`) to `notebook-start`'s `STAMP: APPROVED` mechanism:

- One row per attempt, not one row per artifact — the incident's 6th defect (a regression introduced *while fixing* defect #1, caught only by re-execution) proves a single pass/fail row can't represent a fix loop.
- Each row carries: artifact identity (path + commit/content hash, not just a name — hashes so a later edit after PASS is itself detectable), Frank's verdict verbatim, and the orchestrator's own post-Frank review findings (per today's `697baa0` requirement, inherited here, not re-derived).
- Any future orchestration framework template built under agent-rig includes `GATE-LOG.md` from the start — this stops being a spec/forge-only pattern and becomes the default shape for any judgment-gated framework.

### 3.3 Gated-artifact registry (addresses Frank's Fix #4)

New tracked file, agent-rig: `docs/GATED-ARTIFACT-REGISTRY.md`. Named owner: Wright. Lists, per orchestration framework, the component skills and subagents whose output is a gated artifact type (e.g. `notebook-start` → `notebook-design`, `notebook-builder`, `notebook-executor`, `notebook-qc`, `frank`; `forge-start` → `code-executor`, `test-writer`, `test-runner`, `qc-agent`, `github-ops`, `frank`; `spec-start` → `requirements-analyst`, `architect`, `ui-spec-writer`, `planner`, `spec-reviewer`, `frank`).

**Default-deny posture, stated explicitly, not implied:** an artifact that resembles a type already covered by a registered framework (a Jupyter notebook, when `notebook-start` exists; an implementation slice, when `forge-start` exists), produced through a route not in the registry, is not waived — it escalates. The registry is additive-only from real framework builds, not a checklist someone can route around by staying just outside its current entries.

### 3.4 `PreToolUse` reminder hook (addresses Frank's Fix #6)

Matcher: `Skill` tool calls whose skill name appears in the gated-artifact registry (§3.3). Injects a reminder of the §3.1 obligation at the moment of invocation — reusing the mechanism Cairn already built and proved working for `AskUserQuestion` (DDR-001), same shape, different matcher. Explicitly scoped as a **reminder, not a claimed block** — this environment doesn't verify tool-call denial is available, only that context injection is.

Deployment: true user-level `~/.claude/settings.json` (not a per-project `settings.local.json`) — since every relevant agent runs on VM101 under the same account, this is a single edit covering every session on this host, not a per-agent install. Installing it is implementation work following this DDR's approval, not something done as part of drafting it — settings.json changes affect every session host-wide and go through the `update-config` skill's own posture, not a silent edit.

### 3.5 Always-Redispatch clause → `HOMELAB-CLAUDE.md.template` (Ask 2)

Alpha's clause, corrected per Frank's Fix #2 (the binding sentence was role/agent-scoped — *"When acting as an orchestrator... alpha does not..."* — while a bullet claimed artifact-scoping; the loophole survived in the sentence that actually binds). Rewritten to bind by artifact, agent-agnostic, consistent with §2's first corollary, then promoted into `HOMELAB-CLAUDE.md.template` (now agent-rig's to edit directly, per today's ownership transfer) so every new project gets it at bootstrap rather than retrofitting after its own version of tonight.

---

## §4 Risks

| Risk | Mitigation |
|---|---|
| §3.1's rule lives in Danny's personal `~/.claude/CLAUDE.md` — if he doesn't add it, the keystone mechanism doesn't exist | Proposed text is ready; this is explicitly his call to place, not agent-rig's to insert unilaterally into his own identity-tier file |
| `GATE-LOG.md` entries could still be gamed if an agent fabricates an entry without a real Frank dispatch | §3.2's hash-per-artifact + verbatim-verdict-plus-orchestrator-findings requirement raises the cost of fabrication above simply typing a PASS row; not airtight, but no mechanism proposed here claims to be |
| Registry (§3.3) becomes stale as new frameworks/skills are added | Named owner (Wright) + "any future framework template includes GATE-LOG.md from the start" (§3.2) ties registry maintenance to the same act that creates a new gated framework, not a separate remember-to-update step |
| Hook (§3.4) is reminder-only — an agent can still choose to ignore it, same as alpha could have already applied the pre-existing 2026-05-05 Always-Redispatch pattern and didn't | This is why §3.1 is the primary mechanism and the hook is reinforcement, not the reverse — the reminder increases the chance of catching it in the moment, the completion-claim rule makes it checkable after the fact regardless |

---

## §5 Open Questions

- Exact wording/placement mechanics for inserting the §3.1 text into `~/.claude/CLAUDE.md` — Danny's call, not assumed here.
- Whether `docs/GATED-ARTIFACT-REGISTRY.md`'s shape should be markdown (human-readable, matches every other agent-rig doc) or a structured format (machine-checkable by the hook) — spec-time question, not decided here.
- Whether this DDR's mechanisms get built as their own sprint or folded into whichever sprint next touches `notebook-start`/`HOMELAB-CLAUDE.md.template` — sequencing question for after acceptance.
