# Roadmap: Unsourced-Threshold Provenance Hook — Extension of the Incumbent

**Status**: Draft (awaiting Frank's spec-gate + human approval)
**Traces to**: `01-REQUIREMENTS.md`, `02-ARCHITECTURE.md` §1–§13 (extension design, supersedes prior
from-scratch roadmap in full)

**Scope**: extend the incumbent `.claude/hooks/domain-boundary-provenance.sh` +
`scripts/domain_boundary_provenance_probe.py` in place, per Architecture §1. No new/second hook. No
retrofit into other repos (agent-rig build only, Out of Scope).

This roadmap replaces the prior version's slice structure, which was built against a discarded
from-scratch Stop-hook design and does not match the current, authoritative Architecture doc. No
unit below creates a new probe/wrapper file, a new detection function outside the existing probe
file, or a new hook registration.

---

## Dependency Map

| Unit | Depends On |
|---|---|
| `run_cross_domain_pass()` extraction (incumbent steps 2–7, logic unchanged) | — |
| `load_mode_config()` + `docs/tooling/domain-boundary-mode.json` | — |
| `detect_threshold_literals()` (§2 AST rule, 2 shape-based contexts + exclusions) | — |
| `has_threshold_provenance_marker()` (§4, 5-line window reusing incumbent's `PROXIMITY_WINDOW`, `THRESHOLD-PROVENANCE:` marker) | — |
| `run_local_threshold_pass()` | `detect_threshold_literals`, `has_threshold_provenance_marker` |
| `combine()` (§3 combination rule, mode-aware) | `run_cross_domain_pass`, `run_local_threshold_pass`, `load_mode_config` |
| `TrackRecordEntry` schema migration (§6, nested `cross_domain`/`local_threshold`) | `combine` |
| `run()` restructure (two passes → one decision → one write) | all of the above |
| `.claude/hooks/domain-boundary-provenance.sh` updates (probe_error fallback entry shape, comment updates, wrapper-side mode-config read) | `run()` restructure (schema must be final) |
| `.claude/settings.json` wiring (new `PreToolUse` entry) | wrapper (unchanged path, already correct) |
| `docs/tooling/domain-boundary-provenance-hook.md` addendum | `run()` restructure, wiring |
| `HOOK-DEPLOYMENT-ROSTER.md` status update | wiring |
| Test corpus additions (`tests/fixtures/domain_boundary_corpus.json` + new local-threshold fixtures, incl. `PROXIMITY_WINDOW` self-scan not-flagged case) | `detect_threshold_literals`, `has_threshold_provenance_marker`, `combine` |

No circular dependencies: each unit depends only on units listed above it.

---

## Slice Overview

| Slice | Goal | Depends On | Files |
|---|---|---|---|
| 1 | Extract incumbent's existing cross-domain logic into `run_cross_domain_pass()` — pure refactor, no behavior change | — | `scripts/domain_boundary_provenance_probe.py`, `tests/test_domain_boundary_provenance_probe.py` (existing tests must still pass unmodified) |
| 2 | Mode config loader + committed config file | — | `scripts/domain_boundary_provenance_probe.py` (add `load_mode_config`), `docs/tooling/domain-boundary-mode.json` (new), `tests/test_domain_boundary_provenance_probe.py` (add cases) |
| 3 | `detect_threshold_literals()` — AST detection, 2 shape-based contexts + exclusions | — | `scripts/domain_boundary_provenance_probe.py` (add fn + `FlaggedLiteral`), `tests/test_domain_boundary_provenance_probe.py` (add cases) |
| 4 | `has_threshold_provenance_marker()` — 5-line window (reuses incumbent's `PROXIMITY_WINDOW`), `THRESHOLD-PROVENANCE:` marker | — | `scripts/domain_boundary_provenance_probe.py` (add fn only, no new constant) |
| 5 | `run_local_threshold_pass()` — composes Slices 3–4, gated on `.py` + non-test path, not manifest | Slices 3, 4 | `scripts/domain_boundary_provenance_probe.py` (add fn + `PassResult`) |
| 6 | `combine()` — two-pass combination rule, mode-aware, labeled concatenated reason text | Slices 1, 2, 5 | `scripts/domain_boundary_provenance_probe.py` (add fn + `CombinedResult`) |
| 7 | `TrackRecordEntry` schema migration + `run()` restructure — single write per invocation, both passes' findings folded in | Slice 6 | `scripts/domain_boundary_provenance_probe.py` (edit `run()`, `write_track_record`, `build_track_record_entry`) |
| 8 | Wrapper updates — `write_probe_error` fallback entry shape matches migrated schema, and the wrapper itself reads the mode config for `mode`; timeout-comment and any hardcoded schema fields updated | Slice 7 | `.claude/hooks/domain-boundary-provenance.sh` |
| 9 | Test corpus additions — new local-threshold fixtures (one per context + each exclusion), the `PROXIMITY_WINDOW` self-scan not-flagged case documented as a fixture, and a grep-based test for US-4 AC2 (no soundness-implying language in reason/log text, G-4) | Slices 1–8 | `tests/fixtures/domain_boundary_corpus.json` (edit, add cases), `tests/test_domain_boundary_provenance_corpus.py` (edit, add assertions), new grep-based test file or added case in existing suite |
| 10 | Live wiring — `.claude/settings.json` gains `PreToolUse` entry (currently absent) | Slices 1–9 | `.claude/settings.json` |
| 11 | Documentation — LOCKED spec addendum + roster status update | Slice 10 | `docs/tooling/domain-boundary-provenance-hook.md` (addendum section, additive only — §2–§10 untouched), `HOOK-DEPLOYMENT-ROSTER.md` (status row update) |
| 12 | End-to-end verification — live run against agent-rig's own codebase under `log_only` | Slices 1–11 | none new — verification only |

---

## Slice Detail

### Slice 1: Extract `run_cross_domain_pass()`

**Goal:** Refactor the incumbent's existing steps 2–7 (manifest load, normalize, glob match,
identifier scan, `DOMAIN-BOUNDARY:` window check) into a named function `run_cross_domain_pass(project_dir, tool_input, scan_surface) -> PassResult`, with zero logic change. This is a pure
extraction to enable composition (§3) — Architecture §1/§3 requires this pass be reusable as-is.

**Depends On:** —

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit (extract function, no behavior change)
- `tests/test_domain_boundary_provenance_probe.py` — no new tests required, but must pass
  unmodified (regression check)

**Implementation Notes:**
- `PassResult` TypedDict per Architecture §7: `ran`, `matches_found`, `matches_cited`, `unmarked`,
  `detail`.
- Every existing incumbent test must pass without modification — this slice proves the extraction
  preserved behavior before anything new composes on top of it.

**Tests:**
- [ ] All existing `test_domain_boundary_provenance_probe.py` and
  `test_domain_boundary_provenance_corpus.py` tests pass unmodified.
- [ ] `run_cross_domain_pass` returns a `PassResult` whose fields are derivable from the pre-refactor
  code's decision path (byte-identical decision outcomes across the existing fixture corpus).

**Done When:**
- [ ] All tests pass, including full pre-existing suite with zero modifications.
- [ ] `run_cross_domain_pass` signature matches Architecture §7 exactly.
- [ ] Diff shows extraction only — no incumbent decision logic altered.

---

### Slice 2: Mode Config Loader

**Goal:** `load_mode_config(project_dir) -> str` reads `docs/tooling/domain-boundary-mode.json`,
returns `"log_only"` on any absence, read failure, or schema-invalid content (fail-safe default,
§5). Ship the config file itself, committed with `{"schemaVersion": 1, "mode": "log_only"}`.

**Depends On:** —

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit, add `load_mode_config`
- `docs/tooling/domain-boundary-mode.json` — create, `{"schemaVersion": 1, "mode": "log_only"}`
- `tests/test_domain_boundary_provenance_probe.py` — edit, add cases

**Implementation Notes:**
- Discovery relative to `$CLAUDE_PROJECT_DIR`, same convention as the manifest.
- Sibling file to the manifest, not a manifest field (Architecture §5 rationale — mode is shared
  across both passes).

**Tests:**
- [ ] Absent config file → `"log_only"`.
- [ ] Malformed JSON → `"log_only"`.
- [ ] Missing `mode` key or invalid `mode` value → `"log_only"`.
- [ ] Valid `{"mode": "blocking"}` → `"blocking"`.
- [ ] Valid `{"mode": "log_only"}` → `"log_only"`.

**Done When:**
- [ ] All tests pass.
- [ ] `docs/tooling/domain-boundary-mode.json` committed with exactly the specified initial value.

---

### Slice 3: `detect_threshold_literals()`

**Goal:** AST-based detection of threshold-shaped literals per Architecture §2 — the three
contexts (comparison operand; name-gated default-kwarg/assignment; slice/truncation argument) and
the four explicit exclusions (`range()` bounds, non-slice-stop index, test/tests/fixtures path
component, literal set `{0, 1, -1, 2}`).

**Depends On:** —

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit, add `detect_threshold_literals` and
  `FlaggedLiteral` TypedDict
- `tests/test_domain_boundary_provenance_probe.py` — edit, add cases

**Implementation Notes:**
- Operates on `scan_surface` text only via `ast.parse`, never reads `file_path` from disk;
  `file_path` used only for the `.py`/test-path exclusion checks (Architecture §7 docstring is the
  contract).
- Syntax error on `ast.parse` → return `[]` (fail-open on unparsable partial-edit fragment, not a
  crash).
- Name-gated context (former context 2) is REMOVED per Architecture §2's redesign — measured
  8/10 words never fire in this repo and substring matching produced 11 measured false positives
  (`cap` inside `escaped_rest`, `min` inside `REMINDER_PATH`/`REMINDER_TEXT`/`_load_reminder`).
  Only two shape-based contexts remain: comparison operand, slice/truncation argument.
- `{0, 1, -1, 2}` exclusion set is NOT YET BENCHMARKED — carries the full executable validation
  plan from Architecture §2 (unfiltered scan of roster corpus, JSONL dump, 200-row stratified
  hand-labeled sample, exclude only if measured precision < 5%). Not to be treated as validated
  until that plan runs. `range()` bound exclusion is a language fact (Python spec: `range()` takes
  1-3 positional args), not a benchmarked value — no PROVISIONAL tag needed for it.

**Tests:**
- [ ] Each of the 2 shape-based contexts flags a matching literal (one case per context).
- [ ] `range()` bounds (all 3 positional argument positions) are not flagged.
- [ ] Non-slice-stop index (`x[i]`) is not flagged; slice-stop (`x[:50000]`) is flagged.
- [ ] Literals `0, 1, -1, 2` are never flagged in any context (current unbenchmarked exclusion set).
- [ ] Files under a `test`/`tests`/`fixtures` path component produce no flags.
- [ ] A name-shaped assignment (e.g. `MAX_RETRIES = 500`) that is not itself a comparison operand
  or slice/truncation argument is NOT flagged — regression test confirming the name-gated context
  was actually removed, not just left unused.
- [ ] No domain-crossing/import-graph check exists anywhere in this function (structural test: grep
  the function body for import-related AST node types — none gate a flag decision).
- [ ] Syntax-error input returns `[]`, does not raise.

**Done When:**
- [ ] All tests pass.
- [ ] Function signature matches Architecture §7 exactly:
  `detect_threshold_literals(file_path: str, scan_surface: str) -> list[FlaggedLiteral]`.
- [ ] `FlaggedLiteral` TypedDict matches Architecture §7 exactly (`line_index`, `context`,
  `literal_repr`).

---

### Slice 4: `has_threshold_provenance_marker()`

**Goal:** Citation check against the new `THRESHOLD-PROVENANCE:` marker (Architecture §4), reusing
the incumbent's existing 5-line `PROXIMITY_WINDOW` constant rather than introducing a second window
constant.

**Depends On:** —

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit, add `has_threshold_provenance_marker`
  (no new module-level constant — reuses the incumbent's existing `PROXIMITY_WINDOW = 5`, probe
  L51, per Architecture §4/§7)

**Implementation Notes:**
- Marker string is exact, case-sensitive `THRESHOLD-PROVENANCE:` followed by non-whitespace content
  on the same comment line.
- Window is 5 lines inclusive above or below the flagged literal's line (the incumbent's existing
  `PROXIMITY_WINDOW` value), within `scan_surface` only. The prior draft's separate
  `PROXIMITY_WINDOW_THRESHOLD = 3` constant is dropped — benchmark-measured wrong (13/40, 32.5%, of
  real commented constants in this repo start their comment 4-5 lines above the assignment, so a
  3-line window would miss them) and internally self-contradictory (a required 5-line comment block
  cannot land within a 3-line window of the literal it documents — the self-refuting bug from the
  prior draft). See Architecture §4 for the full correction.
- A `THRESHOLD-PROVENANCE: PROVISIONAL — ...` line is a valid, complete citation (satisfies
  option b) — this function only checks marker presence within the window, not which of the three
  satisfying forms is used (that distinction is not needed here; presence is presence).
- **No self-scan special case remains (Architecture §8, resolved).** With the name-gated context
  removed (Slice 3) and no new window constant introduced, no module-level constant in this probe
  file is flagged by the local-threshold pass purely because of its name. No special comment
  obligation applies to `PROXIMITY_WINDOW` beyond what the incumbent already carries.

**Tests:**
- [ ] Marker on same line as literal is detected.
- [ ] Marker 1-5 lines above/below is detected; 6 lines above/below is not.
- [ ] Marker text without non-whitespace content after `THRESHOLD-PROVENANCE:` does not satisfy.
- [ ] A `DOMAIN-BOUNDARY:` marker or bare `PROVISIONAL` (no `THRESHOLD-PROVENANCE:` marker string)
  does not satisfy this check (distinct marker, not interchangeable — direct regression test for
  Architecture §4's "not `DOMAIN-BOUNDARY:`, not bare `PROVISIONAL`" decision).
- [ ] `PROXIMITY_WINDOW = 5` (an assignment, not a comparison/slice literal) is not itself flagged
  by the local-threshold pass when this probe file is scanned (self-scan regression, Architecture
  §8).

**Done When:**
- [ ] All tests pass.
- [ ] Function signature matches Architecture §7 exactly.
- [ ] No new module-level window constant is introduced — `has_threshold_provenance_marker` uses
  the incumbent's existing `PROXIMITY_WINDOW` (structural check: no `PROXIMITY_WINDOW_THRESHOLD`
  or equivalent second constant exists in the committed source).

---

### Slice 5: `run_local_threshold_pass()`

**Goal:** Compose Slices 3–4 into the new pass function, gated only on `raw_file_path` ending in
`.py` and no `test`/`tests`/`fixtures` path component — never gated by manifest presence
(Architecture §3's "No manifest coupling").

**Depends On:** Slices 3, 4

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit, add `run_local_threshold_pass` and
  `PassResult` reuse (same TypedDict as Slice 1, per Architecture §7)

**Implementation Notes:**
- Signature: `run_local_threshold_pass(tool_name, raw_file_path, scan_surface, mode) -> PassResult`.
- `mode` parameter is accepted here per Architecture §7's signature but the mode-based
  deny→flag downgrade itself happens in `combine()` (Slice 6), not inside this function — keep the
  boundary exactly as Architecture §3's pseudocode draws it.
- `detail` field carries `file_scanned` (bool) for the track-record schema (§6).

**Tests:**
- [ ] Non-`.py` file → `ran: False`, no detection attempted.
- [ ] Test-path `.py` file → `ran: False` (excluded), consistent with Slice 3's own exclusion (no
  double-exclusion logic drift between this function and `detect_threshold_literals`).
- [ ] In-scope `.py` file with an unmarked flagged literal → `unmarked` populated, `matches_found`
  reflects count.
- [ ] In-scope `.py` file with a marked flagged literal (via Slice 4) → `matches_cited` reflects
  count, `unmarked` empty for that literal.
- [ ] Absence of a manifest (no `domain-boundary-manifest.json` in the fixture repo) does not affect
  this function's output — direct regression test for "no manifest coupling."

**Done When:**
- [ ] All tests pass.
- [ ] Function signature matches Architecture §7 exactly.

---

### Slice 6: `combine()`

**Goal:** Two-pass combination rule per Architecture §3 — mode-aware, single deny-or-allow decision,
concatenated labeled reason text when both passes deny.

**Depends On:** Slices 1, 2, 5

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit, add `combine` and `CombinedResult`

**Implementation Notes:**
- `mode="log_only"`: any would-deny pass downgrades to a track-record `decision: "flag"` entry;
  the `PreToolUse` call always emits allow (nothing).
- `mode="blocking"`: denies if either pass has unmarked matches; if both deny, `reason` string
  concatenates both, each clearly labeled (`[domain-boundary]` / `[threshold-provenance]`).
- If only one pass denies, that pass's reason is used unmodified (no label prefix required when
  there's only one source, per Architecture §3 — confirm against Architecture §3's exact wording
  before diverging; if ambiguous, prefer always labeling for consistency and simplicity — flag
  choice in code comment, not a spec deviation).

