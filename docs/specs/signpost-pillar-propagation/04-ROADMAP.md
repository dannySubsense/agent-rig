# Roadmap: Signpost→Pillar Propagation

**Status**: DRAFT — pending Frank spec-gate
**Author**: wright
**Date**: 2026-08-08

## D2 Resolved (Open Item from Architecture)

Read `/home/d-tuned/agent-rig/commands/new-project.md` (source-of-record) in full this session.
Confirmed: the command has **no `.claude/settings.json` step anywhere** in its 13-step sequence —
Step 5 writes `.claude/commands/relay.md` only; no other `.claude/*` file is written or merged.
**Component 3 (SessionStart wiring) is therefore a new write step, not a merge** — Slice 3 below
creates `.claude/settings.json` from scratch, following the same inline-template pattern Step 5
already uses for `relay.md` (construct content, substitute tokens, write via Write tool, verify no
placeholder remains).

Also confirmed source locations for this roadmap's file targets:
- `commands/new-project.md`, `HOMELAB-CLAUDE.md.template`, `MAP-NOT-ROUTE-BRIEFING.md.template`, and
  `ASSERT-CONVENTION.md.template` are all source-of-record at the **agent-rig repo root** (this
  repo), deployed to `~/.claude/{commands,templates}/` per DDR-014's "edit here, then redeploy"
  precedent, formalized for this sprint as Component 11 (Deploy Mechanism, Slice 9 below) — edits
  happen here, never at the deploy location.
- Reference artifacts (Slice 2's deliverable) now exist at agent-rig's own `reference/session_probe.py`
  and `reference/session-start-probe.sh` — written directly, not cited by live path into department-os's
  working tree. department-os's checked-out branch moved after this sprint's docs were drafted, which
  broke an earlier draft's live-path citations (Frank's blind consistency review, 2026-08-08); agent-rig's
  own copy has zero dependency on any consumer repo's branch state. department-os and market-data remain
  cited as historical provenance (where the design was piloted/validated), not as ongoing sources.

---

## Dependency Map

| Unit | Depends On |
|---|---|
| US-9 gate record (Component 10, `ALPHA-REPORT-REVIEW.md`) | — (already satisfied — see Slice 1) |
| Components 4, 5, 7 (practice-only template edits) | US-9 gate record |
| Components 6, 8 (assert/sentinel doc) | US-9 gate record |
| Component 1 (`session_probe.py` generalized) | — (existence-only prerequisite on Slice 1; no
  engineering/content dependency — see Sequence Rule 2) |
| Component 2 (hook wrapper) | Component 1 |
| Component 3 (`new-project.md` settings.json step) | Component 1, 2, D2 resolution (done above) |
| `new-project.md` scaffold steps wired end-to-end | Components 1, 2, 3 |
| Component 9 (`RETROFIT-PROCEDURE.md`) | Components 1-8 finalized (all template text ship-ready) |
| Component 11 (Deploy Mechanism — copy to `~/.claude/`) | Components 1-8 (all edited/created template and command files final) |
| Retrofit pilot (`market_data`, probe-hook items) | Component 9, `new-project.md` slice complete, Component 11 deployed |
| Retrofit remaining roster (practice-only items) | Component 9 (practice items don't need probe pilot to complete first, per architecture's ordering §2) |
| Retrofit remaining roster (probe-hook items) | Successful pilot Frank-gate PASS |

