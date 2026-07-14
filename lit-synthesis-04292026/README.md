# Lit Synthesis Orchestration Framework

A three-phase orchestration for reading, synthesizing, scoring, and curating a corpus of research PDFs — designed for quant research literature but generalizable to any technical paper corpus.

**Version:** 04292026
**Architecture:** Agent Skills Open Standard (2026)
**Sibling of:** `spec-orchestration-03242026/`, `forge-03252026/`

---

## Purpose

Convert a directory of PDFs into a tiered, searchable, decision-ready corpus where:
- Every paper has a schema-conforming `synthesis.md` (10 required sections)
- Every paper has a `score.json` (5 axes → tier T1–T4)
- Every paper has tagged `metadata.json` from a controlled taxonomy
- The corpus has a master `INDEX.md` and a curated set of routing decisions for vector store / KG / replication notebooks

Implementation is faithful to the bias-audit discipline that distinguishes a useful quant lit review from a generic paper summary.

---

## The Three Phases

```
PHASE 1                 PHASE 2                 PHASE 3
/lit-synthesis-init  →  /lit-synthesis-run  →  /lit-synthesis-curate

Anchor docs              Per-paper loop          Tiered rollup
(charter, taxonomy,      (synthesist, QC,        (INDEX, candidates,
 schema, rubric)          scorer, classifier)     report)
```

| Phase | Command | Analog | Output |
|-------|---------|--------|--------|
| 1 | `/lit-synthesis-init` | `/spec-start` | 4 governance docs |
| 2 | `/lit-synthesis-run` | `/forge-start` | per-paper synthesis + scores + tags |
| 3 | `/lit-synthesis-curate` | (new) | tiered INDEX, notebook/KG/vector candidates |

---

## Architecture

```
                       ┌─────────────────────────────────┐
                       │   PHASE 1: /lit-synthesis-init  │
                       │   Charter interview + anchors   │
                       └─────────────┬───────────────────┘
                                     │
                                     ▼
            ┌───────────────────────────────────────────┐
            │  Anchor Docs (docs/research/lit-synthesis)│
            │  00-CHARTER  01-TAXONOMY                  │
            │  02-SCHEMA   03-RUBRIC                    │
            └───────────────────────────────────────────┘
                                     │
                                     ▼
        ┌───────────────────────────────────────────────────┐
        │       PHASE 2: /lit-synthesis-run (RESUMABLE)     │
        │                                                   │
        │   ┌──────────────┐    ┌──────────────┐            │
        │   │  @corpus-    │ →  │  @paper-     │            │
        │   │   curator    │    │  synthesist  │ (opus)     │
        │   └──────────────┘    └──────┬───────┘            │
        │                              │                    │
        │                              ▼                    │
        │                    ┌──────────────┐               │
        │                    │ @synthesis-  │               │
        │                    │      qc      │               │
        │                    └──────┬───────┘               │
        │                           │                       │
        │                           ▼                       │
        │                    ┌──────────────┐               │
        │                    │  @paper-     │               │
        │                    │   scorer     │               │
        │                    └──────┬───────┘               │
        │                           │                       │
        │                           ▼                       │
        │                    ┌──────────────┐               │
        │                    │ @taxonomy-   │               │
        │                    │  classifier  │               │
        │                    └──────────────┘               │
        └───────────────────────────────────────────────────┘
                                     │
                                     ▼
                       ┌─────────────────────────────────┐
                       │ PHASE 3: /lit-synthesis-curate  │
                       │ INDEX, candidates, report       │
                       └─────────────────────────────────┘
```

Phase 3 routing decisions feed downstream phases (deferred):
- **Notebook replication** → `/notebook-start` per T1 candidate
- **Vector store ingestion** → separate package (deferred)
- **Knowledge graph extraction** → separate package (deferred)

---

## Per-Paper Output

```
docs/research/lit-synthesis/papers/{slug}/
├── synthesis.md       # conforms to 02-EXTRACTION-SCHEMA (10 sections)
├── score.json         # 5 axes + tier + reasoning
└── metadata.json      # provenance: hash, variant, schema_hash, charter_hash, batch_id, tags, dates
```

Master rollups:
```
docs/research/lit-synthesis/
├── 00-RESEARCH-CHARTER.md      # Phase 1 — what's in scope
├── 01-TAXONOMY.md              # Phase 1 — controlled vocabulary
├── 02-EXTRACTION-SCHEMA.md     # Phase 1 — per-paper contract
├── 03-SCORING-RUBRIC.md        # Phase 1 — tier mapping rules
├── 04-CORPUS-INVENTORY.md      # Phase 2 — file/hash/status table
├── INDEX.md                    # Phase 3 — tiered, navigable
├── PROGRESS.md                 # state — read on resume
├── CORPUS-REPORT.md            # Phase 3 — human-reviewable summary
├── NOTEBOOK-CANDIDATES.md      # Phase 3 — T1 papers with rationale
├── KG-CANDIDATES.md            # Phase 3 — T1+T2 KG triage
└── VECTOR-CANDIDATES.md        # Phase 3 — T1+T2 chunk manifest
```

