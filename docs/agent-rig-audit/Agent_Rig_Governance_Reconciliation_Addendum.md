# Agent Rig Governance Reconciliation Addendum

**Date:** 2026-09-18
**Scope:** Analysis only; no doctrine adoption or implementation
**Proposal evaluated:** `AGENT-RIG-AI-BUILD-GOVERNANCE-AND-TRACER-BULLET-DOCTRINE.md`
**Evidence baseline:** Frozen cold inventory at `cc9dcb3310f3415b9b6658d3cb8f90014a9bbe55`,
Wright's Author's Declaration, the Build Ideas Index and Map, and the completed Agent Rig
Reconciliation

## 1. Executive judgment

The Signal Current doctrine is directionally sound where it addresses contamination, bounded
work, frozen judgment targets, deterministic feedback, and human accountability. It is not an
as-built description and is not adopted by this addendum.

Agent Rig already contains fragments of most of the doctrine: DDR/status routing rules,
Signpost/Pillar language, map-not-route reviewer briefing, prompt-level role separation, gate
snapshots, PROGRESS/GATE records, tests, human approval, and a special Cold Frank procedure for
enforcement-mechanism issues. Those fragments are inconsistent, duplicated, and mostly
instruction-layer controls. The doctrine should therefore not be copied into more prompts or
expanded into a new ledger, manifest family, hook cluster, or full workflow.

The critical conflict is between the doctrine's “temporary reasoning is ephemeral by default”
rule and Agent Rig's current direction to capture every decision, deviation, and HALT immediately
to LORE. A second conflict is between Canonical Artifact Purity and current commands that append
verdict summaries, attempt histories, snapshots, and orchestrator findings into `PROGRESS.md` and
sometimes use that process record as “ground truth.” The corrective is sharper routing, not more
recording.

Before Tracer Bullet 1, adopt only the rules needed to keep one bounded build and judgment clean.
Do not build Event Core, a Proof/Verdict Ledger, a context-pack system, an artifact classifier, a
semantic anti-narration hook, or a new governance workflow first.

## 2. Decision meanings

| Decision | Meaning |
|---|---|
| **KEEP** | Existing Agent Rig rule is sufficient for the pilot; preserve it without a new surface. |
| **ADD** | A missing rule is justified by observed evidence and is needed in one smallest authoritative surface. |
| **MODIFY** | A useful rule exists or is proposed, but its current or proposed form conflicts, overreaches, duplicates, or needs narrower scope. |
| **DEFER** | Direction is plausible but not required before Tracer Bullet 1 or lacks evidence for implementation. |
| **REJECT** | Do not adopt the rule or its proposed implementation because it adds ceremony, duplicates machinery, or is disproportional. |

Timing means **Before TB1**, **Later**, or **Never**. “Before” does not authorize a code or prompt
change; it identifies a condition the eventual pilot must satisfy.

## 3. Evidence constraints

- The frozen inventory proves Agent Rig is a prompt/tooling workshop with a small hook/probe layer,
  not a durable runtime, event system, or executable orchestration state machine.
- “Binding” spec/forge gates are Markdown contracts interpreted by an external runtime.
- Progress proof is bypassable and unsafe in one authority path; signpost verification establishes
  tool-call existence, not semantic support; no-preamble is log-only; most wrappers fail open.
- Runtime copies drift from repository sources, and root Frank collides with Notebook Frank.
- `PROGRESS.md`, the DDR index, the Hook Deployment Roster, gate logs, snapshots, telemetry, LORE,
  and the project maps are process/evidence aids, not interchangeable sources of current truth.
- The Build Ideas map's Event Core, Mission Control, Radio, Verification Plane, Feature Maps,
  Proof/Verdict Ledger, attention queue, replay engine, and supervisor are proposed only or absent.
- Wright's account is a useful signpost and explicitly not a verified inventory.

## 4. Rule-by-rule reconciliation

### G01 — Cold inventory → reconciliation → adoption → pilot sequencing

**Decision:** KEEP  
**Timing:** Before TB1

- **Current evidence:** Phase 1 was frozen before the declaration, map, and doctrine were
  reconciled; Phase 2 produced a separate report.
- **Existing governing surface:** Cold Inventory Audit Charter and the completed reconciliation.
- **Gap, conflict, or duplication:** None for this audit. Repeating the four-phase sequence for
  every ordinary change would be ceremony.
- **Smallest justified change:** Treat the sequence as an audit/adoption method only, not the
  default software-delivery lifecycle.
