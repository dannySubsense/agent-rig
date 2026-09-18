# Agent Rig Reconciliation

**Phase:** 2 — reconciliation
**Date:** 2026-09-18
**Repository inspected:** `/home/d-tuned/agent-rig`
**Frozen implementation baseline:** `cc9dcb3310f3415b9b6658d3cb8f90014a9bbe55`
**Current HEAD during reconciliation:** `dd42ca06b18512098e9094b26011eac2a0120747`

## 1. Result

Agent Rig is demonstrably a source workshop for Claude-oriented prompt bundles, personas,
templates, hooks, probes, and Git controls. It is not a standalone orchestrator, service, or
state machine. Its strongest capabilities are the small mechanical layer: package installers,
repo-local lifecycle hooks, Python probes, the scrub gate, and probe tests. Its spec/forge model,
Frank authority, human approvals, and most cross-project propagation rules are instruction-layer
contracts interpreted by an external runtime and people.

Wright's account is directionally accurate about the repository's purpose and broad inventory,
but it repeatedly promotes one of four weaker forms of evidence into an operational fact:

1. a Markdown instruction into an enforced invariant;
2. a process record into current system state;
3. a local installed artifact into a reproducible repository capability; or
4. a LORE/GitHub/session recollection into repository-supported evidence.

The proposed project map, `docs/agent-rig-audit/Agent_Rig_Build_Ideas_Index_and_Map.md`, is a
working canonical index reconstructed from project chats. It is useful as a target hypothesis,
but it is not repository reality: most of its durable runtime, event, evidence, control-plane,
communications, replay, and autonomy components have not been built here. Its five requested
inventory deliverables are the frozen Phase 1 reports; its recommended transition from inventory
to target architecture has not yet occurred.

Current HEAD differs from the frozen baseline only by the seven committed frozen-inventory
reports. No Agent Rig implementation changed between the two trees. The project map, Author's
Declaration, and audit charter were untracked inputs and were not modified.

## 2. Method and classification rule

Evidence precedence used here is:

1. current executable source, active routing/configuration, tests, and Git tree;
2. the frozen cold inventory and its captured runtime comparisons;
3. governing documentation when it describes intent or responsibility;
4. sprint records, DDRs, gate logs, telemetry, LORE-derived statements, issue references, and
   Wright's declaration as claims requiring corroboration.

The classifications are exclusive primary dispositions for this report:

| Classification | Meaning in this report |
|---|---|
| **Implemented** | Concrete mechanism exists and an active caller or route is evidenced. This does not imply complete or safe. |
| **Partial** | Material implementation exists, but a claimed path, enforcement boundary, dependency, test, or deployment step is missing or bypassable. |
| **Present but different** | An artifact exists, but its behavior, scope, status, or responsibility differs materially from the claim. |
| **Proposed only** | Intent or design is recorded, but no implementing repository mechanism was found. |
| **Obsolete** | Explicitly retired, archived, sunset, or contradicted by a later active mechanism. |
| **Duplicate** | Two or more artifacts claim or occupy the same responsibility or runtime destination. |
| **Not found** | Targeted repository, history, and accessible-path searches found no artifact. |
| **Indeterminate** | The claim depends on excluded, external, secret-bearing, or missing evidence. |

Passing tests, a gate PASS, a commit reference, a telemetry row, or an `ACCEPTED` label proves
only the fact it directly records. None is treated as proof of current end-to-end behavior.

## 3. Component reconciliation

### 3.1 Repository and governance surfaces

| Component or claim | Classification | Repository reality and reconciliation |
|---|---|---|
| Agent Rig as a workshop, not a product | **Implemented** | `README.md` and `docs/NORTHSTAR.md` match the as-built tree: declarative bundles plus a small hook/probe layer, with no application entry point. |
| `CLAUDE.md` as Wright identity and local operating contract | **Present but different** | The ignored local file exists and contains the described identity, LORE, workflow, and reply syntax. It is not clone-reproducible and therefore cannot be repository-wide canonical evidence. |
| `docs/NORTHSTAR.md` | **Implemented** | Present and coherent as thesis/non-goals. It is doctrine, not evidence that propagation or central stewardship succeeds. |
| `docs/INVARIANTS.md` and `docs/CADENCE.md` | **Present but different** | Present and labeled authoritative, but they include pending proposals and differ from other usage docs. `CADENCE.md` reflects conditional derivation of missing governance docs; Forge README says immediate HALT. |
| `docs/SESSION-MAP.md` | **Obsolete** | It is still `DRAFT v0.1 — pending Danny's review`, calls SessionStart and PreToolUse mechanisms proposed, and lists an older hook topology. Those mechanisms and replacements now exist. Its instruction to update the map first conflicts with its own primary-source doctrine. |
| DDR system | **Partial** | DDR files, definition, and index exist, but the index itself carries long current-status narratives, backlog, external-session claims, and duplicate row 004 despite `DDR-DEFINITION.md` prohibiting status-log behavior. |
| Numbered DDR file set | **Present but different** | Files exist for 001–010 except 011, plus 012. There are no local DDR-013, DDR-014, or DDR-015 files. Rows 011 and 015 exist only in the index. Wright's claim that files 001 through 012 are present is false. |
| Hook Deployment Roster as live-state source | **Partial** | The roster contains useful direct-read dates and correctly marks domain provenance sunset/unwired, but it is manually maintained Markdown about several external repos. It cannot itself make those external states current. |
| Ownership model | **Partial** | README prose assigns stewardship, and Git attribution exists. No `CODEOWNERS`, ownership manifest, release manifest, or install provenance record exists. |
| License | **Proposed only** | README explicitly says no license is declared and points to future selection. |
| `Agent_Rig_Build_Ideas_Index_and_Map.md` | **Present but different** | Present as an untracked working canonical index reconstructed from chats. It is a proposed target/product map, not an as-built architecture, and assigns Agent Rig a much broader identity than the tracked README/Northstar. |

