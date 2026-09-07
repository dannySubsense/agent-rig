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
| 2 | Reused trigger-surface / tool-call-collection functions, copied unmodified | — | `scripts/signpost_checklist_probe.py` (same file, additive) |
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

**Tests:**
- [ ] Unit tests covering US-1 AC1/AC2 (N Signpost lines → N verbatim rows; line changes between
  turns → new label matches verbatim) using hand-constructed markdown strings.
- [ ] `parse_checklist_row_line` unit tests: matches `- [ ]`, `- [x]`, `- [X]`, with and without the
  `(verified: tool_use_id=...)` suffix; returns `None` for non-matching lines.
- [ ] Edge case: empty Signpost section → `extract_signpost_lines` returns `[]`.

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

**Tests:**
- [ ] Existing archived-probe test coverage for these functions (if present in the archived
  sprint) is ported or re-run against the copied versions to confirm byte-identical behavior; if no
  such tests exist in the archive, write minimal smoke tests confirming heading detection and
  tool-call correlation still work against a representative transcript fixture.
- [ ] Confirm none of the §5.2 deleted-machinery symbols appear anywhere in the new file (grep
  check).

**Done When:**
- [ ] All listed tests pass.
- [ ] Grep confirms no deleted-machinery symbols were copied.

---

## Slice 3: `evaluate_checklist` + `build_reason` Evaluation Core

**Goal:** Implement the pure-function evaluation core (architecture §5.4, rules 0–6) mapping
Signpost lines + Pillar rows + qualifying tool calls to an `EvaluationResult`, including rule 0's
fail-closed block when the Signpost heading is entirely absent on a gated turn.

**Depends On:** Slice 1 (parser output types), Slice 2 (`QualifyingToolCall` shape, tool-call
collection)

**Files:**
- `scripts/signpost_checklist_probe.py` — additive; add `evaluate_checklist()`, `build_reason()`.

**Implementation Notes:**
- Implement all seven rules from architecture §5.4 exactly as specified — rule 0 (fail-closed block
  when `signpost_heading_present` is False, no per-line rules evaluated) through rule 6, including
  rule 5 (duplicate `tool_use_id` rejection).
