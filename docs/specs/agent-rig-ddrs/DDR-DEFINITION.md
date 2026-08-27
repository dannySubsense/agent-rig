# What Is a DDR

**Status**: Established 2026-08-27 (Danny/wright, in response to a confirmed recurring failure —
see History below). This is agent-rig's canonical definition, source-of-record for the
`new-project` bootstrap stub (`commands/new-project.md` Step 11).

---

## Definition

A **DDR (Decision Record)** captures one thing: **what was decided, when, and why.** Nothing more.

It is not:
- A feature spec (that's `docs/specs/<sprint>/SPEC.md` or the full spec-forge doc set).
- A status tracker (that's `docs/specs/<sprint>/PROGRESS.md` or `docs/tooling/<tool>/PROGRESS.md`).
- A running log of every downstream sprint that touches the same subsystem.
- A place to quote or restate another document's current state — link to it instead.

A DDR is written once, at the moment a decision is made, and is edited again only under the
Lifecycle rules below — not casually appended to whenever something related happens.

## Lifecycle

- **DRAFT** — decision proposed, not yet made. May be revised freely.
- **ACCEPTED** — decision made and, if applicable, shipped. The row/file states the decision and
  cites the PR/commit that shipped it, if any. **Once ACCEPTED, a DDR's own text does not track
  what happens next** — a shipped mechanism's ongoing behavior, deployment status, or downstream
  hardening work is a fact about the *sprint(s)* that did that work, not about the *decision* to
  build it in the first place. Link forward to those sprints' `PROGRESS.md` files; do not restate
  their content here, and do not update this row every time one of them changes.
- **REJECTED** — decision considered and declined. State why, briefly. Does not get reopened
  without a new DDR that explicitly supersedes it.
- **SUPERSEDED** — a later DDR replaces this one's decision. State which DDR supersedes it. The
  original DDR's text is not rewritten to match the new decision — it stays as the historical
  record of what was decided *then*.

A DDR file may be lightly amended after ACCEPTED only to fix a factual error in the decision
statement itself (e.g. a wrong PR number) — never to add narrative about what happened afterward.

## What Belongs in the DDR-INDEX Row vs. Elsewhere

| Content | Belongs in |
|---|---|
| What was decided, when, why | DDR-INDEX row / DDR file |
| Current deployment/rollout status | The relevant sprint's `PROGRESS.md` |
| Test results, gate verdicts | That sprint's `GATE-LOG.md` |
| "X is still pending / no response yet" | Nowhere permanent — this is exactly the kind of claim that goes stale; if it needs to be tracked, it's a GitHub Issue or a live Switchboard/LORE check, not index-row prose |
| A downstream sprint's outcome (e.g. "the gap this DDR left open was later closed by sprint Y") | Sprint Y's own `PROGRESS.md`; the DDR row may add a **single short link** ("see sprint Y"), never a restatement of Y's content |

**Test for whether an edit belongs in a DDR row**: if the sentence you're about to add would need
to be updated again later as facts change, it does not belong in the DDR row. Decisions don't
change after they're made; status does.

## History

Confirmed recurring failure, 2026-08-27: DDR-004's row accumulated multiple appended status
clauses across separate sessions by separate agents — a deployment-status paragraph, then a
downstream-sprint-outcome paragraph — despite `PROGRESS.md` files already existing for every one
of those facts. One appended clause ("pilot relayed to alpha, no response yet") went stale within
days (the pilot was actually completed, per `docs/specs/signpost-pillar-propagation/PROGRESS.md`)
and was later quoted back as current fact by a downstream session, because nothing distinguished
"decision record" from "status log" for the agents doing the appending. Root cause: no definition
of what a DDR is had ever been written down in this repo, and the `new-project` bootstrap stub
(`commands/new-project.md` Step 11) seeds every new project's `00-DDR-INDEX.md` with a bare table
and no scoping guidance — so the drift was structurally inevitable, not a one-off lapse. This
document, and the corresponding update to the bootstrap stub, are the fix.
