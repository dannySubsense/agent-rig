# Research Charter: [Corpus Name]

> **Purpose of this document:** Define what this corpus is *for*. Every per-paper synthesis is judged against the charter — a methodologically perfect paper that has nothing to do with our work scores low on `applicability_to_us`. The charter is what "applicability" means.

---

## Stack & Style

**Asset classes we trade or could trade:**
- [e.g., US equities, equity futures, crypto spot, crypto perps, …]

**Trading style(s):**
- [e.g., systematic intraday, swing, statistical arbitrage, market making, execution optimization, …]

**Time horizons of interest:**
- [e.g., sub-second / seconds / minutes / hours / days / weeks]

**Infrastructure we have:**
- [e.g., DuckDB warehouse, FMP data, internal feature store, Python research env, no live execution venue yet, …]

**Infrastructure we do NOT have (papers requiring this score lower on replicability):**
- [e.g., colocation, L3 order book feeds, options chain history, alternative data subscriptions, …]

---

## Questions This Corpus Should Help Us Answer

Each question becomes a *recall lens* against which papers are filtered later. Be specific.

1. [e.g., "Which microstructure signals are most predictive of short-horizon equity returns and survive after-cost?"]
2. [e.g., "What execution algorithms minimize implementation shortfall in crypto perps?"]
3. [e.g., "How do regime-detection methods compare on SPX intraday data?"]
4. [...]

---

## What Disqualifies a Paper as Relevant

Papers matching these are scored at low `applicability_to_us` *regardless of methodological quality*. Synthesist still extracts; scorer still rates rigor — but applicability is capped.

- [e.g., requires data we do not and cannot have (L3 NASDAQ ITCH, alternative data feeds, …)]
- [e.g., asset classes we never plan to trade]
- [e.g., horizons we cannot operate at given infra]
- [e.g., theoretical-only with no empirical or operational implication]

---

## Corpus Boundary

**Sources included:**
- [e.g., `quant-rick/alpha-index/quant-research/*.pdf`]

**Sources excluded:**
- [e.g., textbooks, blog posts, slide decks unless flagged]

**Sub-corpora (different schema variant or special handling):**
- [e.g., `Aurora_*` — internal GAT docs, use schema variant `aurora-internal`]

---

## Existing Knowledge State

> **Purpose:** Encode what we already have working and what we already understand cold. This is **state**, not **priors** — we're documenting current reality so the synthesist can frame papers relative to it. We deliberately do NOT encode trust/distrust of authors or methodological schools (those would corrupt the bias audit).

### Section A: What We Already Have Working

Internal signals, models, strategies, or infrastructure that is live, in research, or in production. The synthesist consults this when drafting a paper's `novel_ideas_worth_keeping` and `applicability_to_us` — proposing similar work gets framed as **"vs ours"** rather than as absolute novelty.

| Capability | Status | Description | Owner |
|------------|--------|-------------|-------|
| [e.g., Daily cross-sectional momentum on US equities] | [production / research / prototype] | [one-line description] | [team / individual] |
| [e.g., VWAP execution for crypto perps] | | | |
| [e.g., HMM regime classifier on SPX] | | | |

If empty: write `None — greenfield research stack.` Do not leave the section blank.

### Section B: Background We Don't Need Re-Explained

Topics, frameworks, or standard techniques we already understand cold. The synthesist consults this when drafting `methodology.approach` — when a paper builds on Section B background, the synthesist may write tersely (e.g., "standard Almgren-Chriss formulation" rather than three sentences re-deriving it). This saves tokens and tightens syntheses without dumbing-down the work.

```
- [e.g., Almgren-Chriss execution math]
- [e.g., Standard ML pipeline (CV, train/test split, regularization, holdout)]
- [e.g., Roll spread estimator]
- [e.g., Amihud illiquidity, Kyle's lambda]
- [e.g., GARCH family for vol modeling]
- [e.g., Standard factor models (Fama-French, BAB, momentum)]
```

If empty: write `None — synthesist should explain all background fully.` Do not leave the section blank.

> **What does NOT belong here:**
> - Author or school distrust ("we don't trust Lopez de Prado's labeling claims")
> - Methodological skepticism not anchored in operational state
> - Aspirational positions ("we believe overfitting is the main risk in alpha research")
>
> Those are priors, not state. The rubric already evaluates rigor and bias_audit independently — pre-loading skepticism corrupts that evaluation.

---

## Synthesis Pass Constraints

| Constraint | Value |
|------------|-------|
| Approximate corpus size | [e.g., 150 papers] |
| Synthesist model | opus |
| Scorer model | sonnet |
| Per-paper budget ceiling | [e.g., $1.50] |
| Total pass budget ceiling | [e.g., $250] |
| Wall-clock target | [e.g., 2 sessions × 4h] |
| Halt threshold (per-paper retries) | 2 |

---

## Downstream Decisions Driven by This Pass

Tier outcomes from `03-SCORING-RUBRIC.md` route as follows:

- **T1 (≥22)** → flagged for replication notebook (Phase 4 candidate)
- **T2 (16–21)** → ingested into vector store + KG
- **T3 (10–15)** → synthesis archived, INDEX entry only
- **T4 (<10)** → skim noted, retired

---

## Approval

- [ ] Charter reviewed by human
- [ ] Stack and style accurately reflect current and near-future state
- [ ] Disqualifying conditions are honest (not aspirational)
- [ ] Existing Knowledge State Section A reflects current capabilities, not roadmap
- [ ] Existing Knowledge State Section B does NOT contain author or school priors
- [ ] Budget ceilings agreed

Charter version: 1.0
Approved date: [YYYY-MM-DD]
