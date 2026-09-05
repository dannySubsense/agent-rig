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

## 2. Detection Rule for the New Check (AD-1, resolved for the local-literal case)

**Decision: fixed set of syntactic contexts, Python-only, name-gated on one context** — this is
the same rule shape the prior (discarded) architecture pass selected for AD-1, and nothing in
G-1's finding invalidates the *rule itself* — only the trigger surface, scan-surface framing, and
citation marker it was wired to. Re-adopted here unchanged in substance, re-hosted on the correct
trigger/surface/marker.

**Contexts that count as "threshold-shaped":**
1. **Comparison operand**: a numeric literal appearing as either operand of a comparison
   (`<`, `<=`, `>`, `>=`, `==`, `!=`) — e.g. `if retries > 3:`.
2. **Default-kwarg / assignment whose target name matches a threshold-word pattern**: a numeric
   or boolean literal assigned to a name, or passed as a default parameter value, where the
   target/parameter name (case-insensitive substring match) contains one of: `limit`, `cap`,
   `threshold`, `cutoff`, `retry`, `retries`, `budget`, `timeout`, `max`, `min`. This is the only
   context gated on a name match — contexts 1 and 3 fire on syntactic shape alone, independent of
   naming.
3. **Slice/truncation argument**: a numeric literal used as a slice bound (`x[:50000]`) or as an
   argument to a truncation-shaped call (`str[:N]`, `.ljust(N)`, `[:N]` generally).

**Explicit exclusions** (never flagged, regardless of context match):
- `range()` call bounds (first, second, or third positional argument).
- A non-slice-stop index into a sequence (`x[i]`, not `x[:i]`).
- Files under any `test`/`tests`/`fixtures` path component.
- The literal values `{0, 1, -1, 2}` — idiomatic loop/sentinel/increment values.

**PROVISIONAL — owner: wright.** The `{0, 1, -1, 2}` exclusion set and the context-2 name-word
list are not derived from an external benchmark; they are a first-pass value for this sprint,
same status the prior architecture pass gave them (`05-REVIEW.md` confirmed this compliant under
the prior framing and nothing about re-hosting the rule changes that disposition).

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

## 4. Citation Marker for the New Check

**Decision: new marker, `THRESHOLD-PROVENANCE:`. Does not reuse `DOMAIN-BOUNDARY:` or bare
`PROVISIONAL`.**

**Rationale, following the incumbent's own §5 reasoning pattern (not re-litigating it, applying
it to a third case):**
- **Not `PROVISIONAL` alone** — same objection the incumbent's §5 already establishes: a bare
  `PROVISIONAL — owner: X` tag asserts "not yet validated," which is one of the amendment's three
  satisfying conditions (option b) but not the only one. A citation to a reproducible source
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
  line**: a citation (option a), an explicit named-owner PROVISIONAL tag (option b) — the
  existing `PROVISIONAL — owner: X` string is still what appears, just now recognized by this
  marker rather than required to double as the marker itself — or is simply absent because the
  literal was removed (option c, which trivially satisfies the check by there being no literal
  left to flag). Concretely: `# THRESHOLD-PROVENANCE: PROVISIONAL — owner: wright, unmeasured` is
  a valid, complete citation line satisfying option (b); `# THRESHOLD-PROVENANCE: see DDR-0014
  §Amendment for why 5s is reused from first-turn-contract.sh's measured bound` satisfies (a).

**v1 citation rule for the new check** (deliberately mirrors the incumbent's §5 shape for
consistency, values re-justified independently, not copied):
- A citation is a comment line containing the literal marker `THRESHOLD-PROVENANCE:`
  (case-sensitive, exact string) followed by non-whitespace content on the same line.
