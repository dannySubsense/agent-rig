---
description: Close out a working session cleanly — reconcile status across all layers, verify against ground truth, capture to LORE. Portable across all LORE projects.
argument-hint: "[optional: note on where the session ended]"
---

# Session Close-Out (LORE projects)

Run the Session Closure Protocol for THIS project. The goal: leave zero stale or ambiguous
status behind, so the next cold start can trust what it reads. Optional context from the
invoker: `$ARGUMENTS`.

## Step 0 — Establish project identity (HALT if not a LORE project)

Read this repo's `CLAUDE.md` and extract:
- **projectId** (the "Project ID" / "projectId" field)
- **author / agent name** (the "Agent Identity" name; fall back to projectId)

If `CLAUDE.md` has no LORE projectId → HALT: "Not a LORE project — nothing to close to LORE.
Want me to just reconcile local status docs?"

If this repo has `docs/SOP_SESSION_CLOSURE.md`, treat it as the authoritative detail and follow
it; the steps below are the portable core that applies even without it.

## Step 1 — Enumerate what this session touched

List every feature / sprint / task whose status changed this session (built, fixed, decided,
deployed, or discovered-broken). For each one you will assign an explicit state in Step 2.

## Step 2 — Assign an explicit state; NEVER write "shipped" bare

Each item is exactly one of — and you must PROVE it, not assume it:

| State | Means | How you must verify it THIS run |
|---|---|---|
| `SPEC'D` | Spec written, not built | spec docs exist |
| `CODE-MERGED` | On the main branch; NOT verified live | `git log` / `git show` shows the commits on the branch |
| `LIVE` | Deployed AND a runtime probe confirms it works | run an ACTUAL probe: `curl` the endpoint, `systemctl is-active`, query the DB/file the feature writes, hit the UI route |

"Code merged" is NOT "live." If you cannot run the probe (e.g. service down, no access),
the item is `CODE-MERGED`, not `LIVE` — say so explicitly. Do not upgrade a label on faith.

## Step 3 — Reconcile ALL status layers so they agree

These must tell the same story for every active item before you finish:
- The project's local status memory (`project_status.md`) **and** its one-line `MEMORY.md` index entry
- Any relevant `docs/specs/*/PROGRESS.md`
- The canonical LORE capture(s)

Reconcile them — do NOT merely append a new claim and leave the others stale. If any two
disagree, that disagreement is the bug; fix it now.

## Step 4 — Capture closure to LORE, superseding the open-state memory

Call `mcp__lore-gateway__capture_memory` with:
- `projectId` and `author` from Step 0
- `documentType: "decision"` (or `"review"` for a sprint sign-off)
- `epistemicType: "FACT"`
- `tags`: include `"session-queue"` — this is the deterministic marker that lets the
  SessionStart injection hook find this capture by tag instead of guessing from
  `document_type`. Always include it on the Step-4 closing capture; add other tags as usual.
- `supersedesId`: the documentId of the prior open-state / "in progress" / "queued" memory this
  closure replaces, so the stale version drops out of default search. (Search LORE first to find it.)

Capture what the next session needs to resume — not trivia. One focused capture per closed item
beats one sprawling dump.

Include current git state as a fenced structured block inside `content` (not via
`update_metadata`, not as a separate column — the write path exposes no metadata parameter):

```
git-state:
  branch: <current branch>
  head: <HEAD sha>
  unpushed: <count of commits ahead of upstream, or "no upstream configured">
  dirty: <true/false — uncommitted changes present>
```

Gather these with `git branch --show-current`, `git rev-parse HEAD`, `git log --oneline @{u}..HEAD | wc -l` (or "no upstream configured" if `@{u}` fails), and `git status --porcelain` (non-empty → dirty). This lets the next session inherit git state from the capture itself rather than only from Step 7's interactive prompt.

Also include a second fenced block, sibling to `git-state:`, recording this closing session's own
id (used by session-queue staleness checks to distinguish this session's own close-out tail from a
genuinely later, unclosed session):

