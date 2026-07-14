---
name: synthesis-qc
description: |
  Step-by-step mechanical QC of a synthesis.md against the extraction schema
  and a score.json against the rubric. Pass/fail verdict only — no rewrites.
allowed-tools: Read, Bash, Glob, Grep
---

# Synthesis QC

Procedural guide for `@synthesis-qc`. You verify that produced artifacts conform to specs. You do NOT rewrite. You produce a structured report with PASS or FAIL, and on FAIL list specific issues for the responsible agent.

**You are mechanical, not interpretive.** If a section header says `## bias_audit` but the table only has 3 of 4 bias rows, that's a FAIL — even if the synthesis is otherwise excellent. The orchestrator counts on you to be a hard gate.

**Exception: Check S11 is heuristic, not mechanical.** It uses keyword overlap to surface "vs ours" framing misses. PASS-with-warning is the only soft verdict in the QC suite; everything else is binary. S11 is opt-in interpretation by you, not failable.

**Schema-drift detection (S10/Sm2):** This QC also detects mid-pass schema mutations. The schema_hash is a lock, not a chain — if it changes, papers synthesized under the old schema must be re-processed. Surface the issue; do not attempt to "interpret" old syntheses against new schema.

---

## Step 0: Load Contract Inputs

The contract specifies what to verify:

```
ARTIFACT: synthesis | score | both
SYNTHESIS_PATH: ...
SCORE_PATH: ...                # if ARTIFACT includes score
METADATA_PATH: ...             # always provided post-Slice-1
SCHEMA_VARIANT: academic | aurora-internal
```

---

## Step 1: Load Specs

Read:
- `docs/research/lit-synthesis/02-EXTRACTION-SCHEMA.md` (if checking synthesis)
- `docs/research/lit-synthesis/03-SCORING-RUBRIC.md` (if checking score)

If specs missing → HALT.

---

## Step 2: Synthesis QC Checks (when ARTIFACT includes synthesis)

Run each check. Record PASS/FAIL with evidence per check.

### Check S1: All section headers present in correct order
Required headers:
1. `# [Title]` (h1)
2. `## one_line_thesis`
3. `## core_claim`
4. `## methodology` (with `### data`, `### approach`, `### validation`)
5. `## key_results`
6. `## replicability`
7. `## bias_audit`
8. `## applicability_to_us`
9. `## novel_ideas_worth_keeping`
10. `## raw_quotes`

(Plus YAML frontmatter at top.)

Verify with grep on the file:
```bash
grep -n "^## " {SYNTHESIS_PATH}
```

### Check S2: YAML frontmatter parses

The synthesis must open with a `---` ... `---` YAML block. Validate with an actual YAML parser, not grep:

```bash
python3 -c "
import sys, yaml
with open('{SYNTHESIS_PATH}') as f:
    content = f.read()
if not content.startswith('---'):
    sys.exit('FAIL: no YAML frontmatter delimiter at line 1')
_, fm, _ = content.split('---', 2)
try:
    parsed = yaml.safe_load(fm)
except yaml.YAMLError as e:
    sys.exit(f'FAIL: YAML parse error — {e}')
required = ['title','authors','year','venue','identifier','page_count','file_hash','file_path','schema_variant','schema_hash','batch_id','charter_hash','synthesist_model','synthesis_date']
missing = [k for k in required if k not in parsed]
if missing:
    sys.exit(f'FAIL: missing required keys — {missing}')
if parsed.get('file_hash') in (None, '', 'pending'):
    sys.exit('FAIL: file_hash is null/empty/pending — curator did not populate metadata.json or synthesist did not copy it')
print('PASS: YAML valid, all required keys present, file_hash populated')
"
```

Required keys: `title, authors, year, venue, identifier, page_count, file_hash, file_path, schema_variant, schema_hash, batch_id, charter_hash, synthesist_model, synthesis_date`. Note `batch_id` and `charter_hash` were added by v1.2 — required as of this version.

S2 FAILs if: no frontmatter, YAML parse error, missing required key, OR `file_hash` is null/empty/pending. (The pending check catches the most common Slice 1 bug — synthesist not actually reading metadata.json.)

### Check S3: No silently-empty sections
For each `##` header, the body until the next `##` must contain ONE of:
- Non-whitespace text content, OR
- One or more `###` sub-section headers (with their own content), OR
- A line starting with `N/A —` followed by a reason

An empty body with no sub-sections AND no `N/A` is a FAIL.

