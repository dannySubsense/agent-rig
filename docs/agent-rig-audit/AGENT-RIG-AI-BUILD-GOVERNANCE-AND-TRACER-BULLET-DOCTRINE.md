# Agent Rig AI Build Governance and Tracer-Bullet Doctrine

## Handoff for Agent Rig Reconciliation and Future Execution

**Date:** 2026-09-18  
**Project:** Agent Rig  
**Document type:** Proposed execution doctrine and reconciliation input  
**Status:** Non-canonical until reconciled against the frozen cold inventory and explicitly adopted  

---

## 1. Purpose

This document ports a set of governance and AI-assisted software-development lessons into Agent Rig. The lessons emerged while working on Signal Current, but the underlying failure modes are cross-project and appear especially relevant to Agent Rig because Agent Rig itself coordinates agents, context, judgments, evidence, hooks, handoffs, and execution.

This is not a target-architecture specification. It does not establish what Agent Rig currently contains, and it must not be used to bias the independent inventory already commissioned.

Its purpose is to answer a later question:

> Once we know what Agent Rig actually is, how should agents be allowed to plan, build, review, correct, and record work without creating circular process theater or contaminating the artifacts under judgment?

The doctrine combines:

- Matt Pocock's tracer-bullet and vertical-slice discipline;
- bounded, fresh implementation contexts;
- rapid deterministic feedback loops;
- progressive disclosure of instructions;
- disposable prototypes for uncertainty;
- canonical artifact purity;
- information-boundary discipline among orchestrators, implementers, auditors, and Cold Frank;
- full judgment-surface rehydration before correction;
- separation of system truth, process state, judgment history, and session narrative.

---

## 2. Mandatory sequencing with the Agent Rig cold inventory

Agent Rig already has a separate **Cold Inventory Audit Charter**. That charter must run first.

### Phase 1 — Cold inventory

Codex independently inspects the local Agent Rig repository and its observable operating context. Codex determines what exists from repository and runtime evidence without receiving the author's build-idea index, LORE interpretation, intended architecture, or this proposed doctrine as an expected-component checklist.

The cold inventory must be frozen before this document is introduced.

### Phase 2 — Reconciliation

Only after the cold report is frozen should Agent Rig reconcile:

1. observed as-built reality;
2. the author's declared intent;
3. the Agent Rig build-idea index;
4. relevant LORE claims;
5. this proposed build-governance doctrine.

Use:

**KEEP / ADD / MODIFY / DEFER / REJECT**

for every proposed governance rule.

### Phase 3 — Adoption

Place adopted controls in the smallest appropriate Agent Rig governance surface. Do not duplicate the doctrine throughout specifications, prompts, skills, code comments, and gate logs.

### Phase 4 — Pilot

Exercise the doctrine through one real tracer bullet before generalizing it into a large workflow framework, skill collection, or autonomous control plane.

> **Inventory reality first. Reconcile doctrine second. Pilot third. Standardize only after experience.**

---

## 3. The primary failure pattern

In repeated AI-assisted spec and forge loops, an orchestrator or implementer can begin using governed artifacts as:

- a journal;
- a progress tracker;
- a gate ledger;
- a record of reviewer findings;
- an explanation of why each correction was made;
- a defense of why the latest version should pass;
- a running narrative of failed attempts.

The next reviewer then encounters that narrative as part of the artifact under judgment. New discrepancies appear between the repair narrative and the actual requirements or code. The implementer patches those discrepancies, often using grep and reviewer keywords, and inserts more explanatory narration. The process becomes self-referential:

**finding**  
→ **narrated repair embedded in artifact**  
→ **reviewer judges repair narrative**  
→ **new narrative contradictions**  
→ **keyword patching**  
→ **more embedded narration**

Agent Rig must prevent this failure both in projects it coordinates and in its own development.

---

## 4. Canonical Artifact Purity

The foundational rule is:

> **A governed artifact contains the current truth, not the history of how the truth was reached.**

A specification states current requirements and invariants.  
Code implements current behavior.  
Tests state current expected behavior.  
An ADR records enduring architectural rationale.  
A gate record stores judgments.  
Git and pull requests record changes.

Canonical specifications, code, tests, and ordinary code comments must not become a diary of the agent's work.

### Prohibited process narration in governed artifacts

