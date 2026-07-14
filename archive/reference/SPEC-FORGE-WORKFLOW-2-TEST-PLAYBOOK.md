# Spec + Forge Workflow #2 — Codified
**Approach:** Claude Code spec-forge files + OpenClaw `sessions_spawn`  
**Reference Implementation:** gap-lens-dilution (2026-03-22 to 2026-03-23)  
**Status:** WORKING — with known issues documented  
**Goal:** Danny says "run spec-forge playbook" → Major Tom executes → Danny walks away

---

## Executive Summary

This workflow uses Claude Code's agent definitions (WHO) and skill files (HOW) but executes via OpenClaw's `sessions_spawn` instead of Claude Code CLI. This bypasses Claude Code's interactive mode issues while preserving the battle-tested agent prompts and procedures.

**Verified working:**
- ✅ Requirements analysis → 01-REQUIREMENTS.md
- ✅ Architecture design → 02-ARCHITECTURE.md  
- ✅ UI specification → 03-UI-SPEC.md
- ✅ Implementation planning → 04-ROADMAP.md
- ✅ Spec review → 05-REVIEW.md
- ✅ Code execution (slices 1-5) via Qwen-Coder
- ✅ Test writing and execution via Kimi

**Known issues:**
- ❌ QC agent (Nemotron) — timeouts, unreliable
- ❌ UI spec writer — contract format issues (needs minimal format)
- ❌ No automated quality gates — lint/format/type/coverage not enforced
- ❌ Package structure not validated — import errors not caught early

---

## Prerequisites

### 1. OpenClaw Config

Add to `~/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 5,
        "maxConcurrent": 8,
        "model": "nvidia-nim/moonshotai/kimi-k2.5"
      }
    }
  }
}
```

Restart gateway: `openclaw gateway restart`

### 2. Agent Files Location

Agent identity files and skill files live in Claude Code's directory:

```
~/.claude/
├── agents/
│   ├── requirements-analyst.md
│   ├── architect.md
│   ├── ui-spec-writer.md
│   ├── planner.md
│   ├── spec-reviewer.md
│   ├── code-executor.md
│   ├── test-writer.md
│   ├── test-runner.md
│   └── qc-agent.md
└── skills/
    ├── requirements-extraction/SKILL.md
    ├── architecture-design/SKILL.md
    ├── ui-specification/SKILL.md
    ├── implementation-planning/SKILL.md
    ├── spec-review/SKILL.md
    ├── code-implementation/SKILL.md
    ├── test-writing/SKILL.md
    └── test-execution/SKILL.md
```

Major Tom reads these directly at spawn time. No copies.

### 3. Project Directory Structure

```
~/projects/{feature}/
├── specs/
│   ├── 01-REQUIREMENTS.md
│   ├── 02-ARCHITECTURE.md
│   ├── 03-UI-SPEC.md
│   ├── 04-ROADMAP.md
│   └── 05-REVIEW.md
├── src/           (created by forge)
├── tests/         (created by forge)
└── INTAKE.md      (Danny + Major Tom planning)
```

---

## Model Assignments

| Role | Model | Rationale |
|------|-------|-----------|
| Requirements Analyst | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient for extraction |
| Architect | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Planning/reasoning strength |
| UI Spec Writer | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| Planner | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| Spec Reviewer | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Strongest NIM reasoning |
| Code Executor | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding specialist |
| Test Writer | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding-focused |
| Test Runner | `nvidia-nim/moonshotai/kimi-k2.5` | Just runs bash, free |
| QC Agent | **DEPRECATED** — use automated checks | Nemotron timeouts |

---

## Phase 1: Spec Pipeline

### Trigger
Danny says: **"Run spec pipeline for [feature]"**

### Pre-Flight (Major Tom)

1. **Confirm feature name** — kebab-case (e.g., `gap-lens-dilution`)
2. **Create directory**: `mkdir -p ~/projects/{feature}/specs/`
3. **Create INTAKE.md** — Danny + Major Tom planning session
4. **Verify agent files exist** — `ls ~/.claude/agents/`

### Execution Sequence

