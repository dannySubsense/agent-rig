---
name: notebook-qc
description: |
  Step-by-step mechanical QC of an executed notebook against design sheet + invariants.
  Checklist-driven. No judgment — that's Frank's lane.
allowed-tools: Read, Bash, Glob, Grep
---

# Notebook QC (Mechanical)

Procedural guide for verifying an executed notebook against its design sheet and the project invariants.

## Goal

Produce a structured PASS/FAIL report. Every check is mechanical — either the notebook satisfies a rule or it doesn't. No "mostly good." No partial credit.

Your job is *not* to evaluate whether the notebook is insightful, well-written, or scientifically valid. That's Frank's lane. You check structure, invariants, and design sheet coverage.

---

## Review Mode: MECHANICAL

Prerequisites before you run:
- @notebook-executor reports: CLEAN
- _executed.ipynb exists and is valid JSON

If prerequisites not met → HALT, return to Notebook Advisor.

Time budget: 5-10 minutes. Focus on the checklist, nothing else.

---

## Step 1: Verify Prerequisites

```bash
# Executed notebook exists
test -f "$EXECUTED_PATH" || HALT "Executed notebook missing"

# Valid JSON
python3 -c "import json; json.load(open('$EXECUTED_PATH'))" || HALT "Not valid JSON"

# Executor report says CLEAN
grep "EXECUTION CLEAN" "$EXECUTOR_REPORT" || HALT "Executor did not report CLEAN"
```

## Step 2: Load the Contract

- `DESIGN_SHEET_PATH` — the approved design sheet
- `EXECUTED_PATH` — the _executed.ipynb
- `INVARIANTS_PATH` — project-local `NOTEBOOK-INVARIANTS.md` or `~/.claude/templates/NOTEBOOK-INVARIANTS.md`

## Step 3: Load All Three Documents

```
cat "$DESIGN_SHEET_PATH"
cat "$INVARIANTS_PATH"
# For the notebook, parse the JSON to extract cells
```

## Step 4: Design Sheet Coverage

### Section-by-section

Extract the Sections outline from the design sheet. For each section, verify it exists in the notebook as a markdown header cell with matching numbering and name.

```python
import json
nb = json.load(open("$EXECUTED_PATH"))
headers = [
    c["source"][0].strip() if isinstance(c["source"], list) else c["source"].strip()
    for c in nb["cells"]
    if c["cell_type"] == "markdown" and (
        (isinstance(c["source"], list) and c["source"] and c["source"][0].startswith("#"))
        or (isinstance(c["source"], str) and c["source"].startswith("#"))
    )
]
```

Check each design-sheet section number appears in `headers` (with matching name).

### Question coverage

Extract the "Questions this answers" list from the design sheet. For each question, verify the notebook addresses it somewhere. Simple test: does the notebook contain cells (code or markdown) that reference the subject of the question?

Not a string match — a conceptual mapping. Read each section's content and map to question(s). If a question has no mapping, FAIL.

### "Done when" criterion

Check that the notebook body addresses the Done-when criterion somewhere. Usually in the Findings section or a closing cell.

## Step 5: Invariant Compliance

For each invariant listed in the invariants doc, verify compliance:

### Chart title + axis labels (invariant #1)

Parse code cells for matplotlib/plotly calls. For each chart:
- `ax.set_title` or `plt.title` present
- `ax.set_xlabel` + `ax.set_ylabel` present (or equivalent for the charting library)

```bash
# Quick heuristic — count plot calls vs title/label calls in code cells
python3 <<EOF
import json
nb = json.load(open("$EXECUTED_PATH"))
code_source = "\n".join("".join(c["source"]) if isinstance(c["source"], list) else c["source"]
                       for c in nb["cells"] if c["cell_type"] == "code")
plot_calls = code_source.count(".plot(") + code_source.count("plt.plot") + code_source.count(".hist(") + code_source.count(".bar(")
titles = code_source.count("set_title") + code_source.count("plt.title")
xlabels = code_source.count("set_xlabel") + code_source.count("plt.xlabel")
ylabels = code_source.count("set_ylabel") + code_source.count("plt.ylabel")
print(f"plot_calls={plot_calls} titles={titles} xlabels={xlabels} ylabels={ylabels}")
EOF
```