- “Frank found…”
- “Fixed after review attempt 7…”
- “Codex requested…”
- “Previously this said…”
- “This resolves finding F-3…”
- “Changed so the gate will pass…”
- histories of successive corrective attempts;
- defensive explanations of why the artifact is now correct;
- temporary progress state;
- copied reviewer dialogue.

### Narrow exception

Historical context may remain only when it is itself necessary product or operational truth—for example, a migration constraint or backward-compatibility contract. Even then, state the current constraint cleanly. Do not preserve the review conversation that revealed it.

### Agent Rig implication

Agent Rig should be able to identify the type of each output surface and enforce or warn when information is routed incorrectly. It should not encourage every agent to write everything it knows into the repository.

---

## 5. Separate the information surfaces

| Information | Correct surface |
|---|---|
| Current product requirement | Canonical specification |
| Current executable behavior | Code |
| Current expected behavior | Test or executable assertion |
| Enduring architecture rationale | ADR / DDR |
| Current task or sprint state | Progress/task system |
| Agent events and runtime activity | Event/telemetry plane |
| Gate verdict and attempt history | Judgment/gate record |
| Reviewer findings | Review artifact |
| Why a code change was made | Commit or pull request |
| Temporary session reasoning | Ephemeral by default |
| Minimum continuation context | Temporary handoff |
| Reusable operational learning | Curated lesson or skill after validation |
| As-built reality | Evidence-based inventory/audit artifact |

The compact rule is:

> **Git records change. Events record activity. Progress records state. Gates record judgment. Specs record truth. Code records behavior. Do not mix them.**

This routing rule should inform Agent Rig's event model, hooks, judgment system, handoffs, memory architecture, and UI. It does not mean all surfaces must be implemented immediately.

---

## 6. Three forms of contamination

### 6.1 Artifact contamination

Process narration, prior verdicts, and corrective history leak into the artifact under judgment.

**Control:** Canonical Artifact Purity and surface routing.

### 6.2 Reviewer contamination

The reviewer receives the implementer's explanation of what changed, where to look, why it should pass, or what a previous reviewer concluded.

**Control:** Cold review, artifact isolation, and map-not-path briefs.

### 6.3 Context contamination

The implementing agent carries failed attempts, discarded plans, reviewer reasoning, defensive explanations, and local patch assumptions through repeated correction loops.

**Control:** fresh contexts, bounded handoffs, and full judgment-surface rehydration.

Agent Rig should treat these as distinct risks. A clean prompt cannot rescue a contaminated artifact. A clean artifact cannot create an independent review when the reviewer receives an answer key. A fresh context cannot help when the handoff reproduces the entire failed session.

---

## 7. Cold Frank and independent judgment

Cold Frank is an independent forge gate, not an implementation assistant.

Frank receives:

- the frozen artifact or repository state;
- the governing requirements or evaluation contract;
- the allowed scope;
- required output format.

Frank does not receive:

- the implementer's summary of changes;
- the implementer's confidence statement;
- selected reasons the work should pass;
- prior verdicts;
- prior repair attempts;
- hints about which files or lines were changed;
- a reviewer conclusion from Codex presented as truth;
- test results curated into a persuasive narrative.

The controlling invariant is:

> **Nothing in the judgment prompt or judgment surface may describe prior findings or the corrective path taken to satisfy them.**

Cold Frank independently discovers what matters.

### Map, not path

A gate brief may define repository boundary, evaluation questions, evidence standard, permitted actions, and required outputs. It must not prescribe the inspection route or reveal the intended conclusion.

### Defect, not repair recipe

Frank's output should identify observable defects, contradictions, omissions, failed criteria, or insufficient evidence. It should not become a line-edit recipe that the implementer can mechanically apply without understanding the governing invariant.

### Freeze the judgment target

Every gate must identify the exact target being judged: commit SHA, artifact version, working-tree fingerprint, build artifact, configuration state, or equivalent reproducible identity. A verdict cannot silently follow later mutations.

---

## 8. Role and information boundaries

Agent Rig should preserve genuine separation among roles. Different names or prompts do not create independence if all roles share the same narrated history.

### Human composer/owner

- sets intent and risk tolerance;
- approves material decisions;
- remains accountable for accepted work;
- does not receive a false implication that agent consensus equals correctness.

### Orchestrator

