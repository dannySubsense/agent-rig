# Taxonomy: [Corpus Name]

> **Purpose:** Controlled vocabulary for tagging every paper. `@taxonomy-classifier` may only assign tags from this list. New tags require updating this document and re-running the classifier on prior papers.

---

## Tag Format

`{domain}/{subdomain}` — papers may carry multiple tags across domains.

Each leaf tag has a one-line definition. If a paper does not fit any leaf, the classifier flags it for taxonomy update rather than inventing a tag.

---

## Domain: market-microstructure

- `microstructure/spread-estimation` — Roll, Corwin-Schultz, Abdi-Ranaldo, etc.
- `microstructure/order-flow` — order-book imbalance, flow toxicity, VPIN
- `microstructure/price-impact` — Kyle, Almgren-Chriss derivatives, propagator models
- `microstructure/liquidity` — Amihud, Kyle's lambda, depth measures
- `microstructure/bar-construction` — information bars, dollar bars, imbalance bars

## Domain: execution

- `execution/vwap` — VWAP scheduling, deviation control
- `execution/twap` — time-weighted execution
- `execution/optimal-liquidation` — Almgren-Chriss family, multi-period execution
- `execution/rl-execution` — RL-based execution agents
- `execution/market-making` — quoting, inventory management

## Domain: alpha

- `alpha/momentum` — time-series and cross-sectional momentum
- `alpha/mean-reversion` — short-horizon reversal
- `alpha/stat-arb` — pairs, baskets, cointegration
- `alpha/factor` — Fama-French, BAB, quality, carry
- `alpha/cross-asset` — cross-momentum, lead-lag
- `alpha/event-driven` — earnings, news, announcements

## Domain: regime

- `regime/hmm` — hidden Markov regime models
- `regime/clustering` — Wasserstein, k-means, DBSCAN regime ID
- `regime/changepoint` — Bayesian changepoint, CUSUM
- `regime/volatility` — GARCH-family, realized vol regimes

## Domain: ml-method

- `ml/rl` — reinforcement learning (any application)
- `ml/deep` — deep learning architectures (CNN, LSTM, Transformer)
- `ml/gnn` — graph neural nets
- `ml/tree` — tree ensembles, gradient boosting
- `ml/probabilistic` — Bayesian, HMM (when used as ML method, not regime)
- `ml/labeling` — triple-barrier, meta-labeling, labeling discipline

## Domain: asset-class

- `asset/equity` — stocks, equity indices
- `asset/futures` — equity futures, commodity futures
- `asset/options` — options, vol surfaces
- `asset/fx` — currencies
- `asset/crypto-spot` — crypto cash markets
- `asset/crypto-derivs` — perps, dated futures, options on crypto
- `asset/fixed-income` — bonds, rates
- `asset/commodity` — physical commodities, energy

## Domain: frequency

- `freq/hft` — sub-second
- `freq/intraday` — seconds to hours
- `freq/daily` — daily bars
- `freq/lower` — weekly+

## Domain: methodology-quality

- `quality/replication-study` — paper replicates or refutes prior work
- `quality/survey` — literature survey, no original empirical work
- `quality/theoretical` — proof / model, no empirical validation
- `quality/empirical` — original empirical work
- `quality/dataset-paper` — primary contribution is a dataset

## Domain: corpus-internal

> *Tags reserved for in-house documents — Aurora and other internal research.*

- `internal/aurora-gat` — Aurora GAT methodology docs
- `internal/aurora-outlook` — Aurora market commentary
- `internal/methodology` — internal research methodology notes

---

## Tagging Rules

1. **Minimum:** every paper must carry at least one `domain/*` tag and one `asset/*` tag (or `internal/*` if in-house).
2. **Maximum:** no hard cap, but tags must be defensible from the synthesis. Classifier records evidence sentence per tag in `metadata.json`.
3. **Frequency tag** is optional — only assign if the paper explicitly addresses a frequency or implies one through data choice.
4. **Quality tag** is mandatory — every paper gets exactly one `quality/*`.

---

## When to Update This Taxonomy

`@taxonomy-classifier` HALTs and requests update when:
- A paper does not fit any leaf in a relevant domain.
- The same novel concept appears in 3+ papers without a tag.

Tag additions are logged at the bottom of this file with date and triggering paper.

---

## Tag Additions Log

| Date | Tag added | Triggering paper |
|------|-----------|------------------|
| | | |
