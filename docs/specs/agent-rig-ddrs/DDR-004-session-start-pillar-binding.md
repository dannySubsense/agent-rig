# DDR-004 — Session-Start Signpost→Pillar Binding

- **Status:** DRAFT — concept rewritten against source doctrine ("Signpost, not pillar" — `market_data/docs/reports/POSTMORTEM-2026-06-29-v1-dead-code-and-false-alarm.md` §4.2, `market_data/scripts/session_probe.py`). Danny approved §2 + §3.1 (2026-07-21). **Frank re-gate PASS (attempt 3, both layers firm — Layer 2 no longer PROVISIONAL: `docs/NORTHSTAR.md` verified Established 2026-07-17, not DRAFT).** Ready for `/spec-start` sprint `session-start-signpost-pillar-binding`. **Substrate CONFIRMED (2026-07-21):** SessionStart hook→context injection fires on VM101 (Danny observed the injected marker in a fresh session; throwaway test torn down). Slice 0 is now "stand up the real probe hook end-to-end," not a capability risk. Adopts the proven `session_probe.py` pattern (routed to Lumen for `/new-project`; Cairn built one for Major Tom) — generalize, do not reinvent.
- **Author:** wright
- **Date:** 2026-07-20
- **Sprint (on approval):** TBD — candidate slug `session-start-pillar-binding`
- **Supersedes:** —
- **GitHub issue:** —

---

## §1 Context — a live failure, not a hypothetical

This DDR is written from a failure Wright committed in the session that produced it (2026-07-20, cold start).

Wright ran the three session-start checks (LORE prime, Switchboard inbox, `git`) — the **signpost**: prior-session LORE captures, git position, recorded progress. Wright then **reported status assembled from those captures** — "DDR-002 ACCEPTED," "scrub gate LIVE," "nothing unpushed" — and delivered them to Danny as confident fact. But none was **verified against the primary source this session**: the DDR-index file was not read, `git rev-parse` was not run on both refs, the gate was not probed. The signpost was treated as the pillar. The captures happened to be accurate — luck, not rigor; the identical shape in the origin postmortem (a true fact plus an untraced inference → confident wrong claim) turned dust into a fire.

This is the exact failure the origin doctrine names. From `market_data/docs/reports/POSTMORTEM-2026-06-29-v1-dead-code-and-false-alarm.md` §4.2, *"Narrative knowledge, not ground-truth knowledge"*: the repo's docs and LORE record **conclusions**, not **what is true right now in a form you can re-run**; *"at session start an agent primes on the narrative, absorbs a story, and then fills the gaps with inference."* The cure named there is **traceability, not more documentation**: *"every factual claim cites a file, line, or query you can check yourself. Do not take its word for anything."*

Two distinct defects, one root:

1. **The signpost was mistaken for the pillar.** The session prime *correctly* delivered orientation (LORE/git/progress) — that is what a signpost is for, and receiving it is right. The failure was stopping there: asserting from the narrative without building the pillar (reading the referenced document / running the probe). The global `~/.claude/CLAUDE.md` Research Data Integrity rule already says the equivalent — *"a seal proves storage integrity, not content validity… never cite a test count, a gate, or a seal as evidence a finding is real"* — but the bridge from it to "therefore verify the signpost before asserting" was left to judgment, and that judgment was not exercised.

2. **The verification step was arbitrageable.** The session-start block says *run these checks*. It does not say *before you assert what a check implies, read the primary source it points to.* "Run the checks" was satisfied hollowly. A discipline the agent chooses whether to honor can be skipped, apologized for, and narrated around after the fact — which is exactly what happened.

This is a solved problem elsewhere. A proven reference implementation already exists — `market_data/scripts/session_probe.py` (read-only, run first each session, prints live git/DB/cron state; banner: *"memory tells you where to look; THIS tells you what is actually true right now… The pillar. Memory/docs are signposts on top of this — verify before you assert"*), routed to Lumen for `/new-project`; Cairn built a variant for Major Tom. The gap is not that the principle is unknown; it is that it is **not bound to the session-start priming mechanism tightly enough to be non-optional**, and agent-rig — the exporter of this discipline — had never adopted the existing pattern.

## §2 Principle — Signpost, not pillar (the source model, restored)

**Session start is a *sequence*, not an either/or.** It has two parts, and both are necessary:

1. **The signpost** — the session prime: prior-session LORE captures, git position, recorded PROGRESS. It **orients**: it tells you where to look and what changed. It is important and it is not optional. But it is **narrative** — a record of past *conclusions*, not ground truth about what is true right now.
2. **The pillar** — the ground-truth state, **built by verifying** what the signpost points to. Verification means consulting the **primary source**: reading the actual **document** for a claim about a decision/spec/history, or running a **read-only probe** (`git rev-parse`, `MAX(trade_date)`, a gate self-check) for a claim about live system state. A document records what was true when written; a probe tells you what is true now — both are the pillar, the narrative is the signpost.

