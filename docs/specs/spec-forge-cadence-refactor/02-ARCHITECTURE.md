# Architecture: Spec/Forge Cadence Refactor

**Status**: Draft
**Author**: architect (dispatched by wright)
**Date**: 2026-07-15
**Grounded against**: `spec-orchestration-03242026/commands/spec-start.md`, `spec-orchestration-03242026/skills/requirements-extraction/SKILL.md`, `forge-03252026/commands/forge-start.md`, `agents/frank.md`, `docs/NORTH-STAR.md` (project North Star, DRAFT), and the live `~/.claude/{agents,commands,skills}` surface (confirmed identical to this repo's current vendored packages — install.sh copies by filename, additive/overwrite, never subtractive; this is itself the root of the US11 "additive-only" risk, addressed this sprint via a one-time grep-verified sweep (see Propagation Sweep Mechanism) — a structural subtractive-install upgrade is deferred, not built now).

This document is process/orchestration architecture, not application code. "Components" are files and gate mechanisms; "schemas" are the exact markdown/frontmatter shapes of the artifacts those gates read and write; "API contracts" are the exact Task-tool delegation contracts and HALT-signal shapes.

---

## Overview

Three new gates become load-bearing (mandatory Intake, sprint+project North Star fidelity/relevance, binding Frank verdict) across both packages, plumbed through a shared `GATE-LOG.md` + snapshot mechanism that gives Frank and the orchestrator independent access to primary evidence across loop attempts. A new Interview stage runs inline in the orchestrating session (the session already has the live channel to Danny — this is why it exists) with a documented subagent fallback contract for nested-orchestration cases. Frank's verdict template is restructured to exactly four sections; his five pre-checks and HALT conditions are preserved by leaving that prose untouched and only cutting narrative/character/tone ceremony. Everything lands in new dated packages; propagation to `~/.claude` for this sprint runs through a one-time grep-verified cutover — a structural subtractive-install upgrade (diffing the new package tree against the already-archived old one) is noted as a deferred option, not built this sprint.

---

## Components

| Component | Responsibility | Location |
|---|---|---|
| `spec-start.md` (rewritten) | Orchestrates INTAKE gate → INTERVIEW → NORTH-STAR → 01-05 docs → Frank binding spec-gate → human approval | `spec-orchestration-07152026/commands/spec-start.md` |
| `interview-conduct` skill (new) | Gap-diff seed-question generation + loop-until-dry stopping heuristic + ASSUMED-stamp procedure | `spec-orchestration-07152026/skills/interview-conduct/SKILL.md` |
| `interview-conductor` agent (new, fallback only) | Subagent contract for the HALT-relay-reinvoke path when no inline channel exists | `spec-orchestration-07152026/agents/interview-conductor.md` |
| `requirements-extraction` skill (edited) | Step 2 (embedded clarifying interview) removed; steps renumbered; Step 1 now explicitly reads approved INTAKE.md + INTERVIEW.md | `spec-orchestration-07152026/skills/requirements-extraction/SKILL.md` |
| `INTAKE-TEMPLATE.md`, `INTERVIEW-TEMPLATE.md` (new) | Give Intake/Interview a real checkable shape (status enum) instead of informal prose | `spec-orchestration-07152026/templates/` |
| `NORTH-STAR-TEMPLATE.md` (new) | Sprint-local North Star; authored once by the orchestrator, read (not re-templated) by both Frank gates | `spec-orchestration-07152026/templates/` |
| `GATE-LOG-TEMPLATE.md` (new) | Shared two-section (spec-gate / forge-gate) attempt-counter log | `spec-orchestration-07152026/templates/` |
| `forge-start.md` (rewritten) | HALTs if CADENCE/INVARIANTS/NORTH-STAR missing; runs Frank binding forge-gate once at feature completion | `forge-07152026/commands/forge-start.md` |
| `agents/frank.md` (edited, source-of-record) | Verdict template restructured to `{Findings, Why, Verdict, Fix/Next-step}`; ceremony trimmed; new Layer 1/Layer 2 + convergence-judgment logic added | `agent-rig/agents/frank.md` |
| `~/.claude/agents/frank.md` (redeploy target) | Global dispatch copy; synced only after Danny approves the diff | `~/.claude/agents/frank.md` |
| Sync/redeploy step (new, manual-gated) | `cp` + `diff` verification, gated on Danny's approval | n/a — a procedure, specified below |
| One-time grep-verified sweep (this sprint only) | Removes stale `-03242026`/`-03252026`/pre-trim-Frank/pre-Interview-stage references from `~/.claude` | procedure, specified below |

---

## Data Schemas

### INTAKE.md status contract (formalized — currently informal prose)

```
Required first line after title:
**Status**: DRAFT | APPROVED | REJECTED
```

`spec-start` Step 0 gates on a case-insensitive match of `APPROVED` in that line. Anything else (missing file, `DRAFT`, `REJECTED`, or the line absent entirely) is a HALT before any downstream doc is generated. This is the mechanical, non-vibe form of "Danny approves this INTAKE" — the same rule this very sprint's own `INTAKE.md` was bootstrapped under conversationally, now made checkable by string match instead of memory.

### INTERVIEW.md (durable artifact — template shape)

```markdown
# Interview: {feature-name}
**Status**: Complete | Passed (Danny opted out)
**Mechanism**: Inline | Subagent (interview-conductor, HALT-relay-reinvoke)
**Date**:

## Seed Questions (gap-diff)
| # | Category | Question | Answer | Assumed? |
|---|---|---|---|---|
| 1 | testing/rollback | ... | ... | no |
| 2 | non-functional | ... | ASSUMED — Danny did not answer; based on [precedent] | yes |

## Adaptive Follow-ups
| Triggered by | Question | Answer |
|---|---|---|

## Stopping Rationale
[e.g. "2 consecutive non-generative exchanges after Q5; stopped below the 5-7 anchor."]
```

### NORTH-STAR.md (sprint-local — new template, single authoring point)

```markdown
# Sprint North Star: {feature-name}
**Status**: Locked (set once Interview closes; not re-edited during the doc sequence — a sprint that needs to change its own North Star mid-flight escalates to Danny, it does not silently redefine its target)
**Date**:

## Declared Intent
[As short as it can be while still naming what this sprint is for, in the sprint's own words — length is an editorial judgment call, not a counted target. Must trace to Intake's Problem Statement.]

## In Scope / Out of Scope
[Reference, don't restate: "see 01-REQUIREMENTS.md Out of Scope."]

## Success Criteria (Layer 1 — fidelity)
[What "did the sprint do what it declared, faithfully" looks like, concretely.]

## Traceability (Layer 2 input — Frank verifies independently, does not trust this field)
Project North Star bullet(s) this sprint serves: [cite exact Mission/In-Scope line(s) from docs/NORTH-STAR.md]
Project North Star status at gate time: [DRAFT → Layer 2 verdict is PROVISIONAL PASS, re-run once the project North Star reaches non-DRAFT status | non-DRAFT → normal binding PASS/FAIL, no PROVISIONAL tag]
```

Forge's Frank-gate reads this exact file at `docs/specs/{feature}/NORTH-STAR.md` — no forge-side copy or re-template. The `Status: DRAFT` PROVISIONAL rule exists because `docs/NORTH-STAR.md` (this repo's own project North Star) is itself DRAFT pending Lumen's wholesale swap — a sprint should not be hard-blocked on that external timeline, but the gate must say plainly when its Layer 2 pass is provisional rather than final.

