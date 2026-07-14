---
name: paper-synthesis
description: |
  Step-by-step process for reading a single research PDF and producing a
  schema-conforming synthesis.md. Pacing for long PDFs (sectional reads),
  variant handling, and self-check before handoff.
allowed-tools: Read, Write, Glob, Grep
---

# Paper Synthesis

Procedural guide for `@paper-synthesist`. You read ONE paper at a time and produce ONE `synthesis.md` conforming to `02-EXTRACTION-SCHEMA.md`.

**You are the deepest reading pass in the pipeline.** A sonnet-grade summary is not acceptable here. Every section earns the opus token cost by reading the paper, not abstracting it.

**CRITICAL:** Replace ALL bracketed placeholders. Never write placeholder text. Never invent numerics. If a fact is not in the paper, write `unknown` or `N/A — [reason]`.

---

## Step 0: Load Contract Inputs

The contract from `/lit-synthesis-run` provides:
- `SLUG`
- `PDF_PATH` (absolute)
- `SCHEMA_VARIANT` (`academic` | `aurora-internal`)
- `OUTPUT_PATH` (absolute, target `synthesis.md`)
- `METADATA_PATH` — path to the paper's `metadata.json` (curator-populated; you merge your fields into it)
- `RETRY_NOTES` (optional — specific QC failure feedback to address)

Verify the PDF exists and is readable before proceeding.

---

## Step 1: Load Schema and Charter

Read these — they define what you must produce and what relevance means:
1. `docs/research/lit-synthesis/02-EXTRACTION-SCHEMA.md`
2. `docs/research/lit-synthesis/00-RESEARCH-CHARTER.md`

If either is missing → HALT.

### Step 1a: Load metadata.json