*"Memory tells you where to look; the pillar tells you what is actually true right now"* (`session_probe.py`). The prior framing of this DDR — "session start is a pillar, not a signpost" — was wrong: it vilified the signpost (legitimate, necessary orientation) and mislabeled session-start (which is where you *receive* the signpost and must then *build* the pillar).

**The objective this binds:** stop the agent from making confident decisions and delivering overconfident claims to Danny **without verifying against the primary source.** The signpost is where you start; the pillar is what you must build before you assert. This is the org-level Research Data Integrity rule (*"a seal proves storage, not validity"*; *"check the input before the instrument"*) at session-start scope — not new discipline, the existing discipline restored to its source and bound to the one place it was silently optional.

## §3 Decision (to build; details deferred to spec)

Bind the signpost→pillar sequence to session-start priming through **two layers**, because the failure this DDR documents proves a single layer (instruction) is insufficient. Adopt the existing `session_probe.py` pattern rather than inventing a new mechanism.

### 3.1 The clause (human-readable statement of intent)
A verbatim block added to the session-start section of `HOMELAB-CLAUDE.md.template` and the `/new-project`-generated `CLAUDE.md`, so every project carries it and every agent reads it:

> **Signpost, not pillar.** Your session prime — prior-session LORE, git position, recorded progress — is a **signpost**: it orients you and points the way, but it is narrative, not ground truth. Before you state a status, make a decision, or deliver a claim, **build the pillar: verify it against the primary source.** For a decision/spec/history claim, read the actual document. For a live-state claim (git position, freshness, a gate), run the read-only probe. A prior session's capture tells you *where to look*, never *what is true now*. If you would assert something you have only read *about* — stop, open the source, and confirm it this session. Do not take the narrative's word for anything.

