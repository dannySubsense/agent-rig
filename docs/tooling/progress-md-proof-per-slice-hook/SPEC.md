# PROGRESS.md Proof-Per-Slice Hook — Tooling Spec (spec-lite)

**Status**: LOCKED (2026-08-23, Danny — approved via `/forge-start` invocation; Frank spec-gate PASS, both layers, plus a Danny-directed post-approval revision closing the mutation-bypass gap, final PASS logged in GATE-LOG.md)
**Mode**: spec-lite (per `docs/tooling/progress-md-proof-per-slice-hook/INTAKE.md` — no Requirements/
UI/Roadmap layering; this single document carries purpose, contract, and acceptance criteria)
**Author**: wright
**Date**: 2026-08-23

**Spec of record**: `docs/specs/agent-rig-ddrs/DDR-008-progress-md-proof-per-slice-hook.md`
(implementation-side DDR). **Governing thesis**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-
and-work-orders.md` §1 — "rules that live as exhortations get performed; rules that live as failing
checks get satisfied." This is DDR-005's own named first implementation slice. **Intake**:
`docs/tooling/progress-md-proof-per-slice-hook/INTAKE.md` (APPROVED 2026-08-22). **Sibling build,
same cluster, same session**: `docs/tooling/domain-boundary-provenance-hook.md` — this document
matches its structure, allowlist/manual-stamp split, and PROVISIONAL-constant discipline
throughout; departures are called out explicitly where they occur, not silently.

---

## 1. Purpose

Mechanize the gap named in the standing feedback memory
`feedback_gate_not_substitutable_by_slice_checkboxes.md`: a `[x]` mark on a `PROGRESS.md` slice
line is today self-asserted by the agent marking it, cross-checked against `GATE-LOG.md` only by
convention and discipline — nothing fails if the check is skipped. This hook gives each slice an
optional, declared proof command and mechanically runs it before letting the checkbox transition
from `[ ]` to `[x]` stand, refusing the edit if the command fails or is missing when declared.

## 2. Non-Goals

- **Not a soundness judge.** This hook verifies a declared proof command *passed* (or was
  correctly stamped `manual` because it isn't mechanically runnable). It does not evaluate whether
  the proof command itself is a good test of "done" — a `pytest -k test_stub_only` that trivially
  passes is not this hook's problem to catch. That judgment stays human/Frank's job at spec-gate/
  forge-gate time, same carve-out the sibling hook establishes for its own citation check (§9).
- **Not a replacement for Frank's binding gate or `GATE-LOG.md`.** This hook checks mechanical
  slice-completion claims, one line at a time, in isolation. Frank's gate is a judgment call on the
  whole sprint, across every slice and every Done-When criterion together, and is the only binding
  verdict in this repo's workflow. A slice passing this hook's proof check is necessary evidence for
  Frank's gate, never a substitute for it — this hook has no authority to mark a sprint complete,
  only to stop an individual `[x]` mark that has no evidence behind it.
- **Not a redesign of `first-turn-contract-enforcement`'s wrapper.** Per the Intake constraint, this
  hook reuses that wrapper's bounded-timeout/fail-open/append-only-log shape verbatim — only the
  detection/proof logic specific to slice completion is new.
- **Not retroactive.** See §3/§6 — already-`[x]`-marked slices in any existing `PROGRESS.md` are
  never inspected by this hook, at any point, for any repo.
- **Not a general command-execution sandbox.** This hook does not attempt to safely execute
  arbitrary shell text. A declared proof command that isn't allowlisted (§5) is never run — it is
  stamped `manual` and never blocks, exactly as the reference `gate.py` pattern and the sibling
  hook's manifest-absent posture both already establish.

## 3. Trigger Surface (resolves Intake Open Question 3)

**Decision: PreToolUse, matched on `Edit` against files whose basename matches `*PROGRESS.md`
(fnmatch, case-sensitive), scoped to the specific `[ ]`→`[x]` transition the edit introduces on a
slice line carrying a `PROOF:` marker.** Not a Stop hook.

**Rejected alternative — Stop hook checking any claimed-complete slice at end of turn:**
- **Cannot pinpoint which edit made the claim.** A Stop hook sees the final transcript state, not
  the specific tool call that flipped a checkbox. It would have to re-scan the entire `PROGRESS.md`
  file every turn to find newly-`[x]` lines, re-running proof commands for slices that may have been
  marked complete turns ago and already verified — wasted, redundant execution the sibling hook's
  own §3 rejected-alternatives reasoning already flags for its own analogous choice ("a scan that
  isn't run is exactly the failure mode this hook exists to end" cuts the other way here too: a scan
  that reruns unnecessarily is its own cost, at exactly the point — end of turn — where the agent's
  claimed-complete FOOTER contract, `first-turn-contract-enforcement`, is already checking a
  different property of the same turn).
- **Same tool/turn-boundary preference this repo already has.** `first-turn-contract-enforcement`
  and `session-queue.sh` both establish a preference for hooks anchored to the specific tool call or
  turn boundary that produces the state being checked, not a later, coarser boundary. The specific
  tool call that produces a slice's `[x]` claim is the `Edit` to `PROGRESS.md` itself — a PreToolUse
  hook on that edit can refuse the mark before it lands, letting the agent add or fix the proof in
  the same turn, exactly the ergonomic argument the sibling's §3 makes for `PreToolUse` over
  `PostToolUse`.
- **A Stop hook cannot isolate *which* slice line changed this turn without re-deriving that from a
  diff anyway** — at which point it has reconstructed the PreToolUse view of the world one step
  later and with less precision (no `old_string`/`new_string` pairing, only before/after full-file
  state it would have to fetch and diff itself).

**Why PreToolUse specifically (not PostToolUse):** identical reasoning to the sibling's §3 — a
PreToolUse deny prevents the false `[x]` from landing at all, letting the agent add the missing
proof (or fix the failing one) before the file changes; a PostToolUse hook could only flag after the
fact, forcing a follow-up edit for the same detection power.

**Scope note — Edit only, not Write:** unlike the sibling hook (which matches `Edit` and `Write`
symmetrically because either can introduce an uncited identifier), this hook matches `Edit` only. A
`[ ]`→`[x]` *transition* is inherently a diff between an old and new state of the same file region —
a `Write` (whole-file replacement, no `old_string`) has no old-state region to diff against without
the hook reading the on-disk file itself, which §6 deliberately avoids (same posture as the
sibling's §6 step 4: inspect only what the tool call itself carries, never the on-disk file). A
`Write` that overwrites `PROGRESS.md` wholesale — expected to be rare relative to incremental `Edit`
calls, given every real `PROGRESS.md` example seen this session was edited line-by-line — is not
inspected by this hook. This is a scoped, stated gap (§9), not a silent one.

## 4. Proof-Command Syntax (resolves Intake Open Question 1)

**Decision: an inline `PROOF:` marker appended to the existing slice bullet line, following the
same em-dash-separated-segment convention `PROGRESS.md` files already use for appending metadata
(see the real example this was designed against, `docs/tooling/domain-boundary-provenance-hook-
PROGRESS.md`, e.g. `— \`scripts/...\` (AC1-AC7)` as a trailing segment). No new file, no structured
block, no YAML front-matter per slice.**

**Syntax:**
```
- [ ] Slice N: <description> — PROOF: <shell command, rest of line>
```
- The literal marker `PROOF:` (case-sensitive, exact string) may appear anywhere in a slice bullet
  line (a line whose stripped content starts with `- [ ]` or `- [x]`), always as the **last**
  segment on the line — everything after `PROOF:` (trimmed) is the command, verbatim, to end of
  line. No further ` — ` segments are permitted after a `PROOF:` segment; if authors need to add
  detail once a slice is complete (e.g. `COMPLETE 2026-08-22 (17/17 tests)`, as the real example
  file does), that segment goes *between* the description and `PROOF:`, and `PROOF:` remains
  present, still last, at the point of the completing edit.