```
session-queue-meta:
  writer-session-id: <value of $CLAUDE_CODE_SESSION_ID>
```

`CLAUDE_CODE_SESSION_ID` is an undocumented Claude Code environment variable (not part of any
published API) — confirmed present in the environment of every session on this install, main or
child (verified directly, not assumed; see `docs/tooling/session-queue-hardening.md` §1c). Read it
with `echo "$CLAUDE_CODE_SESSION_ID"`.

If the variable is empty or unset at capture time, **omit this block entirely** — do not write a
placeholder such as `unknown`. An absent field and an explicitly-unknown field must mean the same
thing to a reader, so there is no reason to distinguish them at write time.

## Step 5 — Write the next-entry-point as a HYPOTHESIS

Record the next session's likely starting task in `project_status.md`. Mark it clearly as a
hypothesis to be re-validated at next session start — anything claimed `LIVE` gets a one-line
runtime probe before it is acted on. Never leave a bare "next: do X" that a future session will
trust blindly.

## Step 6 — Guard against duplicated policy

If this session created or changed a standing rule, confirm it lives in ONE version-controlled
file and that other docs point to it rather than restating it. Duplicated policy is how drift
starts.

## Step 7 — Push gate (never leave an unpushed commit silently)

Closure must never leave the human assuming a push that did not happen. The job of this step is
NOT to always push — it is to make the push state an EXPLICIT, reconciled fact every time.

1. Commit any closure-related changes that live IN the repo first (e.g. a `PROGRESS.md` update),
   so the divergence check sees the true final state. (Local status memory under
   `~/.claude/.../memory/` is outside the repo — it is not part of this check.)
2. Detect divergence from upstream: `git log --oneline @{u}..HEAD`.
   - Non-empty → there are unpushed commits.
   - If `@{u}` fails (no tracking branch) → note "no upstream configured; human must set the
     remote" and treat as a deliberate-not-pushed outcome. Do not invent a remote.
3. If unpushed commits exist, act per THIS repo's declared git convention. Read the push policy
   from, in order: the repo's `CLAUDE.md` "Git Workflow" section, then a tracked fallback such as
   `docs/GIT-WORKFLOW.md` (used when `CLAUDE.md` is gitignored and does not travel with a clone).
   If both are absent, there is NO declared push-at-close policy — degrade safely (see below).
   - Repo declares **push-at-close to mainline is the convention** (e.g. "slices commit+push
     directly to main") AND the push is a fast-forward → push now
     (`git push <remote> <branch>`), then verify `git rev-parse @{u}` == `HEAD`.
   - Repo uses **PR / protected-branch / feature-branch** flow, declares **no** push-at-close
     policy, or the upstream has **diverged** (non-fast-forward) → DO NOT push automatically.
     Instead, **ask explicitly**: state the unpushed commits and ask "Push now?" — wait for
     confirmation before pushing. Record the outcome (pushed or held) in the status layers.
4. NEVER force-push to resolve divergence as part of closure. Divergence is a human decision,
   not a close-out action.
5. Reconcile the outcome: the push state (`pushed` / `deliberately not pushed, reason`) must now
   read the same in `project_status.md`, the `MEMORY.md` index line, and the LORE capture. If you
   pushed AFTER the Step 4 capture, that capture's git/push lines are now stale — supersede it
   with a corrected capture so all layers agree (do not leave a "push next session" actionable
   that is already done).

## Final report

Print a short close-out summary:
- Each touched item with its verified state (`SPEC'D` / `CODE-MERGED` / `LIVE`) and the proof used
- Which status layers you reconciled
- LORE documentId(s) captured and what each superseded
- **Push state**: pushed (verified `@{u}` == `HEAD`) / deliberately not pushed (with reason) —
  never silent
- The next-entry-point hypothesis

Do not claim the session is closed until every item has a verified state, the layers agree, and
the push state is explicit.
