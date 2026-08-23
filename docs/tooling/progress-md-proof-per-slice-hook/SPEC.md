# PROGRESS.md Proof-Per-Slice Hook — Tooling Spec (spec-lite)

**Status**: DRAFT
**Mode**: spec-lite (per `docs/tooling/progress-md-proof-per-slice-hook/INTAKE.md` — no Requirements/
UI/Roadmap layering; this single document carries purpose, contract, and acceptance criteria)
**Author**: wright
**Date**: 2026-08-22

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
`[ ]`→`[x]` *transition* is inherently a diff between an old and new state of the same line — a
`Write` (whole-file replacement, no `old_string`) has no old-state line to diff against without the
hook reading the on-disk file itself, which §6 deliberately avoids (same posture as the sibling's
§6 step 4: inspect only what the tool call itself carries, never the on-disk file). A `Write` that
overwrites `PROGRESS.md` wholesale — expected to be rare relative to incremental `Edit` calls, given
every real `PROGRESS.md` example seen this session was edited line-by-line — is not inspected by
this hook. This is a scoped, stated gap (§9), not a silent one.

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
- **Detection consequence (matching rule, defined here and applied verbatim by §6 step 5):** because
  the canonical completing edit *inserts* a metadata segment before `PROOF:` rather than appending
  after it, the detection rule cannot require the new line's full post-checkbox text to have the old
  line's full post-checkbox text as a prefix — that test fails on this document's own worked example
  below. Instead, a transition is recognized by two independent equality checks: (1) the **slice
  description segment** — everything between the checkbox and the first ` — ` on the line, or the
  whole post-checkbox text if there is no ` — ` — must be byte-identical between old and new; (2) if
  the old line carries a `PROOF:` segment, the **`PROOF:` segment** (the literal marker plus command
  text) must also be byte-identical between old and new. Any segment(s) between the description and
  `PROOF:` (e.g. an inserted `COMPLETE ...` segment) are ignored by the match — neither required to
  match nor forbidden from changing. This tolerates the canonical completion edit while still
  refusing to treat an edit that changes the description or swaps out the proof command as the same
  slice's transition.
- Example, matching the real example file's own style:
  `- [ ] Slice 4: Wrapper wiring — PROOF: bash tests/test_progress_proof_wrapper.sh`
  completing to:
  `- [x] Slice 4: Wrapper wiring — COMPLETE 2026-08-22 (15/15 tests) — PROOF: bash tests/test_progress_proof_wrapper.sh`
  This is a detected transition: the description segment (`Slice 4: Wrapper wiring`, ignoring the
  checkbox mark) is identical, the `PROOF:` segment (`PROOF: bash tests/test_progress_proof_wrapper.sh`)
  is identical, and the inserted `COMPLETE 2026-08-22 (15/15 tests)` segment in between is ignored by
  the match.
