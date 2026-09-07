# Architecture: first-turn-contract-c3-signpost-sourcing

## Summary

`check_c3_violation` currently sources claim subjects from `pillar_section_text` only. This
sprint adds a second, additive source — the Signpost section's text, run through
`_extract_claim_subjects` (extended with two new extraction patterns, see below) — and checks
the **union** of Signpost- and Pillar-sourced subjects against qualifying tool calls. This
sprint also mirrors every `scripts/first_turn_contract_probe.py` edit into
`reference/first_turn_contract_probe.py` (see "Reference Mirror" below) — the two files are
required to stay byte-identical.

## Extraction pattern investigation (revised — supersedes the prior "no new patterns" disposition)

The prior draft of this document concluded no new subject-extraction patterns were needed,
based on `docs/tooling/*-track-record.jsonl`. That corpus structurally never stores section
bodies (only a `reason` string, at most quoting a Pillar heading line) — it was the wrong well
to check, and the conclusion drawn from it is reversed here.

**Direct empirical test against the live regexes in `scripts/first_turn_contract_probe.py`**
(not against the track-record corpus), using real subjects drawn from this sprint's own session
history:

| Subject | Existing coverage | Verified result |
|---|---|---|
| `358448c` (commit SHA, digit-leading) | `_IDENTIFIER_RE = ^[A-Za-z_]\w*$` | **Rejected** — starts with a digit |
| `DDR-006` (decision ID) | `_IDENTIFIER_RE`, `_FILE_PATH_RE`, `_PR_NUMBER_RE` | **Rejected** — hyphenated, no dot, no `#`/`PR` token |
| `recovery/checkpoint-2-from-bfe41c4` (branch name) | `_FILE_PATH_RE`'s slash branch (`[\w\-]+/[\w./\-]+`, no dotted-extension requirement when a `/` is present) | **Already extracted**, as `subject_type="path"` — reverified directly against the compiled regex (`_FILE_PATH_RE.finditer` matches the full string). The original task brief's claim that this case is rejected does not hold under direct test; corrected here per Research Data Integrity rule 2 (check the actual bytes, not the relayed claim) |
| `PR #12` | `_PR_NUMBER_RE = PR\s*#?(\d+)\|#(\d+)` | **Already extracted**, as `subject_type="pr"`, value `"12"` — reverified directly; the task brief's claim of rejection does not hold here either |
| `a173279` / `f435622` (letter-leading SHAs) | `_IDENTIFIER_RE` | Extracted (accident of starting with a letter) |

