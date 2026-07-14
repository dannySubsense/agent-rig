# Agent Orchestration Framework Merger — Decision Record

**Date:** 2026-03-19  
**Context:** Strategic discussion between Danny and Major Tom on unifying data and software agent orchestration frameworks  
**Status:** APPROVED for implementation

---

## Background

Danny has been iterating on an agent orchestration framework with Claude Code at work. The framework uses:
- **Spec Orchestration** — Pre-code documentation (5 docs: Requirements, Architecture, UI-Spec, Roadmap, Review)
- **Forge** — Implementation phase (Code → Test → Test-Run → QC → Git)
- **Binding Contracts** — Concrete, section-referenced delegations with IN/OUT scope, HALT conditions
- **INVARIANTS** — Non-negotiable rules that override any contract

Major Tom (this system) has been mimicking this process. The strategic shift: promote Major Tom to orchestration proxy, demote Claude Code to agent executor, with Danny at the top for approval gates only.

---

## Baseline Test Results

**Data Framework v3.1 Status:** PASSED ✓
- All 11 agents present and functional
- All 10+ skills operational
- Commands load properly
- Skill procedures are concrete and executable
- Located at: `~/.claude/`

---

## Conflict/Overlap Audit

### Naming Conflicts: NONE ✓

| Domain | Agents | Notes |
|--------|--------|-------|
| Data | `data-auditor`, `data-executor`, `data-qc`, `dataset-analyst`, etc. | Existing |
| Spec | `requirements-analyst`, `architect`, `ui-spec-writer`, `planner`, `spec-reviewer` | New |
| Forge | `code-executor`, `test-writer`, `test-runner`, `qc-agent`, `github-ops`, `doc-writer`, `research` | New |

**Special case:** `qc-agent` appears in both frameworks:
- `@data-qc` — validates data quality (data framework)
- `@qc-agent` — verifies code against specs (forge framework)

**Decision:** Keep both, distinguish by context. Contracts specify which skill to load.

### Skill Conflicts: NONE ✓

| Domain | Skills |
|--------|--------|
| Data | `duckdb-inspect`, `duckdb-audit`, `data-execution`, `fmp-fetch`, `fmp-reference`, `validation-running`, `validation-writing`, `document-analysis`, `data-qc`, `progress-tracking`, `qa-automation`, `sprint-management`, `system-design`, `backend-dev`, `code-review` |
| Spec | `requirements-extraction`, `architecture-design`, `ui-specification`, `implementation-planning`, `spec-review` |
| Forge | `code-implementation`, `test-writing`, `test-execution`, `quality-verification`, `git-operations`, `documentation-writing`, `technical-research` |

**Note:** `quality-verification` (forge) vs `data-qc` (data) — different domains, keep both.

### Command Conflicts: NONE ✓

| Command | Purpose |
|---------|---------|
| `/data-spec-start` | Data audit & planning (existing) |
| `/data-advisor-start` | Data execution (existing) |
| `/spec-start` | Software specification (new) |
| `/forge-start` | Software implementation (new) |

---

## Approved Merger Structure

### 1. Shared Templates (New)

```
~/.claude/templates/
├── BINDING-CONTRACT.md      (from forge) — Contract format with IN/OUT scope, HALT conditions
├── INVARIANTS.md            (from forge) — Inviolable rules
├── CADENCE.md               (from forge) — Workflow phases and checkpoints
├── 01-REQUIREMENTS.md       (from spec)
├── 02-ARCHITECTURE.md       (from spec)
├── 03-UI-SPEC.md            (from spec)
├── 04-ROADMAP.md            (from spec)
├── 05-REVIEW.md             (from spec)
└── (keep existing data templates: 00-PROJECT-ASSESSMENT.md, etc.)
```

### 2. Agent Additions (11 New)

```
~/.claude/agents/
├── (keep all 11 existing data agents)
├── requirements-analyst.md    [NEW]
├── architect.md               [NEW]
├── ui-spec-writer.md          [NEW]
├── planner.md                 [NEW]
├── spec-reviewer.md           [NEW]
├── code-executor.md           [NEW]
├── test-writer.md             [NEW]
├── test-runner.md             [NEW]
├── qc-agent.md                [NEW — software QC]
├── github-ops.md              [NEW]
├── doc-writer.md              [NEW]
└── research.md                [NEW]
```

### 3. Skill Additions (12 New)