Read `METADATA_PATH` (the paper's `metadata.json`).

Extract: `file_hash`, `schema_variant`, `schema_hash`, `batch_id`, `charter_hash`.

For aurora-internal variant: also extract `internal_status` and `internal_owner` from metadata.json. These come from the curator's roster lookup. Do NOT attempt to extract them from the PDF itself.

**HALT condition:** if the file does not exist, or if `file_hash` is `null` or `"pending"`,
or if `batch_id` is `null`, HALT immediately with the message:

```
HALTED — metadata.json not curator-populated (missing file_hash or batch_id);
request orchestrator to re-run @corpus-curator on slug: {SLUG}
```

Do not proceed to Step 2 until metadata.json exists with a real `file_hash` value.

**Pay specific attention to charter sections:**
- **Stack & Style + Questions** — anchors for `applicability_to_us`
- **Existing Knowledge State Section A (What We Already Have Working)** — frame `novel_ideas_worth_keeping` and `applicability_to_us` *relative to ours*, not as absolute novelty. If a paper proposes something the team already runs, the framing is "vs ours" — does the paper's approach beat or extend what we have?
- **Existing Knowledge State Section B (Background We Don't Need Re-Explained)** — when the paper's `methodology.approach` builds on Section B background, write tersely. "Standard Almgren-Chriss formulation" is acceptable; re-deriving the formula in your synthesis is not.
- **Disqualifiers** — drives `applicability_to_us` cap (off-charter → applicability score floor)

---

## Step 2: First Pass — Structural Scan

Read first 5 pages of the PDF using the `pages` parameter:
```
Read(file_path=PDF_PATH, pages="1-5")
```

Extract:
- Title (verbatim)
- Authors
- Abstract (full)
- Year, venue, identifier (DOI / arxiv id) — usually in header/footer or first page
- Page count (read paper structure: scan TOC if present, or last page reference)

Note paper organization: standard sections (Intro / Lit Review / Methodology / Data / Results / Conclusion) or non-standard (theoretical, survey, dataset paper).

---

## Step 3: Determine Paper Type

Classify the paper:
- **Empirical** — Has data, runs models or strategies, reports numerics
- **Theoretical** — Proves results, derives formulas, no empirical claim
- **Survey** — Reviews and synthesizes prior work, no new data/results
- **Dataset paper** — Primary contribution is a dataset
- **Mixed** — Combination

This determines which sections of the schema have real content vs. `N/A`.

---

## Step 4: Sectional Deep Reads

PDFs over 10 pages MUST be read in chunks via `pages`. Plan reads:

For empirical paper (typical):
1. Methodology section — `pages="X-Y"` covering data + features + model + validation
2. Results section — `pages="X-Y"` covering key numerics, tables, figures
3. Conclusion + limitations — last 2–3 pages
4. Appendix sections referenced from methodology — as needed

Take notes during each read. Specifically capture:
- **Page references for every numeric.** If you cannot anchor a number to a page, do not include it.
- **Verbatim phrases for raw_quotes.** Mark each with page.
- **Bias-audit signals.** Watch for: "we use the current S&P 500 index" (survivorship), "adjusted close" for intraday (look-ahead), "we tried X strategies" (data snooping), "Table 4 shows the best parameter combination" (overfitting), absence of out-of-sample period, absence of cost model.

---

## Step 5: Section-by-Section Drafting

> ⚠️ **HEADER NAMING — read this before drafting.**
>
> The schema template at `02-EXTRACTION-SCHEMA.md` uses `### 1. header`, `### 2. one_line_thesis`, etc. as DOCUMENTATION-format H3 enumeration. **These are NOT the literal target syntax for your output.**
>
> Your `synthesis.md` body sections must use **bare canonical H2 headers, no numeric prefix**:
>
> ```
> ## one_line_thesis
> ## core_claim
> ## methodology
> ### data
> ### approach
> ### validation
> ## key_results
> ## replicability
> ## bias_audit
> ## applicability_to_us
> ## novel_ideas_worth_keeping
> ## raw_quotes
> ```
>
> There is **NO `## header` body section.** The `header` is the YAML frontmatter at the top of the file (between `---` delimiters). Do not emit a `## header` body section.
>
> QC's Check S1 fails on numbered prefixes or extra `## header` sections. Get this right on the first pass — retries are expensive.

Open `02-EXTRACTION-SCHEMA.md` and draft each section in order.

**First, branch on `SCHEMA_VARIANT` (loaded in Step 1a):**

- If `SCHEMA_VARIANT == "academic"` → use the canonical formats below for sections 3, 7, 8. This is the default path.
- If `SCHEMA_VARIANT == "aurora-internal"` → use the **Aurora-internal Variant Formats** subsection below (after section 10's drafting guidance) for sections 3, 7, 8. Sections 1, 2, 4, 5, 6, 9, 10 use the canonical formats.

Do NOT draft a section in the wrong format and rely on QC to catch it. The variant branch is an upfront decision, not a post-hoc correction.

Drafting discipline:

### `header`
Populate from Step 2. Use today's date for `synthesis_date`. Copy `file_hash`, `schema_variant`, `file_path`, `schema_hash`, `batch_id`, and `charter_hash` from `metadata.json` (loaded in Step 1a) — these are the curator's fields. Never override them and never write `pending` for `file_hash`.

The complete YAML frontmatter must include:
- title, authors, year, venue, identifier, page_count (synthesist-derived from PDF)
- file_hash, file_path, schema_variant, schema_hash, batch_id, charter_hash (copied from metadata.json)
- synthesist_model, synthesis_date (synthesist-set)

### `one_line_thesis`
≤25 words. The single most informative sentence. Words count.

### `core_claim`
Distinguish thesis (description) from claim (falsifiable assertion). The claim is the thing that, if shown false, would refute the paper.

### `methodology.data`
Be exhaustive on accessibility — flag if any data is proprietary, retired, or expensive.

### `methodology.approach`
3–8 sentences. If novel: explicitly call out novelty. If standard: name the prior method (e.g., "standard Almgren-Chriss execution with quadratic transaction costs").

**Charter Section B integration:** if the paper's approach builds on background listed in charter Section B, write tersely. Example: instead of three sentences explaining cross-validation methodology, write "uses standard 5-fold CV (Section B background)." Do NOT lecture the reader on material the team already understands cold. This is not summarization sloppiness — it is calibration.

### `methodology.validation`
This table is where look-ahead and overfitting risks live. If the paper does not report a field, write `not reported` (not `unknown` — the difference matters: not-reported is a yellow flag).

### `key_results`
Every line must have `(p. N)`. If a paper has 50 numbers, choose the 5–10 that the abstract or conclusion highlights. Quality > quantity.

### `replicability`
Be honest. If we cannot get the data, say so. If the paper requires colocation we don't have, say so.

### `bias_audit`
Score each of four biases low / medium / high. Provide evidence even when low. The evidence sentence is what matters — humans skim the table, but rely on the evidence.

Common red flags (do NOT auto-mark high without checking):
- Sample period 2009–2019 with results assumed to generalize → ask: does the bias_audit acknowledge regime narrowness? If not, overfitting risk is at least medium.
- "We use the current index constituents" → survivorship at least medium, often high.
- "We use daily close prices to predict intraday returns" → look-ahead high.
- "Of the strategies considered, we report the best performer" without correction → snooping high.

### `applicability_to_us`
Quote a charter question or stack capability. Don't paraphrase the charter — link directly to it.

**Aurora-internal `applicability_to_us` fields:** `internal_status` and `internal_owner` come from metadata.json (curator-populated from AURORA-ROSTER). Use these verbatim — do not invent. If either is `unknown`, write the section as:

> **internal_status:** unknown — slug not in roster; awaiting human entry
> **internal_owner:** unknown — slug not in roster; awaiting human entry

This is acceptable for the synthesis to PASS QC, but it is a yellow flag that the human must resolve before curate phase.

**Charter Section A integration:** if the paper proposes a capability the team already has working (per Section A), the `Why` field MUST include a "vs ours" comparison. Examples:
- "Paper proposes daily cross-sectional momentum on US equities, which we run in production (Section A). Paper extends with [specific factor / cost model / asset]. Worth comparing OOS."
- "Paper's RL execution agent overlaps with our prototype (Section A). Paper improves [aspect]; lacks [aspect we have]."
- "Paper's approach is essentially what we already deploy — no novel contribution vs. our current implementation."

### `novel_ideas_worth_keeping`
Even a methodologically weak paper can have a useful idea. Capture it. If nothing: explicit `N/A — synthesis of well-known material`.

**Charter Section A integration:** novelty is judged *relative to our state*, not absolute. An idea that's "novel in the literature" but already implemented in Section A is NOT novel to us — note that explicitly. An idea that's incremental in the literature but extends a Section A capability in a useful direction IS worth keeping.

### `raw_quotes`
≤5 quotes, verbatim, page-numbered. Choose quotes that ground the most important claims (the thing a reader would want to verify).

---

### Aurora-internal Variant Formats

> Use these formats for sections 3, 7, 8 ONLY when `SCHEMA_VARIANT == "aurora-internal"`. All other sections use canonical formats.

#### Section 3 (`core_claim`) — aurora-internal format

Internal docs do not "fill a gap of prior work" — they have an operational purpose. Use:

```markdown
**Claim:** [the operational assertion the doc makes]
**Operational purpose:** [why this doc exists; what decision it informs or what process it documents]
```

(NOT `Fills gap of:` — that's the academic-variant phrasing.)

#### Section 7 (`bias_audit`) — aurora-internal format

Internal methodology docs are not empirical research. The bias audit is canonically `N/A`:

```markdown
N/A — internal methodology document, not empirical research.
```

Do NOT include the 4-row bias table for aurora-internal. The single-line `N/A` statement is the entire section.

#### Section 8 (`applicability_to_us`) — aurora-internal format

Instead of charter relevance, document operational state. Both fields come from `metadata.json` (curator-populated from `AURORA-ROSTER.md` per Slice 4). Use verbatim — do not extract from PDF:

```markdown
**internal_status:** [active | archived | draft | superseded | unknown]
**internal_owner:** [team or individual; or 'unknown' if not in roster]
**Operational notes:** [2-3 sentences synthesizing the doc's role in current operations, drawn from doc content + roster Notes column if present]
```

If both `internal_status` and `internal_owner` are `unknown` (slug not in roster), the format is still required — write the values verbatim. QC's S9 will emit a soft warning surfacing the missing roster entry; this does not block the cycle.

---

### Sections 1, 2, 4, 5, 6, 9, 10 for aurora-internal

Use canonical formats from above. Specific notes:

- **Section 1 (header):** `schema_variant: aurora-internal` (set by curator); other fields the same.
- **Section 2 (one_line_thesis):** still ≤25 words; describe what the doc says/does, not what was "found."
- **Section 4 (methodology):** internal docs may not have data/approach/validation in the empirical-research sense. Acceptable to fill with descriptive prose of the doc's structure: e.g., `data: N/A — internal methodology doc; describes process not empirical study`. The three sub-sections must still be present (per Check S3); each can be `N/A — [reason]`.
- **Section 5 (key_results):** `N/A — internal doc, no empirical results to enumerate` is acceptable.
- **Section 6 (replicability):** `N/A — internal doc, replicability not applicable in academic sense` OR document whether the *process* described is reproducible internally.
- **Section 9 (novel_ideas_worth_keeping):** still extract anything novel about the methodology or framing.
- **Section 10 (raw_quotes):** still ≤5 verbatim quotes with page refs (or `N/A` if doc has no page numbers).

---

## Step 6: Self-Check Against Schema

Before writing, run through the QC conformance rules from `02-EXTRACTION-SCHEMA.md`:

- [ ] **Variant branch was applied** — sections 3, 7, 8 use the format matching `SCHEMA_VARIANT`. Academic vs aurora-internal use different formats; mixing them = QC FAIL on S9.
- [ ] All 10 section headers present in correct order
- [ ] `header` YAML parses and has all required fields
- [ ] No section silently empty
- [ ] All `key_results` lines have `(p. N)` anchors
- [ ] `bias_audit` has all four bias rows with risk + evidence
- [ ] `raw_quotes` ≤5, all with `(p. N)`
- [ ] No bracketed placeholders remain
- [ ] Word count between 600 and 3,500
- [ ] YAML frontmatter includes `batch_id` and `charter_hash` (copied from metadata.json, not invented)

If any fail, fix before writing.

---

## Step 7: Write Output

Write the full synthesis to `OUTPUT_PATH`.

---

## Step 7.5: Update metadata.json with Synthesist Fields

After writing `synthesis.md`:

1. Read the existing `metadata.json` at `METADATA_PATH`.
2. Merge in the synthesist-owned fields:
   - `title` — exact title from paper (as extracted in Step 2)
   - `authors` — list of author names
   - `year` — publication year (integer)
   - `synthesis_date` — today's date (YYYY-MM-DD)
   - `synthesist_model` — your model id (e.g., `claude-opus-4-5`)
3. Write the full merged object back to `METADATA_PATH`.

Fields you MUST NOT overwrite: `slug`, `file_path`, `file_hash`, `schema_variant`,
`schema_hash`, `batch_id`, `charter_hash`, `internal_status`, `internal_owner`. Preserve any
values already written by other downstream agents (`tags`, `tagged_date`, `classifier_model`,
`scored_date`, `scorer_model`).

---

## Step 8: Report

Return under 40 lines:

```
✅ SYNTHESIS COMPLETE

Slug: {slug}
File: {OUTPUT_PATH}
Variant: {variant}
Variant branch applied: yes — sections 3/7/8 in {academic | aurora-internal} format
Paper type: {empirical | theoretical | survey | ...}

Word count: {N}
Sections populated: 10/10 (or 10/10 with M N/A)
Page refs cited: {N}
Quotes: {N}/5

Bias audit summary:
- Look-ahead: {low/med/high}
- Survivorship: {low/med/high}
- Overfitting: {low/med/high}
- Snooping: {low/med/high}

Notes for scorer/QC: {any synthesist concerns about edge cases}

Status: COMPLETE
```

---

## Retry Mode

If `RETRY_NOTES` is provided in the contract, the prior synthesis failed QC. Read the prior `synthesis.md` and the QC report. Fix only the cited gaps. Do not re-do passing sections. Re-run Step 6 self-check. Write.

---

## HALT Conditions

- PDF unreadable (corrupted, password-protected)
- Schema or charter file missing
- After 2 retries, QC issues persist (orchestrator handles escalation; you HALT with a clear reason)
- Paper is in a language you cannot read confidently (rare; flag for human)
- Paper is fundamentally not a research paper (e.g., a slide deck, a blog post export) — flag for curator to mark `skipped`
