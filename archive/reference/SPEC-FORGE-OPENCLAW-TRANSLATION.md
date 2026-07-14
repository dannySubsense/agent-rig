# Spec + Forge → OpenClaw Translation
**Author:** Claude (design session with Danny)  
**Date:** 2026-03-23  
**Status:** Phase 1 reference — ready for Major Tom

---

## Context

Danny uses two Claude Code frameworks:
- **Spec Orchestration** — produces 5 locked documents before any code is written
- **Forge** — implements, tests, and verifies code slice-by-slice against those documents

This document maps both frameworks to OpenClaw primitives so Major Tom can implement equivalent pipelines using `sessions_spawn`, subagents, and the existing workspace structure.

---

## Core Philosophy (Same in Both Systems)

> A deterministic orchestrator that never does the work itself. It delegates via explicit contracts, verifies file existence before proceeding, and HALTs rather than guesses.

This is already how Major Tom operates. The frameworks just formalize it for multi-agent pipelines.

---

## Concept Translation Table

| Claude Code Concept | OpenClaw Equivalent | Notes |
|---|---|---|
| `~/.claude/agents/*.md` | Read directly from `~/.claude/agents/` at spawn time | No copies — single source of truth |
| `~/.claude/skills/*/SKILL.md` | Read directly from `~/.claude/skills/` at spawn time | Same — no copies |
| `~/.claude/commands/spec-start.md` | Message to Major Tom: "run spec pipeline for X" | Major Tom IS the orchestrator |
| `@requirements-analyst` | `sessions_spawn` with agent file contents as system prompt | Explicit, not auto-resolved |
| `@architect` | `sessions_spawn` with architect.md contents as system prompt | Same pattern |
| `@spec-reviewer` | `sessions_spawn` with model: Nemotron | Strongest NIM reasoning model |
| `@code-executor` | `sessions_spawn` with model: Qwen-Coder | Coding specialist |
| `HALT` | Major Tom messages Danny on Discord/WhatsApp | Already in Action Protocol |
| `PROGRESS.md` | `ACTIVE_SPRINT.md` | Already exists |
| `docs/specs/{feature}/` | `~/projects/{feature}/specs/` | Active projects live in ~/projects/ |
| `INVARIANTS.md` | Rules section in `AGENTS.md` | Already exists |
| `CLAUDE.md` | `SOUL.md` + `AGENTS.md` | Already exists |
| Contract template | `sessions_spawn` message payload | The contract IS the spawn message |

---

## File Locations

Agent identity files and skill HOW files live in `~/.claude/` — the Claude Code installation on this machine. Major Tom reads them directly at spawn time. No copies are maintained elsewhere.

```
~/.claude/
├── agents/
│   ├── requirements-analyst.md   ← WHO (spec)
│   ├── architect.md
│   ├── ui-spec-writer.md
│   ├── planner.md
│   ├── spec-reviewer.md
│   ├── code-executor.md           ← WHO (forge)
│   ├── test-writer.md
│   ├── test-runner.md
│   ├── qc-agent.md
│   └── github-ops.md
└── skills/
    ├── requirements-extraction/SKILL.md   ← HOW (spec)
    ├── architecture-design/SKILL.md
    ├── ui-specification/SKILL.md
    ├── implementation-planning/SKILL.md
    ├── spec-review/SKILL.md
    ├── code-implementation/SKILL.md        ← HOW (forge)
    ├── test-writing/SKILL.md
    ├── test-execution/SKILL.md
    ├── quality-verification/SKILL.md
    └── git-operations/SKILL.md
```

Project specs and code output:

```
~/projects/{feature}/
└── specs/
    ├── 01-REQUIREMENTS.md
    ├── 02-ARCHITECTURE.md
    ├── 03-UI-SPEC.md
    ├── 04-ROADMAP.md
    └── 05-REVIEW.md
```

---

## Model Assignments

| Role | Model | Rationale |
|---|---|---|
| Requirements Analyst | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient for extraction |
| Architect | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Planning/reasoning strength |
| UI Spec Writer | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| Planner | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| Spec Reviewer | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Strongest NIM reasoning model, free |
| Code Executor | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding specialist, free |
| Test Writer | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding-focused, free |
| Test Runner | `nvidia-nim/moonshotai/kimi-k2.5` | Just runs bash, free |
| QC Agent | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Strongest NIM reasoning model, free |
| GitHub Ops | `nvidia-nim/moonshotai/kimi-k2.5` | Just git commands, free |