- **Verification:** Git history shows the frozen inventory predates reconciliation and this
  addendum; no protected input changed.
- **Anti-ceremony:** Close the audit sequence after the pilot decision. Do not create a permanent
  “reconciliation phase” for each ticket.

### G02 — One authoritative home; do not replicate doctrine

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** Governance is repeated across ignored `CLAUDE.md`, README, INVARIANTS,
  CADENCE, SESSION-MAP, DDR index, commands, templates, issue runbook, and installed copies; drift
  is demonstrated.
- **Existing governing surface:** DDR-DEFINITION partially enforces single-purpose records; no
  general governance-placement rule is reliably authoritative.
- **Gap, conflict, or duplication:** Copying this doctrine into prompts and specs would reproduce
  the exact source/runtime and narration problem under review.
- **Smallest justified change:** When implementation is authorized, place the pilot rules once in
  the pilot's bounded work contract; after the pilot, choose one durable governance home only if
  experience justifies standardization.
- **Verification:** One search finds one adopted rule source and references elsewhere, not copied
  prose; installed-copy parity is separately verified if deployment occurs.
- **Anti-ceremony:** References replace restatement. No new doctrine index, adoption ledger, or
  per-rule progress file.

### G03 — Canonical Artifact Purity

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** The DDR index contains status narration despite DDR-DEFINITION; sprint
  artifacts carry gate histories and corrective narratives; the reconciliation identified a
  work→record→context loop.
- **Existing governing surface:** DDR-DEFINITION protects DDRs narrowly; Northstar is intended to
  remain thesis-only; no cross-artifact purity rule exists.
- **Gap, conflict, or duplication:** The doctrine is correct, but a broad prose-pattern hook would
  overlap no-preamble/check-spec-journaling machinery and would confuse semantic judgment with
  string detection.
- **Smallest justified change:** For TB1, state one routing invariant: source, test, and governed
  design artifacts contain current truth only; review history stays outside them.
- **Verification:** Diff review of the judged commit finds no reviewer names, attempt numbers,
  verdict history, or “changed to pass” explanations in canonical artifacts; legitimate migration
  constraints remain stated as current constraints.
- **Anti-ceremony:** Verify the diff directly. Do not require a purity checklist, purity ledger, or
  new permanent metadata block in each file.

### G04 — Separate events, state, evidence, judgment, memory, handoffs, specifications, and history

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** Agent Rig has Git history, PROGRESS state, gate verdicts, snapshots,
  telemetry JSONL, LORE queue/captures, handoff prose, and specifications, but it sometimes calls
  PROGRESS “ground truth” and replays narrative records as evidence.
- **Existing governing surface:** DDR-DEFINITION routing table, CLAUDE/CADENCE, SESSION-MAP
  Signpost/Pillar model, command-specific progress/gate sections.
- **Gap, conflict, or duplication:** The doctrine's conceptual taxonomy is useful; implementing a
  store or schema for every noun before TB1 would recreate the project map's horizontal build.
- **Smallest justified change:** Use a six-line routing note in the TB1 work contract: Git records
  change; task status records state; test output records mechanical evidence; a verdict records
  judgment; specs/source record current intent/behavior; temporary reasoning is not persisted.
- **Verification:** Every TB1 output is attributable to one of those surfaces and no surface is
  cited for a claim it cannot establish.
- **Anti-ceremony:** No Event Core, universal log, new database, or cross-surface replication.

### G05 — Progress is state, not canonical evidence

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** `PROGRESS.md` is called ground truth, yet its hook can be bypassed by
  `Write`, proof-less completion, or manual-unverified proof; commands also transcribe verdicts
  and attempt summaries into it.
- **Existing governing surface:** CLAUDE, CADENCE, spec-start, forge-start, progress-proof hook.
- **Gap, conflict, or duplication:** State, judgment history, and proof claims are co-located and
  then treated as authoritative.
- **Smallest justified change:** TB1 must not use a new PROGRESS file. The bounded ticket is the
  intended state; Git diff and test output are evidence; the final verdict is judgment.
- **Verification:** Completion can be re-derived from the frozen commit and deterministic command
  without reading a progress narrative.
- **Anti-ceremony:** Remove a tracker from the pilot rather than adding validation to it.

### G06 — Temporary reasoning is ephemeral; reusable memory is curated

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** INVARIANTS/CLAUDE require every decision, deviation, and HALT to be captured
  immediately to LORE; lore-close, session queue, proposed Oracle, and lesson capture can feed
  records back into later context.
