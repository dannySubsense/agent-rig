# Scoring Rubric: Per-Paper Tier Assignment

> **Purpose:** Convert each `synthesis.md` into a tier (T1/T2/T3/T4) that drives downstream Phase 3 decisions (notebook, KG, vector store, retire). `@paper-scorer` reads ONLY `synthesis.md` (not the source PDF) and applies this rubric.

> **Why blind to the PDF:** The score must reflect what the synthesist actually captured, not what the paper hoped to demonstrate. If the synthesis is thin, that's a real signal — either the paper was thin or the synthesist's reading was, and either way the corpus shouldn't pretend otherwise.

---

## Five Axes (each 0–5)

### 1. Rigor (0–5)

How methodologically sound is the work?

| Score | Criteria |
|-------|----------|
| 5 | Pre-registered or pre-specified design; explicit OOS holdout; multiple-testing correction; cost model; sensitivity analysis |
| 4 | OOS holdout + cost model + acknowledged limitations; no major bias-audit red flags |
| 3 | Standard empirical practice but missing one of: OOS, costs, multi-testing |
| 2 | Significant methodological gaps (e.g., in-sample only; no costs; obvious p-hacking risk) |
| 1 | Multiple severe issues; bias audit shows high risk on 2+ axes |
| 0 | Theoretical-only with no empirical claim, OR empirical work that is fundamentally unsound |

Source from synthesis: `methodology.validation`, `bias_audit`.

### 2. Novelty (0–5)

How much does this advance vs. prior art?

| Score | Criteria |
|-------|----------|
| 5 | Introduces a genuinely new technique, dataset, or framing referenced by subsequent work |
| 4 | Meaningful extension of prior work — new asset class, new horizon, new method combination |
| 3 | Useful incremental contribution; replicates prior work in a new context |
| 2 | Mostly synthesis or re-derivation of known results |
| 1 | Reproduces well-known results without acknowledged extension |
| 0 | No identifiable novel content |

Source from synthesis: `core_claim.fills_gap_of`, `novel_ideas_worth_keeping`.

### 3. Replicability (0–5)

Could we reproduce this work in our environment?

| Score | Criteria |
|-------|----------|
| 5 | Data accessible to us + code available + low effort |
| 4 | Data accessible + medium effort, code partial or not needed |
| 3 | Data accessible + heavy effort, OR partial data |
| 2 | Data partial OR requires resources we don't have but could acquire |
| 1 | Requires data we cannot reasonably get; replication speculative |
| 0 | Replication impossible (proprietary feed, defunct dataset, dependency on private firm process) |

Source from synthesis: `replicability` (entire section).

### 4. Applicability (0–5)

How directly does this connect to the charter?

| Score | Criteria |
|-------|----------|
| 5 | Direct match to a charter question; usable in our stack today |
| 4 | Adjacent — connects to a charter question with modest translation |
| 3 | Same domain as charter but different asset/horizon; useful as background |
| 2 | Tangential — interesting context but not directly actionable |
| 1 | Off-charter on one disqualifier (e.g., wrong asset class) |
| 0 | Off-charter on multiple disqualifiers; we wouldn't deploy any of this |

Source from synthesis: `applicability_to_us.charter_relevance` and `.why`.

### 5. Robustness (0–5)

Does the result survive interrogation?

| Score | Criteria |
|-------|----------|
| 5 | Multiple regimes tested + multiple assets + OOS + cost-aware + survives sensitivity to hyperparameters |
| 4 | Three of the above |
| 3 | Two of the above (typical "good" published paper) |
| 2 | One of the above (single-regime, single-asset, single-window) |
| 1 | No robustness testing visible; result conditional on narrow setup |
| 0 | Result demonstrably fragile (synthesis flags conflicting evidence within the paper itself) |

Source from synthesis: `methodology.validation`, `key_results`, `bias_audit`.

---

## Tier Mapping

| Total (sum 0–25) | Tier | Phase 3 routing |
|------------------|------|------------------|
| 22–25 | **T1** | Replication notebook candidate; full KG ingest; vector ingest |
| 16–21 | **T2** | KG ingest; vector ingest; INDEX feature row |
| 10–15 | **T3** | Synthesis archived; INDEX entry; not indexed in vector/KG |
| 0–9 | **T4** | INDEX entry only with one-line summary; synthesis retired |

---

## Special Tier Rules

These override the numeric mapping:

1. **Off-charter cap:** if Applicability ≤ 2 → maximum tier is T3, regardless of total. (Score 0 = off-charter on multiple disqualifiers; score 1 = off-charter on one disqualifier; score 2 = tangential / borderline. None of these belong in a notebook candidate or vector/KG ingest pool.)
2. **High-bias cap:** if `bias_audit` shows `high` on look-ahead OR survivorship → maximum tier is T2, regardless of total. (Bias-flawed work cannot be a replication candidate without explicit human override.)
3. **Aurora-internal pass-through:** schema_variant = `aurora-internal` → bypass scoring, assign tier `T-Internal`. These docs aren't graded against the academic rubric.
4. **Theoretical paper:** if Rigor = 0 because theoretical-only, the scorer instead uses *theoretical clarity* (proof complete, assumptions explicit, results stated formally) as the Rigor proxy.
5. **Cap composition rule:** When multiple caps trigger (e.g., off-charter cap → T3 AND high-bias cap → T2), the final tier is the **strictest** — the lowest of all applied caps. Map T1 > T2 > T3 > T4 from least-strict to most-strict; final tier = min over caps applied. Log every triggering cap in `tier_overrides_applied` even when one supersedes another. (Aurora-internal pass-through is a routing override, not a cap; if it applies, tier is `T-Internal` regardless of other caps.)

---

## Output: `score.json`

`@paper-scorer` writes:

```json
{
  "slug": "corwin-schultz-spread-estimator",
  "scores": {
    "rigor": 4,
    "novelty": 5,
    "replicability": 5,
    "applicability": 4,
    "robustness": 4
  },
  "total": 22,
  "tier": "T1",
  "tier_overrides_applied": [],
  "reasoning": {
    "rigor": "OOS holdout 1993-2010, multi-asset, cost-aware (p.12). No multi-testing correction noted.",
    "novelty": "Closed-form spread estimator using only daily H/L — first such derivation; widely cited by subsequent microstructure work.",
    "replicability": "Daily OHLC available in any vendor; code is straightforward arithmetic. Effort: low.",
    "applicability": "Direct match to charter Q3 (microstructure signals on equity). Usable in our stack today.",
    "robustness": "Tested across multiple periods and asset universes (p.18, Table 5). Sensitivity to outlier days addressed (p.20)."
  },
  "scored_date": "YYYY-MM-DD",
  "scorer_model": "claude-sonnet-4-6"
}
```

---

## QC for Scores

`@synthesis-qc` (when also gating scores) verifies:
- All five axes scored 0–5.
- `total` = sum of axes.
- `tier` matches mapping unless `tier_overrides_applied` lists a triggering rule.
- `reasoning` has one entry per axis, each ≥ 15 words, citing synthesis sections.
- Scorer never invented numerics — every cited fact in `reasoning` traceable to `synthesis.md`.