The `## methodology` section legitimately has no prose body — it carries `### data`, `### approach`, `### validation` sub-sections. This passes S3. But each sub-section's body must independently meet the same rule (non-empty content or `N/A —`).

Verify with awk: extract each `##` block, check whether it contains non-whitespace beyond the header line itself OR a `###` sub-header.

```bash
awk '/^## /{name=$0; body=""; next} /^## /{print name "|" body; name=$0; body=""; next} {body = body $0 "\n"} END {print name "|" body}' {SYNTHESIS_PATH}
```

### Check S4: `key_results` page anchors
If `## key_results` content is not `N/A — ...`, every bullet must contain a page anchor in one of two forms:
- Single page: `(p. N)` — e.g., `(p. 12)`
- Multi-page range: `(pp. N-M)` — e.g., `(pp. 14-17)`

Both are accepted; either or both may appear. Use:

```bash
awk '/^## key_results/,/^## replicability/' {SYNTHESIS_PATH} \
  | grep "^- " \
  | grep -vE "\(pp?\. [0-9]"
```

The regex `\(pp?\. [0-9]` matches either `(p. ` or `(pp. ` followed by a digit. Any output → FAIL with the offending lines (bullets missing both forms).

> **Allowed variants:** `(p. 12)`, `(p. 12, Table 3)`, `(pp. 14-17)`, `(pp. 14–17)` (en-dash also fine). Do NOT accept `(page 12)`, `[p. 12]`, or any non-paren form.

### Check S5: `bias_audit` table completeness
The `## bias_audit` section must contain a markdown table with exactly 4 data rows for: Look-ahead bias, Survivorship bias, Overfitting signals, Data snooping. Each row's `Risk level` cell must be one of `low | medium | high`. Each row's `Evidence` cell must be non-empty.

For `aurora-internal` variant, the entire bias_audit may be `N/A — internal methodology document, not empirical research` — that is acceptable.

### Check S6: `raw_quotes` count and anchors
Quote blocks (`> "..."`) must be ≤5 in count. Each must have a `(p. N)` anchor. Empty raw_quotes section is acceptable only if explicitly `N/A — [reason]`.

### Check S7: No bracketed placeholders remain
```bash
grep -n "\[.*\]" {SYNTHESIS_PATH}
```
Filter out legitimate cases (markdown links, table headers) — but unfilled placeholders like `[Sharpe ratio]` or `[exact title from paper]` are FAILs.

### Check S8: Word count
```bash
wc -w {SYNTHESIS_PATH}
```
Must be between 600 and 3,500 words (excluding YAML frontmatter and table syntax — approximate is fine; hard cutoffs are 500 and 4,000 to allow some slack).

### Check S9: Variant-specific rules
If `schema_variant: aurora-internal`:
- `core_claim` must use `Operational purpose:` not `Fills gap of:` (or both — both is OK)
- `bias_audit` may be the canonical N/A statement
- `applicability_to_us` must contain `internal_status:` and `internal_owner:` fields. Acceptable values: `active | archived | draft | superseded | unknown`. ANY other value = FAIL (likely synthesist invented).

If both fields are `unknown`, S9 PASSES but emits a soft warning in the report:
> [S9 internal-roster]: PASS — internal_status and internal_owner are 'unknown'. Slug not in AURORA-ROSTER.md. Suggest human action before curate phase.

This is a "PASS with warning" — does not block the per-paper cycle but is surfaced in the verdict report.

### Check S10: schema_hash matches current schema

The synthesis.md frontmatter carries `schema_hash` — the hash of `02-EXTRACTION-SCHEMA.md` as it existed when this paper was synthesized. Compare against the current schema:

```bash
CURRENT_SCHEMA_HASH=$(sha256sum docs/research/lit-synthesis/02-EXTRACTION-SCHEMA.md | head -c 16)
SYNTHESIS_SCHEMA_HASH=$(python3 -c "
import yaml
with open('{SYNTHESIS_PATH}') as f:
    content = f.read()
_, fm, _ = content.split('---', 2)
print(yaml.safe_load(fm).get('schema_hash', ''))
")

if [ "$CURRENT_SCHEMA_HASH" = "$SYNTHESIS_SCHEMA_HASH" ]; then
    echo "PASS: schema_hash matches current schema ($CURRENT_SCHEMA_HASH)"
else
    echo "FAIL: schema drift detected. synthesis schema_hash=$SYNTHESIS_SCHEMA_HASH, current=$CURRENT_SCHEMA_HASH"
fi
```

