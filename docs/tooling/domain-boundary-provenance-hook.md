# Domain-Boundary Provenance Hook — Tooling Spec (spec-lite)

**Status**: LOCKED (2026-08-22, Danny — approved via `/forge-start` invocation; Frank spec-gate PASS attempt 3/3 + supplementary PASS on the deny-schema live-verification revision, both logged in `domain-boundary-provenance-hook-GATE-LOG.md`)
**Mode**: spec-lite (per `docs/specs/domain-boundary-provenance-hook/INTAKE.md` — no Requirements/
UI/Roadmap layering; this single document carries purpose, contract, and acceptance criteria)
**Author**: wright
**Date**: 2026-08-22

**Spec of record**: `gap-lens-dilution-filter` DDR-0014 (`docs/DDR/DDR-0014-DOMAIN-BOUNDARY-
PROVENANCE-CHECK.md`, commit `eca45d2`, Accepted). This document does not restate DDR-0014's
incidents or rationale — read it directly. **Implementation-side DDR**: `docs/specs/agent-rig-ddrs/
DDR-006-domain-boundary-provenance-hook.md`. **Intake**: `docs/specs/domain-boundary-provenance-
hook/INTAKE.md` (APPROVED 2026-08-22).

---

## 1. Purpose

Mechanize DDR-0014's check: for any numeric constant, cap, threshold, or boolean flag a pipeline
reads from **outside its own config/spec**, require a citation at the consuming site for why that
value is correct for that use. Absence of a citation is a flagged finding, surfaced without
depending on anyone remembering to run `benchmark` or ask the question by hand.

## 2. Non-Goals

- **Not a soundness judge.** This hook verifies a citation *exists* at the point of use. It does
  not evaluate whether the citation is correct, current, or well-reasoned — that stays
  `benchmark`'s job, Frank's job, and a human's, per DDR-0014 §"What it is not" and this Intake's
  own Constraint.
- **Not a retrofit of `gap-lens-dilution-filter`.** Per Intake Open Question 4: this sprint builds
  and ships the mechanism in agent-rig only. It does not wire the hook into
  `gap-lens-dilution-filter`'s `.claude/settings.json`, write that repo's manifest (§4), or touch
  any file there. Retrofit is a separate, later sprint, sequenced per this repo's existing
  retrofit-roster pattern (`signpost-pillar-propagation`'s target list) — DDR-006 §2 already flags
  this as future work, not this sprint's.
- **Not static import/reference analysis.** See §4 for why this design rejects general-purpose
  static analysis in favor of an explicit manifest.
- **Not a replacement for `first-turn-contract-enforcement`'s infrastructure.** This hook is a
  sibling wrapper reusing that pattern's shape (bounded timeout, fail-open, append-only
  track-record log) — it does not redesign the wrapper contract.

## 3. Trigger Surface (resolves Intake Open Question 3)

**Decision: PreToolUse, matched on `Edit` and `Write` against a target repo's declared pipeline
config/data file globs (§4).**

**Rejected alternatives:**
- **Pre-commit-style check** — runs too late relative to the editing agent's own turn; by commit
  time the value has already been "produced" as a completed piece of work, and a block at that
  point is a much larger disruption (undoing a commit) than blocking the edit before it lands.
  `first-turn-contract-enforcement` and `session-queue.sh` both establish this repo's preference
  for tool/turn-boundary hooks over commit-boundary hooks.