- **Identity key (redefined 2026-08-23 — see §6 for the full matching algorithm this feeds):** every
  checkbox-bullet line (`- [ ]` or `- [x]`, any position in the edited text, in either
  `old_string` or `new_string`) has a **description segment** — everything between the checkbox and
  the first ` — ` on the line, or the whole post-checkbox text if there is no ` — ` — and, if
  present, a **`PROOF:` segment** — the literal marker plus command text, always the line's last
  ` — `-separated segment when present. The description segment is this document's identity key:
  "which slice is this," independent of where the line sits in the edited text, exactly the
  correspondence a human reader would use to figure out which line completed which slice, not the
  line's array position. §6 matches slice lines by this identity key, not by comparing text at the
  same line index — this closes the whole family of positional-diffing bypasses (line-count
  mismatch, line reordering) at the root, rather than patching each instance found.
- Example, matching the real example file's own style:
  `- [ ] Slice 4: Wrapper wiring — PROOF: bash tests/test_progress_proof_wrapper.sh`
  completing to:
  `- [x] Slice 4: Wrapper wiring — COMPLETE 2026-08-22 (15/15 tests) — PROOF: bash tests/test_progress_proof_wrapper.sh`
  This is a detected transition (§6): the description segment (`Slice 4: Wrapper wiring`, ignoring
  the checkbox mark) matches an old `- [ ]` candidate with the same description, the `PROOF:`
  segment (`PROOF: bash tests/test_progress_proof_wrapper.sh`) is identical between the matched old
  and new lines, and the inserted `COMPLETE 2026-08-22 (15/15 tests)` segment in between is ignored
  by the match — it is neither part of the description segment nor the `PROOF:` segment.

**Stable per-slice identifier — `SLICE-ID:` segment (added 2026-08-23, forward-only, resolves the
residual named at the top of this revision — see §6/§9/§12 for the full closure trace).**

