# Architecture: Unsourced-Threshold Provenance Hook

**Status**: Draft (awaiting Frank's spec-gate + human approval)
**Date**: 2026-09-05
**Author**: wright
**Traces to**: `01-REQUIREMENTS.md` (US-1..US-4), `NORTH-STAR.md`, `INTAKE.md` amendment
(2026-09-05), DDR-0014 (spec-of-record, `gap-lens-dilution-filter`).

---

## 0. Scope Reminder

This document resolves AD-1 (detection rule), confirms/extends the citation convention, specifies
the Stop-hook wrapper (reusing `first-turn-contract-enforcement`'s shape verbatim, not
redesigning it), and specifies the `log_only`/`blocking` mode switch. No domain-crossing
precondition appears anywhere below — the check fires on any threshold-shaped literal regardless
of where it was defined, per the 2026-09-05 amendment.

---

## 1. AD-1 — Detection Rule for "Threshold-Shaped Literal"

### 1.1 Candidates compared

| Approach | Mechanism | Precision | Recall | Verdict |
|---|---|---|---|---|
| (a) Fixed syntactic contexts | AST match on: (i) comparison operands (`<`, `<=`, `>`, `>=`, `==`, `!=`) where one side is a numeric/boolean literal and the other side is a name/attribute; (ii) default values of function/method parameters or `dataclass`/`NamedTuple`/constant assignments whose target identifier matches a threshold-suggestive name pattern; (iii) slice/truncation arguments (`[:N]`, `str[:N]`, `.head(N)`-shaped calls, `itertools.islice`) where `N` is a literal | High — every match is a literal sitting in a position that is structurally a bound/cutoff | Moderate — misses thresholds expressed as free-standing named constants used only later (e.g. `MAX_RETRIES = 5` then `for i in range(MAX_RETRIES)`) unless (ii) also matches the assignment itself | **Selected** |
| (b) Naming-convention heuristic only | Regex over identifier names for `limit\|cap\|threshold\|cutoff\|retry\|budget\|max_\|_max\|min_\|_min` anywhere the identifier is assigned a literal | Low — flags `max_workers=4` (a concurrency knob, not a scientific/domain threshold) and `retry` used for network jitter as readily as a research-relevant cap; also flags nothing when a threshold is named non-suggestively (e.g. `n = 500`) | High on name-matching literals, zero on the rest | Rejected — precision failure reproduces exactly the false-confidence pattern rule 1 exists to prevent (flags noise, trains reviewers to dismiss the hook) |
| (c) Explicit per-file manifest | A human-maintained list of file:line locations to check | Perfect by construction (only what's listed) | Zero for anything not manually added — defeats the mechanization goal (Problem Statement: "depends on someone remembering") | Rejected — reintroduces the exact human-memory dependency this sprint exists to remove |

### 1.2 Selected rule: (a), fixed syntactic contexts, name-pattern-gated

Rule (a) alone (pure AST-position matching with no name filter) over-fires on ordinary loop
bounds and array indices, which the requirements explicitly exclude (Edge Cases table, row 1).
Rule (b) alone under- and over-fires as shown above. The selected rule is **(a) gated by a name
pattern applied only to the two contexts where a bare positional match is ambiguous** — this is
not rule (b) revived, because the name pattern is never sufficient on its own to flag; it only
narrows an already-structural match.

**Concrete rule** (three independently-sufficient match contexts; a literal is flagged if it
matches ANY of the three):

1. **Comparison-operand context** — a numeric or boolean literal appears as one operand of a
   comparison operator (`<`, `<=`, `>`, `>=`, `==`, `!=`) against a name or attribute access (not
   against another literal — `2 == 2` is not a threshold comparison). No name-pattern gate here:
   position alone is sufficient, because a bare `if size > 5_000_000:` is structurally a
   threshold check regardless of what `size` is called. **Excluded**: comparisons inside a `for`
   loop's `range(...)` call or a list/string index expression (`arr[i]`, `s[:n]` handled
   separately under context 3) — these are loop bounds/indices, not thresholds, per the
   requirements' own exclusion.
2. **Named-constant or default-kwarg assignment context** — a numeric or boolean literal is the
   right-hand side of (i) a module-level or class-level assignment, (ii) a `dataclass`/
   `NamedTuple`/`TypedDict` field default, or (iii) a function/method parameter default — AND the
   target identifier matches (case-insensitive) the pattern
   `(limit|cap|threshold|cutoff|retry|retries|budget|max|min|floor|ceiling)` as a whole word or
   `snake_case`/`camelCase` segment (e.g. `MAX_RETRIES`, `retry_budget`, `sizeLimit`, but not
   `maxwell_coefficient` — segment boundary required, not substring). The name gate exists here
   (unlike context 1) because a bare assignment (`x = 5_000_000`) is syntactically
   indistinguishable from an ordinary configuration constant without it, and the requirements
   exclude "ordinary values" — the name pattern is the one operationalizable signal available at
   this syntactic position.
3. **Slice/truncation-argument context** — a numeric literal appears as the stop argument of a
   slice (`x[:N]`, `x[a:N]`), or as a positional/keyword literal argument to a call whose callee
   name matches `(head|take|truncate|limit|first)` (e.g. `.head(500)`, `itertools.islice(x, 500)`,
   `df.head(n=500)`). No name gate on the literal itself is needed — the callee/slice position is
   the structural signal, mirroring the gap-lens-dilution-filter byte-cap incident's exact shape
   (a slice/truncation argument, per DDR-0014).

**Explicit exclusions** (never flagged regardless of context): literals used as `range()` bounds,
list/array/string index literals not in slice-stop position (`arr[0]`), literals in test files
(`test_*.py`, `*_test.py`, `conftest.py` — asserting an expected count is not defining a
production threshold), and literals `0`, `1`, `-1`, `2` in any context (universally-idiomatic,
zero information value as a "threshold" — flagging them would be pure noise per DDR-0014's own
precedent of the WHO byte-cap being a specific, non-idiomatic number).

This rule is fully specified — no "configurable" or "decided at implementation time" residue.
Language scope: Python only for v1 (both incidents were Python; extending the AST matcher to other
languages is out of scope, not silently assumed — flagged as a Non-Goal in §7).

---

## 2. Citation / PROVISIONAL-Tag Convention

### 2.1 Reuse confirmed, with one addition

The existing convention (`~/.claude/CLAUDE.md` Decision Discipline, rule 1) is sufficient as the
*content* format: a citable source, or `PROVISIONAL — unvalidated` with a named owner. It is
**not** sufficient as a *location* format on its own — CLAUDE.md's convention was written for
narrative docs (specs, architecture docs), not source code, and does not specify how close
"adjacent to its definition" must be in code. This architecture adds that missing location rule;
it does not change the tag's content grammar.

### 2.2 Location rule (new, scoped to this hook only)

A citation or PROVISIONAL tag counts as "at or adjacent to" a flagged literal's definition if it
appears as a `#` comment on the same line as the literal, or on any of the up-to-3 lines
immediately preceding it, containing either:
- the literal string `PROVISIONAL` followed within the same comment block by `owner:` or `owner=`
  and a non-empty name token, or
- a URL, file path (containing `/` or `.md`/`.py`), or a parenthetical citation matching
  `\(.*(commit|DDR|PR|#)\w*\)` — matching this repo's existing citation style seen in
  `first-turn-contract.sh` itself (e.g. `docs/tooling/first-turn-contract-enforcement.md §3.4`).

**3-line lookback is a PROVISIONAL value, not a cited precedent** — no prior hook in this repo's
history has needed a "how far back does an adjacent comment count" rule, so there is no citable
precedent to point to. **PROVISIONAL — owner: wright.** Chosen as a starting value matching the
observed comment-block depth in this repo's own recent PROVISIONAL tags (see
`first-turn-contract.sh` line 72's multi-line comment block, which spans more than 3 lines above
its `timeout 5` — meaning this rule as specified would itself under-detect that exact citation and
require the owner to tune the lookback after first real-world runs). Flagged for revisit once the
hook has run against this repo's own codebase at least once (see §6).