- establishes the bounded task and required evidence;
- routes work to the correct role or deterministic tool;
- enforces context and artifact boundaries;
- does not perform every delegated task itself;
- does not coach the independent gate toward a desired verdict;
- does not write progress narration into canonical artifacts.

### Implementer

- rehydrates the relevant judgment surface;
- implements one approved bounded slice;
- runs required deterministic feedback;
- stops at the ticket boundary;
- does not self-certify or author the gate's interpretation.

### Codex independent auditor

- inventories, traces, diffs, and tests independently;
- distinguishes evidence from inference;
- can perform preflight or semantic audit when explicitly scoped;
- does not silently become the implementer;
- freezes findings before receiving author narrative when running cold.

### Cold Frank

- evaluates the frozen target independently;
- receives no repair narrative;
- issues a verdict grounded in observable evidence and governing criteria.

### Deterministic tools and hooks

- supply mechanical feedback such as tests, types, formatting, schema validation, policy checks, provenance, and artifact assertions;
- do not pretend to make semantic judgments they cannot support.

---

## 9. Matt Pocock's tracer-bullet discipline

The specification describes the destination. A tracer bullet proves one narrow route through the system.

> **Build one smallest useful behavior end to end before constructing complete horizontal subsystems.**

An Agent Rig tracer bullet must cross all layers genuinely required for one real outcome, while implementing the minimum of each.

Illustrative Agent Rig tracer bullet:

**human issues one bounded task**  
→ **orchestrator creates one work contract**  
→ **one implementer receives scoped context**  
→ **one deterministic check produces evidence**  
→ **one event trail is recorded**  
→ **one independent judgment evaluates the frozen result**  
→ **human sees the result and decides**  
→ **system returns to an idle or completed state**

This is illustrative, not a declaration that the as-built Agent Rig contains or should immediately contain every named element.

### Horizontal work to resist

Do not first build a complete:

- event bus;
- memory framework;
- agent registry;
- permissions platform;
- observability stack;
- hosted control plane;
- dashboard;
- judgment engine;
- skills marketplace;
- generalized task graph;
- universal orchestration abstraction.

Build only enough of each required mechanism to prove the current end-to-end outcome.

### One ticket, one context, one independently verifiable result

Each build context should own one bounded outcome. A ticket must specify:

- desired observable result;
- in-scope and out-of-scope boundaries;
- governing requirements and invariants;
- judgment surface;
- deterministic acceptance checks;
- evidence to preserve;
- stop condition;
- review and gate boundary.

“Continue building Agent Rig” is not an acceptable implementation ticket.

### Second tracer bullet

The first tracer bullet proves integration but may hide special-casing. The second should differ materially in task type, tool path, lifecycle, failure/recovery behavior, or agent role while using the same spine.

---

## 10. Context-window-sized work and progressive disclosure

Large project context encourages agents to reopen settled architecture, expand scope, and implement adjacent systems. Agent Rig should favor progressive disclosure.

An implementer receives:

1. small universal project rules;
2. the current bounded work contract;
3. the governing requirement sections;
4. the interfaces and code needed to model the changed seam;
5. required acceptance checks.

The implementer should not automatically receive every roadmap, historical discussion, prior failed attempt, future idea, and review transcript.

This is not permission for shallow understanding. The task context must contain the complete **judgment surface**, but not the entire project history.

> **Minimize irrelevant context; fully understand relevant context.**

Agent Rig handoffs should reference settled canonical sources instead of copying them. A handoff carries only active state that is not already represented elsewhere.

---

## 11. Full judgment-surface rehydration

Before implementing or correcting work, the agent must build a coherent model of the bounded surface under judgment.

At minimum, inspect:

- every changed file;
- governing specification sections;
- relevant interfaces and data contracts;
- relevant tests and fixtures;
- callers and consumers across the changed seam;
- applicable permissions, hooks, and invariants;
- persistence, events, and recovery semantics affected by the change;
- any artifact whose meaning depends on the changed behavior.

For a small spec package, this may mean reading the complete package. For a large repository, it means defining and reading the complete bounded dependency surface.

Search is useful only after understanding:

> **Search proves occurrence, not coherence.**

Grep can locate every use of a term. It cannot prove that lifecycle, cardinality, authority, timing, failure, and recovery semantics agree across differently named representations.

---

## 12. Corrective-loop protocol

When a gate fails:

