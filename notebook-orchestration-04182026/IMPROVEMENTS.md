# Notebook Orchestration — Improvements Log

Observed imperfections and planned enhancements to the framework, discovered through use.

Kept in the package (rather than in a project's `docs/decisions/`) so the log travels with the framework on re-install.

Entry format:
```
## YYYY-MM-DD — [title]
**Observed during:** [context]
**What happened:** [terse fact]
**Root cause:** [best current guess, or "unknown"]
**Impact:** [low/medium/high + one-line consequence]
**Planned fix:** [specific change, or "deferred"]
**Status:** [open / in-progress / resolved / won't-fix]
```

---

## 2026-04-18 — notebook-builder self-reports incorrect cell counts

**Observed during:** First framework test run — building notebook 01 (`01_dataset_sanity_check`) for the gap-lens-dilution-filter backtest corpus.

**What happened:** After the final targeted-edit pass, `@notebook-builder` reported in its status output: "Cells: 34 total (17 code, 17 markdown)". The actual file on disk had 44 cells (17 code, 27 markdown). The on-disk file was structurally correct and passed all downstream gates. Only the report was wrong. Same agent had inconsistent counts on earlier passes in the same session (first build reported "44 (19 code, 19 markdown)" vs actual "44 (17 code, 27 markdown)").

**Root cause:** Unknown. Best guess: the builder counted cells at a mid-edit intermediate state (after deletes but before inserts, or by reading its own in-memory edit plan rather than the final file). The `notebook-build` skill does not currently require the builder to re-parse the written file for its status report.

**Impact:** Low. The report is informational — downstream agents (executor, QC) read the actual file from disk and were unaffected. But an inaccurate self-report can mislead the orchestrator in cases where it uses the count to make branching decisions, and it undermines trust in agent reports in general.

**Planned fix:** Update the `notebook-build` skill to require the builder to re-read and parse the written file as its final step, computing the reported counts from the on-disk content. Add a self-check assertion: "report counts match `len(json.load(open(path))['cells'])`".

**Status:** Open.

---