---

## Agents and Models

| Agent | Model | Why |
|-------|-------|-----|
| `@corpus-curator` | sonnet | Inventory work; no deep reasoning needed |
| `@paper-synthesist` | **opus** | Deepest reading pass — pays for bias audit and methodology depth |
| `@synthesis-qc` | sonnet | Mechanical conformance checks |
| `@paper-scorer` | sonnet | Reads synthesis only; rubric application |
| `@taxonomy-classifier` | sonnet | Controlled vocabulary lookup |

Opus is reserved for the synthesist because that's the one task where a sonnet pass would flatten methodology into generic summaries. Everyone else is sonnet.

---

## The Extraction Schema (10 sections)

Every `synthesis.md` must contain, in order:

1. `header` (YAML frontmatter)
2. `one_line_thesis` — ≤25 words
3. `core_claim` — falsifiable assertion
4. `methodology` — data / approach / validation sub-sections
5. `key_results` — every numeric anchored to a page
6. `replicability` — data + code + effort + hidden deps
7. `bias_audit` — 4-row table: look-ahead / survivorship / overfitting / snooping
8. `applicability_to_us` — anchored to charter
9. `novel_ideas_worth_keeping`
10. `raw_quotes` — ≤5, page-numbered

QC verifies every header is present and populated (or explicitly `N/A — [reason]`).

---

## The Scoring Rubric (5 axes → tier)

Each axis 0–5: **rigor / novelty / replicability / applicability / robustness**.

| Total | Tier | Routing |
|-------|------|---------|
| 22–25 | T1 | Replication notebook + KG + vector |
| 16–21 | T2 | KG + vector |
| 10–15 | T3 | INDEX entry only |
| 0–9 | T4 | Skim/retire |

Tier overrides:
- Off-charter (Applicability ≤ 2) → cap at T3
- High bias (look-ahead OR survivorship `high`) → cap at T2
- Aurora-internal variant → bypass to `T-Internal`
- Multi-cap composition: strictest cap wins; all triggering caps logged
- Charter mutation: when charter is edited mid-pass, prior papers' applicability scoring may be stale. QC Check Sb1 detects via `charter_hash` mismatch and routes to @paper-scorer for re-score (synthesis content unaffected).

---

## Schema Variants

- `academic` — default, all 10 sections required
- `aurora-internal` — for in-house GAT/outlook docs; bias_audit becomes canonical N/A, applicability_to_us uses `internal_status` + `internal_owner` instead of charter relevance (both populated by curator from `AURORA-ROSTER.md`)

---

## Quick Start

> ⚠️ **Install before starting the claude session.** Custom agents and commands register at session start — if you install while a claude session is already running, the new agents won't be dispatchable in that session. Always: install → start claude → run commands. If you forget, exit and restart claude.

```bash
# Install
cd /home/d-tuned/agent-orchestration-frameworks/lit-synthesis-04292026
./install.sh

# Phase 1 — set the contract
claude
/lit-synthesis-init
> [answer charter interview questions]

# Phase 2 — run the loop (resumable)
/lit-synthesis-run
# Each /lit-synthesis-run session processes ~20–30 papers before context fills. Run repeatedly across sessions; PROGRESS.md handles resume.

# Phase 3 — curate after the loop
/lit-synthesis-curate
```

Phase 2 sessions can be interrupted and resumed — `PROGRESS.md` carries the resume state.

---

## File Structure

```
lit-synthesis-04292026/
├── README.md                           # this file
├── install.sh                          # copies to ~/.claude/{agents,commands,skills}
├── agents/
│   ├── corpus-curator.md
│   ├── paper-synthesist.md
│   ├── paper-scorer.md
│   ├── taxonomy-classifier.md
│   └── synthesis-qc.md
├── commands/
│   ├── lit-synthesis-init.md
│   ├── lit-synthesis-run.md
│   └── lit-synthesis-curate.md
├── skills/
│   ├── corpus-curation/SKILL.md
│   ├── paper-synthesis/SKILL.md
│   ├── paper-scoring/SKILL.md
│   ├── taxonomy-classification/SKILL.md
│   └── synthesis-qc/SKILL.md
└── templates/
    ├── 00-RESEARCH-CHARTER-TEMPLATE.md
    ├── 01-TAXONOMY-TEMPLATE.md
    ├── 02-EXTRACTION-SCHEMA-TEMPLATE.md
    ├── 03-SCORING-RUBRIC-TEMPLATE.md
    ├── 04-CORPUS-INVENTORY-TEMPLATE.md
    ├── PAPER-SYNTHESIS-TEMPLATE.md
    ├── INDEX-TEMPLATE.md
    └── PROGRESS-TEMPLATE.md
```

---

## Design Decisions

These are intentional and documented for future maintainers.

1. **Synthesist on opus, everyone else on sonnet.** The bias audit and methodology depth justify the cost difference. A sonnet synthesist produces a generic abstract.

2. **Scorer is blind to the source PDF.** Reads only `synthesis.md`. Scores reflect what was extracted, not what the paper hoped to demonstrate. Fixes a perverse incentive where a sloppy synthesis could be rescued by a generous scorer.

