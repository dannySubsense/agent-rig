---
description: |
  Phase 3 — Post-synthesis curation. Builds tiered INDEX, identifies notebook
  candidates, surfaces vector-store and KG ingest candidates, and produces a
  human-reviewable corpus report.
---

# Lit Synthesis — Curate Mode

You are the **Lit Synthesis Curate Advisor**, producing the final corpus rollup once all papers (or a substantial majority) have been processed by `/lit-synthesis-run`.

This is where the corpus stops being a list of files and becomes a navigable, decision-ready knowledge artifact.

---

## Pre-Conditions

Before running:
- `04-CORPUS-INVENTORY.md` exists with at least N papers in `done` status
- `PROGRESS.md` shows pending count is small (default: <5% of total) OR human explicitly says "curate what we have"

If pending > 5%, ask the human:
> "PROGRESS shows {N} pending papers. Curate what we have, or run more synthesis first?"

---

## Outputs

| File | Purpose |
|------|---------|
| `docs/research/lit-synthesis/INDEX.md` | Master tiered index, sortable, navigable |
| `docs/research/lit-synthesis/CORPUS-REPORT.md` | One-time human-reviewable summary |
| `docs/research/lit-synthesis/NOTEBOOK-CANDIDATES.md` | T1 papers + recommendation rationale |
| `docs/research/lit-synthesis/KG-CANDIDATES.md` | T1+T2 papers earmarked for KG ingestion |
| `docs/research/lit-synthesis/VECTOR-CANDIDATES.md` | T1+T2 papers earmarked for vector store |

---

## Sequence

### Step 1: Refresh Counters

DELEGATE `@corpus-curator` with `mode: refresh` to recompute PROGRESS counters and verify inventory state.

### Step 2: Load All `done` Papers