- **Existing governing surface:** INVARIANTS rule 6, CLAUDE Capture Behaviour, lore-close/session
  queue, DDR-index lesson/oracle proposals.
- **Gap, conflict, or duplication:** Automatic capture conflicts with the doctrine's ephemeral
  default and creates recursive narration. LORE records are explicitly signposts, not proof.
- **Smallest justified change:** For TB1, capture no session diary. Preserve only the work contract,
  commit, deterministic output, and verdict. Curate a reusable lesson only after the human finds a
  durable cross-project principle.
- **Verification:** No new LORE/status/lesson entry is required to reproduce or judge TB1; any later
  lesson cites the primary artifacts and omits session narrative.
- **Anti-ceremony:** Default is no capture. An explicit human curation decision is the exception.

### G07 — Prevent artifact contamination

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** Process and gate narration appear throughout spec/progress packages; the
  doctrine's failure pattern matches the reconciliation's incident→governance loop.
- **Existing governing surface:** Narrow DDR rules and ordinary code-review norms only.
- **Gap, conflict, or duplication:** Artifact contamination is not a distinct enforced concept.
- **Smallest justified change:** Add no new artifact; require the implementer to keep review and
  correction history out of TB1 source/tests and let Git hold change history.
- **Verification:** Cold diff inspection against the parent commit.
- **Anti-ceremony:** This is a negative constraint checked from existing artifacts, not a log of
  compliance.

### G08 — Prevent reviewer contamination; use map-not-path briefs

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** INVARIANTS rule 7 names map-not-route, ISSUE-RUNBOOK requires repo+SHA+
  parent SHA+verdict for Cold enforcement reviews, but ordinary command dispatches provide
  PROGRESS paths, artifact lists, and prior-attempt state.
- **Existing governing surface:** INVARIANTS, ISSUE-RUNBOOK, DDR backlog, spec/forge commands.
- **Gap, conflict, or duplication:** The rule is present but uneven and not in Frank's persona;
  “allowed scope” can itself become a path hint if over-specified.
- **Smallest justified change:** TB1's Cold Frank brief contains repository, exact target, governing
  contract, permitted tools, and verdict format—no change summary, file list, prior verdict, Codex
  conclusion, or confidence statement.
- **Verification:** Preserve and inspect the dispatch input itself; Frank's findings must be
  independently located in the frozen target.
- **Anti-ceremony:** One minimal dispatch is the evidence. Do not add a reviewer-contamination
  checklist or transcript ledger.

### G09 — Fresh corrective contexts after failed semantic gates

**Decision:** MODIFY  
**Timing:** Before TB1, contingent on failure

- **Current evidence:** Current commands snapshot then re-delegate, but do not prove a fresh
  context; the DDR backlog documents warmed-review and corrective-churn failures.
- **Existing governing surface:** Spec/forge retry loops, gate snapshots, governance-audit backlog.
- **Gap, conflict, or duplication:** “End context after every failure” is excessive for a formatter
  or unit-test failure; keeping the same context after a binding semantic FAIL preserves repair
  anchoring.
- **Smallest justified change:** Require a new implementer context only after Codex/Cold Frank
  semantic FAIL or HALT. Mechanical red/green iteration stays in the active build context.
- **Verification:** The corrective dispatch starts after the frozen verdict and contains the
  contract plus defect claim, not the prior conversation or repair attempts.
- **Anti-ceremony:** No context-reset log. The new dispatch boundary is directly observable.

### G10 — Cold Frank is independent judgment, not implementation assistance

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** Frank persona and binding gates exist; true Cold rules apply explicitly to
  enforcement-mechanism issues only; root/Notebook/installed Frank definitions conflict.
- **Existing governing surface:** `agents/frank.md`, INVARIANTS, ISSUE-RUNBOOK, spec/forge commands.
- **Gap, conflict, or duplication:** Universal Cold behavior is claimed more broadly than it is
  implemented. Expanding Frank before resolving which Frank is authoritative would deepen drift.
- **Smallest justified change:** Use the existing root Frank source as the proposed TB1 authority
  target, but run the pilot's final judgment from an isolated checkout at an exact SHA with the
  minimal G08 brief. Do not edit the persona as part of the same pilot.
- **Verification:** Checkout identity, brief, and verdict can be inspected independently; verdict
  cites evidence found in the target.
- **Anti-ceremony:** One cold judgment, no per-slice Frank gates and no new `/frank` command first.

