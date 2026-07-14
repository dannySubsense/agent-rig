---
name: taxonomy-classification
description: |
  Step-by-step process for assigning controlled-vocabulary tags to a paper
  synthesis from the corpus taxonomy. Records evidence per tag.
allowed-tools: Read, Write, Glob, Grep
---

# Taxonomy Classification

Procedural guide for `@taxonomy-classifier`. You read ONE `synthesis.md`, consult `01-TAXONOMY.md`, and produce a tags entry written to the paper's `metadata.json`.

**Tag discipline:** every tag must be defensible from the synthesis. You record one evidence sentence per tag.

---

## Step 0: Load Contract Inputs

- `SLUG`
- `SYNTHESIS_PATH`
- `METADATA_PATH` — the paper's `metadata.json`, already created by `@corpus-curator` and
  extended by `@paper-synthesist`. It exists at this point in the pipeline. You merge your
  classifier-owned fields (`tags`, `tagged_date`, `classifier_model`) into it.

---

## Step 1: Load Taxonomy

Read `docs/research/lit-synthesis/01-TAXONOMY.md`. Build a mental list of available tags. New tags are NOT permitted — if a paper does not fit, follow Step 5.

---

## Step 2: Read Synthesis

Read the full `synthesis.md`. Pay attention to:
- `header.schema_variant` — internal docs use `internal/*` tags
- `core_claim` and `one_line_thesis` — primary domain and method
- `methodology.data` — asset class and frequency
- `methodology.approach` — ML method (if any)

---

## Step 3: Apply Tagging Rules

Per `01-TAXONOMY.md`:

1. **Mandatory tags for academic papers:**
   - At least one `domain/*` tag (microstructure, execution, alpha, regime)
   - At least one `asset/*` tag
   - Exactly one `quality/*` tag (replication-study, survey, theoretical, empirical, dataset-paper)

2. **Mandatory tags for aurora-internal:**
   - At least one `internal/*` tag
   - Domain and asset tags optional but encouraged

3. **Optional:**
   - `freq/*` — only if frequency is explicit
   - `ml/*` — only if a specific ML method is the primary technique
   - Multiple `domain/*` tags allowed and encouraged for cross-domain work

4. **Evidence required per tag:** record one synthesis sentence (paraphrased OK if too long) that justifies the tag.

---

## Step 4: Write Tags to `metadata.json`

`metadata.json` EXISTS at this point — it was created by `@corpus-curator` and extended by
`@paper-synthesist`. If the file is missing, HALT immediately: orchestration is broken and
this slug must be re-run from the curator step.

Read the existing `metadata.json`. Merge YOUR fields (`tags`, `tagged_date`,
`classifier_model`) into it. Write the full merged object back. Never overwrite curator
fields (`slug`, `file_path`, `file_hash`, `schema_variant`, `schema_hash`,
`internal_status`, `internal_owner`) or synthesist fields (`title`, `authors`, `year`,
`synthesis_date`, `synthesist_model`).

The final structure after your merge will look like:
```json
{
  "slug": "corwin-schultz-spread-estimator",
  "title": "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices",
  "authors": ["Corwin, Shane A.", "Schultz, Paul"],
  "year": 2012,
  "file_path": "quant-rick/alpha-index/quant-research/Corwin Schultz Spread Estimator.pdf",
  "file_hash": "sha256:a3f8c12e9b74d056e1c2f3a4b5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
  "schema_variant": "academic",
  "schema_hash": "sha256:1a2b3c4d5e6f7a8b",
  "internal_status": null,
  "internal_owner": null,
  "tags": [
    {
      "tag": "microstructure/spread-estimation",
      "evidence": "Paper derives a closed-form bid-ask spread estimator from daily H/L (one_line_thesis)."
    },
    {
      "tag": "asset/equity",
      "evidence": "Tested on US equity universe 1993-2010 (methodology.data)."
    },
    {
      "tag": "quality/empirical",
      "evidence": "Reports backtested estimator accuracy on real equity data with OOS validation (methodology.validation)."
    }
  ],
  "tagged_date": "2026-04-29",
  "synthesis_date": "2026-04-29",
  "scored_date": "2026-04-29",
  "synthesist_model": "claude-opus-4-5",
  "scorer_model": "claude-sonnet-4-6",
  "classifier_model": "claude-sonnet-4-6"
}
```

---

## Step 5: Handling No-Fit Cases

If the paper does not fit any leaf in a relevant `domain/*`, do NOT invent a tag. Instead:

1. Assign whatever mandatory tags do fit (at minimum `asset/*` and `quality/*`).
2. HALT with a structured request to update `01-TAXONOMY.md`:

```
❌ TAXONOMY GAP

Slug: {slug}
Concept observed: {short description}
Closest existing tag: {nearest tag, or "none"}
Proposed new tag: {suggestion} — {one-line definition}
Evidence: {synthesis sentence}

Action needed: human approval to add tag, then re-run classifier.
```

The orchestrator records the HALT and either appends to taxonomy (with human approval) or accepts a closest-fit tag.

---

## Step 6: Report

Return under 20 lines:

```
✅ CLASSIFICATION COMPLETE

Slug: {slug}
Tags assigned: {count}
- {tag-1}
- {tag-2}
- ...

metadata.json: {METADATA_PATH}

Status: COMPLETE
```

---

## HALT Conditions

- Synthesis missing or unreadable
- Taxonomy file missing
- No existing tag fits in a relevant domain (request taxonomy update — see Step 5)
- Mandatory tag categories cannot be filled (e.g., asset class not derivable)