**On FAIL:** the synthesis was written against an older schema. The paper requires re-synthesis to conform to the current contract.

This check is non-fatal in the sense that it doesn't invalidate the synthesis content — but it surfaces the drift so the orchestrator can flag the paper for re-processing. Route to `@corpus-curator` (mode: full_scan) which will detect the mismatch in metadata.json and reset status to `pending`.

**Special case — initial run:** if `metadata.schema_hash` matches synthesis frontmatter `schema_hash`, but BOTH differ from `CURRENT_SCHEMA_HASH`, the schema was edited AFTER curator's scan. The whole inventory needs a re-scan. Flag in verdict report — orchestrator should re-run curator before proceeding with more papers.

### Check Sb1: charter_hash matches current charter (DRIFT → re-score, not re-synthesize)

> **This check has different recovery semantics than S10.** Schema drift means the structural contract changed → re-synthesize. **Charter drift means the applicability rubric changed → re-score only**. Synthesis content is unaffected by charter mutation; only the `applicability_to_us.charter_relevance` and the scorer's Applicability axis are potentially stale.

Compare the synthesis's `charter_hash` against the current charter:

```bash
CURRENT_CHARTER_HASH=$(sha256sum docs/research/lit-synthesis/00-RESEARCH-CHARTER.md | cut -c1-16)
SYNTHESIS_CHARTER_HASH=$(python3 -c "
import yaml
with open('{SYNTHESIS_PATH}') as f:
    content = f.read()
_, fm, _ = content.split('---', 2)
print(yaml.safe_load(fm).get('charter_hash', ''))
")

if [ "sha256:$CURRENT_CHARTER_HASH" = "$SYNTHESIS_CHARTER_HASH" ]; then
    echo "PASS: charter_hash matches current charter (sha256:$CURRENT_CHARTER_HASH)"
else
    echo "FAIL: charter drift detected. synthesis charter_hash=$SYNTHESIS_CHARTER_HASH, current=sha256:$CURRENT_CHARTER_HASH"
fi
```

**On FAIL:** the charter mutated after this paper was synthesized. Re-route to `@paper-scorer` to refresh the score against the current charter — synthesis.md does NOT need to be re-written.

**Distinction from S10:**
- S10 FAIL → re-synthesize (route to @paper-synthesist; full retry cycle)
- Sb1 FAIL → re-score (route to @paper-scorer; synthesis stays untouched, just rerun the rubric)

This asymmetry is intentional — charter changes don't invalidate the structural extraction, only the relevance rating.

### Check S11: Section A "vs ours" framing heuristic (PASS-with-warning)

> **Heuristic, not exact.** This catches the obvious cases — paper appears to overlap a charter Section A capability, but `applicability_to_us` doesn't reference our existing state. Misses subtle overlaps. Acceptable false-negative rate; near-zero false positives.

```bash
# Skip S11 entirely if schema_variant is aurora-internal
if [ "$SCHEMA_VARIANT" = "aurora-internal" ]; then
    echo "N/A — aurora-internal variant"
    exit 0
fi
```

Procedure:

```bash
# Step 1: Extract Section A capability rows from charter
CHARTER_PATH=docs/research/lit-synthesis/00-RESEARCH-CHARTER.md
SECTION_A_TERMS=$(awk '/^### Section A:/,/^### Section B:/' "$CHARTER_PATH" \
  | grep -E '^\| [A-Za-z]' \
  | awk -F'|' '{print $2}' \
  | sed 's/^ *//; s/ *$//' \
  | grep -vE '^(Capability|---|None)' )

# If Section A is empty (charter says "None — greenfield research stack"), S11 PASSES trivially.
if [ -z "$SECTION_A_TERMS" ]; then
    echo "PASS — Section A is empty/greenfield, no overlap check applicable"
    exit 0
fi

# Step 2: Extract significant nouns from each capability row (drop stopwords, status words)
# Build a list of keyword patterns from Section A capabilities.
# Stopwords: production, research, prototype, daily, weekly, the, of, on, for, in, a, an, and, or
# Keep nouns like: "momentum", "VWAP", "execution", "HMM", "regime", "equity", "crypto"

# Step 3: Read synthesis applicability_to_us section
APPL_TEXT=$(awk '/^## applicability_to_us/,/^## novel_ideas_worth_keeping/' {SYNTHESIS_PATH})

# Step 4: For each Section A capability, check if any of its keywords appears in APPL_TEXT
# AND check if applicability_to_us mentions Section A (e.g., "Section A", "we already", "vs ours", "we run", "in production")

OVERLAP_FOUND=false
SECTION_A_MENTIONED=false

if echo "$APPL_TEXT" | grep -qiE 'section a|we already|we run|vs ours|in production|our (current|existing|implementation|prototype)'; then
    SECTION_A_MENTIONED=true
fi

# For each capability, derive 1-3 keywords and grep synthesis for them
# Pseudo-code (the QC agent implements with awareness of Section A row content):
# for each capability_row in $SECTION_A_TERMS:
#   keywords = significant_nouns(capability_row)  # e.g., "Daily cross-sectional momentum on US equities" -> ["momentum", "cross-sectional"]
#   if synthesis_one_line_thesis OR core_claim contains any keyword:
#       OVERLAP_FOUND=true
#       overlapping_capability = capability_row
#       break

if [ "$OVERLAP_FOUND" = "true" ] && [ "$SECTION_A_MENTIONED" = "false" ]; then
    echo "PASS-with-warning — paper appears to overlap Section A capability '$overlapping_capability' but applicability_to_us does not reference our existing state. Synthesist may have ignored Section A."
elif [ "$OVERLAP_FOUND" = "true" ] && [ "$SECTION_A_MENTIONED" = "true" ]; then
    echo "PASS — overlap detected and 'vs ours' framing present"
else
    echo "PASS — no obvious overlap with Section A capabilities"
fi
```