### 3.2 Distributed packages and cross-cutting assets

| Component or claim | Classification | Repository reality and reconciliation |
|---|---|---|
| Spec Orchestration 07152026 | **Partial** | Full prompt bundle and installer exist; 19/21 observed installed files matched at freeze. No end-to-end execution test exists. Wright omits the actual unconditional `03-UI-SPEC.md` command step from his flow description. |
| Forge 07152026 | **Partial** | Full prompt bundle and installer exist and compared installed assets matched. The command derives missing INVARIANTS/CADENCE when source material exists, while Wright and Forge README say it simply refuses to proceed. |
| Notebook Orchestration 04182026 | **Partial** | Design/build/execute/QC assets exist, but Jupyter was absent locally and the package installs its own `frank.md` over the cross-cutting destination. |
| Lit Synthesis 04292026 | **Partial** | Three commands, roles, skills, templates, and matching installed assets exist. External PDF/tool dependencies and a real run were not verified. |
| Dated packages as portable versioned releases | **Present but different** | They are copy-based dated snapshots without tags, release manifests, compatibility contracts, uninstallation, or end-to-end release tests. “Versioned units” is descriptive naming, not a demonstrated release system. |
| Root `agents/frank.md` | **Partial** | Persona and verdict contract exist, but “binding” is prompt authority. Installed Frank differed from HEAD at freeze. The persona itself does not implement the universal cold/unbriefed/isolated-checkout rule Wright attributes to every sprint. |
| Notebook Frank and root Frank | **Duplicate** | Both own basename `frank.md` and install to `~/.claude/agents/frank.md`; neither matched the frozen installed copy. Install order can select behavior. |
| `/new-project` | **Partial** | A large procedural command exists and its frozen installed copy matched. It mutates GitHub, Git, files, LORE, and relay state and has no safe end-to-end test. |
| `/lore-close` | **Partial** | Repository command exists, but its installed copy differed at freeze. Repository source does not contain the externally claimed oracle/lesson Step 4.5. |
| `/relay` | **Partial** | A seven-line repo-local command names external messaging tools. External relay behavior and delivery were not verified. |
| Root templates and retrofit material | **Partial** | Templates exist and some are distributed through `/new-project` or package installers. There is no single deployment manifest, and not every named template is scaffolded into a new project. |
| Global `~/.claude` install surface | **Duplicate** | It is both runtime and a second mutable copy. Four unique destinations differed from HEAD at freeze; root cross-cutting assets lack a repository installer. |
| “Hub-and-spoke, fix once and redeploy everywhere” | **Partial** | The hub sources exist, but propagation is manual/copy-based, runtime drift is demonstrated, and consumer update state is manually narrated. The thesis is not yet proven by the mechanism. |

### 3.3 Mechanical hooks, probes, tests, and publication controls

| Component or claim | Classification | Repository reality and reconciliation |
|---|---|---|
| Session queue hook | **Partial** | Actively routed on SessionStart and reads one tagged LORE capture. It does not run the broader Git/database/service ground-truth probes implied by “pillar binding”; external DB compatibility was not tested. |
| Signpost checklist hook | **Implemented** | Actively routed on Stop and covered by passing tests. It verifies that a cited completed tool-call ID exists, not that the call semantically supports the claim. |
| No-preamble reminder/analyzer | **Partial** | UserPromptSubmit reminder and Stop analyzer are active, but `MODE = "log_only"`; flagged narration is allowed. User-level and project-level duplicate registration remains unresolved. |
| Progress-proof-per-slice hook | **Partial** | Actively routed only for `Edit`; `Write`, no-proof completion, and nonallowlisted manual-unverified proof can pass. Six of fifteen isolated wrapper cases failed. It also executes prefix-matched edit-authored commands with `shell=True`. |
| Domain-boundary provenance family | **Obsolete** | Code/tests/logs remain, but no route, required manifest, or global copy exists. DDR index and roster explicitly mark v1 and its extension sunset/to-be-reworked. Live-looking code is residue, not an active control. |
| Scrub gate | **Implemented** | Active local pre-commit and GitHub Actions routes exist and a frozen all-tracked scan passed. It remains fragile: it prints matched values and ignores Git subprocess failure status. |
| Shared hook telemetry | **Partial** | Three active probes write normalized ignored JSONL; aggregation exists. Domain uses a legacy excluded shape, logs are local-only, and best-effort writes can disappear. |
| Postgres telemetry sink | **Proposed only** | `write_telemetry_pg()` is a `pass` placeholder. |
| Reference session-start scaffold | **Present but different** | `/new-project` can copy it to other repos, but Agent Rig itself routes the LORE session queue instead. “Canonical pillar implementation” is a narrative/provenance claim, not an active local route. |
| Python probe tests | **Implemented** | Frozen run: 208 passed, one excluded. This verifies functions and selected wrappers, not prompt orchestrators or external integrations. |
| CI test enforcement | **Partial** | CI runs only the scrub scanner. The passing pytest/wrapper corpus is not a configured merge gate. |
| Dependency/reproducibility declaration | **Not found** | No tracked `pyproject`, requirements file, package manifest, or lockfile was found. Runtime tools and Python packages are host-global assumptions. |
| Repo-owned daemon, API, dashboard, TUI, MCP server, or supervisor | **Not found** | No implementation entry point or service definition exists. External LORE/Switchboard services are dependencies, not Agent Rig components. |
| Archives and gate snapshots | **Duplicate** | Archives are mostly labeled obsolete, but 119 archived files and committed snapshots duplicate live blobs and enlarge search/ownership surfaces. |
| Prunable worktrees and stale remote-tracking refs | **Obsolete** | Frozen Git metadata showed three prunable worktrees and three remote-tracking refs absent from the live remote. Intent to retain them is indeterminate. |