- **Scheduled/on-demand scan** — closes the gap DDR-0014 names ("neither incident's own remediation
  depended on this check existing... both were caught by audit/measurement after the fact") no
  better than the status quo `benchmark` agent already does on request. A scan that isn't run is
  exactly the failure mode this hook exists to end.
- **PreToolUse, unscoped (every Edit/Write in every repo)** — rejected as a blocking check: most
  edits in most repos touch no domain-boundary-relevant file. Unscoped blocking risk (false
  positives on unrelated files, e.g. this very document) outweighs any coverage gain; the manifold
  glob scope in §4 is required to keep this both correct and low-noise.

**Why PreToolUse specifically (not PostToolUse):** PreToolUse can prevent the write from landing at
all (deny), giving the editing agent the chance to add the citation in the same turn before the
file changes. PostToolUse could only flag after the fact, which forces a follow-up edit — strictly
worse ergonomics for the same detection power, since the hook inspects `tool_input`, not the
resulting file (§4).

**Deny-shape verification (confirmed, resolved at spec time):** the exact PreToolUse hook JSON
output schema Claude Code expects for a deny decision has been live-verified against the real
harness, in this session, 2026-08-22 — not deferred to forge. Method: a throwaway PreToolUse hook
was installed in `.claude/settings.json` (matcher: `Write`), teed real stdin to a file, emitted a
candidate deny response, and was fired via a real `Write` tool call targeting a marker filename.
**Confirmed shape: top-level `{"decision": "block", "reason": "<text>"}`** — the same shape
`first-turn-contract.sh` already uses for `Stop` — IS honored for `PreToolUse` too. The real
`Write` tool call was actually blocked, and the harness surfaced the exact reason string the
throwaway hook emitted (`THROWAWAY_TEST_DENY_SHAPE_A`) directly to the calling session. This is
the only deny-response schema this document specifies; there is no remaining candidate shape or
hedge on this point, and no forge-time re-verification is required for it. (The throwaway hook,
its settings.json entry, and the capture file were removed immediately after the test —
`git status --porcelain` on `.claude/settings.json` and `.claude/hooks/` confirmed clean, no trace
left.) The same capture also confirmed the real `PreToolUse` stdin envelope for a `Write` call;
see §7's `DomainBoundaryHookInput` for the field list and the specific confirmation this gives
§6 step 3's path-normalization assumption. Not yet verified, and explicitly still open: whether
this shape (or fail-open behavior on a malformed `decision` value) transfers to other tool types
(`Edit`) or other PreToolUse matchers — this session's capture covered `Write` only, and this
document does not assume the result generalizes without a further check.

## 4. Detection Rule (resolves Intake Open Question 1)

**Decision: explicit per-repo manifest, not static import/reference analysis.**

DDR-0014 names two example detection shapes (a DB column owned by a different domain; an imported
module's constant) but does not commit to a general detection mechanism. Intake OQ-1 named two
candidate approaches: static analysis vs. an explicit manifest. This architecture selects the
manifest.

**Rationale:**
- **Matches the reference pattern's shape.** `prompt-router-starter`'s `gate.py` is an allowlist +
  explicit non-blocking fallback for anything outside it — not a general static analyzer inferring
  what should be checked. A manifest is the same shape: an explicit, human-authored list of what
  counts as a domain-boundary read for *this* pipeline, with everything else falling through
  unchecked (never silently escalated to a block the manifest author didn't anticipate).
- **Matches the in-repo "one source, not many" precedent.** `universe_membership.py`'s guard
  (cited by DDR-0014 directly) works because membership has exactly one legitimate implementation
  site, declared once. A manifest is the same discipline applied to domain-boundary crossings:
  each pipeline explicitly declares its own boundary-crossing identifiers once, rather than the
  hook inferring them from import graphs that drift as code changes.
- **Static analysis is a materially larger, riskier build for this sprint.** General cross-language
  import/reference analysis (Python imports, SQL/ORM column references, config-file key lookups)
  would need per-language parsers and would produce a permanent stream of false positives/negatives
  as heuristics fail to match real code shapes. A manifest is deterministic, reviewable in a PR
  diff, and matches this hook's stated scope (presence/absence, not judgment).
- **Consistent with "expedited, not corner-cut."** A manifest-driven check is buildable and
  correct in this sprint; a general static analyzer would either miss the sprint's scope or ship
  with an accuracy gap this document cannot honestly acceptance-test.

**Manifest schema** (per target repo, at `<repo>/docs/tooling/domain-boundary-manifest.json`,
discovered relative to `$CLAUDE_PROJECT_DIR`):

```typescript
interface DomainBoundaryManifest {
  /** Schema version. v1 only value: 1. */
  schemaVersion: 1;
  /**
   * Glob patterns (relative to repo root, POSIX-style, matched with Python's
   * stdlib `fnmatch.fnmatch()` — the only matcher this hook uses, chosen over
   * `pathlib.Path.match()`/`Path.full_match()` for consistency with the
   * sibling probe's zero-new-dependency stdlib posture (§10). Semantics are
   * fnmatch's, explicitly: `*` matches any characters INCLUDING path
   * separators (a pattern like `docs/*.json` matches `docs/a/b.json`, unlike
   * pathlib), and `**` has no special recursive meaning in fnmatch — it
   * behaves identically to `*` (still crosses separators, not a distinct
   * "any depth" token). Manifest authors write globs against this semantic,
   * not pathlib's or shell glob's. Entries identify files this pipeline
   * treats as its own config/spec surface — the files this hook inspects
   * on Edit/Write. A file not matching any entry is never inspected
   * (silent pass, §5). Globs are matched against `tool_input.file_path`
   * only AFTER it has been normalized to this repo-root-relative,
   * POSIX-style form — the normalization procedure (including the
   * fail-open edge case where the file path is not under the repo root
   * at all) is specified in full in §6 step 3, not here; this comment
   * states the glob semantic only, not how the relative path is obtained.
   */
  pipelineConfigGlobs: string[];
  /**
   * Explicit list of identifiers that, if found in an inspected file's
   * proposed content, count as a domain-boundary read requiring citation.
   * Each entry is a literal substring or a `re:`-prefixed Python regex
   * (case-sensitive). No wildcard/glob semantics here — deliberately more
   * restrictive than pipelineConfigGlobs, since a false-positive match here
   * produces a block, not a silent skip.
   */
  externalSourceIdentifiers: string[];
}
```

A manifest is authored once per target repo by that repo's owner, at retrofit time — not part of
this sprint's deliverable content (§2). This sprint ships the schema, the hook that consumes it,
and a **self-test manifest + fixture corpus inside agent-rig** (analogous to
`first_turn_contract_corpus.json`) to exercise the detection and citation logic without depending
on any other repo's real manifest existing.

**No manifest present for the target repo:** the hook treats this as "nothing to check" and allows
silently (same posture as `first_turn_contract_probe.py`'s "not queue-injected" branch) — a repo
that has not yet opted in via a manifest is never blocked by this hook.

## 5. Citation Convention (resolves Intake Open Question 2)

**Decision: reuse of the existing PROVISIONAL-tag convention is confirmed insufficient on its own,
and this hook defines a new, narrower marker: `DOMAIN-BOUNDARY:`.**

**Why PROVISIONAL alone does not transfer:** per CLAUDE.md's Decision Discipline, a PROVISIONAL tag
asserts "this value is unvalidated, here is its named owner" — an admission of *not yet knowing* if
a number is right. DDR-0014's check needs the opposite semantic: an assertion that the value *has
been examined* at the consuming site and *is* correct for this use, with the reasoning stated (per
CLAUDE.md rule 1: "where did this come from, and is it still doing the job it was hired for?"). A
bare `PROVISIONAL — owner: X` tag next to a cross-domain read would pass a naive presence check
while asserting the opposite of what DDR-0014 requires. Reusing the same marker string for two
different semantic claims would blur exactly the distinction DDR-0014 exists to enforce.

**v1 citation rule:**
- A citation is a comment line containing the literal marker `DOMAIN-BOUNDARY:` (case-sensitive,
  exact string) followed by non-whitespace content on the same line (the rationale text itself, a
  doc/DDR reference, or both). Example: `# DOMAIN-BOUNDARY: floor sourced from market_data's
  daily_universe view; see DDR-0014 for why this repo now owns its own ceiling constant instead.`
- The marker must appear within **5 lines** (inclusive, counted in the file content the hook is
  inspecting — i.e. `tool_input.content` for Write, or the post-edit `new_string` for Edit) above
  or below the line containing the matched `externalSourceIdentifiers` entry. **PROVISIONAL —
  owner: wright.** The 5-line proximity window has no external precedent; it is a first-pass value
  chosen for this sprint's build, not a measured or cited number, and is expected to be recalibrated
  against real false-positive/negative rates once a real manifest (e.g. `gap-lens-dilution-filter`'s,
  at retrofit time) is in use. If proximity search proves too strict or too loose in practice, wright
  owns revising this constant — it is not treated as settled by this document.
- Citation location is the same file as the match (not a separate docs file). Rationale: the whole
  failure mode DDR-0014 names is a value crossing a boundary *silently* — requiring the citation to
  live at the point of use maximizes the chance a future reader (human or agent) sees the rationale
  in the same place they see the read, without needing to know a separate doc exists.
- A manifest MAY optionally allow a `DOMAIN-BOUNDARY: see <path>` shorthand pointing at a docs file
  section, but the marker line itself must still be present at the point of use — this is a
  pointer, not an exemption from having something at the consuming site.

## 6. Hook Behavior (v1, complete)

**Components**, reusing `first-turn-contract-enforcement`'s wrapper/probe split:

| Component | Responsibility | Location |
|---|---|---|
| `domain-boundary-provenance.sh` | Wrapper: capture stdin, invoke probe under bounded timeout, validate output shape, fail-open on any failure mode, own `probe_error` fallback writer | `.claude/hooks/domain-boundary-provenance.sh` |
| `domain_boundary_provenance_probe.py` | Probe: load manifest, match `pipelineConfigGlobs`, scan `tool_input` content against `externalSourceIdentifiers`, check `DOMAIN-BOUNDARY:` proximity, decide allow/deny, write track-record line | `scripts/domain_boundary_provenance_probe.py` |
| `domain-boundary-manifest.schema.json` | JSON Schema for §4's manifest shape, used by the probe to validate a target repo's manifest before trusting it | `docs/tooling/domain-boundary-manifest.schema.json` |
| Self-test manifest + fixture corpus | Exercises detection/citation logic without a real target repo's manifest | `tests/fixtures/domain_boundary_manifest_fixture.json`, `tests/fixtures/domain_boundary_corpus.json` |
| Track-record log | Append-only audit trail, same shape/purpose as the sibling hook's | `docs/tooling/domain-boundary-provenance-track-record.jsonl` (gitignored, per sibling convention) |

**Decision procedure** (probe, pure function of `PreToolUse` stdin — `tool_name`, `tool_input`,
`cwd`/`$CLAUDE_PROJECT_DIR`):

1. If `tool_name` is not `Edit` or `Write` → allow (nothing to check), write track-record entry
   `decision: "allow"`, `reason: null`.
2. Load `<repo>/docs/tooling/domain-boundary-manifest.json` relative to `$CLAUDE_PROJECT_DIR`. If
   absent, unreadable, or fails schema validation → allow (§4's "no manifest present" posture),
   track-record entry `decision: "allow"`, `manifest_status: "absent_or_invalid"`.
3. **Normalize `tool_input.file_path` to a repo-root-relative, POSIX-style path before any glob
   match is attempted — no glob comparison in this step ever runs against an absolute path.**
   Claude Code's real `PreToolUse` envelope for `Edit`/`Write` carries `tool_input.file_path` as an
   ABSOLUTE filesystem path (not pre-relativized) — this document does not assume otherwise, and the
   procedure below is required, not optional, for step 3's glob match to ever succeed on a real
   invocation.
   - **Repo root resolution:** use `$CLAUDE_PROJECT_DIR`, the same value already used in step 2 to
     locate the manifest file. Note on consistency with the sibling hook (verified against the real
     files, not from memory): `first_turn_contract_probe.py` and `first-turn-contract.sh` do **not**
     use `$CLAUDE_PROJECT_DIR` — they derive repo root from their own script's on-disk location
     (`os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` in the probe;
     `cd "$(dirname "${BASH_SOURCE[0]}")/../.."` in the wrapper), which works for them because that
     hook only ever runs against the one repo it's installed in. This hook is different: its probe
     script lives in `agent-rig` but must resolve the *target* repo's root — a repo that, per §2,
     may not be `agent-rig` at all once retrofitted elsewhere — so script-location resolution does
     not apply here and would resolve the wrong repo. `$CLAUDE_PROJECT_DIR` (already relied on for
     manifest discovery in step 2 and named in §4's manifest-path description) is therefore the
     correct and only mechanism for this hook, not a deviation from the sibling pattern for its own
     sake.
   - **Algorithm:** resolve `$CLAUDE_PROJECT_DIR` to an absolute, symlink-resolved path
     (`os.path.realpath`). Resolve `tool_input.file_path` to an absolute, symlink-resolved path the
     same way. If the resolved file path is not equal to, or is not under, the resolved
     `$CLAUDE_PROJECT_DIR` (i.e. `os.path.commonpath([...])` does not equal the resolved repo root) →
     **allow** — do not attempt a glob match at all. This is the fail-open edge case: a symlink
     resolving outside the project directory, or an edit somehow targeting a path outside the
     project directory, is treated exactly like "no glob match" (below), consistent with §6's
     overall fail-open posture. Track-record entry `decision: "allow"`, `manifest_status:
     "matched"`, `file_in_scope: false`.
   - Otherwise, strip the resolved `$CLAUDE_PROJECT_DIR` prefix (plus its trailing path separator)
     from the resolved file path to obtain a repo-root-relative path, then convert any `os.sep`
     path separators to `/` (POSIX-style) — relevant only if the probe is ever run on a
     non-POSIX host; on Linux this is a no-op. This relative, POSIX-style path — not
     `tool_input.file_path` verbatim — is what step 3's `pipelineConfigGlobs` match (and step 8's
     reported `file_path`, for readability) is run against.
   - Match the resulting relative path against each glob in `pipelineConfigGlobs` using
     `fnmatch.fnmatch()` (§4). If it matches no glob → allow, track-record entry `decision:
     "allow"`, `manifest_status: "matched"`, `file_in_scope: false`.
4. **Scan surface (identical to §5's definition — this is the single, authoritative statement of
   what the probe inspects; no other resolution is performed):** `tool_input.content` (Write) or
   `tool_input.new_string` (Edit), taken as-is from the tool call. The probe never reads the
   on-disk file, never applies `old_string`→`new_string` against it, and never resolves a "full
   post-edit file" view. If `tool_input.new_string` is absent or empty for an Edit (e.g. a
   pure-deletion edit with no replacement text) → allow, `matches_found: 0` (nothing was
   introduced to scan).
   **Consequence (resolves grandfathered-match handling):** v1 checks only content the current
   tool call is introducing. An `externalSourceIdentifiers` match that exists elsewhere in the
   file — in `old_string`, in untouched lines, or anywhere outside `new_string`/`content` — is
   never inspected and can never cause a deny, regardless of whether it is cited. This is a
   deliberate scope choice, not an oversight: DDR-0014 itself frames the check's value as
   "catching the next instance... not retroactive" (§6's Fail-open rationale already quotes this),
   and a block triggered by a pre-existing, uncited identifier the current edit never touched
   would be exactly the kind of unexplained, edit-unrelated block that §6's fail-open rationale
   warns "would undermine adoption of every hook in DDR-005's cluster." Retroactive scanning of
   untouched file content is out of scope for v1 and not implied by anything in this document;
   flagging pre-existing uncited matches (e.g. via `benchmark` or a future scheduled scan) is a
   separate mechanism, not this hook's job.
5. Scan the scan surface (step 4) for any `externalSourceIdentifiers` match (literal substring or
   `re:` regex, §4). No match → allow, `decision: "allow"`, `matches_found: 0`.
6. For each match, search the 5-line window (§5) — counted within the same scan surface, i.e.
   lines of `new_string`/`content` itself, not the on-disk file — for a `DOMAIN-BOUNDARY:` marker
   line with non-empty trailing content. Any match lacking a marker in its window → **deny**.
7. If all matches have a qualifying marker → allow, `decision: "allow"`, `matches_found: N`,
   `matches_cited: N`.
8. On deny: emit the reason listing every unmarked identifier match (file, line, matched
   identifier) and the exact remediation ("add a `DOMAIN-BOUNDARY: <rationale>` comment within 5
   lines of the flagged read"). Write track-record entry `decision: "deny"` with the same detail.

**Wrapper** (`domain-boundary-provenance.sh`): structurally identical to `first-turn-contract.sh`
(§ references above) — capture stdin to a temp file, invoke the probe under a bounded timeout,
validate stdout shape, `write_probe_error`-equivalent fallback on non-zero exit/timeout/malformed
output, fail open (allow) on every failure path. **Timeout: 5s. PROVISIONAL — owner: wright**,
reused as a starting value from `first-turn-contract.sh`'s own measured-and-cited 5s bound, but
**not itself measured for this probe** (this probe does file I/O the sibling probe does not —
reading and schema-validating the target repo's manifest file (§4/§6 step 2) — even though, per
§6 step 4, it never reads the on-disk Edit target itself; the sibling's 167ms/85ms measurements do
not transfer). Forge must measure this probe's actual runtime against representative manifest
sizes before this value is treated as settled, per the same standard the sibling wrapper's own
comment sets.

**Fail-open guarantee:** identical posture to the sibling hook — a PreToolUse hook whose only power
is to block must, on any internal error (probe crash, manifest read failure mid-scan, timeout,
malformed output), emit an allow, never a deny. A false negative (missed citation) is an acceptable
failure mode per DDR-0014 itself ("the check's value is catching the next instance... not
retroactive," "a false negative is possible"); a false positive that blocks unrelated work on a
probe bug is not acceptable and would undermine adoption of every hook in DDR-005's cluster.

## 7. Data Schemas

```typescript
/** PreToolUse stdin, fields this probe reads. Full envelope has more fields (session_id,
 *  transcript_path, etc., mirrored from the sibling probe's stdin handling) — only the
 *  fields this probe uses are listed. Confirmed by live capture (§3, 2026-08-22): the real
 *  `Write` PreToolUse envelope's top-level fields are session_id, transcript_path, cwd,
 *  prompt_id, permission_mode, effort ({level}), hook_event_name, tool_name, tool_input
 *  (file_path, content for Write), tool_use_id. That same capture confirms
 *  `tool_input.file_path` is genuinely ABSOLUTE in the real envelope (not pre-relativized) —
 *  independent confirmation of the assumption §6 step 3's normalization procedure already
 *  relied on. */
interface DomainBoundaryHookInput {
  tool_name: string;                 // "Edit" | "Write" | other (ignored)
  tool_input: {
    file_path: string;
    content?: string;                // Write
    old_string?: string;             // Edit
    new_string?: string;             // Edit
  };
  cwd?: string;
}

interface DomainBoundaryHookOutput {
  // Deny shape confirmed by live verification against the real harness (§3, 2026-08-22) —
  // not a candidate, no forge-time re-verification needed for this shape.
  decision?: "block";
  reason?: string;
}

interface TrackRecordEntry {
  timestamp: string;                 // ISO 8601 UTC
  session_id: string | null;
  tool_name: string;
  file_path: string | null;
  manifest_status: "absent_or_invalid" | "matched";
  file_in_scope: boolean | null;
  matches_found: number | null;
  matches_cited: number | null;
  decision: "allow" | "deny" | "probe_error";
  reason: string | null;
  probe_error: string | null;
}
```

## 8. Acceptance Criteria

1. A `PreToolUse` event for `Edit`/`Write` targeting a file **not** matched by any
   `pipelineConfigGlobs` entry in the target repo's manifest is always allowed, and the track record
   shows `file_in_scope: false`.
2. A `PreToolUse` event for a repo with no manifest file present at
   `docs/tooling/domain-boundary-manifest.json` is always allowed, and the track record shows
   `manifest_status: "absent_or_invalid"`.
3. A `PreToolUse` event for a matched file whose proposed content contains an
   `externalSourceIdentifiers` match with a qualifying `DOMAIN-BOUNDARY:` marker within the 5-line
   window is allowed.
4. A `PreToolUse` event for a matched file whose proposed content contains an
   `externalSourceIdentifiers` match with **no** qualifying marker within the 5-line window is
   denied, with a reason string naming the file, the matched identifier, and the remediation.
5. A probe crash, malformed manifest, or wrapper timeout always results in allow (fail-open) —
   verified by a fixture-driven test analogous to `tests/test_first_turn_contract_probe.py`'s
   `probe_error` cases.
6. The track-record log is append-only, one JSON line per invocation, and writable-failure-tolerant
   (a log write failure never changes the allow/deny decision already computed) — same guarantee as
   the sibling hook's `write_track_record`.
7. The self-test fixture corpus (§6) exercises, at minimum: no-manifest, out-of-scope file,
   in-scope-no-match, in-scope-match-cited, in-scope-match-uncited, the true window edge at
   distance 5 (allows, per §5's "5 lines, inclusive"), marker-just-outside-window (distance 6,
   denies), pre-existing-uncited-match-unrelated-edit — an Edit whose
   `old_string`/`new_string` do not touch the line carrying a pre-existing, uncited
   `externalSourceIdentifiers` match elsewhere in the file, asserted **not denied** (§6 step 4's
   scan-surface scope: only `new_string`/`content` is inspected, never the rest of the file) — and
   **absolute-path-normalization** (§6 step 3): a manifest `pipelineConfigGlobs` entry written
   relative to repo root (e.g. `docs/tooling/*.json`) exercised against a `tool_input.file_path`
   supplied in its realistic, non-relativized ABSOLUTE form (e.g.
   `/home/d-tuned/agent-rig/docs/tooling/foo.json`, not pre-stripped to `docs/tooling/foo.json`),
   asserting `file_in_scope: true` and correct downstream allow/deny classification — plus a
   sibling case with an absolute `tool_input.file_path` resolving outside the fixture's
   `$CLAUDE_PROJECT_DIR` root entirely, asserting `file_in_scope: false` / allow (the step 3
   fail-open edge case). This is the single most important fixture pair in the corpus: every other
   case above can pass against a self-authored fixture using already-relative test paths while the
   glob match is silently inert against Claude Code's real, always-absolute `tool_input.file_path`
   — only this pair exercises normalization itself rather than assuming it already happened.
8. This sprint's deliverable does not modify any file outside `agent-rig` — verified by `git status`
   / diff scope at forge completion (Intake OQ-4 resolution, §2).
9. No PROVISIONAL constant in this document (§5's 5-line window, §6's 5s timeout) ships without the
   `PROVISIONAL — owner: wright` marker already present above; forge does not need to add markers
   this document omitted, only to keep them as it revises the values if measurement warrants.

## 9. Integration Boundary — What This Tool Does NOT Get Authority Over

- **Whether a cited rationale is correct.** This hook checks for the *presence* of a
  `DOMAIN-BOUNDARY:` marker with non-empty content, nothing more. A citation that exists but is
  wrong, stale, or hand-waved passes this check — judging that stays `benchmark`'s job, Frank's
  job, and a human's (DDR-0014 §"What it is not").
- **CI.** This is a Claude-Code-session PreToolUse hook, not a CI gate. It has no effect on a
  commit made outside a Claude Code session, a direct `git commit` from a shell, or any pipeline
  run that does not go through an Edit/Write tool call. Retrofitting equivalent coverage into CI
  (e.g. a pre-commit or CI-stage scan using the same manifest/marker format) is out of this
  sprint's scope and not implied by anything above.
- **Frank's binding gate.** This hook runs independently of, and has no bearing on, Frank's
  spec-gate or forge-gate verdicts for other sprints. It is not a substitute for either.
- **Retrofit sequencing or scope for other repos.** This document defines the mechanism and its
  schema; it does not decide which repos adopt it next, or author any other repo's manifest. Per
  §2, `gap-lens-dilution-filter`'s retrofit is explicitly out of scope for this sprint.
- **DDR-010's overlapping-family concern.** Per Intake OQ-5, this document does not attempt to
  reconcile scope with DDR-010 (Gate Assertion-Coverage Check, `market_data`, still DRAFT) — flagged
  as a future coordination point, not resolved here.

## 10. Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib (`json`, `re`, `os`, `sys`, `fnmatch`, `datetime`) | matches sibling probe's runtime (no new interpreter requirement) | Probe implementation, consistent with `first_turn_contract_probe.py`'s zero-third-party-dependency posture |
| `jsonschema` (Python) | **not yet confirmed present in this repo's environment — forge must verify before depending on it, or hand-roll manifest validation with stdlib only to avoid adding a new dependency for a spec-lite sprint** | Optional: manifest schema validation (§6, component 3). If unavailable/undesired, forge may implement equivalent validation by hand against §4's schema without a new dependency; this document does not mandate the library, only the validation behavior. |

No new dependency is required for the probe's core detection logic (regex/substring matching,
manifest JSON parsing) — only the optional schema-validation convenience noted above.

## 11. Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Wrapper/probe split | `.claude/hooks/domain-boundary-provenance.sh` + `scripts/domain_boundary_provenance_probe.py` | Reuses `first-turn-contract-enforcement`'s established shape verbatim — bounded-timeout shell wrapper delegating to a pure-function Python probe, per Intake Constraint "reuse the wrapper shape, don't redesign it." |
| Explicit allowlist/manifest, non-blocking fallback for anything outside it | §4 manifest, §6 step 2/3 | Reuses `prompt-router-starter`'s `gate.py` *shape* (not code) per Intake's named reference pattern. |
| Fail-open on any internal error | §6 | Same posture as sibling hook and this repo's general Stop/PreToolUse hook doctrine — a hook whose only power is to block must never let its own bug become an unexplained block. |
| Append-only, gitignored track-record log | §6 | Same convention as `first-turn-contract-track-record.jsonl`. |

**Anti-patterns (do not use):**
- General static import/reference analysis for detection — rejected in §4 with rationale.
- Reusing the bare `PROVISIONAL` marker as the citation format — rejected in §5 with rationale (the
  two claims are semantically different; conflating them defeats DDR-0014's purpose).

## 13. Adopting This Hook in Another Repo

Retrofit is out of scope for this sprint (§2) — this section is a short how-to for whoever does it
later (named consumer: `gap-lens-dilution-filter`, per DDR-0014/DDR-006).

**1. Copy the mechanism.** Bring over `.claude/hooks/domain-boundary-provenance.sh`,
`scripts/domain_boundary_provenance_probe.py`, and register the hook for `PreToolUse` on
`Edit`/`Write` in the target repo's `.claude/settings.json`, matching how
`first-turn-contract.sh` is registered there today.

**2. Write the manifest.** Create `docs/tooling/domain-boundary-manifest.json` in the target repo,
validating against `domain-boundary-manifest.schema.json`:

```json
{
  "schemaVersion": 1,
  "pipelineConfigGlobs": ["src/pipelines/*.py", "config/*.yaml"],
  "externalSourceIdentifiers": ["MAX_BYTE_CAP", "re:daily_universe\\."]
}
```

- `pipelineConfigGlobs`: which files in *this* repo the hook inspects on Edit/Write. Only files
  matching one of these globs are checked at all — everything else passes silently. Glob syntax is
  `fnmatch.fnmatch()`, not shell glob: `*` crosses path separators, and `**` has no special meaning
  (behaves like `*`).
- `externalSourceIdentifiers`: the specific constants, flags, or references that count as a
  cross-domain read in this pipeline — a literal substring, or a `re:`-prefixed regex. Start from
  the pipeline's own known trouble spots (imported constants, config keys owned by another
  pipeline) rather than trying to be exhaustive on day one; the manifest can grow over time.

If no manifest exists at that path, the hook allows every edit unchecked — writing the manifest is
the entire opt-in.

**3. Cite in practice.** When an edit introduces a matched identifier, add a `DOMAIN-BOUNDARY:`
comment within 5 lines of it, on its own line, with the marker followed by non-whitespace content:

```python
# DOMAIN-BOUNDARY: floor sourced from market_data's daily_universe view;
# see DDR-0014 for why this repo now owns its own ceiling constant instead.
MAX_BYTE_CAP = 50_000
```

No marker within the 5-line window → the edit is denied, with a reason naming the file, the
matched identifier, and this same remediation. A marker that exists but is wrong or stale still
passes — this hook checks presence only, not correctness (§9).

## 12. Open Items Carried to Forge

- **§5's 5-line proximity window and §6's 5s timeout** — both explicitly PROVISIONAL, owner wright,
  to be revisited against real measurement once exercised against a real manifest or measured
  runtime.
- **§10's `jsonschema` dependency question** — resolve at forge start, before component 3 is built.

---

*This document does not self-lock. Per this repo's workflow, it proceeds to Frank's binding
spec-gate and human approval before any status change from DRAFT.*