**Tests:**
- [ ] `log_only`, one pass would-deny → combined decision is `"flag"`, `PreToolUse` output is
  allow (empty).
- [ ] **Named test (F1, Frank spec-gate attempt 1):** `test_cross_domain_pass_flag_under_log_only`
  — a fixture that would deny under the incumbent's unmodified cross-domain logic (an unmarked
  in-scope manifest match, the exact LOCKED-doc §6 step 6 / AC4 scenario) resolves to combined
  decision `"flag"`, not `"deny"`, when `mode == "log_only"`. This is the direct regression test
  for the LOCKED-doc behavior-change note in Architecture §3/§6/§11.
- [ ] `blocking`, cross-domain pass denies alone → single unlabeled-or-labeled reason from that pass
  only (per Implementation Note above), decision `"deny"`.
- [ ] `blocking`, local-threshold pass denies alone → same, from that pass only.
- [ ] `blocking`, both passes deny → reason contains both labels and both passes' content.
- [ ] Both passes pass/find nothing → decision `"allow"` regardless of mode.

**Done When:**
- [ ] All tests pass.
- [ ] `combine` signature and `CombinedResult` match Architecture §7 exactly.
- [ ] No code path allows more than one `{"decision": "block", ...}` payload to be constructed for
  emission (structural check — single deny-schema constraint, Architecture §3).

