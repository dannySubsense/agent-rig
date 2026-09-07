# Runbook: How Issues Get Handled

**Scope**: every GitHub issue filed against this repo, regardless of subject. This is the
sequence an issue moves through from "filed" to "closed" — it doesn't replace the standard
Intake → Interview → spec-start → forge-start loop in `CLAUDE.md`, it's the layer above it that
decides how much of that loop a given issue actually needs and adds the checks specific to what
kind of issue it is.

## Step 0 — File the issue before touching the fix

Every issue gets exactly three sections, nothing more:
- **Problem** — the concrete, reproducible failure or gap (quote the actual output/input that
  triggered it, not a paraphrase).
- **Root cause** — traced to the actual design decision or code path responsible, cited by
  file/function/spec-section, not guessed from symptoms. If root cause isn't yet known, say so
  explicitly rather than skipping the section.
- **Proposed direction** — a direction, not a finished design. Mark the fix as deferred if a
  human hasn't yet said "go" on scope.

Do not start Intake until the issue exists — the issue is the durable record of the finding
independent of whether the fix session ever completes.

## Step 1 — Classify the issue

Before any process starts, name which of these it is (state it explicitly, don't silently
assume):

- **Enforcement-mechanism defect** — a hook, gate, Frank's own gate logic, or a track-record/
  roster check that's supposed to catch or verify something and doesn't (or catches the wrong
  thing). See "Enforcement-mechanism issues" below for the extra requirements this category
  carries.
- **Ordinary bug or feature gap** — application/tooling logic outside the enforcement layer.
  Standard loop, standard rigor, no extra requirements from this runbook.
- **Doc/process-only** — no code changes, just a doc, DDR-INDEX entry, or convention fix. Skip
  straight to a direct edit + review; the full loop is disproportionate.

## Step 2 — Judgment check before any process starts (Unasked Judgment doctrine)

Does this actually need a fix, or does the affected mechanism need to be simplified or removed
instead? Something wrong in a way that's cheaper to delete than repair is not automatically a
repair project. State this explicitly even when the answer is "yes, fix it" — don't skip straight
to spec machinery.

## Step 3 — Intake, scoped narrowly to the one issue

`docs/specs/<slug>/INTAKE.md`, citing the issue number. Scope is the one thing named in the
issue — don't fold in adjacent hardening ideas noticed along the way (each of those gets its own
issue via Step 0, not silently bundled here). Bundling is how a narrow, verifiable fix turns into
an unreviewable pile.

## Step 4 — Interview, inline

Standard Interview stage. If the issue's Problem/Root cause/Proposed direction already answer
every gap question, the interview is short — say so, still produce `INTERVIEW.md`.

## Step 5 — Spec, sized to the actual change; decide out loud

Full `/spec-start` vs. lite mode is a decision to state, not default silently. Full is required
whenever the change touches matching/detection *logic*, cross-cuts multiple call sites, or could
plausibly break an adjacent case that isn't the one named in the issue (Easy Menu Choice territory
— a fix that looks narrow can still regress something the issue never mentioned). Lite is
acceptable only when the change is additive and mechanically bounded with no behavior change to
any currently-passing case.

**Enforcement-mechanism issues: Frank spec-gate runs Cold, no exception.** Both Cold Gates
requirements (unbriefed dispatch, isolated detached checkout) apply even when the dispatcher is
already confident what's wrong — confidence is not a substitute for an independent check on a
mechanism other sessions are actively relying on right now.

## Step 6 — Forge

- code-executor implements against the locked spec.
- **Enforcement-mechanism issues**: a regression test reproducing the exact original failure is
  mandatory, not optional coverage — its whole job is proving the specific evasion named in the
  issue can never pass silently again. Name it so a future reader immediately knows what incident
  it guards (`test_c3_signpost_sourced_subjects_catch_unverified_pillar`, not
  `test_c3_edge_case_3`).
- Independent test-runner (not the code-executor) confirms the suite — including any new
  regression test — actually fails on the pre-fix code and passes on the post-fix code. A test
  that would pass either way proves nothing.
- **Enforcement-mechanism issues: Frank forge-gate runs Cold.** Isolated detached worktree of the
  final commit SHA. No file list, no scope narration, no "here's what changed" — repo + SHA +
  parent SHA + verdict required, nothing else.
- Ordinary bugs/features: standard forge-gate per `CLAUDE.md`, no extra Cold requirement beyond
  what already applies.

## Step 7 — PR, human review of the diff, not a status summary

Open a PR, don't push straight to main. For an enforcement-mechanism fix, the diff gets the same
standing as an identity artifact or North Star doc: Danny reviews the actual diff before it
merges, not a description of it — state explicitly what specific gap or evasion this closes, and
paste the regression test's before/after result where one exists.

## Step 8 — Close the loop

- Update the issue: link the PR, and once merged, close with the merge commit SHA.
- If the issue reveals a pattern likely to recur elsewhere (e.g. "any check that extracts
  subjects from freeform prose has this shape of hole"), capture that as its own `lesson-learned`
  LORE entry (via `/lore-close` Step 4.5) so `/oracle` can surface it before the next similar
  mechanism gets designed the same way — don't let the generalizable lesson live only inside this
  one issue's fix.
- If a track-record file exists for an affected hook, confirm post-merge (on `main`, not the
  feature branch) that the fix actually fires as expected — CODE-MERGED is not LIVE until a real
  invocation proves it, same distinction `/lore-close` already enforces for session closure.

## Non-goals

- Does not replace `/lore-close`, `/spec-start`, or `/forge-start` — it sequences and sizes them
  per issue, and adds two things only enforcement-mechanism issues need: a mandatory regression
  test tied to the specific evasion, and Cold-Frank-always-not-just-usually.
- Does not add process to issues that are actually doc-only or trivially scoped (Step 1's
  classification exists precisely so this runbook doesn't become ceremony for its own sake).