### 2.3 Removal path

Per requirements US-1/Edge Cases, a threshold that has been removed (inlined without a magic
number) produces no literal for the AST matcher to find in the first place — "removal" is
satisfied by the absence of a match, not by a separate code path the hook implements.

---

## 3. Trigger Surface

**Selected: Stop hook**, matching `first-turn-contract-enforcement`'s trigger (not PreToolUse, not
a scheduled scan).

Rationale, compared against the requirements' own candidates (Open Question 3):
- **PreToolUse on Edit/Write**: rejected — would require the hook to reconstruct whether a given
  Edit introduces a *new* flagged literal vs. one pre-existing in the file, adding a diff-aware
  code path this hook does not need; the requirements do not ask for per-edit granularity, only a
  session-end scan (US-1's "when the Stop-hook runs" framing, carried from Intake unmodified).
- **Pre-commit-style (git hook)**: rejected — this repo's chosen mechanization pattern for
  in-session checks is Claude Code's own hook system (`first-turn-contract-enforcement`,
  `progress-proof-per-slice.sh`), not git hooks; introducing a second mechanism family for one
  check fragments the pattern DDR-005 argues for consolidating.
- **Scheduled/on-demand scan**: rejected as the *sole* mechanism — reintroduces the "someone has
  to remember to run it" failure mode the Problem Statement names directly; Stop hook fires
  automatically every session end with no operator action required.

