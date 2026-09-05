# Architecture: Unsourced-Threshold Provenance Hook — Extension of the Incumbent

**Status**: DRAFT (revision pass — supersedes this document's prior version in full)
**Date**: 2026-09-05
**Author**: wright

## 0. Correction Notice (read first)

The prior version of this document designed a brand-new Stop-hook with syntactic AST-based
detection, on the premise "currently nothing exists." That premise was false, per
`05-REVIEW.md` G-1 (Critical): a complete, Frank-forge-gate-PASSED implementation of DDR-006
already exists — `.claude/hooks/domain-boundary-provenance.sh`,
`scripts/domain_boundary_provenance_probe.py`, LOCKED spec
`docs/tooling/domain-boundary-provenance-hook.md` — merged via PR #11, listed in
`HOOK-DEPLOYMENT-ROSTER.md`, unwired from `.claude/settings.json`.

**Danny's decision (settled, not re-asked here): extend the incumbent, do not replace it.**

This document therefore:
- Discards the prior AD-1 resolution (fixed-syntactic-contexts detection, Stop trigger,
  `PROVISIONAL` reused as citation marker).
- Leaves the incumbent's manifest-gated cross-domain check completely untouched — same trigger
  surface (`PreToolUse` on `Edit`/`Write`), same manifest schema, same `DOMAIN-BOUNDARY:` marker,
  same scan surface (`tool_input.content`/`new_string` only). No redesign of any of that follows.
- Designs a **new, additive** same-file/local threshold-literal detection pass that composes with
  the incumbent inside the same wrapper/probe invocation.
- Resolves rollout (wiring the incumbent live at all is in scope, per task instruction 5) and the
  citation-marker question for the new check.

This resolves review Open Questions OQ-A (extend, not replace/coexist-as-second-hook) and OQ-B
(re-run comparison against the incumbent's actual shape — the incumbent's manifest design is
correct and un-redesigned for its own scope; the new check does not use a manifest because its
whole purpose is same-file literals a manifest author cannot pre-declare).

### 0.1 Benchmark Audit Correction Notice (this revision)

A `benchmark` agent audit (2026-09-05) ran actual measurements against this repo's own codebase
and found several constants below were not just unlabeled — they were wrong, with measured
false-positive/false-negative evidence, and one section (§7's original marker-comment text)
contained a genuine self-refuting bug (a 5-line comment block prescribed to satisfy a 3-line
detection window). This revision applies every finding. Per this repo's binding rule (CLAUDE.md
Decision Discipline), no constant in this document rests on a self-assigned or unassigned
`owner:` tag anymore — each one now carries either a real citation, a fully-stated executable
benchmarking plan with an explicit "not yet validated" disposition, or a redesign that removes the
need for it. The specific corrections are documented inline at each affected section (§2, §4, §5,
§7, §8, §13) rather than summarized here, so a reader hits the reasoning at the point of use.

## 1. What Changes and What Doesn't

| Surface | Incumbent (unchanged) | New (this document) |
|---|---|---|
| Trigger | `PreToolUse`, `Edit`/`Write` | Same event, same invocation (composed, not duplicated) |
| Wrapper | `.claude/hooks/domain-boundary-provenance.sh` | Same file, extended |
| Probe entrypoint | `scripts/domain_boundary_provenance_probe.py` | Same file, extended with a second detection pass |
| Gating | Per-repo manifest (`pipelineConfigGlobs` + `externalSourceIdentifiers`) | No manifest — runs against any Python file's proposed content, unconditionally (subject to mode gate, §5) |
| Scan surface | `tool_input.content` / `tool_input.new_string` | Same convention, reused verbatim (task instruction 3) |
| Citation marker | `DOMAIN-BOUNDARY:` | New marker, `THRESHOLD-PROVENANCE:` (§4) |
| Decision combination | N/A (only check) | Two independent passes, one combined decision (§3) |

Nothing below re-litigates §2–§13 of `docs/tooling/domain-boundary-provenance-hook.md` for the
manifest-gated check. That document's decision procedure, schemas, and rationale stand as-is and
are cited by reference, not restated.

## 2. Detection Rule for the New Check (AD-1, resolved for the local-literal case — REDESIGNED per benchmark audit)

**Decision, revised this pass: drop the name-gated context entirely; flag on syntactic shape
alone.** The prior draft's AD-1 kept a name-gated "default-kwarg/assignment" context (matching
target names against a 10-word list: `limit, cap, threshold, cutoff, retry, retries, budget,
timeout, max, min`). The benchmark audit measured this against this repo's own code and found it
does not work as designed:

- **8 of the 10 words never fire at all** in this repo (`limit, cap, threshold, cutoff, retry,
  retries, budget, min` — zero hits). Only `timeout` and `max` ever match (5 hits each).
- **Substring matching produces real false positives** — 11 measured in this repo alone: `cap`
  matches inside `escaped_rest`, and `min` matches inside `REMINDER_PATH`, `REMINDER_TEXT`, and
  `_load_reminder`.

The benchmark's recommendation is redesign, not re-tuning, and this document adopts it: **context
2 (name-gated assignment/default) is removed.** Detection now runs only on the two
shape-based contexts, which need no vocabulary and therefore have no substring-false-positive
failure mode:

**Contexts that count as "threshold-shaped":**
1. **Comparison operand**: a numeric literal appearing as either operand of a comparison
   (`<`, `<=`, `>`, `>=`, `==`, `!=`) — e.g. `if retries > 3:`.
2. **Slice/truncation argument**: a numeric literal used as a slice bound (`x[:50000]`) or as an
   argument to a truncation-shaped call (`str[:N]`, `.ljust(N)`, `[:N]` generally).