### 3.4 External dependencies and claims

| Component or claim | Classification | Repository reality and reconciliation |
|---|---|---|
| LORE Postgres/gateway | **Indeterminate** | Code and commands expect it; Phase 1 deliberately did not query it. Schema, availability, captures, and ownership are external. |
| Switchboard live behavior | **Indeterminate** | Commands and Wright describe it, but no implementation lives here and external message state was not inspected. |
| GitHub issues #19, #22–#28, #34, #35 | **Indeterminate** | Wright cites external issue state. Only some ideas are mirrored in the DDR index; issue existence/current status is not repository evidence. |
| Consumer deployments | **Indeterminate** | The roster narrates several repositories and commits, but those repositories were outside the frozen implementation inspection. |
| `check-spec-journaling.py` ownership/import | **Not found** | No script, test, installer, or source exists in Agent Rig. The frozen inventory found only a configured external user hook; Wright's proposed import is not built here. |
| `/oracle` command and lesson-capture Step 4.5 | **Indeterminate** | DDR-index prose says they shipped directly under `~/.claude`, while neither a tracked `/oracle` source nor the claimed lore-close step exists here. This is an author≠install-location gap, not a repository capability. |
| `research-spec-start` source ownership | **Not found** | The DDR backlog itself says it is installed-only and no tracked source of record was found. |

## 4. Idea and decision reconciliation

The proposed map supplies a target vocabulary and order of operations, not an implemented
architecture. The classifications below compare every map row to this repository. External
products and references are not assumed to exist merely because the map names them.

### 4.1 Proposed project-map components