Scan target: files touched (added/modified) in the current session per `git diff` against the
session's starting ref, sourced the same way `first-turn-contract.sh`'s probe already has access
to session context (transcript path via stdin) — full-repo scan on every Stop is not required by
any acceptance criterion and would make `log_only` noisy from unrelated pre-existing files on
day one beyond what's needed to triage the current session's own changes. (Full-repo baseline scan
for initial triage is a one-time manual invocation, not a hook responsibility — see §6.)

---

## 4. Components

| Component | Responsibility | Location |
|---|---|---|
| `unsourced-threshold.sh` | Stop-hook wrapper: capture stdin, invoke probe under bounded timeout, validate probe output shape, fail open on any error, never itself contain detection logic | `.claude/hooks/unsourced-threshold.sh` |
| `unsourced_threshold_probe.py` | Probe: resolve session's changed Python files via git diff, run the AST detection rule (§1) against each, check citation adjacency (§2) for each match, emit `allow`/`block` JSON per mode, write its own track-record line | `scripts/unsourced_threshold_probe.py` |
| Track-record log | Append-only JSONL, one entry per hook invocation (pass, flag, or error) | `docs/tooling/unsourced-threshold-track-record.jsonl` |
| Mode config | Per-repo `log_only`/`blocking` switch | `.claude/hooks/unsourced-threshold.config.json` (new, `{"mode": "log_only"}` default) — kept out of `settings.json` itself so promoting to `blocking` is a one-file edit, not a hook-wiring change |

---

## 5. Data Schemas

```python
# unsourced_threshold_probe.py — internal shapes (dataclasses, not persisted beyond the log)

@dataclass
class FlaggedLiteral:
    file: str                # repo-relative path
    line: int                # 1-indexed
    context: str              # one of: "comparison", "assignment_or_default", "slice_or_truncation"
    literal_repr: str         # source text of the literal, e.g. "5_000_000"
    matched_name: str | None  # identifier that triggered a name-gated context; None for context 1/3
    reason: str               # human-readable, e.g. "comparison operand against 'size', no citation found within 3 lines"

@dataclass
class ProbeResult:
    mode: Literal["log_only", "blocking"]
    files_scanned: list[str]
    flagged: list[FlaggedLiteral]
    decision: Literal["allow", "block"]   # "block" only possible if mode == "blocking" and flagged is non-empty
```

```typescript
// Track-record entry (JSONL, one object per line) — same top-level shape family as
// first-turn-contract-track-record.jsonl (timestamp, session_id, decision) with fields specific
// to this check appended, not a divergent schema.
interface UnsourcedThresholdTrackRecordEntry {
  timestamp: string;            // ISO 8601 UTC
  session_id: string | null;
  mode: "log_only" | "blocking";
  files_scanned: string[];
  flagged_count: number;
  flagged: Array<{
    file: string;
    line: number;
    context: "comparison" | "assignment_or_default" | "slice_or_truncation";
    literal_repr: string;
    reason: string;
  }>;
  decision: "allow" | "block" | "probe_error";
  probe_error: string | null;   // populated only when decision === "probe_error"
}
```

```json
// .claude/hooks/unsourced-threshold.config.json
{ "mode": "log_only" }
```

---

## 6. API Contracts

```python
def find_changed_python_files(repo_dir: str, base_ref: str) -> list[str]:
    """Files changed in the current session vs. base_ref, filtered to *.py, excluding
    test_*.py/*_test.py/conftest.py per §1.2 exclusions."""

def detect_threshold_literals(file_path: str) -> list[FlaggedLiteral]:
    """AST walk applying the three match contexts from §1.2. Returns literals with NO
    adjacency check applied yet (citation check is a separate pass, §2)."""

def has_adjacent_citation(file_path: str, line: int) -> bool:
    """Implements the §2.2 lookback rule (same line + up to 3 preceding lines)."""

def run(mode: Literal["log_only", "blocking"], changed_files: list[str]) -> ProbeResult:
    """Orchestrates detect + citation-check per file, applies mode to decision, writes its own
    track-record line on every path (mirrors first_turn_contract_probe.py's write-before-emit
    invariant, spec §6 of that hook)."""
```