---

### Slice 7: `TrackRecordEntry` Schema Migration + `run()` Restructure

**Goal:** Migrate `TrackRecordEntry` to the nested `cross_domain`/`local_threshold` shape
(Architecture §6, breaking/clean-cutover change — no historical log data to preserve), and
restructure `run()` to perform both passes, call `combine()`, and write exactly one track-record
entry per invocation.

**Depends On:** Slice 6

**Files:**
- `scripts/domain_boundary_provenance_probe.py` — edit `run()`, `write_track_record`,
  `build_track_record_entry`

**Implementation Notes:**
- Follow Architecture §3's pseudocode ordering exactly: extract `tool_name`/`tool_input`/
  `project_dir` → early-allow on non-`Edit`/`Write` → `get_scan_surface` (reused, unchanged) →
  both passes → `combine()` → `write_track_record(combined)` → emit.
- `mode` is read once via `load_mode_config()` at the top of `run()`, passed as a plain argument
  into `combine()` — not re-read anywhere else (Architecture §8's disposition of G-7).
- New `decision` value `"flag"` added to the existing `"allow" | "deny" | "probe_error"` union.
- This is a breaking schema change to the gitignored, never-yet-populated track-record log — clean
  cutover per Architecture §6's migration note, no versioned-log reconciliation needed.

**Tests:**
- [ ] `run()` on a stdin fixture with no matches in either pass → one `TrackRecordEntry` written,
  `decision: "allow"`, both nested objects populated with zero/null counts as appropriate.
- [ ] `run()` on a fixture triggering only the cross-domain pass (manifest-gated scenario,
  unchanged from incumbent's own existing corpus) → nested `cross_domain` object reflects it,
  `local_threshold.file_scanned` reflects whether the file was also `.py`-eligible.
- [ ] `run()` on a fixture triggering only the local-threshold pass (same-file magic number, no
  manifest match) → nested `local_threshold` object reflects it.
- [ ] `run()` on a fixture triggering both passes → combined single entry, both nested objects
  populated, single `decision` value per `combine()`'s rule.
- [ ] Exactly one `write_track_record` call occurs per `run()` invocation (structural/call-count
  test) — no double-write across the two passes.

**Done When:**
- [ ] All tests pass.
- [ ] `TrackRecordEntry` schema matches Architecture §6 exactly, including the `mode` field and
  `"flag"` decision value.
- [ ] Existing incumbent tests updated only where the schema migration requires it (field
  restructuring), with no unrelated decision-logic changes — diff review confirms this.

---

### Slice 8: Wrapper Updates

**Goal:** Update `.claude/hooks/domain-boundary-provenance.sh`'s `write_probe_error` fallback entry
to match the migrated `TrackRecordEntry` schema (Slice 7), so a wrapper-level failure (timeout,
non-zero exit, malformed stdout) writes a schema-conformant entry rather than the old flat shape —
**and, per Architecture §6's resolution of 05-REVIEW.md G-5, the wrapper itself reads
`docs/tooling/domain-boundary-mode.json` to populate the `mode` field on any `probe_error` entry it
constructs. `mode` is never `null`.**

**Depends On:** Slice 7

**Files:**
- `.claude/hooks/domain-boundary-provenance.sh` — edit

**Implementation Notes:**
- The wrapper's own inline Python `write_probe_error` block (lines ~39–84 as currently written)
  constructs a `TrackRecordEntry` dict literal directly — this must be updated field-for-field to
  the nested `cross_domain`/`local_threshold`/`mode` shape.
- **`mode` is non-nullable.** The wrapper must read `docs/tooling/domain-boundary-mode.json` itself
  at the point it constructs a `probe_error` entry, applying the identical fail-safe default
  `load_mode_config` uses: file absent, unreadable, or schema-invalid → `"log_only"`; otherwise the
  file's `mode` value verbatim (Architecture §6). A minimal shell-native read (`jq -r` if available,
  falling back to `grep`/`sed` extraction, falling back to `"log_only"` on any non-zero exit or
  empty result) is sufficient — the wrapper does not need a full JSON parser, only this one field.
  Fields the wrapper genuinely cannot determine (it never runs the passes) may remain `null`/`None`
  — this applies to `cross_domain`/`local_threshold` detail fields, not to `mode`.
- No change to the wrapper's control flow (timeout handling, exit-code branching, stdout
  validation) — this slice touches only the embedded schema literal plus the new mode-config read,
  per Architecture §1's "same wrapper file, extended" framing (schema-shape update, not a logic
  redesign).
