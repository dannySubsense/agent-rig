# Notebook Invariants

Rules every notebook in this project must satisfy. Mechanical — each is either satisfied or violated.

**Owned by:** The notebook orchestration framework
**Enforced by:** `@notebook-qc` via the `notebook-qc` skill
**Project-specific overrides:** Copy this file to `docs/research/NOTEBOOK-INVARIANTS.md` and edit.

---

## 1. Every chart has a title and axis labels

**Rationale:** An untitled chart is a lie by omission. A reader who skims the notebook and lands on a chart must be able to understand what it shows without chasing the cell above.

**Check:** Every matplotlib/plotly/seaborn plot call is followed by `set_title` (or equivalent) and axis label calls.

**Exception:** None. Even exploratory heatmaps get titles.

---

## 2. No bare SQL

**Rationale:** A SQL query without a preceding explanation forces the reader to parse the SQL to understand intent. This is what notebooks exist to avoid — they exist to be narratives around code, not just code.

**Check:** Every code cell containing a SQL query has an immediately preceding markdown cell explaining the query's intent in plain English.

**Exception:** Config cells containing schema inspection queries (e.g., `DESCRIBE SELECT * FROM ...`) at the top of the notebook.

---

## 3. Findings section exists and is non-empty

**Rationale:** A notebook without findings is a pile of queries. The Findings section is where the researcher commits to what the analysis showed. If they can't commit, the notebook isn't done.

**Check:** A markdown cell with a heading containing "Findings" exists, and its content beyond the heading is non-empty. Placeholder text (`_TODO_`, `[placeholder]`, `to be filled`) counts as empty.

**Exception:** None.

---

## 4. Notebook executes end-to-end without cell errors

**Rationale:** A notebook that doesn't run is not a notebook. It's a draft.

**Check:** Every code cell in the _executed.ipynb has outputs (if it produces any), and no code cell has an output of type `error`.

**Exception:** Intentionally failing cells demonstrating an error condition must be marked with a markdown cell above explaining the demonstration, and must use a try/except to not halt the notebook.

---

## 5. Explicit NULL handling in queries

**Rationale:** Silent NULL handling is a leading cause of research miscounting. `COUNT(col)` and `COUNT(*)` differ. `col = 'x'` excludes nulls where `col IS DISTINCT FROM 'x'` includes them. Every query must make an explicit choice.

**Check:** Every SQL query against a nullable column contains one of:
- `IS NULL` or `IS NOT NULL`
- `COALESCE(...)`
- A `WHERE` clause explicitly excluding NULL rows

**Exception:** Aggregations where NULL inclusion is obvious and documented in the preceding markdown cell (rare).

---

## 6. No debug cells

**Rationale:** Debug cells are the notebook equivalent of `console.log` in production code. They signal that the notebook is still mid-construction.

**Check:** No code cells contain:
- Orphan `print(df)` or `df.head()` without a narrative purpose (bare exploratory output at end of cell)
- Only commented-out code
- `# TODO`, `# FIXME`, `# DEBUG` markers as the cell's primary content

**Exception:** Intermediate display cells that are part of a documented walkthrough (e.g., "Let's look at a sample before filtering") are allowed when the intent is narrated in a markdown cell above.

---

## 7. Every design sheet question has at least one notebook section

**Rationale:** The design sheet is the contract. If a listed question has no section addressing it, the notebook is incomplete.

**Check:** For each question in the design sheet's "Questions this answers" list, at least one notebook section addresses it.

**Exception:** None.

---

## 8. No hardcoded paths outside the config cell

**Rationale:** A notebook with paths scattered across cells is unportable and fragile. Every path belongs in one place so it can be updated in one place.

**Check:** Dataset file paths appear only in the config cell (first or second code cell). Path strings in other cells are variable references.

**Exception:** Temporary test paths inside a cell that constructs synthetic data; these must be clearly local and not reference real project files.

---

## 9. The narrative matches the data

**Rationale:** A notebook that says "most filings are 424B4" when the chart shows 58% 424B2 is worse than no notebook. The reader trusts the prose and never checks the chart.

**Check:** Frank's lane, not mechanical QC. Mechanical QC can confirm charts exist; only Frank can confirm the prose is honest about them.

**Exception:** None.

---

## Project overrides

Override any rule by copying this file to `docs/research/NOTEBOOK-INVARIANTS.md` and documenting the deviation with rationale. Frank will still check that local invariants are followed.