### GATE-LOG.md (shared, two independent counters)

```markdown
# Gate Log: {feature-name}

## Spec Gate
Counter: {N}/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | | FAIL | | .gate-snapshots/spec/attempt-1/ |

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]

## Forge Gate
Counter: {N}/3
[same shape]
```

One file, two `##` sections — avoids two files needing to stay in sync, mirrors the NORTH-STAR "one artifact, one authoring point" decision. Written first by `spec-start` on Frank's first spec-gate invocation; appended to by `forge-start` later. A Frank verdict whose Findings state the *project* North Star document is missing does not increment this counter — that failure mode isn't fixable by retrying the same artifacts, so it HALTs to Danny immediately, outside the attempt mechanism.

### Snapshot directories (new — required for cross-attempt diffing)

```
docs/specs/{feature}/.gate-snapshots/{spec|forge}/attempt-{N}/
```

Populated by the orchestrator immediately before each re-delegation following a FAIL/HALT verdict (copy of the current state of every artifact Frank was gating). Without this, "shrinking vs. static vs. thrashing" and "independently re-derive from primary artifacts" are both unimplementable — the docs get overwritten in place by re-delegation, so there is nothing to diff unless prior states are preserved. Not gitignored; persists for the life of the gate loop, prunable after the gate reaches PASS.

