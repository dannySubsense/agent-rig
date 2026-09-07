# Roadmap: Signpost Checklist Redesign

Cites `01-REQUIREMENTS.md` and `02-ARCHITECTURE.md` (this sprint). No `03-UI-SPEC.md` applies — this
is a pure hook/backend mechanism, no UI-driven slices.

**Numeric-constant flag:** No slice in this roadmap introduces a new numeric constant or threshold.
Confirmed against `02-ARCHITECTURE.md` §6 Anti-Patterns ("Any numeric similarity/confidence threshold
... explicitly forbidden") and §1 (only exact-equality / forced-vocabulary / existence-lookup checks
are permitted). Slice 3's rule 5 (duplicate `tool_use_id` rejection) is a mechanical uniqueness
check, not a numeric threshold — flagged in Slice 3 below per architecture's own explicit callout,
for forge-phase reviewer visibility, not because it needs benchmark sourcing.

**G-6 fix (prior revision):** the prior version of this roadmap built and wired the checker
(Slices 1–7 below, renumbered) but delivered the forced Pillar-row syntax to no one — every
session's first reply would necessarily FAIL until the agent inferred the required row format from
a block reason alone. Slice 5, "Agent-Facing Syntax Delivery," closes this: it is a deliberate
two-channel design (block-reason self-teaching + upfront written documentation), not a single
implicit assumption, and it lands *before* Slice 6 (hook wrapper + settings wiring) so the syntax is
documented before the hook can ever enforce it. This slice makes no change to trigger surface or
scope — it is documentation and a `build_reason()` content requirement, not a new gating condition.

**F4 fix (prior revision):** Frank's spec-gate attempt-1 flagged that rule 1a (`duplicate_label`,
02 §5.4) had landed in the architecture but Slice 3 below still described "rule 0 through rule 6"
without naming it and carried no test for it. Slice 3's Goal/Implementation Notes/Tests were updated
to name every rule then in 02 §5.4 explicitly (rule 0, 0a, 1, 1a, 1b, 2–6) and to add a
`duplicate_label` test, a rule 0a test, and a `stray_prose` (rule 1b) test.

**F2a/b/c, F3-schema, F5 fix (this revision):** Frank's spec-gate attempt-2 findings correspond to a
further architecture update since the F4 fix: (1) Rule 0a redefined — `signpost_section_has_content`
now includes trailing content on the Signpost heading line itself, not just text strictly between
headings (F2a). (2) Rule 1b clarified — the Pillar heading line is in scope for `unparsed_lines`, its
own label is stripped/never flagged, but trailing content on that line IS evaluated like a normal
line (F2b). (3) New rule 7 (`unmatched_row`) — any parsed `PillarRow` with no matching `SignpostLine`
now runs through rules 3–5 AND is always additionally flagged `RowViolation(kind="unmatched_row", ...)`
(F2c). (4) `RowViolation.kind` schema extended with `"malformed_signpost"` (rule 0a) and
`"unmatched_row"` (rule 7) (F3-schema). (5) Slice 5's agent-facing syntax delivery was "noted, not
delivered" — the transcript self-lookup step architecture §5.3 requires was never actually written
into the `CLAUDE.md` edit or `build_reason()`'s self-teaching content (F5). Slice 3 and Slice 5 below
are updated to close all five. This dispatch does not touch F6 (first-turn detection bypass) or rule
0's ALLOW4 divergence citation — both remain separate open decisions pending Danny's explicit call,
out of scope here.

---

## Dependency Map

| Unit | Depends On |
|---|---|
| Data schemas (§3) | — |
| New parsers (`extract_signpost_lines`, `extract_pillar_rows`, `parse_checklist_row_line`) | Data schemas |
| Reused trigger-surface / tool-call-collection functions (§5.1) | Data schemas (for `QualifyingToolCall` shape) |
| `evaluate_checklist` + `build_reason` | New parsers' output types, reused `QualifyingToolCall` |
| Agent-facing syntax delivery (written docs + self-teaching `build_reason` content) | `evaluate_checklist` + `build_reason` (needs the finalized row syntax/vocabulary to document) |
| `run()` / `main()` wiring, track-record log | New parsers, reused §5.1 functions, `evaluate_checklist` |
| Hook wrapper `.claude/hooks/signpost-checklist.sh` + `.claude/settings.json` wiring | `run()`/`main()` complete; agent-facing syntax delivery complete (docs must exist before the hook can enforce against them) |
| Real-transcript validation of new parsers | New parsers (Slice 1); practically exercised once the hook is live (Slice 6) |

---

## Slice Overview