For each `done` row in inventory, read:
- `papers/{slug}/synthesis.md` (header + applicability_to_us only — don't reread the full body)
- `papers/{slug}/score.json`
- `papers/{slug}/metadata.json`

Build an in-memory table: slug, title, year, tier, scores, tags, applicability_relevance, batch_id, charter_hash.

### Step 3: Build INDEX.md

Use `~/.claude/templates/lit-synthesis/INDEX-TEMPLATE.md` as the structural starting point.

For each tier section (T1, T2, T3, T4, T-Internal):
- Sort by `total` score descending within tier
- Populate row: slug, title (link to synthesis.md), authors (first + et al), year, score (NN/25), tags (top 3), notes (override flag if any)

For "By Tag" sections at bottom: group all papers by their `domain/*` tag. List slug — title — tier under each.

**Also add a "By Batch" section** at the bottom of INDEX.md:

For each unique `batch_id` in the corpus (in chronological order — sort by the date prefix of the batch_id, or by min(synthesis_date) within batch as tiebreaker):

```markdown
### Batch: {batch_id}

Papers added in this batch: {N}

Tier breakdown:
- T1: {count} ({slugs})
- T2: {count} ({slugs})
- T3: {count}
- T4: {count}
- T-Internal: {count}

Charter version (charter_hash): {sha256:...}
```

This makes batches first-class navigable. Useful when reviewing "what did we get from the Q3 ingest" or auditing "which papers were scored under which charter version."

Update `Summary Counts` at top.

Write to `docs/research/lit-synthesis/INDEX.md`.

### Step 4: Build NOTEBOOK-CANDIDATES.md

For each T1 paper, write a one-paragraph recommendation:

```markdown
## {slug} — {title}

**Score:** {N}/25 | **Tier:** T1 | **Tags:** {tags}

**Why this is a notebook candidate:**
{2-3 sentences synthesizing rigor + replicability + applicability — directly drawn from
score.json reasoning fields and synthesis.md applicability_to_us.}

**Replication effort:** {low | medium | high — from synthesis.md replicability section}
**Data we need:** {from synthesis.md methodology.data}
**Hidden dependencies:** {from synthesis.md replicability.hidden_dependencies}

**Suggested notebook scope:**
- [Verbatim or near-verbatim from key_results — what would be the OOS replication target?]
- [Robustness extension if natural — different regime, different asset]
```

Sort T1 papers by `applicability` axis score (highest first), then by `total`.

Append at end:
```markdown
## Recommended order for /notebook-start sessions

1. {slug} — {short rationale}
2. ...
```

### Step 5: Build KG-CANDIDATES.md

List T1 + T2 papers with their tags (these are the ones whose entities/relations should populate the KG).

For each: extract the candidate entities/relations from `core_claim` and `novel_ideas_worth_keeping`. Format as a checklist for a future `@kg-extractor` agent (deferred — not implemented in this package).

```markdown
## {slug}

Suggested entities:
- [entity type]: [entity value]

Suggested relations:
- [subject] — [predicate] — [object]
```

Keep this lightweight — the goal is a triage list, not the actual KG.

### Step 6: Build VECTOR-CANDIDATES.md

List T1 + T2 papers with chunking guidance (paragraph from `methodology.approach`, page-anchored quotes from `raw_quotes`, the entire `synthesis.md`). Format as a manifest a future `@vector-prep` agent could consume.

### Step 7: Build CORPUS-REPORT.md

Human-reviewable summary, one page or so:

```markdown
# Corpus Synthesis Report

**Pass complete:** {date}
**Papers synthesized:** {N}
**Total budget spent:** ${X}

## Tier Distribution
{table from INDEX summary}

## What we have
- {tier T1 count} papers worth replicating
- {tier T2 count} papers worth indexing
- {by-tag highlights — top 5 tags by count}

## Notable findings
- {3-5 bullets — e.g., "12 papers on RL execution; tier-1 candidates concentrated in 2018-2022"}
- {bias audit summary — "{N}/{total} papers flagged with high look-ahead or survivorship bias"}

## Gaps
- {tags with zero papers in T1}
- {charter questions with no T1+T2 coverage — flagged for future literature search}

## Recommended next phases
1. Vector store ingestion — see VECTOR-CANDIDATES.md ({N} papers)
2. KG ingestion — see KG-CANDIDATES.md ({N} papers)
3. Notebook replications — see NOTEBOOK-CANDIDATES.md ({N} candidates, prioritized)

## Quality of the synthesis pass
- QC pass rate: {N}% first-attempt
- Synthesist retry rate: {pct}
- Failed papers: {N} (see inventory `Failed` table)

## Per-Batch Breakdown

For each batch in the corpus:

| Batch | Papers | T1 | T2 | T3 | T4 | T-Internal | Charter (hash) |
|-------|--------|----|----|----|----|------------|----------------|
| {batch_id_1} | {N} | {n} | {n} | {n} | {n} | {n} | {sha256:...} |
| {batch_id_2} | {N} | {n} | {n} | {n} | {n} | {n} | {sha256:...} |

**Charter drift across batches:** {if all charter_hashes match → "no drift"; else list the divergent batches and recommend running re-score on the affected papers via QC's Sb1 routing}.

**Batch-aligned recommendations:**
- For incremental vector store ingest: process batches sequentially; use `batch_id` filter to scope each ingestion call.
- For incremental KG overlay: same — `batch_id` is the partition key.
- For audit ("what did we know as of {date}?"): filter on batches with `synthesis_date ≤ {date}`.
```

### Step 8: Human Approval Gate

```
═══════════════════════════════════════════════════════════════════
LIT SYNTHESIS CURATE — APPROVAL GATE
═══════════════════════════════════════════════════════════════════

Files written:
✅ INDEX.md
✅ CORPUS-REPORT.md
✅ NOTEBOOK-CANDIDATES.md ({N} T1 papers)
✅ KG-CANDIDATES.md ({N} T1+T2 papers)
✅ VECTOR-CANDIDATES.md ({N} T1+T2 papers)

Tier distribution:
T1: {N} | T2: {N} | T3: {N} | T4: {N} | T-Internal: {N}

Batches in corpus: {list of batch_ids}
Charter drift: {none | yes — see CORPUS-REPORT}

Top T1 by applicability:
1. {slug} — {one line}
2. {slug} — {one line}
3. {slug} — {one line}

═══════════════════════════════════════════════════════════════════

Review the CORPUS-REPORT first. Then NOTEBOOK-CANDIDATES.

When ready:
- "Approved" → curate complete; corpus is ready for Phase 4 decisions
- "Adjust X" → I'll route the change

Phase 4 candidates:
- Build vector store from VECTOR-CANDIDATES (deferred — separate command)
- Build KG from KG-CANDIDATES (deferred — separate command)
- Pick notebook-replication targets from NOTEBOOK-CANDIDATES → /notebook-start per paper
═══════════════════════════════════════════════════════════════════
```

Wait for approval.

---

## HALT Conditions

- Pending count is too high and human did not approve "curate what we have"
- Inventory or governance docs missing
- A `done` paper has missing artifacts (synthesis.md, score.json, or metadata.json) — flag for `/lit-synthesis-run` rerun on that slug
- Tier overrides applied across many papers in inconsistent ways — flag for human review of rubric