### Frank verdict (US8 — exact structural contract)

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — [artifact name]
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks (terse, one line each): Premise [pass/fail — evidence], Input
  [pass/fail — evidence], Evidence independence [pass/fail — evidence]
- [Substantive findings about the artifact]
- Layer 1: [pass/fail]. Layer 2: [pass/fail — PROVISIONAL if project North
  Star Status is DRAFT — against docs/NORTH-STAR.md directly — HALT if
  that file does not exist. Evaluated on EVERY attempt, not just attempt 3.
- [Loop attempt 3 only] Cross-attempt evidence: which finding recurs, what
  each attempt's diff (via .gate-snapshots) actually touched, and the
  SHRINKING/STATIC/THRASHING classification

Why:
[Root-cause reasoning per finding above — why it's wrong, not just that it is]

Verdict: PASS | FAIL | HALT

Fix/Next-step (FAIL/HALT only):
1. [Location]: [problem] → [required change]
Route to: @[agent]
═══════════════════════════════════════════════════════════════════
```

No content outside these four labeled sections. The five non-negotiable pre-checks (premise, input, evidence independence, standing authority to widen scope, do-not-cite-isn't-a-stop) are unchanged prose in `agents/frank.md` itself — the trim never touches their wording; they're reported *tersely* in Findings, not narrated.

---

## API Contracts

### Contract: spec-start Step 0 — Intake gate (no delegation, orchestrator-only)

```
CHECK: docs/specs/{feature}/INTAKE.md exists AND contains "**Status**: APPROVED" (case-insensitive)
PASS → proceed to Step 1 (Interview)
FAIL → HALT
  Reason: No approved Intake for this sprint
  Blocking: Any downstream doc generation
  Needs: Danny to author/approve INTAKE.md via INTAKE-TEMPLATE.md
```

### Contract: spec-start Step 1 — Interview (inline, default path)

Inline is the required default because the orchestrating session running `/spec-start` *is* the session with Danny's live channel — the same reasoning that made this sprint's own `INTERVIEW.md` work when nothing else existed yet. Delegating this specific stage to a subagent reproduces the exact failure diagnosed in `INTAKE.md` lines 39-41 (isolated dispatch, no live channel, fabrication risk) and gains nothing, since the gap-diff/adaptive-loop process is inherently a multi-turn dialog — running it inline means zero round-trip ceremony; running it via subagent means one dispatch per question round. Procedure (read from `skills/interview-conduct/SKILL.md`, executed directly by the orchestrating session, no Task-tool dispatch):

```
gap_diff(intake, conversation_since_intake_open):
  categories = [testing/rollback, non-functional constraints, downstream
                impact, edge cases not already resolved]
  for category in categories:
    if intake.text already resolves category: skip
    elif conversation_since_intake_open already resolved it:
      skip, but fold the resolution back into INTERVIEW.md as a resolved
      item (durable-artifact requirement — don't silently rely on memory)
    else:
      seed_questions.append(candidate question for category)
  return seed_questions   # target 5-7, soft anchor only

interview_loop(seed_questions):
  non_generative_streak = 0
  for q in seed_questions (or until Danny signals done):
    answer = ask(q)  # or, if Danny opted out: stand_in(q) — see below
    if answer opens a new thread not already covered:
      ask adaptive follow-up(s) on that thread
      non_generative_streak = 0
    else:
      non_generative_streak += 1
    if non_generative_streak >= 2: break  # 2 is the chosen upper end of
      # Danny's 1-2 heuristic (INTERVIEW.md), not a separately-derived number
  write INTERVIEW.md (template above)
```

The stage always runs — even if `gap_diff` returns zero candidates, `INTERVIEW.md` is still produced (`Status: Complete`, empty question table, explicit "no gaps found") so the stage remains a real, non-skippable step rather than reintroducing an "optional in practice" gate.

Pass-option stand-in (`stand_in(q)`): generated by the same model conducting the interview (no separate tier). Every stand-in answer is stamped:
```
ASSUMED — Danny did not answer; based on [named industry pattern/framework precedent]
```
A bare `ASSUMED` flag with no `[rationale]` is a defect in the artifact, not an acceptable output.

### Contract: spec-start Step 1 — Interview (subagent fallback, HALT-relay-reinvoke)

Used only when `/spec-start` itself is invoked from within a context that has no live channel to Danny (e.g. a meta-orchestrator dispatches spec-start as a subagent rather than running it in the live session). `agents/interview-conductor.md` deliberately carries **no `model:` frontmatter field** — it inherits whatever model is dispatching it, which is how "same model as whoever's conducting" is implemented without extra plumbing.

```
DISPATCH @interview-conductor
  INPUTS: INTAKE.md path, conversation summary since Intake approval
  TASK: run gap_diff + generate seed question list only — do not answer
        them, do not fabricate answers under any circumstance
  RETURN: either
    (a) HALTED — PENDING_HUMAN_INPUT
        Questions: [literal list]
        Needs: Danny's real replies
    (b) COMPLETE, INTERVIEW.md written (if DRY on first pass — rare)

ORCHESTRATOR, on receiving (a):
  HALT the session, relay the exact question list to Danny verbatim,
  wait for real replies (this may itself be a live turn-by-turn exchange
  if Danny's answers open new threads)
  RE-INVOKE @interview-conductor with INTAKE.md + running Q&A transcript
  REPEAT until subagent returns COMPLETE (its own 2-non-generative-exchange
  judgment) or Danny explicitly stops
```

Silent fabrication is not an acceptable fallback under either path — this is the one absolute in both contracts.

### Contract: requirements-extraction Step 1 (edited)

Now reads: "Read the approved `INTAKE.md` and `INTERVIEW.md` for this sprint" (both guaranteed to exist by this point in the sequence). Step 2 ("Conduct Clarifying Interview") is deleted outright, not commented out — leaving it present-but-unused recreates the exact dead-ceremony problem this sprint exists to fix. Steps 3-8 renumber to 2-7.

### Contract: Frank binding gate (spec-gate and forge-gate — identical shape, different LANE)

```
TASK: FRANK BINDING GATE — {LANE: spec-gate | forge-gate}
LANE: spec-gate | forge-gate
ATTEMPT: {N} of 3
ARTIFACTS: [paths to all docs / all changed implementation files this attempt]
SPRINT_NORTH_STAR: docs/specs/{feature}/NORTH-STAR.md
PROJECT_NORTH_STAR: docs/NORTH-STAR.md  ← Frank reads this himself; the
                     orchestrator passes the PATH, never paraphrases its
                     content into the contract (checking a document's
                     claim about itself via a summary is a SHARED WELL)
GATE_LOG: docs/specs/{feature}/GATE-LOG.md (prior attempts, if any — read
          directly, don't trust the orchestrator's recap of them either)
SNAPSHOT_DIR: docs/specs/{feature}/.gate-snapshots/{spec|forge}/

OBJECTIVE: Layer 1 (sprint North Star fidelity) AND Layer 2 (project North
Star relevance) must both independently PASS, evaluated on EVERY attempt
(1, 2, and 3 alike) — not deferred to the final attempt. If
PROJECT_NORTH_STAR does not exist: HALT outright, do not evaluate Layer 2
as a pass, do not let a Layer 1 PASS stand in for it. If PROJECT_NORTH_STAR
exists but its Status is DRAFT: Layer 2 may still PASS, but is stamped
PROVISIONAL — the sprint is not blocked on the project North Star reaching
non-DRAFT status, but the verdict must say so explicitly, and the gate
should be re-run once it does.

OUTPUT: Verdict per the four-section template above.
```

Orchestrator loop on receiving the verdict:
```
PASS  → append to GATE-LOG.md, proceed (spec: to human review; forge:
        to @github-ops / PR). A PROVISIONAL Layer 2 pass still counts as
        PASS — not blocking — but the PROVISIONAL tag carries through to
        the human-approval presentation, it is never silently dropped.
FAIL  → snapshot current artifacts to attempt-{N}/, append to GATE-LOG.md,
        route Fix/Next-step items to the named agent(s), re-delegate,
        increment attempt counter, re-invoke Frank
HALT (missing PROJECT_NORTH_STAR)
      → surface to Danny immediately, does NOT increment the counter
HALT (attempt 3, STATIC or THRASHING)
      → orchestrator independently re-derives the diagnosis (below)
        before surfacing anything to Danny
```

No manual override path exists at any FAIL/HALT — this is the literal enforcement of "no conditional pass, no exceptions."

### Algorithm: orchestrator's independent stuck-loop re-derivation (attempt 3, STATIC/THRASHING only)

```
1. Read GATE-LOG.md attempts 1-3 directly (not Frank's verbal recap)
2. Read .gate-snapshots/{lane}/attempt-{1,2,3}/ directly — diff attempt
   N against attempt N-1 for each artifact
3. Classify independently: does the same substantive finding recur
   unchanged (STATIC)? Does each attempt touch different files/issues
   with no convergence (THRASHING)? Are failures shrinking (would have
   been a routine continue, not actually stuck)?
4. Compare own classification to Frank's Findings classification
   AGREE    → escalate to Danny with combined evidence (GATE-LOG entry +
              diff summary + Frank's verdict), Frank's underlying
              PASS/FAIL/HALT stays binding
   DISAGREE → escalate to Danny presenting BOTH classifications
              side-by-side; the disagreement itself is what's surfaced —
              neither the orchestrator nor Frank resolves it unilaterally.
              Frank's quality verdict (not the stuck-loop diagnosis) is
              still binding.
```

This is "pillar not signpost": the orchestrator re-derives the conclusion from `GATE-LOG.md` and the snapshot diffs, it does not re-read Frank's summary a second time and call that verification.

### Contract: spec-start human-approval step (edited)

The existing "Completing a Session" step (present all docs for Danny's approval) must explicitly include `NORTH-STAR.md` alongside `INTAKE.md`, `INTERVIEW.md`, and `01`-`05` — not just the numbered docs, and not silently folded into "the spec docs" as a category. The orchestrator authored `NORTH-STAR.md` itself (see its schema above — single-authoring-point pattern); Frank's Layer 1 check reads it, but the orchestrator is not an independent check on its own output. Danny's eyes on `NORTH-STAR.md` at this same human-approval gate is what supplies that independence — presenting it is not optional, and it is presented alongside Frank's spec-gate verdict (including any PROVISIONAL tag), not instead of it.

### Contract: CADENCE/INVARIANTS/NORTH-STAR gate (forge-start, replaces "Load Governance")

```
Load Governance (all three, in order, HALT-if-missing on any):
  1. CLAUDE.md            — context, no HALT if absent (unchanged)
  2. docs/INVARIANTS.md   — HALT if missing, before any delegation
  3. docs/CADENCE.md      — HALT if missing, before any delegation
     (removes the current "(if exists)" wording — both files are now
     equally mandatory, matching Intake's diagnosis that the asymmetric
     wording was cosmetic, not a real distinction)
  4. docs/specs/{feature}/NORTH-STAR.md — HALT if missing (forge cannot
     run its Frank-gate without the same artifact spec produced)
```

---

## Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Inline stage for human-channel steps | Interview (Step 1) | Only the top-level orchestrating session has Danny's live channel; anything requiring real back-and-forth belongs there, not in an isolated subagent dispatch |
| One artifact, one authoring point | NORTH-STAR.md, GATE-LOG.md | Avoids two templates needing to stay in sync (explicit Danny resolution for North Star; extended to the gate log for the same reason) |
| Snapshot-before-retry | `.gate-snapshots/{lane}/attempt-N/` | Cross-attempt diffing and independent re-derivation are impossible once artifacts are overwritten in place — snapshotting is the only way to make "primary artifacts" durably available |
| Status-enum gate (mechanical, not vibe) | INTAKE.md `**Status**: APPROVED` | Makes "Danny approved this" a string-match, not a memory of a conversation — directly closes the CADENCE/INVARIANTS "if exists" failure shape |
| Distinct HALT variants | `HALTED — PENDING_HUMAN_INPUT` (Interview relay), generic `❌ HALTED` (terminal) | Lets the orchestrator's branch logic tell "relay these questions and loop" apart from "stop the whole sprint" without inventing a new control-flow primitive |

### Anti-Patterns (Do Not Use)

- **Subagent-dispatched Interview as the default path** — reproduces the exact isolated-dispatch failure this sprint's Intake diagnosed as the root cause of the dead `requirements-extraction` Step 2. Fallback-only.
- **Trusting the sprint North Star's own Traceability claim for Layer 2** — this is the literal SHARED WELL failure (checking a document's claim about itself with the same document). Frank reads `docs/NORTH-STAR.md` directly, always.
- **A single global attempt counter across spec + forge** — requirements explicitly call for independent counters per gate; conflating them would let a struggling spec phase silently eat into forge's budget or vice versa.
- **A second counting track for editorial vs. substantive fix iterations** — explicitly rejected (folded into the existing shrinking/static/thrashing read); adding one back would be exactly the kind of incidental ceremony this sprint's YAGNI pressure (US12) exists to prevent.
- **Deferring Layer 1/Layer 2 evaluation to the final loop attempt** — collapses the North Star check into an afterthought that only runs once convergence is already in question; both layers must run on every attempt, or the gate isn't actually load-bearing until the very end.

---

## Dependencies

None. No new libraries — this is markdown/process tooling operating entirely through `Read`, `Write`, `Glob`, `Grep`, `Bash` (`cp`, `diff`, `mkdir`), all already available to every agent/command involved.

---

## Integration Points

- **`spec-orchestration-03242026/` → `spec-orchestration-07152026/`**: full copy forward with the edits above; old folder moves to `archive/spec-orchestration-03242026/` untouched thereafter (mirrors the existing `archive/spec-orchestration-03132026` precedent exactly).
- **`forge-03252026/` → `forge-07152026/`**: same pattern; old folder moves to `archive/reference/forge-03252026/` (mirrors the existing asymmetric `archive/reference/forge-03132026` precedent — forge's archive has always lived one level deeper than spec-orchestration's, this sprint doesn't change that asymmetry).
- **`agents/frank.md` (this repo) ↔ `~/.claude/agents/frank.md`**: today identical (confirmed by `diff`, not assumed). After the trim, sync is a named, gated step — see Sequencing below.
- **`~/.claude/commands/spec-start.md`, `~/.claude/commands/forge-start.md`, `~/.claude/skills/requirements-extraction/SKILL.md`**: confirmed identical to the current vendored packages (`diff` returned no output) — this repo IS the install source; `install.sh` is how they got there and how the new versions will replace them.
- **Consumers (`gap-lens-dilution-filter`, `d-code`, `sonic-store`, `agent-dashboard`)**: none touched directly. All four resolve `/spec-start`, `/forge-start`, and `subagent_type: frank` through the shared `~/.claude` surface, confirmed by grep across all four (only `gap-lens-dilution-filter/notebook-orchestration-04182026/agents/frank.md` carries a local divergent copy, explicitly out of scope per Requirements US11 and already flagged to `beta` via Switchboard).
- **`security-loop.md` (`~/.claude/commands/`)**: observed during the propagation-surface skim to reference "the `senior-qc` skill or the `frank` agent" — `senior-qc` is already archived (`archive/obsolete/senior-qc-skill`), predating this sprint. This is a pre-existing stale reference, not one this sprint's changes create; it does not meet the US11 sweep criteria (stale `-03242026`/`-03252026` paths, pre-trim Frank prose, pre-Interview-stage skill references) and is called out here only as an observation, not a fix obligation — flagging it as a possible follow-up item avoids scope creep into files this refactor didn't touch.
- **`docs/NORTH-STAR.md` (project North Star)**: already exists in this repo (DRAFT, per Lumen-pending placeholder). Frank's Layer 2 check for *this sprint's own* gate reads this exact file and, being DRAFT, produces a PROVISIONAL Layer 2 pass rather than a hard block. Other consuming projects are assumed to have (or will need) their own `docs/NORTH-STAR.md` at the same relative path — this is the interface-contract convention this design adopts, consistent with Requirements' "Assumes" clause treating the project North Star as schema+location to consume, not re-derive.

---

## Package Versioning & Directory Layout

```
spec-orchestration-07152026/
├── agents/
│   ├── architect.md              (unchanged, carried forward)
│   ├── planner.md                (unchanged)
│   ├── requirements-analyst.md   (unchanged — the edit is in its skill, not this file)
│   ├── spec-reviewer.md          (unchanged)
│   ├── ui-spec-writer.md         (unchanged)
│   └── interview-conductor.md    (NEW — subagent fallback only, no `model:` field)
├── commands/
│   └── spec-start.md             (REWRITTEN — see API Contracts)
├── skills/
│   ├── architecture-design/      (unchanged)
│   ├── implementation-planning/  (unchanged)
│   ├── requirements-extraction/SKILL.md   (EDITED — Step 2 removed, renumbered)
│   ├── spec-review/              (unchanged)
│   ├── ui-specification/         (unchanged)
│   └── interview-conduct/SKILL.md         (NEW — gap-diff + stopping heuristic)
├── templates/
│   ├── INTAKE-TEMPLATE.md        (NEW)
│   ├── INTERVIEW-TEMPLATE.md     (NEW)
│   ├── NORTH-STAR-TEMPLATE.md    (NEW)
│   ├── GATE-LOG-TEMPLATE.md      (NEW)
│   ├── 01-REQUIREMENTS-TEMPLATE.md  (unchanged)
│   ├── 02-ARCHITECTURE-TEMPLATE.md  (unchanged)
│   ├── 03-UI-SPEC-TEMPLATE.md       (unchanged, conditional)
│   ├── 04-ROADMAP-TEMPLATE.md       (unchanged)
│   └── 05-REVIEW-TEMPLATE.md        (unchanged)
├── install.sh                    (EDITED — version bump only)
└── README.md                     (EDITED — new sequence, mandatory-Intake rule, version bump)

forge-07152026/
├── agents/                       (unchanged: code-executor, doc-writer, github-ops,
│                                   qc-agent, research, test-runner, test-writer)
├── commands/
│   └── forge-start.md            (REWRITTEN — see API Contracts)
├── skills/                       (unchanged)
├── templates/                    (unchanged: BINDING-CONTRACT, CADENCE, CLAUDE, INVARIANTS)
├── install.sh                    (EDITED — version bump only)
├── QUICKSTART.md                 (EDITED — version bump, mandatory-gate note)
└── README.md                     (EDITED — version bump, Frank binding-gate note)
```

Moves (this sprint only, already-archived `-03132026` packages untouched):
```
spec-orchestration-03242026/  →  archive/spec-orchestration-03242026/
forge-03252026/               →  archive/reference/forge-03252026/
```

---

## Propagation Sweep Mechanism

**Required this sprint (one-time):**
1. Run the new packages' `install.sh` (installs new/changed files, backs up anything it overwrites — existing behavior, unchanged this sprint).
2. `diff /home/d-tuned/agent-rig/agents/frank.md ~/.claude/agents/frank.md` after the redeploy step (below) — must be empty.
3. `grep -rl "03242026\|03252026" ~/.claude/agents ~/.claude/commands ~/.claude/skills` — must return nothing (excluding `~/.claude/history.jsonl`, `~/.claude/projects/**`, `~/.claude/file-history/**`, which are session logs, not live dispatch surface, and are out of scope for a sweep).
4. `grep -rn "Conduct Clarifying Interview" ~/.claude/skills/requirements-extraction/SKILL.md` — must return nothing.
5. Manually diff old vs. new `~/.claude/commands/spec-start.md` and `forge-start.md` to confirm no orphaned old-sequence prose (e.g. a leftover "if exists" CADENCE wording) survives the overwrite.

**Deferred**: a structural subtractive-install mechanism — diffing the new package's file tree directly against its already-archived predecessor (`archive/spec-orchestration-03242026/`, `archive/reference/forge-03252026/`) to compute removals, no manifest file needed — is a future option if Danny ever wants subtractive installs for real. Not built this sprint: it doesn't trace to any Intake "What Is Missing" gap, and untested deletion logic running against the live `~/.claude` surface four consumer projects depend on is exactly the kind of risk this sprint's own philosophy warns against introducing without a named need.

---

## Frank Prose Trim Specification

**Verdict template**: replaced exactly as shown in Data Schemas above — `{Findings, Why, Verdict, Fix/Next-step}`, checkable by scanning any real verdict for content outside those four headers.

**`agents/frank.md` mandate prose — sections and disposition:**

| Section | Disposition | Why |
|---|---|---|
| Frontmatter | Unchanged | Functional |
| "Why your mandate looks like this" | Trim to the shortest statement that still names the postmortem's cause-mechanism-outcome, plus a citation to the postmortem doc (already exists at the cited path) — no sentence-count target, this is an editorial judgment call | Ceremony is the retelling; the citation carries the substance |
| "Non-negotiable pre-checks" (5 items) | **Untouched, zero wording changes** | Explicit constraint — must survive verbatim in substance |
| "When invoked" | Unchanged | Functional, already terse |
| "Your review lens" | Unchanged | Functional guidance, not ceremony |
| "Your character" (5 verbose paragraphs) | Compress to one compact list | Persona flavor, not load-bearing |
| "You do NOT" | Unchanged | Already terse |
| "Structure of your verdict" | **Replaced** with the four-section template | This is the deliverable |
| "Things you squash" / "Things you approve quickly" | Trim each to the shortest list that still names each distinct calibration case, cutting duplicative or overlapping items — no target count, this is an editorial judgment call | Calibration examples, not mandate |
| "Tone" | Fold into the compressed "Your character" list | Pure flavor |
| "HALT Conditions" (final list) | Unchanged in substance; wording may tighten only | Functional, maps directly to pre-checks |
| **NEW**: "Layered North Star Check (spec-gate/forge-gate only)" | Added | Layer 1/Layer 2 definitions, the DRAFT/PROVISIONAL rule, and the missing-project-North-Star HALT, per US4-US6 |
| **NEW**: "Loop convergence judgment (attempt 3)" | Added | SHRINKING/STATIC/THRASHING classification + evidence-format requirement, per US7 |

**Measurable target** (structural, per Danny's locked Intake resolution #5 — "the target is structural, not a line count"; no supplementary number is introduced):
1. Verdict template structurally conforms to exactly 4 headers — checkable by inspection of a real verdict.
2. The five pre-checks + HALT Conditions list: 0% substance loss — checkable by Danny's direct diff review (US8 AC4), not delegated to Frank.
3. The ceremony sections in the disposition table above are visibly condensed per their stated disposition (e.g. "5 verbose paragraphs" → "one compact list") — checked by reading the disposition table against the actual diff, not a separate numeric threshold.
4. The two new substantive sections (Layered Check, Convergence Judgment) are additions, not ceremony — they don't count toward "shorter" one way or the other; the criterion is structural conformance to the disposition table, not aggregate file length.

---

## Sequencing (this sprint's rollout order)

1. `/forge-start` (or its lightly-adapted successor, since this is the sprint building it) implements the file/folder changes above.
2. `agents/frank.md` edited per the trim spec; Danny reviews the diff directly (not delegated to Frank — US8 AC4).
3. Only on Danny's explicit approval: sync/redeploy — `cp agent-rig/agents/frank.md ~/.claude/agents/frank.md`, then `diff` to confirm exact match. This step is gated on approval, not run opportunistically alongside the file edit.
4. Run new packages' `install.sh` (installs new/changed files; version bump only, no manifest logic).
5. Run the one-time grep-verified sweep checklist above.
6. Archive `spec-orchestration-03242026/` and `forge-03252026/` to their respective archive locations.
7. Full spec loop (this document's own sprint) runs Frank's spec-gate using current pre-trim Frank per the Intake's own Sequencing note (the trim is this sprint's output, not a precondition for reviewing it) — i.e., this document and its siblings get gated by *today's* Frank, and only subsequent sprints see the trimmed persona.

---

## Requirements Coverage

| User Story | Addressed by |
|---|---|
| US1 Mandatory Intake Gate | INTAKE.md status-enum contract; spec-start Step 0 |
| US2 Standalone Interview Stage | Inline contract + subagent fallback (HALT-relay-reinvoke); gap-diff/stopping-heuristic algorithm; INTERVIEW.md schema |
| US3 Retire Embedded Interview | requirements-extraction Step 2 deletion + Step 1 edit |
| US4 Sprint North Star | NORTH-STAR.md schema, single authoring point, read by both gates; presented at human-approval step |
| US5 Frank Binding Spec Gate | Frank binding-gate contract; Layer 1/Layer 2 on every attempt; GATE-LOG.md; snapshot mechanism; independent re-derivation algorithm |
| US6 Mandatory CADENCE/INVARIANTS Gate | forge-start Load Governance contract |
| US7 Frank Binding Forge Gate | Same contract/lane mechanism as US5, `LANE: forge-gate`, once at feature completion |
| US8 Frank's Prose Trim | Verdict template + section-by-section trim spec + structural measurable target |
| US9 Frank Source-to-Dispatch Sync | Gated sync/redeploy step in Sequencing |
| US10 New Dated Packages | Package Versioning & Directory Layout |
| US11 Global Sweep | Propagation Sweep Mechanism (one-time grep-verified checklist; structural subtractive-install deferred) |
| US12 YAGNI Pressure | Anti-Patterns section; every new file above traces to a named Intake "What Is Missing" gap, not speculative generality |