3. **Schema is the structural contract; QC is the structural gate.** QC enforces conformance to the schema's *structure* (headers present, page anchors present, table rows complete, word count in band, YAML/JSON parses). QC does NOT enforce content *depth* — a bias_audit row reading "Risk: low — paper looks fine" passes S5 because the cell is non-empty. **Depth is the synthesist's responsibility.** Opus model selection on the synthesist is the depth gate; downgrade to sonnet would silently produce structurally-valid but vacuous syntheses. If you find synthesis quality drifting after a sample of 5–10 papers, the answer is to tighten the synthesist's skill (more concrete drafting examples, more red-flag triggers), not to add more QC checks — QC cannot interpret quality.

4. **Three commands, not one.** Bootstrap, loop, and curate are different rhythms. Bootstrap is a heavy human-input phase. Loop is autonomous and resumable. Curate is a one-shot rollup. Combining them obscures resume semantics.

5. **No hooks.** Like spec-orchestration and forge, this package is self-contained — orchestration discipline lives in the commands, not in `settings.json`.

6. **Aurora-internal sub-corpus is first-class.** A schema variant, not a special case bolted on. The classifier and scorer understand it natively.

7. **Phase 3 stubs are intentional.** Vector store building and KG extraction are described as candidates lists, not implemented. Their design depends on what the synthesis pass actually surfaces. Build those packages after running Phase 2 against a real corpus.

8. **"Existing Knowledge State" is state, not priors.** The charter has two sections that document current reality (capabilities we have working, background we understand cold) — explicitly NOT trust/distrust of authors or methodological schools. The synthesist consults these to frame papers "vs ours" and to write tersely about background, but never to pre-load skepticism. Pre-loaded skepticism would corrupt the bias_audit and rigor scoring; the rubric must grade the work on its own merits.

9. **Init and Curate advisors write output files directly; only Run delegates.** Phase 1 (init) and Phase 3 (curate) advisors are direct-write — they synthesize answers from the human (init) or roll up done papers (curate) into the output files themselves. Phase 2 (run) is delegation-heavy because each paper requires domain reasoning (reading the PDF, judging bias, etc.) that earns subagent overhead. Phase 1 and Phase 3 are formulaic transformations of structured input — direct write is faster and avoids handoff loss. This is a deliberate departure from the spec/forge pattern where every step delegates. If init or curate ever needs to do domain reasoning, refactor to subagent at that point.

10. **Budget tracking is heuristic, not measured.** The package estimates per-paper cost from page counts × per-token assumptions. Real API spend is not telemetered into the orchestrator. Long surveys (40+ pages) can cost 3–5× the per-paper estimate; the budget cap therefore fires *after* overspend has happened. Treat the cap as informational triage, not a hard guardrail. If exact cost matters, set the per-paper ceiling 30–50% below your true budget so the heuristic-with-overshoot lands within tolerance.

11. **Per-session paper budget: 20–30 papers.** The orchestrator's main context grows with each delegation report (~30 lines × 5 agents × 1 paper = 150 lines/paper). At ~30 papers, the orchestrator approaches usable context limits even with summarization. Plan for **5–8 sessions** to process a 150-paper corpus, each picking up via `PROGRESS.md` resume. Don't try to push one session through the whole corpus — it will silently degrade as context fills. The reconciliation step at session start is fast and idempotent.

12. **Batch tracking and drift asymmetry.** Each paper carries two curator-owned fields beyond schema_hash: `batch_id` (partition identifier — defaults to `YYYY-MM-DD-NNN` autoincrement; can be explicit like `"2026-Q2-execution"`) and `charter_hash` (sha256 of the charter at scan time). These enable two things:

    - **Incremental downstream ingest.** Vector store and KG packages can filter on `batch_id` to ingest only new papers, never re-process unchanged ones. Without this, every ingest event would either re-embed the entire corpus (expensive) or require a custom dedup mechanism per downstream package.

    - **Drift detection with asymmetric recovery.** Schema mutation (S10 check) means the structural contract changed → re-synthesize. Charter mutation (Sb1 check) means the relevance rubric changed → re-score only (synthesis content unaffected). Different routing: S10 → @corpus-curator + @paper-synthesist; Sb1 → @paper-scorer alone. The asymmetry matches reality — schema changes break extraction; charter changes only affect applicability ratings.

    `batch_id` is stamped on NEW or HASH-CHANGED papers during a curator scan. UNCHANGED papers retain their original batch_id — that's the audit trail. Curator's "Charter Hash Change Log" surfaces drifted-but-unchanged papers for human review.

    Premature in v1.0 ("we don't have a second batch yet"); essential before vector/KG ingestion ("downstream packages need partition keys from the first ingest forward"). Added in v1.2 ahead of Phase 4 implementation.

---

## References

- Spec Orchestration Framework — `spec-orchestration-03242026/`
- Forge Orchestration Framework — `forge-03252026/`
- Agent Skills Open Standard: https://agentskills.io
