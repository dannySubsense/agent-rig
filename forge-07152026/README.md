# Forge

A multi-agent software development framework that builds, tests, and verifies code through disciplined orchestration.

**Version:** 07152026
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

## Mandatory Governance Gate

**`/forge-start` HALTs before any agent delegation if any of the following is missing:**

- `docs/INVARIANTS.md` — Inviolable rules
- `docs/CADENCE.md` — Workflow phases
- `docs/specs/{feature}/NORTH-STAR.md` — Sprint North Star (produced once by `/spec-start`)

There is no "if exists" fallback and no partial-credit path — a missing governance artifact
blocks the whole session, the same way a missing approved `INTAKE.md` blocks `/spec-start`.
`CLAUDE.md` (project context) remains no-HALT if absent — that asymmetry is unchanged.

---

## Architecture

```
Spec Documents (from Spec Orchestration)
        │
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORGE ADVISOR (Orchestrator)                  │
│   Command: /forge-start                                         │
│   Gates governance, sequences agents, passes contracts,          │
│   binds Frank's forge-gate once at completion, verifies outputs  │
└────┬─────────┬─────────┬─────────┬─────────┬─────────┬──────────┘
     │         │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  CODE  │ │  TEST  │ │  TEST  │ │   QC   │ │ FRANK  │ │ GITHUB │
│EXECUTOR│ │ WRITER │ │ RUNNER │ │ AGENT  │ │FORGE-  │ │  OPS   │
│        │ │        │ │        │ │        │ │ GATE   │ │        │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
     │         │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼         ▼
  Code       Tests      Test      QC      Binding    Git
  Files      Files     Results   Report   Verdict   Commits
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
| @frank | Binding forge-gate verdict (`LANE: forge-gate`), runs once at feature completion | fable | Modify anything; override its own verdict |

**Core principle:** No agent verifies their own work.

---

## Orchestration Flow

Every implementation slice follows this sequence:

```
1. @code-executor  → Implements the slice
   ├── Automated gates: lint, format, type check (baked in)
   └── PASS → Continue | FAIL → Fix or HALT

2. @test-writer    → Writes tests for the slice
   ├── Automated gates: compile, smoke test (baked in)
   └── PASS → Continue | FAIL → Fix or HALT

3. @test-runner    → Runs tests + coverage check
   ├── Coverage threshold from INVARIANTS.md
   ├── PASS + Coverage met → Continue to QC
   └── FAIL or Coverage low → Advisor diagnoses

4. @qc-agent       → Deep review (spec compliance)
   ├── Prerequisites: All automated gates passed
   ├── PASS → Continue to Final Check
   └── VIOLATIONS → Advisor re-delegates

5. Forge Advisor   → Final Check
   ├── Verify all gates passed
   ├── Verify tests + coverage
   ├── STAMP: APPROVED → proceed
   └── STAMP: SEND BACK → re-route to agent

6. @github-ops     → Commits (optional, per workflow)
```

Once **every** slice above reaches STAMP: APPROVED, Forge Advisor runs Frank's binding
forge-gate exactly once — not per-slice — before `@doc-writer` and the PR. See
**Frank's Binding Forge-Gate** below.

---

## Integration with Spec Orchestration

Forge consumes the spec documents produced by `/spec-start`:

```
docs/specs/{feature}/
├── NORTH-STAR.md        → Sprint North Star; mandatory input to Frank's forge-gate
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

## Frank's Binding Forge-Gate

Once all slices in `04-ROADMAP.md` reach STAMP: APPROVED, `/forge-start` invokes Frank as a
binding gate — `LANE: forge-gate` — using the same contract shape as Spec Orchestration's
`LANE: spec-gate`. PASS/FAIL/HALT with no manual override at any point. It runs **once**, at
feature/implementation completion, not per-slice:

- **Layer 1** (sprint North Star fidelity) and **Layer 2** (project North Star relevance) are
  both evaluated on **every** attempt (1, 2, and 3 alike) — neither is ever deferred to the
  final attempt.
- Missing `docs/NORTHSTAR.md` (the project North Star) is a HALT outright; a Layer 1 PASS
  never substitutes for a missing Layer 2 check.
- If the project North Star exists but its `Status` is `DRAFT`, Layer 2 may still PASS, but the
  verdict is stamped `PROVISIONAL` and that tag carries unmodified through `GATE-LOG.md`, the
  Session End summary, and the PR description.
- On FAIL, the current implementation artifacts are snapshotted to
  `docs/specs/{feature}/.gate-snapshots/forge/attempt-{N}/` before re-delegation, and the
  attempt counter for `LANE: forge-gate` is independent of `LANE: spec-gate`'s counter.
- At attempt 3, a FAIL includes a convergence judgment (`SHRINKING` / `STATIC` / `THRASHING`);
  the orchestrator independently re-derives that classification from `GATE-LOG.md` and the
  snapshots before surfacing a STATIC/THRASHING result to Danny.

Verdicts append to `docs/specs/{feature}/GATE-LOG.md`'s `## Forge Gate` section. Only a PASS
verdict (PROVISIONAL or not) allows the sequence to continue to `@doc-writer`, the full test
suite, and `@github-ops`'s PR.

Full procedure: `commands/forge-start.md`.

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
│   ├── doc-writer.md
│   └── research.md
├── skills/
│   ├── code-implementation/SKILL.md
│   ├── test-writing/SKILL.md
│   ├── test-execution/SKILL.md
│   ├── quality-verification/SKILL.md
│   ├── git-operations/SKILL.md
│   ├── documentation-writing/SKILL.md
│   └── technical-research/SKILL.md
└── commands/
    └── forge-start.md
```

`@frank` is installed and maintained separately (`agents/frank.md`, shared across Spec
Orchestration and Forge) — not part of this package's own agent set.

---

## Governance Documents

Your project should have:

| Document | Purpose | Location | Status |
|----------|---------|----------|--------|
| `CLAUDE.md` | Project context, conventions | Project root | Optional — no HALT if absent |
| `INVARIANTS.md` | Inviolable rules | `docs/` | **Mandatory — HALT if missing** |
| `CADENCE.md` | Workflow phases | `docs/` | **Mandatory — HALT if missing** |
| `NORTH-STAR.md` | Sprint North Star | `docs/specs/{feature}/` | **Mandatory — HALT if missing** |

Templates for `CLAUDE.md`, `INVARIANTS.md`, and `CADENCE.md` are provided in `templates/`.
`NORTH-STAR.md` is authored by `/spec-start`, not this package.

---

## HALT Conditions

Agents HALT (don't guess) when:
- Specification is ambiguous
- Required input is missing
- Constraint would be violated
- Decision exceeds their authority

The Forge Advisor session itself HALTs before any delegation if `docs/INVARIANTS.md`,
`docs/CADENCE.md`, or `docs/specs/{feature}/NORTH-STAR.md` is missing.

HALTs are **success** — they surface problems before they compound.

---

## References

- Agent Orchestration Architecture (03112026)
- Agent Skills Open Standard: https://agentskills.io
- Anthropic: "How we built our multi-agent research system"