```
Step 1: SPAWN requirements-analyst
  ├── Read: ~/.claude/agents/requirements-analyst.md
  ├── Read: ~/.claude/skills/requirements-extraction/SKILL.md
  ├── Model: nvidia-nim/moonshotai/kimi-k2.5
  ├── Contract: (see Minimal Contract Template below)
  └── VERIFY: ~/projects/{feature}/specs/01-REQUIREMENTS.md exists

Step 2: SPAWN architect
  ├── Read: ~/.claude/agents/architect.md
  ├── Read: ~/.claude/skills/architecture-design/SKILL.md
  ├── Model: nvidia-nim/nvidia/nemotron-3-super-120b-a12b
  ├── Contract: reference 01-REQUIREMENTS.md
  └── VERIFY: ~/projects/{feature}/specs/02-ARCHITECTURE.md exists

Step 3: SPAWN ui-spec-writer
  ├── Read: ~/.claude/agents/ui-spec-writer.md
  ├── Read: ~/.claude/skills/ui-specification/SKILL.md
  ├── Model: nvidia-nim/moonshotai/kimi-k2.5
  ├── Contract: reference 01 and 02
  └── VERIFY: ~/projects/{feature}/specs/03-UI-SPEC.md exists

Step 4: SPAWN planner
  ├── Read: ~/.claude/agents/planner.md
  ├── Read: ~/.claude/skills/implementation-planning/SKILL.md
  ├── Model: nvidia-nim/moonshotai/kimi-k2.5
  ├── Contract: reference 01, 02, 03
  └── VERIFY: ~/projects/{feature}/specs/04-ROADMAP.md exists

Step 5: SPAWN spec-reviewer
  ├── Read: ~/.claude/agents/spec-reviewer.md
  ├── Read: ~/.claude/skills/spec-review/SKILL.md
  ├── Model: nvidia-nim/nvidia/nemotron-3-super-120b-a12b
  ├── Contract: reference all 4 docs
  └── VERIFY: ~/projects/{feature}/specs/05-REVIEW.md exists

Step 6: HALT — Human Gate
  └── Message Danny: "Spec complete. 05-REVIEW.md ready for approval."
  └── Include: gap count, risk count, open questions
  └── WAIT for explicit approval before Forge phase
```

---

## Phase 2: Forge Pipeline

### Trigger
Danny says: **"Forge [feature]"** (after approving specs)

### Pre-Flight (Major Tom)

1. **Read 04-ROADMAP.md** — extract slice list
2. **Create ACTIVE_SPRINT.md** — track slice progress
3. **Verify dependencies** — Python, Node, etc. installed

### Per-Slice Execution

```
For each slice in 04-ROADMAP.md:

  Step 1: PRE-SLICE VALIDATION (NEW — automated gates)
    ├── Check: Package structure valid (__init__.py files exist)
    ├── Check: Dependencies installed (requirements.txt, package.json)
    └── Check: Previous slice tests pass

  Step 2: SPAWN code-executor
    ├── Read: ~/.claude/agents/code-executor.md
    ├── Model: nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct
    ├── Contract: slice details, file list, spec paths
    └── VERIFY: implementation files exist

  Step 3: SPAWN test-writer
    ├── Read: ~/.claude/agents/test-writer.md
    ├── Model: nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct
    ├── Contract: implementation files, acceptance criteria
    └── VERIFY: test files exist

  Step 4: SPAWN test-runner
    ├── Read: ~/.claude/agents/test-runner.md
    ├── Model: nvidia-nim/moonshotai/kimi-k2.5
    ├── Contract: test files to run
    └── BRANCH:
        ├── PASS → continue to QC
        └── FAIL → diagnose, check fix attempts in ACTIVE_SPRINT.md
            ├── < 3 attempts → re-spawn code-executor with fix
            └── ≥ 3 attempts → HALT, message Danny

  Step 5: AUTOMATED QC GATES (NEW — replaces QC agent)
    ├── Run: flake8 (lint check)
    ├── Run: black --check (format check)
    ├── Run: mypy (type check)
    └── Run: pytest --cov-fail-under=90 (coverage check)
    └── BRANCH:
        ├── ALL PASS → slice complete
        └── ANY FAIL → HALT, message Danny with specific failures

  Step 6: Update ACTIVE_SPRINT.md
    └── Mark slice complete, log any issues
```

### Post-Slices

```
After ALL slices complete:

  Step 1: INTEGRATION GATE (NEW)
    ├── Run: End-to-end smoke test
    ├── Run: Real API call test (if applicable)
    └── Run: Playwright verification (if frontend)

  Step 2: SPAWN github-ops (optional)
    ├── Commit all changes
    └── Create PR

  Step 3: Message Danny
    └── "Feature complete. PR ready for review."
```

---

