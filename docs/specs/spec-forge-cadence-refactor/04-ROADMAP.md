# Roadmap: Spec/Forge Cadence Refactor

**Status**: Draft
**Author**: planner (dispatched by wright)
**Date**: 2026-07-15
**Inputs**: `INTAKE.md`, `INTERVIEW.md`, `01-REQUIREMENTS.md` (12 user stories, 46 ACs), `02-ARCHITECTURE.md` (12 components, 6 schemas — revised post-Frank-FAIL; this roadmap is reconciled to the current version). No `03-UI-SPEC.md` exists or is expected — confirmed no user-facing UI (Interview Q2).

This roadmap slices the architecture's 12 components into 13 ordered, independently verifiable implementation slices. Every slice has a concrete verification method (diff, grep, dry-run, or Danny's manual review) — no slice is "done" on a prose read alone, per this sprint's own stated purpose.

**Note on process bootstrap**: this sprint's own forge execution of this roadmap runs under the *current* (`-03252026`) `forge-start.md` and the *current* (pre-trim) Frank, per `INTAKE.md`'s own Sequencing note — the new packages and trimmed Frank are this roadmap's output, not a precondition for building it. This is a process fact about how the roadmap gets executed, not a slice in it.

---

## Dependency Map

| Slice | Depends On |
|---|---|
| 1 — spec-orchestration scaffold + new templates | — |
| 2 — Interview mechanism artifacts (skill + agent) | 1 |
| 3 — requirements-extraction skill edit | 1 |
| 4 — spec-start.md rewrite | 1, 2, 3 |
| 5 — spec-orchestration install.sh + README | 1, 2, 3, 4 |
| 6 — forge-07152026 scaffold | — |
| 7 — forge-start.md rewrite | 6 (contract parity check against Slice 4) |
| 8 — forge install.sh + QUICKSTART/README | 6, 7 |
| 9 — Frank prose trim (source edit) | — (independent of 1-8; sequenced here per 02-ARCHITECTURE.md's own Sequencing order) |
| 10 — Frank redeploy (sync) | 9 + Danny's explicit approval (manual gate) |
| 11 — Execute install.sh against live `~/.claude` | 5, 8, 10 |
| 12 — One-time grep-verified propagation sweep | 11 |
| 13 — Archive old packages | 12 |

No circular dependencies. Slices 1-5 (spec-orchestration) and 6-8 (forge) have no file overlap and could build in parallel; Slice 9 (Frank) is also file-independent of 1-8 but is sequenced after them here because `02-ARCHITECTURE.md`'s own "Sequencing (this sprint's rollout order)" section lists package-build before the Frank edit, and this roadmap preserves that explicit ordering rather than introducing an independent judgment call. Slices 10-13 are strictly sequential — each is a live, stateful action against `~/.claude` or the repo root that the next slice's verification depends on.

---

## Slice Overview

| Slice | Goal | Depends On | Verification Method |
|---|---|---|---|
| 1 | spec-orchestration-07152026 scaffold: unchanged files copied forward + 4 new templates | — | diff (unchanged files) + schema review (new templates) |
| 2 | Interview mechanism: `interview-conduct` skill + `interview-conductor` agent | 1 | manual review against pseudocode + grep (no `model:` field) |
| 3 | `requirements-extraction/SKILL.md` edit: Step 2 removed, Step 1 rewritten, renumbered | 1 | grep + diff |
| 4 | `spec-start.md` rewrite: Intake gate, Interview contracts, North Star step, Frank binding spec-gate | 1, 2, 3 | manual contract-by-contract review + grep |
| 5 | spec-orchestration `install.sh` version bump + README | 1-4 | diff (version string + README content) |
| 6 | forge-07152026 scaffold: unchanged files copied forward | — | diff |
| 7 | `forge-start.md` rewrite: mandatory Load Governance, Frank binding forge-gate | 6 | manual contract review + grep + structural parity diff vs Slice 4 |
| 8 | forge `install.sh` version bump + QUICKSTART/README | 6, 7 | diff (version string + doc content) |
| 9 | Frank prose trim (`agent-rig/agents/frank.md`) | — | Danny's diff review (blocking gate) + structural-target checks |
| 10 | Frank redeploy (`~/.claude/agents/frank.md`) | 9 + Danny approval | diff (must be empty) |
| 11 | Execute both packages' `install.sh` against live `~/.claude` | 5, 8, 10 | diff (installed files match package) |
| 12 | One-time grep-verified propagation sweep | 11 | 4 grep/diff checks from `02-ARCHITECTURE.md` |
| 13 | Archive `-03242026`/`-03252026` packages | 12 | path existence + untouched-archive check |

