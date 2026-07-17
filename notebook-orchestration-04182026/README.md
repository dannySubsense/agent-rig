# Notebook Orchestration

A multi-agent framework for building research and validation Jupyter notebooks through disciplined orchestration.

**Version:** 04182026
**Architecture:** Agent Skills Open Standard (2026)

---

## Philosophy

Notebooks are not features. They don't have acceptance criteria, component architectures, or test suites. But they *do* need consistency, quality, and a defensible process — otherwise a 10-notebook series drifts into 10 different quality bars.

This framework adapts the Forge discipline to notebook work:

1. **Separating WHO from HOW** — Agents define identity; Skills define procedures
2. **No self-verification** — Each agent's work is checked by another
3. **Concrete contracts** — Actual paths, not placeholders
4. **File as deliverable** — Work lives in files, not responses
5. **Right-sized scaffolding** — Design sheet (1-2 pages), not full spec (5 docs)

---

## Architecture

```
Planning Doc + Dataset + Design Request
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│           NOTEBOOK ADVISOR (Orchestrator)                        │
│   Command: /notebook-start                                       │
│   Sequences agents, passes contracts, verifies outputs           │
└────┬─────────┬─────────┬─────────┬─────────┬───────────────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│DESIGNER│ │BUILDER │ │EXECUTOR│ │   QC   │ │ FRANK  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
     │         │         │         │         │
     ▼         ▼         ▼         ▼         ▼
 design     .ipynb    _executed   QC        Verdict
 sheet      file      .ipynb      report
```

---

## Agents

| Agent | Responsibility | Model | Cannot |
|-------|----------------|-------|--------|
| @notebook-designer | Produce design sheet from concept + context | sonnet | Write notebook code, execute anything |
| @notebook-builder | Write the .ipynb from approved design sheet | sonnet | Execute the notebook, make design decisions |
| @notebook-executor | Run the notebook, produce _executed version | sonnet | Modify cells, fix errors |
| @notebook-qc | Mechanical QC against design sheet + invariants | opus | Modify any file |
| @frank | Judgment QC — executive verdict gate | opus | Modify any file |

**Core principle:** No agent verifies their own work. Two QC stages (mechanical + judgment).

---

## Orchestration Flow

Every notebook follows this sequence:

```
1. @notebook-designer → Produces design-sheet.md
   ├── Input: concept, planning doc, dataset schema
   └── HUMAN APPROVAL GATE → proceed or revise

2. @notebook-builder → Writes 0X_name.ipynb
   ├── Input: approved design sheet + skeleton template + dataset paths
   └── Output: unexecuted .ipynb

3. @notebook-executor → Produces 0X_name_executed.ipynb
   ├── Input: the unexecuted .ipynb
   ├── Runs: cells in order, captures outputs, flags cell errors
   └── BRANCH:
       ├── CLEAN → Continue to QC
       └── CELL ERRORS → Advisor diagnoses, returns to builder

4. @notebook-qc → Mechanical check
   ├── Checks: design sheet match, invariants, section structure, 
   │          narrative presence, findings populated
   └── BRANCH:
       ├── PASS → Continue to Frank
       └── FAIL → Advisor re-delegates specific fixes

5. @frank → Judgment gate
   ├── Checks: does prose match data, are claims defensible,
   │          what's missing that a skeptic would catch
   └── BRANCH:
       ├── PASS → Continue to Final Check
       └── FAIL → Advisor re-delegates specific fixes

6. Notebook Advisor Final Check
   └── STAMP: APPROVED → hand to human

7. HUMAN FINAL GATE → commit
```

---

## Skills

Each agent is paired with a skill that defines its procedure:

| Agent | Skill |
|-------|-------|
| @notebook-designer | `notebook-design` |
| @notebook-builder | `notebook-build` |
| @notebook-executor | `notebook-execute` |
| @notebook-qc | `notebook-qc` |
| @frank | (persona embedded in agent — no separate skill) |

Skills update independently of agents. Agent definitions stay thin.

---

## Invariants (enforced by @notebook-qc)

A notebook must satisfy all of these to pass mechanical QC:

1. Every chart has a title and axis labels
2. No bare SQL — every query is preceded by a markdown cell explaining intent
3. Findings section exists and is non-empty
4. Notebook executes end-to-end without cell errors
5. All NULL handling in queries is explicit (COALESCE, IS NULL, or filtered)
6. No debug cells (no orphan `print(df)`, no exploratory leftovers)
7. Every "Question this answers" from the design sheet maps to at least one section
8. No hardcoded paths — use the config cell variables

See `templates/NOTEBOOK-INVARIANTS.md` for the full list and rationale.

---

## Quick Start

```bash
# Install
./install.sh

# Start a notebook session
claude
/notebook-start

# Point to the notebook to build
> Build notebook 02 — The Plays — from docs/research/planning/notebook-roadmap.md
```

See `QUICKSTART.md` for a full walkthrough.

---

## File Structure

```
~/.claude/
├── agents/
│   ├── notebook-designer.md
│   ├── notebook-builder.md
│   ├── notebook-executor.md
│   ├── notebook-qc.md
│   └── frank.md
├── skills/
│   ├── notebook-design/SKILL.md
│   ├── notebook-build/SKILL.md
│   ├── notebook-execute/SKILL.md
│   └── notebook-qc/SKILL.md
├── commands/
│   └── notebook-start.md
└── templates/
    ├── DESIGN-SHEET-TEMPLATE.md
    ├── NOTEBOOK-SKELETON.ipynb
    ├── NOTEBOOK-INVARIANTS.md
    └── NOTEBOOK-BINDING-CONTRACT.md
```

---

## Project Inputs

When invoking `/notebook-start`, the orchestrator expects:

- **Planning doc** — the notebook roadmap that describes what this notebook is for (e.g., `docs/research/planning/notebook-roadmap.md`)
- **Notebook concept** — which notebook in the series (by number + name)
- **Dataset paths** — where the data lives (e.g., `docs/research/data/backtest_results.parquet`)
- **Notebook location** — where to write the .ipynb (e.g., `research/notebooks/`)
- **Convention reference** — optional; an existing notebook to match style (e.g., `/home/d-tuned/market_data/notebooks/01_eod_explorer.ipynb`)

These are project-specific inputs. The framework itself holds no project paths.

---

## HALT Conditions

Agents HALT (don't guess) when:
- Design sheet is ambiguous or incomplete
- Required dataset is missing
- Invariant would be violated to satisfy the design
- Decision exceeds the agent's authority

HALTs are **success** — they surface problems before they compound.

---

## Relationship to Forge and Spec Orchestration

This is a sibling framework, not a successor. Use the right tool:

| Artifact | Framework |
|----------|-----------|
| Production feature | Spec Orchestration → Forge |
| Research notebook | Notebook Orchestration |
| Ad-hoc analysis | Interactive Claude session |

---

## References

- Forge: `/home/d-tuned/projects/gap-lens-dilution-filter/forge-03252026/`
- Spec Orchestration: `/home/d-tuned/projects/gap-lens-dilution-filter/spec-orchestration-03242026/`
- Agent Skills Open Standard: https://agentskills.io
