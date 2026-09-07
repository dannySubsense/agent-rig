# Spec: first-turn-contract-c3-claim-matching

**Status**: DRAFT

**Date**: 2026-08-27
**Author**: wright
**Parent Intake**: `docs/tooling/first-turn-contract-c3-claim-matching/INTAKE.md` (APPROVED)
**Parent decision record**: DDR-004 (`signpost-pillar-propagation`), C3 gap logged there as a
future hardening item, not resolved by that sprint.

---

## 1. Purpose and Non-Goals

**Purpose**: `check_c3_violation` in `scripts/first_turn_contract_probe.py` currently checks only
*presence* of any qualifying tool call before the current turn. This spec upgrades it to check
that a qualifying tool call's **target** matches the **subject of the specific Pillar claim**
being asserted, so a stale or unrelated tool call can no longer satisfy C3 for a claim it never
verified.

**Non-goals** (explicitly out of scope for this fix):
- Does not redesign C1 (Signpost-before-Pillar ordering) or C2 (forbidden third section).
- Does not add a new hook, new script file, or touch `.claude/settings.json` wiring.
- Does not change the first-turn-only scope (`analyze_queue_injection_and_first_turn`'s
  `if not first_turn: ... return` short-circuit is untouched — checks still never run past turn 1).
- Does not add fuzzy/ML-based similarity matching, or any similarity threshold. v1 matching is
  exact substring/token containment only (see §3).
- Does not change `run()`'s control flow, `write_track_record`'s schema, or `build_reason`'s
  signature beyond the C3 reason string's content (see §4).
- Does not take authority over Frank's or a human's judgment — this remains a mechanical,
  narrow, auditable check, same posture as existing C1/C2/C3.

---

## 2. Current Behavior (for contrast)

`check_c3_violation(records, current_turn_index, pillar_idx)`:
1. If no Pillar heading, no violation.
2. Collect every completed (`tool_use` id present in a matching `tool_result`), non-`TodoWrite`
   tool call in `records[:current_turn_index]`.
3. Violation iff that set is empty.

This has no concept of *which* Pillar section, or what it claims — `pillar_idx` is used only to
gate whether the check runs at all, never to extract subject matter.

---

## 3. The Matching Contract

### 3.1 Claim subject — what it is

A **claim subject** is one or more identifier-shaped tokens extracted from the text of a single
Pillar section (from its heading line through the next Signpost/Pillar heading line or end of
`last_assistant_message`, whichever comes first). "Identifier-shaped" is deliberately narrow for
v1 — it is not a free-text NLP extraction. A token qualifies if it matches one of:

| Subject type | Extraction pattern | Example |
|---|---|---|
| File path | Backtick- or plain-token substrings containing at least one `/` or a recognized extension (`.py`, `.md`, `.ts`, `.tsx`, `.json`, `.sh`, `.yml`, `.yaml`), via regex `` `?([\w./\-]+\.\w+|[\w\-]+/[\w./\-]+)`? `` | `` `scripts/first_turn_contract_probe.py` `` |
| PR/issue number | `#\d+` or `PR\s*#?\d+` (case-insensitive) | `PR #42`, `#42` |
| Identifier / symbol | Backtick-quoted bare identifier (function/class/var name), regex `` `([A-Za-z_][\w]*)` `` | `` `check_c3_violation` `` |
| Command / gh reference | Inside backticked or fenced code spans containing `gh `, capture the PR/issue number per above; otherwise treat the whole backticked command string as the subject | `` `gh pr view 42` `` |
| Quoted query string | Double-quoted string following words "search", "query", "grep", "find" (case-insensitive) within the section | `search "session queue"` |

Extraction is performed independently for the **currently-open Pillar section only** — i.e. the
section whose heading is at `pillar_idx` (the first Pillar heading, consistent with existing
`find_pillar_heading_line` usage) through the next heading or end of text. This matches the
existing single-Pillar-section scope of `pillar_idx`/`pillar_line` used elsewhere in the file; if
a turn has multiple Pillar headings, this spec's v1 only strengthens the check for the first one,
matching the file's current single-`pillar_idx` model. Widening to multiple Pillar sections is
listed as an open question (§7) requiring a genuinely separate change to `find_signpost_pillar_positions`'s
return shape.

A Pillar section may yield **zero or more** claim subjects (a section can name several files/PRs).

### 3.2 Tool-call target fields matched against

