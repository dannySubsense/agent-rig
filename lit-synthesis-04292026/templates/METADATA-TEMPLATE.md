# Per-Paper Metadata Contract

> **Single source of provenance per paper.** Every paper in the corpus has exactly one
> `metadata.json` file. It is created by `@corpus-curator`, progressively extended by
> downstream agents, and never overwritten by a non-owning agent.

---

## File Location

```
docs/research/lit-synthesis/papers/{slug}/metadata.json
```

One file per slug. The slug is assigned by `@corpus-curator` during inventory.

---

## Locked Schema

```json
{
  "slug": "...",
  "title": null,
  "authors": [],
  "year": null,
  "file_path": "...",
  "file_hash": "sha256:...",
  "schema_variant": "academic",
  "schema_hash": "sha256:...",
  "batch_id": "...",
  "charter_hash": "sha256:...",
  "internal_status": null,
  "internal_owner": null,
  "tags": [],
  "tagged_date": null,
  "synthesis_date": null,
  "scored_date": null,
  "synthesist_model": null,
  "scorer_model": null,
  "classifier_model": null
}
```

Do NOT add or remove fields without a schema revision across all agents and templates.

---

## Field Ownership Table

| Field | Owner | Written when |
|-------|-------|-------------|
| `slug` | `@corpus-curator` | On scan |
| `file_path` | `@corpus-curator` | On scan |
| `file_hash` | `@corpus-curator` | On scan (sha256 of source PDF) |
| `schema_variant` | `@corpus-curator` | On scan (`academic` or `aurora-internal`) |
| `schema_hash` | `@corpus-curator` | On scan (sha256 of `02-EXTRACTION-SCHEMA.md`, truncated to 16 hex chars) |
| `batch_id` | `@corpus-curator` | On scan (per-batch identifier; default `{YYYY-MM-DD}-{NNN}` autoincrement) |
| `charter_hash` | `@corpus-curator` | On scan (sha256 of `00-RESEARCH-CHARTER.md`, truncated to 16 hex chars) |
| `internal_status` | `@corpus-curator` | On scan for aurora-internal variant (Slice 4 wires roster lookup) |
| `internal_owner` | `@corpus-curator` | On scan for aurora-internal variant (Slice 4 wires roster lookup) |
| `title` | `@paper-synthesist` | On synthesis completion |
| `authors` | `@paper-synthesist` | On synthesis completion |
| `year` | `@paper-synthesist` | On synthesis completion |
| `synthesis_date` | `@paper-synthesist` | On synthesis completion |
| `synthesist_model` | `@paper-synthesist` | On synthesis completion |
| `scored_date` | `@paper-scorer` | On score completion |
| `scorer_model` | `@paper-scorer` | On score completion |
| `tags` | `@taxonomy-classifier` | On tagging |
| `tagged_date` | `@taxonomy-classifier` | On tagging |
| `classifier_model` | `@taxonomy-classifier` | On tagging |

---

## Update Lifecycle

```
@corpus-curator  (scan)
   └── Creates metadata.json with curator-owned fields
       slug, file_path, file_hash, schema_variant, schema_hash, charter_hash,
       batch_id, internal_status, internal_owner
       All downstream fields: null or []

@paper-synthesist  (synthesis)
   └── Reads metadata.json, copies file_hash / schema_variant / schema_hash
       into synthesis.md frontmatter.
       Merges into metadata.json:
       title, authors, year, synthesis_date, synthesist_model
       NEVER overwrites curator fields.

@paper-scorer  (scoring)
   └── Merges into metadata.json:
       scored_date, scorer_model
       NEVER overwrites curator or synthesist fields.

@taxonomy-classifier  (tagging)
   └── Merges into metadata.json:
       tags, tagged_date, classifier_model
       NEVER overwrites curator, synthesist, or scorer fields.
```

---

## Merge Rule (all non-curator agents)

1. Read the existing `metadata.json`.
2. Update ONLY the fields you own (see ownership table).
3. Write the full merged object back to the file.
4. Never set a field you do not own to `null` or `[]` — preserve whatever value is there.

---

## Example: Curator-populated state (post-scan, pre-synthesis)

```json
{
  "slug": "corwin-schultz-spread-estimator",
  "title": null,
  "authors": [],
  "year": null,
  "file_path": "quant-rick/alpha-index/quant-research/Corwin Schultz Spread Estimator.pdf",
  "file_hash": "sha256:a3f8c12e9b74d056e1c2f3a4b5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
  "schema_variant": "academic",
  "schema_hash": "sha256:1a2b3c4d5e6f7a8b",
  "batch_id": "2026-04-29-001",
  "charter_hash": "sha256:abcd1234ef567890",
  "internal_status": null,
  "internal_owner": null,
  "tags": [],
  "tagged_date": null,
  "synthesis_date": null,
  "scored_date": null,
  "synthesist_model": null,
  "scorer_model": null,
  "classifier_model": null
}
```

## Example: Fully-populated state (post-classification)

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
  "batch_id": "2026-04-29-001",
  "charter_hash": "sha256:abcd1234ef567890",
  "internal_status": null,
  "internal_owner": null,
  "tags": [
    {
      "tag": "microstructure/spread-estimation",
      "evidence": "Paper derives a closed-form bid-ask spread estimator from daily H/L prices."
    },
    {
      "tag": "asset/equity",
      "evidence": "Tested on US equity universe 1993-2010."
    },
    {
      "tag": "quality/empirical",
      "evidence": "Reports backtested estimator accuracy on real equity data with OOS validation."
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

## HALT Conditions for Downstream Agents

- If `metadata.json` is **missing** when a downstream agent needs it → HALT. The file must be
  created by `@corpus-curator` before any other agent runs on this slug.
- If `file_hash` is `"pending"` or `null` when `@paper-synthesist` reads it → HALT and request
  orchestrator to re-run `@corpus-curator` on this slug.
- If `tags` is populated but `tagged_date` is null → data integrity issue; flag for human review.
- If `batch_id` is null when a downstream agent reads it → HALT and request curator re-run.
- If `charter_hash` mismatch detected by QC's Sb1 → route to @paper-scorer for re-score (synthesis content stays valid; only applicability axis is re-evaluated).