- The marker must appear within **3 lines** (inclusive) above or below the line containing the
  flagged literal, counted within the same scan surface (`tool_input.content`/`new_string`) — not
  the incumbent's 5-line window. The window bound is held in a new constant,
  `PROXIMITY_WINDOW_THRESHOLD = 3` (§7), named distinctly from the incumbent's own
  `PROXIMITY_WINDOW = 5` (probe L51) so the two module-level constants do not collide (§7's
  addition rationale). **PROVISIONAL — owner: wright.** A tighter window than the incumbent's is
  deliberate, not arbitrary-different-for-its-own-sake: threshold literals are typically
  single-line assignments or comparisons with no natural multi-line block the way a cross-domain
  read's surrounding context often has, so a tighter default is being tried first; like the
  incumbent's window, this is unmeasured and owned by wright for revision once real
  false-positive/negative data exists (Roadmap Slice 10, unchanged from prior pass's plan).
  **Self-scan consequence of this name (resolved, see §8 G-4 disposition):** because
  `PROXIMITY_WINDOW_THRESHOLD` contains the name-gate word `threshold`, the constant's own
  assignment line is itself a "named threshold" match under §2 context 2 once the local-threshold
  pass goes live and scans this probe file. It must therefore carry a real
  `THRESHOLD-PROVENANCE:` marker line (not a bare `PROVISIONAL` comment) within 3 lines of its
  assignment. The required comment text is specified exactly in §7.
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

**Initial `.claude/settings.json` wiring**: add one `PreToolUse` entry matching `Edit`/`Write`,
pointing at `.claude/hooks/domain-boundary-provenance.sh` (unchanged path), with
`docs/tooling/domain-boundary-mode.json` shipped at `{"schemaVersion": 1, "mode": "log_only"}` as
the initial committed value — satisfying `01-REQUIREMENTS.md`'s Must: "No repo's hook installation
ships in `blocking` mode as its initial configuration."

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
    """AD-1 detection (§2). file_path used only to apply the test/fixture path exclusion and
    the .py extension gate — never read from disk; operates on scan_surface text only, parsed
    via ast.parse(scan_surface, ...) with a syntax-error -> return [] (fail-open: an
    unparsable partial-edit fragment is not flagged, not crashed on)."""

class FlaggedLiteral(TypedDict):
    line_index: int         # 0-based, within scan_surface
    context: str            # "comparison" | "named_threshold" | "slice_truncation"
    literal_repr: str       # e.g. "50000", "True"

# THRESHOLD-PROVENANCE: PROVISIONAL — owner: wright, unmeasured. Proximity window (lines)
# above/below a match, for the local-threshold pass only (§2/§4). Independent of the incumbent's
# PROXIMITY_WINDOW (probe L51, value 5, cross-domain purpose) — named PROXIMITY_WINDOW_THRESHOLD,
# not PROXIMITY_WINDOW, to avoid a module-level name collision (two constants of the same name in
# the same file is a Python bug: the second assignment would silently shadow the first).
PROXIMITY_WINDOW_THRESHOLD = 3
# ^ This comment is deliberately written as the exact text to land in
#   scripts/domain_boundary_provenance_probe.py (Roadmap Slice 4). It is required to start with
#   the literal marker `THRESHOLD-PROVENANCE:` (not a bare `PROVISIONAL —` line) because the
#   constant's own name contains the name-gate word "threshold" (§2 context 2) — once the local-
#   threshold pass is live, an edit to this file that assigns `PROXIMITY_WINDOW_THRESHOLD` is
#   itself a context-2 match, and the required qualifying marker for that check's own detection
#   rule (§4) is `THRESHOLD-PROVENANCE:`, not `PROVISIONAL —` (that string alone does not contain
#   the marker and would not satisfy `has_threshold_provenance_marker`, causing the probe to flag
#   its own source line). See §8 G-4 for the full self-scan resolution and why the incumbent's
#   `PROXIMITY_WINDOW = 5` (probe L51) does NOT need the same treatment.

def has_threshold_provenance_marker(lines: list[str], match_line_idx: int) -> bool:
    """3-line window (§4), same shape as the incumbent's has_qualifying_marker_in_window but
    against THRESHOLD-PROVENANCE: and PROXIMITY_WINDOW_THRESHOLD (=3, above), kept as a separate
    function/constant rather than parameterizing the incumbent's (`PROXIMITY_WINDOW`, probe
    L51) — the two windows are independently PROVISIONAL and must be revisable independently
    without an accidental shared-constant coupling. Verified by direct read of the live file
    (2026-09-05) that `PROXIMITY_WINDOW_THRESHOLD` does not collide with any other existing name
    in `scripts/domain_boundary_provenance_probe.py`."""

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
| **G-9 / G-4** (self-scan, and 05-REVIEW.md's G-3/G-4 rename consequence) | Whether the new probe's own PROVISIONAL constants get scanned by its own detection rule once live, and — per 05-REVIEW.md G-4 — whether renaming the new constant away from `PROXIMITY_WINDOW` to satisfy G-3 (name-collision fix) silently flips this row's original "false negative" conclusion into a false positive on the *new* constant. | **Resolved with two distinct, definite answers — one per constant, since after the G-3 rename they are no longer analogous cases:** (1) **The incumbent's `PROXIMITY_WINDOW = 5` (probe L51, unchanged by this sprint)** — its name contains no name-gate word (`limit`/`cap`/`threshold`/`cutoff`/`retry`/`retries`/`budget`/`timeout`/`max`/`min`), so §2 context 2 does NOT match it. This is an accepted v1 detection gap (a threshold by role, not by name) exactly as originally found — **unaffected by the rename**, because this constant was never renamed. Its existing `# §5 — PROVISIONAL, owner: wright` comment (probe L50) needs no change and does not need to contain `THRESHOLD-PROVENANCE:`, because context 2 never fires on it in the first place. (2) **The new constant, renamed to `PROXIMITY_WINDOW_THRESHOLD = 3` per G-3 (§7)** — its name DOES contain `threshold`, so §2 context 2 fires on its own assignment line once the local-threshold pass scans this probe file (self-scan, per G-9's original question). This is the opposite situation from case (1) and requires an actual qualifying marker, not just an accepted gap: the comment immediately above the assignment (§7) is written to start with the literal string `THRESHOLD-PROVENANCE:` (not a bare `PROVISIONAL —` line) specifically so it satisfies `has_threshold_provenance_marker`'s check within the 3-line window (§4). A bare `# PROVISIONAL — owner: wright` comment, as this document's prior draft used, does NOT contain the required marker string and would NOT have satisfied the check — that was this document's own error, corrected in §7's exact comment text. Roadmap Slice 4's Done-When must require the comment be written verbatim as specified in §7, and Slice 9's fixture corpus must add a case for `PROXIMITY_WINDOW_THRESHOLD`'s own assignment resolving to "cited" (not "flagged"), distinct from the existing `PROXIMITY_WINDOW` false-negative fixture case (which remains, unchanged, for case (1)). |
| **G-4** (US-4 AC2 no verification path) | "No log message implies soundness" has no test. | **Still applies, unchanged from before** — this is a requirements-level testability gap independent of which design implements it. Not this document's to resolve; flagged to Roadmap the same way the review already did (a grep-based test asserting the deny/flag `reason` string template contains no soundness-implying language, e.g. no "verified correct"/"sound"/"validated" claims beyond presence-check wording). |

## 9. Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib `ast` | matches existing interpreter (no new requirement) | `detect_threshold_literals` (§2) — parses `scan_surface` to find comparison/assignment/slice nodes. New import for this probe file, but stdlib, zero new third-party dependency. |
| Python 3 stdlib (`json`, `re`, `os`, `sys`, `fnmatch`, `datetime`) | unchanged | Reused from the incumbent, no change. |

No new third-party dependency. Consistent with the incumbent's own zero-third-party posture
(its §10).

## 10. Patterns (delta from incumbent's §11)

| Pattern | Usage | Rationale |
|---|---|---|
| Two independent detection passes, one combined decision | `run()` (§3) | Composes cleanly without duplicating the wrapper/probe/hook-registration machinery for a second hook entry; keeps one `PreToolUse` call, one track-record entry, one deny-schema emission per Claude Code's own one-decision-per-call constraint. |
| Fail-safe config default (absent mode file → `log_only`, never `blocking`) | `load_mode_config` (§5) | Mirrors the incumbent's "absent manifest → allow" fail-safe posture — an unconfigured or partially-installed hook must always default toward the less disruptive behavior, never the more disruptive one. |
| AST-based syntactic detection over regex | `detect_threshold_literals` (§2) | Reliably distinguishes "literal is a comparison operand" from "literal merely appears near a comparison token" — same rationale the discarded design already established for this specific sub-decision, unaffected by the trigger-surface correction. |

**Anti-patterns (do not use), unchanged from incumbent plus one addition:**
- General static import/reference analysis for either check — rejected (incumbent §4, unaffected).
- Reusing `DOMAIN-BOUNDARY:` or bare `PROVISIONAL` as the new check's marker — rejected, §4.
- **New**: a second, independent hook registration/process for the local-threshold check — rejected,
  §3 (violates task instruction 3's explicit "same wrapper... not duplicated").

## 11. Integration Points

- **`.claude/settings.json`**: gains one new `PreToolUse` entry (currently absent, §5) — no entry
  is modified or removed, since none currently exists for this hook family.
- **`docs/tooling/domain-boundary-provenance-hook.md`**: this LOCKED doc's §2–§10 remain the
  authoritative spec for the cross-domain pass; it is not rewritten by this sprint. A short
  addendum section should be appended (Roadmap concern, not this document's) pointing at this
  architecture doc for the composed local-threshold behavior, so a future reader of the LOCKED doc
  isn't misled into thinking the hook is still single-purpose.
- **`docs/tooling/domain-boundary-manifest.json`** (self-test fixture manifest, incumbent's own):
  untouched — still governs only the cross-domain pass.
- **`docs/tooling/domain-boundary-mode.json`** (new, §5): read by both passes via one `run()`-level
  call.
- **`HOOK-DEPLOYMENT-ROSTER.md`**: needs a status update (Roadmap concern) — the roster's existing
  `domain-boundary-provenance` (DDR-006) row currently reflects "built, unwired"; after this
  sprint it becomes "built, wired, `log_only`."

## 12. Contradictions Flagged to `01-REQUIREMENTS.md` (not silently patched here, per task instruction)

1. **US-1 AC1** still says the detection rule is "to be finalized at architecture time" (G-5,
   already flagged by review) — now finalized by §2 of this document; the requirements doc needs
   a pointer, not a rewrite.
2. **US-3 / Constraints** say "reuse `first-turn-contract-enforcement`'s wrapper shape" — true in
   spirit, but the actual reused shape is now the **incumbent domain-boundary hook's** wrapper
   (which is itself already a reuse of `first-turn-contract.sh`'s shape, per that hook's own §11).
   Requirements should clarify this is a two-generations-removed reuse, not a direct one, so a
   forge reader doesn't go looking for a fresh copy of `first-turn-contract.sh`'s literal code.
3. **Title/identity mismatch**: `01-REQUIREMENTS.md`'s Summary describes "A Stop-hook, sibling in
   shape to `first-turn-contract-enforcement`" — this document's design is a `PreToolUse` hook
   (inherited from the incumbent, not a `Stop` hook). This is a direct contradiction, not a
   phrasing nuance: trigger surface changed from `Stop` to `PreToolUse` as a consequence of
   extending the incumbent rather than building fresh. Requirements needs this corrected, not
   just annotated.
4. **Out of Scope** doesn't mention the incumbent's disposition at all (this was G-1's core
   complaint) — needs an explicit line: "the incumbent `domain-boundary-provenance` hook and its
   LOCKED spec doc are extended, not replaced or retired; no new/second hook is created."
5. **NORTH-STAR.md**'s Success Criteria bullet "A working Stop-hook wrapper... reusing that
   infrastructure" has the same Stop-vs-PreToolUse mismatch as item 3 above; per this repo's
   Decision Discipline, Danny personally reviews North Star doc edits before any change to this
   file is treated as locked — flagged for that review, not edited here.

## 13. Open Items Carried to Forge

- **§2's exclusion set and name-word list** — PROVISIONAL, owner wright, unmeasured (unchanged
  disposition from the prior pass, re-hosted here).
- **§4's 3-line window** — PROVISIONAL, owner wright, unmeasured, deliberately independent from
  the incumbent's 5-line window.
- **§8's self-scan disposition (two constants, two outcomes)** — the incumbent's
  `PROXIMITY_WINDOW = 5` remains an accepted, explicitly documented v1 detection gap (threshold by
  role, not by name; unaffected by this sprint). The new `PROXIMITY_WINDOW_THRESHOLD = 3` (§7) is
  a name-gate match and must carry the exact `THRESHOLD-PROVENANCE:`-prefixed comment specified in
  §7 to avoid self-flagging. Both must be captured as distinct named fixture cases in the
  roadmap's test corpus (Slice 9), not silently absent from it.
- **§11's roster/LOCKED-doc addendum updates** — Roadmap-level housekeeping, not architecture.

---

*This document does not self-lock. Per this repo's workflow, it proceeds to Frank's binding
spec-gate and human approval before any status change from DRAFT — including explicit review of
this revision's resolution of OQ-A/OQ-B against the human decision already given (extend, not
replace).*