For each qualifying tool call (same eligibility as today: completed `tool_use`/`tool_result`
pair, name not in `C3_EXCLUDED_TOOLS`), the **target text** is extracted from `tool_use.input`
(present on real transcripts; may be absent on malformed/synthetic records, handled per §3.4) by
tool name:

| Tool name | Target field(s) read from `input` |
|---|---|
| `Read`, `Edit`, `Write` | `file_path` |
| `Grep`, `Glob` | `path` (if present) and `pattern` |
| `Bash` | `command` (full string — PR numbers, file paths, and gh references inside it are matched as substrings) |
| `WebSearch`, `WebFetch` | `query` or `url` |
| Any other tool | `input` serialized to a string via `json.dumps` (best-effort catch-all — still exact substring matching, no special parsing) |

### 3.3 Matching algorithm (v1)

For a given claim subject `s` and a tool call's target text `t`:

- **Match** iff `s` (case-sensitive for paths/identifiers, case-insensitive for PR numbers written
  as `PR #N` vs `#N`) appears as a **substring** of `t`, or vice versa (handles the case where the
  claim quotes a longer path than the tool call's arg, e.g. claim says
  `scripts/first_turn_contract_probe.py`, tool call's `file_path` is an absolute path ending in
  the same suffix — substring containment in either direction covers both truncation directions).
- For file paths specifically: additionally match if the **basename** (`os.path.basename`) of the
  claim subject equals the basename of the target field, to tolerate absolute-vs-relative path
  differences without inventing fuzzy logic.
- No thresholds, no edit-distance, no scoring. This is exact/substring/basename matching only —
  deliberately conservative per this repo's no-fabricated-numbers rule (a similarity threshold
  would be exactly such a fabricated number, and none is introduced here).