1. Preserve the gate finding outside governed artifacts.
2. Freeze the failed target identity and verdict.
3. End the original implementation context.
4. Start a fresh corrective context.
5. Rehydrate the complete bounded judgment surface.
6. Independently reproduce the defect.
7. Determine the governing invariant, not merely the mentioned keyword.
8. Identify all affected representations and consumers.
9. Make the smallest coherent correction.
10. Run the required deterministic feedback.
11. Commit or freeze the new target without embedding gate narration.
12. Submit it to a new Cold Frank with no explanation of the repair path.

The working rhythm is:

> **Understand → Build → Verify → Stop.**

For correction:

> **Fresh context → Rehydrate → Reproduce → Correct → Verify → Stop.**

The orchestrator must not feed Frank the list of changes or feed the implementer a reviewer-authored patch recipe.

---

## 13. Feedback loops before autonomy

Agent autonomy should expand only after fast, reliable feedback exists.

Depending on the slice, feedback may include:

- type checking;
- unit, integration, and end-to-end tests;
- formatting and linting;
- schema and contract validation;
- permissions and policy checks;
- provenance and evidence assertions;
- event-ordering and state-transition invariants;
- idempotency and retry tests;
- recovery and resume tests;
- frozen-artifact identity checks;
- reproducible build/run commands;
- browser-visible acceptance behavior.

Feedback should run during implementation, not only after the agent has accumulated many untested assumptions.

Hooks belong primarily to enforcement and feedback. Their emitted facts may feed the event and judgment planes, but a hook should not be mislabeled as a semantic judgment merely because it blocks work.

---

## 14. Prototype uncertainty; do not architect around guesses

When a design question cannot be settled through existing evidence, build the smallest disposable experiment that can answer it.

Examples:

- Can one event envelope represent both interactive agent chat and background work without losing ordering semantics?
- Can a sleeping runtime resume one interrupted work contract safely?
- Can a cold reviewer receive enough governing context without receiving the repair narrative?

The prototype exists to produce a decision. It is not automatically production code.

Record the resulting enduring decision in the appropriate place. Discard or isolate experimental scaffolding.

> **Prototype uncertainty. Do not construct a generalized subsystem to avoid confronting it.**

---

## 15. Memory, events, judgments, and handoffs are not interchangeable

Agent Rig risks collapsing several different forms of information into one universal log or memory store.

They must remain conceptually separate:

- **Events:** what happened.
- **State:** what is true now for an active workflow.
- **Evidence:** what supports a factual claim.
- **Judgment:** an evaluator's conclusion under stated criteria.
- **Memory:** curated information worth retrieving later.
- **Handoff:** minimum transient context needed to continue.
- **Specification:** current intended system truth.
- **History:** how artifacts and decisions changed over time.

The same underlying event may be referenced from multiple surfaces, but its meaning must not be silently changed. A stream of agent narration is not automatically institutional memory. A judgment is not a system fact merely because an agent wrote it. A handoff is not a canonical specification.

---

## 16. Governance that Agent Rig may eventually enforce

Do not implement all of these before the pilot. During reconciliation, determine which are current, near-term, deferred, or rejected.

Potential controls include:

- classify repository artifacts by surface type;
- prohibit known gate-narration patterns in canonical specs;
- require frozen target identity for judgment requests;
- separate implementer context from reviewer context;
- prevent prior verdicts from entering Cold Frank briefs;
- require explicit work-contract scope and stop conditions;
- require judgment-surface manifests for correction tasks;
- enforce new-context boundaries after failed gates;
- record gate history outside canonical artifacts;
- validate that required deterministic checks ran against the judged target;
- make author explanation optional evidence, never hidden fact;
- show the human which claims are observed, inferred, or judged;
- preserve rejected and failed approaches only when curated into reusable lessons.

Agent Rig must not become a bureaucracy generator. Every control must address an observed failure mode and justify its cost.

---

## 17. What Agent Rig should not adopt automatically

Do not automatically:

- install Matt Pocock's entire skills collection;
- adopt Ralph or another autonomous loop;
- replace the existing orchestrator/worker model;
- rename current roles to match another person's framework;
- create a permanent bot for every responsibility;
- build a universal workflow engine before one path works;
- replicate this doctrine across many files;
- treat longer prompts as stronger governance;
- give every agent the full repository and project history;
- confuse more telemetry with better judgment;
- treat agreement among agents as proof;
- let the orchestrator perform implementation, audit, and gate roles in one shared context;
- sanitize existing artifacts before the cold inventory captures reality;
- implement governance controls before reconciliation establishes where they belong.

