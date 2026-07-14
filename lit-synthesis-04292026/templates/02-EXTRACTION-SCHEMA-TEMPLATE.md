# Extraction Schema: Per-Paper Synthesis Contract

> **Purpose:** This is the contract every `synthesis.md` must conform to. `@paper-synthesist` writes against it. `@synthesis-qc` verifies every required section is present and populated (or explicitly marked `N/A — [reason]`).

> **Conformance rule:** Every section header below MUST appear in every `synthesis.md`, in the order shown. If a section does not apply to the paper type, write `N/A — [one-line reason]` under the header. Do not omit headers.

---

## The 10 Required Sections

### 1. `header`

YAML frontmatter at the top of the document. All fields required (use `unknown` if not derivable from the paper).

```yaml
---
title: [exact title from paper]
authors: [list of author names]
year: [publication year]
venue: [journal / conference / arxiv / SSRN / preprint / internal]
identifier: [doi or arxiv id or ssrn id; "none" if preprint]
page_count: [int]
file_hash: [sha256 of source PDF — synthesist copies from metadata.json, populated there by curator]
file_path: [relative path from repo root — synthesist copies from metadata.json]
schema_variant: [academic | aurora-internal — synthesist copies from metadata.json]
synthesist_model: [model id used]
synthesis_date: [YYYY-MM-DD]
schema_hash: [hash of schema at synthesis time — synthesist copies from metadata.json]
batch_id: [batch identifier — synthesist copies from metadata.json, populated there by curator]
charter_hash: [sha256 of charter at synthesis time — synthesist copies from metadata.json]
---
```

### 2. `one_line_thesis`

A single sentence, ≤25 words, capturing what the paper claims.

> *Anti-pattern:* "This paper studies X." → Bad. Doesn't say what was found.
> *Good:* "Order-book imbalance over 100ms windows predicts the next-trade direction with 58% accuracy on Nasdaq mid-caps."

### 3. `core_claim`

The testable assertion of the paper. Distinct from thesis: the claim is what would have to be falsified to refute the paper.

```markdown
**Claim:** [the falsifiable assertion]
**Fills gap of:** [one sentence on what prior work did not address]
```

### 4. `methodology`

Three required sub-sections.

#### `data`
| Field | Value |
|-------|-------|
| Assets | [universe — tickers, instruments, exchanges] |
| Frequency | [tick / 1s / 1m / 1d / etc.] |
| Window | [start — end] |
| Source | [vendor, exchange feed, public dataset] |
| Accessibility to us | [free / paid-we-have / paid-we-could / restricted / proprietary] |

#### `approach`
Prose, 3–8 sentences. Cover: feature/signal construction, model or technique, training procedure if any. Be specific about what's novel vs. standard.

#### `validation`
| Field | Value |
|-------|-------|
| In-sample window | [dates / N obs] |
| Out-of-sample window | [dates / N obs] |
| Walk-forward | [yes / no / N folds] |
| Cross-validation | [yes / no / scheme] |
| Multiple-testing correction | [yes / no / method] |
| Cost model | [yes / no / what's modeled] |

### 5. `key_results`

Numerics with page references. Bullet list, each line has a page anchor `(p. N)`.

```markdown
- Sharpe ratio of strategy: 1.84 net of costs (p. 12)
- t-statistic on excess return: 3.41 (p. 13)
- Hit rate: 54.2% (p. 11, Table 3)
- Max drawdown: 18.7% over 2018-2020 (p. 14)
```

If no numerics (theoretical paper): write `N/A — theoretical paper, no empirical results.`

### 6. `replicability`

| Field | Value |
|-------|-------|
| Data available to us | [yes / partial — describe / no] |
| Code available | [yes — link / partial / no] |
| Reasonable to replicate | [yes / heavy-but-feasible / no — why] |
| Estimated replication effort | [hours: low / med / high] |
| Hidden dependencies | [list things the paper assumes you have, e.g., specific exchange feed, institutional cost model, proprietary news data] |

### 7. `bias_audit`

> **This section is the discriminating value of the synthesis pass.** Be skeptical. Cite page references for each finding.

| Bias | Risk level | Evidence |
|------|------------|----------|
| Look-ahead bias | [low / medium / high] | [specific evidence — e.g., "uses end-of-day adjusted prices for intraday signal (p. 8)"] |
| Survivorship bias | [low / medium / high] | [evidence — e.g., "universe is current S&P 500 constituents over 10y window (p. 6)"] |
| Overfitting signals | [low / medium / high] | [evidence — e.g., "12 hyperparameters, 3y in-sample, no holdout"] |
| Data snooping | [low / medium / high] | [evidence — e.g., "report only the best of 8 strategies tried"] |

If a bias is `low`, still write one line of evidence (e.g., "explicit point-in-time joins, no future data used").

### 8. `applicability_to_us`

Anchored to `00-RESEARCH-CHARTER.md`. Two required sub-fields.

```markdown
**Charter relevance:** [direct / adjacent / tangential / off-charter]
**Why:** [2–4 sentences linking paper claim to a charter question or stack capability. If off-charter, state which charter disqualifier applies.]
```

### 9. `novel_ideas_worth_keeping`

Bullet list of ideas, techniques, or framings worth remembering even if the paper as a whole is weak. These feed the KG and future-search recall in Phase 3.

```markdown
- [Idea 1: one sentence, with page ref]
- [Idea 2]
```

If nothing novel: write `N/A — synthesis of well-known material.`

### 10. `raw_quotes`

Up to 5 verbatim quotes, each with page reference. Used by `@synthesis-qc` as anti-hallucination ground truth and by Phase 3 KG/vector for grounding.

```markdown
> "[exact quote]" (p. N)

> "[exact quote]" (p. N)
```

---

## Schema Variants

### Variant: `academic`
All 10 sections required. Default.

### Variant: `aurora-internal`
Used for in-house GAT and outlook docs. Modifications:
- Section 3 `core_claim` — `Fills gap of:` becomes `Operational purpose:` (these aren't published research; they're internal artifacts)
- Section 7 `bias_audit` — write `N/A — internal methodology document, not empirical research` for all four biases.
- Section 8 `applicability_to_us` — instead of charter relevance, document `internal_status: [active / archived / draft]` and `owner: [team or person]`.

`@paper-synthesist` selects the variant based on `header.schema_variant`, which is set by `@corpus-curator` during inventory based on filename pattern (e.g., `Aurora_*` → `aurora-internal`).

---

## QC Conformance Rules (enforced by `@synthesis-qc`)

A `synthesis.md` PASSES QC iff:

1. All 10 section headers present in correct order.
2. `header` frontmatter parses as YAML and contains all required fields.
3. No section is silently empty — must contain content or `N/A — [reason]`.
4. `key_results` lines (if present, not N/A) each have a `(p. N)` anchor.
5. `bias_audit` table has all four rows with risk level + evidence.
6. `raw_quotes` are ≤5 in count, each with `(p. N)` anchor.
7. No bracketed placeholders (e.g., `[Sharpe ratio]`) remain in the output.
8. Word count is between 600 and 3,500 (a paper that produces a 200-word synthesis was not actually read; a 5,000-word synthesis is rambling).

Any violation → FAIL with specific issue list returned to synthesist for retry.

---

## Required Output Path

`docs/research/lit-synthesis/papers/{slug}/synthesis.md`

Slug rule (assigned by `@corpus-curator`): lowercase, alphanumeric + hyphens, derived from title, ≤60 chars, no extension. Example: `corwin-schultz-spread-estimator`.