Wrapper (`unsourced-threshold.sh`) contract: identical shape to `first-turn-contract.sh` verbatim
— same stdin capture, same `timeout N` invocation, same stdout-shape validation
(`{}`/no-`decision`-key = allow; `{"decision":"block","reason":str}` = block; anything else =
probe failure → fail open), same `write_probe_error` fallback writer for paths where the probe
never got to write its own line. This is a reuse, not a new design — see §7 for the one
new-vs-inherited constant.

---

## 7. Patterns, Dependencies, Constants

| Pattern | Usage | Rationale |
|---|---|---|
| Stop-hook wrapper + subprocess probe, bounded timeout, fail-open | `unsourced-threshold.sh` / `unsourced_threshold_probe.py` | Cited precedent: `first-turn-contract-enforcement` (`docs/tooling/first-turn-contract-enforcement.md` §3.4/§4.2, `.claude/hooks/first-turn-contract.sh`). Not redesigned per Constraints. |
| Append-only JSONL track record | `docs/tooling/unsourced-threshold-track-record.jsonl` | Same precedent, same file family (`first-turn-contract-track-record.jsonl`) — one schema per check, not a shared file, matching the existing pattern of per-hook logs. |
| AST-based structural matching over regex-only heuristics | `detect_threshold_literals` | §1.2 rationale — regex-only (candidate b) rejected for precision failure. |
| Per-repo JSON config file for mode switch, separate from `settings.json` | `unsourced-threshold.config.json` | No existing precedent in this repo for a hook-specific mode file; chosen over a `settings.json` env-var because promoting to `blocking` should not require editing the hook-wiring file Frank/reviewers scrutinize for hook *registration*, only a small dedicated config. This is a new pattern, not a cited one — flagged as **PROVISIONAL, owner: wright**, revisit if a second mode-switchable hook is ever added (should the pattern generalize to a shared config, or stay per-hook). |

**Anti-patterns (do not use)**:
- Domain-crossing / import-graph detection of any kind — explicitly dropped by the 2026-09-05
  amendment; no code path may reconstruct it.
- Regex-only name matching as the sole detection signal (candidate b, §1.1) — rejected for
  precision.
- A shared track-record file across multiple hooks — breaks the one-schema-per-log precedent and
  couples unrelated hooks' failure/log formats.

### Constants introduced by this sprint (Decision Discipline compliance check)

| Constant | Value | Source |
|---|---|---|
| Wrapper subprocess timeout | 5s | **Not a fresh number** — copied directly from `first-turn-contract.sh`'s cited 5s bound (line 72-79 of that file: "PROVISIONAL — owner: wright. 5s budget... measured directly against this probe"). That measurement does not transfer to this probe (different workload: AST-walking a diff's worth of Python files vs. parsing a transcript) — so this is re-flagged here as **PROVISIONAL, owner: wright, unmeasured for this probe**, not silently inherited as if re-validated. Must be measured against this probe's actual runtime once built (mirrors how the precedent hook measured its own 167ms/85ms figures) before this PROVISIONAL can be closed out. |
| Citation lookback window | 3 lines | **PROVISIONAL, owner: wright** — see §2.2; no citable precedent exists in this repo for comment-adjacency depth in source code (only in narrative docs). Flagged for revisit after first real-world run against this repo. |
| Excluded idiomatic literals | `{0, 1, -1, 2}` | **PROVISIONAL, owner: wright** — chosen by inspection of DDR-0014's own incident literals (all were far outside this set: byte caps and market-cap floors are multi-digit domain-specific numbers), not by any external benchmark. No citable source exists; flagged rather than fabricated as if derived. |
| Name-pattern gate word list (`limit|cap|threshold|cutoff|retry|retries|budget|max|min|floor|ceiling`) | — | Not a numeric constant, so Decision Discipline's "citable precedent or PROVISIONAL" applies more loosely (it is a design choice, not a magic number) — but flagged as **PROVISIONAL, owner: wright** for completeness, since an incomplete word list has the same silent-failure shape as an uncited number: it will under-detect without anyone noticing. Revisit after first real-world run. |

No constant in this table is treated as finalized without an owner or a source — every row is
either a direct citation to an existing measured value (timeout, re-flagged as unmeasured for
*this* probe) or an explicit named-owner PROVISIONAL.

### Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib `ast` module | (stdlib, already used by `first_turn_contract_probe.py`'s repo) | AST parsing for detection rule — no new external dependency |
| Python 3 stdlib `subprocess`/`json`/`datetime` | (stdlib) | Wrapper/probe plumbing, matches precedent hook | 

No new third-party libraries — matches `first-turn-contract-enforcement`'s zero-new-dependency
footprint.

---

## 8. Integration Points

- **`.claude/settings.json`**: add a new `Stop` hook entry, sibling to the existing
  `first-turn-contract.sh` entry (same array, additional object) — does not replace or reorder the
  existing entry.
- **`docs/tooling/`**: new track-record log and a new `unsourced-threshold-enforcement.md` spec
  doc (implementation-time artifact, mirroring `first-turn-contract-enforcement.md`'s role as the
  probe's own detailed spec — out of scope for this architecture doc to pre-write, but flagged so
  forge knows it's expected, matching the precedent hook's documentation shape).
- **`git`**: probe shells out to `git diff` (or reads `git status`-equivalent) to find the current
  session's changed files — read-only, no git state mutation.
- **DDR-0014** (`gap-lens-dilution-filter`): this build implements the detection rule DDR-0014
  assigned to agent-rig; no code-level integration, citation-only per Constraints.

---

## 9. Mode Switch: `log_only` vs `blocking`

- Config file `unsourced-threshold.config.json` (§4) is read by the probe at the start of `run()`.
  Missing file or missing `mode` key defaults to `log_only` (fail-safe default, not just
  initial-install default — matches Edge Cases table row "no repo's hook ships in blocking mode").
- `log_only`: `ProbeResult.decision` is always `"allow"` regardless of `flagged`; the flagged list
  is still fully populated and written to the track-record log (US-2's "writes findings... does
  not block").
- `blocking`: `ProbeResult.decision` is `"block"` if `flagged` is non-empty, `"allow"` otherwise.
  The wrapper relays this exactly as `first-turn-contract.sh` relays its probe's block/allow
  (§6's contract) — no new relay logic needed in the wrapper.
- No migration/upgrade path is implemented for auto-promoting a repo from `log_only` to
  `blocking` — promotion is a manual one-line edit to the config file by the repo owner, per
  Constraints ("never bundled into initial install").

---

## 10. Requirements Coverage

| Requirement | Covered by |
|---|---|
| US-1 (detect + flag) | §1 detection rule, §5 `FlaggedLiteral`, §6 `detect_threshold_literals` |
| US-1 AC4 (no domain-crossing condition) | §1.2 rule contains no import/boundary check anywhere; §0 restated |
| US-2 (log_only default, blocking opt-in) | §9 |
| US-3 (fail-open, bounded timeout, append-only log) | §3 trigger, §6 wrapper contract (verbatim reuse), §7 timeout constant, §5 track-record schema |
| US-4 (presence-only, no soundness judgment) | §2 citation convention checks presence of tag/citation text only, never evaluates truth of a citation's content — no code path in §6 does so |
| AD-1 | §1 (this document's core resolution) |
| Every introduced constant sourced/PROVISIONAL | §7 table |

---

## 11. Non-Goals (explicit, for Frank/forge)

- Multi-language support beyond Python (§1.2).
- Full-repo baseline scan as a hook responsibility (§3) — a one-time manual invocation of the
  probe script directly (not via the Stop hook) is the intended path for initial-triage baselining
  of a newly-installed repo; this is not a separate component, just the same probe script run
  by hand with `changed_files` supplied as the full file list instead of a git diff.
- Auto-promotion from `log_only` to `blocking`.
- Retrofit into `gap-lens-dilution-filter` or any other repo (Out of Scope, requirements).
- Solving DDR-010's overlapping shape (`market_data`).

---

## HALT Check

No HALT triggered. AD-1 is resolved with one concrete rule (§1.2), no design decision was left
"configurable," and every introduced constant is either cited (timeout, re-flagged as
unmeasured-for-this-probe) or an explicit named-owner PROVISIONAL (lookback window, idiomatic
literal set, name-pattern word list, config-file-vs-settings.json pattern choice). The one item
carried forward as a known gap rather than resolved here: the 5s timeout's applicability to this
probe's actual (not yet measured) runtime — this is not a HALT because the precedent hook's own
process was identical (ship a PROVISIONAL bound, measure at forge time, tighten if needed), not a
gap unique to this sprint.
