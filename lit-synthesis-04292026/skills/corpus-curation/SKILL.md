---
name: corpus-curation
description: |
  Step-by-step process for inventorying a PDF corpus, hashing files, assigning
  slugs, detecting duplicates, and maintaining processing status.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Corpus Curation

Procedural guide for the curator. The curator owns `04-CORPUS-INVENTORY.md` and `PROGRESS.md` counters. It does NOT read paper content.

**CRITICAL:** Replace ALL bracketed placeholders with concrete values. Never write placeholder text to inventory.

---

## Contract Inputs

The curator accepts these inputs from the orchestrator:

- `mode` — `full_scan` (default) | `refresh`
- `BATCH_ID` (optional) — explicit batch identifier (e.g., `"2026-Q2-execution"`). If omitted, auto-generated as `{YYYY-MM-DD}-{NNN}` where NNN is the next available 3-digit suffix for today's date (read inventory's existing batch_ids, find the max NNN for today, add 1; default to 001 if none).

`BATCH_ID` is stamped on every NEW or HASH-CHANGED paper during this scan. UNCHANGED papers retain their original batch_id.

---

## Step 1: Load Charter

Read `docs/research/lit-synthesis/00-RESEARCH-CHARTER.md`. Extract:
- Corpus root path (e.g., `quant-rick/alpha-index/quant-research/`)
- Sub-corpora rules (filename patterns → schema_variant)
- Sources excluded

If charter missing → HALT.

---

## Step 2: Scan Corpus

```bash
find {CORPUS_ROOT} -maxdepth 1 -type f -name "*.pdf" | sort
```

For non-PDF files in the corpus dir, log to `Skipped Papers` table with reason.

---

## Step 3: Hash Each PDF

```bash
sha256sum {CORPUS_ROOT}/*.pdf
```

Persist full hash; display first 8 chars in inventory table.

---

## Step 4: Assign Slugs

For each PDF:

1. Extract title from filename (strip `.pdf`, normalize spaces).
2. Lowercase, replace non-alphanumeric with `-`, collapse multiple `-`, strip leading/trailing `-`, truncate to 60 chars.
3. Check inventory for existing slug.
   - If slug not present → use it.
   - If present and hash matches → skip (already known).
   - If present and hash differs → log to `Hash Change Log`, reset status to `pending`.
   - If present (different file, same slug) → suffix `-2`, `-3`, etc. Log to `Slug Collision Log`.

Slug examples:
- `A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices.pdf`
  → `a-simple-way-to-estimate-bid-ask-spreads-from-daily-high-and-low`
- `Aurora Outlook A Case for American Industrial Exceptionalism.pdf`
  → `aurora-outlook-a-case-for-american-industrial-exceptionalism`

---

## Step 5: Assign Schema Variant

Apply charter sub-corpora rules. Default: `academic`.

Default rules (override from charter if specified):
- Filename starts with `Aurora_` (case-insensitive, literal underscore prefix) → `aurora-internal`
- Filename matches `* (GAT)*` (paren-required, NOT bare GAT substring) → `aurora-internal`
- Otherwise → `academic`

> **Why paren-required:** A bare `*GAT*` substring rule case-insensitively matches academic
> filenames containing "investiGATion", "miGATion", "litiGATion", etc. Paren-required avoids
> these false positives. Internal docs reliably use the ` (GAT) ` convention.

---

## Step 6: Update Inventory

Read existing `04-CORPUS-INVENTORY.md`. For each PDF, upsert a row:

| Slug | Title | File | Hash | Variant | Batch | Status | Tier | Last update |

Status decision tree:
- New file → `pending`
- Existing slug, same hash → leave status as-is
- Existing slug, hash changed → `pending` (re-process)

Update `Last scan`, `File count`, `New since last scan`, `Removed since last scan` headers.

For files in inventory but no longer on disk: do NOT delete the row; mark status `failed` with reason `source_pdf_missing` so a human can decide.

---

## Step 6.5: Write Per-Paper metadata.json

For each paper that is new or hash-changed, create or refresh the per-paper metadata file at:

```
docs/research/lit-synthesis/papers/{slug}/metadata.json
```

Create the paper directory if it does not exist:

```bash
mkdir -p docs/research/lit-synthesis/papers/{slug}
```

Compute `schema_hash` (truncated to 16 hex chars for readability):

```bash
sha256sum docs/research/lit-synthesis/02-EXTRACTION-SCHEMA.md | cut -c1-16
```

Prefix with `sha256:` — e.g., `sha256:1a2b3c4d5e6f7a8b`.

Compute `charter_hash` (truncated to 16 hex chars):

```bash
sha256sum docs/research/lit-synthesis/00-RESEARCH-CHARTER.md | cut -c1-16
```

