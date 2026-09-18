# Agent Rig Cold Inventory Audit Charter

**Audit type:** Independent, evidence-based, read-only inventory  
**Primary auditor:** Codex  
**Primary subject:** The local `agent-rig` repository and its observable local operating context  
**Secondary subject:** The configured remote repository, reconciled after the local state is captured  
**Initial posture:** Cold review — inspect implementation before receiving the author’s architectural narrative

## 1. Mission

Determine what Agent Rig **actually is today** from the live repository and directly observable evidence.

Produce a reproducible inventory of:

- the committed repository at the checked-out `HEAD`;
- staged, unstaged, and untracked local work, kept separate from `HEAD`;
- branches, worktrees, commands, hooks, services, integrations, interfaces, state stores, and runtime dependencies that can be established from evidence;
- the relationship between the local repository and its configured remote;
- capabilities that demonstrably exist, partially exist, or do not have sufficient implementation evidence;
- overlaps, disconnected pieces, obsolete experiments, and material gaps visible from the implementation.

This is a **reality inventory**, not an architecture redesign, implementation task, or validation of the author’s intentions.

## 2. Governing principle

> Give the unbiased auditor the map, not the path.

The auditor receives the repository boundary, audit questions, evidence rules, and required outputs. The auditor must determine its own inspection route.

Repository evidence outranks names, documentation claims, memory, prior verdicts, and completion statements.

## 3. Independence boundary

### Phase 1: Cold inventory

Before the Phase 1 report is frozen, do **not** consult:

- the Agent Rig build-idea index;
- an orchestrator or author’s explanation of intended architecture;
- LORE records or summaries;
- prior assistant descriptions of Agent Rig;
- PStack, HumanLayer, PostHog, Grok Bot, or other external comparison frameworks;
- a checklist organized around expected named components.

Repository-local documentation is part of the implementation evidence and may be inspected, but its claims must be distinguished from executable or operational evidence.

### Phase 2: Reconciliation

Phase 2 begins only after the Phase 1 report is saved and its repository state is identified by SHA and working-tree fingerprint.

During Phase 2, compare the frozen inventory with:

1. the author/orchestrator declaration;
2. the Agent Rig build-idea index;
3. relevant LORE claims;
4. remote repository state and other adjacent systems explicitly brought into scope.

Do not rewrite the Phase 1 findings. Record reconciliation as a separate report or appended section that preserves the original observations.

## 4. Authorization and safety constraints

The audit is read-only.

### Permitted

- Read files and repository metadata.
- Run non-mutating discovery commands.
- Inspect Git history, branches, tags, worktrees, remotes, diffs, and configuration.
- Use static-analysis tools that do not rewrite files.
- Run tests or diagnostic commands only when they are known not to modify tracked or user-owned files.
- Inspect process/service/configuration metadata when access already exists and inspection is non-mutating.
- Use `git ls-remote` when network access is available because it does not update local refs.

### Prohibited without explicit approval

- Editing, formatting, generating, deleting, moving, or renaming files.
- Committing, merging, rebasing, stashing, checking out another branch, or changing worktrees.
- Installing dependencies or updating lockfiles.
- Starting, stopping, or reconfiguring services.
- Running migrations.
- Invoking agents, hooks, automations, or workflows that can perform mutations.
- Fetching or pulling during the initial local-state capture. `git fetch` changes local remote-tracking metadata and requires separate authorization.
- Exposing secret values. Record only the existence, expected role, and source location of secret-bearing configuration.

If a useful command may mutate state, do not run it. Record the limitation and the proposed command under **Blocked Verification**.

## 5. Evidence planes

Keep these planes separate throughout the report:

| Evidence plane | What it establishes |
|---|---|
| Local committed `HEAD` | Reproducible code baseline currently checked out |
| Staged changes | Local work prepared for a possible commit |
| Unstaged tracked changes | Local modifications not represented by `HEAD` |
| Untracked files | Local artifacts or work not represented in Git history |
| Ignored/configuration files | Local runtime support; inspect carefully without exposing secrets |
| Local runtime evidence | Processes, services, stores, sockets, logs, and integrations directly observable without mutation |
| Existing local remote-tracking refs | Last locally recorded view of remote branches; potentially stale |
| Live remote observation | Current published/shared state established without altering the local working state |
| Documentation claims | Statements of intent or operation requiring corroboration |
| Inference | Auditor interpretation, explicitly labeled and never presented as observed fact |

Never silently blend local uncommitted work into the committed baseline or treat locally configured runtime state as remotely reproducible.

## 6. Required opening capture

Record before deeper inspection:

- absolute repository path;
- audit start time and timezone;
- current branch or detached-HEAD state;
- full `HEAD` SHA;
- concise and porcelain Git status;
- staged, unstaged, and untracked file lists;
- configured remotes without credentials;
- local branches and their upstream/tracking status;
- tags relevant to the current line of development;
- registered Git worktrees;
- submodules, nested repositories, and symlinks;
- applicable `AGENTS.md`, `CLAUDE.md`, or repository-local instructions;
- available toolchain versions relevant to safe verification.

If secrets appear in command output, redact values in the report.

## 7. Inventory scope

Inventory what is demonstrably present in or directly connected to the repository. Do not assume these categories exist merely because they are listed:

