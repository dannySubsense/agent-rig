# Intake: first-turn-contract-c3-path-query-boundary-matching

**Status**: APPROVED

**Date**: 2026-08-27
**Author**: wright

---

## Problem Statement

`_subject_matches_target` in `scripts/first_turn_contract_probe.py` (§3.3 of the prior
`first-turn-contract-c3-claim-matching` sprint's SPEC.md) matches `path`, `command`, and `query`
claim subjects against tool-call targets via plain substring containment in either direction
(`scripts/first_turn_contract_probe.py:419`: `if subject_value in target_text or target_text in
subject_value`). For file paths, an optional basename fallback is layered on top.

This is deliberately loose for a real reason: a claim can legitimately name a shorter relative path
(`scripts/foo.py`) while the tool call recorded an absolute one, or quote a short phrase from a
longer search query — plain substring containment is what makes those legitimate matches work.

The gap: substring containment has no concept of a path-component or word boundary, so it can also
match cases that are not legitimate. Concretely:
- A claim subject that is a short, extension-only filename (e.g. `c3.py`, extracted when the
  Pillar text names a bare filename with no directory component) would match inside any longer
  target string containing that same character sequence at any offset — e.g. a target path
  `scripts/legacy_c3.pyx` or a target command string that happens to contain the literal substring
  `c3.py` for unrelated reasons. Containment does not require the match to fall on a real path
  separator or filename boundary.
- A claim quoting a short query fragment could match inside an unrelated longer query string that
  happens to contain the same characters as a substring, not as a real word/phrase.

This was identified as Open Question 4 (narrowed) in the prior sprint's SPEC.md §7, itself a
narrowing of a defect the orchestrator found in post-PASS review (the original finding was a
digit-substring collision for PR numbers, fixed via exact-match; the same theoretical risk was
flagged, but not fixed, for path/query subjects, since exact-match would break the legitimate
truncation/partial-phrase cases those two types need). Tracked as GitHub Issue #19.

## Context

This is the second sprint in the `first-turn-contract` C3 hardening family. The first
(`first-turn-contract-c3-claim-matching`, PR #20, merged 2026-08-27) fixed presence-only matching
and closed the same collision-shape bug for PR numbers and identifiers via exact-match carve-outs.
That fix was straightforward because PR numbers and identifiers have no legitimate truncation case
— exact match was strictly correct for them. Paths and queries are different: they *need* partial
matching to work correctly, so this sprint's fix must be a **boundary rule**, not an on/off switch.

No concrete false-positive instance has been observed in this repo's actual track record
(`docs/tooling/first-turn-contract-track-record.jsonl`, 290+ real entries) — this is a hardening
fix against a demonstrated *mechanism* (the same substring-collision class already proven real for
PR numbers), not a fix for an observed incident. Danny requested closing this now rather than
waiting for an incident, given the mechanism is already proven to cause false matches elsewhere in
this exact function.

## Capability Gaps This Sprint Closes

- **Path-boundary matching**: a path-type claim subject must match a tool-call target only at a
  path-component boundary (e.g. `/` or start/end of string), not at an arbitrary character offset
  inside an unrelated longer path.
- **Query/word-boundary matching**: a query-type claim subject must match at a word/phrase boundary
  in the target, not as an arbitrary substring inside an unrelated longer string.

## Constraints

- No new hook, no new script file, no new settings.json wiring — this is a fix inside
  `_subject_matches_target` (and possibly `_extract_claim_subjects`/`_extract_tool_target` if
  boundary detection needs support there) in `scripts/first_turn_contract_probe.py`.
- Must NOT regress the legitimate cases substring matching exists for: relative-vs-absolute path
  matching (existing test `test_c3_matching_ac6_absolute_vs_relative_path_basename_match_allows`),
  and partial-phrase query matching. A boundary rule that breaks these is not an acceptable fix —
  it would trade one correctness bug for another.
- `command`-type subjects (whole gh command strings used as a fallback subject when no PR number is
  extractable — see the prior sprint's SPEC.md §3.1) are explicitly in scope for the same
  boundary-matching question; whether they need the same treatment as `path`/`query` or can keep
  plain substring matching is an open question for the spec to resolve, not decided here.
- Any predetermined boundary-character set or pattern needs a citable rationale or an explicit
  PROVISIONAL tag with a named owner — no fabricated numbers/patterns, same binding rule as the
  prior sprint.
- Existing 26 tests (`tests/test_first_turn_contract_probe.py`) must not regress without an
  explicit, reviewed reason for each changed expectation.

## Open Questions

- What exactly counts as a "path-component boundary"? Candidates: match only when the subject is
  preceded/followed by `/`, start-of-string, or end-of-string in the target (and vice versa for the
  reverse-containment direction); or match on `os.path` component splitting rather than raw
  character boundaries. This is a real design decision for the spec, not resolved here.
- Does `command`-type subject matching need the same boundary treatment, or is it lower-risk enough
  (whole command strings tend to be long and specific) to leave as plain substring matching for now
  — deferred rather than fixed, same reasoning as this sprint's own predecessor left it?
- Should the fix apply the same boundary logic to both matching directions (subject-in-target and
  target-in-subject), or does one direction need different treatment than the other?

---

## Approval

Danny's approval of this document (Status line above set to `APPROVED`) is what gates
`spec-start --lite` Step 0.
