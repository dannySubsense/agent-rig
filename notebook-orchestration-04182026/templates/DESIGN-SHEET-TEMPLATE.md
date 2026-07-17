# Notebook NN: Name — Design Sheet

**Status:** Draft | Approved
**Date:** YYYY-MM-DD
**Author(s):**

---

## Purpose

*1-2 sentences. What this notebook is for. Why it exists. Not "what it does" — "why."*

Example:
> Make each setup_type A–E comprehensible with real examples. Every Tier 2 notebook depends on the play vocabulary being clear — this is where we make it clear.

---

## Questions this answers

*Bulleted list. Concrete. Answerable from the dataset. 3-8 questions. Each one becomes at least one notebook section.*

- Example: What filings characterize setup_type A (SHELF_TAKEDOWN)?
- Example: Who are the top 10 institutional actors in each setup?
- Example: What form types dominate each setup, and how stable is that over time?

---

## Sections

*Hierarchical outline, matching the convention reference if one was provided.*

Example:
```
1. Setup A — SHELF_TAKEDOWN
   1.1  Definition and plain-English description
   1.2  Characteristic filings (3 real examples with tickers, dates, EDGAR links)
   1.3  Institutional actors most commonly involved
   1.4  Form type distribution

2. Setup B — ...
   2.1  ...

...

6. Findings
```

---

## Data sources

*Exact paths. No wildcards.*

Example:
```
- docs/research/data/backtest_results.parquet
- docs/research/data/backtest_participants.parquet
- /home/d-tuned/market_data/duckdb/market_data.duckdb
  - raw_symbols_massive (for ticker → company name lookup)
```

---

## Expected outputs

*What the reader walks away with. Concrete artifacts.*

Example:
- For each setup_type: plain-English definition, 3 example filings (ticker + date + EDGAR link), top-10 actors table, form type distribution bar chart
- Summary table: setup_type counts, pass rates, median filing size
- Findings section populated with 3-5 observations

---

## Done when

*A single unambiguous sentence. The criterion that tells us this notebook is complete.*

Example:
> A reader unfamiliar with the pipeline can, after reading this notebook, describe each setup_type and recognize it in a new filing.

---

## References

- Planning doc: `docs/research/planning/notebook-roadmap.md`
- Pipeline spec: `docs/research/backtest-pipeline/`
- Convention reference (if any): `/home/d-tuned/market_data/notebooks/01_eod_explorer.ipynb`
- Relevant hypotheses: `docs/research/HYPOTHESIS.md` (e.g., H1a, H1b)

---

## Human approval

**Approved by:** [name]
**Date:** YYYY-MM-DD
**Notes:** [any adjustments from initial draft]