### G11 — Reviewer reports defects and invariants, not mechanical repair recipes

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** Frank's format includes specific Fix/Next-step items routed to an agent;
  the DDR backlog also demands verbatim pass-through, which can turn verdicts into patch recipes.
- **Existing governing surface:** `agents/frank.md`, spec/forge retry procedures, DDR backlog.
- **Gap, conflict, or duplication:** A total ban on actionable guidance would reduce usefulness;
  line-edit instructions encourage keyword patching and contaminate corrective context.
- **Smallest justified change:** Findings identify observable defect, governing criterion, affected
  behavior, and required outcome; they do not prescribe exact edits or an inspection route.
- **Verification:** A verdict is actionable without containing replacement text, line-by-line
  instructions, or claims that uninspected code is the repair location.
- **Anti-ceremony:** Improve the content of the existing verdict; add no separate remediation doc.

### G12 — Freeze every judgment target

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** Enforcement ISSUE-RUNBOOK uses final commit SHA and isolated worktree;
  spec/forge commands use mutable artifacts plus snapshots; no universal target identity exists.
- **Existing governing surface:** ISSUE-RUNBOOK, Git commits, gate snapshots, some command prompts.
- **Gap, conflict, or duplication:** Verdicts can otherwise appear to follow later mutations;
  snapshot directories duplicate Git and are not a uniform identity scheme.
- **Smallest justified change:** TB1 judgment target is one commit SHA plus parent SHA. Dirty trees
  are not judged. Test evidence records the same SHA.
- **Verification:** Reviewer runs `git rev-parse HEAD`; the verdict states that SHA; later changes
  require a new verdict.
- **Anti-ceremony:** Use Git identity already present. Do not build a Proof/Verdict Ledger first.

### G13 — Preserve Wright, implementer, Codex, Cold Frank, tool, and human boundaries

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** Composer/Producer/Frank roles and delegated agents exist as prompt
  contracts; Codex performed a genuinely cold inventory; no runtime prevents role collapse.
- **Existing governing surface:** CLAUDE role table, INVARIANTS rules 1/3/4/7, spec/forge agent
  definitions, audit charter.
- **Gap, conflict, or duplication:** Wright is both producer/orchestrator in prose; separate names
  do not create separate information contexts; Codex findings can contaminate Frank if forwarded.
- **Smallest justified change:** For TB1: human approves contract and final acceptance; Wright
  orchestrates but does not author the implementation; one implementer sees the contract and
  bounded surface; deterministic tools report mechanics; Codex audits the frozen commit without
  author narrative; Cold Frank independently judges the same commit without Codex/Wright findings.
- **Verification:** Tool/dispatch records show distinct invocations and inputs; no role's private
  narrative is copied into another's brief.
- **Anti-ceremony:** Information boundaries are enforced by what is omitted from existing briefs,
  not by creating role journals.

### G14 — One bounded work contract, one outcome, one stop condition

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** Intake/spec/forge and ISSUE-RUNBOOK provide scope machinery, but can require
  Issue→Intake→Interview→five spec docs→progress→gate snapshots for small changes.
- **Existing governing surface:** ISSUE-RUNBOOK, `/spec-start --lite`, `/forge-start --lite`,
  CADENCE, DDR-001/005.
- **Gap, conflict, or duplication:** “One ticket, one context” is useful but should not force a new
  document set; mandatory Intake/Interview can itself become process theater for the pilot.
- **Smallest justified change:** Use one existing issue or approved task as the entire TB1 contract
  with seven fields: observable result, scope, governing invariant, judgment surface,
  deterministic check, evidence to preserve, and stop condition.
- **Verification:** The commit and test satisfy every field without implementing adjacent work.
- **Anti-ceremony:** No separate Intake, Interview, roadmap, PROGRESS, or new gate ledger for TB1.

### G15 — Build the smallest vertical tracer; resist horizontal subsystems

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** The Build Ideas map proposes a “tracer bullet” spanning Frame, Forge,
  Event Core, ledger, Mission Control, and Radio; the reconciliation found this is a program, not
  a bullet.
- **Existing governing surface:** Northstar YAGNI language, lite modes, reconciliation's Frank-only
  tracer recommendation.
- **Gap, conflict, or duplication:** No adopted sizing rule prevents the map's horizontal build.
- **Smallest justified change:** TB1 proves only one deterministic root-Frank source→install→verify
  path in a temporary HOME and eliminates/avoids Notebook overwrite. No Event Core, UI, Radio,
  LORE, telemetry database, or generalized deploy pipeline.
- **Verification:** One integration test proves clean install, idempotence, drift detection, and no
  destination collision at the frozen commit.
