# Spec: first-turn-contract-c3-path-query-boundary-matching

**Status**: DRAFT

**Date**: 2026-08-27
**Author**: wright

---

## 1. Purpose

Replace plain substring containment for `path` and `query` claim subjects in
`_subject_matches_target` (`scripts/first_turn_contract_probe.py:392-424`) with a
boundary-aware match: a match counts only when it aligns with a real path-component
split (for `path`) or a real word/phrase edge (for `query`), not an arbitrary character
offset inside an unrelated longer string. This closes the same substring-collision
mechanism already fixed for `pr`/`identifier` subjects in the prior sprint
(`first-turn-contract-c3-claim-matching`, PR #20), applied here as a boundary rule
rather than an exact-match switch, since `path` and `query` have legitimate partial-match
cases that must keep working.

## Non-Goals

- Does NOT touch `pr` or `identifier` matching (`_subject_matches_target` lines 398-415)
  — already exact-match-only and correct.
- Does NOT add any new hook, script file, or `settings.json` wiring.
- Does NOT change require-all-subjects behavior (the caller of `_subject_matches_target`
  is out of scope).
- Does NOT change the first-turn-only scope of the probe.
- Does NOT change `_extract_claim_subjects` or `_extract_tool_target` extraction logic
  — only the comparison inside `_subject_matches_target` changes. (No support code is
  needed there; boundary detection is self-contained string logic on the two already-
  extracted values.)

## 2. Path-Subject Boundary Rule

**Rule**: for `subject_type == "path"`, containment (in either direction) counts as a
match only if the shorter string aligns with a full path-component split of the longer
string — i.e., the character immediately before the match and the character immediately
after the match in the longer string are each either `/` or "no character" (start/end
of string). A match landing mid-component (e.g. `c3.py` inside `legacy_c3.pyx`, where
the character after the match is `x`, not `/` or end-of-string) is rejected.

**Implementation approach**: use `os.path` semantics rather than a hand-rolled offset
check, per the intake's suggestion. Split both strings on `/` into component lists
(`subject_value.split("/")`, `target_text.split("/")`), then check whether one
component-list is a **contiguous suffix or prefix** of the other:

```python
def _path_components_align(subject_value, target_text):
    subj_parts = subject_value.split("/")
    targ_parts = target_text.split("/")
    if len(subj_parts) <= len(targ_parts):
        shorter, longer = subj_parts, targ_parts
    else:
        shorter, longer = targ_parts, subj_parts
    if not shorter:
        return False
    n = len(shorter)
    # suffix alignment: shorter matches the tail of longer's components
    if longer[len(longer) - n:] == shorter:
        return True
    # prefix alignment: shorter matches the head of longer's components
    if longer[:n] == shorter:
        return True
    return False
```

This is equivalent to the intake's "preceded/followed by `/` or start/end of string"
character-boundary rule, expressed as component-list alignment instead of raw offset
arithmetic — splitting on `/` and comparing component lists cannot land mid-component
by construction, so it is the cleaner of the two equivalent formulations. No new
character set or regex pattern is introduced; `/` is the pre-existing path separator
already used throughout this module (`os.path.basename`, `os.path.splitext`), not a new
predetermined constant, so no PROVISIONAL tag is needed.

**Replaces**: the raw `subject_value in target_text or target_text in subject_value`
check, for `path` subjects only. The existing `os.path.basename(subject_value) ==
os.path.basename(target_text)` fallback is **retained unchanged** as a second check
after the component-alignment check — it already only fires on exact basename equality
(not substring containment) so it carries no collision risk, and removing it is out of
scope (intake constraint: don't regress the existing basename-fallback test).

### Walkthrough: AC6 regression check

`test_c3_matching_ac6_absolute_vs_relative_path_basename_match_allows`:
- `subject_value = "scripts/foo.py"` → `["scripts", "foo.py"]`
- `target_text = "/home/d-tuned/agent-rig/scripts/foo.py"` → `["", "home", "d-tuned",
  "agent-rig", "scripts", "foo.py"]`
- `shorter = ["scripts", "foo.py"]` (len 2), `longer` = the 6-element list above.
- Suffix check: `longer[-2:] == ["scripts", "foo.py"]` → `True`.

Match succeeds via the new component-alignment rule directly (the basename fallback is
no longer even needed for this case, though it remains in place as a safety net for
cases where components don't align but the basename still legitimately matches, e.g. a
symlink-relocated directory). Test continues to pass.

### Walkthrough: the gap being closed

Claim subject `"c3.py"` (bare filename, no `/`) against target
`"scripts/legacy_c3.pyx"`:
- `subj_parts = ["c3.py"]`, `targ_parts = ["scripts", "legacy_c3.pyx"]`.
- Suffix check: `longer[-1:] == ["c3.py"]` → `["legacy_c3.pyx"] == ["c3.py"]` → `False`.
- Prefix check: `longer[:1] == ["c3.py"]` → `False`.
- No alignment → correctly rejected. (Under the old rule, `"c3.py" in
  "scripts/legacy_c3.pyx"` was `True` — this was the exact false-positive mechanism the
  intake describes.)

## 3. Query-Subject Boundary Rule

**Rule**: for `subject_type == "query"`, containment counts as a match only at a
word/phrase boundary — the shorter string's match in the longer string must not have an
alphanumeric character immediately adjacent on either side (Python's `\w` class, same
alphanumeric-plus-underscore boundary concept already used by `_WORD_TOKEN_RE` in this
module for identifier matching). This is implemented with `re.escape` + `\b`-style
manual boundary assertion rather than raw substring containment:

```python
def _phrase_boundary_match(subject_value, target_text):
    for shorter, longer in ((subject_value, target_text), (target_text, subject_value)):
        if not shorter:
            continue
        pattern = r"(?<!\w)" + re.escape(shorter) + r"(?!\w)"
        if re.search(pattern, longer):
            return True
    return False
```

`(?<!\w)` / `(?!\w)` are negative lookaround assertions on Python's built-in `\w`
class — not a new predetermined character set; `\w` is already the exact class used by
`_WORD_TOKEN_RE = re.compile(r"[A-Za-z_]\w*")` at line 292 of this same module, so this
reuses an existing, already-justified boundary definition rather than introducing one.

This correctly allows partial **phrase** matches (a query fragment spanning multiple
words with internal spaces, e.g. `"claim matching"` inside `"first-turn-contract claim
matching hardening"`) because the lookaround only checks the two outer edges of the
matched span, not internal word breaks — internal spaces in the shorter string are part
of the literal match, `\b`-style edges apply only at the start and end.

### Walkthrough: the gap being closed

Claim subject `"c3"` against target `"grep -r c3matching-helper"`:
- Old rule: `"c3" in "grep -r c3matching-helper"` → `True` (false positive: `"c3"` is a
  substring of `"c3matching-helper"` but not a real word in that context).
- New rule: `(?<!\w)c3(?!\w)` against the target — the character after `"c3"` in
  `"c3matching-helper"` is `"m"`, which is `\w`, so `(?!\w)` fails. No match found
  elsewhere in the string. Correctly rejected.

### Walkthrough: existing legitimate case preserved

Claim subject `"claim matching"` against target `"first-turn-contract claim matching
fix"`: `(?<!\w)claim\ matching(?!\w)` — preceded by a space (not `\w`), followed by a
space (not `\w`). Matches. Partial-phrase query matching continues to work.

## 4. Command-Subject Decision

**Decision: `command`-type subjects keep plain substring containment (both
directions), unchanged.** No boundary treatment is applied.

**Reasoning**: `command` subjects are only produced by `_extract_claim_subjects` for a
backtick-span gh-command reference from which no PR number could be extracted (line
323-333) — the full literal command string quoted in the Pillar text (e.g. `` `gh pr
list --state open` ``). Two properties distinguish this from `path`/`query`:

1. **No legitimate truncation case exists.** Unlike paths (relative-vs-absolute) or
   queries (phrase fragments), there is no documented or intake-described scenario
   where a Pillar claim legitimately quotes a *partial* gh command that should match a
   *longer* or *different* target command. The substring-containment behavior for
   `command` was inherited from the shared code path with `path`/`query` (line 419), not
   because command matching has its own partial-match requirement.
2. **The collision surface is materially smaller.** gh command strings are structured,
   multi-token, and contain spaces and flags (`gh pr list --state open`), unlike bare
   short filenames (`c3.py`) or short words (`c3`) that were the demonstrated collision
   shape for path/query. A short, arbitrary substring of one gh command string
   accidentally appearing inside an unrelated one is a lower-probability collision than
   a 5-character filename appearing inside an unrelated longer filename — no concrete
   instance has been observed for `command` either in the 290+-entry track record cited
   in the intake, and unlike `path`/`query`, no theoretical mechanism specific to
   `command` has been demonstrated (the intake's Open Question 2 asks this as a genuine
   fork, not a demonstrated risk).

Given no demonstrated risk and no legitimate-truncation requirement pulling toward a
boundary rule, applying word/phrase-boundary matching to `command` would add complexity
(a third boundary code path) without closing a demonstrated gap. If a concrete
`command`-subject false-positive is ever observed in the track record, it should be
handled as its own follow-up sprint with its own evidence, not spec'd preemptively here.

This is a design decision, not deferred: `command` is explicitly excluded from this
sprint's changes; the `if subject_type == "path": ... ` and query-boundary branches are
added, and the fallback branch (formerly shared by `path`/`command`/`query`) becomes
`command`-only, using the unchanged `subject_value in target_text or target_text in
subject_value` line.

## 5. Behavior Table

| # | subject_type | subject_value | target_text | Old result | New result | Case |
|---|---|---|---|---|---|---|
| 1 | path | `c3.py` | `scripts/legacy_c3.pyx` | match (false positive) | no match | Gap closed (§2 walkthrough) |
| 2 | path | `scripts/foo.py` | `/home/.../scripts/foo.py` | match | match | AC6 regression preserved (§2 walkthrough) |
| 3 | path | `foo.py` | `bar/foo.py` | match | match | Legitimate suffix alignment |
| 4 | path | `x/foo.py` | `y/foo.py` (different dir, same basename) | match (basename fallback) | match (basename fallback, component check fails first) | Existing basename-fallback case preserved |
| 5 | query | `c3` | `grep -r c3matching-helper` | match (false positive) | no match | Gap closed (§3 walkthrough) |
| 6 | query | `claim matching` | `first-turn-contract claim matching fix` | match | match | Partial-phrase preserved (§3 walkthrough) |
| 7 | query | `matching` | `word matching test` | match | match | Legitimate single-word match |
| 8 | command | `gh pr list --state open` | `gh pr list --state open --limit 5` | match | match (unchanged) | Command matching untouched |
| 9 | command | `pr list` | `unrelated pr list-view thing` | match | match (unchanged, by design decision §4) | Command stays on plain substring per §4 decision |

## 6. Acceptance Criteria

- **AC1**: A path claim subject that is a short bare filename with no directory
  component (e.g. `c3.py`) does NOT match a target containing that character sequence
  at a non-component-boundary offset (e.g. `scripts/legacy_c3.pyx`) — new test asserting
  `_subject_matches_target("path", "c3.py", "scripts/legacy_c3.pyx")` returns `False`.
- **AC2**: A query claim subject that is a short word does NOT match a target where
  that character sequence appears only as a fragment inside a longer unrelated word
  (e.g. `c3` inside `c3matching-helper`) — new test asserting
  `_subject_matches_target("query", "c3", "grep -r c3matching-helper")` returns `False`.
- **AC3**: `test_c3_matching_ac6_absolute_vs_relative_path_basename_match_allows`
  continues to pass unmodified — relative claim path `scripts/foo.py` still matches
  absolute target `/home/.../scripts/foo.py` (§2 walkthrough).
- **AC4**: A partial query phrase spanning multiple words still matches correctly — new
  test asserting `_subject_matches_target("query", "claim matching", "first-turn-contract
  claim matching fix")` returns `True`.
- **AC5**: `command`-type subjects retain plain bidirectional substring containment,
  unchanged — new test asserting a partial/fragment command substring still matches
  (per §4's decision), e.g. `_subject_matches_target("command", "pr list", "gh pr list
  --state open")` returns `True`, confirming no boundary rule was applied to `command`.
- **AC6**: `pr` and `identifier` subject matching is unmodified — existing tests for
  those subject types in `tests/test_first_turn_contract_probe.py` pass with no changes
  to their expected results.
- **AC7**: A path claim subject with a directory component that suffix-aligns with a
  longer target path still matches (e.g. `bar/foo.py` inside `x/bar/foo.py`) — new test
  asserting `True`.
- **AC8**: A path claim subject whose basename matches a target's basename but whose
  full path does not component-align (existing basename-fallback case, distinct
  directory trees) still matches via the retained basename fallback — new test
  confirming the fallback path is still reachable and returns `True`.

## 7. Integration Boundary

Confined entirely to `_subject_matches_target` (`scripts/first_turn_contract_probe.py:
392-424`) plus two new private helper functions colocated in the same module
(`_path_components_align`, `_phrase_boundary_match`), both called only from within
`_subject_matches_target`. No changes to:
- `_extract_claim_subjects`, `_extract_tool_target` (extraction logic unchanged).
- `pr`/`identifier` branches of `_subject_matches_target` (lines 398-415, untouched).
- Require-all-subjects logic or any caller of `_subject_matches_target`.
- `settings.json`, hook wiring, or any file outside `scripts/first_turn_contract_probe.py`
  and its test file.

## 8. Dependencies

None new. `os.path` and `re` are both already imported and used elsewhere in this
module (`os.path.basename`, `os.path.splitext`, `re.compile` for existing patterns at
lines 280-292).

## 9. Open Questions

None outstanding — the two open questions from the intake (path-boundary definition,
command-subject treatment) are resolved in §2 and §4 above. The intake's third question
(same boundary logic for both matching directions?) is resolved: yes, both
`_path_components_align` and `_phrase_boundary_match` check both directions
symmetrically (shorter-in-longer is computed regardless of which argument started
longer), consistent with the existing bidirectional `in` check being replaced.
