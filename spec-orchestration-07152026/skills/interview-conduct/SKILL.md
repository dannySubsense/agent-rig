---
name: interview-conduct
description: |
  Gap-diff seed-question generation and loop-until-dry stopping heuristic
  for the standalone Interview stage. Use when running spec-start Step 1
  (Interview) — either inline in the orchestrating session (default) or
  when dispatched into the interview-conductor subagent fallback.
allowed-tools: Read, Write, Glob, Grep
---

# Interview Conduct

Procedural guide for the gap-diff + adaptive-loop Interview stage that runs
between an approved `INTAKE.md` and the start of `01-REQUIREMENTS.md`
extraction. This is a real, non-skippable stage — it always produces
`INTERVIEW.md`, never silently folds into requirements extraction, and
never fabricates an answer under any circumstance.

Two callers use this skill:
- **Inline (required default):** the orchestrating `/spec-start` session
  executes the procedures below directly, in the same live turn Danny is
  part of. No Task-tool dispatch, no round-trip ceremony.
- **Subagent fallback (documented, not default):** `interview-conductor.md`
  runs only `gap_diff` + seed question generation from this skill, then
  returns without answering — see that agent's contract for the
  HALT-relay-reinvoke loop this triggers in the orchestrator.

## Step 1: gap_diff — Diff Against Two Sources, Not One

`gap_diff` never diffs against `INTAKE.md` alone. It diffs against BOTH:
1. **`INTAKE.md`'s text** — the durable, already-approved artifact.
2. **The conversation since Intake approval** — anything Danny and the
   orchestrating session have already discussed live, in this session,
   that never made it into the Intake doc itself.

Skipping the second source recreates the exact "shared well" failure this
sprint exists to avoid: relying on memory of a conversation instead of
checking what was actually resolved.

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
```

### The Four Blind-Spot Categories

Every seed question traces to exactly one of these four. Do not invent a
fifth category or subdivide these into more granular ones — they are the
complete list:

1. **Testing/rollback** — how will this be verified, and what happens if
   it needs to be undone?
2. **Non-functional constraints** — performance, security, availability,
   compatibility, or other constraints not captured as a functional user
   story.
3. **Downstream impact** — what else in the system, or which other
   consumers/projects, does this change touch or risk breaking?
4. **Edge cases not already resolved** — boundary conditions, error paths,
   or unusual inputs that Intake's Problem Statement and Scope sections
   left open.

For each category: check Intake's text first, then the live conversation.
Only generate a seed question if *neither* source already resolves it. A
category with nothing left to ask is not a defect in the Interview — it
means Intake did its job for that category.

The `5-7` seed-question count in the return is a **soft anchor**, not a
target to pad toward or a ceiling to enforce — if gap_diff genuinely
produces zero or twelve candidates, that is the real state of the gaps,
not something to round toward the anchor.

## Step 2: interview_loop — Ask, Adapt, Stop

```
interview_loop(seed_questions):
  non_generative_streak = 0
  for q in seed_questions (or until Danny signals done):
    answer = ask(q)  # or, if Danny opted out: stand_in(q) — see Step 3
    if answer opens a new thread not already covered:
      ask adaptive follow-up(s) on that thread
      non_generative_streak = 0
    else:
      non_generative_streak += 1
    if non_generative_streak >= 2: break  # 2 is the chosen upper end of
      # Danny's 1-2 heuristic (INTERVIEW.md), not a separately-derived number
  write INTERVIEW.md (template below)
```

### Stopping Rule

Track a running `non_generative_streak` counter across the whole loop, not
per-question. An exchange is **non-generative** when the answer does not
open a new thread beyond what is already covered by an existing seed
question, an already-asked follow-up, or an already-resolved category.
Any generative exchange (one that opens a genuinely new thread) resets the
streak to zero and spawns adaptive follow-up question(s) on that thread
before continuing.

**Stop the loop once `non_generative_streak` reaches 2.** This is the
chosen upper end of Danny's own 1-2 heuristic recorded in `INTERVIEW.md`
for this sprint — 2 consecutive non-generative exchanges, not 1 and not a
separately-derived number. Record the stopping point in the
`## Stopping Rationale` section of the written `INTERVIEW.md`, e.g.:
"2 consecutive non-generative exchanges after Q5; stopped below the 5-7
soft anchor."

The loop may also end early if Danny explicitly signals he is done
answering, independent of the streak counter — record that explicitly in
the Stopping Rationale too, and note the pass-option below applies to any
remaining un-asked seed questions.

## Step 3: stand_in(q) — The ASSUMED-Stamp Procedure

If Danny opts out of answering (a specific question, or the Interview
stage as a whole), the conducting model — the same model running the
interview, no separate lightweight tier — generates a stand-in answer via
`stand_in(q)`.

Every stand-in answer MUST be stamped in exactly this form:

```
ASSUMED — Danny did not answer; based on [named industry pattern/framework precedent]
```

The `[named industry pattern/framework precedent]` is a required, cited
rationale — name the actual pattern, framework, precedent, or prior
decision the stand-in is based on. **A bare `ASSUMED` flag with no
`[rationale]` is a defect in the artifact, not an acceptable output.** Do
not write `ASSUMED` alone, `ASSUMED — no answer given`, or any other form
that omits a citable basis.

Mark the `Assumed?` column `yes` for every stand-in row in the Seed
Questions table.

## Step 4: Write INTERVIEW.md — Always, Even on Zero Gaps

This stage always produces `INTERVIEW.md`, with no exception. If `gap_diff`
returns zero candidate questions, still write the file:
- `Status: Complete`
- An empty Seed Questions table (headers only)
- An explicit statement in Stopping Rationale: "no gaps found — Intake and
  prior conversation already resolved all four categories."

Never skip this artifact and never fold its content silently into
`01-REQUIREMENTS.md` — a stage that can be silently skipped in practice is
exactly the dead-ceremony failure this sprint exists to retire (see
`requirements-extraction`'s deleted Step 2).

Use this exact shape (matches `templates/INTERVIEW-TEMPLATE.md`):

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

`Status: Passed (Danny opted out)` is used when Danny opts out of the
Interview stage entirely (not just individual questions) — every seed
question in that case is answered via `stand_in(q)`, stamped as above.

## Output Verification

Before reporting the Interview stage complete, verify:
- [ ] `gap_diff` was checked against both `INTAKE.md` text and the live
      conversation since Intake approval — not just one source
- [ ] Every seed question traces to exactly one of the four categories
- [ ] The stopping rule (2 consecutive non-generative exchanges) was
      applied and is recorded in Stopping Rationale, OR an explicit "Danny
      signaled done" note is present instead
- [ ] Every `ASSUMED` row carries a `[named precedent]` — no bare stamps
- [ ] `INTERVIEW.md` was written even if the Seed Questions table is empty

## Error Handling

If Danny's answer is ambiguous about whether it opens a new thread:
→ Treat it as generative (ask a clarifying follow-up) rather than
  silently counting it non-generative — false negatives on "dry" cost one
  extra question; false positives end the Interview too early.

If a stand-in would require inventing a precedent that doesn't actually
exist:
→ Do not fabricate one. Leave the question unresolved, mark it for Danny's
  explicit follow-up, and note this in Stopping Rationale rather than
  writing an uncited ASSUMED stamp.