- **Anti-ceremony:** The tracer removes ambiguity and duplication; it adds no new process system.

### G16 — A materially different second tracer bullet

**Decision:** DEFER  
**Timing:** Later

- **Current evidence:** No first tracer has been authorized or executed under reconciled doctrine.
- **Existing governing surface:** None beyond the proposal.
- **Gap, conflict, or duplication:** Selecting TB2 now would turn future planning into current
  scope and bias TB1 toward premature generalization.
- **Smallest justified change:** After TB1, choose TB2 only if it tests reuse of the same minimal
  authority path with a materially different asset or failure mode.
- **Verification:** TB2 reuses a demonstrated seam and exposes one real generalization gap.
- **Anti-ceremony:** No TB2 backlog package before TB1 evidence exists.

### G17 — Progressive disclosure and minimal handoffs

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** DDR-005 diagnoses context dominated by conduct rules; current prompts and
  governance files are large; handoffs and LORE can replay extensive history.
- **Existing governing surface:** DDR-005/work-order practice, map-not-route templates, role prompts.
- **Gap, conflict, or duplication:** Progressive disclosure is not a reliable runtime mechanism;
  merely creating a “context pack” would add another copy plane.
- **Smallest justified change:** TB1 implementer receives the seven-field work contract and only
  source/install/test files needed for the seam, with references to governing sources rather than
  copied excerpts.
- **Verification:** Inspect the dispatch: sufficient files and criteria are present; prior audit,
  roadmap, failed attempts, and future architecture are absent.
- **Anti-ceremony:** The handoff is smaller, not a persisted Context Pack artifact.

### G18 — Full bounded judgment-surface rehydration

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** Backlog and lessons document narrow line fixes, grep-driven corrections,
  shared-well validation, and failures to read complete relevant sections.
- **Existing governing surface:** Frank pre-checks, ISSUE-RUNBOOK root-cause requirement, scattered
  backlog doctrine.
- **Gap, conflict, or duplication:** “Read everything” conflicts with progressive disclosure;
  “read named lines” misses dependencies.
- **Smallest justified change:** Define TB1's complete surface in the work contract: root Frank,
  Notebook Frank/install path, relevant installers, destination convention, and new integration
  test. Implementer and auditors read that complete bounded surface.
- **Verification:** Findings and changes account for every owner/caller of the destination, not only
  the initially named file.
- **Anti-ceremony:** The judgment surface is a field in the work contract, not a separate manifest.

### G19 — Search navigates; it does not establish coherence

**Decision:** KEEP  
**Timing:** Before TB1

- **Current evidence:** Agent Rig's own lessons already identify keyword patching and require direct
  reads; Frank requires opening artifacts and sources, not trusting summaries.
- **Existing governing surface:** Frank persona, governance-audit backlog, ISSUE-RUNBOOK root-cause
  step.
- **Gap, conflict, or duplication:** No new rule is needed for TB1; compliance is behavioral and
  cannot be proven by counting Read calls alone.
- **Smallest justified change:** Apply the existing principle: use `rg` to enumerate the Frank
  destination/owners, then read each relevant file end to end.
- **Verification:** Audit reasoning covers semantics and call paths that use different names, not
  just matching tokens.
- **Anti-ceremony:** No “files read” ledger, timestamp, or transcript-coverage hook.

### G20 — Corrective-loop protocol

**Decision:** MODIFY  
**Timing:** Before TB1, contingent on failure

- **Current evidence:** Spec/forge already snapshot, log, retry, and classify convergence; this
  produces substantial gate history and snapshot duplication without proving fresh context.
- **Existing governing surface:** Spec/forge retry loops, PROGRESS gate history, `.gate-snapshots`,
  Frank verdict format.
- **Gap, conflict, or duplication:** Adopting the doctrine's twelve steps as another logged workflow
  would duplicate existing ceremony. Absolute verbatim verdict pass-through conflicts with fresh
  independent reproduction when the verdict contains repair instructions.
- **Smallest justified change:** On semantic FAIL: retain target SHA and verdict outside source;
  open a fresh implementer context with contract plus defect claim; rehydrate/reproduce; make one
  coherent correction; run the same deterministic check; commit a new SHA; re-run cold judgment.
- **Verification:** Two immutable SHAs, one prior verdict, red-on-old/green-on-new evidence, and a
  new uncontaminated reviewer brief.
- **Anti-ceremony:** Git and the existing verdict suffice. No attempt diary or copied snapshot tree.