- Trigger surface, `Edit`/`Write` matching, and the bounded-timeout/fail-open shape are unchanged
  (Architecture §1 table).

**Tests:**
- [ ] `tests/test_domain_boundary_provenance_wrapper.sh` — existing timeout/malformed-output/
  non-zero-exit cases still pass, and the resulting logged entry (when inspected) matches the new
  nested schema, not the old flat one.
- [ ] A `probe_error` entry constructed with `docs/tooling/domain-boundary-mode.json` absent has
  `mode: "log_only"` (fail-safe default, wrapper-side).
- [ ] A `probe_error` entry constructed with the mode config present and set to `"blocking"` has
  `mode: "blocking"`.
- [ ] `mode` is never written as `null`/`None` in any `probe_error` entry produced by the wrapper,
  across the above cases.

**Done When:**
- [ ] All wrapper tests pass.
- [ ] Diff shows the `write_probe_error` dict-literal update plus the new mode-config read — no
  other control-flow change.
- [ ] No code path in the wrapper writes `null` for `mode` on a `probe_error` entry.

---

### Slice 9: Test Corpus Additions

**Goal:** Extend the existing fixture corpus and test suites with local-threshold-pass cases,
combination-rule cases, the documented `PROXIMITY_WINDOW` self-scan not-flagged case (Architecture
§8, simplified this revision — no second window constant exists to need a distinct "cited" case),
and a grep-based test satisfying US-4 AC2 / Architecture §8's G-4 disposition.

