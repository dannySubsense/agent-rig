# Forge

A multi-agent software development framework that builds, tests, and verifies code through disciplined orchestration.

**Version:** 03132026  
**Architecture:** Agent Skills Open Standard (2026)

---

## Philosophy

> "Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information." — Anthropic

Forge solves this by:
1. **Separating WHO from HOW** — Agents define identity; Skills define procedures
2. **No self-verification** — Each agent's work is checked by another
3. **Concrete contracts** — Actual paths, not placeholders
4. **File as deliverable** — Work lives in files, not responses

---

## Architecture

```
Spec Documents (from Spec Orchestration)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORGE ADVISOR (Orchestrator)                  │
│   Command: /forge-start                                         │
│   Sequences agents, passes contracts, verifies outputs          │
└────┬─────────┬─────────┬─────────┬─────────┬───────────────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  CODE  │ │  TEST  │ │  TEST  │ │   QC   │ │ GITHUB │
│EXECUTOR│ │ WRITER │ │ RUNNER │ │ AGENT  │ │  OPS   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
  Code       Tests      Test      QC        Git
  Files      Files     Results   Report   Commits
```

---

## Agents

| Agent | Responsibility | Model | Cannot |
|-------|----------------|-------|--------|
| @code-executor | Implement code per spec | sonnet | Write tests, make design decisions |
| @test-writer | Write tests per spec | sonnet | Run tests, modify implementation |
| @test-runner | Run tests, report results | sonnet | Fix failures, modify code |
| @qc-agent | Verify against spec + invariants | opus | Modify anything |
| @github-ops | Git operations, PRs | sonnet | Write code or tests |
| @doc-writer | Documentation only | sonnet | Modify code |
| @research | Technical investigation | sonnet | Implement, make decisions |

**Core principle:** No agent verifies their own work.

---

## Orchestration Flow

Every implementation slice follows this sequence:

```
1. @code-executor  → Implements the slice
   └── VERIFY: files exist

2. @test-writer    → Writes tests for the slice
   └── VERIFY: test files exist

3. @test-runner    → Runs tests
   ├── PASS → Continue to QC
   └── FAIL → Advisor diagnoses, re-delegates fix

4. @qc-agent       → Verifies compliance with spec
   ├── PASS → Slice complete
   └── VIOLATIONS → Advisor re-delegates correction

5. @github-ops     → Commits (optional, per workflow)
```

---

## Integration with Spec Orchestration

Forge consumes the 5 spec documents:

```
docs/specs/{feature}/
├── 01-REQUIREMENTS.md   → Acceptance criteria for QC
├── 02-ARCHITECTURE.md   → Patterns, schemas for @code-executor
├── 03-UI-SPEC.md        → Layouts, flows for @code-executor
├── 04-ROADMAP.md        → Slices for Forge Advisor to sequence
└── 05-REVIEW.md         → Risks, assumptions to watch for
```

Contracts reference these documents:
- "Per 02-ARCHITECTURE.md §Data Schemas..."
- "Per 04-ROADMAP.md Slice 2..."

---

## Quick Start

```bash
# Install
./install.sh

# Start a forge session (after specs are approved)
claude
/forge-start

# Point to the spec directory
> Build from docs/specs/model-viewer/
```

---

## File Structure

```
~/.claude/
├── agents/
│   ├── code-executor.md
│   ├── test-writer.md
│   ├── test-runner.md
│   ├── qc-agent.md
│   ├── github-ops.md
│   └── doc-writer.md
├── skills/
│   ├── code-implementation/SKILL.md
│   ├── test-writing/SKILL.md
│   ├── test-execution/SKILL.md
│   ├── quality-verification/SKILL.md
│   ├── git-operations/SKILL.md
│   └── documentation-writing/SKILL.md
└── commands/
    └── forge-start.md
```

---

## Governance Documents

Your project should have:

| Document | Purpose | Location |
|----------|---------|----------|
| `CLAUDE.md` | Project context, conventions | Project root |
| `INVARIANTS.md` | Inviolable rules | `docs/` |
| `CADENCE.md` | Workflow phases | `docs/` |

Templates provided in `templates/`.

---

## HALT Conditions

Agents HALT (don't guess) when:
- Specification is ambiguous
- Required input is missing
- Constraint would be violated
- Decision exceeds their authority

HALTs are **success** — they surface problems before they compound.

---

## References

- Agent Orchestration Architecture (03112026)
- Agent Skills Open Standard: https://agentskills.io
- Anthropic: "How we built our multi-agent research system"