### G21 — Deterministic feedback before autonomy or semantic judgment

**Decision:** MODIFY  
**Timing:** Before TB1

- **Current evidence:** 208 Python cases passed at freeze, but CI omits them; progress proof is
  bypassable and runs weakly allowlisted shell; orchestration workflows lack end-to-end tests.
- **Existing governing surface:** Tests, package commands, progress-proof hook, scrub CI, Forge
  test-runner role.
- **Gap, conflict, or duplication:** “A check ran” is not evidence it tests the failure mode; adding
  more hook telemetry would not improve coverage.
- **Smallest justified change:** TB1 defines one integration test that fails before the authority
  collision fix and passes after, using temporary HOME and no real runtime mutation.
- **Verification:** Independent runner demonstrates red-on-parent and green-on-target; command and
  SHA are recorded with the verdict.
- **Anti-ceremony:** One executable test replaces prose proof and avoids PROGRESS proof commands.

### G22 — Prototype uncertainty; discard experiments

**Decision:** DEFER  
**Timing:** Later

- **Current evidence:** The repository retains obsolete hooks, archived packages, snapshots, and a
  sunset domain-provenance experiment, showing weak retirement discipline.
- **Existing governing surface:** Archive directories and ad hoc sunset records.
- **Gap, conflict, or duplication:** The principle is sound, but TB1's Frank path does not require an
  unresolved architecture experiment.
- **Smallest justified change:** When a real uncertainty blocks a later slice, define one question,
  disposable location, decision owner, and deletion/archive condition before experimenting.
- **Verification:** Experiment answers the question; production adoption is a separate diff; unused
  scaffolding is removed or explicitly archived.
- **Anti-ceremony:** No permanent “prototype loop” framework or experiment ledger.

### G23 — Author explanation is optional evidence; label observed, inferred, and judged claims

**Decision:** ADD  
**Timing:** Before TB1

- **Current evidence:** The declaration is properly caveated, but Wright/LORE/gate statements have
  been promoted into active-state claims; signpost tooling checks IDs, not semantic support.
- **Existing governing surface:** Audit charter evidence hierarchy, Signpost/Pillar doctrine,
  Frank's distinction between consistency and truth.
- **Gap, conflict, or duplication:** A UI/schema for epistemic labels does not exist and is not
  needed for the pilot.
- **Smallest justified change:** TB1 decision presentation separates observed test/Git facts,
  auditor inference, Frank judgment, and human decision in plain headings.
- **Verification:** Every acceptance claim can be traced to a command/artifact or is explicitly
  labeled inference/judgment.
- **Anti-ceremony:** Labels appear once in the final decision presentation, not in every source file
  or event.

### G24 — Automatically enforce every proposed control

**Decision:** DEFER  
**Timing:** Later

- **Current evidence:** Existing hooks are narrow, fail-open/log-only/partial, duplicated across
  scopes, and one sunset implementation remains live-looking; an external journaling hook lacks
  repository ownership.
- **Existing governing surface:** Hook cluster, governance-audit backlog, check-spec-journaling
  proposal.
- **Gap, conflict, or duplication:** Artifact classifiers, anti-narration scanning, context-reset
  checks, dispatch analyzers, and judgment-surface validators would create another horizontal
  governance build before a pilot establishes the smallest failure surface.
- **Smallest justified change:** Use direct audit for TB1. After the pilot, mechanize only a
  repeatedly observed, structurally checkable violation with a safe authority model.
- **Verification:** A later control must have a real failing corpus, red/green regression test,
  explicit caller, and demonstrated non-duplication.
- **Anti-ceremony:** No telemetry or ledger merely to prove the control ran; measure the violation
  it prevents.

### G25 — Wholesale frameworks, universal workflow engines, longer prompts, and full-history context

**Decision:** REJECT  
**Timing:** Never as an automatic adoption

- **Current evidence:** Agent Rig already has large prompt bundles, duplicated installed sources,
  governance bloat, archives, and a proposed broad control plane; operational guarantees remain
  partial.
- **Existing governing surface:** Northstar/YAGNI, DDR-005 context-ratio diagnosis, the doctrine's
  own “do not automatically adopt” list.
- **Gap, conflict, or duplication:** Importing PStack/Matt Pocock skills wholesale, adding Ralph,
  renaming roles, building a universal engine, or loading all history would compound existing
  drift and process theater.
- **Smallest justified change:** Borrow only a principle that closes an evidenced Agent Rig gap and
  prove it in a bounded slice.