| Map component or idea | Classification | Reconciliation with repository reality |
|---|---|---|
| Agent Rig | **Present but different** | The map calls it an internal production system; the tracked README/Northstar define a workshop that develops tooling for other repos. No durable operating layer or system-of-record service exists here. |
| Department OS | **Indeterminate** | The map calls it a separate public product. That boundary concerns an external product; no Department OS implementation or shared contract lives here. |
| Frame | **Present but different** | No component is named Frame. `/spec-start`, Intake, Interview, North Star, and spec artifacts partially perform framing as prompt contracts. |
| Forge | **Partial** | Full and lite Markdown workflows exist, but there is no executable controller or event instrumentation. |
| Frank | **Partial** | Persona and prompt gates exist; installed identity drifts, Notebook collides at the destination, and judgment records have no canonical schema. |
| Hooks and controls | **Partial** | Active hooks span observe, remind, execute, and block behaviors, but several fail open, one is log-only, one is bypassable, and the sunset hook remains in the live tree. |
| Durable local runtime / supervisor | **Not found** | No repo-owned daemon, service, durable scheduler, wake/sleep controller, or recovery supervisor exists. |
| Claude Code, Codex, custom agents | **Proposed only** | Claude-oriented assets exist, but no harness-neutral adapter or normalized event model exists. |
| Radio / Switchboard | **Indeterminate** | A tiny relay command and external integration claims exist. Radio naming, routing ownership, and live behavior are outside this repository. |
| Radio language and readable transcript | **Proposed only** | No message envelope, conversation state machine, acknowledgement protocol, or transcript UI exists. |
| Mission Control | **Not found** | No React control center or web application exists here. The private agent-dashboard comparison is external and unverified. |
| Local / hosted / hybrid control plane | **Proposed only** | No control plane implementation or deployment boundary exists to choose among these modes. |
| Event Rig / Event Core | **Proposed only** | No canonical event envelope, entity model, event store, correlation layer, query API, or replay engine exists. |
| OpenTelemetry / OTLP ingestion | **Not found** | No OTel SDK, collector config, OTLP adapter, or dependency manifest was found. Existing JSONL telemetry is custom and local. |
| PostHog-inspired adapter | **Proposed only** | Reference pattern only; no adapter or PostHog dependency exists. |
| Verification Plane CLI | **Not found** | No feature/architecture verification CLI exists. Individual probes and the scrub CLI are narrower controls. |
| Feature Maps | **Proposed only** | This reconciliation maps capabilities manually; no schema, generator, or maintained feature-to-evidence artifact exists. |
| SHA-bound Proof / Verdict Ledger | **Proposed only** | Gate prose and records mention commits, but there is no immutable schema/store binding evidence, reviewer, verdict, and SHA. |
| Context Packs | **Proposed only** | No package manifest or reproducible context-bundle mechanism exists. |
| Architecture Arena | **Proposed only** | No comparison runner, criteria schema, or experiment record exists. |
| Prototype Loop | **Proposed only** | Iterative sprint practice exists, but no Event Core lifecycle or implemented tracer-loop mechanism exists. |
| Gardener constraints | **Proposed only** | No coherence/pruning checks exist; duplicate assets and stale machinery demonstrate the open gap. |
| LORE | **Indeterminate** | Agent Rig contains a read-only queue client and commands that name external APIs. The memory service, schema, and current state are external. |
| LORE boundary | **Proposed only** | The map states a boundary, but no Event Core or operational database exists against which to implement or test it. |
| Git / worktrees / artifacts | **Implemented** | Git and artifact-oriented workflows are real primitives, although worktree lifecycle is prompt-driven and frozen metadata includes prunable registrations. |
| GitHub review loop | **Partial** | Commands describe branch/PR operations and GitHub is used, but no normalized review ingestion, authority model, or internal executable review service exists. |
| Attention / approval queue | **Not found** | Human prompts exist inside commands; no durable queue, priority, expiry, evidence package, or resume state exists. |
| Sleeping / wakeable runtime | **Indeterminate** | The map cites an external precedent/desired behavior. No Agent Rig runtime implements it. |
| Continuation, handoffs, coordinators | **Partial** | LORE queue, relay prose, resumable Markdown PROGRESS files, and agent dispatch instructions provide fragments, not durable bounded continuation. |
| Replay and audit | **Partial** | Git history, gate snapshots, transcripts, and local telemetry provide fragments. No causal replay over normalized events exists. |
| Normalized agent transcript/event corpus | **Partial** | Signpost and session probes parse parts of Claude transcripts, but no recursive normalized corpus builder or mining pipeline exists. |
| CLI / TUI / MCP / web clients | **Proposed only** | Markdown slash commands are the only in-repo CLI-like interface; no shared control API, TUI, MCP server, or web client exists. |
| YAML for static topology only | **Proposed only** | This is a target constraint for systems not yet present, not an implemented configuration boundary. |
| Fail-closed mutation allowlists | **Present but different** | The map calls this decided, while current lifecycle hooks generally fail open and progress proof's command allowlist uses weak prefix matching with `shell=True`. |
| HumanLayer | **Indeterminate** | External comparison reference; not vendored, depended on, or evaluated in the repository. |
| PStack | **Indeterminate** | External comparison reference; no package, adapter, or completed Reuse/Adapt/Rebuild/Skip analysis exists here. |
| A7T / Three-Body | **Indeterminate** | External future reference with no repository integration or evaluation. |
| Hybrid cloud / hosted Agent Rig | **Proposed only** | Explicitly late commercialization idea; no productization implementation exists. |

The map's five inventory deliverables are **Implemented** by the frozen Phase 1 report set. Its
remaining build order—target architecture, event/evidence spine, Radio/control API, Mission
Control, instrumentation, approvals, autonomy, replay, and hosting—is **Proposed only** except for
the partial primitives identified above.

### 4.2 Repository DDR decisions and proposals

| Idea | Classification | Reconciliation |
|---|---|---|
| DDR-001 Ask-vs-Act | **Partial** | Doctrine and prompt practice exist; no general mechanical decision gate enforces it. |
| DDR-002 Orchestration Gate-Bypass Prevention | **Partial** | The index itself says §3.5 shipped while §3.1–§3.4 require another sprint. Binding remains prompt-mediated. |
| DDR-003 Public Surface & Contribution Model | **Proposed only** | DRAFT; missing license and contribution/ownership machinery remain. |
| DDR-004 Session-Start Signpost→Pillar Binding | **Partial** | Session queue and signpost mechanisms exist, but queue injection is a signpost and tool-ID checking is not semantic verification. `SESSION-MAP` still describes the hook as proposed. |
| DDR-005 Context Ratio / Work Orders | **Partial** | Some practice and research docs exist, but the broader replacement of prose by mechanisms is ongoing. |
| DDR-006 Unsourced-Threshold/Domain Boundary | **Obsolete** | Explicitly sunset; disconnected implementation remains in the live tree. |
| DDR-007 No-Preamble/No-Meta-Narration | **Partial** | Reminder and analyzer exist; current enforcement is advisory/log-only. |
| DDR-008 Progress Proof Per Slice | **Present but different** | DDR file says DRAFT/not yet spec'd, while an active but bypassable implementation and completed tooling records exist. Decision record and reality disagree. |
| DDR-009 Anti-Sycophancy | **Proposed only** | DRAFT; no position-reversal hook found. |
| DDR-010 Gate Assertion Coverage | **Proposed only** | DRAFT; no generic assertion-coverage checker found. |
| DDR-011 Plain-Language/No-AI-Slop | **Proposed only** | Index row only; no DDR file or implementation found. |
| DDR-012 Unasked Judgment/Rigor Theater | **Proposed only** | DRAFT decision record; no pre-dispatch gate found. |
| DDR-013 Frank transfer | **Not found** | Referenced as an agent-dashboard decision; no Agent Rig DDR-013 file exists. Frank itself is present. |
| DDR-014 new-project transfer | **Not found** | Referenced as an agent-dashboard decision; no Agent Rig DDR-014 file exists. `/new-project` itself is present. |
| DDR-015 Hook/Probe Deployment Pipeline | **Partial** | The reference-mirror retirement happened; the actual global-vs-copy-vs-plugin deployment mechanism remains undecided and unbuilt. No DDR-015 file exists. |