**Implementation note for the QC agent:** S11 is interpretive enough that a literal bash script is unreliable — the QC agent should do the keyword extraction in its head from the Section A rows it reads, then use grep against the synthesis `applicability_to_us` body. Acceptable for this check to be ≤80% precise; the goal is surfacing gross misses, not blocking legitimate variation.

**Verdict semantics:**
- `PASS` → no overlap detected, or overlap with proper "vs ours" framing
- `PASS-with-warning` → overlap detected but no Section A reference. Surface in report; do NOT block the cycle. Synthesist did not necessarily fail — could be the paper takes the capability in a different direction. Human can review.
- `FAIL` → never. This check does not fail; warnings are advisory.

**For aurora-internal variant:** S11 is N/A. Internal docs use a different applicability_to_us format; "vs ours" framing doesn't apply.

### Check Sm1: metadata.json parses as valid JSON

```bash
jq empty {METADATA_PATH} 2>&1
```

The classifier appends to metadata.json — if its merge produced invalid JSON, downstream curate-phase reads will fail. Validate before signing off.

Exit code 0 → PASS. Non-zero → FAIL, route to whoever last wrote metadata.json (check `tagged_date` vs `synthesis_date` to determine).

### Check Sm2: metadata.schema_hash present and matches synthesis.schema_hash

```bash
META_HASH=$(jq -r '.schema_hash // ""' {METADATA_PATH})
SYN_HASH=$(python3 -c "
import yaml
with open('{SYNTHESIS_PATH}') as f:
    content = f.read()
_, fm, _ = content.split('---', 2)
print(yaml.safe_load(fm).get('schema_hash', ''))
")

if [ -z "$META_HASH" ]; then
    echo "FAIL: metadata.schema_hash is empty — curator did not compute it (route to @corpus-curator)"
elif [ "$META_HASH" != "$SYN_HASH" ]; then
    echo "FAIL: synthesis.schema_hash ($SYN_HASH) does not match metadata.schema_hash ($META_HASH) — synthesist copied wrong value"
else
    echo "PASS: schema_hash consistent between metadata and synthesis"
fi
```

**On FAIL:** the synthesist either skipped Step 1a (load metadata.json) or hand-typed the hash incorrectly. Re-run synthesist with retry instruction "copy schema_hash from metadata.json verbatim."

---

## Step 3: Score QC Checks (when ARTIFACT includes score)

### Check Sc0: score.json parses as valid JSON

```bash
jq empty {SCORE_PATH} 2>&1
```

Exit code 0 → PASS. Non-zero → FAIL with the jq error message as evidence. Without this gate, Sc1–Sc6 cannot run reliably (they assume parseable JSON).

### Check Sc1: All five axes present and integers 0–5

### Check Sc2: total = sum of axes (no off-by-one, no fractional)

### Check Sc3: tier matches the rubric mapping
Unless `tier_overrides_applied` lists a triggering rule (off-charter-cap / high-bias-cap / aurora-internal). If overrides_applied claims a rule that doesn't actually trigger per the synthesis (e.g., claims "high-bias-cap" but synthesis bias_audit shows no `high`), FAIL.