- **Verification:** TB1 adds no external framework, global role rename, generalized task graph, or
  always-on context corpus.
- **Anti-ceremony:** Rejection prevents a new framework whose main output would be more governance
  artifacts.

### G26 — Human judgment and accountability remain final

**Decision:** KEEP  
**Timing:** Before TB1

- **Current evidence:** Composer role, personal review of identity/North Star artifacts, human spec
  approval, manual-push-only policy, and escalation chain all reserve human authority.
- **Existing governing surface:** CLAUDE role table, INVARIANTS rules 4/5, CADENCE human approval,
  spec/forge commands.
- **Gap, conflict, or duplication:** Prompt language can falsely imply a Frank PASS or agent
  consensus is correctness; no executable controller guarantees human review.
- **Smallest justified change:** For TB1, the human approves the contract, reviews the raw diff,
  sees deterministic evidence plus independent judgments, and explicitly accepts or rejects. A
  PASS permits a decision; it does not make the decision.
- **Verification:** Human approval is explicit and tied to the judged SHA; no push/merge is inferred
  from agent agreement.
- **Anti-ceremony:** One final accountable decision, not approval at every internal step.

## 5. Duplicate or process-theater risks in the proposal

| Proposed control or interpretation | Existing overlap | Disposition |
|---|---|---|
| Semantic Canonical Artifact Purity hook before the pilot | no-preamble analyzer, external `check-spec-journaling.py`, domain-provenance precedent | **DEFER**; direct diff review first. |
| New Proof/Verdict Ledger | PROGRESS gate history, GATE-LOG, snapshots, Git, telemetry, LORE | **REJECT before TB1**; use SHA + verdict + test output. Reconsider only after a real query/replay need. |
| Judgment-surface manifest as a separate artifact | Intake, architecture, roadmap, command ARTIFACTS lists, context-pack proposal | **REJECT for TB1**; one field in the bounded contract. |
| Automatic lesson capture after failures | immediate LORE capture rule, lore-close, Oracle/Frank's-Lessons proposals | **REJECT by default**; human-curated durable lesson only. |
| Fresh-context compliance ledger | transcripts, telemetry, dispatch logs, proposed Cold-Frank checker | **REJECT**; the distinct dispatch is observable evidence. |
| Full twelve-step corrective log | existing retry/snapshot/convergence procedures | **REJECT**; perform the essential sequence without journaling it. |
| Full map tracer (Event Core + ledger + Mission Control + Radio) | proposed project-map program | **REJECT as TB1 sizing**; it is multiple horizontal systems. |
| Read-call coverage as proof of rehydration | proposed issue #34 transcript correlation; signpost tool-ID limitation | **REJECT as semantic proof**; tool-call existence does not prove understanding. |
| Per-slice or per-document Frank gates | existing major-phase gates and process burden | **REJECT**; one final independent judgment for TB1. |
| Copying this doctrine into CLAUDE/INVARIANTS/CADENCE/prompts | existing governance drift | **REJECT**; one pilot contract, then one authoritative home if earned. |

## 6. Minimum governance required before Tracer Bullet 1

Only these six combined rules are required:

1. **Pure truth surfaces:** source, tests, and governed design state current truth; no review or
   repair diary. Git holds change history.
2. **Explicit routing:** the work contract is intent/state, test output is mechanical evidence,
   Codex output is audit/inference, Frank output is judgment, and the human records the decision.
3. **Independent information boundaries:** implementer receives bounded work; Codex receives the
   frozen target and contract without author narrative; Cold Frank receives target and criteria
   without Wright/Codex findings or repair history.
4. **Frozen target:** one clean commit SHA and parent SHA; tests and judgments bind to that SHA.
5. **Bounded completeness:** progressive disclosure plus full rehydration of the declared Frank
   ownership/install/test seam; one stop condition and one deterministic red/green integration
   check.
6. **Human accountability:** human approves the contract and decides on the raw diff, evidence,
   and independent judgments. Agent agreement is not proof.

If a semantic gate fails, one contingent seventh rule applies: start a fresh corrective context
with the contract and defect claim, reproduce independently, correct coherently, and create a new
SHA. Do not carry the prior session or repair narrative forward.

These rules should live in the TB1 work contract for the pilot. They should not yet be propagated
to global prompts or converted into hooks.

## 7. Rules that should wait