All models are free via NVIDIA NIM. No Anthropic API calls during pipeline execution.

---

## Required Config Change

Add to `openclaw.json` under `agents.defaults`:

```json
"subagents": {
  "maxSpawnDepth": 2,
  "maxChildrenPerAgent": 5,
  "maxConcurrent": 8,
  "model": "nvidia-nim/moonshotai/kimi-k2.5"
}
```

`maxSpawnDepth: 2` enables: Major Tom (depth 0) → orchestrator subagent (depth 1) → worker subagents (depth 2).  
`subagents.model` sets the default cheap model for all spawned workers. Individual spawns override this with the model field.

---

## Phase 1: Spec Pipeline

Major Tom acts as Spec Advisor. He never writes spec documents himself — he delegates, verifies, and gates.

### Trigger
Danny sends: `"Run spec pipeline for [feature description]"`

### How to Load an Agent

Before spawning, Major Tom reads the agent file and skill file:

```bash
cat ~/.claude/agents/requirements-analyst.md
cat ~/.claude/skills/requirements-extraction/SKILL.md
```

For complex multi-step tasks (spec pipeline, architecture, review): pass agent file + skill file as combined systemPrompt. For simple single-file implementation tasks: pass agent file only. Adding the skill file causes runtime 0s failures.

### Sequence

```
1. INTAKE
   └── Confirm feature name with Danny (kebab-case)
   └── Create output dir: mkdir -p ~/projects/{feature}/specs/

2. SPAWN requirements-analyst
   ├── systemPrompt: contents of ~/.claude/agents/requirements-analyst.md
   │                 + contents of ~/.claude/skills/requirements-extraction/SKILL.md
   ├── model: nvidia-nim/moonshotai/kimi-k2.5
   ├── message: contract (see Contract Template below)
   └── VERIFY: ~/projects/{feature}/specs/01-REQUIREMENTS.md exists
       └── If missing: HALT → message Danny

3. SPAWN architect
   ├── systemPrompt: architect.md + architecture-design/SKILL.md
   ├── model: nvidia-nim/nvidia/nemotron-3-super-120b-a12b
   ├── message: contract referencing 01-REQUIREMENTS.md
   └── VERIFY: 02-ARCHITECTURE.md exists

4. SPAWN ui-spec-writer
   ├── systemPrompt: ui-spec-writer.md + ui-specification/SKILL.md
   ├── model: nvidia-nim/moonshotai/kimi-k2.5
   ├── message: contract referencing 01 and 02
   └── VERIFY: 03-UI-SPEC.md exists

5. SPAWN planner
   ├── systemPrompt: planner.md + implementation-planning/SKILL.md
   ├── model: nvidia-nim/moonshotai/kimi-k2.5
   ├── message: contract referencing 01, 02, 03
   └── VERIFY: 04-ROADMAP.md exists

6. SPAWN spec-reviewer
   ├── systemPrompt: spec-reviewer.md + spec-review/SKILL.md
   ├── model: nvidia-nim/nvidia/nemotron-3-super-120b-a12b
   ├── message: contract referencing all 4 docs
   └── VERIFY: 05-REVIEW.md exists

7. HUMAN GATE
   └── Message Danny on Discord: "Spec complete. 05-REVIEW.md ready for approval."
   └── Include: gap count, risk count, open questions
   └── HALT — do not proceed to Forge without Danny approval
```

### Review Fix Loop

If Danny requests changes after reviewing 05-REVIEW.md:
1. Parse which document needs the fix
2. Re-spawn the relevant agent with a fix contract
3. Re-spawn spec-reviewer
4. If gaps remain after 2 iterations → HALT, escalate to Danny

---

## Phase 2: Forge Pipeline

Major Tom acts as Forge Advisor. He sequences implementation slice by slice.

### Trigger
Danny approves specs and says: `"Forge [feature]"`

### Sequence (per slice from 04-ROADMAP.md)