1. Repository structure and package/module boundaries
2. Entry points, commands, scripts, and interfaces
3. Agent definitions, roles, prompts, skills, and lifecycle
4. Orchestration, task routing, delegation, resumption, and handoffs
5. Hooks, enforcement controls, permissions, and approval gates
6. Judgment, review, tests, evidence, and quality gates
7. Runtime processes, supervision, wake/sleep behavior, and recovery
8. Events, telemetry, logs, traces, metrics, and provenance
9. Memory, context assembly, state, persistence, and data stores
10. Git, branches, worktrees, commits, artifacts, and review workflow
11. User interfaces, dashboards, CLI/TUI/web/MCP surfaces
12. External integrations and adjacent repositories/services
13. Configuration, deployment, infrastructure, and environment assumptions
14. Tests, fixtures, examples, demonstrations, and operational runbooks
15. Dead code, duplicated mechanisms, unfinished migrations, and abandoned experiments

## 8. Evidence standard

Every substantive finding must include the strongest available evidence:

- exact file path and line reference where practical;
- command and summarized output;
- commit, branch, tag, or worktree identity;
- test or reproducible observation;
- dependency/configuration reference;
- direct runtime observation; or
- an explicit statement that the conclusion is inference rather than fact.

Documentation alone proves that a claim was written, not that the described capability works.

The absence of a discovery result is not automatically proof of absence. Use **Not Found** or **Indeterminate** when appropriate and state the search performed.

## 9. Classification vocabulary

Use these status labels consistently:

| Status | Meaning |
|---|---|
| **Implemented** | Concrete implementation exists and its basic operation is directly verifiable |
| **Partial** | Some implementation exists, but the capability or path is incomplete |
| **Present — unverified** | Relevant implementation exists but cannot be safely exercised in this audit |
| **Documentation only** | Described in documentation with no corroborating implementation found |
| **Proposed only** | Appears as a plan, issue, placeholder, TODO, or design proposal |
| **Duplicate/overlapping** | Multiple mechanisms appear to serve substantially the same role |
| **Disconnected** | Implemented code exists but no active route, caller, registration, or deployment was found |
| **Obsolete/abandoned candidate** | Evidence suggests supersession or abandonment; do not declare obsolete without support |
| **Not found** | Targeted searches found no evidence; include search scope |
| **Indeterminate** | Available evidence cannot resolve the status |

Also assign a maturity level where evidence supports it:

- **Concept**
- **Prototype**
- **Operational but fragile**
- **Operational**
- **Hardened**
- **Indeterminate**

Do not use unsupported percentage-complete estimates.

## 10. Required deliverables

Produce the following as Markdown files in a new audit-output directory outside the audited repository, unless the user specifies another safe location.

### A. `00-audit-state.md`

- Repository identity and audit timestamp
- `HEAD`, branch, status, remotes, worktrees, and toolchain
- Scope, exclusions, blockers, and commands used
- Working-tree fingerprint sufficient to identify the audited state

### B. `01-repository-and-service-register.md`

For each repository, package, service, process, store, interface, or integration:

- observed name;
- type;
- path/location;
- apparent purpose;
- entry point;
- dependencies;
- evidence;
- status and maturity;
- ownership only when evidenced;
- open questions.

### C. `02-capability-matrix.md`

Map observed capabilities to their implementations, callers/consumers, evidence, status, maturity, and known limitations.

### D. `03-as-built-architecture.md`

Describe the architecture that exists—not the architecture the auditor thinks should exist. Include a compact Mermaid diagram and explain important flows and boundaries.

### E. `04-gap-overlap-and-risk-register.md`

Record:

- missing or unverifiable operational dependencies;
- duplicate or overlapping mechanisms;
- disconnected components;
- naming collisions;
- hidden local-only dependencies;
- provenance, authority, permission, and recovery risks;
- documentation/implementation drift.

Prioritize by consequence and evidence, not speculation.

### F. `05-decision-queue.md`

List only decisions that cannot be settled from repository evidence. For each:

- the decision required;
- why evidence cannot settle it;
- affected components;
- available options already evidenced;
- the minimum person or source needed to resolve it.

Do not recommend a target architecture during Phase 1.

### G. `06-cold-inventory-summary.md`

A concise executive summary containing:

- what Agent Rig demonstrably is today;
- what appears operational;
- what is partial, local-only, disconnected, or unverified;
- the most consequential gaps or contradictions;
- confidence and limitations;
- a clear statement that the report predates author/index/LORE reconciliation.

## 11. Local-to-remote reconciliation

After capturing local state:

1. Identify the configured canonical remote from Git configuration; do not assume `origin` is authoritative.
2. Distinguish existing local remote-tracking refs from live remote observations.
3. Without changing the working tree, determine whether the current local branch is aligned, ahead, behind, diverged, unpublished, or indeterminate.
4. Identify remote-only branches or tags relevant to the current system when this can be done non-mutatively.
5. Record remote comparison separately from local implementation findings.
6. Never treat uncommitted local work as published or canonical.

If current remote state cannot be observed safely or credentials are unavailable, mark it **Blocked** or **Indeterminate** rather than guessing.

## 12. Stop conditions

Stop and ask for direction if:

- the repository path is ambiguous;
- repository-local instructions conflict with this charter;
- inspection requires credentials not already configured for the task;
- a necessary command would mutate user data or repository state;
- secret material cannot be safely avoided;
- the repository appears to contain another person’s unrelated private data;
- the audit scope expands materially beyond Agent Rig and its directly evidenced dependencies.

## 13. Completion gate

Phase 1 is complete only when:

- all seven deliverables exist;
- the inspected SHA and working-tree state are recorded;
- observed facts and inference are visibly separated;
- committed, uncommitted, runtime, documentation, and remote evidence are not blended;
- every material claim has evidence or an explicit limitation;
- no repository or runtime mutation occurred;
- the cold report has been frozen before receiving the build-idea index, LORE, or author narrative.

The next action after completion is **reconciliation**, not implementation.