### 4.3 Named backlog and governance-audit ideas

| Idea | Classification | Reconciliation |
|---|---|---|
| Benchmark as standing pre-QC gate | **Proposed only** | No command flow structurally invokes it as a universal stage. |
| Market-data Slice 10 check-in | **Indeterminate** | External message/LORE state, not an Agent Rig build. |
| Frank's-Lessons cross-project store | **Present but different** | Tracked runbook/index refer to external lesson capture and oracle use, but no repository-owned oracle or matching lore-close source exists. |
| Portable `/frank` command | **Proposed only** | No `commands/frank.md` exists. |
| Decision Discipline backfill | **Indeterminate** | Intended edits are in eight external ignored `CLAUDE.md` files. |
| No-hedge gate | **Duplicate** | Explicitly absorbed into DDR-005; keeping it as a separate backlog narrative is historical duplication. No mechanical gate exists. |
| Three-check session-start template promotion | **Implemented** | Marked resolved and present in template/session doctrine, although the local active SessionStart hook performs the narrower queue function. |
| Adopt ownership of `research-spec-start` | **Proposed only** | Target source is absent from this repository. |
| Add a license | **Proposed only** | No `LICENSE` exists. |
| Adopt `ponytail` | **Proposed only** | Evaluation/security review is described; no vendored or installed repository asset exists. |
| Structural deferral/scope gate | **Proposed only** | Forge contains instructions, but no gate at the adjudication boundary was found. |
| Gap-lens pre-checks at doer/dispatcher | **Partial** | Some doctrine/templates exist; the four proposed structural controls are not implemented as a complete mechanism. |
| Governance-document audit | **Proposed only** | The backlog defines a recurring audit procedure. This Phase 2 report performs one analysis pass but does not implement that recurring mechanism. |
| Cold-review cadence / Cold-Frank dispatch checker | **Proposed only** | No transcript-before-dispatch hook or full-read coverage checker exists. |
| Independent verification of Frank facts | **Proposed only** | A doctrine idea, not a repository control. |
| “Speed kills” full-section dispatch check | **Proposed only** | No dispatch analyzer was found. |
| Precise self-report / over-confession check | **Proposed only** | Semantic doctrine only. |
| Verbatim verdict pass-through | **Partial** | Some command/persona prose requires exact verdict handling, but no general downstream-dispatch enforcement exists. |
| Frank self-refusal of warmed briefs | **Proposed only** | `agents/frank.md` contains no cold/warm/isolated-dispatch refusal logic. |
| Administrative FAIL-churn analyzer | **Proposed only** | Recorded diagnosis; no detector or procedure exists. |
| Fix-agent verbatim pass-through | **Duplicate** | Same responsibility as the general verdict pass-through idea, restated one hop downstream. |
| Benchmark self-refusal | **Proposed only** | No repository-owned benchmark persona or refusal rule found. |
| Whole-section sweep requirement | **Proposed only** | No mechanical check found. |
| `/decision-matrix` skill/command | **Proposed only** | No registered command or skill exists. |
| Graph-enforced procedure | **Proposed only** | A design slogan/architecture direction, not an implemented graph. |
| Homelab Oracle forced read/write nodes | **Present but different** | External installed-only behavior is claimed, but forced integration into a decision graph is explicitly absent and no source lives here. |
| Domain-boundary relevance/wiring audit | **Obsolete** | Its conclusion is now captured by the sunset decision and frozen inventory; the inactive machinery remains. |
| Reactor-as-gatekeeper lesson | **Proposed only** | Catalogued for future integration into spec/decision flows; no standalone control intended. |
| Stale `senior-qc` external reference | **Obsolete** | The senior-qc skill is archived; the cited live command is external and no Agent Rig fix is present. |
| Cold-Frank shadow-discipline issue #34 | **Proposed only** | The proposed transcript correlation mechanism is absent. |
| Import `check-spec-journaling.py` issue #35 | **Proposed only** | The import, source ownership, and tests are absent. |
| First-turn/signpost hardening issues #19/#22–#28 | **Indeterminate** | Current signpost implementation exists, but external issue scope/status was not independently available. |

## 5. Wright claims the repository does not support