```
For each slice:

1. SPAWN code-executor
   ├── systemPrompt: code-executor.md + code-implementation/SKILL.md
   ├── model: nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct
   ├── message: contract (slice details, file list, spec paths)
   └── VERIFY: implementation files exist

2. SPAWN test-writer
   ├── systemPrompt: test-writer.md + test-writing/SKILL.md
   ├── model: nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct
   ├── message: contract (implementation files, acceptance criteria)
   └── VERIFY: test files exist

3. SPAWN test-runner
   ├── systemPrompt: test-runner.md + test-execution/SKILL.md
   ├── model: nvidia-nim/moonshotai/kimi-k2.5
   ├── message: contract (test files to run)
   └── BRANCH:
       ├── PASS → continue to QC
       └── FAIL → diagnose, check ACTIVE_SPRINT.md fix attempts
           ├── < 3 attempts → re-spawn code-executor with specific fix
           └── ≥ 3 attempts → HALT, message Danny

4. SPAWN qc-agent
   ├── systemPrompt: qc-agent.md + quality-verification/SKILL.md
   ├── model: nvidia-nim/nvidia/nemotron-3-super-120b-a12b
   ├── message: contract (all files, all spec docs)
   └── BRANCH:
       ├── PASS → slice complete
       └── FAIL → re-spawn fix, re-spawn qc-agent
           └── ≥ 2 iterations → HALT, message Danny

5. Update ACTIVE_SPRINT.md: mark slice complete

6. (Optional) SPAWN github-ops
   ├── systemPrompt: github-ops.md + git-operations/SKILL.md
   ├── model: nvidia-nim/moonshotai/kimi-k2.5
   └── message: commit the completed slice
```

### End of Feature

```
After ALL slices complete:

1. SPAWN doc-writer (once only, not per slice)
2. Full test suite run across all slices
3. SPAWN github-ops → create PR
4. Message Danny: "Feature complete. PR ready for review."
```

---

## The Spawn Contract Template (Minimal Format — Effective 2026-03-23)

**Critical Discovery:** Complex contracts with code blocks and verbose sections cause runtime 0s failures. Use minimal format.

```
You are [agent-name]. [One sentence role description].

FILE: [exact path]
PROJECT: [project root]
SPEC: [path to relevant spec doc, if needed]

[Objective in 2-3 sentences max]

Reply with: DONE or HALTED [reason]
```

**System Prompt Rules:**
- Simple tasks (single file, clear objective): agent file only
- Complex multi-step backend work: agent file + skill file
- Never combine into massive system prompt

**Format Rules:**
- No code blocks in contract
- No output format templates
- No constraints sections
- No verbose explanations

**Timeout Handling:**
Timeout ≠ failure. Always verify file existence via exec before treating a timeout as a failed spawn. The announce may arrive late or not at all on complex tasks.

---

## HALT Protocol

All agents and Major Tom use this format:

```
❌ HALTED

Reason: [specific reason]
Blocking: [what cannot proceed]
Needs: [what would unblock — Danny decision, clarification, missing file]
```

Major Tom routes all HALTs to Danny via Discord. Never attempts to resolve HALTs autonomously.

---

## Critical Bug to Avoid (OpenClaw 2026.3.13)

**Do NOT use `sessions_yield` + subagent patterns inside cron isolated sessions.**  
The orchestrator aborts after exactly one LLM turn after the subagent completes.

**Workaround:** Run all pipeline steps sequentially within a single session. Major Tom spawns agent 1, waits for the completion announcement, then spawns agent 2. He controls the sequencing — not a workflow engine. This is actually cleaner because Major Tom stays in control of approval gates between steps.

---

## AGENTS.md Additions Required

Major Tom should add two sections to AGENTS.md:

### Section 1: Subagent Model Assignments
The model assignment table from this document — so he knows which model to use for each spawn without re-reading this doc every time.

### Section 2: Spec + Forge Protocol
- When to run spec pipeline vs forge pipeline
- Agent files live at `~/.claude/agents/`, skill files at `~/.claude/skills/`
- Load agent file always. Add skill file only for complex multi-step tasks.
- HALT and approval gate rules
- Contract template reference

---

## Recommended Implementation Phases

### Phase 1 — Foundation (current)
- Add `maxSpawnDepth: 2` config to `openclaw.json` ✓
- Create `~/projects/` directory ✓
- Delete any copied agent/skill files from workspace — use `~/.claude/` directly
- Add Subagent Model Assignments to AGENTS.md
- Add Spec + Forge Protocol to AGENTS.md

### Phase 2 — Spec Pipeline
- Implement full spec pipeline end-to-end
- First real test: token usage dashboard (already in backlog, well-scoped)
- Validate 5-document output before adding Forge

### Phase 3 — Forge Pipeline
- Add forge pipeline after spec is reliable
- Start with a single-slice test before full multi-slice runs
- Add fix-loop logic and PROGRESS tracking to ACTIVE_SPRINT.md
