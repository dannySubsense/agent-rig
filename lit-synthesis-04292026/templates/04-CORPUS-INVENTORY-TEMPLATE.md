# Corpus Inventory

> **Owner:** `@corpus-curator`. Auto-generated on first run of `/lit-synthesis-run`. Updated on every paper status change. Humans should not edit by hand — re-run the curator to refresh.

> **Purpose:** Single source of truth for which papers exist, their slugs, hashes (for change detection), schema variant, and processing status. Drives resume behavior.

---

## Source

**Corpus root:** [populated by curator from CHARTER]
**Last scan:** [YYYY-MM-DDTHH:MM:SSZ]
**File count:** [N PDFs]
**New since last scan:** [N]
**Removed since last scan:** [N]

---

## Inventory Table

| Slug | Title (truncated) | File | Hash (first 8) | Variant | Batch | Status | Tier | Last update |
|------|-------------------|------|----------------|---------|-------|--------|------|-------------|
| corwin-schultz-spread-estimator | A Simple Way to Estimate Bid-Ask Spreads… | A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices.pdf | a3f9b2c1 | academic | 2026-04-29-001 | done | T1 | 2026-04-29 |
| | | | | | pending | — | — |

**Status values:**
- `pending` — discovered, not yet processed
- `in_progress` — synthesist running (or interrupted mid-paper; resume picks these up first)
- `synthesis_done` — synthesis.md written, awaiting QC
- `qc_failed` — QC found issues; retry pending (with `retry_count` in metadata)
- `qc_passed` — synthesis QC passed, awaiting scoring
- `done` — synthesis + score + classification complete
- `failed` — exhausted retries; needs human review (logged below)
- `skipped` — explicitly excluded by curator (e.g., duplicate, non-PDF, sub-corpus excluded)

---

## Failed Papers (require human review)

| Slug | Reason | Last error | Retries |
|------|--------|------------|---------|
| | | | |

---

## Skipped Papers

| Filename | Reason |
|----------|--------|
| | |

---

## Slug Collision Log

When two papers would produce the same slug, the curator suffixes with `-2`, `-3`, etc. and logs:

| Slug | Files |
|------|-------|
| | |

---

## Hash Change Log

When the curator detects an existing slug whose hash has changed (PDF replaced), it logs here and resets status to `pending` so the paper is re-synthesized:

| Slug | Old hash | New hash | Detected | Action |
|------|----------|----------|----------|--------|
| | | | | |