- **Syntax:** `SLICE-ID: <token>`, a new em-dash-separated segment, same segment family as
  `PROOF:` and the `COMPLETE ...` metadata segment. **Placement:** by convention, immediately
  after the description segment and before any `COMPLETE ...` metadata segment and before
  `PROOF:` (which remains, unconditionally, the line's last segment when present) — e.g.
  `- [ ] Slice N: <description> — SLICE-ID: <token> — PROOF: <command>`. The probe does **not**
  rely on this position to extract the segment — it scans all em-dash-separated segments on the
  line for the exact prefix `SLICE-ID:` (case-sensitive), wherever it falls among the non-last
  segments, so a line that deviates from the recommended ordering (e.g. `COMPLETE` before
  `SLICE-ID`) is still parsed correctly. `PROOF:`'s "always last" rule (above) is unchanged and
  takes precedence — a segment reading `SLICE-ID: ...` is never treated as the `PROOF:` segment
  regardless of position, since the two are distinguished by their literal marker text, not
  position.
- **Token format:** any non-empty, whitespace-free string not containing ` — ` (so it cannot be
  mistaken for a segment boundary) and not itself starting with the literal `PROOF:` or `SLICE-ID:`
  prefixes. No format is mandated beyond that — a short human-readable slug is recommended (e.g.
  `slice-04`, reusing the slice's own number at authoring time is a reasonable default) but the
  token is **content-independent** once assigned: it is never re-derived from the description text
  and must not change even if the slice is later renumbered or reworded. This is the entire point
  of the token — it is a name, not a description.
- **Assignment and scope:** author-assigned (human or agent authoring the slice line), **not
  hook-assigned.** This hook is a `PreToolUse` inspector with no authoring role and no persisted
  state (§6) — it never generates, writes, or backfills a `SLICE-ID`, only reads one if present.
  The token is assigned once, when a slice line is first written to the file (as `- [ ]`, with or
  without a `SLICE-ID` segment already present at that point), and must never change on any
  subsequent edit to that line, including the completing edit — an ID that changes or is
  removed falls through step 4a to ordinary
  description/PROOF-identity matching (steps 5-6), not automatically to allowed-unchecked; see §6's
  residual-gap statement of record for exactly when that still catches the edit versus when it
  doesn't.
- **Uniqueness scope: per-file.** A `SLICE-ID` token must be unique among slice lines within the
  same `PROGRESS.md` file. This hook does not check, and does not need, uniqueness across files or
  across the repo — matching (§6) only ever compares candidates extracted from the same file's
  `old_string`/`new_string` in a single `Edit` call.
- **Required or optional:** **optional, and, when present, authoritative over content-based
  matching for that candidate** (§6). A file may mix ID'd and non-ID'd slice lines freely — the
  matching algorithm handles both per-candidate, not per-file. This hook does not require any file,
  new or existing, to adopt `SLICE-ID` — see §6's residual section and §9 for the explicit,
  permanent two-tier posture this establishes.
- **Worked example — SLICE-ID survives a simultaneous description+PROOF edit (traced by hand):**
  ```
  - [ ] Slice 7: Config loader — SLICE-ID: slice-07 — PROOF: pytest tests/test_config_loader.py
  ```
  completing, in one edit, to:
  ```
  - [x] Slice 7: Config loader (renamed to Settings loader) — SLICE-ID: slice-07 — COMPLETE 2026-08-23 (9/9 tests) — PROOF: pytest tests/test_settings_loader.py -k full_suite
  ```
  Trace: the description segment changed (`Slice 7: Config loader` → `Slice 7: Config loader
  (renamed to Settings loader)`) **and** the `PROOF:` segment changed (`pytest
  tests/test_config_loader.py` → `pytest tests/test_settings_loader.py -k full_suite`) in the same
  edit — under content-based matching alone (no `SLICE-ID`), this pair would fall through
  unmatched, per §6's residual (the case this addition exists to close; see the narrower residual
  named in the prior revision). With `SLICE-ID: slice-07` present and identical on both the
  old-open and new-done candidate, §6's identity-matching step finds the token equal on both sides
  and matches the pair **by `SLICE-ID`, before description or `PROOF:` content is even compared for
  matching purposes.** The pair is then treated as a normal completion: the new-done candidate's
  `PROOF:` command (`pytest tests/test_settings_loader.py -k full_suite`) is extracted, allowlist-
  checked, and run — no mutation-deny fires, because `SLICE-ID` equality is itself sufficient
  evidence this is the same slice completing with updated text, not two unrelated candidates.
- **A slice bullet line whose matched `- [x]` candidate carries no `PROOF:` marker at all is never
  proof-checked — allowed unconditionally, same posture as "no manifest" in the sibling hook.** It
  is the completed (`- [x]`) side of a matched pair that governs whether a proof command is
  extracted (§6 step 8) — a slice that never declares a proof command, on either side of the match,
  is opt-in-skipped. Declaring a proof command is opt-in per slice, not mandatory; this hook adds a
  mechanism, not a new requirement that every slice must satisfy to be marked done. (Whether Frank
  or a human reviewer requires proof commands as a matter of process is out of this hook's authority
  — §9.) **This is distinct from the case where the matched `- [ ]` candidate has no `PROOF:` marker
  but the matched `- [x]` candidate does** (a slice completed by adding its proof command in the
  same edit that flips the checkbox) — that case has a `PROOF:` marker on the completed side, so it
  is not opt-in-skipped; §6's matching step has nothing to compare on the old side for the `PROOF:`
  equality check (skipped), and §6 step 8 governs: the newly-present `PROOF:` command on the matched
  `- [x]` line is allowlist-checked and, if allowlisted, run — see AC11's dedicated fixture.
- A slice line MAY carry more than one `PROOF:`-introduced command by separating commands with
  ` && ` within the single trailing segment (shell semantics: all must succeed). This document does
  not define a multi-command list syntax beyond what the shell's own `&&` already provides — no new
  parsing surface for "multiple proofs" is needed.

**Rejected alternative — structured block per slice:** a fenced or indented sub-block under each
slice bullet (e.g. a nested `- proof: ...` list item) was considered and rejected. `PROGRESS.md`'s
existing convention (confirmed against the real example file) is single-line, em-dash-segmented
bullets — every slice's full history (description, completion date, test counts, file paths) lives
on one line, appended to as the slice progresses. A structured block would be the first multi-line
slice-entry shape in the file, breaking that convention for the sake of one new field, and would
also complicate detection. The inline marker is the smaller, less invasive addition — consistent
with the Intake's explicit instruction to "propose a concrete, minimal syntax addition to the
existing checkbox format, don't invent a whole new file format."

## 5. Proof-Command Allowlist (resolves Intake Open Question 2)

**Decision: this hook defines its own allowlist, narrower in purpose than the sibling's — a
departure from straight reuse, with a stated reason.**

**Why straight reuse doesn't transfer:** the sibling hook's allowlist-shaped artifact (§4's
manifest) declares *files to inspect* and *identifiers to flag* — it never executes anything.
`first-turn-contract-enforcement`'s probe never executes anything either. This hook is different in
kind: its entire job is to **run a command declared in a markdown file**, which is a materially
different trust boundary (arbitrary shell execution sourced from prose, versus read-only content
inspection). Reusing either sibling's allowlist file or convention verbatim would be reusing a shape
built for a different risk; the *pattern* — an explicit allowlist, everything outside it stamped
`manual` and never blocking — is what transfers, not the artifact itself. This is the "real reason
not to" straight-reuse the Intake's OQ-2 anticipated.

**Allowlist schema**, at `docs/tooling/progress-proof-allowlist.json` (agent-rig only, this sprint —
no per-repo manifest deliverable, since this hook ships with agent-rig's own allowlist as its only
consumer for v1; a future retrofit to another repo would ship that repo's own file at the same
relative path, same pattern as the sibling's §13):

```typescript
interface ProgressProofAllowlist {
  /** Schema version. v1 only value: 1. */
  schemaVersion: 1;
  /**
   * Command prefixes trusted to execute. A declared PROOF: command is allowlisted iff its
   * exact leading substring (after stripping leading/trailing whitespace from the full
   * command) matches one of these entries verbatim. No glob/regex here, deliberately more
   * restrictive than the sibling's pipelineConfigGlobs — a false-positive allowlist match
   * here means running an untrusted command, not silently skipping a check, so the match
   * rule is exact-prefix only, not pattern-based.
   */
  allowedCommandPrefixes: string[];
}
```

**v1 allowlist content — PROVISIONAL, owner: wright, no external precedent (first-pass value for
this sprint, expected to grow as real proof commands are declared in real slices):**
```json
{
  "schemaVersion": 1,
  "allowedCommandPrefixes": [
    "pytest ",
    "python3 -m pytest ",
    "python3 scripts/",
    "bash tests/",
    "sh tests/",
    "npm test",
    "npm run "
  ]
}
```
These seven prefixes are chosen to cover every proof-command shape already seen in this repo's own
forge slices this session (`pytest tests/...`, `bash tests/test_*.sh`, `python3 scripts/*.py`), not
measured against any external corpus. wright owns revising this list as real declared proof
commands in real `PROGRESS.md` files turn up shapes not covered here.

**Not-allowlisted `PROOF:` command:** stamped `manual` — the hook never runs it, never blocks the
`[x]` transition on it, and records `proof_status: "manual_unverified"` in the track record (§7).
This is a deliberate, permanent non-blocking state, not a temporary one pending allowlist growth —
same posture as the sibling's "no manifest present" and the `gate.py` precedent's own manual-stamp
fallback (Intake, `gate.py` reference).

## 6. Hook Behavior (v1, complete — identity-based matching, redesigned 2026-08-23; SLICE-ID stable-identifier matching added 2026-08-23)

**Components**, reusing `first-turn-contract-enforcement`'s wrapper/probe split:

| Component | Responsibility | Location |
|---|---|---|
| `progress-proof-per-slice.sh` | Wrapper: capture stdin, invoke probe under bounded timeout, validate output shape, fail-open on any failure mode, own `probe_error` fallback writer | `.claude/hooks/progress-proof-per-slice.sh` |
| `progress_proof_per_slice_probe.py` | Probe: extract slice-line candidates from `tool_input.old_string`/`new_string`, match by identity, check allowlist, run allowlisted proof command under its own inner timeout, decide allow/deny, write track-record line | `scripts/progress_proof_per_slice_probe.py` |
| Allowlist file | §5 schema, loaded and validated before any command is trusted | `docs/tooling/progress-proof-allowlist.json` |
| Self-test fixture corpus | Exercises detection/execution/allowlist logic without depending on a real slice completion | `tests/fixtures/progress_proof_corpus.json` |
| Track-record log | Append-only audit trail, same shape/purpose as the sibling hook's | `docs/tooling/progress-proof-per-slice-track-record.jsonl` (gitignored, per sibling convention) |

### Why the redesign (context for this revision)

The prior version of this document detected a transition by comparing `old_lines[i]` to
`new_lines[i]` at the same array index. Frank's spec-gate found, across three supplementary review
rounds, an unbounded family of bypasses stemming from that one root cause: index-based comparison
assumes line *i* in `old_string` corresponds to line *i* in `new_string`, and any edit that breaks
that positional correspondence — a line-count mismatch, or simply reordering the slice line relative
to an adjacent line while keeping line count equal — caused the hook to silently miss or
misclassify the completion, with the proof never checked. Patching each newly-found instance did not
converge. This revision replaces positional matching with **identity-based matching**: candidate
slice lines are extracted from `old_string` and `new_string` independently, then matched to each
other by their description segment (and, for orphans, by their `PROOF:` segment — see step 6),
never by index. Line count and line position are no longer inputs to the algorithm at all.

### Decision procedure (probe, pure function of `PreToolUse` stdin — `tool_name`, `tool_input`)

1. If `tool_name` is not `Edit` → allow, track-record entry `decision: "allow"`, `reason: null`.
2. Normalize `tool_input.file_path`'s basename (final path component, no directory resolution
   needed — this check does not depend on repo root the way the sibling's glob match does). If the
   basename does not match `*PROGRESS.md` (fnmatch) → allow, track-record entry `decision: "allow"`,
   `file_in_scope: false`.
3. Read `tool_input.old_string` and `tool_input.new_string`. If either is absent → allow (nothing to
   diff), `decision: "allow"`, `reason: null`.

4. **Extract candidate lines independently from each side.** Split `old_string` into lines; for
   every line whose stripped content starts with `- [ ]`, record an **old-open candidate**: `{
   description, slice_id_or_null, proof_segment_or_null, full_line }` (description/`SLICE-ID:`/
   `PROOF:` extraction per §4). Ignore old lines starting `- [x]` and every non-checkbox line
   entirely — they are never inputs to matching. Split `new_string` into lines; for every line
   whose stripped content starts with `- [x]`, record a **new-done candidate** with the same shape.
   **Line counts of `old_string` and `new_string` are not compared at any point in this
   procedure** — a structural edit (lines added, removed, or reordered elsewhere) has no bearing on
   whether a slice-line identity matches, which is the specific property this redesign exists to
   guarantee. If neither side yields any candidates → allow, `decision: "allow"`, `transitions_found:
   0`.

4a. **SLICE-ID matching pass (added 2026-08-23, runs before description-based matching, and takes
   precedence over it for any candidate carrying a `SLICE-ID` segment).** Among old-open candidates
   that carry a non-null `slice_id`, group by token; do the same for new-done candidates. **Duplicate-
   ID check**, identical in shape to step 5's duplicate-description check: if any token has more
   than one old-open candidate AND at least one new-done candidate sharing it (or the symmetric
   case), the identity is ambiguous — deny conservatively, `decision: "deny"`, `proof_status:
   "ambiguous_match_denied"`, reason naming the duplicated `SLICE-ID` token. Otherwise, for each
   token with exactly one old-open candidate and exactly one new-done candidate: this is a **matched
   transition (matched_by: "slice_id")**. Unlike description-based matches (step 6), a `slice_id`
   match has **no C1/C2 mutation-deny distinction and no equality check on the description or
   `PROOF:` segments between old and new** — token equality alone is sufficient evidence this is the
   same slice completing, however much its description or `PROOF:` text changed in the same edit
   (this is the entire reason `SLICE-ID` closes the residual named in §6's residual section below).
   Proceed straight to step 8 onward for this matched pair. Every candidate consumed by a `slice_id`
   match (on either side) is removed from the pool before steps 5-6 run — description-based matching
   never re-considers a candidate already matched by `SLICE-ID`. A new-done candidate with a
   `slice_id` that matches no old-open candidate's `slice_id` (and vice versa) is **not** an error —
   it falls through to steps 5-6 to attempt a description-based match like any other candidate (a
   `SLICE-ID` on only one side of a pair is not itself a signal of anything; the file may be
   mid-adoption, or the ID may belong to a genuinely new slice with no matching old-open line).

5. **Duplicate-identity check (resolves the ambiguous-match question this redesign must answer
   explicitly). Operates only on candidates not already consumed by a step 4a `slice_id` match.**
   Group the remaining old-open candidates by description segment, and the remaining new-done
   candidates by description segment. If any description segment has **more than one** old-open candidate AND
   **at least one** new-done candidate with that same description (or vice versa: more than one
   new-done candidate for a description that has at least one old-open candidate) — the identity key
   is ambiguous: this hook cannot determine, from description text alone, which specific old line
   the specific new line completes. **Decision: deny conservatively, do not guess.** Emit
   `decision: "deny"`, `proof_status: "ambiguous_match_denied"`, reason naming the duplicated
   description segment and instructing the author to make each slice's description unique before
   marking either duplicate `[x]` (proof commands, if declared, are never extracted or run for an
   ambiguous key). This is a deliberate, permanent posture, not a placeholder: a `PROGRESS.md` file
   with two slices sharing identical description text is itself a latent correctness problem this
   hook is entitled to refuse to arbitrate. (A description that is duplicated **within only one
   side** — e.g. two old-open candidates share a description but neither has a same-description
   new-done counterpart — is not ambiguous in this sense; nothing is completing, so there is nothing
   to disambiguate. This falls through to step 6 and normally resolves to "no match" for that
   description, same as any other unmatched candidate.)

6. **Match by identity.** Operating on the same remaining-candidate pool as step 5 (candidates
   already matched by `SLICE-ID` in step 4a are never reconsidered here). For each description
   segment that is *not* flagged ambiguous by step 5 and has exactly one old-open candidate and
   exactly one new-done candidate: this is a **matched
   transition (primary match, matched_by: "description")**. Compare the two candidates' `PROOF:`
   segments:
   - **C1 — matching transition:** the old-open candidate has no `PROOF:` segment, or its `PROOF:`
     segment is byte-identical to the new-done candidate's `PROOF:` segment. Proceed to step 8
     onward for this matched pair (proof extraction, allowlist check, execution, allow/deny).
   - **C2 — mismatched transition (mutation-during-flip, PROOF changed or removed):** the old-open
     candidate had a `PROOF:` segment and the new-done candidate's `PROOF:` segment differs or is
     absent. **Deny**: `decision: "deny"`, `proof_status: "mutation_denied"`, reason naming the
     slice's description segment and "PROOF: segment altered or removed," with the same remediation
     as before ("mark this slice complete in a separate edit from any proof-command change"). No
     proof command is extracted or run for this pair.

   For every old-open candidate that was **not** consumed by a description match above (its
   description does not appear among new-done candidates) **and carries a `PROOF:` segment**: check
   whether that exact `PROOF:` segment text appears on any new-done candidate that was itself not
   consumed by a description match. If so, this is a **matched transition (secondary match,
   matched_by: "proof_identity")** — the description changed between old and new, but the proof
   command's identity is stable, which is enough signal to recognize the same slice completing under
   a reworded description. This is always treated as **C2 — mismatched transition (description
   mutated)**: `decision: "deny"`, `proof_status: "mutation_denied"`, reason naming the old
   description segment, "description segment altered," and the command that tied the match, with the
   same remediation. No proof command is extracted or run.

   An old-open candidate that matches neither by description nor by `PROOF:` identity, and a
   new-done candidate that matches neither by description nor by `PROOF:` identity, are each left
   **unmatched** — not a transition this edit is understood to make a claim about. An unmatched
   new-done candidate is treated exactly as a brand-new already-complete slice line would be (always
   allowed, no claim to verify); an unmatched old-open candidate is treated as a slice that remains
   pending (no claim was made this edit).

7. If step 6 produces no matched pairs at all (no C1, no C2, no ambiguous-denial from step 5) →
   allow, `decision: "allow"`, `transitions_found: 0`.

8. For each C1-matched pair, extract the `PROOF:` marker (§4) from the new-done candidate's full
   line (the completed line, since that is the line as it will exist post-edit). **No `PROOF:`
   marker present on the new-done candidate → allow this transition** (opt-in, §4).

9. If a `PROOF:` marker is present, extract the command (trailing text after the marker, trimmed).
   Check it against the allowlist (§5), exact-prefix match. **No match → allow, `proof_status:
   "manual_unverified"`, `decision: "allow"`.**

10. If allowlisted, execute the command via `subprocess.run(command, shell=True, cwd=REPO_ROOT,
    timeout=INNER_TIMEOUT)` (§ below for `INNER_TIMEOUT`). Exit code 0 → allow this transition,
    `proof_status: "verified_pass"`. Non-zero exit, or inner timeout → **deny**, `proof_status:
    "verified_fail"` or `"verified_timeout"`.

11. If any matched pair resolves to a **deny** — step 5's ambiguous-match denial, step 6's C2
    mutation-denial (by either description-primary or proof-identity-secondary matching), or step
    10's failed/timed-out proof — the whole edit is denied. A single `Edit` call can in principle
    carry multiple candidate pairs (the procedure handles the general case: **any** denied pair
    denies the tool call), though the overwhelming common case is one slice line per edit. The
    reason lists every denied pair — for an ambiguous-match denial: the duplicated description and
    the instruction to disambiguate; for a C2 denial: the slice's description segment, what changed
    (PROOF and/or description, whichever applies), and the remediation; for a step-10 denial: the
    slice line text, command, exit code or timeout, and stderr tail up to 2000 chars, plus
    remediation ("fix the failing command, or don't mark this slice `[x]` yet"). Multiple denial
    shapes are concatenated into one `reason` string when more than one occurs in the same edit. If
    every matched pair is allowed (C1 pairs resolved via steps 8-10 with no deny, and no ambiguous
    denial), allow, `decision: "allow"`, `transitions_found: N` (count of C1 matched pairs),
    `transitions_verified: <count with proof_status verified_pass>`.

### Residual gap after this redesign (honest, final — one variant, not a family)

**Two-call mutate-then-flip dodge — the only remaining variant.** This detection is a pure function
of a single `PreToolUse Edit` call's `old_string`/`new_string`. It has no memory of a line's state
in a prior `Edit` call earlier in the same turn. An agent (or human) can still dodge both C1's proof
check and C2's mutation-deny by splitting the work across two separate `Edit` calls: one `Edit` that
changes the description and/or drops the `PROOF:` segment while the line is still `- [ ]` (no flip
yet — that line is simply an old-open candidate with new text this call, allowed, since no
completion claim is being made), followed by a second `Edit` that flips the checkbox against the
now-already-mutated line. In that second call's own diff, the old-open candidate already carries the
mutated description/no-PROOF state, so the identity match against the new-done candidate has nothing
to disagree with — it matches its own already-altered baseline. This is a genuine, separate scope
limit, not a gap in the identity-matching algorithm itself: no single-call positional or content
manipulation reopens it, because the redesign no longer depends on position at all, and both the
description-preserved (PROOF-only) and PROOF-preserved (description-only) single-call mutation
shapes are now caught (C2, both matching tiers in step 6). Closing the two-call variant would require
either persisting cross-call line-state within a turn (new state, a step beyond this hook's current
pure-function-of-one-call design) or moving detection to a Stop-hook full-file comparison against
turn-start state — both rejected in §3 for this v1 on other grounds and not revisited here. Stated
here, not silently assumed away; see §9/§12.

**A narrower residual within a single call — CLOSED for `SLICE-ID`-carrying lines, 2026-08-23,
when the token survives the completing edit unchanged; still open for slices without one, and
reopened for any slice whose `SLICE-ID` token itself is altered or removed.** If a single `Edit` call changes **both** the description
segment **and** the `PROOF:` segment of the same slice line in the same edit that flips its
checkbox, and **neither side carries a `SLICE-ID` segment**, there is no shared text left on either
side to match by (description differs, and the proof-identity fallback in step 6 also has nothing
stable to key on, since the command text differs too). This pair falls through as two unmatched
candidates — indistinguishable, by this hook, from an unrelated old line going untouched plus a
brand-new already-complete line being authored. **This is exactly the residual `SLICE-ID` (§4) was
added to close:** when both the old-open and new-done candidate carry the same `SLICE-ID` token,
step 4a matches them by token *before* description or `PROOF:` content is compared for matching
purposes at all — token equality is sufficient identity evidence on its own, so a simultaneous
description+`PROOF:` change no longer breaks the match (§4's worked example traces this by hand).
**This closure is per-slice, not per-file, and is opt-in, forward-only:** a slice line that never
carries a `SLICE-ID` — whether in a file that has adopted the segment for other slices or a file
that has never adopted it at all — remains exposed to exactly the gap described above. Adopting
`SLICE-ID` going forward is how a project closes this residual for a given slice; it is not
automatic, and it is not retroactively required or applied to any existing `PROGRESS.md` file or
slice line by this hook (§9). This is a permanent two-tier state, not a transitional one: `SLICE-ID`-
carrying slices are fully closed against this residual; slices without one carry it indefinitely,
by design, unless and until an author chooses to add the segment to that slice line themselves.

**Full, precise closure statement (this is the one statement of record — §9 and §12 reference
it rather than restate it):** the simultaneous-description+PROOF-mutation dodge is closed for
SLICE-ID-carrying lines when the token survives the completing edit unchanged. An edit that
alters or removes the SLICE-ID segment — alongside a description and/or PROOF change, in the
same edit — reopens the exact dodge the token was added to close: with no stable token to key
on, the pair falls through step 4a into ordinary description/PROOF-identity matching (steps
5-6), and if both description and PROOF also changed, falls through further as two unmatched
candidates — indistinguishable, by this hook, from an unrelated old line going untouched plus
a brand-new already-complete line being authored (delete-plus-new-line). **Decision (2026-08-23,
Danny): accept this SLICE-ID-mutation variant as residual rather than adding a conservative
deny-on-vanished/changed-SLICE-ID rule.** See §12 for the full rationale.

**Inner execution timeout: 25s. PROVISIONAL — owner: wright.** No external precedent transfers —
`first-turn-contract.sh`'s 5s bound (measured against its own content-scanning probe, 167ms/85ms) is
for a probe that never executes external commands; this hook's entire job is to execute one. 25s is
a first-pass budget sized to comfortably fit a modest `pytest`/`bash` test-file run (the real example
`PROGRESS.md` file's own slices report suites in the 15-27 test range) without being large enough to
stall a turn indefinitely. Forge must measure this against a real allowlisted proof command's actual
runtime before this value is treated as settled, per the same standard the sibling wrapper's own
5s-measurement comment sets.

**Outer wrapper timeout: 30s. PROVISIONAL — owner: wright**, sized to the inner 25s plus headroom
for the probe's own overhead (allowlist load/validation, candidate extraction and matching) — not
itself measured. Forge must confirm 30s is sufficient outer slack once the inner 25s figure (above)
is itself measured and, if necessary, revised.

**Fail-open guarantee:** identical posture to both prior hooks in this cluster — a PreToolUse hook
whose only power is to block must, on any internal error (probe crash, allowlist read failure,
malformed output, outer timeout), emit an allow, never a deny. An inner proof-command timeout
(step 10) is **not** a probe error — it is a legitimate deny outcome (the declared proof did not
complete successfully within its budget, same evidentiary weight as a non-zero exit) and is handled
by the probe itself, not the wrapper's fail-open path. Step 5's ambiguous-match denial and step 6's
C2 mutation-denial are likewise not probe errors — they are legitimate, deliberate deny outcomes,
handled by the probe, not the wrapper's fail-open path (fail-open covers *probe/infrastructure*
failure, not a probe correctly reaching a deny verdict on the input it was given).

## 7. Data Schemas

```typescript
/** PreToolUse stdin, fields this probe reads. Full envelope has more fields (session_id,
 *  transcript_path, etc.) — only fields this probe uses are listed. Shape confirmed for Edit
 *  specifically by this slice's own live verification (a real throwaway PreToolUse/Edit hook,
 *  a real Edit call, a real captured payload, 2026-08-23) — old_string/new_string/file_path
 *  presence and the deny-shape schema are independently confirmed for this hook's actual
 *  Edit trigger surface, not merely inherited from the sibling hook's Write-only capture
 *  (domain-boundary-provenance-hook.md §3, 2026-08-22). replace_all was also observed present
 *  on the real Edit envelope and is recorded below though this probe does not currently read it. */
interface ProgressProofHookInput {
  tool_name: string;                 // "Edit" | other (ignored)
  tool_input: {
    file_path: string;
    old_string?: string;
    new_string?: string;
    replace_all?: boolean;
  };
}

interface ProgressProofHookOutput {
  // Deny shape reused from the sibling/first-turn-contract precedent, independently re-verified
  // for this hook's own Edit envelope (see the interface comment above and §12's closed item).
  // One shape covers every denial kind (ambiguous-match
  // denial, C2 mutation-denial by either matching tier, and step-10 proof-fail/timeout-denial) —
  // `reason` is prose in all cases, distinguished only by its text content, not by a separate
  // field. No new top-level field is needed on this output schema: `decision`/`reason` already
  // generalize to "any deny, any cause." The finer-grained distinction (which denial kind
  // occurred, and how the pair was matched) lives in TrackRecordEntry's `proof_status` and
  // `matched_by`, not in the hook's own PreToolUse response.
  decision?: "block";
  reason?: string;
}

interface TrackRecordEntry {
  timestamp: string;                 // ISO 8601 UTC
  session_id: string | null;
  file_path: string | null;
  file_in_scope: boolean | null;
  transitions_found: number | null;
  transitions_verified: number | null;
  matched_by: "slice_id" | "description" | "proof_identity" | null;
              // "slice_id" (NEW, 2026-08-23 — highest priority, checked before description/
              // proof_identity, per §6 step 4a): old-open and new-done candidates share an
              // identical SLICE-ID token. Never resolves to mutation_denied — SLICE-ID equality
              // is sufficient identity evidence regardless of description/PROOF text changes.
              // "description" (primary content-based match — old-open and new-done candidates
              // share the same description segment) or "proof_identity" (secondary content-based
              // match — descriptions differ but PROOF: segment text ties the pair together,
              // always resolves to mutation_denied). null when no matched pair exists (allow with
              // transitions_found: 0) or for an ambiguous_match_denied entry (no single pair was
              // resolved — see proof_status).
  proof_status: "verified_pass" | "verified_fail" | "verified_timeout"
              | "manual_unverified" | "mutation_denied" | "ambiguous_match_denied" | null;
              // last matched pair's/candidate's status, if any denied or verified.
              // "mutation_denied": a matched pair's PROOF: segment and/or description segment did
              // not survive the edit unchanged (§6 step 6, C2, either matching tier) — denied
              // before any proof command was extracted or run. Never produced for a matched_by:
              // "slice_id" pair (§6 step 4a) — SLICE-ID matches have no mutation-deny path.
              // "ambiguous_match_denied": either a description segment (§6 step 5) or, as of
              // 2026-08-23, a SLICE-ID token (§6 step 4a) had more than one old-open or new-done
              // candidate, so identity could not be resolved uniquely — denied before matching was
              // attempted for that description/token. matched_by is null for this status (no
              // single pair was resolved).
  decision: "allow" | "deny" | "probe_error";
  reason: string | null;
  probe_error: string | null;
}
```

## 8. Acceptance Criteria

1. A `PreToolUse` `Edit` targeting a file whose basename does not match `*PROGRESS.md` is always
   allowed, track record shows `file_in_scope: false`.
2. A `PreToolUse` `Edit` to a matched file whose diff contains no candidate lines, or whose
   candidate lines yield no matched pair, is always allowed, `transitions_found: 0`.
3. A matched transition where the new-done candidate has no `PROOF:` marker is always allowed
   (opt-in, §4/§6 step 8) — this covers the case where neither old nor new line ever declared a
   proof command. (The distinct case where the old-open candidate has no `PROOF:` marker but the
   new-done candidate does — a proof added in the same edit that completes the slice — is **not**
   this AC; it is governed by step 8's extraction from the new-done candidate and is covered by
   AC11's dedicated fixture below, not by this unconditional-allow AC.)
4. A matched transition on a slice with a `PROOF:` marker whose command is **not** allowlisted is
   always allowed, and the track record shows `proof_status: "manual_unverified"`.
5. A matched transition with an allowlisted `PROOF:` command that exits 0 is allowed,
   `proof_status: "verified_pass"`.
6. A matched transition with an allowlisted `PROOF:` command that exits non-zero, or times out at
   the inner budget, is **denied**, with a reason naming the slice line, the command, and the exit
   code/timeout plus a stderr tail.
7. **Line-count and line-order independence (rewritten this revision — was "line-count-mismatch
   always allowed," now the stronger, correct property).** An `Edit` whose `old_string`/`new_string`
   differ in line count, and/or whose slice line's position relative to other checkbox lines changes
   between `old_string` and `new_string` (reordering), still correctly detects and verifies (or
   denies) a genuine `[ ]`→`[x]` transition present in that edit — matching is by identity (§6 steps
   4a/6), never by index or line count, so neither a structural edit elsewhere in the same diff nor a
   reordering of the slice line relative to its neighbors causes a real transition to be missed or
   misclassified. (Fixture: `reordering-preserves-detection` — see AC11.)
7a. **SLICE-ID-based matching survives simultaneous description+PROOF mutation (added 2026-08-23,
   the case not closeable before this addition).** A matched pair carrying an identical `SLICE-ID`
   token on both the old-open and new-done candidate is detected and verified even when both the
   description segment and the `PROOF:` segment differ between old and new in the same edit —
   `matched_by: "slice_id"`, no `mutation_denied` outcome, proof extracted from the new-done side and
   allowlist-checked/run normally. (Fixture: `slice-id-match-survives-simultaneous-mutation` — see
   AC11.)
7b. **Absence of SLICE-ID falls back to content-based matching unchanged (regression check, added
   2026-08-23).** A file whose slice lines carry no `SLICE-ID` segment at all behaves identically to
   this hook's pre-SLICE-ID behavior — description-primary, proof-identity-secondary matching, with
   the simultaneous-description+PROOF-mutation case still falling through unmatched exactly as
   documented in §6's residual section. Adopting `SLICE-ID` on other slices in the same file, or in
   other files, has no effect on a slice line that never carries the segment. (Fixture:
   `no-slice-id-falls-back-to-content-matching` — see AC11.)
8. A probe crash, unreadable/malformed allowlist file, or outer wrapper timeout always results in
   allow (fail-open) — verified by a fixture-driven test analogous to the sibling's
   `probe_error` cases.
9. Already-`[x]`-marked slice lines are never inspected by this hook under any circumstance — no
   migration, backfill, or retroactive scan exists in this document, at any layer (resolves Intake
   Open Question 4; an already-`[x]` old line is never an old-open candidate by construction — §6
   step 4 only extracts old-open candidates from lines starting `- [ ]` — so it can never be matched
   as completing this edit).
10. The track-record log is append-only, one JSON line per invocation, writable-failure-tolerant —
    same guarantee as both prior hooks in this cluster.
11. The self-test fixture corpus exercises, at minimum: out-of-scope filename, no-candidate-lines
    edit, transition-no-proof-marker, transition-non-allowlisted-command, transition-allowlisted-
    pass, transition-allowlisted-fail, transition-allowlisted-timeout, multiple-transitions-in-one-
    edit-mixed-outcomes (asserting the whole call denies if any pair denies, per §6 step 11),
    **transition-with-inserted-completion-metadata** (§4's canonical edit shape: checkbox flip plus
    a `COMPLETE ...` segment inserted between the description and an unchanged trailing `PROOF:`
    segment — asserting this IS detected as a matched transition and its `PROOF:` command is
    verified, not silently skipped), **transition-adding-proof-on-completion** (old-open candidate
    has no `PROOF:` segment at all; new-done candidate adds one while flipping the checkbox —
    asserting the description match still succeeds, the PROOF equality check is skipped on the old
    side, and step 8 extracts, allowlist-checks, and runs the new-side `PROOF:` command), **line-
    count-mismatch-with-real-transition** (retained from the prior design, now with a corrected
    expected outcome: `old_string`/`new_string` differ in line count due to an unrelated added or
    removed line elsewhere in the edit, AND the diff also contains a genuine `[ ]`→`[x]` transition
    with a matching-PROOF pair — asserting the transition is still detected and verified, not
    allowed-through-unchecked as the pre-redesign line-count-mismatch rule would have done),
    **reordering-preserves-detection** (NEW, this revision, proves the specific bypass this redesign
    was required to close: `old_string` contains two `- [ ]` slice lines, e.g. `Slice A` with a
    `PROOF:` segment followed by `Slice B` with no `PROOF:` segment; `new_string` contains the same
    two lines with their relative order swapped AND `Slice A` flipped to `- [x]` with its `PROOF:`
    segment unchanged — asserting the transition on `Slice A` is detected and its proof command
    verified regardless of the reordering, i.e. `transitions_found: 1`, `matched_by: "description"`,
    correct `proof_status`), **transition-with-proof-mutation-only** (description segment identical
    old-to-new, `PROOF:` segment differs or is removed — asserting `decision: "deny"`,
    `proof_status: "mutation_denied"`, `matched_by: "description"`, and that the command is never
    executed), **transition-with-description-mutation-only** (NEW, this revision: description
    segment differs old-to-new, `PROOF:` segment identical on both — asserting the secondary
    proof-identity match in §6 step 6 still recognizes and denies this as `proof_status:
    "mutation_denied"`, `matched_by: "proof_identity"`, and that the command is never executed —
    this fixture specifically exercises the matching tier that lets description-only mutation stay
    caught under identity-based matching, not just PROOF-only mutation), **ambiguous-duplicate-
    description-denied** (NEW, this revision, exercises §6 step 5: `old_string` contains two
    `- [ ]` lines with the identical description segment — e.g. two lines both reading
    `- [ ] Slice N: same wording` with different or absent `PROOF:` segments — and `new_string`
    flips one of them to `- [x]` with the same description — asserting `decision: "deny"`,
    `proof_status: "ambiguous_match_denied"`, and that no proof command is executed for either
    candidate), and **duplicate-description-no-completion-allowed** (NEW, this revision, the
    non-ambiguous counterpart: `old_string` contains two `- [ ]` lines sharing a description
    segment, `new_string` leaves both as `- [ ]` — no `- [x]` counterpart exists for that
    description at all — asserting `decision: "allow"`, `transitions_found: 0`, confirming step 5's
    ambiguity rule only fires when a same-description completion claim actually exists, not merely
    because duplicate pending descriptions exist in the file), **slice-id-match-survives-
    simultaneous-mutation** (NEW, 2026-08-23, proves AC7a: `old_string` has a `- [ ]` line with
    `SLICE-ID: slice-09` and `PROOF: pytest tests/test_old.py`, description `Slice 9: old wording`;
    `new_string` has the same line flipped to `- [x]` with `SLICE-ID: slice-09` unchanged, description
    reworded to `Slice 9: new wording (renamed)`, and `PROOF:` changed to `pytest tests/test_new.py`
    — asserting `decision` reflects the allowlisted new command's actual exit code (not a mutation
    denial), `matched_by: "slice_id"`, `proof_status` is `verified_pass`/`verified_fail` per the
    command's exit code, never `mutation_denied`), and **no-slice-id-falls-back-to-content-matching**
    (NEW, 2026-08-23, proves AC7b as a regression check: the identical simultaneous
    description+PROOF-mutation scenario as the fixture above, but with no `SLICE-ID` segment on
    either candidate — asserting the pair falls through as two unmatched candidates exactly as
    documented in §6's residual section, `decision: "allow"`, `transitions_found: 0`, i.e. the
    absence of `SLICE-ID` reproduces this hook's pre-2026-08-23-SLICE-ID-addition behavior
    unchanged). Existing fixtures for genuinely unrelated edits (edits to lines that were never
    `- [ ]` to begin with, edits that touch no checkbox line at all) remain **allow** fixtures —
    unaffected by this revision, since those lines never yield an old-open or new-done candidate in
    the first place.
12. No PROVISIONAL constant in this document (§5's allowlist content, §6's 25s inner timeout, §6's
    30s outer timeout) ships without the `PROVISIONAL — owner: wright` marker already present above;
    forge does not need to add markers this document omitted, only to keep them as it revises the
    values if measurement warrants.

## 9. Integration Boundary — What This Tool Does NOT Get Authority Over

- **Whether a proof command is a good test of "done."** This hook checks that a declared,
  allowlisted command exited 0, nothing more. A `pytest` invocation that asserts nothing meaningful
  passes this check — judging that stays `benchmark`'s job, Frank's job, and a human's, same
  carve-out the sibling hook establishes for citation correctness (§2).
- **Frank's binding gate or `GATE-LOG.md`.** This hook runs independently of, and has no bearing on,
  Frank's spec-gate or forge-gate verdicts. A slice passing this hook is evidence Frank's gate may
  consider; it is not a substitute verdict, and this hook has no mechanism to mark a sprint, a
  `PROGRESS.md` file, or `GATE-LOG.md` itself as complete.
- **Whether a slice must declare a proof command at all.** `PROOF:` is opt-in per §4. This hook
  cannot compel an agent to declare one; that expectation, if any, is set by process (Frank's gate
  criteria, Danny's review) outside this hook's authority.
- **CI.** This is a Claude-Code-session PreToolUse hook, not a CI gate. It has no effect on a direct
  `git commit`, a `PROGRESS.md` edit made outside a Claude Code session, or any edit that doesn't go
  through the `Edit` tool. Retrofitting equivalent coverage into CI is out of this sprint's scope.
- **`Write`-based edits to `PROGRESS.md`.** Per §3's scope note, a whole-file `Write` is not
  inspected — a stated, permanent gap in this v1, not a temporary one.
- **Positional bypass family — CLOSED, 2026-08-23, by redesign (not a patch).** Every prior version
  of this document detected a `[ ]`→`[x]` transition by comparing `old_lines[i]` to `new_lines[i]`
  at the same array index. Frank's spec-gate found, across three supplementary review rounds, that
  this positional assumption produced an unbounded family of bypasses — a line-count mismatch (any
  added/removed line anywhere in the edit) caused the whole edit to be allowed unconditionally
  without inspection, and, most recently, simply reordering the slice line relative to an adjacent
  line while preserving line count caused the same silent miss or a false deny. Patching each
  instance did not converge — closing one variant did not close the next. This revision replaces
  positional matching with **identity-based matching** (§6): candidate slice lines are extracted
  from `old_string` and `new_string` independently and matched to each other by description segment
  (primary) or `PROOF:` segment (secondary, for description-only mutations), never by array index or
  line count. This closes the line-count-mismatch and reordering variants at the root — neither is a
  special case anymore, because the algorithm never depends on position in the first place.
- **`SLICE-ID` adoption (§4) — this hook does not require or retrofit it into any existing
  `PROGRESS.md` file.** `SLICE-ID` is forward-only, per Danny's explicit decision: a new file may
  adopt it from its first slice line onward; an existing file (including this feature's own
  `docs/tooling/progress-md-proof-per-slice-hook/PROGRESS.md` and the sibling
  `docs/tooling/domain-boundary-provenance-hook/PROGRESS.md`) is never required to add it, and this
  hook never proposes, suggests, or mechanically adds one on a file's behalf. A file that never
  adopts `SLICE-ID` continues to be matched by content alone (§6 steps 5-6), unmodified, indefinitely
  — this is accepted, permanent behavior, not a gap pending a future migration.
- **Residual gap, honest and final as of this revision — two variants, distinct causes, one now
  per-slice-conditional rather than universal.** (a) **Two-call mutate-then-flip — universal, not
  narrowed by `SLICE-ID`.** This hook is a pure function of one `PreToolUse Edit` call at a time and
  has no memory of any line's state earlier in the same turn, regardless of whether that line carries
  a `SLICE-ID`. An agent can still mutate a slice's description/`PROOF:` segment (and, if present,
  leave its `SLICE-ID` token unchanged — the token is not expected to change) in one `Edit` while the
  line is still `- [ ]` (no completion claim yet, allowed), then flip the checkbox against the
  already-mutated line in a second `Edit`. In that second call, the old-open candidate already
  carries the mutated content and the *same* `SLICE-ID` token as the new-done candidate — step 4a
  matches them by token, finds nothing to disagree with (a `slice_id` match has no mutation-deny path
  by design), and allows the transition exactly as it would for a legitimate single-edit completion.
  **Tracing why `SLICE-ID` does not close this:** the token's whole purpose is to *never change*, so
  it provides no signal at all about *when*, across how many calls, the content around it changed —
  it answers "is this the same slice" (yes, always, since the token is stable by construction), not
  "did this content change in one suspicious step versus two innocuous ones." This is a residual
  about **cross-call memory** — a property no per-call identity key, `SLICE-ID` included, can supply,
  since the hook has no state persisted between separate `PreToolUse` invocations within a turn. (b)
  **Single-call both-fields-mutated, plus the SLICE-ID-mutation variant it depends on — see §6's
  residual-gap subsection for the full, precise closure statement of record; not restated here.**
  Closed for `SLICE-ID`-carrying lines only when the token itself survives the completing edit
  unchanged; open, unchanged, for slices without one; reopened whenever the SLICE-ID token itself is
  altered or removed alongside description/PROOF changes. This is a residual about **content-identity
  ambiguity within one call**, a different cause from (a)'s cross-call-memory gap — `SLICE-ID` closes
  (b) only under the qualification above and has no bearing on (a)'s cause, which is why (a) survives
  `SLICE-ID` adoption unchanged while (b) does not (subject to that qualification). Closing (a) would
  require either persisting cross-call line-state within a turn or moving detection to a Stop-hook
  full-file comparison against turn-start state, both larger changes than this revision and both
  rejected in §3 for v1 on other grounds; see §12 for both (a) and the SLICE-ID-mutation variant of
  (b), including Danny's decision not to add a deny rule for the latter.
- **Allowlist growth or retrofit scope for other repos.** This document defines the mechanism, the
  syntax, and agent-rig's own v1 allowlist content; it does not decide which repos adopt this next
  or author any other repo's allowlist file.

## 10. Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib (`json`, `os`, `sys`, `fnmatch`, `subprocess`, `datetime`) | matches sibling probe's runtime (no new interpreter requirement) | Probe implementation, consistent with this cluster's zero-third-party-dependency posture |

No new dependency. `subprocess.run(..., shell=True, ...)` is a new *capability* relative to both
prior hooks in this cluster (which never execute anything) but is stdlib, not a new package.

## 11. Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Wrapper/probe split | `.claude/hooks/progress-proof-per-slice.sh` + `scripts/progress_proof_per_slice_probe.py` | Reuses `first-turn-contract-enforcement`'s established shape verbatim, per Intake constraint. |
| Explicit allowlist, non-blocking `manual` fallback for anything outside it | §5, §6 step 9 | Reuses `prompt-router-starter`'s `gate.py` *shape* (allowlisted proofs run and are trusted; anything else stamped manual, never blocks) and the sibling hook's manifest-absent posture — applied to command execution rather than content inspection, with the departure in trust-boundary rationale stated in §5. |
| Identity-based matching (extract-then-match, not diff-by-index) | §6 steps 4-6 | Replaces positional line diffing, which produced an unbounded bypass family under any edit that broke old/new positional correspondence (line-count change, reordering). Extracting candidates independently and matching by a stable content key (description segment, with a proof-segment fallback) makes the algorithm invariant to position and line count by construction, not by special-casing each observed bypass shape. |
| Optional, author-assigned, content-independent `SLICE-ID` segment, checked first when present on both sides | §4, §6 step 4a | Closes the one residual content-based matching cannot close on its own (simultaneous description+PROOF mutation, §6/§9) — an explicit stable-token identity key, forward-only and opt-in per Danny's decision, never retrofitted into existing files. |
| Fail-open on any internal error | §6 | Same posture as both prior hooks in this cluster. |
| Append-only, gitignored track-record log | §6 | Same convention as both prior hooks. |
| Inline em-dash-segmented marker in an existing line format, not a new file | §4 | Matches `PROGRESS.md`'s own established single-line-per-slice convention, confirmed against a real example file rather than assumed. |

**Anti-patterns (do not use):**
- A structured/multi-line block per slice — rejected in §4 with rationale (breaks the file's
  existing single-line convention for one field, complicates extraction).
- Straight reuse of the sibling hook's manifest/glob allowlist artifact for command trust — rejected
  in §5 with rationale (different trust boundary: read-only inspection vs. execution).
- **Positional (index-based) line comparison for detecting a transition — rejected, this revision,
  after producing an unbounded bypass family across three supplementary review rounds (line-count
  mismatch, then reordering).** Replaced by identity-based matching (§6). Any future revision to
  this hook that reintroduces same-index comparison as a detection mechanism, even as an
  optimization or special case, reopens this family and should be treated as a regression, not a
  style choice.
- Realigning `old_string`/`new_string` lines on a count mismatch to guess at a transition, or
  attempting to infer identity from line position at all — both rejected; identity is determined
  solely by description/`PROOF:` segment content (§6), never by where a line sits in the text.

## 12. Open Items Carried to Forge

- **§5's allowlist content, §6's 25s inner timeout, §6's 30s outer timeout** — all explicitly
  PROVISIONAL, owner wright, to be revisited against real declared proof commands and measured
  runtime, per §8 AC12.
- **Envelope-shape re-verification for `Edit` specifically — CLOSED, 2026-08-23.** Forge performed
  the same throwaway-hook live-verification method the sibling used (domain-boundary-provenance-hook
  §3), scoped to `Edit`: a real throwaway `PreToolUse`/`Edit` hook was registered, a real `Edit` call
  made, and the captured payload confirmed `tool_input.old_string`/`new_string`/`file_path` present
  as assumed, plus a previously-unlisted `replace_all: boolean` field (now added to §7's schema).
  The deny-shape schema was confirmed against this same capture. Cleanup of the throwaway hook was
  verified. §7's interface comment now cites this capture directly rather than the sibling's
  Write-only precedent.
- **`shell=True` execution surface.** §6 step 10 runs the declared command through a shell (needed
  to support `&&`-chained multi-command proofs, §4). Forge should confirm no unintended shell
  metacharacter exposure beyond what an allowlisted command author already controls — the allowlist
  (§5) already limits *which* commands run, but does not sanitize the remainder of the command
  string, which is trusted verbatim once the prefix matches. This is an accepted risk for v1 (the
  attacker model is "someone editing this repo's own `PROGRESS.md` file," not an external input
  surface), stated here so it isn't silently assumed safe.
- **Residual gap after the identity-based redesign plus `SLICE-ID` — final count as of
  2026-08-23, two variants, distinct causes, one now conditional on adoption rather than universal
  (supersedes the prior two-item list, which predates `SLICE-ID`).**
  1. **Two-call mutate-then-flip dodge — universal, unaffected by `SLICE-ID` adoption.** A
     description/`PROOF:` mutation applied in one `Edit` call while the line is still `- [ ]`,
     followed by the checkbox flip in a separate `Edit` call, is undetected regardless of whether the
     line carries a `SLICE-ID` — the token is stable by design, so it supplies no information about
     *how many calls* the surrounding content took to change (§9's trace). This hook has no
     cross-call memory within a turn; closing this requires either persisting cross-call line-state
     within a turn or moving detection to a Stop-hook full-file comparison against turn-start state,
     both larger changes than this revision and both rejected in §3 on other grounds for v1.

     **Decision (2026-08-24, Danny): accept as residual, do not build cross-call state tracking.**
     Rationale, applying the same decision framework as item 2 below: this hook's threat model is
     self-honesty, not adversarial security, so fix effort should match that stake, not a default
     maximum-scrutiny posture. This is in fact the *easier* of the two remaining variants — it needs
     no special technique, just two ordinary edits — so closing it while item 2 (which requires
     deliberately mutating multiple fields at once) stays open would spend real design effort
     (persistent cross-call state, a new artifact to keep in sync) closing the easier gap while
     leaving the harder one open, which is backwards. Consistent with this spec's posture elsewhere
     (`Write` gap, `shell=True`, item 2). This is decided, not an open question for forge to resolve.
  2. **Single-call both-fields-mutated dodge — CLOSED, per-slice, for `SLICE-ID`-carrying lines,
     only when the token itself survives the completing edit unchanged; open, unchanged, for lines
     without one; reopened whenever the SLICE-ID token is altered or removed alongside a
     description/PROOF change (§6's residual-gap subsection has the full closure statement of
     record — not restated here). Adoption is forward-only and opt-in, per slice line, per file
     (§4, §9) — this document does not retroactively add `SLICE-ID` to any existing file, including
     this feature's own `PROGRESS.md` or the sibling's.

     **Decision (2026-08-23, Danny): accept the SLICE-ID-mutation variant as residual rather than
     adding a conservative deny-on-vanished/changed-SLICE-ID rule.** Rationale: this hook's threat
     model is self-honesty (a linter against shortcuts), not adversarial security; the two-call
     cross-edit dodge (item 1, above) is already an accepted, strictly easier-to-exploit residual
     that a deny-on-changed-SLICE-ID rule would not close either, so closing this narrower variant
     does not raise the real bar; and a deny rule would cost real false positives on a legitimate
     pattern — deleting a pending slice while completing a different, genuinely-finished slice in
     the same edit, where a SLICE-ID happens to be removed as a side effect of the deletion, not as
     an attempt to dodge the check. Same posture this spec has used consistently elsewhere (the
     `Write` gap, `shell=True`, cross-call statelessness). This is decided, not an open question for
     forge to resolve.
  Forge/Danny should decide whether (1) is worth closing now (cross-call state or a Stop-hook layer,
  both strictly larger design changes than this revision) or accepted as a stated permanent v1 gap
  pending real-world evidence it is being exploited; (2) is decided (above) — accepted as residual,
  not preempted by this document, and not open for forge to revisit absent new information. **The
  line-count-mismatch and reordering variants tracked in the prior revision remain removed from this
  list — both are closed universally by the identity-based redesign (§6, §9) and require no
  `SLICE-ID` or further forge follow-up.**

---

*This document does not self-lock. Per this repo's workflow, it proceeds to Frank's binding
spec-gate and human approval before any status change from DRAFT.*
