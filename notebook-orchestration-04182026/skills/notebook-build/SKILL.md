---
name: notebook-build
description: |
  Step-by-step process for writing a Jupyter notebook from an approved design sheet.
  Use after the design sheet is human-approved, before execution.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Notebook Build

Procedural guide for implementing an approved design sheet as a runnable .ipynb.

## Goal

Produce a Jupyter notebook that:
- Matches every section in the design sheet
- Answers every listed question with a concrete cell
- Satisfies every invariant in `NOTEBOOK-INVARIANTS.md`
- Will execute end-to-end without modification

This is a translation task, not a design task. If you find yourself inventing sections or questions, HALT.

---

## Step 1: Load the Contract

Read and extract from the contract:
- `DESIGN_SHEET_PATH` — approved design sheet
- `NOTEBOOK_PATH` — where to write the .ipynb
- `SKELETON_PATH` — template to start from (default: `~/.claude/templates/NOTEBOOK-SKELETON.ipynb`)
- `DATASET_PATHS` — paths to the data
- `INVARIANTS_PATH` — `docs/research/NOTEBOOK-INVARIANTS.md` or template fallback
- `CONVENTION_REFERENCE` — optional, the notebook to match style to

## Step 2: Load All Inputs

```
1. Read DESIGN_SHEET_PATH — your ground truth
2. Read INVARIANTS_PATH — the rules you cannot violate
3. Read SKELETON_PATH — the starting shape of the .ipynb
4. Read CONVENTION_REFERENCE if provided — style match
5. Inspect each dataset path via DuckDB DESCRIBE — know the schema
```

## Step 3: Start From the Skeleton

Copy the skeleton to the output path. The skeleton contains:
- Title cell (to be filled)
- Purpose cell (to be filled)
- Imports cell
- Config cell (dataset paths, DB connection)
- Section scaffold placeholder
- Findings cell at the end

You extend this. You do not throw it away.

## Step 4: Fill the Header

Replace skeleton placeholders with:
- **Title cell:** `# Notebook [NN]: [Name]` + 1-2 sentence purpose from design sheet
- **Config cell:** parameterize dataset paths from the design sheet:

  ```python
  # Config — all paths parameterized here
  BACKTEST_RESULTS = "docs/research/data/backtest_results.parquet"
  BACKTEST_PARTICIPANTS = "docs/research/data/backtest_participants.parquet"
  MARKET_DATA_DB = "/home/d-tuned/market_data/duckdb/market_data.duckdb"
  ```

  **No hardcoded paths anywhere else in the notebook** (invariant #8).

## Step 5: Build Each Section

For each section in the design sheet's outline, in order:

1. **Markdown header cell** with the section number and title (match design sheet exactly)
2. **Intent markdown cell** — 1-2 sentences on what this section is doing and why
3. **Code cell** — the query/analysis. Follow these rules:
   - DuckDB-first for data queries (not pandas loading then filtering)
   - Parameterized by the config variables
   - Explicit NULL handling (invariant #5)
   - Output a result (table, chart, value) — not silent
4. **If the cell produces a chart:**
   - Title (invariant #1)
   - Axis labels (invariant #1)
   - Optional caption markdown cell below explaining what to take from it
5. **Optional "Try It Yourself" callout** if the convention reference uses these

Common patterns:

```python
# DuckDB read Parquet directly
import duckdb
con = duckdb.connect(':memory:')
df = con.execute(f"""
    SELECT setup_type, COUNT(*) AS n
    FROM '{BACKTEST_RESULTS}'
    WHERE filter_status = 'PASSED'
      AND setup_type IS NOT NULL  -- explicit NULL handling
    GROUP BY setup_type
    ORDER BY n DESC
""").fetchdf()
```

```python
# Chart with required title + labels
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
df.plot(kind='bar', x='setup_type', y='n', ax=ax)
ax.set_title('Passed Filings by Setup Type')
ax.set_xlabel('setup_type')
ax.set_ylabel('count')
plt.tight_layout()
```

## Step 6: Populate the Findings Section

The Findings section at the end must be **non-empty** (invariant #3).

You cannot actually run the queries — that's the executor's job. But you *can* project what the findings will look like based on the queries you wrote. Populate with:

- Bullet list of observations the notebook will produce
- Placeholders for numerical values using the format `_<query N output>_` or similar
- One summarizing sentence on what "Done when" from the design sheet means in this context

The executor and the builder iterate: after execution, if findings are still placeholder-heavy or don't reflect actual outputs, QC will flag and you re-populate with real numbers.

## Step 7: Verify Your Output Before Writing

- [ ] Every section in the design sheet has a corresponding section in the notebook, in order
- [ ] Every question from the design sheet maps to at least one section
- [ ] Every SQL code cell has an intent markdown cell above it
- [ ] Every chart has title + axis labels
- [ ] NULL handling is explicit in every query
- [ ] No hardcoded paths (all via config variables)
- [ ] Findings section is non-empty
- [ ] No debug cells (no orphan print, no commented-out code)
- [ ] Notebook JSON is valid (cells array well-formed)

If any box is unchecked, fix before writing.

## Step 8: Write the File

Write the .ipynb to `NOTEBOOK_PATH`. Validate by parsing back as JSON.

## Step 9: Return Status

```
✅ NOTEBOOK BUILT

File: [path]
Cells: [total] ([code] code, [markdown] markdown)
Sections: [count from design sheet] — all present
Invariants self-check: all satisfied

Ready for: @notebook-executor

Status: COMPLETE
```

---

## HALT Conditions

HALT if:
- Design sheet or skeleton missing
- Design sheet is ambiguous about a section's content
- An invariant would be violated to satisfy a design sheet requirement
- A design sheet question cannot be answered from the given dataset schema
- Invariants file missing (neither project-local nor template fallback)