These are not accusations of bad faith. Wright explicitly labels the declaration a narrative
signpost. They are places where that signpost outruns repository proof.

| Wright claim | Finding |
|---|---|
| Numbered DDR files 001 through 012 are present | False. DDR-011 is absent; 013–015 are also absent as local files. |
| Frank is “active” and “dispatched routinely” | Persona and command references are present; routine dispatch frequency was not demonstrated by repository evidence. |
| Every Frank gate is cold, unbriefed, and isolated | The universal rule is not in `agents/frank.md` or all command dispatches. `docs/ISSUE-RUNBOOK.md` applies Cold Gates specifically to enforcement-mechanism issues. No mechanical checker exists. |
| Frank has no override because the orchestrator enforces it | The command prose says so, but the repository contains no executable orchestration controller preventing direct invocation, skipped stages, or manual continuation. |
| `/forge-start` refuses to proceed whenever INVARIANTS/CADENCE are missing | Current command instead derives them from source material, seeks confirmation, and HALTs only if derivation is impossible or unconfirmed. README and local CLAUDE remain stale. |
| Wright's spec flow description is complete | It omits the command's unconditional Step 5 `03-UI-SPEC.md` path and lite-mode variants. |
| Dated packages are centrally versioned and redeployed | They are dated copy bundles. There is no release/install manifest or update pipeline, and installed drift is demonstrated. |
| Root Frank is the global source of record in practice | Documentation assigns that role, but Notebook owns the same destination and the installed file matched neither source at freeze. |
| SessionStart builds a pillar from primary sources | Active Agent Rig SessionStart retrieves a tagged LORE capture and labels it unverified. It does not run the full ground-truth probe family described in older doctrine. |
| No-preamble is enforced mechanically | Current mode is advisory `log_only`. |
| Proof-per-slice refuses unsupported completion | It can be bypassed by `Write`, no `PROOF:`, or manual-unverified proof. |
| Hook layer is the most rigorously tested and therefore operational | It is the most tested area, but progress wrapper portability fails, several hooks fail open, and CI does not run the tests. |
| Domain-boundary design authority was withdrawn | This is supported by the index/roster, but the code is not archived; repository shape alone still presents it as live machinery. |
| Ten Cold-Frank violations, unread Switchboard messages, issue states, and a LORE gateway defect | These may be true external incidents, but the repository does not prove them. They remain **Indeterminate** here. |
| `/oracle` and lore-close lesson capture shipped | Only index/runbook narration supports this; repository-owned command sources do not. |
| `check-spec-journaling.py` is live globally | Frozen runtime configuration observed an external hook, but no Agent Rig-owned source or tests exist. Ownership and behavior remain external. |
| All relevant agents run on one host | A narrative deployment assumption, not a repository-enforced constraint. |

## 6. Existing capabilities Wright or the declaration omitted or understated

- The scrub gate has two real active enforcement paths: local pre-commit and GitHub Actions.
- `/spec-start --lite` and `/forge-start --lite` provide a separate bounded-tooling flow.
- The spec flow includes an unconditional command-level UI-spec stage, delegated judgment about
  whether a no-UI artifact is appropriate, and snapshot-before-retry behavior.
- The active UserPromptSubmit no-preamble reminder is distinct from the Stop analyzer.
- The signpost checklist correlates transcript tool-use/tool-result IDs and has a substantial test
  suite, although it does not establish semantic relevance.
- Progress proof can execute proof commands, which is both a capability and a high-risk authority
  surface because its prefix check feeds `shell=True`.
- The scrub gate can scan staged or all tracked content, but its error paths can disclose matches
  or fail open.
- Shared hook telemetry, aggregation, ignored local logs, and a placeholder Postgres sink form a
  distinct observability subsystem.
- `docs/ISSUE-RUNBOOK.md`, tooling specs, sprint artifacts, committed gate snapshots, and research
  findings are substantial operational/process surfaces omitted from Wright's component account.
- The repository has real code-level tests, but no CI job runs them.
- Git metadata contains obsolete worktrees/refs, and the repository has a large duplicate archive
  surface.
- No dependency manifest or license exists; both materially limit reproduction/reuse.

## 7. Proposed capabilities not built

The important unbuilt set is larger than Wright's four-item priority list:

- the map's durable local runtime/supervisor and shared control API;
- Event Core semantic envelopes, stable entity/causality IDs, persistence, query, and replay;
- OTel/OTLP ingestion and harness-neutral Claude Code/Codex/custom-agent adapters;
- Mission Control, Radio UX, and a durable attention/approval queue;
- Feature Maps, Verification Plane CLI, SHA-bound Proof/Verdict Ledger, Context Packs,
  Architecture Arena, Prototype Loop, and Gardener checks;
- normalized recursive transcript corpus generation;
- fail-closed mutation authorization—the current hook posture is substantially fail-open; and
- GitHub review ingestion, sleeping/wakeable runtime, durable continuation, and hosted/hybrid
  control-plane options;
