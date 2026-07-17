---
name: notebook-design
description: |
  Step-by-step process for producing a notebook design sheet.
  Use when starting a new notebook, before any .ipynb is written.
allowed-tools: Read, Write, Glob, Grep
---

# Notebook Design

Procedural guide for producing a design sheet from a notebook concept.

## Goal

A 1-2 page document that, if handed to someone else, would be enough to build the notebook without further clarification. Not a spec. Not a wishlist. A structured outline with concrete inputs and expected outputs.

---

## Step 1: Load the Contract

Read and extract from the contract:
- `NOTEBOOK_NUMBER` — e.g., 02
- `NOTEBOOK_NAME` — e.g., the_plays
- `PLANNING_DOC` — path to the planning doc describing this notebook
- `DATASET_PATHS` — concrete Parquet/DB paths
- `DESIGN_SHEET_PATH` — where to write the output
- `CONVENTION_REFERENCE` — optional, a notebook to match style to

## Step 2: Load the Template

Read `~/.claude/templates/DESIGN-SHEET-TEMPLATE.md`. This is the required structure.

## Step 3: Load the Planning Doc

Read the full planning doc. Find the section describing this notebook number. If it doesn't exist, HALT — the notebook hasn't been planned yet.

Extract:
- Purpose (1-2 sentences from the planning doc)
- Intended audience / reader
- Where this notebook sits in the series (what depends on it, what it depends on)

## Step 4: Inspect the Dataset Schema

Use DuckDB's schema inspection — do NOT read full data:

```python
import duckdb
con = duckdb.connect(':memory:')
schema = con.execute("DESCRIBE SELECT * FROM '[PARQUET_PATH]'").fetchall()
```

Or use `pyarrow.parquet.read_schema()` directly.

Capture:
- Column names and types
- Approximate row count (`SELECT COUNT(*) FROM '[PATH]'`)
- Any obvious date range (`SELECT MIN(filed_at), MAX(filed_at) FROM '[PATH]'`)

You need this to know what the notebook can and cannot answer.

## Step 5: Read the Convention Reference (If Given)

If the contract points to a reference notebook, read its structure:
- Section numbering style (1.1, 1.2 vs 1, 2, 3)
- Cell organization (imports location, config cell, section headers)
- Query style (DuckDB-first, pandas-first, hybrid)
- "Try It Yourself" callouts or similar engagement patterns

Match this style in the design sheet's Sections outline.

## Step 6: Draft the Design Sheet

Fill out each required section:

### Purpose
1-2 sentences. What this notebook is *for*. Not "what it does" — "why it exists."

Bad: "This notebook queries the backtest_results table."
Good: "Establish trust in the dataset by mechanically verifying schema, nullability, and distribution expectations before any research derives from it."

### Questions this answers
Bulleted list. Concrete. Answerable from the dataset.

Bad: "Understand the dataset."
Good:
- Are all 11 canonical filter_status values present?
- Does every NON-NULL column have zero nulls?
- Does the SHA-256 in the Parquet match the manifest JSON?

Rule of thumb: 3-8 questions. Fewer = too vague, more = scope creep.

### Sections
Hierarchical outline matching the convention. If the reference uses 1.1, 1.2, 2.1, do the same.

Each leaf section should map to 1-2 questions. If you can't map a section to a question, delete it.

### Data sources
Exact paths. No wildcards.

```
- docs/research/data/backtest_results.parquet
- docs/research/data/backtest_run_metadata.json
```

If the notebook needs tables from `market_data.duckdb`, list them by table name too:

```
- /home/d-tuned/market_data/duckdb/market_data.duckdb
  - daily_prices (for universe verification)
  - raw_symbols_massive (for FK consistency check)
```

### Expected outputs
What the reader walks away with. Concrete artifacts:

- Summary table: filter_status counts across the dataset
- Chart: setup_type distribution by quarter
- Assertion block: SHA-256 of Parquet matches manifest
- Findings section populated with 3-5 bullet observations

### Done when
A single sentence. The criterion that tells you this notebook is complete.

Bad: "When it works."
Good: "A reader unfamiliar with the pipeline can, after reading this notebook, describe each setup_type and recognize it in a new filing."

## Step 7: Self-Check

Before writing to disk:

- [ ] Each question has at least one section that addresses it
- [ ] Each data source is a real path (not `[dataset]`)
- [ ] Each expected output is concrete (not "some charts")
- [ ] "Done when" is a single unambiguous sentence
- [ ] Section outline is hierarchical (matches convention reference if given)
- [ ] No scope creep beyond what the planning doc describes for this notebook

## Step 8: Write the File

Write to `DESIGN_SHEET_PATH`. Use the exact section order and headers from the template.

## Step 9: Return Status

```
✅ DESIGN SHEET COMPLETE

File: [path]
Notebook: [NN_name]
Sections: [count]
Questions: [count]

Ready for: HUMAN APPROVAL GATE

Status: COMPLETE
```

---

## HALT Conditions

HALT if:
- Planning doc doesn't describe this notebook
- Dataset schema doesn't include fields needed to answer the listed questions
- Convention reference cannot be read
- The questions require datasets not in the contract inputs