---

## Slice Detail

### Slice 1: spec-orchestration-07152026 Scaffold + New Templates

**Goal:** Stand up the new package directory with all unchanged files carried forward byte-for-byte, plus the four new templates that give Intake/Interview/North Star/Gate-Log a checkable shape.

**Depends On:** —

**Files:**
- `spec-orchestration-07152026/agents/architect.md` — copy from `spec-orchestration-03242026/agents/architect.md`, unchanged
- `spec-orchestration-07152026/agents/planner.md` — copy, unchanged
- `spec-orchestration-07152026/agents/requirements-analyst.md` — copy, unchanged
- `spec-orchestration-07152026/agents/spec-reviewer.md` — copy, unchanged
- `spec-orchestration-07152026/agents/ui-spec-writer.md` — copy, unchanged
- `spec-orchestration-07152026/skills/architecture-design/SKILL.md` — copy, unchanged
- `spec-orchestration-07152026/skills/implementation-planning/SKILL.md` — copy, unchanged
- `spec-orchestration-07152026/skills/spec-review/SKILL.md` — copy, unchanged
- `spec-orchestration-07152026/skills/ui-specification/SKILL.md` — copy, unchanged
- `spec-orchestration-07152026/templates/01-REQUIREMENTS-TEMPLATE.md` through `05-REVIEW-TEMPLATE.md` — copy, unchanged
- `spec-orchestration-07152026/templates/INTAKE-TEMPLATE.md` — create (Status: DRAFT | APPROVED | REJECTED contract)
- `spec-orchestration-07152026/templates/INTERVIEW-TEMPLATE.md` — create (per `02-ARCHITECTURE.md` schema: Seed Questions table, Adaptive Follow-ups table, Stopping Rationale)
- `spec-orchestration-07152026/templates/NORTH-STAR-TEMPLATE.md` — create (Declared Intent, In/Out Scope by reference, Success Criteria, Traceability)
- `spec-orchestration-07152026/templates/GATE-LOG-TEMPLATE.md` — create (two `##` sections: Spec Gate, Forge Gate, each with attempt counter and convergence-judgment fields)

**Implementation Notes:**
- Unchanged files must be byte-identical copies, not re-authored — any drift here is an unintended edit.
- New templates must match the exact schema shapes in `02-ARCHITECTURE.md` Data Schemas section, including the `**Status**` line contract for INTAKE and the "Traceability (Layer 2 input — Frank verifies independently, does not trust this field)" framing for NORTH-STAR.

**Done When:**
- [ ] `diff` between each unchanged file and its `-03242026` source returns nothing
- [ ] Each new template file exists and its section headers match `02-ARCHITECTURE.md`'s schema exactly
- [ ] `INTAKE-TEMPLATE.md` contains the literal `**Status**: DRAFT | APPROVED | REJECTED` line

---

### Slice 2: Interview Mechanism Artifacts

**Goal:** Author the gap-diff/stopping-heuristic skill and the subagent-fallback agent contract that `spec-start.md` (Slice 4) will invoke.

**Depends On:** Slice 1 (directory scaffold; templates these artifacts reference)

**Files:**
- `spec-orchestration-07152026/skills/interview-conduct/SKILL.md` — create
- `spec-orchestration-07152026/agents/interview-conductor.md` — create

**Implementation Notes:**
- `SKILL.md` must encode the `gap_diff` and `interview_loop` procedures from `02-ARCHITECTURE.md`'s API Contracts section, including: diffing against both the Intake text AND conversation-since-Intake-approval; the four blind-spot categories (testing/rollback, non-functional, downstream impact, edge cases); the 2-consecutive-non-generative-exchange stop rule; the `stand_in(q)` ASSUMED-stamp procedure with cited rationale requirement; and the "always produce INTERVIEW.md even if zero gaps found" non-skippable requirement.
- `interview-conductor.md` must carry **no `model:` frontmatter field** — this is how "same model as whoever's dispatching" is implemented. This is a hard requirement, not a style choice.
- `interview-conductor.md` must implement the `HALTED — PENDING_HUMAN_INPUT` return contract (never fabricate answers).