The clause alone is what already failed. It is necessary (states intent, names the concept so it can't be un-known) but **not sufficient** — it is still an instruction an agent can arbitrage.

### 3.2 The enforcement (SessionStart hook that runs the probes)

> **Capability status (Frank FAIL 2026-07-20, remediated).** The original draft asserted this keystone as settled design and borrowed a false precedent (see §3.3). Corrected state, two rungs:
> - **Rung 1 — documented (CONFIRMED):** `SessionStart` hooks *can* inject text into the model's context window, via plain stdout or a `hookSpecificOutput.additionalContext` field. Verified against the official Claude Code hooks documentation, `https://code.claude.com/docs/en/hooks.md` (fetched 2026-07-20, not asserted from memory). Matcher values `startup | resume | clear | compact` exist and are scopable — the pillar hook will scope to `startup|resume|clear` and **exclude `compact`** to preserve the once-per-cold-start property (mid-session compaction must not re-fire it).
> - **Rung 2 — host-empirical (CONFIRMED 2026-07-21):** SessionStart context-injection fires on VM101. Proven by a throwaway `SessionStart` hook (`hookSpecificOutput.additionalContext`, matcher `startup|resume|clear`) armed in an isolated scratch project; a fresh Claude session started there **observed the injected marker `PILLAR-PROBE-7X9Q2` in its context** (confirmed by Danny), and the hook's sentinel logged the fire. The keystone the design rests on is no longer a hypothesis. Spec Slice 0 remains as the *first implemented slice* (stand up the real probe hook and re-confirm end-to-end with the actual `session_probe`-style output), but the capability risk is retired. Kill-condition no longer active.

A `SessionStart` hook — harness-executed, not agent-elected — that runs a **read-only ground-truth probe** (the pillar-builder for live state) and injects its raw output into context. **Adopt and generalize the proven `market_data/scripts/session_probe.py` pattern — do not reinvent it.** The probe prints:

- `git fetch` + `git rev-parse HEAD` and `origin/<branch>` (both refs, printed), working-tree status;
- the DDR-index / PROGRESS status lines (the file's own text, not a summary);
- a live probe of any repo-declared gate (e.g. scrub-gate self-check).

Note the division of labour from §2: the **probe** builds the pillar for *live-state* claims (git, freshness, gates). It cannot build the pillar for *decision/spec* claims — those require the agent to open and read the referenced **document**, which no hook can force. The hook's job is to make the live-state pillar unavoidable *and* to carry the §3.1 clause that directs the agent to the documents; the document-reading itself stays a discipline the clause names and the probe cannot replace.

The critical design point, learned from this failure: a **reminder-only** hook that merely re-injects the §3.1 text is *not enough* for the live-state half — it leaves verification to the same judgment that just failed. The probe must **put live ground truth mechanically in context**, so relaying a stale capture is visibly contradicted by data already on screen. The hook cannot force correct reasoning; it removes the option of *not having the live source present*, which is where the "sailor's yarn about missing it" comes from.

### 3.3 Portability
Both layers ship to every project, not just agent-rig: the clause via the HOMELAB template + `/new-project`; the hook via a globally-deployable `~/.claude/` SessionStart hook (single host, VM101 — centrally deployable). Per-project probe specifics (which gate to probe, which status file) resolved at bootstrap from the generated `CLAUDE.md`, so the hook is generic and the project supplies its targets.

> **Cross-reference correction (Frank FAIL 2026-07-20).** An earlier draft claimed this ships "same as the DDR-002 §3.4 hook mechanism." That is wrong on two counts and is withdrawn: (a) DDR-002 §3.4 is a **`PreToolUse`** hook — a *different event* with different firing semantics than `SessionStart`; (b) it is **committed-to-build, not deployed**, and is itself explicitly hedged as context-injection-only. It is neither the same mechanism nor a proven one, and cannot lend proven-ness here. The two are *siblings in thesis* (bind an arbitrageable instruction to a harness hook) only — not a shared implementation. Central single-host deployability is a property of the host (VM101), not inherited from §3.4.

## §4 Relationship to existing work

- **Source doctrine + reference implementation (must build against, not paraphrase).** The concept originates in `market_data/docs/reports/POSTMORTEM-2026-06-29-v1-dead-code-and-false-alarm.md` (alpha) and its operational half `market_data/scripts/session_probe.py`; the per-project feedback memory is `feedback_signpost_not_pillar`. This DDR's first draft drifted by working from the spec-forge docs' derivative use of the phrase instead of the origin — the exact failure the concept forbids, applied to itself. The rewrite is anchored on the primary sources above. The probe pattern was already routed to Lumen for `/new-project` and re-implemented by Cairn for Major Tom — agent-rig adopts/generalizes it.
- **Thesis-sibling to DDR-002 §3.4** (PreToolUse gate-bypass hook) — shares only the "instruction is arbitrageable, bind it to the harness" thesis, at a different trigger point (session start vs. gated-skill dispatch). *Not* a shared mechanism and *not* a proven precedent (see §3.3): different hook event, and §3.4 is committed-to-build. Central single-host deployability is a property of VM101 itself, not inherited from §3.4.
- **Absorbs / supersedes backlog item "promote the 3-check session-start block"** (DDR-INDEX) — that item moves the *checks* into the template; this DDR adds the pillar clause + enforcement that makes the checks non-hollow. They are one HOMELAB-template-hardening pass; this DDR is the correct home for it.
- **Sibling to the "no-hedge GATE" backlog item** — both convert an aspirational value into a checkable, non-arbitrageable gate. Same design property: detection must not depend on the agent's correct introspection.

## §5 Risks

| Risk | Mitigation |
|---|---|
| Hook injects probe output but agent still relays the stale capture over it | The contradiction is now *visible in-context* (ground truth on screen); combined with §3.1 clause it is detectable by any reader/reviewer, where before it was invisible. Not a guarantee of correct reasoning — an removal of the "I didn't have the data" excuse. |
| SessionStart hook slows every cold start (runs `git fetch` + probes) | Probes are the same commands the 3-check block already prescribes; the hook runs them once, deterministically, instead of the agent running them ad-hoc or skipping them. Net cost is neutral-to-lower. |
| Hook is over-engineered / brittle across projects | §3.3 keeps the hook generic and project targets bootstrap-resolved; YAGNI-gate the probe set to git + status-file + declared-gate, not an open-ended probe framework. |
| Reminder-only hook shipped instead of probe-running hook (the tempting shortcut) | Called out explicitly in §3.2 as insufficient; spec must implement the probe-running version or the DDR's whole point is lost. |

## §6 Open Questions (for spec)

- **Does `SessionStart` context-injection actually fire on this host (VM101)?** — Rung 2 in §3.2. *Existence of the feature* is answered (documented, cited); *host-empirical confirmation* is spec Slice 0, gating. This was an unstated assumption in the first draft; promoted to an explicit, must-answer-first question per Frank.
- Hook mechanism specifics: `SessionStart` hook only, or does any part need `PreToolUse`? Docs confirm `SessionStart` matcher scoping — plan is `startup|resume|clear`, exclude `compact`, to preserve the once-per-cold-start property (the 3-check block's inbox check has this same once-only property). Confirm this scoping behaves as documented during Slice 0.
- Probe set scope: git + status-file + declared-gate is the proposed minimum. Which gates does a project declare, and how (a line in the generated `CLAUDE.md`)?
- Failure mode when a probe itself errors (no network for `git fetch`, missing status file): inject the error into context (fail-loud) vs. HALT. Bias: fail-loud, never silently skip — a skipped probe reads as "all clear."
- Does the clause wording need Danny's / North-Star-adjacent sign-off before distribution (template-tier + identity-adjacent language)? Assume yes per existing personal-signoff discipline.
