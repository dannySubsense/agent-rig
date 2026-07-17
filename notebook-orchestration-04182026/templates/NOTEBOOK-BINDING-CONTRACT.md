# Notebook Binding Contract Template

Every notebook-framework delegation uses this template. Contracts must be concrete — no placeholders reach the agent.

---

## Standard Contract Format

```
═══════════════════════════════════════════════════════════════════
TASK: NOTEBOOK — [AGENT TASK DESCRIPTION]
═══════════════════════════════════════════════════════════════════

ROLE
Agent: @[agent-name]
Constraints: Follow your preloaded skill exactly. HALT on ambiguity.

GOVERNANCE (LOCKED)
- INVARIANTS: [path to NOTEBOOK-INVARIANTS.md]
- PLANNING_DOC: [path to planning doc]

INPUTS
- NOTEBOOK_NUMBER: [e.g., 02]
- NOTEBOOK_NAME: [e.g., the_plays]
- [additional inputs specific to the agent]

OBJECTIVE
[Single sentence describing what this delegation achieves]

SCOPE
IN:
- [Specific thing to do]
- [Specific thing to do]

OUT:
- [Explicit exclusion]
- [Explicit exclusion]

HALT IF
- [Condition that should stop work]
- Any ambiguity in inputs

OUTPUT
- Files: [expected output files with paths]
- Report: Status + summary under 30 lines

═══════════════════════════════════════════════════════════════════
```

---

## Example: Designer Contract

```
═══════════════════════════════════════════════════════════════════
TASK: NOTEBOOK — Produce design sheet for notebook 02
═══════════════════════════════════════════════════════════════════

ROLE
Agent: @notebook-designer
Constraints: Follow notebook-design skill. HALT on ambiguity.

GOVERNANCE (LOCKED)
- INVARIANTS: docs/research/NOTEBOOK-INVARIANTS.md
- PLANNING_DOC: docs/research/planning/notebook-roadmap.md

INPUTS
- NOTEBOOK_NUMBER: 02
- NOTEBOOK_NAME: the_plays
- DESIGN_SHEET_PATH: docs/research/planning/notebooks/02-design.md
- DATASET_PATHS:
  - docs/research/data/backtest_results.parquet
  - docs/research/data/backtest_participants.parquet
- CONVENTION_REFERENCE: /home/d-tuned/market_data/notebooks/01_eod_explorer.ipynb

OBJECTIVE
Produce a 1-2 page design sheet for notebook 02 "The Plays" — defines
setup_type A-E with real examples and characteristic actors.

SCOPE
IN:
- Extract notebook 02's context from the planning doc
- Inspect Parquet schemas (not full data)
- Read the convention reference for style match
- Produce design sheet following DESIGN-SHEET-TEMPLATE

OUT:
- Do not write the notebook itself
- Do not execute any queries against the data
- Do not invent questions beyond what the planning doc suggests

HALT IF
- Planning doc doesn't describe notebook 02
- Dataset paths don't exist
- A question in the sheet cannot be answered from the given data

OUTPUT
- File: docs/research/planning/notebooks/02-design.md
- Report: Status + sections/questions counts under 30 lines

═══════════════════════════════════════════════════════════════════
```

---

## Example: Builder Contract

```
═══════════════════════════════════════════════════════════════════
TASK: NOTEBOOK — Build notebook 02 from approved design sheet
═══════════════════════════════════════════════════════════════════

ROLE
Agent: @notebook-builder
Constraints: Follow notebook-build skill. HALT on ambiguity.

GOVERNANCE (LOCKED)
- INVARIANTS: docs/research/NOTEBOOK-INVARIANTS.md
- DESIGN_SHEET: docs/research/planning/notebooks/02-design.md (APPROVED)

INPUTS
- NOTEBOOK_PATH: research/notebooks/02_the_plays.ipynb
- SKELETON_PATH: ~/.claude/templates/NOTEBOOK-SKELETON.ipynb
- DATASET_PATHS:
  - docs/research/data/backtest_results.parquet
  - docs/research/data/backtest_participants.parquet
- CONVENTION_REFERENCE: /home/d-tuned/market_data/notebooks/01_eod_explorer.ipynb

OBJECTIVE
Implement the approved design sheet as a runnable .ipynb.

SCOPE
IN:
- Every section in the design sheet
- Every question mapped to at least one section
- Populated (non-placeholder) Findings section

OUT:
- Sections not in the design sheet
- Execution (that's @notebook-executor)
- Debug cells or exploratory leftovers

HALT IF
- Design sheet is ambiguous about a section's content
- An invariant would be violated to satisfy the design

OUTPUT
- File: research/notebooks/02_the_plays.ipynb
- Report: Status + cell/section counts under 30 lines

═══════════════════════════════════════════════════════════════════
```

---

## Contract Rules

1. **Concrete values only** — Never `[placeholder]`, always actual paths and names
2. **Reference documents by path** — "INVARIANTS: docs/research/NOTEBOOK-INVARIANTS.md"
3. **Explicit scope** — IN and OUT sections prevent drift
4. **Clear HALT conditions** — Agent knows when to stop
5. **Verifiable output** — Advisor can check files exist

## Common Mistakes

❌ `NOTEBOOK_PATH: research/notebooks/[name].ipynb`
✅ `NOTEBOOK_PATH: research/notebooks/02_the_plays.ipynb`

❌ `Build the notebook`
✅ `Implement the approved design sheet as a runnable .ipynb, per notebook-build skill`

❌ `HALT IF: something goes wrong`
✅ `HALT IF: design sheet missing or an invariant would be violated`