**Depends On:** Slices 1–8

**Files:**
- `tests/fixtures/domain_boundary_corpus.json` — edit, add local-threshold and combined-pass cases
- `tests/test_domain_boundary_provenance_corpus.py` — edit, add assertions consuming the new fixture
  cases
- `tests/test_domain_boundary_provenance_probe.py` — edit, add a grep-based test for the reason/log
  string template (no "verified correct"/"sound"/"validated"-type soundness-implying language)

**Implementation Notes:**
- Include a fixture case matching Architecture §8's G-9 finding: `PROXIMITY_WINDOW` (the
  incumbent's own constant, value 5, unchanged) is an assignment, not a comparison operand or
  slice/truncation argument, so it is never in scope for the redesigned shape-only rule (§2) — no
  name-gate to fire on since that context was removed entirely. Document this as a fixture asserting
  the constant is NOT flagged, with a code comment pointing at Architecture §8 so a future reader
  doesn't mistake the fixture for an oversight. There is no second, "self-scan cited" case to add —
  the prior draft's `PROXIMITY_WINDOW_THRESHOLD` constant and its associated cited-case fixture no
  longer exist, since no second window constant is introduced by this design (§4/§7).
- Grep-based test (G-4/US-4 AC2): assert that no track-record `reason` string, hook output string,
  or user-facing log message anywhere in the probe/wrapper source asserts or implies a citation's
  correctness — check literal string templates, not runtime output alone.