| Slice | Goal | Depends On | Files |
|---|---|---|---|
| 1 | Data schemas + new verbatim parsers | — | `scripts/signpost_checklist_probe.py` (new) |
| 2 | Reused trigger-surface / tool-call-collection functions, copied with one additive change (§5.1a) | — | `scripts/signpost_checklist_probe.py` (same file, additive) |
| 3 | `evaluate_checklist` + `build_reason` pure evaluation core | 1, 2 | `scripts/signpost_checklist_probe.py` (same file, additive) |
| 4 | `run()`/`main()` wiring, stdin contract, fail-open wrapper, track-record log | 1, 2, 3 | `scripts/signpost_checklist_probe.py` (same file, additive); `docs/tooling/signpost-checklist-track-record.jsonl` (new, gitignored, created at runtime) |
| 5 | Agent-facing syntax delivery | 3 | `CLAUDE.md` (edit, this repo's local instructions); `scripts/signpost_checklist_probe.py` (`build_reason()`, same file, additive-to-content-only) |
| 6 | Hook wrapper script + settings wiring | 4, 5 | `.claude/hooks/signpost-checklist.sh` (new); `.claude/settings.json` (edit) |
| 7 | Real-transcript validation of new parsers | 1 (structurally); practically run after 6 is live | none (verification task, may produce a findings note under `docs/specs/signpost-checklist-redesign/`) |

All slices 1–4 land in the same new file (`scripts/signpost_checklist_probe.py`), built additively in
dependency order within that file — no file-ownership conflict since each slice's tests are scoped to
the functions it adds and later slices don't rewrite earlier slices' functions. Slice 5 touches that
same file again, but only to shape `build_reason()`'s output *content* (a string it already returns);
it adds no new function and does not reopen Slice 3's logic.

---

## Slice 1: Data Schemas + New Verbatim Parsers

**Goal:** Define the dataclasses (§3) and implement the three new parsing functions that read
Signpost/Pillar text and produce `SignpostLine`/`PillarRow` lists, using exact-equality/forced-syntax
matching only.

**Depends On:** —

**Files:**
- `scripts/signpost_checklist_probe.py` — create; add `SignpostLine`, `PillarRow`,
  `QualifyingToolCall`, `RowViolation`, `EvaluationResult` dataclasses (§3); add
  `extract_signpost_lines()`, `extract_pillar_rows()`, `parse_checklist_row_line()` (§4, §5.3
  `_PILLAR_ROW_RE`).

**Implementation Notes:**
- `_PILLAR_ROW_RE` is the exact regex given in architecture §5.3 — reproduce verbatim, do not
  re-derive.
- List-item marker stripping for Signpost lines must match architecture §4's description
  (`-`, `*`, `+`, or `N.` marker; non-list-item lines skipped).
- No fuzzy/near-match logic anywhere in this slice (§1 governing constraint, §6 anti-patterns).
- `extract_signpost_lines` returns `[]` both when no Signpost heading exists and when the heading
  is present but zero lines match the list-item shape — the caller (Slice 3/4) must distinguish
  these two cases via the separate `signpost_section_has_content` flag (architecture §4's note),
  not by treating every empty result as "nothing to verify." `signpost_section_has_content` includes
  trailing content on the Signpost heading line itself, after the `Signpost:` label is stripped —
  not only text strictly between the heading and the next heading (architecture §4).
- `extract_pillar_rows` also returns `unparsed_lines: list[str]` — the raw non-blank Pillar-section
  lines that failed to match the forced row syntax — per architecture §4's corrected contract, so
  Slice 3's rule 1b (stray-prose) has something to evaluate. The Pillar heading line itself is
  included in this span: its own label (`Pillar:`, case-insensitive, up to and including the first
  colon) is stripped and never itself treated as a row or as stray prose, but any trailing content
  after the label on that same heading line IS included and evaluated exactly like a normal line
  (row-parsed or classified as stray prose).

**Tests:**
- [ ] Unit tests covering US-1 AC1/AC2 (N Signpost lines → N verbatim rows; line changes between
  turns → new label matches verbatim) using hand-constructed markdown strings.
- [ ] `parse_checklist_row_line` unit tests: matches `- [ ]`, `- [x]`, `- [X]`, with and without the
  `(verified: tool_use_id=...)` suffix; returns `None` for non-matching lines.
- [ ] Edge case: empty Signpost section → `extract_signpost_lines` returns `[]`.
- [ ] `extract_pillar_rows` unit test: a non-conforming Pillar line (fails §5.3's forced syntax) is
  absent from the returned `PillarRow` list and present in `unparsed_lines`.
- [ ] `extract_signpost_lines` unit test: a reply with only `Signpost: I verified the build and the
  tests.` and nothing beneath it → `signpost_section_has_content = True`, `signpost_lines = []`
  (heading-line trailing prose counts as content, not as a claim line).
- [ ] `extract_pillar_rows` unit test: a bare `Pillar:` heading line with nothing else does not
  self-flag (label stripped, not treated as stray prose); a heading line with trailing content
  (`Pillar: all verified, trust me`) IS evaluated as a normal line (row-parsed or added to
  `unparsed_lines`).

**Done When:**
- [ ] All listed tests pass.
- [ ] No regex or logic in this slice performs similarity/fuzzy matching (spot-checked against §6
  anti-patterns).

---

## Slice 2: Reused Trigger-Surface / Tool-Call-Collection Functions

**Goal:** Copy the architecture-designated §5.1 functions from the archived probe into the new file,
unmodified in behavior, satisfying US-5's unchanged-trigger-surface requirement.

**Depends On:** — (independent of Slice 1; both are additive to the same new file)

**Files:**
- `scripts/signpost_checklist_probe.py` — additive; copy `read_stdin()`, `QUEUE_MARKER`,
  `load_transcript_records()`, `analyze_queue_injection_and_first_turn()`,
  `strip_leading_markup()`, `find_signpost_pillar_positions()`, `find_pillar_heading_line()`,
  `_collect_qualifying_tool_calls()` (renamed `collect_qualifying_tool_calls` per §4's public
  signature), and rename `C3_EXCLUDED_TOOLS` → `EXCLUDED_TOOLS` (same value, `{"TodoWrite"}`).
- Source: `archive/first-turn-contract-enforcement/scripts/first_turn_contract_probe.py` — read
  from, do not modify.

**Implementation Notes:**
- Copy, do not reimplement — architecture §5.1/§8 is explicit that re-deriving this logic risks
  introducing new bugs in already-battle-tested code with no requirement benefit.
- Do **not** copy any of the §5.2 deleted machinery (`_C2_LABEL_RE`, `find_c2_heading_line()`,
  `_extract_claim_subjects()`, `_subject_matches_target()`, `_path_components_align()`,
  `_phrase_boundary_match()`, `_FILE_PATH_RE`, `_PR_NUMBER_RE`, `_IDENTIFIER_RE`,
  `_QUOTED_QUERY_RE`, `_GH_*_RE`, `check_c3_violation()`).
- `collect_qualifying_tool_calls()` is copied with one additive change (architecture §5.1a, not
  byte-identical): also capture `tool_id` into each returned item and wrap the result as
  `QualifyingToolCall(tool_use_id=tool_id, name=name, tool_input=input)` — the archived function
  returns bare `(name, input)` tuples with `tool_use_id` discarded, which rule 4 (Slice 3) needs.

**Tests:**
- [ ] Existing archived-probe test coverage for these functions (if present in the archived
  sprint) is ported or re-run against the copied versions to confirm byte-identical behavior; if no
  such tests exist in the archive, write minimal smoke tests confirming heading detection and
  tool-call correlation still work against a representative transcript fixture.
- [ ] Confirm none of the §5.2 deleted-machinery symbols appear anywhere in the new file (grep
  check).
- [ ] `collect_qualifying_tool_calls()` unit test: each returned `QualifyingToolCall.tool_use_id`
  matches the real `tool_use` block ID from a fixture transcript (confirms the additive capture
  didn't drop or mis-map the ID).

**Done When:**
- [ ] All listed tests pass.
- [ ] Grep confirms no deleted-machinery symbols were copied.

---

## Slice 3: `evaluate_checklist` + `build_reason` Evaluation Core

**Goal:** Implement the pure-function evaluation core (architecture §5.4) mapping Signpost lines +
Pillar rows + qualifying tool calls to an `EvaluationResult`, including every rule currently in
§5.4: rule 0 (Signpost heading absent, fail-closed), rule 0a (heading present with non-blank
content — including heading-line trailing content — but zero parsed claim lines, fail-closed), rule
1 (`missing`), rule 1a (`duplicate_label`), rule 1b (`stray_prose`, including the Pillar heading
line's own trailing content when present), rule 2 (`unverified` always allowed), rule 3 (`verified`
with no `tool_use_id`, defensive `false_claim`), rule 4 (`verified` with an ID absent from
`qualifying_calls`, `false_claim`), rule 5 (`verified` with a reused `tool_use_id`,
`duplicate_id`), rule 6 (all-clear → `allow`), and rule 7 (`unmatched_row` — a syntactically valid
`PillarRow` with no matching `SignpostLine` still runs through rules 3–5 and is always additionally
flagged `unmatched_row`).

**Depends On:** Slice 1 (parser output types, including `unparsed_lines`), Slice 2
(`QualifyingToolCall` shape, tool-call collection)

**Files:**
- `scripts/signpost_checklist_probe.py` — additive; add `evaluate_checklist()`, `build_reason()`.

**Implementation Notes:**
- Implement every rule in architecture §5.4 exactly as specified — this is a rule *set*, not a
  numbered 0–6 sequence alone: rule 0 (fail-closed block when `signpost_heading_present` is False),
  rule 0a (fail-closed block when `signpost_section_has_content` is True but `signpost_lines` is
  empty — malformed/prose-only claims, including prose written directly on the Signpost heading
  line, distinct from a genuinely empty section), rule 1 (`missing`), rule 1a (`duplicate_label` —
  more than one `PillarRow` matches the same `SignpostLine.text`; neither matching row proceeds to
  rules 2–5 for that line), rule 1b (`stray_prose` — one violation per entry in `unparsed_lines`,
  including a Pillar heading line's own trailing content when present, in addition to any `missing`
  violation the same gap may also produce), rule 2 through rule 6 as previously specified, and rule
  7 (`unmatched_row` — a `PillarRow` with no matching `SignpostLine.text` is NOT silently ignored:
  it is subject to rules 3–5 exactly as a matched row would be, and in addition always produces
  `RowViolation(kind="unmatched_row", signpost_text=None, row=row)`, regardless of its status).
- `evaluate_checklist`'s signature per architecture §4 takes three boolean/list inputs beyond the
  parsed structures: `signpost_heading_present` (rule 0), `signpost_section_has_content` (rule 0a),
  and `pillar_unparsed_lines` (rule 1b) — none of these are inferred from `signpost_lines`/
  `pillar_rows` being empty; each is an explicit caller-supplied input (Slice 4 computes and passes
  all three). Rule 7 requires no additional input — it is computed by iterating `pillar_rows` after
  the per-Signpost-line matching pass and flagging any row that was never matched.
- **Flag for forge-phase benchmark-before-QC visibility:** rule 5 is a mechanical uniqueness
  constraint (a `tool_use_id` may back at most one row), not a numeric threshold or similarity
  score — it requires no citation/sourcing under the unsourced-number rule, since it introduces no
  magic number. Architecture explicitly marks it as a design addition beyond the literal ACs and
  states it can be deleted without affecting anything else if a reviewer judges it out of scope —
  surfacing that here so forge/QC doesn't have to rediscover it. Rule 1a is the same shape one size
  smaller: a structural count check (how many rows matched a Signpost line), not text inference, so
  it likewise needs no citation. Rule 7 is the same shape again: a structural presence/absence check
  (did this row match any Signpost line), not text inference or a threshold — no citation needed.
- Empty-Signpost edge case (heading present, zero lines, zero non-blank content anywhere including
  the heading line) is distinct from rule 0a: zero violations, `decision = "allow"`, per
  architecture §5.4's final paragraph and requirements' Edge Cases table.
- `build_reason()`'s literal string content is *drafted* here but its self-teaching completeness
  requirement, including rule 0's, rule 0a's, and rule 7's distinct reason strings, is owned by
  Slice 5.

**Tests:**
- [ ] One unit test per requirements AC (US-2 AC1/AC2, US-3 AC1/AC2/AC3) mapped directly to
  `evaluate_checklist` inputs/outputs, per architecture §9's stated testability approach — no
  transcript fixtures needed for this slice.
- [ ] Test for rule 0: `signpost_heading_present = False` → `decision = "block"`,
  `signpost_heading_absent = True`, `violations = []` (no per-line violations listed).
- [ ] Test for rule 0a: `signpost_heading_present = True`, `signpost_section_has_content = True`,
  `signpost_lines = []` → `decision = "block"` with a `malformed_signpost` violation.
- [ ] Test for rule 0a with heading-line trailing prose specifically: `signpost_lines = []`,
  `signpost_section_has_content = True` derived from trailing text on the Signpost heading line
  itself (not text between headings) → `decision = "block"` with a `malformed_signpost` violation
  — confirms the heading-line-trailing-content path, not only the between-headings path.
- [ ] Test for rule 1a (`duplicate_label`): two Pillar rows matching the same Signpost line — one
  `(unverified)`, one `(verified: tool_use_id=...)` — both produce
  `RowViolation("duplicate_label", ...)`, `decision = "block"`.
- [ ] Test for rule 1b (`stray_prose`): a non-conforming Pillar line in `pillar_unparsed_lines`
  produces `RowViolation("stray_prose", ...)`.
- [ ] Test for rule 1b on the Pillar heading line: a bare `Pillar:` heading with nothing else
  produces no violation (label stripped, never flagged); a `Pillar: all verified, trust me` heading
  line produces a `RowViolation("stray_prose", ...)` (or is row-parsed, if it happens to match the
  forced syntax) exactly as any other line would.
- [ ] Test for rule 5 (duplicate `tool_use_id` across two rows → `RowViolation("duplicate_id", ...)`
  on the second).
- [ ] Test for rule 7 (`unmatched_row`): a `PillarRow` whose label matches no `SignpostLine.text` →
  runs through rules 3–5 (e.g. an unbacked `verified` claim on the unmatched row still produces
  `RowViolation("false_claim", ...)`) AND always additionally produces
  `RowViolation(kind="unmatched_row", row=row)`, regardless of the row's status.
- [ ] Edge case test: empty `signpost_lines` with `signpost_heading_present = True`,
  `signpost_section_has_content = False` → `decision = "allow"`, no violations.
- [ ] Edge case test: repeated identical Signpost line across two separate evaluations (simulated as
  two independent calls) → each evaluated independently, no cross-call state.

**Done When:**
- [ ] All listed tests pass.
- [ ] `evaluate_checklist` and `build_reason` have no I/O (pure functions, confirmed by test design
  alone, not a mock).

---

## Slice 5: Agent-Facing Syntax Delivery

**Goal:** Deliver the forced Pillar-row syntax — including the active transcript self-lookup step
required to produce a real `tool_use_id` — to the agent that will actually be writing Pillar
sections at runtime, through two independent channels, before the hook (Slice 6) is wired to
enforce it — closing the gap where every session's first reply would necessarily FAIL pending
inference from a block reason alone, and closing F5's specific finding: as previously drafted this
slice's instructions were "noted, not delivered," so "an agent following Slice 5 as written cannot
produce a verified row except by fabrication."

**Depends On:** Slice 3 (the row syntax and legal row vocabulary must be finalized before it can be
documented or quoted in a block reason). The row vocabulary is already settled: per
`02-ARCHITECTURE.md` §5.3, there are exactly two forced literal statuses a Pillar row may declare —
`verified` (paired with a real `tool_use_id`) and `unverified` — no third, free-form status exists.

**Files:**
- `CLAUDE.md` (this repo's local, gitignored instructions) — edit; add a short section documenting
  the exact required Pillar-row format: one row per Signpost line, the label copied verbatim from
  the Signpost line, and either a real `tool_use_id` citation (`status = "verified"`) or the forced
  literal `(unverified)` suffix for a claim the agent is not verifying. Quote the row grammar
  directly from architecture §5.3 (`_PILLAR_ROW_RE`'s plain-language form) — do not paraphrase it
  into a second, possibly-diverging description. **Also add the transcript self-lookup step
  explicitly** (architecture §5.3, "Resolving 05-REVIEW Q-3/A-7"): a `tool_use_id` is not
  automatically visible to the agent in a normal reply. Before writing a `(verified:
  tool_use_id=<id>)` row, the agent must actively look it up by reading its OWN current session's
  transcript file — the most recently modified `*.jsonl` under `~/.claude/projects/<project>/` —
  and searching backward from the end of that file for the `tool_use` block matching the specific
  call it wants to cite, to read that block's real `id`. State plainly that this is an active
  lookup step the agent must perform every time, not something already present in its context, and
  that skipping it leaves only two honest options: perform the lookup, or write `(unverified)`.
- `scripts/signpost_checklist_probe.py` — additive-to-content-only; amend `build_reason()` (added
  in Slice 3) so a block's `reason` string is a complete, self-teaching specification of the
  required syntax on first failure, not merely a list of which rows were violated, and so it
  includes the same transcript self-lookup instruction described above for the `CLAUDE.md` edit.
  This is the second, redundant delivery channel — it covers any agent session that starts without
  the CLAUDE.md guidance in context (e.g. a different repo, or a session where local instructions
  were not loaded).

**Implementation Notes:**
- This is a deliberate two-channel design, not a single point of failure: CLAUDE.md documentation
  reaches an agent *before* it ever writes a first reply (proactive delivery); the self-teaching
  block reason reaches an agent that reached the hook without that context (reactive, mid-turn
  delivery, per the archived mechanism's own postmortem note that hooks self-teach only for the
  audience that hits them in blocking mode). Both channels must describe the same syntax — do not
  let CLAUDE.md and `build_reason()` drift into two different phrasings of the row format.
- Both channels must state the transcript self-lookup step explicitly and identically in substance:
  find the most recently modified `*.jsonl` under `~/.claude/projects/<project>/`, search backward
  for the matching `tool_use` block, read its real `id`. This is not optional flavor text — per
  architecture §5.3, without it stated explicitly an agent has no way to produce a real ID and is
  forced into either fabrication (caught by rule 4) or defaulting to `(unverified)` even when
  verification did happen.
- This slice makes no change to trigger surface or scope: it adds no new gating condition, no new
  hook, and no new evaluation rule. It is pure documentation plus the content (not the logic) of an
  existing return value.
- Do not invent new row-status vocabulary here — the vocabulary is fixed to the two forced literals
  in architecture §5.3 (`verified` with `tool_use_id`, `unverified`); document exactly those two,
  nothing more.
- `build_reason()` must cover distinct reason strings for every non-per-row-violation rule and for
  the two new violation kinds:
  - Rule 0 (`signpost_heading_absent = True`): a plain statement that the Signpost heading is
    required on this turn — not a per-row violation list.
  - Rule 0a (heading present, content present including heading-line trailing content, zero parsed
    claim lines): a plain statement that Signpost claims must be written as list items, including
    the case where the claim was written as trailing prose directly on the heading line — not the
    rule-0 message and not a per-row violation list.
  - `malformed_signpost` (rule 0a's violation kind): self-teaching text distinguishing this from
    `missing` — claims exist as prose (including on the heading line) rather than as list items;
    the fix is to rewrite the claim as a `-`/`*`/`+`/`N.` list item, not to add a Pillar row.
  - `unmatched_row` (rule 7's violation kind): self-teaching text explaining that this Pillar row's
    label does not match any Signpost line — the fix is either to correct the label to match an
    existing Signpost claim verbatim, or to add the missing Signpost line the row was meant to back,
    not to leave an orphaned row in place.

**Tests:**
- [ ] `build_reason()` output, given a representative violation set including at least one
  `"missing"` and one `"false_claim"` violation, contains the literal row-grammar example (both the
  `verified` and `unverified` forms) inline in the string — not just the names of the violated
  Signpost lines.
- [ ] `build_reason()` output for a rule-0 result (`signpost_heading_absent = True`, `violations = []`)
  is a distinct, plain statement that the Signpost heading is required — not a per-row violation
  list, and not the empty/allow message.
- [ ] `build_reason()` output for a rule-0a result (`malformed_signpost` violation) is a distinct,
  plain statement that Signpost claims must be written as list items — not the rule-0 message and
  not a per-row violation list.
- [ ] `build_reason()` output for a result containing an `unmatched_row` violation is a distinct,
  self-teaching reason string explaining the row's label matched no Signpost line, and directs the
  agent to either correct the label or add the missing Signpost line.
- [ ] `build_reason()`'s output (or the equivalent `CLAUDE.md` section text) explicitly instructs,
  in plain language, the transcript self-lookup step: read the current session's own most recently
  modified `*.jsonl` transcript file and search backward for the matching `tool_use` block's real
  `id` before writing a `(verified: tool_use_id=...)` row.
- [ ] Manual read-through: a person with no prior knowledge of this mechanism, given only the
  `CLAUDE.md` section, can correctly hand-write one valid `verified` row (including correctly
  describing how they would locate the real `tool_use_id`) and one valid `unverified` row from the
  documentation alone.

**Done When:**
- [ ] `CLAUDE.md` documents the exact row format, matching architecture §5.3 verbatim in grammar
  (not just in spirit), covering both forced literal statuses (`verified`, `unverified`), AND
  documents the transcript self-lookup step explicitly.
- [ ] `build_reason()`'s output is confirmed self-teaching by the manual read-through test above,
  confirmed to handle rule 0's, rule 0a's (`malformed_signpost`), and rule 7's (`unmatched_row`)
  distinct reason strings separately from per-row violations, and confirmed to state the transcript
  self-lookup step.
- [ ] Both channels' descriptions of the row syntax, the two new violation-kind reason strings, and
  the transcript self-lookup step are checked side by side for consistency — no divergent wording.

---

## Slice 4: `run()`/`main()` Wiring, Stdin Contract, Track-Record Log

**Goal:** Wire the top-level entry point — stdin read, gating order (`stop_hook_active` → queue
marker → first-turn check → section parsing), computing `signpost_heading_present`,
`signpost_section_has_content`, and `pillar_unparsed_lines` for rules 0/0a/1b, `emit_block`/
`emit_allow`, track-record writing, and the outer fail-open try/except — reproducing the archived
probe's exact ordering per US-5.

**Depends On:** Slice 1, Slice 2, Slice 3

**Files:**
- `scripts/signpost_checklist_probe.py` — additive; add `run()`, `main()`,
  `emit_block()`/`emit_allow()` (adapted to new `EvaluationResult` schema), `write_track_record()`
  (new row-level schema, gitignored).
- `docs/tooling/signpost-checklist-track-record.jsonl` — new, gitignored, created at first runtime
  invocation (not committed).

**Implementation Notes:**
- Gating order is fixed by requirements US-5 and architecture §5.1 — no reordering:
  `stop_hook_active` bypass first (unconditional allow) → queue-marker check → first-turn check →
  only then section parsing.
- `run()` computes all three of `evaluate_checklist`'s non-parsed-structure inputs (architecture §4
  signature) and passes them through explicitly — `evaluate_checklist()` itself never re-derives
  any of them from the transcript:
  - `signpost_heading_present` (bool, from whether `find_signpost_pillar_positions()` located a
    Signpost heading) — makes rule 0 reachable.
  - `signpost_section_has_content` (bool, whether the Signpost section's text — including trailing
    content on the heading line itself — after stripping blank lines, is non-empty) — makes rule 0a
    reachable.
  - `pillar_unparsed_lines` (`list[str]`, from `extract_pillar_rows()`'s `unparsed_lines` return,
    Slice 1, including the Pillar heading line's own trailing content when present) — makes rule 1b
    reachable.
- Track-record schema is row-level (block/allow, violated rows, `probe_error`), distinct from the
  archived C1/C2/C3 schema — do not reuse the old schema shape.
- Outer `try`/`except` in `main()` must fail-open (allow) on any unhandled exception, matching
  repo convention.

**Tests:**
- [ ] `stop_hook_active` present → allow, no further processing (verify via a stub/mock stdin
  payload, not a real transcript).
- [ ] Queue marker absent → mechanism does not activate (US-5 AC3).
- [ ] Not first reply of session → mechanism does not activate (US-5 AC3).
- [ ] `run()` correctly computes `signpost_heading_present = False` and passes it through to
  `evaluate_checklist()` when a reply has no Signpost heading, producing rule 0's block.
- [ ] `run()` correctly computes `signpost_section_has_content = True` with `signpost_lines = []`
  and passes both through, producing rule 0a's block.
- [ ] `run()` correctly passes a non-empty `pillar_unparsed_lines` through, producing rule 1b's
  `stray_prose` violation.
- [ ] Simulated exception inside evaluation path → `main()` still exits allow (fail-open).
- [ ] Track-record entry written on both block and allow paths, matching the new schema.

**Done When:**
- [ ] All listed tests pass.
- [ ] Gating order verified by test to match architecture §5.1 exactly (test asserts short-circuit
  at each gate, not just final outcome).

---

## Slice 6: Hook Wrapper Script + Settings Wiring

**Goal:** Add the Stop-hook wrapper script and point `.claude/settings.json` at it, replacing the
already-unwired archived `first-turn-contract.sh` entry.

**Depends On:** Slice 4, Slice 5 (the agent-facing syntax must already be documented before the
hook can be live to enforce against it — wiring the hook ahead of Slice 5 would recreate the exact
gap this revision fixes).

**Files:**
- `.claude/hooks/signpost-checklist.sh` — new; same shape as archived `first-turn-contract.sh`
  (invoke the probe, fail-open on any wrapper-level error).
- `.claude/settings.json` — edit; Stop-hook entry points at
  `.claude/hooks/signpost-checklist.sh`.

**Implementation Notes:**
- Confirm the archived `first-turn-contract.sh` entry is indeed already unwired (per architecture
  §8 note) before editing — if it is still wired, this slice also removes/replaces that entry
  explicitly rather than assuming.

**Tests:**
- [ ] Manual/integration check: a crafted stdin payload through the wrapper script produces the
  same block/allow decision as calling the probe directly.
- [ ] Wrapper fails open (exit allowing) on a deliberately broken probe invocation (e.g. missing
  file), matching repo convention.

**Done When:**
- [ ] `.claude/settings.json` Stop-hook entry verified pointing at the new wrapper (read the live
  file, not a recollection).
- [ ] Wrapper script tests pass.

---

## Slice 7: Real-Transcript Validation of New Parsers

**Goal:** Validate `extract_signpost_lines`, `extract_pillar_rows`, and `parse_checklist_row_line`
(Slice 1's new logic) against real `~/.claude/projects/*/*.jsonl` transcript data, per the task's
explicit instruction and architecture §9 — self-written fixtures alone do not certify this logic.

**Depends On:** Slice 1 structurally (the functions must exist); practically most useful once
Slice 6 is live and at least one real first-turn reply exists in the new Signpost/checklist format
(architecture §9 notes the format doesn't exist in real transcripts until the mechanism has run at
least once).

**Files:** None created by default. If real-data runs surface a parser defect, the fix lands back
in `scripts/signpost_checklist_probe.py` (amending Slice 1's functions) and this slice's Done-When
is not met until a passing re-run confirms the fix. A short findings note may be added under
`docs/specs/signpost-checklist-redesign/` if defects are found and fixed, documenting what real-data
shape caused the miss.

**Implementation Notes:**
- Per requirements' Out of Scope, this is explicitly **not** an elaborate pre-ship test corpus —
  it is a real-data spot-check against whatever genuine first-turn replies exist, consistent with
  "Danny's live daily use with feedback" being the actual validation model.
- If zero real transcripts in the new format exist yet at the time this slice is reached, that is
  itself the finding to report — do not fabricate synthetic transcripts and call it real-data
  validation; that would silently violate the self-certification constraint this slice exists to
  satisfy. In that case, this slice's Done-When becomes: run once real data exists, and this gap is
  surfaced explicitly rather than skipped.

**Tests:**
- [ ] Run the three parser functions against every available real `~/.claude/projects/*/*.jsonl`
  transcript that contains a Signpost/Pillar section in the new checklist format.
- [ ] For each, manually confirm parsed `SignpostLine`/`PillarRow` output matches the actual reply
  text (no silent misparse, no dropped line, no false match).

**Done When:**
- [ ] At least one real transcript has been checked and results reported (pass, or defect found and
  fixed with a passing re-run), OR the "zero real transcripts exist yet" gap has been explicitly
  surfaced to Danny rather than silently deferred.

---

## Sequence Rules

1. Complete each slice fully (including its Done-When checklist) in dependency order per the
   Dependency Map — not necessarily the order slices appear in this document.
2. Slices 1 and 2 may proceed in either order or in parallel (no dependency between them), but both
   must be complete before Slice 3 begins.
3. Slice 5 (agent-facing syntax delivery) must complete before Slice 6 (hook wrapper + settings
   wiring) — documentation must exist before the hook that enforces it goes live. This is the fix
   for G-6 and is not optional ordering.
4. No partial slice work — a slice's tests must pass before the next slice starts.
5. If blocked (e.g. Slice 7 finds zero real transcripts available), HALT and surface the gap rather
   than skipping ahead or fabricating a substitute.
6. No new slices added without human approval.

---

## Dispositions (05-REVIEW.md Open Questions)

Recorded here so these three items are not silently open. Each is a Danny-level judgment call
already made; not re-opened by future slices absent a new finding.

- **Q-1 (keep/delete architecture §5.4 rule 5, duplicate `tool_use_id` rejection): KEEP.**
  Reasoning: cheap, mechanical, no unsourced constant — it is a structural uniqueness check, not a
  threshold. It closes a real gaming vector (one tool call trivially "backing" every row, which
  would satisfy US-2 AC2's literal wording while defeating the mechanism's evident purpose).
- **Q-4 (is `CLAUDE.md`-only delivery, gitignored/repo-local, acceptable given this mechanism may
  run in other repos): ACCEPTED for this sprint's scope.** This sprint is agent-rig-only — see
  `01-REQUIREMENTS.md`'s "Propagation Scope (this sprint: agent-rig only)" section, which now
  states explicitly that the archived mechanism remains live, unmodified, in the other nine
  `HOOK-DEPLOYMENT-ROSTER.md` repos, and that redeploying this redesign elsewhere is a separate,
  later sprint's work. `CLAUDE.md`-only delivery is sufficient for that scope; it is not a
  cross-repo delivery mechanism and was never claimed to be one.
- **Q-5 (does the mechanism ship before Slice 7's real-data validation can run): ACCEPTED, already
  the explicit design.** Slice 7 itself states "zero real transcripts is itself the finding; do not
  fabricate" — trailing, honestly-reported real-data validation is intentional, not an oversight,
  consistent with "Danny's live daily use with feedback" being the actual validation model (see
  Slice 7 and 01's Out of Scope).

**F6 (first-turn detection bypass) — RESOLVED, accepted (2026-09-07, Danny).** Measured 1/10 on
real transcripts; tested against this sprint's North Star intent and accepted as a known,
documented limitation rather than redesigned now — see `01-REQUIREMENTS.md` US-5's Known
Limitation and Constraints. Not re-opened absent a real incident or a rising real-world rate.

**Rule 0's ALLOW4 divergence — RESOLVED, confirmed (2026-09-07, Danny).** Tested against this
sprint's North Star intent (closing evasion channels): blocking on a missing Signpost heading
points the same direction as that intent, so the stricter behavior stands as designed — see
`02-ARCHITECTURE.md` §5.4 rule 0 and `01-REQUIREMENTS.md` Edge Cases.

---

## Deferred (Not This Roadmap)

- Row-key normalization/truncation scheme (per requirements, explicitly deferred — verbatim-only
  for this build).
- Any consumer of the Signpost/Pillar convention besides this mechanism.
- Dedup logic for identical Signpost lines across turns.
- Any retry-count/attempt-ceiling logic on this mechanism's own FAIL path (belongs solely to
  Frank's separate gate).
- Relevance-of-evidence-to-claim checking beyond rule 5's uniqueness constraint (would require its
  own Intake/spec cycle per architecture §6 anti-patterns).
- Delivering the row syntax via any channel beyond CLAUDE.md and the self-teaching block reason
  (e.g. an output style, a system-prompt change, or a separate onboarding doc) — out of scope for
  this fix; the two channels in Slice 5 are judged sufficient for this repo's actual operating
  pattern (session-start CLAUDE.md load, plus hook fail-open with a readable reason).
- Propagating this redesign to any repo besides agent-rig (see Dispositions, Q-4, and 01's
  Propagation Scope section) — a separate, later sprint's work.
- Redesigning the inherited first-turn-detection boundary to close F6's known 1-in-10 bypass —
  accepted, not fixed, this sprint (see Dispositions above).