- Rule 0 takes `signpost_heading_present` as an explicit function parameter to `evaluate_checklist`
  (architecture §4's signature) — it is not inferred from `signpost_lines` being empty, since an
  empty-but-present Signpost section is a distinct, non-blocking case (architecture §5.4's paragraph
  following rule 6).
- **Flag for forge-phase benchmark-before-QC visibility:** rule 5 is a mechanical uniqueness
  constraint (a `tool_use_id` may back at most one row), not a numeric threshold or similarity
  score — it requires no citation/sourcing under the unsourced-number rule, since it introduces no
  magic number. Architecture explicitly marks it as a design addition beyond the literal ACs and
  states it can be deleted without affecting anything else if a reviewer judges it out of scope —
  surfacing that here so forge/QC doesn't have to rediscover it.
- Empty-Signpost edge case (heading present, zero lines): zero violations, `decision = "allow"`, per
  architecture §5.4 final paragraph and requirements' Edge Cases table — distinct from rule 0's
  heading-absent-entirely case.
- `build_reason()`'s literal string content is *drafted* here but its self-teaching completeness
  requirement, including rule 0's distinct reason string, is owned by Slice 5.

**Tests:**
- [ ] One unit test per requirements AC (US-2 AC1/AC2, US-3 AC1/AC2/AC3) mapped directly to
  `evaluate_checklist` inputs/outputs, per architecture §9's stated testability approach — no
  transcript fixtures needed for this slice.
- [ ] Test for rule 0: `signpost_heading_present = False` → `decision = "block"`,
  `signpost_heading_absent = True`, `violations = []` (no per-line violations listed).
- [ ] Test for rule 5 (duplicate `tool_use_id` across two rows → `RowViolation("duplicate_id", ...)`
  on the second).
- [ ] Edge case test: empty `signpost_lines` with `signpost_heading_present = True` →
  `decision = "allow"`, no violations.
- [ ] Edge case test: repeated identical Signpost line across two separate evaluations (simulated as
  two independent calls) → each evaluated independently, no cross-call state.

**Done When:**
- [ ] All listed tests pass.
- [ ] `evaluate_checklist` and `build_reason` have no I/O (pure functions, confirmed by test design
  alone, not a mock).

---

## Slice 5: Agent-Facing Syntax Delivery

**Goal:** Deliver the forced Pillar-row syntax to the agent that will actually be writing Pillar
sections at runtime, through two independent channels, before the hook (Slice 6) is wired to
enforce it — closing the gap where every session's first reply would necessarily FAIL pending
inference from a block reason alone.

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
  into a second, possibly-diverging description.
- `scripts/signpost_checklist_probe.py` — additive-to-content-only; amend `build_reason()` (added
  in Slice 3) so a block's `reason` string is a complete, self-teaching specification of the
  required syntax on first failure, not merely a list of which rows were violated. This is the
  second, redundant delivery channel — it covers any agent session that starts without the
  CLAUDE.md guidance in context (e.g. a different repo, or a session where local instructions were
  not loaded).

**Implementation Notes:**
- This is a deliberate two-channel design, not a single point of failure: CLAUDE.md documentation
  reaches an agent *before* it ever writes a first reply (proactive delivery); the self-teaching
  block reason reaches an agent that reached the hook without that context (reactive, mid-turn
  delivery, per the archived mechanism's own postmortem note that hooks self-teach only for the
  audience that hits them in blocking mode). Both channels must describe the same syntax — do not
  let CLAUDE.md and `build_reason()` drift into two different phrasings of the row format.
- This slice makes no change to trigger surface or scope: it adds no new gating condition, no new
  hook, and no new evaluation rule. It is pure documentation plus the content (not the logic) of an
  existing return value.
- Do not invent new row-status vocabulary here — the vocabulary is fixed to the two forced literals
  in architecture §5.3 (`verified` with `tool_use_id`, `unverified`); document exactly those two,
  nothing more.
- `build_reason()` must also cover rule 0's distinct reason string: when `signpost_heading_absent`
  is True, the reason is a plain statement that the Signpost heading is required on this turn — not
  a per-row violation list, since rule 0 produces none.

**Tests:**
- [ ] `build_reason()` output, given a representative violation set including at least one
  `"missing"` and one `"false_claim"` violation, contains the literal row-grammar example (both the
  `verified` and `unverified` forms) inline in the string — not just the names of the violated
  Signpost lines.
- [ ] `build_reason()` output for a rule-0 result (`signpost_heading_absent = True`, `violations = []`)
  is a distinct, plain statement that the Signpost heading is required — not a per-row violation
  list, and not the empty/allow message.
- [ ] Manual read-through: a person with no prior knowledge of this mechanism, given only the
  `CLAUDE.md` section, can correctly hand-write one valid `verified` row and one valid `unverified`
  row from the documentation alone.

**Done When:**
- [ ] `CLAUDE.md` documents the exact row format, matching architecture §5.3 verbatim in grammar
  (not just in spirit), covering both forced literal statuses (`verified`, `unverified`).
- [ ] `build_reason()`'s output is confirmed self-teaching by the manual read-through test above,
  and confirmed to handle rule 0's distinct reason string separately from per-row violations.
- [ ] Both channels' descriptions of the row syntax are checked side by side for consistency — no
  divergent wording.

---

## Slice 4: `run()`/`main()` Wiring, Stdin Contract, Track-Record Log

**Goal:** Wire the top-level entry point — stdin read, gating order (`stop_hook_active` → queue
marker → first-turn check → section parsing), computing `signpost_heading_present` for rule 0,
`emit_block`/`emit_allow`, track-record writing, and the outer fail-open try/except — reproducing
the archived probe's exact ordering per US-5.

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
- `run()` computes `signpost_heading_present` (a bool, derived from whether
  `find_signpost_pillar_positions()` located a Signpost heading in the reply text) and passes it as
  the explicit `signpost_heading_present` argument to `evaluate_checklist()` (architecture §4
  signature) — this is what makes rule 0 (§5.4) reachable at runtime; `evaluate_checklist()` itself
  never re-derives this value from the transcript.
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