- Each of the two shape-based detection contexts, each of the four exclusions, both citation-satisfying forms
  (citation vs. named-owner PROVISIONAL), and the unowned-PROVISIONAL-treated-as-absent edge case
  (Requirements Edge Cases table) each need at least one fixture case if not already covered by
  Slices 3–4's unit tests — this slice is about corpus-level (integration) coverage, not
  duplicating unit tests.

**Tests:**
- [ ] All new fixture cases pass under `run()`/`combine()` end-to-end (not just the unit-level
  functions from Slices 3–6).
- [ ] `PROXIMITY_WINDOW` self-scan fixture case passes (confirms the constant is not flagged,
  since it is never a comparison/slice literal under the redesigned shape-only rule).
- [ ] Grep-based soundness-language test passes.

**Done When:**
- [ ] All tests pass.
- [ ] Corpus file diff is additive only — no existing fixture case removed or altered.
- [ ] Corpus contains the `PROXIMITY_WINDOW` self-scan not-flagged case — verified by direct
  read of the corpus file, not assumed from test pass/fail alone.

---

### Slice 10: Live Wiring

**Goal:** Add the `PreToolUse` entry to `.claude/settings.json` for
`.claude/hooks/domain-boundary-provenance.sh` — currently absent from the live config (Architecture
§5, confirmed by direct read). This wires both the incumbent cross-domain pass and the new
local-threshold pass live, for the first time, under `log_only`.