- authoritative source-to-runtime deployment, provenance, drift detection, or uninstall;
- a resolution to the root-Frank/notebook-Frank destination collision;
- Cold-Frank dispatch-shape, isolated-checkout, and fresh-full-read enforcement;
- a repository-owned `/oracle`, `/frank`, `/decision-matrix`, or `research-spec-start` source;
- `check-spec-journaling.py` source and tests;
- anti-sycophancy, plain-language, assertion-coverage, rigor-theater, deferral/scope, whole-section
  sweep, and general verdict-pass-through controls;
- mandatory proof on every supported PROGRESS completion path;
- Postgres telemetry persistence and unified domain telemetry;
- CI execution of the existing Python and wrapper tests;
- end-to-end tests for Spec, Forge, Notebook, Lit Synthesis, `/new-project`, and `/lore-close`;
- a dependency/compatibility manifest and a declared license;
- any standalone Agent Rig application, service, dashboard, TUI, MCP server, or supervisor.

## 8. Naming and responsibility conflicts

1. **Frank vs. Frank:** root and Notebook personas share the same runtime filename. “Cross-cutting
   source of record” and “package-contained agent” cannot both own that destination.
2. **Source vs. runtime:** repository README claims source-of-record authority while mutable
   `~/.claude` copies determine behavior and can drift without a manifest.
3. **Session probe vs. session queue:** `reference/session_probe.py` is a bootstrap ground-truth
   scaffold; `scripts/session_queue_probe.py` is the active local LORE signpost reader. Their
   adjacent names invite false equivalence.
4. **Domain-boundary vs. unsourced-threshold provenance:** a renamed, broadened/narrowed,
   explicitly sunset family retains the old filenames and live-tree location.
5. **DDR ownership/numbering:** Agent Rig prose refers to DDR-013/014 held in agent-dashboard and
   a DDR-015 with only an index row. Local numbering therefore does not denote local artifacts.
6. **Ground truth:** CLAUDE/CADENCE call `PROGRESS.md` ground truth, while project doctrine says
   narrative records must be checked against primary sources. A status ledger is not the work.
7. **Forge governance:** README/CLAUDE say missing files HALT; command/CADENCE say derive them when
   evidence permits. There is no declared precedence rule resolving the conflict.
8. **Telemetry:** normalized shared logs coexist with the legacy domain log, while a database sink
   name suggests persistence that is not implemented.
9. **Cross-cutting command inventory:** `commands/README.md` lists only `/new-project`, although
   tracked `lore-close.md` is also resident.
10. **Map authority:** `SESSION-MAP.md` remains unratified and stale, while the build-ideas map
    calls itself a working canonical index reconstructed from chats. Neither is as-built evidence.
11. **Agent Rig identity:** tracked README/Northstar say workshop; the proposed map says internal
    production system and operating layer. That is a target change, not a naming synonym.
12. **Frame vs. Spec:** the map reconceptualizes existing spec-start behavior without a component,
    migration, or boundary saying whether Frame replaces, wraps, or merely labels it.
13. **Event Rig vs. Event Core, Radio vs. Switchboard, agent-dashboard vs. Mission Control:** the
    map itself leaves these responsibility/name pairs unresolved.
14. **Judgment vs. enforcement:** the map correctly separates them, while current Frank gates are
    enacted through the same prompt orchestrators that perform workflow control.

## 9. Obsolete and duplicate machinery

- Archived Spec 03132026/03242026 and Forge 03132026/03252026 packages are obsolete; many blobs
  are byte-identical to other active/archive copies.
- `archive/first-turn-contract-enforcement/` is superseded by signpost-checklist-redesign.
- `archive/obsolete/senior-qc-skill/` and Lobster materials are explicitly obsolete.
- The domain-boundary hook is sunset but still occupies active `.claude/hooks`, `scripts`, tests,
  specs, documentation, and ignored-log naming surfaces.
- The root and Notebook Frank definitions are a live destination duplicate.
- User-level and project-level registrations may duplicate no-preamble/signpost execution; runtime
  merge semantics were not established.
- DDR row 004 appears twice in the index. The no-hedge and verbatim-pass-through ideas also appear
  in absorbed or repeated forms.
- Package source, root source, installed copies, consumer-vendored copies, archived copies, and
  gate snapshots create several uncontrolled copy planes.
- Three prunable worktrees and three stale remote refs are obsolete metadata candidates, not active
  components.

## 10. Journaling, ledgering, commentary, and meta-narration loops

The repository contains two reinforcing loops.

### 10.1 Work-to-record-to-context loop

```text
work
  -> PROGRESS / GATE-LOG / snapshots
  -> proof hook and telemetry JSONL
  -> LORE close/status/lesson capture
  -> next SessionStart queue injection
  -> Signpost/Pillar response rows
  -> signpost/no-preamble telemetry
  -> more status and close records
```

Each element has a legitimate local purpose, but together they make the system spend substantial
machinery recording, validating, re-injecting, and commenting on its own process narration. The
loop is especially weak where the validator checks only record shape: a tool ID exists, a checkbox
changed, a proof string has an allowed prefix, a gate verdict was written, or a capture carries a
tag. None of those facts establishes that the underlying claim is true.

### 10.2 Incident-to-governance-to-more-governance loop

```text
incident or missed rule
  -> LORE / issue / DDR-index entry
  -> Intake + Interview + 5 spec docs
  -> Frank verdict + snapshots + PROGRESS/GATE-LOG
  -> lessons-learned / oracle proposal
  -> new hook proposal
  -> hook telemetry + governance audit proposal
```