```
~/.claude/skills/
├── (keep all existing data skills)
├── requirements-extraction/SKILL.md    [NEW]
├── architecture-design/SKILL.md        [NEW]
├── ui-specification/SKILL.md           [NEW]
├── implementation-planning/SKILL.md    [NEW]
├── spec-review/SKILL.md                [NEW]
├── code-implementation/SKILL.md        [NEW]
├── test-writing/SKILL.md               [NEW]
├── test-execution/SKILL.md             [NEW]
├── quality-verification/SKILL.md       [NEW]
├── git-operations/SKILL.md             [NEW]
├── documentation-writing/SKILL.md      [NEW]
└── technical-research/SKILL.md         [NEW]
```

### 4. Command Additions (2 New)

```
~/.claude/commands/
├── (keep existing: data-spec-start.md, data-advisor-start.md)
├── spec-start.md              [NEW]
└── forge-start.md             [NEW]
```

---

## Memory & Orchestration Integration

### Major Tom's Role (Approved)

- **Orchestration Proxy:** Spawn and manage Claude Code agents
- **Decision Authority:** Re-delegate failed tests (3-attempt rule), HALT on invariant violation
- **Approval Gates:** Surface spec docs to Danny for approval before Forge phase
- **Briefing & Handoff:** Deliver completed sprints with summary, files, verification, decisions, limitations, next steps

### Memory Scaffolding (No New .md Files)

| Component | Purpose |
|-----------|---------|
| `ACTIVE_SESSIONS.md` | Track spawned Claude Code sessions (status, task, start time) |
| `memory/YYYY-MM-DD.md` | Sprint progress, blockers, decisions |
| `HEARTBEAT.md` | Safety net to remind Major Tom to check sessions |
| `PROGRESS.md` (per sprint) | Framework-native progress tracking |

### HALT Protocol for Invariant Violation

```markdown
❌ SPRINT HALTED — INVARIANT VIOLATION

Invariant: [which one]
Violation: [what happened]
Sprint: [name]
Action required: [Danny's decision needed]
```

Written to daily note, surfaces in memory, heartbeat catches if missed.

### Approval Flow (Approved)

```
Feature Request
    │
    ├── /spec-start (if software) or /data-spec-start (if data)
    │   └── Agents produce spec docs
    │
    ├── Major Tom surfaces specs to Danny
    ├── Danny approves (human gate)
    │
    ├── /forge-start or /data-advisor-start
    │   └── Major Tom orchestrates, 3-attempt rule on failures
    │
    ├── Major Tom delivers briefing
    └── Danny reviews completed sprint
```

---

## Briefing & Handoff Format (Proposed)

```
═══════════════════════════════════════════════════════════════════
SPRINT COMPLETE — [Feature Name]
═══════════════════════════════════════════════════════════════════

SUMMARY
[2-3 sentences: what was built and why]

FILES DELIVERED
- [path] — [purpose]
- [path] — [purpose]

VERIFICATION
- Tests: [X] passing, [Y] failing (if any)
- QC: [PASS / FAIL with notes]
- Invariants: All maintained ✓

DECISIONS MADE
- [Key decision 1]
- [Key decision 2]

KNOWN LIMITATIONS
- [If any]

NEXT STEPS
- [Suggested actions]

═══════════════════════════════════════════════════════════════════
```

---

## Multi-Sprint Management (Experimental)

- Spawn Claude Code sessions with distinct labels (e.g., `kvs-db-deep-dive`, `video-pipeline-spec`)
- `ACTIVE_SESSIONS.md` tracks all
- Major Tom polls/checks status on heartbeat
- If multiple sessions need attention → report all, Danny prioritizes
- Risk: Context switching overhead. Mitigation: Each session self-contained via PROGRESS.md

---

## Next Steps (Post-Approval)

1. ✅ **Create this decision record** (this file)
2. ⏳ **Execute merger:** Install 11 agents, 12 skills, 2 commands, 9 templates
3. ⏳ **Test merged framework:** Run minimal `/spec-start` test
4. ⏳ **Discuss results:** Danny and Major Tom review together

---

## Key Decisions Summary

| Decision | Status |
|----------|--------|
| Unified framework (data + software) | ✅ APPROVED |
| Keep both `@data-qc` and `@qc-agent` (Option B) | ✅ APPROVED |
| Major Tom as orchestration proxy | ✅ APPROVED |
| No new .md files for memory (use existing scaffold) | ✅ APPROVED |
| Human approval gate between spec and forge | ✅ APPROVED |
| 3-attempt rule for test failures | ✅ APPROVED |
| HALT on invariant violation | ✅ APPROVED |
| Test merged framework before full adoption | ✅ APPROVED |

---

**Approved by:** Danny  
**Date:** 2026-03-19 08:49 UTC  
**Executor:** Major Tom