If `plot_calls > titles` or `plot_calls > xlabels` or `plot_calls > ylabels`, FAIL with specific cells listed.

### SQL intent comments (invariant #2)

For each code cell containing SQL (detect via `.execute(` with triple-quoted string, or `SELECT` / `FROM` keywords), verify the preceding cell is a markdown cell with text explaining the query.

### Findings section non-empty (invariant #3)

Find the markdown cell titled "Findings" (or similar). Verify:
- It contains content beyond the heading
- Content is not placeholder text like `_TODO_`, `[placeholder]`, `to be filled`

### No execution errors (invariant #4)

```python
errors = [
    (i, c) for i, c in enumerate(nb["cells"])
    if c["cell_type"] == "code"
    and any(o.get("output_type") == "error" for o in c.get("outputs", []))
]
assert len(errors) == 0, f"Cells with errors: {[i for i, _ in errors]}"
```

Executor should have caught this, but verify anyway.

### Explicit NULL handling (invariant #5)

For each SQL query (cells containing `SELECT`), verify at least one of:
- `IS NULL` or `IS NOT NULL`
- `COALESCE(`
- A `WHERE` clause that filters nulls

If a query touches a nullable column and has none of these, FAIL with the cell index.

### No debug cells (invariant #6)

Scan code cells for:
- Orphan `print(...)` without a narrative purpose (heuristic: `print(df)`, `print(df.head())` at end of cell with no surrounding context)
- Cells containing only commented-out code
- Cells with `# TODO`, `# FIXME`, `# DEBUG` as the cell content

### Design sheet question mapping (invariant #7)

Already checked in Step 4.

### No hardcoded paths (invariant #8)

Grep code cells for string literals that look like paths (contain `/` or end in `.parquet`, `.duckdb`, `.csv`, `.json`) *outside* the config cell (first or second code cell). If found outside config, FAIL with cell index.

## Step 6: Structural Check

- [ ] Notebook is valid JSON (already verified in Step 1)
- [ ] First cell is a markdown cell with a title (`#` heading)
- [ ] First or second code cell is a config cell (contains path assignments)
- [ ] Last markdown cell is a Findings section

## Step 7: Generate the Report

```
═══════════════════════════════════════════════════════════════════
NOTEBOOK QC REPORT — [NN_name]
═══════════════════════════════════════════════════════════════════

DESIGN SHEET COVERAGE
[✅/❌] All sections present
   [list any missing with design sheet section number]
[✅/❌] All questions addressed
   [list any unaddressed question with its text]
[✅/❌] "Done when" criterion addressed

INVARIANTS CHECK
[✅/❌] Chart title + axis labels       [if ❌: specific cells]
[✅/❌] SQL intent markdown above       [if ❌: specific cells]
[✅/❌] Findings section non-empty      [if ❌: what was found]
[✅/❌] No execution errors             [if ❌: which cells]
[✅/❌] Explicit NULL handling          [if ❌: which queries]
[✅/❌] No debug cells                  [if ❌: which cells]
[✅/❌] No hardcoded paths              [if ❌: which cells]

STRUCTURAL CHECK
[✅/❌] Valid JSON
[✅/❌] Title cell at top
[✅/❌] Config cell near top
[✅/❌] Findings section at end

═══════════════════════════════════════════════════════════════════
VERDICT: PASS | FAIL

[If FAIL:]
Issues requiring fix:
1. [Specific violation with cell index or section]
2. [...]

Route fixes to: @notebook-builder
═══════════════════════════════════════════════════════════════════
```

## Verdict Rules

**PASS** only if:
- ALL design sheet sections present
- ALL questions addressed
- ALL invariants satisfied
- ALL structural checks pass

**FAIL** if ANY violation found. No partial credit. No "mostly good."

If PASS, hand to @frank. If FAIL, back to @notebook-builder with specific fix list.

---

## HALT Conditions

HALT if:
- Design sheet missing
- Invariants doc missing (both project-local and template)
- Executed notebook missing
- Executed notebook not valid JSON (escalate — executor should have caught this)