No circular dependencies: the US-9 gate record already exists (satisfied by Slice 1, an
independent Frank dispatch outside this sprint's own authorship chain) so it imposes no wait on any
other slice. Probe-hook components (Slices 2-3) have no dependency on the documentation-only
components (Slices 4-7) or vice versa — they proceed in parallel, sequenced here for reviewability,
not because either blocks the other. The Deploy Mechanism (Slice 9) depends on every file-editing
slice (2-7) being finished, since it copies their final state; it is not gated on Slice 1, only on
the slices that produce the files it copies.

---

## Slice Overview

| Slice | Goal | Depends On | Files |
|---|---|---|---|
| 1 | Independent review of alpha's handoff report recorded (US-9 gate) — already satisfied | — | `docs/specs/signpost-pillar-propagation/ALPHA-REPORT-REVIEW.md` (existing artifact, produced by an independent Frank dispatch) |
| 2 | Generalized probe script + hook wrapper committed as reference artifacts in agent-rig | 1 (existence only) | `reference/session_probe.py`, `reference/session-start-probe.sh` (agent-rig-local staging location — see note) |
| 3 | `new-project.md` scaffolds Components 1-3 into every new project | 1, 2 | `commands/new-project.md` |
| 4 | Session Start Behaviour template gets Signpost:/Pillar: + 3-check block | 1 | `HOMELAB-CLAUDE.md.template` |
| 5 | Map-not-route briefing convention template | 1 | `MAP-NOT-ROUTE-BRIEFING.md.template` (repo root, beside `HOMELAB-CLAUDE.md.template`), `HOMELAB-CLAUDE.md.template` (cross-ref) |
| 6 | Assert-convention + sentinel pattern combined doc | 1 | `ASSERT-CONVENTION.md.template` (repo root; D1: combined file, see below), `HOMELAB-CLAUDE.md.template` (cross-ref) |
| 7 | Capture schema addition (`Verification:`/`Re-verify with:`) | 1 | `HOMELAB-CLAUDE.md.template` (Capture Behaviour section edit) |
| 8 | Retrofit procedure doc | 3, 4, 5, 6, 7 | `docs/specs/signpost-pillar-propagation/RETROFIT-PROCEDURE.md` |
| 9 | Deploy Mechanism (Component 11): copy source-of-record files to `~/.claude/` | 3, 4, 5, 6, 7 | `~/.claude/templates/HOMELAB-CLAUDE.md.template`, `~/.claude/templates/MAP-NOT-ROUTE-BRIEFING.md.template`, `~/.claude/templates/ASSERT-CONVENTION.md.template`, `~/.claude/commands/new-project.md` (deploy targets, overwritten via `cp` from repo-root sources) |
| 10 | Retrofit pilot: `market_data` (probe-hook items, per-project Frank gate) | 8, 9 | `market_data` repo (external to agent-rig — resident agent `alpha` owns) |
| 11 | Retrofit rollout: remaining roster, practice-only items first | 8, 9 (pilot not required for practice-only per architecture §2) | `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`, `sonic-store`, `quant-foundry`, `runtime/agent-lore` repos (each owned by that project's resident agent) |
| 12 | Retrofit rollout: remaining roster, probe-hook items | 10 (pilot Frank-gate PASS required) | same roster as Slice 11, probe-hook components only |

**D1 resolved**: Components 6 and 8 ship as **one combined template file**
(`ASSERT-CONVENTION.md.template`) per architecture's stated rationale (sibling sections in alpha's
source doc, no independent scaffolding logic, avoids a near-empty fourth file). Filename retained
from architecture's Component 6 row; the file's body covers both the assert convention and the
sentinel/observability pattern as two sections.

**Forge-closability**: this sprint's forge phase is closable when Slices 1-9 plus the retrofit pilot
(Slice 10, `market_data`) reach PASS. Slices 11 and 12 (remaining 7-project roster) are explicitly
**non-blocking** — tracked as ongoing, per-project work with no single sprint-wide completion gate
(architecture's Retrofit Mechanism ordering + Requirements US-10's framing).

---

## Slice Detail

### Slice 1: Alpha's Report — Independent Review (US-9 Gate) — Already Satisfied

**Goal:** Confirm a recorded, binding review verdict exists on
`market_data/docs/reports/HANDOFF-2026-08-07-verify-before-assert-what-actually-works.md` before any
downstream slice cites its recommendations as settled.

**Status:** **Already satisfied.** This slice is not new work — `ALPHA-REPORT-REVIEW.md` already
exists as the output of an independent Frank dispatch (per Requirements US-9 AC and Constraint: the
review is performed by Frank, not Wright, and recorded in its own artifact distinct from and not
satisfied by `05-REVIEW.md` — that filename is this sprint's own spec-completeness review of the
requirements/architecture/roadmap doc set, a different document with a different purpose). No
further action is required to close this slice; it is listed here so the Dependency Map and
Sequence Rules have an explicit anchor.

**Depends On:** —

**Files:**
- `ALPHA-REPORT-REVIEW.md` — existing (reviewed by Frank; located in this sprint's own spec
  directory, `docs/specs/signpost-pillar-propagation/`, alongside `05-REVIEW.md` but a distinct
  file — not created or owned by `market_data`).

**Implementation Notes:**
- Reviewer: Frank, per Requirements US-9 and Constraint — not Wright, and not folded into this
  sprint's `05-REVIEW.md`.
- `ALPHA-REPORT-REVIEW.md` records **8 directly-verified claims** (DDR-0009 status, hooks directory,
  `settings.local.json`, single root CLAUDE.md, `assert_gate_date_coupling.py` fail-closed behavior,
  `session_probe.py` read-only/timing, the 2026-06-29 incident, and the repo-vs-live systemd unit
  value), a short **could-not-verify list** (historical live-unit value, the 2026-07-07 incident
  timeline, and how alpha's own briefing was conducted), and **one overall verdict** (`SAFE TO
  CITE`) with **two mandatory caveats** — there is no per-item pass/concerns/rejected verdict table.
  Any item this sprint cites (Components 5, 6, 8, and the Probe Runtime Budget's 3s citation) is
  covered by the 8 verified claims or the overall verdict, not by a separate per-item ruling.
- Any item marked "could not verify" per that list is excluded from Slices 4-6's shipped template
  text — the corresponding template section is either omitted or rewritten without that specific
  claim.
- **Frank's verdict is `SAFE TO CITE` with two mandatory caveats when propagating** (verbatim from
  `ALPHA-REPORT-REVIEW.md`): (a) do not propagate DDR-0009 / hook-based enforcement (retrofit item
  6) as an existing mechanism — the report itself flags this and Frank confirmed the mechanism does
  not exist; any propagated artifact must carry that non-existence status forward, not just the
  recommendation; (b) cite Section 2.5 ("repetition as a diagnostic instrument") as a heuristic, not
  an established pattern — N=1, accidental discovery, self-acknowledged by the report itself. These
  two caveats are not this slice's own Done-When items (this slice only confirms the review record
  exists) — they are checked at the slices that actually produce citing content: see Slice 4, Slice
  5, Slice 6, and Slice 7's own Done-When lists below, and Slice 2's Done-When list for the Probe
  Runtime Budget citation.

**Tests:**
- [x] `ALPHA-REPORT-REVIEW.md` exists and contains 8 directly-verified claims, a could-not-verify
      list, and one overall `SAFE TO CITE` verdict with two mandatory caveats — not a per-item
      verdict table.

**Done When:**
- [x] Review record exists and is referenced by file path (`ALPHA-REPORT-REVIEW.md`).
- Note: the forward-looking constraint "no downstream slice ships template text citing a
  rejected/unverified item" is **not** a Slice 1 completion criterion — it cannot be true or false
  until Slices 2, 4, 5, 6, 7 actually ship content, and pre-checking it here would assert a property
  of work not yet performed. That check now lives, unchecked, on each citing slice's own Done-When
  list (Slice 2, Slice 4, Slice 5, Slice 6, Slice 7), to be verified when that slice actually
  completes.

---

### Slice 2: Generalized Probe Script + Hook Wrapper (Reference Artifacts) — SATISFIED

**Status:** Already satisfied (2026-08-08). `reference/session_probe.py` and
`reference/session-start-probe.sh` exist in agent-rig, written directly (not cited by live path into
any consumer repo), generalized from the department-os pilot with the `timeout=15` fix already
applied per this slice's own Done-When criteria. Listed here so the Dependency Map and later slices
(3+) have an explicit anchor, same pattern as Slice 1.

**Goal (met):** Produce the generalized, domain-neutral `session_probe.py` and its
`session-start-probe.sh` wrapper as reviewable artifacts in agent-rig, before wiring them into
`new-project.md`.

**Depends On:** Slice 1 (existence only — no engineering/content dependency; Slices 2-3 generalize
department-os's own code with no exposure to alpha's report; see Sequence Rule 2)

**Files:**
- `reference/session_probe.py` — create (agent-rig-local staging copy; this is the artifact
  `new-project.md`'s new scaffold step will write verbatim into each new project's
  `scripts/session_probe.py` — staging it here first makes the diff reviewable independent of the
  command-file edit in Slice 3).
- `reference/session-start-probe.sh` — create (same staging rationale; written into each new
  project's `.claude/hooks/session-start-probe.sh` by Slice 3).

**Implementation Notes:**
- (Done) Based directly on department-os's piloted `scripts/session_probe.py` and
  `.claude/hooks/session-start-probe.sh` — per architecture, these were already domain-neutral
  (git + docs only, no DuckDB/table logic). Generalization work was confirming no
  department-os-specific strings remained (project name references, hardcoded paths); no logic
  rewrite was needed. Files now live at agent-rig's own `reference/` — see Status note above.
- Apply the 5s PROVISIONAL soft budget (architecture's Probe Runtime Budget section) as a
  `timeout 5` wrap at the hook-script level — this is the **sole** enforcement point, per
  architecture's resolution of the inner-timeout question (02's Probe Runtime Budget + API Contract
  sections). **Drop** `session_probe.py`'s inner `timeout=15` kwarg on its `_run()` subprocess
  helper: it is unreachable dead code under the outer `timeout 5` wrap (a 15s inner cap can never
  fire — the outer wrap kills the process at 5s first). Simplify the `subprocess.run(...)` call
  inside `_run()` to drop the `timeout=` argument entirely, not comment it out or leave it dormant.
- Corroborating evidence for the 5s ceiling: Frank's independent review (`ALPHA-REPORT-REVIEW.md`)
  measured `session_probe.py` end-to-end at **0.7s** against a live DB — a Pillar-level measurement
  corroborating alpha's ~3s Signpost-level estimate and confirming the 5s PROVISIONAL budget is
  generous (~7x headroom over the measured runtime), not merely resting on the report's own figure.
- Preserve the four-element `additionalContext` composition order from architecture's Data Schemas
  section exactly (self-disclaimer → probe output → blank-line separator → action-required
  directive naming `search_knowledge`).
- Read-only git/filesystem operations only — no new operations beyond department-os's reference.

**Tests:**
- [ ] Manual run of `reference/session_probe.py` in a test git repo produces git state + doc listing
      output with no department-os-specific strings.
- [ ] Manual run of `reference/session-start-probe.sh` produces valid `SessionStartHookOutput` JSON
      on stdout, exits 0, and — on a forced probe failure (e.g. temporarily rename `.git`) — the
      injected `additionalContext` contains the literal `"probe failed: <error>"` pattern, not a
      silent empty payload.

**Done When:**
- [ ] Both files exist under `reference/` and pass the two manual trace checks above.
- [ ] No department-os- or market-data-specific string (project name, table name, DuckDB reference)
      appears in either file.
- [ ] `session_probe.py`'s `_run()` helper contains no `timeout=15` (or any inner timeout) kwarg —
      confirmed by reading the file, not assumed from this note.
- [ ] The 5s budget citation in code comments/docstrings (if any) references both alpha's ~3s and
      Frank's 0.7s measurement, not the ~3s figure alone.
- [ ] No content shipped in this slice cites a recommendation from `ALPHA-REPORT-REVIEW.md` marked
      rejected or unverified (Slice 1's forward-looking check, verified here).

---

### Slice 3: `new-project.md` Scaffolds Components 1-3

**Goal:** `/new-project` writes the generalized probe script, hook wrapper, and a new
`.claude/settings.json` `SessionStart` wiring block into every newly bootstrapped project.

**Depends On:** Slice 1, Slice 2

**Files:**
- `commands/new-project.md` — edit (this repo's source-of-record; deploys to
  `~/.claude/commands/new-project.md` per Slice 9's Deploy Mechanism, not edited directly there).

**Implementation Notes:**
- Per D2 (resolved above): add a **new** write step — no existing `.claude/settings.json` exists in
  the current 13-step sequence to merge into. Insert as a new numbered step (e.g. "Step 6.5 —
  Probe Hook + Session Start Wiring") sequenced alongside Step 5 (Relay Skill) and Step 6
  (MACHINE-SETUP.md Generation), before Step 7 (`.gitignore`) — matching the pattern those steps
  already use (inline content construction, Write tool, zero-placeholder verification, staged in
  Step 12).
- Three writes in the new step: `scripts/session_probe.py` (verbatim copy of Slice 2's reference
  file, no placeholders), `.claude/hooks/session-start-probe.sh` (verbatim copy), and
  `.claude/settings.json` with a `SessionStart` block registering the hook against
  `matcher: "startup|resume|clear"` (architecture's Integration Points section) — this file has no
  existing content to merge with, so it is written fresh, not read-then-merged.
- The `.claude/settings.json` write is **create-only**, not clobbering: on a `/new-project` re-run
  against an already-scaffolded directory, confirm the file does not exist (or does not already
  contain a `SessionStart` block) before writing; do not overwrite a hand-added settings file.
- Add the three new files to the Step 12 staged-files bootstrap list (currently exactly 5 items) —
  update the Fixed Decision Table row and the `git add` command in Step 12 to include
  `scripts/session_probe.py .claude/hooks/session-start-probe.sh .claude/settings.json`.
- Add a HALT/verification check mirroring Step 5's "no placeholder remains" pattern: verify all
  three files exist on disk before Step 7 begins, matching the existing `docs/NORTHSTAR.md`
  precondition-check pattern (Step 5's precondition block).
- Update the Error Reference tables (Halt Conditions, Non-blocking Failures) to include any new HALT
  introduced by this step, matching this file's existing documentation convention exactly.
- **Rollback note** (architecture's "Rollback: `/new-project` Scaffolding" section): this case is
  distinct from the retrofit rollback (Interview Q1, roster of 8, prior-state preservation). For a
  freshly bootstrapped project, rollback is: remove `.claude/hooks/session-start-probe.sh` and
  delete the `SessionStart` block from `.claude/settings.json`. That fully reverts the scaffold — no
  data migration needed, since a freshly bootstrapped project has no prior probe/hook state to
  restore; the scaffold is purely additive. `scripts/session_probe.py` may be left in place (inert,
  no hook invokes it) or deleted alongside; either is a complete rollback.

**Tests:**
- [ ] Dry-run a `/new-project` bootstrap (or trace an existing test bootstrap) and confirm, via file
      listing, that `scripts/session_probe.py`, `.claude/hooks/session-start-probe.sh`, and
      `.claude/settings.json` all exist in the scaffolded project root.
- [ ] Confirm all three new files appear in the Step 12 staged/committed set (`git show --stat` on
      the bootstrap commit).
- [ ] Confirm `.claude/settings.json` is valid JSON and contains the `SessionStart` matcher block.
- [ ] Confirm the rollback procedure above (removing the hook file and `SessionStart` block) leaves
      no scaffold trace beyond an optionally-inert `session_probe.py`.
- [ ] Byte-equality check: `diff reference/session_probe.py <scaffolded-project>/scripts/session_probe.py`
      and `diff reference/session-start-probe.sh <scaffolded-project>/.claude/hooks/session-start-probe.sh`
      both produce zero output — the inline content `new-project.md` actually writes must be
      byte-identical to Slice 2's staged `reference/` copy, not merely "based on" it, so the two
      cannot silently drift apart.

**Done When:**
- [ ] `commands/new-project.md` diff reviewed and contains the new step, updated Fixed Decision
      Table, updated Step 12 file list, and updated Error Reference tables.
- [ ] The three dry-run tests above pass.
- [ ] No placeholder token remains unresolved in any of the three written files.
- [ ] The byte-equality diff check above passes with zero output for both staged files.

---

### Slice 4: Session Start Behaviour Template — Signpost:/Pillar: + 3-Check Block

**Goal:** `HOMELAB-CLAUDE.md.template`'s `## Session Start Behaviour` section documents the
Signpost:/Pillar: labeling convention and absorbs the pre-existing "3-check" DDR-INDEX backlog item
(LORE / Switchboard / git) into the same edit.

**Depends On:** Slice 1

**Files:**
- `HOMELAB-CLAUDE.md.template` — edit (`## Session Start Behaviour` section).

**Implementation Notes:**
- Source text: this repo's own `CLAUDE.md` "Session Start Behaviour" section (the 3-check pattern
  already lives there) plus department-os's Signpost:/Pillar: convention text, per architecture's
  Reference Implementation Provenance table.
- Preserve the noted key property unchanged: Switchboard inbox check fires once at cold start, not
  on compaction/mid-session (architecture's Backlog Reconciliation section, explicit instruction).
- Every claim in a first-turn summary must be labeled **Signpost:** or **Pillar:**, with
  **Pillar:**-labeled claims stating verification method — mirror Requirements US-4 ACs verbatim
  into the template's checkable-requirement language.
- This edit closes DDR-INDEX's "Template tier: promote the 3-check session-start block"
  (2026-07-20) backlog item — note in the commit/capture that this backlog item is now resolved by
  this slice, not left open in parallel.

**Tests:**
- [ ] Template renders (placeholder-substitution dry run against a fresh `InputBundle`) with no
      broken cross-references.
- [ ] Manual read-through confirms both the Signpost:/Pillar: convention and 3-check block are
      present in the same section, matching architecture's Component 4 target.

**Done When:**
- [ ] `HOMELAB-CLAUDE.md.template` diff reviewed and merged.
- [ ] DDR-INDEX's 3-check promotion backlog item marked resolved (cross-reference this slice).
- [ ] No content shipped in this slice presents hook-based/automated enforcement (DDR-0009-style) as
      an existing mechanism — any reference to it is explicitly labeled practice-only convention
      (Frank's mandatory caveat (a) from `ALPHA-REPORT-REVIEW.md`).

---

### Slice 5: Map-Not-Route Briefing Convention Template

**Goal:** A standalone, checkable template documents the map-not-route checker-briefing
convention, cross-referenced from `HOMELAB-CLAUDE.md.template`.

**Depends On:** Slice 1

**Files:**
- `MAP-NOT-ROUTE-BRIEFING.md.template` — create at the **agent-rig repo root** (beside
  `HOMELAB-CLAUDE.md.template`), per architecture's Component 11 (Deploy Mechanism) source-of-record
  location — not under a `templates/` subdirectory.
- `HOMELAB-CLAUDE.md.template` — edit (add cross-reference).

**Implementation Notes:**
- Structure: objective + architecture + what's-claimed sections; structurally omits the briefing
  author's own checklist/method/suspicions — per Requirements US-5 ACs, both properties are
  independently testable (presence of the three required sections, absence of a
  checklist/method/suspicions section).
- Explicitly note the DDR-INDEX backlog item 25 reconciliation in this file's own text (not just in
  the architecture doc) — Requirements US-5 AC3 requires this reconciliation be "documented as
  either folded-in or kept-separate, not silently absorbed"; carry architecture's "kept separate,
  detection vs. prevention" framing into the template's own preamble so a future reader of the
  template alone (without the architecture doc) sees the distinction.
- **Citation caveat (Frank, `ALPHA-REPORT-REVIEW.md`):** if this template's text references
  DDR-0009 or any hook-based/automated enforcement mechanism, it must be labeled explicitly as
  practice-only convention — DDR-0009 is `PROPOSED / QUEUED (not started)`, confirmed by Frank, and
  no hook enforcement exists for this convention. Do not present it as an existing mechanism.

**Tests:**
- [ ] Template file contains exactly the three required sections (objective, architecture,
      what's-claimed) and no checklist/method section.
- [ ] Template's preamble states the DDR-INDEX item 25 reconciliation explicitly.

**Done When:**
- [ ] Both files' diffs reviewed and merged.
- [ ] No content shipped in this slice presents hook-based/automated enforcement (DDR-0009-style) as
      an existing mechanism — any reference to it is explicitly labeled practice-only convention
      (Frank's mandatory caveat (a) from `ALPHA-REPORT-REVIEW.md`).
- [ ] No content shipped in this slice cites a recommendation from `ALPHA-REPORT-REVIEW.md` marked
      rejected or unverified (Slice 1's forward-looking check, verified here).

---

### Slice 6: Assert-Convention + Sentinel Pattern Combined Doc

**Goal:** One combined template documents the `assert_*.py` fail-closed convention and the
sentinel/observability pattern, per D1's resolved combined-file decision.

**Depends On:** Slice 1

**Files:**
- `ASSERT-CONVENTION.md.template` — create at the **agent-rig repo root** (beside
  `HOMELAB-CLAUDE.md.template`), per architecture's Component 11 source-of-record location — not
  under a `templates/` subdirectory. Two sections: assert convention, sentinel pattern.
- `HOMELAB-CLAUDE.md.template` — edit (add cross-reference).

**Implementation Notes:**
- Assert-convention section: document the fail-closed exit-code contract from architecture's API
  Contracts section verbatim (exit 0 only on confirmed determinate match; non-zero on
  mismatch/missing/ambiguous/error; never default-pass on uncertainty). Reference
  `market_data`'s `assert_gate_date_coupling.py` as the worked example by path. State the scope
  boundary explicitly: "applies when a coupling is known," not a blanket mandate (Requirements US-7
  AC3).
- Sentinel section: state "success and failure must produce different bytes" and alpha's F3 lesson
  ("a signal nobody reads is not a control") both explicitly, not implied (Requirements US-8 ACs).
- Both sections cite Slice 1's review record (`ALPHA-REPORT-REVIEW.md`) for any number/claim sourced
  from alpha's report.
- **Citation caveats (Frank, `ALPHA-REPORT-REVIEW.md`), both mandatory if this doc cites the report:**
  (a) do not propagate DDR-0009 or hook-based/automated enforcement as an existing mechanism for
  either the assert convention or the sentinel pattern — both remain practice-only conventions and
  must be labeled as such; (b) if the sentinel/observability section draws on the report's Section
  2.5 ("repetition as a diagnostic instrument"), it must be labeled a **heuristic, not an
  established pattern** — N=1, accidental discovery, self-acknowledged by the report itself.

**Tests:**
- [ ] Assert-convention section states the scope boundary explicitly.
- [ ] Sentinel section states both required principles as literal sentences, not paraphrased away.

**Done When:**
- [ ] Both files' diffs reviewed and merged.
- [ ] No content shipped in this slice presents hook-based/automated enforcement (DDR-0009-style) as
      an existing mechanism — any reference to it is explicitly labeled practice-only convention
      (Frank's mandatory caveat (a)).
- [ ] Any content citing the report's Section 2.5 ("repetition as diagnostic instrument") is labeled
      "heuristic, not established pattern" (Frank's mandatory caveat (b)) — or the section does not
      cite 2.5 at all.
- [ ] No content shipped in this slice cites a recommendation from `ALPHA-REPORT-REVIEW.md` marked
      rejected or unverified (Slice 1's forward-looking check, verified here).

---

### Slice 7: Capture Schema Addition (`Verification:` / `Re-verify with:`)

**Goal:** `HOMELAB-CLAUDE.md.template`'s `## Capture Behaviour` section requires
`Verification:`/`Re-verify with:` lines on every durable capture.

**Depends On:** Slice 1

**Files:**
- `HOMELAB-CLAUDE.md.template` — edit (`## Capture Behaviour` section).

**Implementation Notes:**
- Guidance-only change (per architecture: LORE's capture API/schema is `agent-lore`'s lane, not this
  repo's — this edits the documented convention agents follow when calling `capture_memory`'s
  free-text fields, not the MCP schema itself).
- Add both lines as required alongside the existing `documentType`/`epistemicType`/`status`/
  `supersedesId` guidance already in the template's Capture Behaviour section.
- This repo's own `CLAUDE.md` Capture Behaviour section may also be updated for dogfooding
  consistency — optional, not blocking this slice's Done criteria (this repo's own CLAUDE.md is
  gitignored/local, per this repo's existing precedent).

**Tests:**
- [ ] Template's Capture Behaviour section, read in isolation, states both lines as required.

**Done When:**
- [ ] `HOMELAB-CLAUDE.md.template` diff reviewed and merged.
- [ ] No content shipped in this slice presents hook-based/automated enforcement (DDR-0009-style) as
      an existing mechanism — any reference to it is explicitly labeled practice-only convention
      (Frank's mandatory caveat (a) from `ALPHA-REPORT-REVIEW.md`).

---

### Slice 8: Retrofit Procedure Doc

**Goal:** `RETROFIT-PROCEDURE.md` exists as the copyable, executable per-project cutover checklist
each resident agent runs, reflecting the now-finalized Components 1-8 template text.

**Depends On:** Slices 3, 4, 5, 6, 7 (must be forge-complete and finalized first — per Intake item 7
and this task's explicit sequencing instruction: retrofit does not start until new-project/template-
facing components are finalized).

**Files:**
- `docs/specs/signpost-pillar-propagation/RETROFIT-PROCEDURE.md` — create.

**Implementation Notes:**
- Transcribe architecture's "Per-Project Cutover Procedure (Component 9, RETROFIT-PROCEDURE.md)"
  six-step sequence verbatim (blast-radius audit → install → remove → trace-verify → dispatch
  unbriefed Frank gate → record `RetrofitAuditRecord`).
- Include the `RetrofitAuditRecord` TypeScript-shape schema from architecture's Data Schemas section
  as a literal block resident agents can fill in.
- State explicitly: each resident agent copies/executes this doc in their own repo; it is not
  imported as a dependency (architecture's stated non-goal — no symlink/submodule).
- Include the ordering rule from architecture's Retrofit Mechanism section: practice-only items
  (4, 5, 7) proceed per-project immediately; probe-hook items (1-3) wait for pilot Frank-gate PASS.

**Tests:**
- [ ] Doc contains all six procedure steps and the `RetrofitAuditRecord` schema, matching
      architecture verbatim (no drift from the architecture doc's specified content).

**Done When:**
- [ ] `RETROFIT-PROCEDURE.md` exists and is reviewed.
- [ ] Slices 3-7 are all independently Done (verified against their own Done-When lists, not
      assumed complete because this slice started).

---

### Slice 9: Deploy Mechanism (Component 11) — Copy Source-of-Record to `~/.claude/`

**Goal:** Every source-of-record file this sprint edited or created at the agent-rig repo root
(`HOMELAB-CLAUDE.md.template`, `MAP-NOT-ROUTE-BRIEFING.md.template`, `ASSERT-CONVENTION.md.template`,
`commands/new-project.md`) is live at its deploy target under `~/.claude/`, closing the gap between
"edited in agent-rig" and "installed" (DDR-0009's failure mode) — implementing architecture's
Component 11.

**Depends On:** Slices 3, 4, 5, 6, 7 (every slice that edits or creates one of the deployed files
must be independently Done first — this slice copies final state, not intermediate drafts).

**Files:**
- `~/.claude/templates/HOMELAB-CLAUDE.md.template` — overwrite (already exists at deploy target from
  prior sprints).
- `~/.claude/templates/MAP-NOT-ROUTE-BRIEFING.md.template` — create (new file at deploy target).
- `~/.claude/templates/ASSERT-CONVENTION.md.template` — create (new file at deploy target; omitted
  only if D1 is later revisited to bundle into `HOMELAB-CLAUDE.md.template` instead — not expected,
  since D1 is already resolved as combined-file-as-Component-6/8, distinct from the D1 caveat this
  sentence flags for completeness).
- `~/.claude/commands/new-project.md` — overwrite (already exists at deploy target; carries Slice 3's
  edits).

**Implementation Notes:**
- Manual `cp`, no deploy script exists in this repo (confirmed by architecture: only
  `scrub_gate.py`/`scrub-gate-allow.txt` live under `scripts/`, unrelated) — this matches DDR-014's
  own rollout precedent ("edit here, then redeploy — don't edit the installed copy directly").
- Mechanism, per architecture's Deploy Mechanism section:
  1. `cp HOMELAB-CLAUDE.md.template ~/.claude/templates/HOMELAB-CLAUDE.md.template`
  2. `cp MAP-NOT-ROUTE-BRIEFING.md.template ~/.claude/templates/MAP-NOT-ROUTE-BRIEFING.md.template`
  3. `cp ASSERT-CONVENTION.md.template ~/.claude/templates/ASSERT-CONVENTION.md.template`
  4. `cp commands/new-project.md ~/.claude/commands/new-project.md`
- **Verification is diffed, not asserted** — after each copy, run `diff <source> <deploy-target>`
  and confirm zero output (byte-identical). A deploy step that isn't diff-verified reproduces
  exactly the "documented but not installed" failure mode this sprint exists to close.

**Tests:**
- [ ] `diff HOMELAB-CLAUDE.md.template ~/.claude/templates/HOMELAB-CLAUDE.md.template` — no output.
- [ ] `diff MAP-NOT-ROUTE-BRIEFING.md.template ~/.claude/templates/MAP-NOT-ROUTE-BRIEFING.md.template`
      — no output.
- [ ] `diff ASSERT-CONVENTION.md.template ~/.claude/templates/ASSERT-CONVENTION.md.template` — no
      output.
- [ ] `diff commands/new-project.md ~/.claude/commands/new-project.md` — no output.

**Done When:**
- [ ] All four `diff` checks above pass with zero output (byte-identical), not merely "copy command
      ran without error."
- [ ] This slice is complete before Slice 10 (retrofit pilot) begins — the pilot's Frank gate
      exercises the deployed, live template/command surface, not the repo-root source alone.

---

### Slice 10: Retrofit Pilot — `market_data`

**Goal:** `market_data` (resident agent `alpha`) completes the first probe-hook retrofit, replacing
its own domain-specific `session_probe.py` variant with the canonical Components 1-3, verified by
an independent unbriefed Frank gate.

**Depends On:** Slice 8, Slice 9

**Files:** (external to agent-rig; owned by `market_data`'s repo, executed by `alpha`)
- `market_data/scripts/session_probe.py` — replaced by canonical version (or layered per
  architecture's note: `market_data`'s domain-specific checks may become a separate, project-owned
  extension invoked after the generalized probe, not a parameter to it).
- `market_data/.claude/hooks/session-start-probe.sh`, `market_data/.claude/settings.json` — installed.
- `market_data`'s own CLAUDE.md — practice-only sections (4, 5, 7) applied per that project's blast
  radius audit.

**Implementation Notes:**
- This is alpha's own resident-agent-owned work, per Requirements US-10 and this repo's Out of
  Scope ("NOT: a centralized agent-rig-run sweep"). Agent-rig's role here is limited to: confirming
  Slice 8's procedure doc is finalized and Slice 9's deploy is diff-verified, then handing off — not
  executing the audit/cutover itself.
- `market_data` is the recommended (not binding) pilot per architecture's D3 — chosen because alpha
  already has the deepest context and a live-comparison baseline. If `alpha`/Danny select a
  different pilot at execution time, substitute here without re-planning this slice's structure.
- Frank gate for this cutover must be dispatched unbriefed (map-not-route) by `alpha`, from within
  `market_data`'s own session — not by Wright, and not substitutable by this sprint's own spec/forge
  Frank gates.

**Tests:**
- [ ] Live tool-call trace (`--output-format stream-json`) confirms the canonical hook fires and
      `search_knowledge` still fires afterward (priming not masked).
- [ ] Prior `market_data`-local probe variant is confirmed removed (grep for old script path/doc
      references returns zero hits post-cutover).
- [ ] `alpha`'s independently dispatched, unbriefed Frank gate verdict is PASS (binding, no
      conditional pass).

**Done When:**
- [ ] `RetrofitAuditRecord` for `market_data` is captured to LORE with `cutoverComplete: true`,
      `priorVariantRemoved: true`, `frankGateVerdict: "PASS"`, `frankGateUnbriefed: true`.

---

### Slice 11: Retrofit Rollout — Remaining Roster, Practice-Only Items

**Goal:** `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`,
`sonic-store`, `quant-foundry`, `runtime/agent-lore` each apply Components 4, 5, 6, 7, 8 (practice-
only: Signpost/Pillar labeling, map-not-route, capture schema, assert/sentinel doc) via their own
resident agent's blast-radius audit and Frank gate.

**Depends On:** Slice 8, Slice 9 (does not require Slice 10's pilot PASS — practice-only items have
"no engineering dependency" per architecture's Retrofit Mechanism ordering, and can proceed in
parallel with Slice 10).

**Files:** external, per-project, owned by each project's resident agent — no agent-rig file changes.

**Implementation Notes:**
- Each project independently: blast-radius audit → install practice-only template text → remove any
  prior local variant of these practice items → trace-verify → unbriefed Frank gate → record.
- `api-doc-scraper` is explicitly excluded from this roster per Requirements Out of Scope.
- No uniform propagation script — each resident agent executes `RETROFIT-PROCEDURE.md` independently
  in their own repo and on their own timeline; this slice's "Done" is evaluated per-project, not as
  one atomic batch completion.

**Tests:** (per project, from `RETROFIT-PROCEDURE.md`'s own step 4)
- [ ] Trace-verification per project confirms practice-only content is present and no stale
      reference to a prior local variant remains.

**Done When:**
- [ ] Each of the 7 listed projects has its own `RetrofitAuditRecord` captured, independently, with
      `frankGateVerdict: "PASS"` for its own cutover — partial roster completion is expected and
      acceptable as ongoing state, not a blocker to closing this sprint's forge phase (per
      Requirements US-10's framing: each project's cutover is its own checkable unit, not a single
      sprint-wide gate; also see Forge-Closability note in Slice Overview above).

---

### Slice 12: Retrofit Rollout — Remaining Roster, Probe-Hook Items

**Goal:** The same 7-project roster (Slice 11) applies Components 1-3 (probe-hook rollout) once the
pilot (Slice 10) has passed its Frank gate.

**Depends On:** Slice 10 (Frank-gate PASS specifically — architecture's ordering rule: probe-hook
rollout is "piloted in exactly one retrofit-roster project before broader rollout").

**Files:** external, per-project, owned by each project's resident agent.

**Implementation Notes:**
- Same six-step procedure as Slice 10, applied per project, per `RETROFIT-PROCEDURE.md`.
- If Slice 10's Frank gate returns FAIL or HALT, this slice does not proceed — the pilot's findings
  must be resolved and re-gated before any further probe-hook rollout, per this repo's binding
  (non-overridable) Frank verdict discipline.

**Tests:** same shape as Slice 10's, evaluated per project.

**Done When:**
- [ ] Each project's `RetrofitAuditRecord` for probe-hook items shows `cutoverComplete: true`,
      `priorVariantRemoved: true`, `frankGateVerdict: "PASS"`.
- [ ] Partial roster completion at sprint-forge-close is acceptable and expected — same framing as
      Slice 11; per the Forge-Closability note above, this slice does not block sprint forge-close.

---

## Sequence Rules

1. Complete each slice fully (all Done-When items verified against live files, not assumed) before
   starting the next in its dependency chain.
2. Slice 1 (US-9 gate) is already satisfied — it is a status confirmation, not a blocking task, and
   imposes no wait on Slices 2-7. Slices 2-7 are drafted in the numeric order above for
   reviewability, but none of 2-7 blocks another among themselves and none of them (including
   Slices 2/3, which generalize department-os's own code with no exposure to alpha's report) has any
   engineering dependency on Slice 1's content — only on its existence as a completed gate. Slice 2's
   "Depends On" line, the Slice Overview table, and this Dependency Map row all state this the same
   way: **existence-only prerequisite, no content dependency.** Do not, however, ship (merge/finalize)
   any of 4-6's template text before confirming Slice 1's review record exists and covers the
   relevant recommendations, per this sprint's binding US-9 gate constraint.
3. Slice 8 does not start until Slices 3-7 are each independently Done — not merely "in progress" or
   "drafted." Verify each slice's own Done-When list against live files before starting Slice 8.
4. Slice 9 (Deploy Mechanism) does not start until Slices 3-7 are each independently Done, for the
   same reason as Slice 8 — it copies final file state. Slice 9 may run in parallel with Slice 8
   (neither depends on the other), but Slice 10 (retrofit pilot) requires both 8 and 9 complete.
5. Slice 10 (pilot) must reach a Frank-gate PASS before Slice 12 (probe-hook rollout to the rest of
   the roster) starts. Slice 11 (practice-only rollout) does not wait on Slice 10.
6. No centralized agent-rig sweep across Slices 10-12 — each project's resident agent executes
   independently; agent-rig's role ends at handing off a finalized `RETROFIT-PROCEDURE.md` (Slice 8)
   and a diff-verified deploy (Slice 9).
7. Sprint forge-close requires Slices 1-9 plus Slice 10 (pilot) at PASS. Slices 11-12 are non-blocking
   and continue as ongoing state after forge-close.
8. If blocked on any slice → HALT, do not skip ahead to a later slice.
9. No new slices added without human approval.

---

## Deferred (Not This Roadmap)

- Items 4-6 of the Intake's "What Is Missing" list shipping as anything beyond the documentation
  produced in Slices 5-7 — actual per-project *application* (writing a project's own `assert_*.py`)
  happens on that project's own timeline, "when a coupling is known," not scheduled here.
- `api-doc-scraper`'s stale-reference fix — tracked separately per Requirements Out of Scope.
- DDR-INDEX backlog item "prevention layer: gap-lens pre-checks at doer+dispatcher" — kept as a
  separate future DDR per architecture's Backlog Reconciliation section; no slice here addresses it.
- A standing/ongoing monitoring system for probe-masking regressions post-cutover — each retrofit
  gets one trace-verification at cutover time only (Interview Q1); a later regression is a new
  incident, not something this roadmap schedules detection for.
- Lint/CI enforcement of the map-not-route, assert, or sentinel conventions — explicitly an
  anti-pattern per architecture; these remain judgment-applied documentation, not mechanically
  enforced.
- Retrofitting `market_data`'s own domain-specific DB-freshness checks into the generalized probe —
  out of scope; those remain a separate, project-owned layered extension per architecture's API
  Contracts note.
- A general-purpose deploy script for the `~/.claude/` sync (beyond Slice 9's manual `cp`/`diff`
  mechanism) — architecture confirms none exists today and does not scope one for this sprint;
  automating the Deploy Mechanism is future work if the manual pattern proves error-prone.