**Disposition:** two genuine gaps remain — a bare hex-ish SHA that starts with a digit, and a
hyphenated decision/issue ID — and both get new, narrowly-scoped patterns below. Branch names
and `#`-style PR references are **already** reliably extracted by existing patterns; adding a
redundant branch-name pattern (as the task brief's literal wording suggested) would be
unnecessary machinery solving an already-solved problem — verified before building, not assumed
from the brief. This reverses the prior "no new patterns" disposition and honors INTAKE.md's
approved Design Decision 4 (branch names, SHAs, decision IDs need real extraction support) using
only the two patterns actually shown to be missing.

### New patterns

**Constant sourcing (G10):** `_BARE_SHA_RE`'s bounds are both citable and now cited inline:
SHA-1 (git's object-hash algorithm) produces a 40-hex-character digest, and `git rev-parse
--short`/`core.abbrev` has a documented **minimum** abbreviation length of 7 characters (git
2.11+; `core.abbrev=auto` scales upward from there, but 7 is the floor, not a fixed default —
corrected per G16) — these are the two bounds, not arbitrary. `_DECISION_ID_RE`'s prior
`{2,6}`/`{1,4}` bounds had no precedent and, per this repo's Unasked Judgment doctrine, do not
need to exist — `[A-Za-z]+-\d+` does the identical job with zero numeric constants, so the bounds
are deleted rather than sourced.

**Prose false-positive exclusion (G11-R/G13, iteration-3 redesign):** iteration 2's fix for
`_DECISION_ID_RE`'s prose false-positive problem (`SHA-1`, `Rule-1`, `UTF-8`, etc. all match the
same shape as a real decision ID) was a **denylist**
(`_DECISION_ID_PROSE_EXCLUSIONS = {"UTF","COVID","ISO","IEEE","SLICE","LAYER"}`). Two defects were
independently found in that denylist: it is structurally incomplete (a denylist over open-ended
English/technical `Word-N` prose can never enumerate every look-alike — `SHA-1` itself, appearing
in this very document, was the first miss), and it was itself an unsourced non-numeric constant
(no attested Signpost occurrence was ever given for `ISO`/`IEEE` specifically). The judgment
question — does an exclusion set here need to be a denylist at all — was not asked before
extending it; asking it now: the actual identifier space this repo needs to recognize is finite
and self-attested, so an **allowlist** of prefixes this repo's own decision/tracking artifacts
actually use replaces the denylist entirely. Verified directly (not assumed) against this repo's
real convention, 2026-09-07:
- `ls docs/specs/agent-rig-ddrs/` shows every DDR file named `DDR-NNN-slug.md`
  (`DDR-001-ask-vs-act-decision-flow.md` … `DDR-012-unasked-judgment-rigor-theater.md`) — `DDR` is
  a real, attested hyphenated prefix used by this repo's own decision records.
- Issue and PR references in this repo's own docs (e.g. `DDR-006-domain-boundary-provenance-hook.md`:
  "PR #11") are written exclusively as `#N` / `PR #N` — never as a hyphenated `ISSUE-N` or `PR-N`
  token. `grep -rn "PR-[0-9]\{2,\}\b"` and `grep -rn "ISSUE-[0-9]"` across `docs/` return no
  attested hyphenated occurrence outside this sprint's own drafting comments. That shape is
  already fully covered by the existing `_PR_NUMBER_RE`, so it gets no allowlist entry — adding
  `ISSUE`/`PR` prefixes here would itself be an uncited addition with zero attested usage, the
  same defect this redesign exists to close.

`_DECISION_ID_PREFIX_ALLOWLIST = {"DDR"}` is therefore the complete, cited set. An allowlist over a
finite, self-attested set cannot false-positive on arbitrary English/technical prose by
construction — `SHA-1`, `Rule-1`, `Story-4`, `AC-1`, `Python-3`, `UTF-8`, `COVID-19`, `Slice-2`,
`Layer-1` are all excluded because their prefix is simply not `DDR`, not because each was
individually anticipated and denylisted. This closes both G11-R and G13 with the same change.

```python
# New: bare hex-ish commit SHA. Bounds are cited, not arbitrary: SHA-1 (git's object-hash
# algorithm) produces a 40-hex-character digest; `git rev-parse --short` (governed by
# `core.abbrev`) has a documented minimum abbreviated-SHA length of 7 characters (see G16).
# `any(c.isdigit())` excludes plain alphabetic English words that happen to be hex-valid — but
# the negative test for this guard must use a word of at least 7 characters (e.g. "deadbeef"),
# since a shorter word like "cafe"/"deed" already fails the `{7,` bound above and never reaches
# this guard at all (see G14 — a prior test of this exact shape was non-discriminating for
# precisely this reason). `not token.isdigit()` excludes purely-numeric runs — dates like
# "20260907" and bare counts like "1234567", which are hex-valid but not SHAs (see G11).
_BARE_SHA_RE = re.compile(r"\b[0-9a-fA-F]{7,40}\b")

def _looks_like_sha(token):
    return (
        bool(_BARE_SHA_RE.fullmatch(token))          # guard: length bound (7-40 hex chars)
        and any(c.isdigit() for c in token)           # guard: excludes alphabetic-only hex words
        and not token.isdigit()                       # guard: excludes purely-numeric runs
    )

# New: hyphenated decision ID — an alphabetic prefix, a hyphen, and a digit run, with no
# length bounds on either side (no citable precedent for any specific bound existed, and none is
# needed — unbounded does the same job with zero numeric constants, per G10). Covers DDR-006-shaped
# tokens. Distinct from _PR_NUMBER_RE's `PR #12` / `#12` shapes, which are already covered and are
# this repo's only attested way of referencing issues/PRs (see G11-R/G13 above) — no hyphenated
# `PR-N`/`ISSUE-N` form exists in this repo's docs, so none is allowlisted.
_DECISION_ID_RE = re.compile(r"\b([A-Za-z]+-\d+)\b")

# ALLOWLIST (not a denylist) of decision-ID prefixes this repo's own tracking artifacts actually
# use. See "Prose false-positive exclusion (G11-R/G13, iteration-3 redesign)" above for the full
# citation and the reasoning for replacing the prior denylist. Checked case-insensitively against
# the matched prefix. This set is complete against this repo's attested usage, not exhaustive
# against hypothetical usage — extend it only by citing a new real, observed prefix the same way
# `DDR` is cited here, never by anticipating a look-alike prose token.
_DECISION_ID_PREFIX_ALLOWLIST = {"DDR"}

def _looks_like_decision_id(match):
    prefix = match.group(1).split("-")[0]
    return prefix.upper() in _DECISION_ID_PREFIX_ALLOWLIST
```

Both patterns are scanned directly against the section's raw text (not only inside backtick
spans), mirroring how `_FILE_PATH_RE` and `_PR_NUMBER_RE` already scan raw prose today — a bare
SHA or decision ID in free-flowing Signpost prose (not wrapped in backticks) must still be
caught, consistent with how Signpost text is written per the sprint's own investigation (free
prose, not backtick-constrained). `_extract_claim_subjects` applies `_looks_like_sha` per token
and `_looks_like_decision_id` per match, respectively, as filtering predicates over
`_BARE_SHA_RE`/`_DECISION_ID_RE`'s raw matches — the regexes find candidates, the predicates
decide which candidates are real subjects (see G12 note below on `fullmatch`'s role).

New subject types: `"sha"` and `"decision_id"`, added to `_extract_claim_subjects`'s existing
`{"path", "pr", "identifier", "command", "query"}` set. `_subject_matches_target` requires no
change — both new types fall through to its existing unnamed-type fallback branch (substring
containment in either direction, §4), which is generic and already handles any subject_type not
explicitly special-cased. This satisfies the constraint that the matching algorithm is reused
unchanged.

**Wiring clarification (G12):** `_looks_like_sha`'s `_BARE_SHA_RE.fullmatch(token)` call operates
on individual whitespace/word-boundary-delimited tokens produced by a per-token sweep over the
section text, not on `_BARE_SHA_RE.finditer` matches directly — `fullmatch` is the filtering step
in that sweep, not dead code. `_looks_like_decision_id`, by contrast, is applied to
`_DECISION_ID_RE.finditer` match objects (it needs `match.group(1)` to isolate the prefix), not to
raw tokens. `_extract_claim_subjects` must call these two predicates according to their actual
input shape (token vs. match object) — implementers should not assume a single uniform
"sweep-then-filter" wiring works identically for both without checking which one each predicate
expects.

These two additions are v1-scoped, exact-match only, no fuzzy/similarity matching — consistent
with 01-REQUIREMENTS.md's Out of Scope. They do not attempt to be a formal grammar for every
possible SHA/ID/branch shape; a future sourced example that these patterns still miss is its own
follow-up, per 01-REQUIREMENTS.md's edge-case table allowance.

## Reference Mirror

`reference/first_turn_contract_probe.py` is a checked-in mirror of
`scripts/first_turn_contract_probe.py`. `tests/test_first_turn_contract_probe.py::test_reference_copy_matches_executed_copy`
(line 872) asserts the two files are byte-identical. **Every edit this sprint makes to
`scripts/first_turn_contract_probe.py` — the new patterns above, `_extract_section_text`, the
`check_c3_violation` signature change, and the `run()` call-site update — must be applied
identically to `reference/first_turn_contract_probe.py` in the same commit.** This is not a new
mechanism; it is an existing drift guard this sprint must not silently break.

## Components

| Component | Responsibility | Location |
|-----------|----------------|----------|
| `_extract_section_text` (new, extracted from existing inline logic) | Given full message text and a heading line index, return that section's text up to the next Signpost/Pillar heading or end of message. Replaces the Pillar-only inline slicing currently in `run()`, reused for both Pillar and Signpost. | `scripts/first_turn_contract_probe.py`, mirrored verbatim into `reference/first_turn_contract_probe.py` |
| `_BARE_SHA_RE`, `_looks_like_sha`, `_DECISION_ID_RE` (new) | Recognize bare hex-ish SHAs and hyphenated decision/issue IDs in raw section text. | `scripts/first_turn_contract_probe.py`, mirrored into `reference/first_turn_contract_probe.py` |
| `_extract_claim_subjects` (modified — additive) | Extract `(subject_type, value)` tuples from a section's text; now also emits `"sha"` and `"decision_id"` subjects via the two new patterns above, alongside the four existing categories, unchanged in every other respect. Called twice per turn — once for Pillar text, once for Signpost text. | `scripts/first_turn_contract_probe.py`, mirrored |
| `check_c3_violation` (modified) | Adds a `signpost_section_text` parameter; unions Pillar-sourced and Signpost-sourced subjects (deduped) before checking against qualifying tool-call targets. | `scripts/first_turn_contract_probe.py`, mirrored |
| `run` (modified) | Computes `signpost_section_text` using `_extract_section_text` (mirroring the existing Pillar slice), passes it into `check_c3_violation`. | `scripts/first_turn_contract_probe.py`, mirrored |

No new files. No changes to `_extract_tool_target`, `_subject_matches_target`,
`_collect_qualifying_tool_calls`, C1/C2 logic, or the hook wrapper.

## Data Schemas

No new persistent data structures. The existing in-memory subject representation is extended by
two new type tags:

```python
# subject: tuple[str, str] — (subject_type, value)
# subject_type in {"path", "pr", "identifier", "command", "query", "sha", "decision_id"}
```

The union of subjects computed inside `check_c3_violation` is the same tuple list shape, just
assembled from two extraction calls instead of one:

```python
# Conceptual shape (not a new named type — stays a List[Tuple[str, str]] local variable):
pillar_subjects: list[tuple[str, str]]     # from _extract_claim_subjects(pillar_section_text)
signpost_subjects: list[tuple[str, str]]   # from _extract_claim_subjects(signpost_section_text)
combined_subjects: list[tuple[str, str]]   # deduped union, order-insensitive
```

## API Contracts

### `_extract_section_text` (new)

```python
def _extract_section_text(text, section_idx):
    """Given the full assistant message `text` (already split conceptually into lines) and
    the line index of a Signpost/Pillar heading (`section_idx`), return the section's text:
    the heading line through (but not including) the next Signpost/Pillar heading line, or
    through end of message if none follows. Returns None if `section_idx` is None.

    This is the existing Pillar-slicing logic in `run()` (lines computing `pillar_section_text`
    today), extracted verbatim into a function so the identical slicing rule applies to both
    Pillar and Signpost without duplicating the loop.

    Known low-impact edge case: where a Pillar heading precedes a Signpost heading (a
    C1-violation shape — Pillar-before-Signpost), the Signpost slice runs to end of message
    (there is no *later* Signpost/Pillar heading to stop at) and may absorb unrelated trailing
    prose into the Signpost section's extracted text, inflating the Signpost-sourced subject
    set. This is expected behavior, not a defect to fix here: C1 already fires independently on
    that same turn (Signpost-before-Pillar ordering is violated), so the turn is blocked
    regardless of what C3 concludes from an over-inclusive Signpost slice.
    """
```

Signature: `_extract_section_text(text: str, section_idx: int | None) -> str | None`

**Test coverage note (G17):** `_extract_section_text(text, None) -> None` (the no-heading-found
case, load-bearing for the `signpost_idx is None` path described under `run()` below and the
Anti-Pattern against special-casing it) has no direct assertion in Slice 1's test list — Slice 1's
existing-suite-passes check never reaches the helper with `None` as input. Slice 1 must add one
direct unit assertion of this return value; it is a real, touched code path this sprint
introduces via the extraction into a standalone function, not a hypothetical one.

### `check_c3_violation` (modified signature)

```python
def check_c3_violation(records, current_turn_index, pillar_idx, pillar_section_text,
                        signpost_section_text):
    """§5.4/§3.3 — applies only if a Pillar heading was asserted (`pillar_idx is not None`),
    unchanged precondition. Returns `(violation: bool, unmatched_subjects: list)`.

    Subject sourcing (this sprint's change): subjects are the deduplicated union of
    `_extract_claim_subjects(pillar_section_text)` and
    `_extract_claim_subjects(signpost_section_text)`. Pillar-sourced subjects are additive to,
    not replaced by, Signpost-sourced subjects (INTAKE.md Design Decision). Dedup key is
    `(subject_type, value)`, identical to `_extract_claim_subjects`'s own existing dedup key —
    a subject named identically by both sections counts once, satisfied by one matching tool
    call (per 01-REQUIREMENTS.md's edge-case table).

    `signpost_section_text` may be None or empty (e.g. malformed input) — treated as
    contributing zero subjects, identical to how an empty `pillar_section_text` is already
    treated by `_extract_claim_subjects`'s own empty-input guard.

    Presence-only fallback (§3.4) is preserved for the case where the *union* yields zero
    subjects (both sections empty of extractable subjects) — this is the edge case
    01-REQUIREMENTS.md's table marks as "C3 does not fire on subject-matching grounds,"
    unchanged from today's single-source fallback except it now requires both sources to be
    empty, not just Pillar.
    """
```

New parameter is added at the end (positional 5th argument), not inserted between existing
params — this keeps any exhaustive-argument call in the existing test suites unaffected in
practice; verified no test file calls `check_c3_violation` directly (`grep -n
"check_c3_violation(" tests/test_first_turn_contract_probe.py` returns no matches, confirmed
independently — the only occurrences are inside a fixture payload string, not a call) — both
existing suites exercise C3 only through `run()`'s stdin/transcript path, so the signature
change is invisible to them as long as `run()`'s own call site is updated (below).

### `run` (modified call site only, no signature change — `run` is not a public API called by tests directly with a fixed arg list beyond stdin)

```python
# Existing (today):
#   pillar_section_text = <inline slice loop ending at next Signpost/Pillar heading>
#
# New:
pillar_section_text = _extract_section_text(last_assistant_message, pillar_idx)
signpost_section_text = _extract_section_text(last_assistant_message, signpost_idx)
c3_violation, c3_unmatched_subjects = check_c3_violation(
    records, current_turn_index, pillar_idx, pillar_section_text, signpost_section_text
)
```

`signpost_idx` is already computed earlier in `run()` by the existing
`find_signpost_pillar_positions` call — no new heading-detection logic needed. If
`signpost_idx is None` (no Signpost heading found — a case gated out before C3 ever runs in
practice, since a Pillar with no preceding Signpost is already a C1 violation, but the value can
still be `None` if C1 already fired and C3 is evaluated independently in the same pass),
`_extract_section_text` returns `None` and `check_c3_violation` treats it as zero Signpost
subjects — no crash, no special-casing needed in `run()`.

## Patterns

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| Additive union over dual extraction calls | Combining Pillar- and Signpost-sourced subjects | Matches INTAKE.md's resolved Design Decision verbatim ("Signpost-sourced subjects supplement, not replace"); reuses `_extract_claim_subjects` and its existing dedup key rather than inventing a new merge structure. |
| Extract-then-reuse helper (`_extract_section_text`) | Slicing both Pillar and Signpost section bodies | The existing Pillar-slicing loop in `run()` already implements exactly the rule Signpost slicing needs (stop at next Signpost/Pillar heading); duplicating it inline for Signpost would create two copies of the same boundary logic to keep in sync. Extracting it once is the smaller, safer diff. |
| Two narrowly-scoped new regex patterns, additive to the existing four | Bare SHA and decision-ID subject extraction | Direct empirical testing against real session subjects showed genuine gaps (digit-leading SHAs, hyphenated decision IDs) that INTAKE's approved Design Decision 4 explicitly called for; branch names and `#`-style PR refs were verified already covered and get no redundant new pattern. |
| Generic fallback matching for new subject types | `_subject_matches_target` handling of `"sha"`/`"decision_id"` | The function's existing unnamed-type fallback (substring containment) already does the right thing for these types without modification — reuses the matcher unchanged, per the sprint's constraint against new fuzzy/similarity matching. |
| Exact substring/token containment only | Subject matching (unchanged) | Constraint from 01-REQUIREMENTS.md and the parent C3 sprint's own non-goals — no fuzzy/similarity matching in v1. |
| Reference-mirror sync as part of every code-editing slice | `reference/first_turn_contract_probe.py` | Pre-existing drift guard (`test_reference_copy_matches_executed_copy`) requires byte-identity; silently omitting this from scope would leave the test suite red through the whole sprint. |

### Anti-Patterns (Do Not Use)

- Do not build a separate `_extract_signpost_subjects` function that duplicates
  `_extract_claim_subjects`'s regex logic — the function is already generic over "some section's
  text," not Pillar-specific; its docstring/parameter name (`pillar_section_text`) is a naming
  artifact, not a behavioral constraint. Reuse it directly.
- Do not add a new subject_type whose dedup key or matching semantics diverge between the Pillar
  and Signpost call sites — `"sha"` and `"decision_id"` are added once, inside the shared
  `_extract_claim_subjects`, so both call sites get identical behavior by construction.
- Do not add a redundant branch-name-specific pattern — verified above that `_FILE_PATH_RE`'s
  existing slash branch already reaches this shape; adding one anyway would be unsourced,
  unnecessary machinery for an already-solved case.
- Do not special-case "signpost_idx is None" as a separate branch inside `check_c3_violation` —
  `_extract_section_text(text, None)` returning `None`, combined with
  `_extract_claim_subjects(None)`'s existing empty-input guard (`if not
  pillar_section_text: return []`), already handles it for free.
- Do not edit `scripts/first_turn_contract_probe.py` in any slice without applying the identical
  edit to `reference/first_turn_contract_probe.py` in the same commit.

## Dependencies

None. No new libraries — this is a pure refactor/extension of existing stdlib-only (`re`, `os`,
`json`) code in `scripts/first_turn_contract_probe.py` and its `reference/` mirror.

## Pre-existing constant disposition (not resolved by this sprint)

`_FILE_EXTENSION_ALLOWLIST` (`scripts/first_turn_contract_probe.py`, currently tagged
`PROVISIONAL — owner: wright`) is reused unchanged by this sprint for a second input source
(Signpost text, via the existing file-path extraction branch). This sprint does not resolve that
pre-existing PROVISIONAL/self-owned status — it is out of scope per INTAKE's stated scope limits
and is recorded here, not silently inherited, so the widened blast radius (a second call site now
depends on the same unsourced constant) is visible rather than assumed away.

## Integration Points

- `scripts/first_turn_contract_probe.py::run` — the only call site of `check_c3_violation`;
  updated to compute and pass `signpost_section_text`.
- `reference/first_turn_contract_probe.py` — byte-identical mirror; every edit to `scripts/`
  in this sprint (new patterns, `_extract_section_text`, `check_c3_violation`, `run()`) is
  applied here in the same commit, per `test_reference_copy_matches_executed_copy`.
- `tests/test_first_turn_contract_probe.py` — existing suite exercises C3 exclusively through
  `run()`'s stdin/transcript-driven path (no direct unit calls to `check_c3_violation` or
  `_extract_claim_subjects` found via grep), so both prior suites
  (`first-turn-contract-c3-claim-matching`, `first-turn-contract-c3-path-query-boundary-matching`)
  continue to exercise the modified code path without needing call-site edits in the test file
  itself, other than the new tests this sprint adds (Story 4, dedup edge case).
- New regression test (Story 4, forge phase) — constructs a transcript fixture whose
  `last_assistant_message` contains a Signpost section with at least one real extractable
  subject and the literal Pillar text `"Pillar: none yet — nothing independently checked this
  session"` (yields zero Pillar subjects), plus one qualifying tool call earlier in the turn
  targeting something unrelated to the Signpost subject. Asserts `check_c3_violation` (via
  `run()`'s block decision) returns a violation — this is the exact issue #27 reproduction and
  the direct proof the presence-only fallback no longer masks an evasive Pillar.
- New dedup test (Slice 2, forge phase, closes G4) — constructs a fixture where Pillar and
  Signpost both name the identical subject (same `(subject_type, value)`, e.g. the same file
  path quoted in both sections), with exactly one qualifying tool call matching it. Asserts
  `check_c3_violation` treats it as satisfied by that single match (no violation raised for that
  subject, and the subject is not double-counted or double-required) — directly exercises the
  edge-case row "Signpost and Pillar both name the same subject, one qualifying tool call
  matches it → counts once."
- Fail-then-pass verification procedure for the Story 4 regression test (closes G5-R and G15):
  the new test is authored in the same commit as the fix, so it does not exist at the parent SHA —
  running pytest directly against a parent-SHA worktree would report a collection error ("no
  tests found"), which is not valid evidence the defect existed. Independently re-verified
  (G15): copying only the new test function orphans the module-level helpers it depends on
  (`_load_probe`, `_queue_marker_record`, `_assistant_text_record`, `_tool_use_record_with_input`,
  `_tool_result_record`, `_write_transcript`, `_run_probe`, `_decision`,
  `_signpost_then_pillar`, plus the `importlib`/`io`/`json`/`os`/`sys`/`redirect_stdout` imports),
  producing a `NameError`/`ImportError` — not the assertion failure the proof requires. The test
  must also drive the code through `run()`'s stdin/transcript-in, stdout-out contract, not call
  `check_c3_violation` directly — the pre-fix signature takes 4 positional params, so a direct
  5-arg call raises `TypeError` (another non-assertion error), and per 02's own confirmed finding
  above, no existing test calls `check_c3_violation` directly anyway; there is no reason for the
  new one to be the first. The corrected mechanic:
  1. `git worktree add` a detached checkout of the parent commit SHA (the commit immediately
     before this sprint's `check_c3_violation`/`run()` changes land).
  2. Copy the **entire** `tests/test_first_turn_contract_probe.py` file (not just the one new
     function) into that parent-SHA worktree, so every module-level helper and import the new
     test needs resolves without modification. Do not hand-pick a subset of helpers — copying the
     whole file is the only version of this step that cannot silently omit a dependency.
  3. Run only the new test (`test_c3_signpost_sourcing_catches_issue_27_evasion`) from inside the
     parent-SHA worktree, invoking `scripts/first_turn_contract_probe.py` through that worktree's
     own copy — importing it from the worktree ensures the pre-fix code runs, not the fixed one —
     and driving it through `run()`'s stdin-in/stdout-out contract (the same route every other
     test in this file already uses), never by calling `check_c3_violation` or any other internal
     function directly with a fixed positional-argument count.
  4. **Guard, before treating step 3's output as evidence:** if the run raises anything other than
     an `AssertionError` originating from the new test itself (a `NameError`, `ImportError`,
     `TypeError`, or a pytest collection error), the procedure was set up wrong — fix the setup
     (most likely an incomplete copy or a call that bypasses `run()`) and re-run before drawing
     any conclusion. Only a genuine `AssertionError` (the presence-only fallback wrongly reporting
     no violation) is valid pre-fix evidence.
  5. Run the same test (now the real committed one, at its real location) against the fixed
     commit in the normal working tree; record the passing output verbatim.
  6. Both outputs — the parent-SHA assertion failure and the fixed-commit pass — are recorded in
     `PROGRESS.md` for Slice 3, with an explicit note that step 3's output was an assertion
     failure, not a collection/import/type error, since that distinction is the entire
     evidentiary point.

## Coverage Check Against 01-REQUIREMENTS.md

- Story 1 / AC1 (now satisfiable as reworded — see 01-REQUIREMENTS.md's Out of Scope addition
  and the extraction pattern investigation above): branch name (`_FILE_PATH_RE`, already
  covered), commit SHA (new `_BARE_SHA_RE`/`_looks_like_sha`), PR/issue/decision ID (`#12`/`PR
  #12` via existing `_PR_NUMBER_RE`; hyphenated `DDR-006`/`PR-012` via new `_DECISION_ID_RE`),
  and file path (`_FILE_PATH_RE`, existing) are all reliably extracted by the union computation.
- Story 1 / AC2 (issue #27 repro), AC3 (both empty → no fire): satisfied by the union
  computation — empty-Pillar-nonempty-Signpost fires on the Signpost subject; both-empty falls
  through to the preserved presence-only fallback.
- Story 2 / both ACs: satisfied — every Signpost-sourced subject is independently checked against
  `targets`; partial matches leave the unmatched Signpost subject(s) in the returned list, cited
  by the existing `build_reason` C3 branch unchanged.
- Story 3 / all three ACs: satisfied — Pillar-sourced extraction call, its inputs, and
  `_subject_matches_target` are byte-for-byte unchanged; both prior suites drive C3 only through
  `run()`, which now supplies an additional (unioned) subject source but no altered behavior for
  turns whose Signpost yields zero subjects. Requires the `reference/` mirror to be kept in sync
  (see above) for these suites to pass at all.
- Story 4 / both ACs: covered by the new regression test described under Integration Points, with
  a concrete, auditable fail-then-pass procedure specified above.
- Dedup edge case (01-REQUIREMENTS.md edge-case table): covered by the new dedup test described
  under Integration Points.
- Constraint "`pillar_idx is None` → C3 does not run": untouched — the existing guard clause at
  the top of `check_c3_violation` is unchanged.

## HALT Check

No ambiguity requiring a HALT was found. The prior draft's "no new extraction patterns"
disposition is reversed here based on direct empirical testing against the live code, which also
corrected two claims in the task brief itself (branch names and `#`-style PR refs are already
covered, contrary to the brief's assertion) — resolved by checking the actual regex behavior
rather than accepting either the original investigation's or the brief's claim at face value.