Borrow principles. Add tooling only where repeated Agent Rig experience proves it useful.

---

## 18. Reconciliation assignment

After the Agent Rig cold inventory is frozen, reconcile this doctrine against as-built reality.

For each proposal, record:

| Field | Required answer |
|---|---|
| Decision | KEEP / ADD / MODIFY / DEFER / REJECT |
| Current evidence | What the frozen inventory proves exists |
| Current governing surface | Where the rule or behavior presently lives |
| Gap or conflict | Exact mismatch, duplication, or absence |
| Smallest justified change | Minimum intervention |
| Pilot relevance | Required before Tracer Bullet 1, later, or never |
| Verification | How adoption will be proven |
| Contamination risk | How the change avoids becoming more process narration |

At minimum, reconcile:

1. Canonical Artifact Purity
2. artifact/reviewer/context contamination
3. information-surface routing
4. role and context isolation
5. Cold Frank and frozen targets
6. Codex cold inventory and audit role
7. judgment-surface rehydration
8. search as navigation, not review
9. corrective-loop protocol
10. tracer-bullet sizing
11. progressive disclosure
12. deterministic feedback loops
13. prototype discipline
14. handoff minimalism
15. event/state/evidence/judgment/memory separation
16. human decision and accountability

Do not edit Agent Rig during the initial reconciliation unless the user explicitly authorizes implementation after reviewing the findings.

---

## 19. Proposed first governance pilot

After reconciliation, select one real, low-risk Agent Rig workflow as the first tracer bullet.

The pilot should prove:

- one bounded human intent enters the rig;
- the orchestrator creates a finite work contract;
- the implementer receives sufficient but limited context;
- deterministic checks provide evidence;
- activity is represented without contaminating canonical artifacts;
- the result is frozen and identifiable;
- Codex can independently audit the result;
- Cold Frank can judge without an author narrative;
- the human can review evidence and decide;
- failure or rejection leaves a clean, useful record;
- the runtime returns to a known state.

The pilot should not attempt to prove the entire hosted control plane, every agent role, all memory designs, the full UI, or every integration.

---

## 20. Definition of success

This doctrine has been successfully ported only when:

- it is reconciled against the frozen as-built inventory;
- adopted rules have one clear authoritative home;
- Agent Rig's canonical artifacts no longer serve as process journals;
- event, progress, history, judgment, and specification surfaces are distinguishable;
- work is packaged as bounded tracer bullets;
- each implementation context has a stop condition;
- failed gates begin fresh corrective contexts;
- implementers rehydrate the complete bounded judgment surface;
- reviewers receive artifacts, criteria, and boundaries—not answer keys;
- judged targets are reproducibly frozen;
- deterministic evidence is available before semantic judgment;
- the human remains the final accountable decision-maker;
- the first real pilot works before the doctrine is generalized.

---

## 21. Prompt to hand Agent Rig after the cold inventory

> The attached document is a proposed Agent Rig AI-build governance and tracer-bullet doctrine. Do not treat it as a description of current implementation or as authority over the frozen cold inventory. First read the completed Agent Rig cold-inventory artifacts and preserve their findings unchanged. Then reconcile this doctrine against the observed system using KEEP / ADD / MODIFY / DEFER / REJECT. Identify where each adopted rule should live, but do not edit the repository yet. Pay particular attention to Canonical Artifact Purity; separation of events, state, evidence, judgments, memory, handoffs, specifications, and history; context isolation; full judgment-surface rehydration; Codex's independent audit role; Cold Frank; and one-ticket/one-context tracer bullets. Recommend the smallest first governance pilot and end with one next action. Ask only one question if a material decision truly cannot be made from the inventory and existing project evidence.

---

## Final orientation

> **Agent Rig should help agents do bounded work, preserve evidence, and support independent human judgment. It should not turn agent narration into system truth or process ceremony into product architecture.**

And:

> **Inventory cold. Reconcile explicitly. Build vertically. Keep truth surfaces clean. Rehydrate before correcting. Judge frozen work independently. Standardize only what repeated experience earns.**