- A second materially different tracer.
- Event Core schemas, OTel adapters, replay, Mission Control, Radio, or an attention queue.
- Feature Maps, Context Packs, Architecture Arena, Prototype Loop framework, or Gardener checks.
- A durable Proof/Verdict store or cross-client control API.
- Automatic artifact classification or semantic contamination scanning.
- Context-reset, dispatch-shape, or full-read coverage hooks.
- General CI/deployment expansion beyond the deterministic TB1 test.
- Reconciled global governance placement and consumer-repository propagation.
- Curated cross-project lessons/oracle integration.
- Autonomy, continuation, coordinators, sleeping runtime, or hosted deployment.

Waiting does not reject the architectural direction. It prevents proposed infrastructure from
certifying itself before one clean path exists.

## 8. Rules and implementations that should be rejected

- Treating PROGRESS, LORE, gate logs, telemetry, the Author's Declaration, or either project map
  as canonical evidence of current implementation.
- Automatic capture of every decision, deviation, HALT, failed attempt, or reviewer finding.
- Embedding verdicts, repair histories, attempt counts, or reviewer dialogue in canonical source,
  tests, or specifications.
- A separate ledger or manifest for every information category.
- An absolute fresh-context reset for ordinary deterministic failures.
- An absolute ban on actionable reviewer outcomes; prohibit patch recipes, not clear acceptance
  conditions.
- A universal semantic hook that claims to decide whether prose is valid governance or evidence.
- Read/tool-call counts as proof that an agent understood the judgment surface.
- The map's compound Frame→Forge→Event Core→ledger→Mission Control→Radio package as TB1.
- Wholesale framework/skill imports, universal workflow engines, role renaming, permanent bots,
  full-history prompts, or additional prose as a substitute for enforcement.

## 9. Smallest governance pilot

Use the completed reconciliation's existing smallest tracer: **one deterministic Frank authority
path**, not the project map's compound product slice.

### Observable result

In a temporary HOME, `agents/frank.md` is the sole Agent Rig source for
`~/.claude/agents/frank.md`; Notebook installation cannot silently replace it; clean install,
idempotent reinstall, deliberate drift detection, and collision prevention are executable.

### Information boundaries

- **Human:** approves the seven-field work contract and final judged SHA; reviews the raw diff.
- **Wright/orchestrator:** routes the contract and tools; does not implement, audit, or coach Frank.
- **Implementer:** receives only the contract and full bounded install/ownership/test surface; no
  audit narrative, prior verdict, Event Core roadmap, or repair history.
- **Deterministic runner:** proves red on the parent and green on the target in temporary HOME.
- **Codex:** audits target SHA against contract and test independently; reports observed facts and
  labeled inferences, not a repair recipe.
- **Cold Frank:** receives repo, target SHA, parent SHA, contract/criteria, allowed tools, and
  verdict format only; no Wright summary, Codex findings, file list, or prior verdict.
- **Human:** decides. Codex/Frank agreement informs but does not replace accountability.

### Records retained

- One approved work contract or issue.
- Parent and target commit SHAs.
- One reproducible test command and its red/green output.
- Codex audit result.
- Frank verdict tied to target SHA.
- Human decision.

No new PROGRESS file, gate snapshot tree, LORE diary, lesson capture, event schema, proof ledger,
context pack, or dashboard is required.

### Pilot success test

Another clean reader can reproduce the installation test and determine what was intended, what
changed, what evidence passed, what Codex inferred, what Frank judged, and what the human decided
without reading any session transcript or process narrative.

## 10. Immediate next action

**Human confirms the Frank authority-path pilot and approves one seven-field work contract.**

That contract should name only:

1. observable result;
2. in/out scope;
3. governing ownership invariant;
4. complete bounded judgment surface;
5. deterministic red/green integration test;
6. evidence to preserve; and
7. stop condition.

Do not first amend CLAUDE, INVARIANTS, CADENCE, Frank, spec/forge prompts, DDRs, ledgers, or hooks.
Do not start Event Core, Mission Control, Radio, or a deployment pipeline. The pilot contract is
the temporary authoritative governance surface; standardization is a later human decision earned
by pilot evidence.

## 11. Final recommendation

Adopt the doctrine's contamination model and bounded-build principles, but not its potential
governance machinery. The strongest pre-TB1 controls are omissions and identities: omit repair
narrative, omit irrelevant history, omit cross-role conclusions, bind judgment to one SHA, run one
real test, and leave the final decision with the human.

Agent Rig's current problem is not a lack of places to record process. It is that too many process
records compete with source, evidence, and each other. The governance pilot succeeds if it proves
clean separation with fewer artifacts than the current workflow—not if it produces a more
complete account of itself.
