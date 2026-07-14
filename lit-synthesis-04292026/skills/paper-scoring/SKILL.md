---
name: paper-scoring
description: |
  Step-by-step process for scoring a paper synthesis on five axes and assigning
  a tier. Reads ONLY synthesis.md (not the source PDF) for honest scoring.
allowed-tools: Read, Write, Glob, Grep
---

# Paper Scoring

Procedural guide for `@paper-scorer`. You read ONE `synthesis.md` and produce ONE `score.json`.

**You are blind to the source PDF.** This is intentional. Your score reflects what the synthesist captured, not what the paper hoped to demonstrate. If the synthesis is thin, the score is thin.

**CRITICAL:** Never invent numerics. Every fact in `reasoning` must be traceable to a sentence or table cell in `synthesis.md`.

---

## Step 0: Load Contract Inputs

The contract from `/lit-synthesis-run` provides:
- `SLUG`
- `SYNTHESIS_PATH` — path to the paper's `synthesis.md`
- `OUTPUT_PATH` — path to write `score.json`
- `METADATA_PATH` — path to the paper's `metadata.json` (you merge scorer-owned fields into it)

---

## Step 1: Load Rubric and Charter

Read:
1. `docs/research/lit-synthesis/03-SCORING-RUBRIC.md` — the five axes and tier mapping
2. `docs/research/lit-synthesis/00-RESEARCH-CHARTER.md` — the basis for the Applicability axis

If either is missing → HALT.

---

## Step 2: Read the Synthesis

Read the full `synthesis.md`. Note specifically:
- `header.schema_variant` — if `aurora-internal`, apply special rule (Step 6)
- `methodology.validation` — primary input for Rigor and Robustness
- `bias_audit` — primary input for Rigor; can trigger Tier override
- `key_results` — input for Robustness
- `replicability` — primary input for Replicability axis
- `applicability_to_us` — primary input for Applicability axis
- `novel_ideas_worth_keeping` and `core_claim.fills_gap_of` — primary input for Novelty

---

## Step 3: Score Each Axis (0–5)

Apply rubric criteria from `03-SCORING-RUBRIC.md` literally. For each axis:

1. Identify the synthesis evidence.
2. Match it to the closest rubric tier.
3. Write the score and the reasoning sentence (≥15 words, citing the synthesis section by name).

Scoring discipline:
- **5 is rare.** Reserve for genuinely exceptional work on that axis.
- **0 is also rare.** Most papers have some merit on most axes.
- **Default-to-3 is forbidden.** If you find yourself scoring everything 3, you are not reading the synthesis carefully. Read the rubric criteria again.
- **Ties go to lower score.** If a paper sits between 3 and 4, it gets 3.

For Robustness specifically, count the rubric's checklist items concretely — multiple regimes / multiple assets / OOS / cost-aware / hyperparameter sensitivity. Score = number satisfied.

---

## Step 4: Compute Total and Tier

```
total = rigor + novelty + replicability + applicability + robustness
```

Map to tier per `03-SCORING-RUBRIC.md`:
- 22–25 → T1
- 16–21 → T2
- 10–15 → T3
- 0–9   → T4

---

## Step 5: Apply Tier Overrides

Check rubric override rules in order. Each override applied is logged in `tier_overrides_applied`:

1. **Off-charter cap:** Applicability ≤ 2 → tier capped at T3.
2. **High-bias cap:** look-ahead OR survivorship is `high` in the synthesis bias_audit → tier capped at T2.
3. **Aurora-internal pass-through:** `header.schema_variant == aurora-internal` → tier = `T-Internal`, axes still scored for record but tier mapping bypassed.
4. **Theoretical paper rule:** if Rigor was scored 0 because the paper is theoretical, re-score Rigor using *theoretical clarity* (proof complete + assumptions explicit + results stated formally) as the proxy.

### Cap composition

When multiple caps trigger, the **strictest cap wins** — final tier = the most-strict of all applied caps. Strictness order: T1 (least strict) > T2 > T3 > T4 (strictest). Examples:

- Applicability=0, look-ahead=high → off-charter cap (T3) AND high-bias cap (T2). Final tier = T2 (stricter). Log both caps in `tier_overrides_applied`.
- Applicability=2, survivorship=high → off-charter cap (T3) AND high-bias cap (T2). Final tier = T2.
- Applicability=2, no high biases → off-charter cap only. Final tier = T3.

**Aurora-internal pass-through is not a cap.** If `header.schema_variant == aurora-internal`, tier is set to `T-Internal` regardless of any cap calculations. Caps still get logged for record but do not affect the assigned tier.

Example overrides_applied entries:
- `"off-charter-cap: applicability 1 — capped at T3"`
- `"high-bias-cap: look-ahead high — capped at T2; supersedes off-charter-cap"`
- `"composition: strictest cap = T2 (high-bias)"`

---

## Step 6: Write `score.json`

Write to `OUTPUT_PATH` exactly this structure (no extra fields, no missing fields):

```json
{
  "slug": "...",
  "scores": {
    "rigor": 0,
    "novelty": 0,
    "replicability": 0,
    "applicability": 0,
    "robustness": 0
  },
  "total": 0,
  "tier": "Tx",
  "tier_overrides_applied": [],
  "reasoning": {
    "rigor": "...",
    "novelty": "...",
    "replicability": "...",
    "applicability": "...",
    "robustness": "..."
  },
  "scored_date": "YYYY-MM-DD",
  "scorer_model": "claude-sonnet-4-6"
}
```

Every reasoning entry ≥ 15 words. Every reasoning entry cites at least one synthesis section by name.

---

## Step 6.5: Update metadata.json with Scorer Fields

After writing `score.json`:

1. Read the existing `metadata.json` at `METADATA_PATH`.
2. Merge in the scorer-owned fields:
   - `scored_date` — today's date (YYYY-MM-DD)
   - `scorer_model` — your model id (e.g., `claude-sonnet-4-7`)
3. Write the full merged object back to `METADATA_PATH`.

Fields you MUST NOT overwrite: `slug`, `title`, `authors`, `year`, `file_path`, `file_hash`,
`schema_variant`, `schema_hash`, `internal_status`, `internal_owner`, `synthesis_date`,
`synthesist_model`. Preserve `tags`, `tagged_date`, `classifier_model` if already populated
from a prior pass.

This is required for INDEX/CORPUS-REPORT renders during `/lit-synthesis-curate` — without
it, those fields stay null and downstream rollups can't trace scoring lineage.

---

## Step 7: Report

Return under 25 lines:

```
✅ SCORING COMPLETE

Slug: {slug}
Scores: rigor={N}, novelty={N}, replicability={N}, applicability={N}, robustness={N}
Total: {N}/25
Tier: {Tx}
Overrides applied: {none | list}

Score file: {OUTPUT_PATH}

Status: COMPLETE
```

---

## HALT Conditions

- Synthesis missing or unreadable
- Rubric or charter missing
- Synthesis is malformed (sections missing, schema not respected) — flag for synthesis-qc rerun rather than scoring sloppy input
- Synthesis claims facts you cannot trace to its own sections (e.g., a Sharpe ratio in `key_results` with no page anchor) — flag rather than incorporate