## Minimal Contract Template

**CRITICAL:** Complex contracts with code blocks cause runtime 0s failures. Use this minimal format:

```
You are [agent-name]. [One sentence role description].

FILE: [exact output path]
PROJECT: [project root]
SPEC: [path to relevant spec doc, if needed]

[Objective in 2-3 sentences max]

Reply with: DONE or HALTED [reason]
```

**Rules:**
- No code blocks in contract
- No output format templates
- No constraints sections
- No verbose explanations
- Simple tasks: agent file only
- Complex multi-step: agent file + skill file

---

## HALT Protocol

All agents and Major Tom use this format:

```
❌ HALTED

Reason: [specific reason]
Blocking: [what cannot proceed]
Needs: [what would unblock — Danny decision, clarification, missing file]
```

Major Tom routes all HALTs to Danny via Discord/WhatsApp. Never attempts to resolve autonomously.

---

## Known Issues & Workarounds

### Issue 1: QC Agent Timeouts
**Problem:** Nemotron model times out on large code reviews  
**Workaround:** Replace with automated QC gates (flake8, black, mypy, pytest-cov)  
**Status:** Implemented in this workflow

### Issue 2: UI Spec Writer Contract Errors
**Problem:** UI spec writer fails with verbose contracts  
**Workaround:** Use minimal contract template (see above)  
**Status:** Documented, needs verification

### Issue 3: Package Structure Validation Missing
**Problem:** Import errors not caught until test phase  
**Workaround:** Add pre-slice validation gate (see Phase 2)  
**Status:** Implemented in this workflow

### Issue 4: No Automated Quality Gates
**Problem:** Code passes tests but fails lint/format/type checks  
**Workaround:** Add automated QC gates after test-runner (see Phase 2)  
**Status:** Implemented in this workflow

---

## Workflow Comparison

| Aspect | Claude Code Direct | Workflow #2 (This Doc) | Lobster |
|--------|-------------------|------------------------|---------|
| Interactive mode | Required | Not needed | Not needed |
| HALT behavior | Good | Good | Unknown |
| Approval gates | Manual | Manual | Built-in |
| Resume after HALT | Manual | Manual | Token-based |
| Agent definitions | Auto-resolved | Explicit spawn | YAML-defined |
| Quality gates | Manual QC agent | Automated | Unknown |
| Danny walk-away | No | **Yes (with this workflow)** | TBD |

---

## Files to Update

### AGENTS.md Additions

Add these sections to `~/.openclaw/workspace/AGENTS.md`:

1. **Subagent Model Assignments** — the model table from this document
2. **Spec + Forge Protocol** — when to run spec vs forge, HALT rules, contract template
3. **Automated QC Gates** — flake8, black, mypy, pytest-cov commands
4. **Pre-Slice Validation** — package structure checks

### ACTIVE_SPRINT.md Template

Create template for tracking slice progress:

```markdown
# Active Sprint: [feature-name]
**Phase:** spec | forge
**Status:** [status]
**Started:** [date]

## Danny Approved
- [ ] spec
- [ ] architecture  
- [ ] development

## Slices
| # | Component | Status | QC Pass | Notes |
|---|-----------|--------|---------|-------|
| 1 | [name] | ☐ | ☐ | |

## Fix Attempts Log
| Slice | Attempt | Issue | Resolution |
|-------|---------|-------|------------|
```

---

## Verification Checklist

Before claiming "Danny can walk away":

- [ ] Spec pipeline runs end-to-end without intervention
- [ ] All 5 spec documents generated
- [ ] HALT triggers correctly on ambiguity
- [ ] Forge pipeline runs slice-by-slice without intervention
- [ ] Automated QC gates catch all quality issues
- [ ] Pre-slice validation catches package structure issues
- [ ] Test failures trigger retry loop (< 3 attempts)
- [ ] QC failures HALT with specific error messages
- [ ] Final integration gate passes
- [ ] Danny receives only approval requests and completion notices

---

## Next Steps to Complete Codification

1. **Update AGENTS.md** with sections above
2. **Create ACTIVE_SPRINT.md template**
3. **Test UI spec writer** with minimal contract format
4. **Verify automated QC gates** work on gap-lens-dilution slices 1-5
5. **Run full spec+forge pipeline** on new test project
6. **Document any new issues** in this file

---

**Last Updated:** 2026-03-25  
**Reference Project:** gap-lens-dilution  
**Test Status:** Partial — needs completion