### Check Sc4: reasoning entries
Each axis has a reasoning entry of ≥15 words. Each cites at least one synthesis section by name (e.g., mentions `methodology.validation`, `bias_audit`, `replicability`, `applicability_to_us`, etc.).

### Check Sc5: scorer did not invent numerics
Spot-check: for any number in the reasoning entries (e.g., "Sharpe of 1.84"), grep the synthesis to confirm it appears there.

### Check Sc6: schema_variant pass-through honored
If the paper's `synthesis.md` has `schema_variant: aurora-internal`, the score's `tier` must be `T-Internal` and `tier_overrides_applied` must include the aurora-internal rule.

---

## Step 4: Verdict

```
═══════════════════════════════════════════════════════════════════
SYNTHESIS QC REPORT
═══════════════════════════════════════════════════════════════════

Slug: {slug}
Artifact(s) checked: {synthesis | score | both}

SYNTHESIS CHECKS
[S1 headers]: PASS | FAIL — {evidence}
[S2 yaml]: PASS | FAIL — {evidence}
[S3 no-empty]: PASS | FAIL — {evidence}
[S4 page-anchors]: PASS | FAIL — {evidence}
[S5 bias-table]: PASS | FAIL — {evidence}
[S6 quotes]: PASS | FAIL — {evidence}
[S7 placeholders]: PASS | FAIL — {evidence}
[S8 word-count]: PASS | FAIL — {N words}
[S9 variant]: PASS | FAIL — {evidence}
[S10 schema-hash-vs-current]: PASS | FAIL — {evidence}
[Sb1 charter-hash-vs-current]: PASS | FAIL — {evidence (re-score, not re-synthesize, on FAIL)}
[S11 section-a-framing]: PASS | PASS-with-warning | N/A — {evidence}
[Sm1 metadata-json]: PASS | FAIL — {evidence}
[Sm2 schema-hash-consistency]: PASS | FAIL — {evidence}

SCORE CHECKS
[Sc0 json-parses]: PASS | FAIL — {evidence}
[Sc1 axes]: PASS | FAIL
[Sc2 total]: PASS | FAIL
[Sc3 tier]: PASS | FAIL
[Sc4 reasoning]: PASS | FAIL
[Sc5 numerics]: PASS | FAIL
[Sc6 variant-pass-through]: PASS | FAIL

═══════════════════════════════════════════════════════════════════
VERDICT: PASS | FAIL

If FAIL — Issues for {responsible-agent}:
1. [check id]: [specific issue]
2. ...

═══════════════════════════════════════════════════════════════════
```

> Note: S11 is heuristic and never FAILs. PASS-with-warning is informational and does not gate the cycle.

---

## Step 5: Routing Hint on FAIL

Indicate which agent owns the fix:
- S1, S3, S4, S5, S6, S7, S8 failures → `@paper-synthesist`
- S2 failures (yaml) → `@paper-synthesist` (or `@corpus-curator` if `file_hash` field is wrong)
- S2 file_hash=pending failure → `@corpus-curator` (re-run on this slug to repopulate metadata.json)
- S9 failures → `@paper-synthesist`
- S10 failure → `@corpus-curator` (mode: full_scan; will reset paper to pending due to hash mismatch). If many papers fail S10, schema was edited mid-pass — full re-process needed.
- Sb1 failure → `@paper-scorer` (re-score against refreshed charter; synthesis content stays valid). Do NOT re-route to synthesist for Sb1 — that's S10's lane.
- Sm1 failure → `@taxonomy-classifier` (most recent writer); if json was bad before classifier, route to `@paper-synthesist`
- Sm2 failure → `@paper-synthesist` (rerun with explicit instruction to copy schema_hash from metadata.json verbatim — likely synthesist Step 1a was skipped)
- Sc0 failure → `@paper-scorer` (rerun)
- Sc1–Sc4, Sc6 failures → `@paper-scorer`
- Sc5 numeric-invention failures → `@paper-scorer` (rerun) AND flag synthesis page-anchor discipline if numbers exist in synthesis without anchors
- S11 PASS-with-warning → no automatic re-route. Surface in PROGRESS.md "Recent Findings" if you choose to track it. Synthesist may be invited to re-do applicability_to_us with explicit Section A reference, but it's optional.

---

## HALT Conditions

- Specs (schema, rubric) missing
- Artifact files unreadable
- Specs themselves are malformed (e.g., schema doesn't list 10 sections) — orchestrator-level issue