This loop is visible in the 105-line DDR index's long backlog entry, the domain-provenance sprint,
the governance-audit cluster, and the proposed journaling import. It risks treating additional
records and checkers as completion while source/runtime authority, destination collisions, CI,
and dependency reproduction remain unresolved.

The no-preamble subsystem is the clearest meta-narration example: a prompt reminder tells the
agent not to narrate its process; a Stop analyzer evaluates that narration; wrappers and probes
record the evaluation; an aggregator summarizes the record; a future database sink is proposed.
Current mode does not block the narration.

## 11. Process records treated as canonical evidence

| Record | Canonical treatment found | Why that treatment is unsafe |
|---|---|---|
| `PROGRESS.md` | Called “ground truth for sprint state” | It is manually authored Markdown; completion can bypass the partial proof hook. Live files/tests are the primary evidence. |
| Hook Deployment Roster | Named as the place deployment state “lives” | It is manually updated, spans external repos, and already exists because other records became stale. It remains a signpost until each target is checked. |
| DDR index | Intended as decision-only but used for current rollout, installed-only claims, issue state, incident narration, and a large audit backlog | It contradicts its own DDR definition and invites stale statements to be replayed as fact. |
| `SESSION-MAP.md` | Says update the map first, then the artifact; calls itself a pillar/canonical once ratified | It is unratified and stale. Updating a map before the source reverses the repository's own evidence doctrine. |
| Gate PASS / Frank verdict | Used in index prose to establish shipped/accepted state | A verdict is judgment over supplied evidence, not proof of merge, deployment, runtime identity, or continued operation. |
| Telemetry JSONL | Used to demonstrate hook operation | Local ignored rows demonstrate invocations, not clone-reproducible behavior, semantic correctness, or current user/project hook merge rules. |
| LORE queue/captures | Used by Wright for next-work, issue, incident, and deployment claims | The active probe explicitly labels the queue unverified. LORE was not queried in the frozen phase. |
| Git commit/PR references in prose | Used to imply active deployment | A commit proves history. It does not prove the active installed copy, target branch, consumer state, or runtime caller. |
| Author's Declaration | Uses session experience and recall to label components active | Wright correctly caveats it as a signpost. It must not be upgraded beyond that caveat. |
| Build Ideas Index and Map | Labels a chat reconstruction “working canonical” and assigns current dispositions such as Core/Existing/Decided | It is an architecture proposal. Repository implementation, external-system inspection, and explicit boundary decisions must independently substantiate each row. |

## 12. Smallest defensible next tracer bullet

The map's proposed “first tracer bullet” is not one bullet: it combines Frame, Forge,
artifact/commit capture, Frank, human decision, Event Core, Feature Maps, an immutable ledger,
Mission Control, and Radio. That is a multi-subsystem program with no existing runtime spine and
would allow each new component to self-certify the others. The smallest repository-grounded proof
must precede it.

**Resolve one end-to-end authority path: Frank only.** Do not begin the broad DDR-015 deployment
pipeline, import another hook, or add another ledger first.

The tracer bullet should:

1. designate `agents/frank.md` as the only Agent Rig source allowed to own
   `~/.claude/agents/frank.md`;
2. remove or rename Notebook's ownership of that destination without changing Frank's substantive
   persona in the same slice;
3. add one repository-owned, noninteractive install/verify path for root Frank that records source
   path and content hash and refuses ambiguous multiple ownership;
4. add a temporary-`HOME` integration test proving clean install, idempotent reinstall, drift
   detection, and no Notebook overwrite; and
5. leave the real user-level installation untouched until that test passes and a human explicitly
   chooses deployment.

This is smaller and more defensible than “build the deployment pipeline.” It resolves the highest
confidence responsibility collision, tests the source→installer→destination chain without relying
on a process ledger, and produces evidence that can decide whether the same pattern should expand
to commands, hooks, skills, and templates. If this one-asset path cannot be made deterministic,
the broader hub-and-spoke/source-of-record architecture is not yet a buildable premise.

The two high-risk existing controls—progress proof's `shell=True` prefix handling and scrub gate's
secret-print/fail-open behavior—should be handled as separate safety fixes, not folded into this
tracer bullet or used to enlarge it.

## 13. Final disposition

Phase 2 supports the frozen inventory's central conclusion and sharpens it: Agent Rig has useful
mechanical parts, but its project story currently assigns more authority to prompts, ledgers,
installed copies, retrospective records, and now an aspirational “canonical” system map than
repository reality can guarantee. Wright's proposed priority of solving distribution is
directionally correct, but “DDR-015 first” is too broad. The map's event/evidence-first direction
is also defensible as a later architecture choice, but its stated tracer bullet is far too broad
for the current baseline. The first proof should be one deterministic, collision-free asset path.

Reconciliation against Wright and every row in `Agent_Rig_Build_Ideas_Index_and_Map.md` is
complete for repository-verifiable claims. External products, services, installed-only assets,
and comparison references remain explicitly **Indeterminate** rather than being inferred from
chat reconstruction or process records.