C3 **violates** iff: a Pillar heading exists, AND ((no qualifying tool call exists at all — same
as today's presence check, preserved as a subcase) OR (qualifying tool calls exist, but for every
extracted claim subject, no qualifying tool call's target matches it)).

Equivalently: if at least one claim subject is extracted, C3 passes iff at least one qualifying
tool call matches at least one extracted subject. If zero claim subjects are extracted, see §3.4.

### 3.4 Un-extractable subject — explicit fallback (required by intake)

If the Pillar section's text yields **zero** claim subjects under §3.1's extraction rules (e.g.
the claim is prose with no path, PR number, backticked identifier, or quoted query — "Pillar:
the fix behaves correctly"), the check **falls back to today's presence-only behavior**: C3
violates iff no qualifying tool call exists at all anywhere before the turn (the original,
unmodified check). This is a deliberate, named fallback — it does not silently treat an
un-extractable claim as "matched" or "passed for free" beyond what the current, already-shipped
behavior does. It also does not make the check stricter than today for prose-only claims, which
is a conscious choice: tightening presence-only claims further (e.g. requiring *any* named
subject to exist) is a stricter posture change than "fix the matching gap," is not requested by
the intake, and is called out as an open question (§7) rather than decided here.

---

## 4. Complete v1 Behavior Table

| Pillar section subjects extracted | Qualifying tool calls exist | At least one target matches a subject | C3 result |
|---|---|---|---|
| ≥1 | No | — | Violation (unchanged from today) |
| ≥1 | Yes | Yes | Pass |
| ≥1 | Yes | No (all calls target something else) | **Violation — this is the exact gap being closed** |
| 0 (un-extractable) | No | — | Violation (unchanged from today — presence-only fallback, §3.4) |
| 0 (un-extractable) | Yes | n/a | Pass (unchanged from today — presence-only fallback, §3.4) |

`build_reason`'s C3 message is extended (not replaced) to name the unmatched subject(s) when the
violation is a matching failure rather than a pure absence failure, e.g.:

> "C3 violation: a Pillar heading was asserted (quoted: "...") whose claimed subject(s)
> (`scripts/foo.py`) do not match any qualifying tool call recorded before it — the qualifying
> call(s) present target something else. Run the verifying tool call(s) for these specific
> claims before reporting them."

vs. the existing absence message (unchanged) when zero qualifying calls exist at all. This
distinction directly answers Open Question 2 from the intake: **yes**, the reason string is
strengthened to say what was actually missing (a matching call, not just any call), for
track-record diagnostic value — this is a string content addition, not a schema change to
`write_track_record`.

---

## 5. Acceptance Criteria

Builds on, does not replace, the existing 12 C3 tests. All existing 16 tests (4 non-C3 + 12 C3)
must continue passing except where a listed AC below explicitly says an existing test's
*expectation* changes (none are expected to — the presence-only paths in the table above are
unchanged; only the "qualifying calls exist but for a different claim" path is new). At minimum,
add tests covering:

1. **True positive**: Pillar section names a file path; a `Read`/`Edit`/`Write` tool call on
   exactly that path (or same basename) precedes the turn → C3 passes.
2. **True negative — the exact gap being closed**: Pillar section names file path A; a qualifying
   tool call exists but targets unrelated file path B (no substring/basename match, no other
   subject overlap) → C3 violates, with the "subject(s) do not match" reason variant.
3. **Un-extractable subject fallback**: Pillar section is prose with no path/PR/identifier/query
   → falls back to presence-only check; verify both sub-cases (no qualifying call → violation;
   any qualifying call → pass), matching §3.4 exactly.
4. **PR-number match**: Pillar claims "PR #42 was reviewed"; a `Bash` tool call with
   `gh pr view 42` in its `command` precedes the turn → C3 passes; a call referencing `#7` does
   not → violates.
5. **Multiple subjects, partial match**: Pillar section names two files; a tool call matches only
   one → C3 passes (per §3.3's "at least one subject matches" rule — a partial-coverage decision,
   not a require-all-subjects decision; documented explicitly so it isn't mistaken for an
   oversight — see §7 for whether require-all should be a future tightening).
6. **Absolute vs. relative path basename match**: claim quotes a relative path, tool call's
   `file_path` is absolute with the same basename → C3 passes via the basename fallback in §3.3.
7. **Non-C3 regression check**: all existing C1/C2 tests and the 4 non-C3 tests pass unmodified.

---

## 6. Integration Boundary

- Changes are confined to `check_c3_violation` and new private helper functions it calls directly
  (e.g. `_extract_claim_subjects(pillar_section_text)`, `_extract_tool_target(tool_name, tool_input)`,
  `_subject_matches_target(subject, target)`) inside `scripts/first_turn_contract_probe.py`.
- `run()`'s call site (`c3_violation = check_c3_violation(records, current_turn_index, pillar_idx)`)
  gains one additional argument: the Pillar section's text slice (needed for subject extraction,
  since today's `pillar_idx` alone doesn't carry section boundaries). Signature becomes
  `check_c3_violation(records, current_turn_index, pillar_idx, pillar_section_text)`, sourced from
  `last_assistant_message` in `run()` using the existing line-split/`pillar_idx` machinery already
  present in `find_pillar_heading_line`. No other call sites exist (verified: `check_c3_violation`
  is called once, from `run()`).
- Does not get authority over C1 or C2 (`c1_violation`/`c2_violation` computation is untouched).
- Does not get authority over the first-turn-only scope decision (`analyze_queue_injection_and_first_turn`
  and its `if not first_turn` short-circuit in `run()` are untouched).
- Does not get authority over Frank's or a human's judgment — same as today, this is one
  mechanical check among three, feeding into the same `violations` list and `build_reason`.

---

## 7. Open Questions (not resolved here — carried from Intake + one new one)

1. **Multiple Pillar sections in one turn** (Intake OQ1, partially answered): this spec's v1
   extracts subjects only from the first (`pillar_idx`) Pillar section, consistent with the file's
   existing single-`pillar_idx` model. Extending to *every* Pillar section in a multi-Pillar turn
   requires widening `find_signpost_pillar_positions`'s return shape (currently first-occurrence
   only) and is out of scope for this fix — flagged for a follow-up, not decided here.
2. **Require-all-subjects vs. require-any-subject** (§5 AC 5): v1 requires at least one extracted
   subject to match (partial coverage passes). Whether *every* named subject in a Pillar section
   should require its own matching call is a stricter design decision the intake did not request
   and this spec does not make unilaterally — needs Danny's call if desired as a future tightening.
3. **DDR-004 status-line update** (Intake OQ3): whether merging this fix changes DDR-004's status
   line from "ACCEPTED (gap noted)" to something else, and whether this sprint's own
   PROGRESS/GATE-LOG should cite DDR-004 explicitly as parent — a process/documentation decision,
   not an architecture one; left for the forge/PR step to resolve with Danny, not fabricated here.

No numeric threshold, similarity score, or fuzzy-matching constant appears anywhere in this spec;
matching is exact substring/basename containment only, per the intake's explicit constraint.
