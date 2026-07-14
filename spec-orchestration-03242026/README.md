# Spec Orchestration Framework

A pre-code documentation system that produces locked specifications before implementation begins.

**Version:** 03132026  
**Architecture:** Agent Skills Open Standard (2026)

---

## Purpose

Prevent agent drift by creating explicit, approved documentation that locks:
- **What** we're building (and NOT building)
- **How** it fits together technically (patterns, schemas, APIs)
- **What** the user sees (screens, flows, interactions)
- **When** each piece gets built (sequence, dependencies)

Implementation agents reference these docs. QC agents verify against them. Humans approve before coding starts.

---

## Architecture

```
Feature Request (vague)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC ADVISOR (Orchestrator)                   │
│   Command: /spec-start                                          │
│   Coordinates agents, passes contracts, verifies outputs        │
└────┬─────────┬─────────┬─────────┬─────────┬───────────────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│REQUIRE-│ │        │ │ UI-SPEC│ │        │ │  SPEC  │
│ MENTS  │ │ARCHITECT│ │ WRITER │ │PLANNER │ │REVIEWER│
│ANALYST │ │        │ │        │ │        │ │        │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
   01-       02-       03-       04-       05-
REQUIRE-   ARCHI-    UI-SPEC   ROADMAP   REVIEW
MENTS.md  TECTURE.md   .md       .md       .md
```

---

## The 5-Document Structure

| Doc | Agent | Locks | Freedom Level |
|-----|-------|-------|---------------|
| `01-REQUIREMENTS.md` | @requirements-analyst | What (and NOT what) | High |
| `02-ARCHITECTURE.md` | @architect | Technical how | Medium |
| `03-UI-SPEC.md` | @ui-spec-writer | Screens, flows, layouts | Medium |
| `04-ROADMAP.md` | @planner | Sequence, files, slices | Low |
| `05-REVIEW.md` | @spec-reviewer | Gaps, risks, approval | — |

---

## Agent/Skill Separation

This framework follows the **Agent Skills Open Standard**:

- **Agents** (`~/.claude/agents/`) — WHO: Identity, tools, model selection
- **Skills** (`~/.claude/skills/`) — HOW: Step-by-step execution procedures
- **Commands** (`~/.claude/commands/`) — Orchestrators that delegate with contracts

Each agent preloads its corresponding skill for procedural guidance.

---

## Quick Start

```bash
# Install
./install.sh

# Start a spec session
claude
/spec-start

# Provide your feature request
> Build a 3D model viewer with real-time collaboration
```

---

## File Structure

```
~/.claude/
├── agents/
│   ├── requirements-analyst.md
│   ├── architect.md
│   ├── ui-spec-writer.md
│   ├── planner.md
│   └── spec-reviewer.md
├── skills/
│   ├── requirements-extraction/SKILL.md
│   ├── architecture-design/SKILL.md
│   ├── ui-specification/SKILL.md
│   ├── implementation-planning/SKILL.md
│   └── spec-review/SKILL.md
└── commands/
    └── spec-start.md
```

---

## Output Location

All spec documents go to: `docs/specs/{feature-name}/`

```
docs/specs/model-viewer/
├── 01-REQUIREMENTS.md
├── 02-ARCHITECTURE.md
├── 03-UI-SPEC.md
├── 04-ROADMAP.md
└── 05-REVIEW.md
```

---

## Integration with Implementation

After human approval, these docs feed into the Implementation Orchestration framework:

1. Implementation Advisor loads all 5 docs
2. Binding contracts reference specific sections
3. QC agent verifies against spec docs
4. Changes require spec amendment + re-approval

---

## References

- Agent Orchestration Architecture (03112026)
- Agent Skills Open Standard: https://agentskills.io
- Anthropic Skills Guide (January 2026)