**Depends On:** Slices 1–9

**Files:**
- `.claude/settings.json` — edit (additive only)

**Implementation Notes:**
- Match `Edit`/`Write` tool names, per the incumbent's existing (already-correct, unwired) design.
- This is the first live wiring of the incumbent hook at all, not just the new pass — treat with
  the same caution Architecture §5 assigns: `docs/tooling/domain-boundary-mode.json` must already
  be `log_only` (Slice 2) before this slice runs.

**Tests:**
- [ ] `.claude/settings.json` is valid JSON after edit.
- [ ] No existing hook entry is modified, reordered, or removed (byte-diff check on unrelated
  entries).
- [ ] New entry present, correctly shaped, matching the existing entries' object structure.

**Done When:**
- [ ] All tests pass.
- [ ] A live Claude Code `Edit`/`Write` call triggers the hook (manual verification), producing a
  track-record entry with `mode: "log_only"` and no session block.

---

### Slice 11: Documentation

**Goal:** Append an addendum section to the LOCKED `docs/tooling/domain-boundary-provenance-hook.md`
pointing at `02-ARCHITECTURE.md` for the composed local-threshold behavior (additive only — §2–§10
of that doc remain untouched, per Architecture §11), and update `HOOK-DEPLOYMENT-ROSTER.md`'s
existing `domain-boundary-provenance` (DDR-006) row from "built, unwired" to "built, wired,
`log_only`."

**Depends On:** Slice 10

**Files:**
- `docs/tooling/domain-boundary-provenance-hook.md` — edit, append addendum section only
- `HOOK-DEPLOYMENT-ROSTER.md` — edit, update existing row

**Implementation Notes:**
- **Revised rule (F1, Frank spec-gate attempt 1):** §2–§10 of the LOCKED doc stay byte-identical —
  no edit to their existing text. But the addendum is NOT barred from stating what changed; the
  prior "must not restate or contradict §2–§10" framing incorrectly forbade naming a real behavior
  change. The addendum records, in its own words, that §6 step 6 / AC4's "deny" semantics are now
  gated by `docs/tooling/domain-boundary-mode.json` (Architecture §3's reconciliation paragraph,
  §5, §11): under `mode == "blocking"`, the LOCKED doc's original unconditional deny still holds
  exactly as written; under the shipped default `mode == "log_only"`, that same condition now
  produces `decision: "flag"` (§6) and the call allows. The addendum points outward to Architecture
  §3/§5/§6 for the full mechanism rather than duplicating it, but it must not omit or soften the
  fact that the outcome changed.
- Roster update is a status-field edit only, consistent with this repo's Decision Discipline
  (decision-gate status and deployment status are separate claims, per prior feedback captured in
  this repo — do not bundle "wired" and "verified end-to-end" into one status string; Slice 12
  covers verification separately).

**Tests:** (documentation slice — no automated tests)
- [ ] Addendum reviewed against actual shipped code (Slices 1–10) for accuracy, not against the
  architecture doc's design intent alone.

**Done When:**
- [ ] LOCKED doc's §2–§10 are byte-identical to their pre-sprint state; only the new addendum
  section is added.
- [ ] Roster row accurately reflects wired/`log_only` status, distinct from any end-to-end
  verification claim.

---

### Slice 12: End-to-End Verification

**Goal:** Run the composed hook for real in agent-rig under `log_only`, confirming fail-open
behavior, single-entry-per-invocation logging, and that no pre-existing agent-rig code causes a
session block (impossible by construction under `log_only`, but confirm the config file's mode
value directly rather than assuming).

**Depends On:** Slices 1–11

**Files:** none new — verification only. §2's exclusion-set benchmarking plan (unfiltered
roster-corpus scan, 200-row stratified sample, per Architecture §2) is separate future work, not
part of this slice's deliverable; any resulting change to the `{0, 1, -1, 2}` exclusion set is a
follow-up edit to `02-ARCHITECTURE.md`, tracked separately.

**Tests:**
- [ ] At least one real `Edit`/`Write`-triggered run completes and appends a single, schema-valid
  track-record entry, with no session block.