Prefix with `sha256:` — e.g., `sha256:a1b2c3d4e5f6a7b8`.

Resolve `BATCH_ID`:
- If contract provided BATCH_ID → use verbatim.
- If not → read existing inventory; find max `NNN` suffix among today's `YYYY-MM-DD-NNN` batch_ids; default `BATCH_ID = {YYYY-MM-DD}-{NNN+1}` (or `{YYYY-MM-DD}-001` if no prior scans today).

**If metadata.json does not exist**, create it with curator-owned fields populated and all
downstream fields at their null/empty defaults:

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
  "charter_hash": "sha256:a1b2c3d4e5f6a7b8",
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

**If metadata.json already exists** (e.g., from a prior pass where downstream agents have
already populated title, tags, etc.):
- Read the existing file.
- Update ONLY the curator-owned fields: `slug`, `file_path`, `file_hash`, `schema_variant`,
  `schema_hash`, `charter_hash`, `internal_status`, `internal_owner`.
- `batch_id` is updated ONLY for NEW or HASH-CHANGED papers (preserves the original batch_id
  for unchanged papers — that's the per-batch audit trail).
- Write the merged object back.
- Never set `title`, `authors`, `year`, `tags`, `synthesis_date`, `scored_date`,
  `tagged_date`, `synthesist_model`, `scorer_model`, `classifier_model` — those are
  downstream-agent territory.

**aurora-internal variant:**

For aurora-internal variant papers:
1. Read `docs/research/lit-synthesis/AURORA-ROSTER.md`.
2. Find the row for this slug (column "Slug").
3. If found: copy `Status` to `metadata.internal_status`, `Owner` to `metadata.internal_owner`.
4. If not found:
   - Write `internal_status: "unknown"` and `internal_owner: "unknown"` to metadata.json.
   - Append a row to AURORA-ROSTER.md under "Unrostered Slugs": `{slug} | {today} | needs human entry`.
   - Continue (do not HALT — human can backfill before /lit-synthesis-run processes the paper).

For non-aurora-internal papers, both `internal_status` and `internal_owner` stay `null`.

Set `schema_variant: "aurora-internal"` for aurora-internal papers.

**Scope:** only run Step 6.5 for papers that are new or hash-changed. Skip papers whose
hash is unchanged — their metadata.json is already correct for curator fields.

---

## Step 6.6: Charter-Hash Drift Detection

For every UNCHANGED paper in inventory (existing slug, same file_hash):

1. Read its existing `metadata.charter_hash`.
2. Compare against the current `charter_hash` you computed in Step 6.5.
3. If different (charter mutated since this paper was processed): log to a new "Charter Hash Change Log" section at the bottom of `04-CORPUS-INVENTORY.md`:

```markdown
## Charter Hash Change Log

When the curator detects an existing slug whose charter_hash no longer matches the current charter, it logs here. This signals that the paper's applicability scoring may be stale; QC's Check Sb1 will surface this and route to @paper-scorer for re-score (NOT re-synthesize — synthesis content is unaffected by charter changes).

| Slug | Old charter_hash | New charter_hash | Detected | Recommended action |
|------|------------------|------------------|----------|--------------------|
| {slug} | {old} | {new} | {YYYY-MM-DD} | re-score (charter applicability may be stale) |
```

Do NOT auto-update `charter_hash` on these papers. Let QC detect and route. Preserves audit trail.

---

## Step 7: Update PROGRESS.md Counters

Recompute `Total papers`, `Pending`, `Done`, `Failed`, `Skipped` from inventory and write to `PROGRESS.md`.

---

## Step 8: Report

Return under 30 lines:

```
✅ CURATION COMPLETE

Corpus: {root}
Total: N papers
New: N
Removed: N
Hash-changed: N
Skipped: N (non-PDF or rule-excluded)
Slug collisions: N
batch_id: {BATCH_ID used this scan}
charter_hash: {sha256:...}
charter-drifted slugs (existing papers, charter changed): {N}

Variants:
- academic: N
- aurora-internal: N

Inventory updated: docs/research/lit-synthesis/04-CORPUS-INVENTORY.md
Progress updated: docs/research/lit-synthesis/PROGRESS.md

Status: COMPLETE
```

---

## Resume Mode

When called by `/lit-synthesis-run` mid-pass to refresh counters only (no rescan):

1. Skip Steps 2–6.
2. Read inventory, recompute counters, update PROGRESS.md.
3. Report counter delta only.

Caller specifies `mode: refresh` in the contract.

---

## HALT Conditions

- Charter missing or corpus root invalid
- Cannot read PDF dir (permissions)
- Inventory file is malformed (cannot parse table)
- Hash collision on different filename (extremely unlikely; flag for human)