**Done When:**
- [ ] `SKILL.md` contains the gap-diff categories, stopping rule, and ASSUMED-stamp format matching `02-ARCHITECTURE.md` verbatim in substance
- [ ] `grep -L "^model:" spec-orchestration-07152026/agents/interview-conductor.md` confirms no `model:` field present
- [ ] `interview-conductor.md`'s return contract includes both the `HALTED — PENDING_HUMAN_INPUT` and `COMPLETE` paths exactly as specified

---

### Slice 3: requirements-extraction Skill Edit

**Goal:** Remove the dead-ceremony embedded clarifying interview (Step 2) from the new package's copy of `requirements-extraction/SKILL.md`, and point Step 1 at the now-guaranteed `INTAKE.md`/`INTERVIEW.md`.

**Depends On:** Slice 1 (package scaffold to hold the edited file)

**Files:**
- `spec-orchestration-07152026/skills/requirements-extraction/SKILL.md` — edit (starts as a copy of `-03242026`'s version, then edited)

**Implementation Notes:**
- Step 2 ("Conduct Clarifying Interview") is **deleted outright**, not commented out — per Requirements US3 AC2 and Architecture's explicit rejection of "present but unused" as recreating dead ceremony.
- Step 1 rewritten to: "Read the approved `INTAKE.md` and `INTERVIEW.md` for this sprint."
- Original Steps 3-8 renumber to 2-7.

**Done When:**
- [ ] `grep -n "Conduct Clarifying Interview" spec-orchestration-07152026/skills/requirements-extraction/SKILL.md` returns nothing
- [ ] `diff` against the `-03242026` source shows only the Step 1 rewrite, Step 2 deletion, and renumbering — no unrelated changes
- [ ] Steps are sequentially numbered 1-7 with no gap or duplicate

---

### Slice 4: spec-start.md Rewrite

**Goal:** Orchestrate the full new spec sequence: mandatory Intake gate → Interview (inline default + subagent fallback) → sprint North Star authoring → 01-05 docs → Frank binding spec-gate loop (GATE-LOG.md + snapshots + independent re-derivation) → human approval.

**Depends On:** Slices 1, 2, 3 (references templates, interview-conduct skill, interview-conductor agent, and the edited requirements-extraction Step 1 wording)

**Files:**
- `spec-orchestration-07152026/commands/spec-start.md` — rewrite (starts as a copy of `-03242026`'s version)

**Implementation Notes:** each of the following, from `02-ARCHITECTURE.md`'s API Contracts, must be present and independently checkable within this one file:
- Step 0: Intake gate — `CHECK: docs/specs/{feature}/INTAKE.md exists AND contains "**Status**: APPROVED"` (case-insensitive), HALT otherwise, before any downstream doc generation.
- Step 1: Interview — inline path is the required default (executed directly by the orchestrating session, no Task-tool dispatch), running `gap_diff` + `interview_loop` from Slice 2's skill; subagent fallback path (`interview-conductor`, `HALT-relay-reinvoke`) documented for the no-live-channel case. Stage always produces `INTERVIEW.md`, even on zero gaps.
- North Star step: sprint North Star authored once (using Slice 1's `NORTH-STAR-TEMPLATE.md`), status `Locked` once Interview closes, not re-edited mid-sequence (escalates to Danny if a change is needed).
- Frank binding spec-gate: `LANE: spec-gate`, reads `SPRINT_NORTH_STAR` + `PROJECT_NORTH_STAR` (path only, never paraphrased) + `GATE_LOG.md` directly; independent 3-attempt counter; PASS/FAIL/HALT loop with no manual override; snapshot-before-retry to `.gate-snapshots/spec/attempt-{N}/`; **Layer 1 (sprint North Star fidelity) and Layer 2 (project North Star relevance) are both evaluated on every attempt (1, 2, and 3 alike), never deferred to the final attempt**; if `docs/NORTH-STAR.md` exists but its `Status` is `DRAFT`, Layer 2 may PASS but is stamped `PROVISIONAL` (the sprint is not blocked on the project North Star reaching non-DRAFT status, but the verdict says so explicitly, and the gate is re-run once it does); at attempt 3, convergence judgment (SHRINKING/STATIC/THRASHING) and the orchestrator's independent re-derivation algorithm (reads `GATE-LOG.md` + snapshot diffs directly, not Frank's recap) before surfacing to Danny; disagreement between orchestrator's read and Frank's diagnosis escalates to Danny with both classifications, without unilateral resolution by either side; a HALT for missing `PROJECT_NORTH_STAR` does not increment the attempt counter.
- Human-approval step: the existing "present all docs for Danny's approval" step explicitly includes `NORTH-STAR.md` alongside `INTAKE.md`, `INTERVIEW.md`, and `01`-`05` — not silently folded into an unnamed "spec docs" category — and presents it alongside Frank's spec-gate verdict (including any `PROVISIONAL` tag, which is never silently dropped at this step).

**Done When:**
- [ ] Step 0 Intake gate matches the CHECK/PASS/FAIL contract verbatim in substance; a missing or non-APPROVED Intake demonstrably HALTs before Step 1 in a manual walkthrough
- [ ] Step 1 inline path is documented as the default; subagent fallback path is documented as fallback-only, with the `HALTED — PENDING_HUMAN_INPUT` relay-and-reinvoke loop spelled out
- [ ] North Star authoring step references `NORTH-STAR-TEMPLATE.md` from Slice 1 and states the "Locked, not re-edited mid-sequence" rule
- [ ] Frank binding spec-gate section includes: independent 3-attempt counter, no-override language, snapshot-before-retry procedure, convergence-judgment-at-attempt-3 procedure, and the orchestrator's independent re-derivation algorithm — all present as concrete procedure text, not summarized as "Frank's gate applies"
- [ ] Layer 1/Layer 2 evaluation is documented as running on **every** attempt (1, 2, and 3), not deferred to attempt 3 — verified by inspecting the contract text for the "evaluated on EVERY attempt" language and by tracing an attempt-1 verdict through both layers in a manual walkthrough
- [ ] The DRAFT-project-North-Star → PROVISIONAL-Layer-2-pass rule is present as concrete procedure text (not summarized), and a manual walkthrough confirms the `PROVISIONAL` tag survives unmodified through to the human-approval step's presentation
- [ ] The human-approval step's text explicitly names `NORTH-STAR.md` as a presented artifact, alongside Frank's spec-gate verdict — verified by grep for an explicit `NORTH-STAR.md` reference in that step's section, not an inference from a general "spec docs" mention
- [ ] `grep` confirms no leftover "if exists" / optional-governance language carried over from the old file for any of these gates

---

### Slice 5: spec-orchestration install.sh + README

**Goal:** Version-bump `install.sh` (no manifest/subtractive logic — that mechanism was cut from `02-ARCHITECTURE.md` as redundant with the dated-package-archive convention, and untested deletion logic against the live shared `~/.claude` surface was assessed as unwarranted risk); update `README.md` to reflect the new sequence and mandatory-Intake rule.

**Depends On:** Slices 1-4 (README documents the full new sequence, so it needs the finished sequence to describe)

**Files:**
- `spec-orchestration-07152026/install.sh` — edit (version bump only; installer behavior otherwise unchanged from `-03242026`)
- `spec-orchestration-07152026/README.md` — edit

**Implementation Notes:**
- `install.sh`'s existing install/overwrite/backup behavior is unchanged — the only edit is the version string. Per `02-ARCHITECTURE.md`'s Propagation Sweep Mechanism, a structural subtractive-install mechanism (diffing a new package's tree against its archived predecessor) is explicitly deferred, not built this sprint: it doesn't trace to a named Intake gap, and this sprint already achieves thoroughness via the one-time grep-verified sweep (Slice 12).
- README updates: new 0-6 step sequence (Intake → Interview → North Star → 01-05 → Frank spec-gate → human approval), mandatory-Intake rule stated as a workflow rule (not sprint-specific), version bump.

**Done When:**
- [ ] `install.sh`'s version string reflects the new package date; `diff` against `-03242026`'s `install.sh` shows only the version-string change
- [ ] README reflects the new sequence and mandatory-Intake rule

---

### Slice 6: forge-07152026 Scaffold

**Goal:** Stand up the new forge package directory with all unchanged agents/skills/templates carried forward byte-for-byte.

**Depends On:** —

**Files:**
- `forge-07152026/agents/code-executor.md`, `doc-writer.md`, `github-ops.md`, `qc-agent.md`, `research.md`, `test-runner.md`, `test-writer.md` — copy from `forge-03252026/agents/`, unchanged
- `forge-07152026/skills/documentation-writing/SKILL.md`, `code-implementation/SKILL.md`, `quality-verification/SKILL.md`, `git-operations/SKILL.md`, `test-execution/SKILL.md`, `technical-research/SKILL.md`, `test-writing/SKILL.md` — copy, unchanged
- `forge-07152026/templates/BINDING-CONTRACT.md`, `CADENCE.md`, `INVARIANTS.md`, `CLAUDE.md` — copy, unchanged

**Done When:**
- [ ] `diff` between each copied file and its `-03252026` source returns nothing

---

### Slice 7: forge-start.md Rewrite

**Goal:** Make `docs/INVARIANTS.md`, `docs/CADENCE.md`, and the sprint's `NORTH-STAR.md` HALT-if-missing (removing the current asymmetric "if exists" wording), and wire in Frank's binding forge-gate using the same contract shape as the spec-gate, run once at feature completion.

**Depends On:** Slice 6 (package scaffold); structural parity against Slice 4's Frank binding-gate contract

**Files:**
- `forge-07152026/commands/forge-start.md` — rewrite (starts as a copy of `-03252026`'s version)

**Implementation Notes:**
- Load Governance, in order, HALT-if-missing on any of: `docs/INVARIANTS.md`, `docs/CADENCE.md`, `docs/specs/{feature}/NORTH-STAR.md`. `CLAUDE.md` stays no-HALT (unchanged behavior).
- Frank binding forge-gate: identical contract shape to the spec-gate (Slice 4) with `LANE: forge-gate`; own independent 3-attempt counter (not shared with spec-gate); same convergence-judgment-at-attempt-3 and independent-re-derivation behavior; same Layer 1/Layer 2-every-attempt evaluation and DRAFT → PROVISIONAL Layer 2 pass logic as the spec-gate (Slice 4); runs once at feature/implementation completion, not per-slice.

**Done When:**
- [ ] `grep -n "if exists"` against the new file returns nothing for CADENCE/INVARIANTS references
- [ ] Manual walkthrough confirms `forge-start` HALTs before any implementation delegation if `INVARIANTS.md`, `CADENCE.md`, or sprint `NORTH-STAR.md` is missing (test each of the three independently)
- [ ] Frank binding forge-gate section, diffed structurally against Slice 4's spec-gate section, shows the same procedure with only `LANE` and cadence (once-at-completion vs. per-doc-cycle) differing
- [ ] Layer 1/Layer 2 evaluation is documented as running on **every** attempt (1, 2, and 3), matching Slice 4's spec-gate requirement exactly — not deferred to attempt 3
- [ ] The same DRAFT-project-North-Star → PROVISIONAL-Layer-2-pass rule from Slice 4 is present in the forge-gate contract text, unmodified from the spec-gate shape

---

### Slice 8: forge install.sh + QUICKSTART/README

**Goal:** Same version-bump-only edit as Slice 5, forge-side; update `QUICKSTART.md` and `README.md` for the mandatory-gate note and version bump.

**Depends On:** Slices 6, 7

**Files:**
- `forge-07152026/install.sh` — edit (version bump only; no manifest/subtractive logic, same rationale as Slice 5)
- `forge-07152026/QUICKSTART.md` — edit
- `forge-07152026/README.md` — edit

**Done When:**
- [ ] `install.sh`'s version string reflects the new package date; `diff` against `-03252026`'s `install.sh` shows only the version-string change
- [ ] QUICKSTART/README reflect the mandatory CADENCE/INVARIANTS/NORTH-STAR gate and Frank binding forge-gate, plus version bump

---

### Slice 9: Frank Prose Trim (Source Edit)

**Goal:** Restructure `agents/frank.md`'s verdict template to exactly `{Findings, Why, Verdict, Fix/Next-step}` (the fourth section's literal header text is `Fix/Next-step (FAIL/HALT only):`), trim ceremony (character/tone/narrative-origin/squash-approve lists), add the two new substantive sections (Layered North Star Check, Loop Convergence Judgment), and leave the five non-negotiable pre-checks and HALT Conditions untouched in substance. This is a source-only edit — no redeploy yet (see Slice 10).

**Depends On:** — (file-independent of Slices 1-8; sequenced here to match `02-ARCHITECTURE.md`'s own stated rollout order)

**Files:**
- `agent-rig/agents/frank.md` — edit

**Implementation Notes (per `02-ARCHITECTURE.md`'s Frank Prose Trim Specification table):**
- Frontmatter: unchanged.
- "Why your mandate looks like this": trim to the shortest statement that still names the postmortem's cause-mechanism-outcome, plus a citation to the postmortem doc (already exists at the cited path) — no sentence-count target, this is an editorial judgment call (matches `02-ARCHITECTURE.md`'s current phrasing for this row, which dropped the earlier unsourced "2-3 sentences" figure).
- "Non-negotiable pre-checks" (5 items): **zero wording changes**.
- "When invoked", "Your review lens", "You do NOT", "HALT Conditions": unchanged in substance (HALT Conditions wording may tighten only).
- "Your character" (5 verbose paragraphs) + "Tone": compress into one compact list.
- "Structure of your verdict": replaced with the four-section template, `Fix/Next-step (FAIL/HALT only):` as the literal fourth header.
- "Things you squash" / "Things you approve quickly": trim each to the shortest list that still names each distinct calibration case — no target count (per `02-ARCHITECTURE.md`'s disposition table, revised to remove the previously-invented "~6 to 3 sharpest" figure as an unsourced editorial number).
- New: "Layered North Star Check (spec-gate/forge-gate only)" — Layer 1/Layer 2 definitions (evaluated every attempt) + the DRAFT/PROVISIONAL rule + missing-project-North-Star HALT.
- New: "Loop convergence judgment (attempt 3)" — SHRINKING/STATIC/THRASHING classification + evidence-format requirement.

**Done When (structural criteria only, per Danny's locked Intake resolution #5 — "the target is structural, not a line count"; matches `02-ARCHITECTURE.md`'s current Measurable Target section exactly, no numeric threshold):**
- [ ] Verdict template structurally conforms to exactly 4 headers — Findings, Why, Verdict, and the literal `Fix/Next-step (FAIL/HALT only):` header — checkable by `grep` for that exact string in a real verdict, present only when Verdict is FAIL/HALT
- [ ] Five pre-checks + HALT Conditions: 0% substance loss — **Danny personally reviews the diff and confirms this himself; not delegated to Frank** (this is a hard blocking gate — Slice 10 cannot proceed without Danny's explicit sign-off on this specific point)
- [ ] The ceremony sections named in the disposition table above are visibly condensed per their stated disposition (e.g. "5 verbose paragraphs" → "one compact list") — checked by reading the disposition table against the actual diff, not a separate numeric threshold
- [ ] The two new substantive sections (Layered Check, Convergence Judgment) are present and are not counted against the shrink target — they are additions, not ceremony being cut

---

### Slice 10: Frank Redeploy (Sync)

**Goal:** Propagate the trimmed `agents/frank.md` to the global dispatch location, only after Danny's explicit approval of Slice 9's diff.

**Depends On:** Slice 9 **and** Danny's explicit approval (manual gate — do not proceed on Slice 9's completion alone)

**Files:**
- `~/.claude/agents/frank.md` — overwrite via `cp`

**Implementation Notes:**
- `cp /home/d-tuned/agent-rig/agents/frank.md ~/.claude/agents/frank.md`
- This step is gated on approval, not run opportunistically alongside the Slice 9 edit — these are two separate steps by design (per task framing and `02-ARCHITECTURE.md` Sequencing item 3).

**Done When:**
- [ ] Danny has explicitly approved the Slice 9 diff (recorded, not assumed)
- [ ] `diff /home/d-tuned/agent-rig/agents/frank.md ~/.claude/agents/frank.md` returns nothing
- [ ] The `subagent_type: frank` invocation signature/contract is unchanged for existing consumers (gap-lens-dilution-filter, d-code, sonic-store, agent-dashboard) — confirmed by inspecting frontmatter/invocation-relevant fields only, not the full prose body

---

### Slice 11: Execute install.sh Against Live `~/.claude`

**Goal:** Run both new packages' `install.sh` for real, installing the new command/skill/agent/template files into the live global dispatch surface (install/overwrite/backup behavior, unchanged from today — only the version strings differ per Slices 5 and 8).

**Depends On:** Slices 5, 8 (install.sh version-bumped), 10 (Frank redeploy done first, per architecture's explicit ordering)

**Files:** none new — this slice executes `spec-orchestration-07152026/install.sh` and `forge-07152026/install.sh` against `~/.claude/{agents,commands,skills,templates}`

**Done When:**
- [ ] `~/.claude/commands/spec-start.md` and `~/.claude/commands/forge-start.md` match the new package versions (`diff` against the package source files returns nothing)
- [ ] `~/.claude/skills/interview-conduct/SKILL.md`, `~/.claude/agents/interview-conductor.md`, and the edited `~/.claude/skills/requirements-extraction/SKILL.md` are present and match their package sources
- [ ] `~/.claude/templates/` contains the four new templates (INTAKE, INTERVIEW, NORTH-STAR, GATE-LOG), matching their package sources

---

### Slice 12: One-Time Grep-Verified Propagation Sweep

**Goal:** Confirm the `~/.claude` sweep is thorough, not additive-only — old references are actually gone, not just superseded by new ones sitting alongside them.

**Depends On:** Slice 11

**Files:** none new — verification-only slice against `~/.claude/{agents,commands,skills}`

**Implementation Notes (the 4 remaining checks from `02-ARCHITECTURE.md`'s Propagation Sweep Mechanism; check 1 there is Slice 11):**
1. `diff /home/d-tuned/agent-rig/agents/frank.md ~/.claude/agents/frank.md` → empty (re-confirms Slice 10 survived the install pass)
2. `grep -rl "03242026\|03252026" ~/.claude/agents ~/.claude/commands ~/.claude/skills` → empty (excluding `~/.claude/history.jsonl`, `~/.claude/projects/**`, `~/.claude/file-history/**` — session logs, explicitly out of scope)
3. `grep -rn "Conduct Clarifying Interview" ~/.claude/skills/requirements-extraction/SKILL.md` → empty
4. Manual diff of old vs. new `~/.claude/commands/spec-start.md` and `forge-start.md` confirming no orphaned old-sequence prose (e.g. leftover "if exists" CADENCE wording) survives the overwrite

**Explicitly not this slice's problem:** `~/.claude/commands/security-loop.md`'s stale reference to the archived `senior-qc` skill is a pre-existing condition, unrelated to this sprint's changes. It is not created by this refactor and does not meet the sweep criteria above (stale `-03242026`/`-03252026` paths, pre-trim Frank prose, pre-Interview-stage skill references). Do not treat it as a blocking finding in this slice.

**Done When:**
- [ ] All 4 checks above pass with the stated (empty) results

---

### Slice 13: Archive Old Packages

**Goal:** Move the now-superseded `-03242026`/`-03252026` packages to their archive locations, matching the existing precedent, without touching already-archived `-03132026` packages.

**Depends On:** Slice 12 (sweep verified complete — follows `02-ARCHITECTURE.md`'s literal Sequencing order, which places archiving after the sweep, not concurrently with it)

**Files:**
- `spec-orchestration-03242026/` → `archive/spec-orchestration-03242026/` (move)
- `forge-03252026/` → `archive/reference/forge-03252026/` (move; note the asymmetric one-level-deeper path, matching the existing `archive/reference/forge-03132026` precedent)

**Done When:**
- [ ] `spec-orchestration-03242026/` and `forge-03252026/` no longer exist at repo root
- [ ] `archive/spec-orchestration-03242026/` and `archive/reference/forge-03252026/` exist with full, unmodified content
- [ ] `archive/spec-orchestration-03132026` and `archive/reference/forge-03132026` show no changes (confirmed via `git status`/`git diff` on those paths)

---

## Sequence Rules

1. Complete each slice fully (all "Done When" items checked) before starting the next slice in its dependency chain.
2. No partial slice work carried forward — a slice is either fully done or not started.
3. If blocked on any slice, HALT and report; do not skip ahead to a dependent slice.
4. Slice 10 requires Danny's **explicit** approval of Slice 9's diff — this is a manual, non-automatable gate. Do not redeploy on the assumption that the trim "looks fine."
5. Slices 11-13 are stateful, live-environment actions (against `~/.claude` and the repo root) — each must be individually verified before the next begins; do not batch them into a single unverified pass.
6. No new slices without human approval.
7. This roadmap's own execution (the forge phase that implements these 13 slices) runs under the *current* `forge-start.md` and *current* Frank — that is a fact about this sprint's own bootstrap, not something any slice needs to implement.

---

## Deferred (Not This Roadmap)

- `03-UI-SPEC.md` — no user-facing UI this sprint (confirmed, Interview Q2).
- `/new-project` bootstrap wiring for project-North-Star creation — Lumen's / `/new-project`'s territory.
- Authoring or finalizing the project-level North Star schema/template itself — `docs/NORTH-STAR.md` is a placeholder pending Lumen's global template, swapped wholesale later, not touched by this roadmap.
- Reconciling gap-lens-dilution-filter's locally-diverged `agents/frank.md` copy — their own call; this sprint's obligation there (the Switchboard message to `beta`) is already discharged per `INTAKE.md`.
- The `franks-lessons` cross-project lessons-learned initiative — needs its own DDR before spec; logged in `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md`.
- Editing already-archived `archive/spec-orchestration-03132026` or `archive/reference/forge-03132026`.
- Fixing `~/.claude/commands/security-loop.md`'s stale `senior-qc` reference — pre-existing, out of this sprint's sweep criteria (noted in Slice 12, not actioned).
- A separate lightweight/fixed-persona model tier for the Interview pass-option path — explicitly rejected by Requirements (reuses whichever model is already conducting the interview).
- A separate counting track for editorial-only vs. substantive loop iterations — folded into the existing convergence read at attempt 3.
- A structural subtractive-install mechanism (diffing a new package's tree against its archived predecessor to compute removals) — cut from `02-ARCHITECTURE.md` as redundant with the dated-package-archive convention and an untested-risk introduction against the live shared `~/.claude` surface; noted there as a future option if ever needed for real, not built this sprint.

---

## Requirements & Architecture Coverage

| User Story | Slice(s) |
|---|---|
| US1 Mandatory Intake Gate | 4 |
| US2 Standalone Interview Stage | 2, 4 |
| US3 Retire Embedded Interview | 3 |
| US4 Sprint North Star | 1, 4 |
| US5 Frank Binding Spec Gate | 4 |
| US6 Mandatory CADENCE/INVARIANTS Gate | 7 |
| US7 Frank Binding Forge Gate | 7 |
| US8 Frank's Prose Trim | 9 |
| US9 Frank Source-to-Dispatch Sync | 9, 10 |
| US10 New Dated Packages | 1, 6, 13 |
| US11 Global Sweep | 5, 8, 11, 12 |
| US12 YAGNI Pressure | all slices (each file traces to a named Intake gap; no speculative additions) |

| Architecture Component | Slice(s) |
|---|---|
| `spec-start.md` (rewritten) | 4 |
| `interview-conduct` skill (new) | 2 |
| `interview-conductor` agent (new) | 2 |
| `requirements-extraction` skill (edited) | 3 |
| `INTAKE-TEMPLATE.md`, `INTERVIEW-TEMPLATE.md` (new) | 1 |
| `NORTH-STAR-TEMPLATE.md` (new) | 1 |
| `GATE-LOG-TEMPLATE.md` (new) | 1 |
| `forge-start.md` (rewritten) | 7 |
| `agents/frank.md` (edited, source-of-record) | 9 |
| `~/.claude/agents/frank.md` (redeploy target) | 10 |
| Sync/redeploy step | 10 |
| One-time grep-verified sweep | 12 |

All 12 architecture components and all 12 user stories map to at least one slice. No component or user story is unaddressed. (Slices 5 and 8's version-bump-only `install.sh` edits are folded into the package-build slices they belong to; this is consistent with the Components table, which no longer lists the manifest-diff installer as a separate row following the Propagation Sweep Mechanism revision.)