- [ ] `docs/tooling/domain-boundary-mode.json`'s committed value is directly confirmed as
  `log_only` at verification time (not assumed from Slice 2's Done-When alone).
- [ ] Observed probe runtime is recorded (for future timeout re-validation), even if not acted on
  in this slice.
- [ ] At least one live run against this repo's own pre-existing same-file magic numbers surfaces a
  `"flag"` decision in the track-record log (confirms the widened blast radius US-2 anticipates is
  actually observed, not just theorized).

**Done When:**
- [ ] Verification run(s) complete, log entries confirmed schema-valid by direct inspection.
- [ ] Findings (runtime, any lookback-window misses, any unexpectedly-noisy false-positive class)
  captured as a LORE entry or an architecture-doc comment for future PROVISIONAL-value revisit —
  this slice surfaces the data, it does not resolve the PROVISIONAL tags itself.

---

## Sequence Rules

1. Complete each slice fully (tests + Done When) before starting the next.
2. Slices 1–4 have no mutual dependency and may be built in any order relative to each other, but
   each must independently pass its own tests before Slice 5 begins (Slice 5 needs 3 and 4; Slice 6
   needs 1, 2, and 5).
3. If blocked → HALT, do not skip ahead.
4. No new slices without human approval.
5. Slice 10 (`.claude/settings.json` edit — live wiring) is the only slice that changes hook
   registration — keep it isolated from Slices 8–9 and 11, on its own for reviewability, same
   discipline the prior roadmap applied to its analogous slice.
6. Slice 1 (pure extraction) must land with the full pre-existing test suite passing unmodified
   before any new-pass code is written — this is the regression guard against silently altering the
   incumbent's already-Frank-forge-gate-PASSED cross-domain logic while extending it.

---

## Deferred (Not This Roadmap)

- Retrofit into `gap-lens-dilution-filter`, `market_data`, or any other repo (Out of Scope,
  requirements — separate follow-on sprint, per the existing retrofit-roster pattern).
- Promotion of any repo's hook installation to `blocking` mode (per-repo decision, later).
- Auto-promotion tooling from `log_only` to `blocking`.
- Multi-language support beyond Python (Bash/TS/JSON thresholds unscanned by v1 of either pass).
- Resolving DDR-010 (Gate Assertion-Coverage Check, `market_data`, still DRAFT).
- Running §2's `{0, 1, -1, 2}` exclusion-set benchmarking plan (unfiltered roster-corpus scan,
  JSONL dump, 200-row stratified hand-labeled sample) — the plan is fully specified in Architecture
  §2, but executing it is out of scope for this roadmap; the current exclusion set ships unvalidated
  until that plan runs.
- Tightening the §2 exclusion set based on Slice 12's findings — follow-up work, not a new slice in
  this roadmap.
- Any rewrite, retirement, or redesign of the incumbent's manifest-gated cross-domain check itself
  (schema, trigger, scan surface, `DOMAIN-BOUNDARY:` marker, decision logic) — untouched by this
  sprint per Architecture §1/§11.

---

## HALT Check

No HALT triggered. Both prior docs (`01-REQUIREMENTS.md`, `02-ARCHITECTURE.md`, both rewritten
2026-09-05) are complete and internally consistent under the extend-not-replace design confirmed by
Danny's settled decision (Architecture §0). Every new component named in Architecture §2–§7
(`load_mode_config`, `detect_threshold_literals`, `FlaggedLiteral`, `has_threshold_provenance_marker`,
`run_cross_domain_pass`, `run_local_threshold_pass`, `PassResult`, `combine`, `CombinedResult`, the
migrated `TrackRecordEntry`, the mode config file, the `.claude/settings.json` wiring, the LOCKED-doc
addendum, and the roster update) maps to exactly one slice above. No circular dependencies exist in
the Dependency Map. Each slice touches concrete, already-existing or precisely-named-new file paths
(no placeholder paths) and has testable Done-When criteria. Architecture §8's G-9 self-scan finding (no module-level constant is ever flagged
purely by name under the redesigned shape-only rule — `PROXIMITY_WINDOW` is confirmed not-flagged
by a dedicated fixture, and no second window constant exists to require a "cited" case) and §8's
G-4 finding (no soundness-implying language) are both carried into Slices 4/9 as named fixture/test
obligations rather than left as unaddressed review notes. Architecture §6's resolution of G-5 (`mode`
non-nullable, wrapper reads mode config for `probe_error` entries) is carried into Slice 8's
Done-When explicitly, replacing the prior draft's "write `null` for `mode`" framing. Architecture
§12's five contradictions flagged to `01-REQUIREMENTS.md`/`NORTH-STAR.md` have all been Applied
(confirmed in both documents directly — Frank spec-gate attempt 2 verified this against current
file content, not this roadmap's prior claim) — nothing outstanding there as of 2026-09-05.