- **A slice bullet line whose `new_lines[i]` (the post-edit, completed line) carries no `PROOF:`
  marker at all is never proof-checked — allowed unconditionally, same posture as "no manifest" in
  the sibling hook.** This is the *new* line's `PROOF:` status that governs (§6 step 7 checks
  `new_lines[i]`, not `old_lines[i]`) — a slice that never declares a proof command, on either side
  of the edit, is opt-in-skipped. Declaring a proof command is opt-in per slice, not mandatory; this
  hook adds a mechanism, not a new requirement that every slice must satisfy to be marked done.
  (Whether Frank or a human reviewer requires proof commands as a matter of process is out of this
  hook's authority — §9.) **This is distinct from the case where `old_lines[i]` has no `PROOF:`
  marker but `new_lines[i]` does** (a slice completed by adding its proof command in the same edit
  that flips the checkbox) — that case has a `PROOF:` marker on the new line, so it is not
  opt-in-skipped; §6 step 5's equality check has nothing to compare on the old side (skipped), and
  §6 step 7 governs: the newly-present `PROOF:` command on `new_lines[i]` is allowlist-checked and,
  if allowlisted, run — see §6 step 5's parenthetical and AC11's dedicated fixture.
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
also complicate detection (§6's line-pairing approach, below, depends on slice state living on a
single line). The inline marker is the smaller, less invasive addition — consistent with the Intake
's explicit instruction to "propose a concrete, minimal syntax addition to the existing checkbox
format, don't invent a whole new file format."

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

## 6. Hook Behavior (v1, complete)

**Components**, reusing `first-turn-contract-enforcement`'s wrapper/probe split:

| Component | Responsibility | Location |
|---|---|---|
| `progress-proof-per-slice.sh` | Wrapper: capture stdin, invoke probe under bounded timeout, validate output shape, fail-open on any failure mode, own `probe_error` fallback writer | `.claude/hooks/progress-proof-per-slice.sh` |
| `progress_proof_per_slice_probe.py` | Probe: detect `[ ]`→`[x]` transition on a `PROOF:`-carrying slice line from `tool_input.old_string`/`new_string`, check allowlist, run allowlisted proof command under its own inner timeout, decide allow/deny, write track-record line | `scripts/progress_proof_per_slice_probe.py` |
| Allowlist file | §5 schema, loaded and validated before any command is trusted | `docs/tooling/progress-proof-allowlist.json` |
| Self-test fixture corpus | Exercises detection/execution/allowlist logic without depending on a real slice completion | `tests/fixtures/progress_proof_corpus.json` |
| Track-record log | Append-only audit trail, same shape/purpose as the sibling hook's | `docs/tooling/progress-proof-per-slice-track-record.jsonl` (gitignored, per sibling convention) |

**Decision procedure** (probe, pure function of `PreToolUse` stdin — `tool_name`, `tool_input`):

1. If `tool_name` is not `Edit` → allow, track-record entry `decision: "allow"`, `reason: null`.
2. Normalize `tool_input.file_path`'s basename (final path component, no directory resolution
   needed — this check does not depend on repo root the way the sibling's glob match does). If the
   basename does not match `*PROGRESS.md` (fnmatch) → allow, track-record entry `decision: "allow"`,
   `file_in_scope: false`.
3. Read `tool_input.old_string` and `tool_input.new_string`. If either is absent → allow (nothing to
   diff), `decision: "allow"`, `reason: null`.
4. Split both into lines. **If the line counts differ, allow unconditionally — do not attempt to
   realign lines.** A structural edit (lines added/removed) is out of this hook's detection scope;
   attempting to guess which new-line corresponds to which old-line risks a false deny on an
   unrelated structural edit, which is a worse failure mode than missing a same-turn transition
   that happens to co-occur with other edits to the file. Track-record entry `decision: "allow"`,
   `reason: null`, `skip_reason: "line_count_mismatch"`.
5. For each line index `i`, compare `old_lines[i]` and `new_lines[i]` (both stripped of leading
   whitespace only, not markdown markup — checkbox bullets are always `- [ ]`/`- [x]` at the start
   of the stripped line, no heading-style markup stripping needed here unlike the sibling's C1/C2
   detection). A **transition** at line `i` is: `old_lines[i]` starts with `- [ ]` AND
   `new_lines[i]` starts with `- [x]` AND both refer to the same slice, per §4's matching rule
   (defined there, applied here verbatim, not restated with different semantics):
   - Take each line's post-checkbox text (everything after the `- [ ]`/`- [x]` marker, leading
     whitespace trimmed) and split it on the first ` — ` into a **description segment** (before)
     and a **rest segment** (after, absent if there is no ` — `).
   - The description segments of `old_lines[i]` and `new_lines[i]` must be byte-identical.
   - If `old_lines[i]`'s rest segment contains a `PROOF:` marker (§4), extract its `PROOF:` segment
     (the literal marker plus command text, i.e. from `PROOF:` to end of line) from both
     `old_lines[i]` and `new_lines[i]`; these two `PROOF:` segments must be byte-identical. (If
     `old_lines[i]` has no `PROOF:` segment, this equality check has nothing to compare against and
     is skipped — it does **not** mean the transition is allowed unconditionally. Whether the
     transition is ultimately allowed or denied still depends entirely on step 7 below, which
     inspects `new_lines[i]` independently: if `new_lines[i]` also has no `PROOF:` marker, step 7's
     opt-in rule allows it; if `new_lines[i]` *does* carry a newly-added `PROOF:` marker — the
     add-a-proof-while-completing case — step 7 extracts it, and steps 8-9 allowlist-check and run
     it exactly as they would for any other transition's `PROOF:` command, denying on a non-zero
     exit or timeout like any other verified proof. See §4's matching parenthetical and AC11's
     dedicated fixture for this case.)
   - Any segment(s) between the description and the `PROOF:` segment (e.g. an inserted
     `COMPLETE ...` segment, §4's example) are ignored by this match — free to differ between old
     and new, or to be newly introduced in `new_lines[i]`, without breaking the match.
   - This is deliberately not a full-line prefix or equality test: it tolerates the canonical
     completing edit (metadata inserted between description and `PROOF:`) while still requiring the
     description and any existing proof command to survive the edit unchanged. Lines that fail
     either equality check are not a transition and are skipped.
6. If no transition line found in the diff → allow, `decision: "allow"`, `transitions_found: 0`.
7. For each transition line, extract the `PROOF:` marker (§4) from `new_lines[i]` (the completed
   line — checking `new_lines[i]` is required per §4's placement rule, since that is the line as it
   will exist post-edit). **No `PROOF:` marker present → allow this transition** (opt-in, §4).
8. If a `PROOF:` marker is present, extract the command (trailing text after the marker, trimmed).
   Check it against the allowlist (§5), exact-prefix match. **No match → allow, `proof_status:
   "manual_unverified"`, `decision: "allow"`.**
9. If allowlisted, execute the command via `subprocess.run(command, shell=True, cwd=REPO_ROOT,
   timeout=INNER_TIMEOUT)` (§ below for `INNER_TIMEOUT`). Exit code 0 → allow this transition,
   `proof_status: "verified_pass"`. Non-zero exit, or inner timeout → **deny**, `proof_status:
   "verified_fail"` or `"verified_timeout"`.
10. If any transition line in the diff is denied (step 9), the whole edit is denied — a single
    `Edit` call can carry only one transition in the overwhelming common case (`old_string`/
    `new_string` typically scope a single slice line), but the procedure handles the general case:
    **any** denied transition denies the tool call. Reason lists every denied transition (slice
    line text, command, exit code or timeout, stderr tail up to 2000 chars) and the remediation
    ("fix the failing command, or don't mark this slice `[x]` yet").
11. If every transition is allowed (steps 6-9 for each), allow, `decision: "allow"`,
    `transitions_found: N`, `transitions_verified: <count with proof_status verified_pass>`.

**Inner execution timeout: 25s. PROVISIONAL — owner: wright.** No external precedent transfers —
`first-turn-contract.sh`'s 5s bound (measured against its own content-scanning probe, 167ms/85ms) is
for a probe that never executes external commands; this hook's entire job is to execute one. 25s is
a first-pass budget sized to comfortably fit a modest `pytest`/`bash` test-file run (the real example
`PROGRESS.md` file's own slices report suites in the 15-27 test range) without being large enough to
stall a turn indefinitely. Forge must measure this against a real allowlisted proof command's actual
runtime before this value is treated as settled, per the same standard the sibling wrapper's own
5s-measurement comment sets.

**Outer wrapper timeout: 30s. PROVISIONAL — owner: wright**, sized to the inner 25s plus headroom
for the probe's own overhead (allowlist load/validation, line diffing) — not itself measured. Forge
must confirm 30s is sufficient outer slack once the inner 25s figure (above) is itself measured and,
if necessary, revised.

**Fail-open guarantee:** identical posture to both prior hooks in this cluster — a PreToolUse hook
whose only power is to block must, on any internal error (probe crash, allowlist read failure,
malformed output, outer timeout), emit an allow, never a deny. An inner proof-command timeout
(step 9) is **not** a probe error — it is a legitimate deny outcome (the declared proof did not
complete successfully within its budget, same evidentiary weight as a non-zero exit) and is handled
by the probe itself, not the wrapper's fail-open path.

## 7. Data Schemas

```typescript
/** PreToolUse stdin, fields this probe reads. Full envelope has more fields (session_id,
 *  transcript_path, etc.) — only fields this probe uses are listed. Shape confirmed by the
 *  sibling hook's live verification (domain-boundary-provenance-hook.md §3, 2026-08-22) for
 *  the same PreToolUse Edit/Write envelope on this same harness — not re-verified independently
 *  in this document; if PreToolUse's real envelope shape differs for Edit specifically (the
 *  sibling's own live capture covered Write only, per its §3 closing note), that gap is
 *  inherited here and remains open (§12). */
interface ProgressProofHookInput {
  tool_name: string;                 // "Edit" | other (ignored)
  tool_input: {
    file_path: string;
    old_string?: string;
    new_string?: string;
  };
}

interface ProgressProofHookOutput {
  // Deny shape reused from the sibling/first-turn-contract precedent, not independently
  // re-verified for this hook — see §12.
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
  proof_status: "verified_pass" | "verified_fail" | "verified_timeout"
              | "manual_unverified" | null;   // last transition's status, if any denied
  decision: "allow" | "deny" | "probe_error";
  reason: string | null;
  probe_error: string | null;
}
```

## 8. Acceptance Criteria

1. A `PreToolUse` `Edit` targeting a file whose basename does not match `*PROGRESS.md` is always
   allowed, track record shows `file_in_scope: false`.
2. A `PreToolUse` `Edit` to a matched file whose diff contains no `[ ]`→`[x]` transition is always
   allowed, `transitions_found: 0`.
3. A `[ ]`→`[x]` transition where **`new_lines[i]` (the post-edit line) has no `PROOF:` marker**
   is always allowed (opt-in, §4/§6 step 7) — this covers the case where neither old nor new line
   ever declared a proof command. (The distinct case where `old_lines[i]` has no `PROOF:` marker but
   `new_lines[i]` does — a proof added in the same edit that completes the slice — is **not** this
   AC; it is governed by step 7's extraction from `new_lines[i]` and is covered by AC11's dedicated
   fixture below, not by this unconditional-allow AC.)
4. A `[ ]`→`[x]` transition on a slice line with a `PROOF:` marker whose command is **not**
   allowlisted is always allowed, and the track record shows `proof_status: "manual_unverified"`.
5. A `[ ]`→`[x]` transition on a slice line with an allowlisted `PROOF:` command that exits 0 is
   allowed, `proof_status: "verified_pass"`.
6. A `[ ]`→`[x]` transition on a slice line with an allowlisted `PROOF:` command that exits non-zero,
   or times out at the inner budget, is **denied**, with a reason naming the slice line, the command,
   and the exit code/timeout plus a stderr tail.
7. An `Edit` whose `old_string`/`new_string` line counts differ is always allowed
   (`skip_reason: "line_count_mismatch"`) — no attempted realignment.
8. A probe crash, unreadable/malformed allowlist file, or outer wrapper timeout always results in
   allow (fail-open) — verified by a fixture-driven test analogous to the sibling's
   `probe_error` cases.
9. Already-`[x]`-marked slice lines are never inspected by this hook under any circumstance — no
   migration, backfill, or retroactive scan exists in this document, at any layer (resolves Intake
   Open Question 4; see §6 step 5's transition definition, which by construction requires an
   observed `[ ]`→`[x]` edit and cannot match a line that was already `[x]` before this hook existed).
10. The track-record log is append-only, one JSON line per invocation, writable-failure-tolerant —
    same guarantee as both prior hooks in this cluster.
11. The self-test fixture corpus exercises, at minimum: out-of-scope filename, no-transition edit,
    line-count-mismatch edit, transition-no-proof-marker, transition-non-allowlisted-command,
    transition-allowlisted-pass, transition-allowlisted-fail, transition-allowlisted-timeout,
    multiple-transitions-in-one-edit-mixed-outcomes (asserting the whole call denies if any
    transition denies, per §6 step 10), **transition-with-inserted-completion-metadata** (§4's
    canonical edit shape: checkbox flip plus a `COMPLETE ...` segment inserted between the
    description and an unchanged trailing `PROOF:` segment, e.g. `- [ ] Slice N: X — PROOF: cmd`
    completing to `- [x] Slice N: X — COMPLETE ... — PROOF: cmd` — asserting this IS detected as a
    transition and its `PROOF:` command is verified per §6 step 5, not silently skipped), and
    **transition-adding-proof-on-completion** (old line has no `PROOF:` segment at all, e.g.
    `- [ ] Slice N: X`; new line adds one while flipping the checkbox, e.g.
    `- [x] Slice N: X — PROOF: cmd` — asserting §6 step 5's old-side equality check is skipped (no
    old `PROOF:` to compare) but the transition is still detected via the matching description
    segments, and step 7 extracts `PROOF:` from `new_lines[i]`, allowlist-checks it, and runs it —
    denying on non-zero exit/timeout and allowing with `proof_status: "verified_pass"` on success —
    exactly as any other transition's `PROOF:` command would be treated, per the F1 fix above).
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
- **A checkbox-flip edit that also changes the description segment, or that mutates/deletes an
  existing `PROOF:` segment, in the same edit.** §6 step 5's transition detection requires both the
  description segment and (when `old_lines[i]` has one) the `PROOF:` segment to be byte-identical
  between old and new. An edit that flips `[ ]`→`[x]` while *also* rewording the description or
  altering/removing an existing `PROOF:` command fails one of those equality checks, so it is not
  recognized as a transition at all (§6 step 5's closing line: "lines that fail either equality
  check are not a transition and are skipped") — the whole edit is then silently **allowed**, with
  no proof ever run, exactly like any other non-transition edit. This is a real bypass: an agent (or
  a human) can dodge a would-be-failing proof by simultaneously editing the description or dropping
  the `PROOF:` marker in the same `Edit` call that marks the slice complete. **Accepted as a stated
  v1 gap, not closed by new blocking logic** — consistent with this document's minimal-scope-for-v1
  posture elsewhere (§3's `Write` gap, §12's `shell=True` risk acceptance): closing it would require
  a second detection path (recognizing an edit as *attempting* a checkbox-flip-plus-mutation and
  denying it, rather than just failing to recognize it as a clean transition), which is new
  detection surface this v1 deliberately does not add. Forge/process mitigation: this bypass
  requires deliberately co-editing the description or proof text in the same edit as the checkbox
  flip — a reviewer (Frank, human) skimming a diff for exactly this shape is the accepted backstop
  for v1, same as the `Write` gap's reliance on the `Edit`-only convention holding in practice.
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
| Explicit allowlist, non-blocking `manual` fallback for anything outside it | §5, §6 step 8 | Reuses `prompt-router-starter`'s `gate.py` *shape* (allowlisted proofs run and are trusted; anything else stamped manual, never blocks) and the sibling hook's manifest-absent posture — applied to command execution rather than content inspection, with the departure in trust-boundary rationale stated in §5. |
| Fail-open on any internal error | §6 | Same posture as both prior hooks in this cluster. |
| Append-only, gitignored track-record log | §6 | Same convention as both prior hooks. |
| Inline em-dash-segmented marker in an existing line format, not a new file | §4 | Matches `PROGRESS.md`'s own established single-line-per-slice convention, confirmed against a real example file rather than assumed. |

**Anti-patterns (do not use):**
- A structured/multi-line block per slice — rejected in §4 with rationale (breaks the file's
  existing single-line convention for one field, complicates line-pairing detection).
- Straight reuse of the sibling hook's manifest/glob allowlist artifact for command trust — rejected
  in §5 with rationale (different trust boundary: read-only inspection vs. execution).
- Realigning `old_string`/`new_string` lines on a count mismatch to guess at a transition — rejected
  in §6 step 4 (false-deny risk on unrelated structural edits outweighs the missed-detection cost of
  skipping).

## 12. Open Items Carried to Forge

- **§5's allowlist content, §6's 25s inner timeout, §6's 30s outer timeout** — all explicitly
  PROVISIONAL, owner wright, to be revisited against real declared proof commands and measured
  runtime, per §8 AC12.
- **Envelope-shape re-verification for `Edit` specifically.** §7's schema inherits the sibling
  hook's live-verified `Write` envelope shape without an independent `Edit`-specific capture in this
  session (the sibling's own §3 already flags this as its own open gap). Forge should perform the
  same throwaway-hook live-verification method the sibling used, scoped to `Edit`, before treating
  `tool_input.old_string`/`new_string` field presence and the deny-shape schema as fully confirmed
  for this hook's actual trigger surface — this document proceeds on the sibling's precedent as a
  reasonable basis to build against, not as an independent confirmation.
- **`shell=True` execution surface.** §6 step 9 runs the declared command through a shell (needed to
  support `&&`-chained multi-command proofs, §4). Forge should confirm no unintended shell
  metacharacter exposure beyond what an allowlisted command author already controls — the allowlist
  (§5) already limits *which* commands run, but does not sanitize the remainder of the command
  string, which is trusted verbatim once the prefix matches. This is an accepted risk for v1 (the
  attacker model is "someone editing this repo's own `PROGRESS.md` file," not an external input
  surface), stated here so it isn't silently assumed safe.

---

*This document does not self-lock. Per this repo's workflow, it proceeds to Frank's binding
spec-gate and human approval before any status change from DRAFT.*
