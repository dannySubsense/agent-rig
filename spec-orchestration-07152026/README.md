# Spec Orchestration Framework

A pre-code documentation system that produces locked specifications before implementation begins.

**Version:** 07152026
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

## Mandatory Intake Rule

**No downstream spec document is generated before an approved Intake exists.**

Every spec session starts with a mechanical gate: `docs/specs/{feature}/INTAKE.md` must exist and contain a `**Status**: APPROVED` line (case-insensitive) before the orchestrator will proceed to the Interview stage or any of the 01-05 documents. A missing file, a `DRAFT`/`REJECTED` status, or an absent Status line is a FAIL — there is no "if exists" fallback and no partial credit. This is a general workflow rule for every sprint that uses this framework, not a one-time or sprint-specific requirement.

---

## Architecture

```
Feature Request (vague)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SPEC ADVISOR (Orchestrator)                   │
│   Command: /spec-start                                          │
│   Gates Intake, conducts Interview, authors North Star,         │
│   delegates 01-05, binds Frank's spec-gate, seeks approval       │
└──┬────────┬─────────┬─────────┬─────────┬─────────┬─────────────┘
   │        │         │         │         │         │
   ▼        ▼         ▼         ▼         ▼         ▼
 STEP 0   STEP 1    STEP 2    STEP 3-7                STEP 8-9
 INTAKE   INTER-    NORTH     REQUIRE-  ARCHI-  UI-  ROAD-  REVIEW  FRANK
 GATE     VIEW      STAR      MENTS     TECTURE SPEC MAP            SPEC-GATE
                                                                    → HUMAN
                                                                      APPROVAL
```

---

## The Full Sequence

The orchestrator (`@spec-advisor`, via `/spec-start`) runs a fixed 0-9 step sequence:

| Step | What Happens | Agent/Mechanism | Output |
|------|--------------|------------------|--------|
| 0 | Intake gate — orchestrator-only, no delegation. Blocks everything downstream until an approved `INTAKE.md` exists | Orchestrator | (gate check, no file) |
| 1 | Interview — inline by default (runs in the live session using the `interview-conduct` skill); subagent fallback (`@interview-conductor`) only when no live channel exists | Orchestrator (inline) or @interview-conductor | `INTERVIEW.md` |
| 2 | North Star — authored once by the orchestrator immediately after Interview closes; `Status: Locked` at authoring, not re-edited mid-sequence | Orchestrator | `NORTH-STAR.md` |
| 3 | Extract requirements | @requirements-analyst | `01-REQUIREMENTS.md` |
| 4 | Design architecture | @architect | `02-ARCHITECTURE.md` |
| 5 | Define UI spec | @ui-spec-writer | `03-UI-SPEC.md` |
| 6 | Build roadmap | @planner | `04-ROADMAP.md` |
| 7 | Review completeness (editorial gap-fix loop precedes Frank's gate) | @spec-reviewer | `05-REVIEW.md` |
| 8 | Frank binding spec-gate (`LANE: spec-gate`), up to 3 attempts, Layer 1 (sprint North Star fidelity) and Layer 2 (project North Star relevance) evaluated on every attempt | @frank | Verdict appended to `GATE-LOG.md` |
| 9 | Human approval — full artifact set (including `NORTH-STAR.md` by name) plus Frank's verdict presented to Danny | Danny | Approval / change request |

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

The orchestrator will first check for an approved `INTAKE.md` before doing anything else. If none exists, it HALTs and asks Danny to author/approve one via `INTAKE-TEMPLATE.md`.

---

## File Structure

```
~/.claude/
├── agents/
│   ├── requirements-analyst.md
│   ├── architect.md
│   ├── ui-spec-writer.md
│   ├── planner.md
│   ├── spec-reviewer.md
│   └── interview-conductor.md
├── skills/
│   ├── requirements-extraction/SKILL.md
│   ├── architecture-design/SKILL.md
│   ├── ui-specification/SKILL.md
│   ├── implementation-planning/SKILL.md
│   ├── spec-review/SKILL.md
│   └── interview-conduct/SKILL.md
└── commands/
    └── spec-start.md
```

---

## Output Location

All spec documents go to: `docs/specs/{feature-name}/`

```
docs/specs/model-viewer/
├── INTAKE.md
├── INTERVIEW.md
├── NORTH-STAR.md
├── 01-REQUIREMENTS.md
├── 02-ARCHITECTURE.md
├── 03-UI-SPEC.md
├── 04-ROADMAP.md
├── 05-REVIEW.md
└── GATE-LOG.md
```

---

## Integration with Implementation

After human approval at Step 9, these docs feed into the Implementation Orchestration framework:

1. Implementation Advisor loads all approved artifacts
2. Binding contracts reference specific sections
3. QC agent (Frank, `LANE: forge-gate`) verifies against spec
4. Changes require spec amendment + re-approval

---

## References

- Agent Orchestration Architecture (03112026)
- Agent Skills Open Standard: https://agentskills.io
- Anthropic Skills Guide (January 2026)