Both remaining contexts fire on syntactic shape alone, independent of naming — there is no
name-gated context left in this design. The `log_only` mode (§5) and the `THRESHOLD-PROVENANCE:`
citation convention (§4) absorb whatever additional volume this produces, per the benchmark's own
recommendation ("let `log_only` volume and the citation convention absorb the rest").

**A direct consequence of this redesign**: because no context is name-gated anymore, no assignment
statement (e.g. `PROXIMITY_WINDOW = 5`) is ever flagged by this check purely because of its
variable name — only literals that are themselves comparison operands or slice/truncation
arguments are in scope. This resolves the self-scan question the prior draft raised in §7/§8
(there is no name-gate left to fire on the probe's own constants); see §7 and §8's updated
disposition.

**Explicit exclusions** (never flagged, regardless of context match):
- **`range()` call bounds (first, second, or third positional argument) — LANGUAGE FACT, not a
  benchmarked value.** Python's `range()` accepts exactly one, two, or three positional arguments
  (`stop`; or `start, stop`; or `start, stop, step`) — this is definitional per the Python
  Language Reference (`range` built-in function,
  https://docs.python.org/3/library/functions.html#func-range), not an empirical claim, and
  carries no PROVISIONAL tag because there is nothing to measure: a fourth positional argument to
  `range()` is a `TypeError` at the language level, so "any of the first three positional
  arguments to `range()`" is a closed, syntactically-checkable set.
- A non-slice-stop index into a sequence (`x[i]`, not `x[:i]`).
- Files under any `test`/`tests`/`fixtures` path component.
- **The literal values `{0, 1, -1, 2}`** — see disposition immediately below. **NOT YET
  BENCHMARKED. Do not treat as validated until the stated plan runs.**

**Disposition of the `{0, 1, -1, 2}` exclusion set (benchmark audit finding, highest-leverage
constant in this design).** The benchmark agent measured this set directly against this repo: 61
of 72 threshold-shaped literal candidates (84.7%) fall inside `{0, 1, -1, 2}`. This makes it the
single highest-impact value in the entire detection rule, and it was chosen with zero measurement
in the prior draft. Per this repo's binding rule, it cannot ship with a bare `owner:` tag. The
disposition is: **this value is not yet benchmarked, and carries the following executable plan as
its validation path (Roadmap concern, not yet run):**

1. Run the local-threshold detection pass **unfiltered** (i.e. with the `{0, 1, -1, 2}` exclusion
   temporarily disabled) against a defined corpus: this repo (`agent-rig`) plus the seven repos
   currently listed in `HOOK-DEPLOYMENT-ROSTER.md`, plus `market_data`.
2. Dump every resulting candidate (file, line, literal value, context) to a JSONL file.
3. Draw a stratified random sample of 200 rows from that JSONL (stratified by literal value, so
   `0`, `1`, `-1`, `2`, and non-excluded values are all represented rather than dominated by
   whichever value is most common).
4. Hand-label each sampled row true-positive ("this literal genuinely needed a provenance
   citation") or false-positive ("this is an idiomatic loop/sentinel/increment value that citation
   would not meaningfully improve").
5. For each candidate value in `{0, 1, -1, 2}` (and any other value considered for exclusion),
   compute its measured precision as a true positive across the labeled sample. **Exclude a value
   from flagging only if its measured precision falls below 5%.** Values at or above that
   threshold stay in scope for flagging even if they are numerically small.
6. Until this run happens, the current `{0, 1, -1, 2}` exclusion set ships as an inherited,
   unvalidated default — not a validated design decision. Any false negative it produces (a real
   unsourced threshold at exactly `0`, `1`, `-1`, or `2` that goes unflagged) is a known, named risk
   of shipping ahead of the benchmark, not a silent gap.

This is a Roadmap-tracked open item (§13), not resolved by this architecture document — the
benchmarking run itself requires the corpus scan described above, which is out of scope for an
architecture-fix task and belongs to implementation/forge follow-up.

**AST-based, Python-only, no regex fallback** — same posture as the prior pass: syntactic
detection needs a real parse tree to reliably distinguish "is this a comparison operand" from
"is this token merely near a `<`". Python's stdlib `ast` module is a new import for this probe
file (not currently used anywhere in this repo's hook tooling), but it is stdlib, so it carries
no new third-party dependency cost (§9).

**Scope note**: per Out of Scope in `01-REQUIREMENTS.md`, Python-only is an accepted narrowing,
not a silent gap — Bash/TS/JSON thresholds in this repo are not scanned by v1 of either check.

## 3. Composition: Two Passes, One Decision

Both checks now run from the same `PreToolUse` invocation of `domain-boundary-provenance.sh` →
`domain_boundary_provenance_probe.py`, against the same stdin envelope
(`DomainBoundaryHookInput`, unchanged, §7). The probe's `run()` is restructured to perform two
independent passes and combine their results:

```
run(stdin_data):
    tool_name, tool_input, project_dir  # unchanged extraction

    if tool_name not in ("Edit", "Write"):
        allow (unchanged, §6 step 1 of incumbent doc)

    scan_surface = get_scan_surface(tool_name, tool_input)   # unchanged helper, reused as-is

    cross_domain_result = run_cross_domain_pass(project_dir, tool_input, scan_surface)
        # == incumbent's existing steps 2-7, UNMODIFIED logic, extracted into a named function
        # for composition. Still manifest-gated; still allows silently if no manifest/no
        # in-scope match.

    local_threshold_result = run_local_threshold_pass(tool_name, raw_file_path, scan_surface, mode)
        # == new detection (§2, §4), gated only by file extension (.py) and mode (§5) —
        # NOT gated by any manifest.

    combined = combine(cross_domain_result, local_threshold_result)
    write_track_record(combined)   # single entry, both passes' findings folded in (§6 schema)
    emit combined.decision (block if either pass denies and mode allows blocking; else allow)
```

**Combination rule**: a `PreToolUse` call may only ever emit one `{"decision": "block", "reason":
...}` payload (§3 of the incumbent doc — this is a hard constraint of the deny schema, not a
design choice available to revisit). If both passes find unmarked matches, the combined `reason`
string concatenates both passes' findings, clearly labeled by check name (`[domain-boundary]` /
`[threshold-provenance]`), so a denied edit's remediation is unambiguous about which marker is
missing where. If either pass alone denies, that pass's reason is used unmodified. If both pass
(or find nothing), the whole call allows.

**Why one wrapper/probe instead of two separate hook entries**: task instruction 3 requires this;
additionally, both checks operate on the identical scan surface and stdin envelope — a second
independent hook process would re-parse the same `tool_input` and double the invocation overhead
for zero decision-quality gain. `first-turn-contract.sh`'s own pattern (one wrapper, one probe,
one decision) is preserved at the level of "one hook installation," which is what
`.claude/settings.json` wiring (§5) actually registers.

**No manifest coupling**: the new pass takes no manifest input and is not affected by a target
repo having no `domain-boundary-manifest.json` — that absence only short-circuits the cross-domain
pass (per the incumbent's own step 2 "absent → allow" rule, unchanged). The new pass runs
independently of manifest presence, since its entire premise (per the DDR-0014 amendment) is that
manifest-based gating is exactly the mechanism that let same-file thresholds go unscanned.

**Reconciliation with the LOCKED doc's recorded rejection of unscoped blocking (05-REVIEW.md
G-7).** `docs/tooling/domain-boundary-provenance-hook.md` §3 explicitly rejected "`PreToolUse`,
unscoped (every `Edit`/`Write`)" as a *blocking* check, on false-positive-noise grounds — the
manifest glob scope was called "required to keep this both correct and low-noise." The new
local-threshold pass is, by shape, exactly that rejected surface: it runs on every `.py`
`Edit`/`Write`, with no manifest gate. This document does not treat that as settled by silence.
The reconciliation is: **the LOCKED §3 rejection was scoped to a check that blocks**; §5's
`log_only` default is the mechanism that keeps this pass outside the scope of that rejection *for
now* — under `log_only`, an unscoped match never blocks anything, so the noise the LOCKED doc
warned about surfaces only as track-record log entries (Slice 12), not as disrupted edits. This is
not the same shape under a different name; it is the same shape with the one property (blocking)
that made the rejection apply, deliberately withheld pending data. **What would justify promoting
it to blocking despite the LOCKED rejection**: real track-record data (accumulated under
`log_only`, per repo, per §5) showing the false-positive rate on that repo's own `.py` edits is low
enough that a repo owner's manual triage judges blocking acceptable for their codebase — the same
per-repo promotion decision the DDR-0014 amendment's Rollout section already requires for the
cross-domain check. Absent that data, the correct reading of the LOCKED rejection is "do not ship
this pass in blocking mode," which §5 already guarantees as the initial state. No promotion
decision is made or implied by this document; this paragraph exists so a future promoter meets the
LOCKED doc's argument explicitly rather than rediscovering or silently overriding it.

**Explicit naming of the LOCKED-doc behavior change (F1, Frank spec-gate attempt 1).** The above
reconciliation has a direct, previously-unstated consequence for the incumbent's own LOCKED text:
`docs/tooling/domain-boundary-provenance-hook.md` §6 step 6 and AC4 currently read as unconditional
— "an unmarked identifier match → deny" / "an unmarked cross-domain read is denied." **That is no
longer true as shipped by this sprint.** Under the `mode` gate (§5), the cross-domain pass's deny
now fires only when `mode == "blocking"`; under the shipped default (`log_only`), the same
condition that the LOCKED doc calls "denied" instead produces `decision: "flag"` (§6) and the
`PreToolUse` call allows. This is a real behavior change to a LOCKED spec's stated outcome, not a
new document overriding an old one by omission — it is named here explicitly so it is not
discovered later as an undocumented contradiction. The LOCKED doc's own §2–§10 text is not edited
(Roadmap Slice 11 keeps it byte-identical); instead, the addendum appended in that slice states
this exact gating relationship in so many words, per Roadmap Slice 11's revised rule (see that
slice for the corrected instruction — it no longer forbids saying what changed).

## 4. Citation Marker for the New Check

**Decision: new marker, `THRESHOLD-PROVENANCE:`. Does not reuse `DOMAIN-BOUNDARY:` or bare
`PROVISIONAL`.**

**Rationale, following the incumbent's own §5 reasoning pattern (not re-litigating it, applying
it to a third case):**
- **Not `PROVISIONAL` alone** — same objection the incumbent's §5 already establishes: a bare
  `PROVISIONAL — [disposition]` tag asserts "not yet validated," which is one of the amendment's
  three satisfying conditions (option b) but not the only one. A citation to a reproducible source
  (option a) is a different, stronger claim than PROVISIONAL and needs a marker that doesn't
  presuppose "unvalidated." Reusing bare `PROVISIONAL` as the universal marker would make option
  (a)'s citations indistinguishable from option (b)'s admissions in a mechanical text-presence
  scan, which is exactly the ambiguity DDR-0014's own citation-format open question (Interview,
  01-REQUIREMENTS Constraints) flagged as not yet confirmed sufficient. The requirements doc
  already anticipates the existing PROVISIONAL convention might prove insufficient (Constraints:
  "flagged as not yet confirmed sufficient... if architecture finds it insufficient, that is an
  architecture-level finding, not a requirements gap") — this is that finding.
- **Not `DOMAIN-BOUNDARY:`** — per the incumbent's own §5, that marker's semantic is specifically
  "this value crossed from another domain and here is why it's correct for this consuming site."
  A same-file threshold that never crossed anything is not a domain-boundary claim; forcing it
  under that marker would make `DOMAIN-BOUNDARY:` comments appear on code that domain-boundary
  review has no reason to look at, diluting the marker's own signal value for its original
  purpose (cross-repo/cross-module retrofit triage, per DDR-0014's retrofit section).
- **`THRESHOLD-PROVENANCE:` accepts any of the three amendment-satisfying forms on one marker
  line**: a citation (option a), an explicit PROVISIONAL disposition naming what would validate it
  (option b) — the existing `PROVISIONAL — ...` string is still what appears, just now recognized
  by this marker rather than required to double as the marker itself — or is simply absent because
  the literal was removed (option c, which trivially satisfies the check by there being no literal
  left to flag). Concretely: `# THRESHOLD-PROVENANCE: PROVISIONAL — not yet benchmarked, see
  02-ARCHITECTURE.md §2 for the exclusion-set validation plan` is a valid, complete citation line
  satisfying option (b); `# THRESHOLD-PROVENANCE: see DDR-0014 §Amendment for why 5s is reused
  from first-turn-contract.sh's measured bound` satisfies (a).

**v1 citation rule for the new check** (deliberately mirrors the incumbent's §5 shape for
consistency, values re-justified independently, not copied):
- A citation is a comment line containing the literal marker `THRESHOLD-PROVENANCE:`
  (case-sensitive, exact string) followed by non-whitespace content on the same line.
- **The marker must appear within 5 lines (inclusive) above or below the line containing the
  flagged literal — the incumbent's own `PROXIMITY_WINDOW` constant (probe L51, value 5) is reused
  as-is for this check; no second window constant is introduced.** This corrects the prior draft
  of this document, which specified a new, tighter `PROXIMITY_WINDOW_THRESHOLD = 3` constant. That
  value has been dropped for two independent reasons, both from the benchmark audit:
  1. **It was empirically wrong.** The benchmark agent measured real commented constants in this
     repo and found 13 of 40 (32.5%) have their comment starting 4–5 lines above the assignment
     line — a 3-line window would miss a third of the real citations already in this codebase's
     own style, producing false "unmarked" flags against genuinely-cited code.
  2. **It was internally self-contradictory (self-refuting bug, benchmark finding #1).** The prior
     draft's §7 prescribed an exact 5-line comment block as the *only* acceptable
     `THRESHOLD-PROVENANCE:` marker text for `PROXIMITY_WINDOW_THRESHOLD`'s own assignment, while
     this same section required the marker to land within 3 lines of the literal it cites. A
     5-line comment cannot land within a 3-line window of the line it sits beside — the prescribed
     fix would have caused the probe to flag its own source line, undetected across two prior gate
     rounds because neither checked distance, only marker-string content.
  Reusing the incumbent's existing 5-line `PROXIMITY_WINDOW` resolves both problems at once: it
  matches the measured 32.5% long-comment population, and it removes the need to maintain two
  different window constants for two passes of the same hook — simpler, and no separate constant
  means no separate distance-vs-comment-length arithmetic to get wrong a second time. See §7 for
  the corresponding function-signature update and §8 for the self-scan disposition this also
  simplifies.
- Same location rule as the incumbent: citation lives in the same file as the flagged literal, not
  a separate doc.

## 5. Rollout: `log_only` Mode (new capability, both checks)

**Current state (confirmed by direct read, task instruction 5): the incumbent is NOT wired into
`.claude/settings.json`.** No `PreToolUse` entry exists for `domain-boundary-provenance.sh`
anywhere in the live hooks config. Getting the hook live at all — for both the incumbent
cross-domain check and the new local-threshold check — is in scope for this sprint.

**Decision: wire it live now under `log_only`, not straight to blocking.**

**Rationale:**
- `01-REQUIREMENTS.md` US-2 and `NORTH-STAR.md` both make `log_only`-first a Must, specifically
  because widening scope (dropping the domain-crossing precondition, per the amendment) surfaces
  every pre-existing same-file magic number in this repo — a class of finding the incumbent's
  manifest-gated design never touches today (manifest scope + cross-domain-only kept its blast
  radius small). The new check has no comparable natural narrowing; it runs on any `.py` file
  edited via `Edit`/`Write`, unconditionally.
- **The incumbent's cross-domain check has never run live in this repo** (unwired since 2026-08-22
  per the roster) — there is zero production track-record data on its own false-positive rate.
  Wiring both checks straight to blocking on day one would be the first time either check's real
  behavior against live editing sessions is observed, with the failure mode being a block, not a
  log line. That is the exact rollout risk `log_only`-first exists to absorb (DDR-0014 amendment's
  Rollout section, quoted directly: "report-only first, each repo owner triages existing constants
  against their own backlog, promotion to blocking is a separate per-repo decision").
- Fail-open (probe crash/timeout) already bounds the risk of an unrelated block from a bug: `mode`
  bounds the risk of a *correct* detection being disruptive before triage has happened.

**Design addition required: a `mode` config, since v1 of the incumbent is binary allow/deny with
no log-only concept.**

```typescript
/** New config file, sibling to the manifest, read by the probe at the start of run().
 *  Absent file -> mode defaults to "log_only" (fail-safe default: an uninstalled/unconfigured
 *  mode file must never default to blocking). */
interface DomainBoundaryModeConfig {
  schemaVersion: 1;
  /** "log_only": findings are written to the track-record log with decision "flag" (new value,
   *  §6) but the PreToolUse call always allows (never emits {"decision":"block"}).
   *  "blocking": findings that would deny under log_only instead actually deny. */
  mode: "log_only" | "blocking";
}
```

**Path**: `docs/tooling/domain-boundary-mode.json`, discovered relative to
`$CLAUDE_PROJECT_DIR` — same discovery convention as the manifest (§2 of the incumbent doc),
sibling file, not a field added to the manifest itself (kept separate because the mode applies to
*both* checks composed in §3, while the manifest only ever configured the cross-domain check;
folding mode into the manifest schema would misleadingly suggest mode is manifest-scoped).

**No existing precedent in this repo for a hook-specific mode file** — `first-turn-contract.sh`
has no equivalent (it has no graduated-severity concept, only allow/deny). This is a new,
minimal addition, schema-versioned the same way the manifest is, for the same forward-compat
reason.

**Behavior change to the decision procedure (§3's `combine`)**: when `mode` is `"log_only"`, any
pass that would otherwise produce a deny instead produces a track-record entry with
`decision: "flag"` (new value, §6) and the `PreToolUse` call emits nothing (allow). When `mode` is
`"blocking"`, a would-deny pass denies exactly as the incumbent's cross-domain check already does
today. This mode gate wraps **both** passes identically — the cross-domain check, once wired live,
also starts under `log_only` rather than jumping straight to the blocking behavior its
already-written code implements, since it has equally never run against live traffic.

**Consequence for the LOCKED doc named explicitly (F1):** this is the mechanism by which
`docs/tooling/domain-boundary-provenance-hook.md` §6 step 6 / AC4's unconditional "deny" text is
superseded in practice — under the shipped `log_only` default, that step's condition now resolves
to `decision: "flag"`, never `"deny"`. See §3's reconciliation paragraph and §11's integration-point
entry for the LOCKED doc, and Roadmap Slice 11 for the addendum text obligation this creates.

**Initial `.claude/settings.json` wiring**: add one `PreToolUse` entry matching `Edit`/`Write`,
pointing at `.claude/hooks/domain-boundary-provenance.sh` (unchanged path), with
`docs/tooling/domain-boundary-mode.json` shipped at `{"schemaVersion": 1, "mode": "log_only"}` as
the initial committed value — satisfying `01-REQUIREMENTS.md`'s Must: "No repo's hook installation
ships in `blocking` mode as its initial configuration."

### 5.1 Re-justification of the Inherited 5s Probe Timeout (benchmark audit finding #5)

The wrapper's existing `5s` timeout budget (`.claude/hooks/domain-boundary-provenance.sh`, marked
`PROVISIONAL — owner: wright... reused as a starting value from first-turn-contract.sh's own
measured-and-cited 5s bound`) was measured for the cross-domain pass, which per the LOCKED doc
never calls `ast.parse` on the file content. This sprint adds a full `ast.parse(scan_surface, ...)`
call on every `.py` `Edit`/`Write` (§2, §7) — a materially different cost profile under the same
inherited bound, and the benchmark audit is correct that this cannot be silently inherited without
re-justification.

**Disposition: verified directly against this repo, not left as an unvalidated inheritance.**
Measured 2026-09-05, reproducible via `python3 -c "import ast, time; ..."` against this repo's own
files:
- `ast.parse()` against this repo's actual largest `.py` file (`tests/test_first_turn_contract_probe.py`,
  949 lines) took **~8ms** average over 50 runs.
- `ast.parse()` against a synthetic 10,010-line file (well beyond any single file currently in this
  repo or the roster corpus) took **~76ms** average over 20 runs.

Both figures are more than **two orders of magnitude below the 5,000ms budget** (76ms is 1.5% of
the budget even at 10x this repo's largest real file). This is a citable, reproducible measurement
against this repo (not a back-of-envelope guess and not a claim about "commodity hardware" in the
abstract) — `ast.parse`'s cost is negligible relative to the existing 5s bound for any file size
plausible in this codebase or the roster corpus. **The 5s timeout is re-justified as-is for this
sprint's addition; no re-measurement Roadmap slice is required for the `ast.parse` cost
specifically.** The timeout constant's own PROVISIONAL/owner framing in the wrapper file is a
pre-existing artifact outside this sprint's file-touch scope (see report) and is not edited here.

## 6. Data Schema Changes

```typescript
// Unchanged from the incumbent doc's §7, reused verbatim:
interface DomainBoundaryHookInput {
  tool_name: string;
  tool_input: {
    file_path: string;
    content?: string;
    old_string?: string;
    new_string?: string;
  };
  cwd?: string;
}

interface DomainBoundaryHookOutput {
  decision?: "block";
  reason?: string;
}

// Extended: TrackRecordEntry gains a `checks` breakdown and a new decision value.
interface TrackRecordEntry {
  timestamp: string;
  session_id: string | null;
  tool_name: string;
  file_path: string | null;
  mode: "log_only" | "blocking";                  // NEW — which mode produced this decision
  cross_domain: {
    manifest_status: "absent_or_invalid" | "matched";
    file_in_scope: boolean | null;
    matches_found: number | null;
    matches_cited: number | null;
  };
  local_threshold: {                               // NEW
    file_scanned: boolean;                         // false for non-.py files, test paths
    matches_found: number | null;                  // count of flagged threshold-shaped literals
    matches_cited: number | null;                  // count carrying a qualifying THRESHOLD-PROVENANCE: marker
  };
  decision: "allow" | "flag" | "deny" | "probe_error";  // "flag" is NEW — log_only would-have-denied
  reason: string | null;
  probe_error: string | null;
}
```

**Migration note**: this is a breaking schema change to `TrackRecordEntry` (nested `cross_domain`/
`local_threshold` objects replace the incumbent's flat `manifest_status`/`file_in_scope`/
`matches_found`/`matches_cited` fields). The incumbent's track-record log
(`docs/tooling/domain-boundary-provenance-track-record.jsonl`) is gitignored and has never been
populated by a live wiring (§5) — there is no historical data this migration needs to preserve or
reconcile, so the schema change is a clean cutover, not a versioned-log concern.

**Resolution of 05-REVIEW.md G-5 (`mode` nullability): `mode` stays non-nullable
(`"log_only" | "blocking"`, no `| null`). The wrapper, not just the probe, must read the mode
config.** Rationale for keeping it non-nullable rather than widening the type: `mode` is the field
every downstream reader (triage, promotion decisions, Roadmap Slice 12's end-to-end verification)
uses to interpret every other field in the entry — a `null` mode on a `probe_error` row would mean
"we don't know whether this crash happened under log_only or blocking," which is exactly the kind
of ambiguity this schema exists to prevent, and it is avoidable: the mode config
(`docs/tooling/domain-boundary-mode.json`, §5) is a small, static, already-fail-safe-specified
file that either component can read independently without needing the probe to have run
successfully first.

**Concrete requirement**: `.claude/hooks/domain-boundary-provenance.sh` (the wrapper) reads
`docs/tooling/domain-boundary-mode.json` itself, at the point it constructs any `probe_error`
`TrackRecordEntry` (i.e. whenever the wrapper detects the probe invocation failed, timed out, or
produced no parseable output) — this is a **new** wrapper responsibility this sprint adds, not a
pre-existing one. It applies the identical fail-safe default `load_mode_config` uses (§7): file
absent, unreadable, or schema-invalid → `"log_only"`; otherwise the file's `mode` value verbatim.
A minimal shell-native read (e.g. `grep`/`sed` extraction of the `"mode"` value, or `jq -r` if
available, falling back to `"log_only"` on any non-zero exit or empty result) is sufficient — the
wrapper does not need a full JSON parser, only this one field, and correctness on malformed input
means "fail toward log_only," not "fail toward crashing the wrapper itself." This closes the gap
Roadmap Slice 8 currently leaves open (wrapper "never reads the mode config file"): after this
sprint, both the probe (`load_mode_config`, §7, for all non-`probe_error` entries) and the wrapper
(this new read, for `probe_error` entries only) independently supply a real `mode` value, and
`TrackRecordEntry.mode` is never `null` in any code path.

## 7. New Function Signatures

```python
# scripts/domain_boundary_provenance_probe.py — additions, alongside all existing functions
# (load_manifest, normalize_file_path, match_globs, get_scan_surface, etc.), which are
# UNMODIFIED.

def load_mode_config(project_dir: str) -> str:
    """Reads docs/tooling/domain-boundary-mode.json. Returns "log_only" on any absence,
    read failure, or schema-invalid content (fail-safe default, §5)."""

def detect_threshold_literals(file_path: str, scan_surface: str) -> list[FlaggedLiteral]:
    """AD-1 detection (§2, redesigned this pass — two shape-based contexts only, no name-gated
    context). file_path used only to apply the test/fixture path exclusion and the .py extension
    gate — never read from disk; operates on scan_surface text only, parsed via
    ast.parse(scan_surface, ...) with a syntax-error -> return [] (fail-open: an unparsable
    partial-edit fragment is not flagged, not crashed on)."""

class FlaggedLiteral(TypedDict):
    line_index: int         # 0-based, within scan_surface
    context: str            # "comparison" | "slice_truncation" — no "named_threshold" value;
                             # the name-gated context (§2) was removed this pass
    literal_repr: str       # e.g. "50000", "True"

# No new module-level constant is introduced by this pass (§4). The proximity window for
# THRESHOLD-PROVENANCE: reuses the incumbent's existing PROXIMITY_WINDOW = 5 (probe L51,
# unchanged) rather than defining a second, independently-tuned window — see §4 for why the
# prior draft's PROXIMITY_WINDOW_THRESHOLD = 3 constant and its prescribed comment block have
# been dropped (empirically wrong per measurement, and internally self-contradictory: a
# 5-line-minimum comment block cannot satisfy a 3-line detection window).

def has_threshold_provenance_marker(lines: list[str], match_line_idx: int) -> bool:
    """5-line window (§4), same shape and same PROXIMITY_WINDOW constant (probe L51, value 5) as
    the incumbent's has_qualifying_marker_in_window, checked against THRESHOLD-PROVENANCE: instead
    of DOMAIN-BOUNDARY:. Implemented as a distinct function (different marker string) but the same
    window value, not a second constant — kept as one shared PROXIMITY_WINDOW so the two passes of
    the same hook do not require independently maintaining two window bounds."""

def run_cross_domain_pass(project_dir, tool_input, scan_surface) -> PassResult:
    """Incumbent's existing steps 2-7 (manifest load, normalize, glob match, identifier scan,
    DOMAIN-BOUNDARY: window check), extracted verbatim into a function, no logic change."""

def run_local_threshold_pass(tool_name, raw_file_path, scan_surface, mode) -> PassResult:
    """New. Gated on: raw_file_path ends with .py, and no path component is
    test/tests/fixtures (§2 exclusion). Not gated by manifest presence."""

class PassResult(TypedDict):
    ran: bool
    matches_found: int | None
    matches_cited: int | None
    unmarked: list[tuple[int, str]]   # (line_idx, description) pairs feeding combine()'s reason text
    detail: dict                      # pass-specific track-record fields (manifest_status/file_in_scope, or file_scanned)

def combine(cross_domain: PassResult, local_threshold: PassResult, mode: str) -> CombinedResult:
    """§3's combination rule. mode="log_only" downgrades any would-deny to decision="flag",
    always emits allow to the caller. mode="blocking" denies if either pass has unmarked
    matches, concatenating both passes' reasons, labeled."""
```

This resolves review items G-6/G-7/G-8/G-9, which were raised against the discarded from-scratch
design — see §8 for per-item disposition.

## 8. Disposition of 05-REVIEW.md's Five Lesser Drifts (G-6 through G-9, G-4)

| Finding | Was about | Status under this extension design |
|---|---|---|
| **G-6** (`base_ref` undefined) | The discarded design's Stop-hook trigger needed a git base ref to find "session-changed files." | **Moot.** This design keeps `PreToolUse` on `Edit`/`Write` (the incumbent's trigger) — there is no "changed files since session start" concept at all; the scan surface is the single tool call's own `content`/`new_string`, exactly as the incumbent already does. No base-ref resolution is needed anywhere in this document. |
| **G-7** (`run()` takes `mode` as param AND reads config) | Same ambiguity risk exists in principle. | **Addressed directly**, not just moot: §7 specifies `run()` calls `load_mode_config()` itself, once, at the top, then passes the resulting `mode` string into `combine()` as a plain argument — config is read exactly once, by `run()`, never re-read or re-passed ambiguously. |
| **G-8** (`ProbeResult.decision` can't express `probe_error`) | The discarded design's `ProbeResult` type omitted `probe_error`. | **Addressed.** §6's `TrackRecordEntry.decision` explicitly lists `"allow" \| "flag" \| "deny" \| "probe_error"` as one flat union, matching the incumbent's own existing pattern (its `TrackRecordEntry.decision` already includes `probe_error`) — no separate `ProbeResult` type with a narrower union is introduced by this design; `PassResult`/`CombinedResult` (§7) are per-pass/pre-decision structures, not the final logged decision. |
| **G-9 / G-4** (self-scan) | Whether the new probe's own PROVISIONAL constants get scanned by its own detection rule once live. | **Simplified and resolved this revision, superseding the prior draft's two-case analysis.** The prior draft's self-scan concern existed only because of the now-removed name-gated context (§2): a constant literally named `PROXIMITY_WINDOW_THRESHOLD` would have matched on its own name. That context is gone. Under the redesigned rule (§2: comparison operand or slice/truncation argument only), **no module-level constant assignment is ever flagged purely by name** — `PROXIMITY_WINDOW = 5` (incumbent, unchanged) is not a comparison operand or slice bound, so it was never in scope for the local-threshold pass under either the old or new design, and no new window constant is introduced by this pass (§4/§7) for the same question to apply to. The self-scan question therefore has one answer instead of two: **the local-threshold pass does not flag either window constant**, and no comment-text obligation is created for `PROXIMITY_WINDOW` beyond what the incumbent already carries. Roadmap Slice 9's fixture corpus should still include one case verifying this directly (an assignment like `PROXIMITY_WINDOW = 5` in a scanned file resolves to "not flagged," not "flagged and cited") so the absence of a self-scan false-positive is a tested claim, not an inferred one. |
| **G-4** (US-4 AC2 no verification path) | "No log message implies soundness" has no test. | **Still applies, unchanged from before** — this is a requirements-level testability gap independent of which design implements it. Not this document's to resolve; flagged to Roadmap the same way the review already did (a grep-based test asserting the deny/flag `reason` string template contains no soundness-implying language, e.g. no "verified correct"/"sound"/"validated" claims beyond presence-check wording). |

## 9. Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python 3 stdlib `ast` | matches existing interpreter (no new requirement) | `detect_threshold_literals` (§2) — parses `scan_surface` to find comparison/slice nodes. New import for this probe file, but stdlib, zero new third-party dependency. Cost re-justified directly against this repo, §5.1. |
| Python 3 stdlib (`json`, `re`, `os`, `sys`, `fnmatch`, `datetime`) | unchanged | Reused from the incumbent, no change. |

No new third-party dependency. Consistent with the incumbent's own zero-third-party posture
(its §10).

## 10. Patterns (delta from incumbent's §11)

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| Two independent detection passes, one combined decision | `run()` (§3) | Composes cleanly without duplicating the wrapper/probe/hook-registration machinery for a second hook entry; keeps one `PreToolUse` call, one track-record entry, one deny-schema emission per Claude Code's own one-decision-per-call constraint. |
| Fail-safe config default (absent mode file → `log_only`, never `blocking`) | `load_mode_config` (§5) | Mirrors the incumbent's "absent manifest → allow" fail-safe posture — an unconfigured or partially-installed hook must always default toward the less disruptive behavior, never the more disruptive one. |
| AST-based syntactic detection over regex | `detect_threshold_literals` (§2) | Reliably distinguishes "literal is a comparison operand" from "literal merely appears near a comparison token" — same rationale the discarded design already established for this specific sub-decision, unaffected by the trigger-surface correction. |
| Shape-only detection, no name-vocabulary gate | `detect_threshold_literals` (§2) | Benchmark-measured: an English-word name gate produces both false negatives (8/10 words never fire in this repo) and false positives (substring matches inside unrelated identifiers). Removing it and relying on `log_only` + citation convention to absorb volume avoids maintaining an unvalidated word list at all. |

**Anti-patterns (do not use), unchanged from incumbent plus two additions:**
- General static import/reference analysis for either check — rejected (incumbent §4, unaffected).
- Reusing `DOMAIN-BOUNDARY:` or bare `PROVISIONAL` as the new check's marker — rejected, §4.
- A second, independent hook registration/process for the local-threshold check — rejected,
  §3 (violates task instruction 3's explicit "same wrapper... not duplicated").
- **New**: a name/vocabulary-gated detection context for local thresholds — rejected, §2 (measured
  false-negative and false-positive rate too high in this repo to justify the added detection
  surface; shape-based contexts alone are simpler and better-measured).

## 11. Integration Points

- **`.claude/settings.json`**: gains one new `PreToolUse` entry (currently absent, §5) — no entry
  is modified or removed, since none currently exists for this hook family.
- **`docs/tooling/domain-boundary-provenance-hook.md`**: this LOCKED doc's §2–§10 remain the
  authoritative spec for the cross-domain pass; it is not rewritten by this sprint. A short
  addendum section should be appended (Roadmap Slice 11's concern, not this document's) pointing
  at this architecture doc for the composed local-threshold behavior, and explicitly stating the
  mode-gated deny semantics (§3/§5 above): under `log_only`, the condition §6 step 6/AC4 call
  "denied" instead resolves to `decision: "flag"` and the call is allowed — a real behavior change
  to this LOCKED doc's stated outcome, named here rather than left implicit. This is what §5's
  pointer to this bullet resolves to.

  **Separately (not this sprint's file-touch scope, reported for Danny's routing):** this LOCKED
  doc's own §5/§6 and AC4 currently institutionalize the exact "PROVISIONAL — owner: X" bare-tag
  pattern that this revision removes from every doc it touches. That LOCKED doc and the live probe
  script (`scripts/domain_boundary_provenance_probe.py`, `.claude/hooks/domain-boundary-provenance.sh`)
  are out of this sprint's file-touch scope and are not edited here — see the accompanying report
  for the exact instances and a recommended separate correction pass.
- **`docs/tooling/domain-boundary-manifest.json`** (F2 correction, Frank spec-gate attempt 1):
  **this file does not exist and has never been tracked in this repo** — confirmed by direct
  check. No repo-root manifest exists in agent-rig; this is deliberate, not an oversight — the
  cross-domain pass's own step 2 "absent → allow" rule means it currently always short-circuits to
  allow here (the incumbent's own gate log records this). The real fixture used by the incumbent's
  tests is `tests/fixtures/domain_boundary_manifest_fixture.json`, written into a tmp dir by the
  test harness, not read from the repo root. This document's prior draft incorrectly listed
  `domain-boundary-manifest.json` as an existing, untouched integration point; that row is deleted
  and replaced by this corrected one. **Roadmap Slice 12's self-scan verification still correctly
  yields its required `"flag"` result via the new local-threshold pass alone** — that pass has no
  manifest dependency at all (§3 "No manifest coupling"), so the absence of a repo-root manifest
  does not affect whether Slice 12's self-scan produces the expected `"flag"` outcome.
- **`docs/tooling/domain-boundary-mode.json`** (new, §5): read by both passes via one `run()`-level
  call.
- **`HOOK-DEPLOYMENT-ROSTER.md`**: needs a status update (Roadmap concern) — the roster's existing
  `domain-boundary-provenance` (DDR-006) row currently reflects "built, unwired"; after this
  sprint it becomes "built, wired, `log_only`."

## 12. Corrections to `01-REQUIREMENTS.md`/`NORTH-STAR.md` (F3, Frank spec-gate attempt 1: Applied)

1. **US-1 AC1** ("to be finalized at architecture time", G-5) — **Applied.** `01-REQUIREMENTS.md` now points at Architecture §2 as the finalized detection rule.
2. **US-3 / Constraints** (wrapper-reuse framing) — **Applied.** Requirements now clarifies this
   is a two-generations-removed reuse via the incumbent's wrapper, not a direct copy of
   `first-turn-contract.sh`.
3. **Title/identity mismatch** (Stop-hook vs. `PreToolUse`) — **Applied.** Requirements now
   correctly describes a `PreToolUse` hook, inherited from the incumbent. Confirmed by direct
   check: `grep -n "Stop-hook" 01-REQUIREMENTS.md NORTH-STAR.md` returns no matches.
4. **Out of Scope** (incumbent's disposition unstated, G-1) — **Applied.** Out of Scope now
   states explicitly that the incumbent hook and its LOCKED spec are extended, not replaced or
   retired, and no new/second hook is created.
5. **NORTH-STAR.md** Success Criteria (same Stop-vs-`PreToolUse` mismatch as item 3) —
   **Applied**, with Danny's personal sign-off obtained per this repo's Decision Discipline for
   North Star doc edits. Confirmed by the same `grep -n "Stop-hook"` check above: no remaining
   references.
6. **`01-REQUIREMENTS.md` L110** (benchmark audit, this revision) — the bare `PROVISIONAL (owner:
   wright, unmeasured)` tag on the exclusion-set/name-list disclosure is **Applied/corrected**:
   replaced with the disposition-based language matching this document's §2 (not-yet-benchmarked,
   executable plan cited, and the name-word list itself removed per the §2 redesign rather than
   re-tagged).

## 13. Open Items Carried to Forge

- **§2's `{0, 1, -1, 2}` exclusion set** — NOT YET BENCHMARKED. Carries the full executable
  validation plan stated in §2 (unfiltered scan of the roster corpus, JSONL dump, 200-row
  stratified hand-labeled sample, 5%-precision exclusion threshold). Not to be treated as
  validated until that plan runs; running it is Roadmap/forge follow-up, not resolved here.
- **§2's name-gated context** — REMOVED, not carried forward. The redesign (drop context 2,
  flag on shape alone) is adopted in this document; there is no name-word list left to
  benchmark or re-tag.
- **§4's proximity window** — RESOLVED, not carried forward as open. Reuses the incumbent's
  existing, already-5-line `PROXIMITY_WINDOW` constant; no second window constant, no separate
  PROVISIONAL tag needed for this value going forward.
- **§5.1's 5s timeout** — RESOLVED for this sprint's `ast.parse` addition specifically (measured
  directly against this repo, see §5.1); the timeout constant's pre-existing PROVISIONAL/owner
  framing in the wrapper file itself is unchanged and out of this sprint's file-touch scope.
- **§8's self-scan disposition** — RESOLVED, simplified from the prior draft's two-case analysis
  to one outcome: no window constant is flagged by the local-threshold pass under the redesigned
  shape-only rule. Roadmap Slice 9 should still add one explicit fixture case asserting this
  ("not flagged") so it is a tested claim.
- **§11's roster/LOCKED-doc addendum updates** — Roadmap-level housekeeping, not architecture.
- **LOCKED doc / live probe self-assigned-owner pattern** — out of this sprint's file-touch scope;
  reported to Danny for separate routing (see accompanying report and §11's integration-point
  note).

---

*This document does not self-lock. Per this repo's workflow, it proceeds to Frank's binding
spec-gate and human approval before any status change from DRAFT — including explicit review of
this revision's resolution of OQ-A/OQ-B against the human decision already given (extend, not
replace).*
