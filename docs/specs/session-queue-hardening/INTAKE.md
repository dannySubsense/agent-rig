# INTAKE — session-queue-hardening

**Status**: APPROVED (2026-08-13, Danny) — rev 2 after Frank Intake gate FAIL on S2 predicate (self-inclusion); S2 restated, first-run transition added
**Author**: wright
**Date**: 2026-08-13
**Mode**: spec-lite (Danny, 2026-08-13)
**DDR**: none

---

## 1. What exists now

`85194cb` (branch `feature/session-queue-injection`, agent-rig only, unpushed) installs a
`SessionStart` hook that reads the most recent canonical LORE capture for the project and injects it
into context labeled as a signpost. It passed an independent Frank gate on its third revision.

`/lore-close` (`~/.claude/commands/lore-close.md`) writes that capture, in Step 4, via
`capture_memory`. It is invoked manually; nothing fires it.

## 2. The two problems

**P1 — the hook cannot identify the queue, only guess at it.**
There is no `queue` documentType. Of agent-rig's 39 captures, 25 are `decision` — the same type
`/lore-close` writes for a close-out *and* the type used for mid-session decisions. The hook
therefore infers "is this a close-out?" from `document_type`, which cannot distinguish them. Frank
logged this as a real, non-theoretical false-positive rate; the injected text currently hedges
("MAY be the last session's own account") because it genuinely cannot know.

Verification: `SELECT document_type, count(*) FROM documents WHERE project_id='agent-rig' GROUP BY 1`
→ decision 25, review 7, discovery 5, test-result 2. `tags` is non-empty on 21 of 39 rows, so the
column is live and in use.

**P2 — a stale queue is indistinguishable from a current one.**
The head capture for agent-rig is dated 2026-08-10. Sessions ran on 08-11 and 08-12 (the latter
producing PRs #5–#8) and wrote no capture. The hook presents the 08-10 row as the queue with no
indication that two sessions have happened since. Frank's gate flagged this as undetectable from the
database alone — correct, given only the database.

## 3. What is proposed

**S1 — label the queue explicitly.** `/lore-close` Step 4 adds a `session-queue` tag to its capture.
The hook queries by tag instead of "most recent canonical row." Provenance stops being a heuristic:
either a tagged queue exists, or none does, and the hook says which.

**S2 — spot-check against on-disk session transcripts, EXCLUDING THE CURRENT SESSION.**
Claude Code writes one `.jsonl` per session under `~/.claude/projects/<project-slug>/`, with real
mtimes. The check: **exclude the running session's own transcript** — the `SessionStart` hook
receives `session_id` / `transcript_path` on stdin — then compare the newest *remaining* transcript
mtime against the queue capture's `created_at`. `N` = count of transcripts newer than the capture,
self excluded. If `N > 0`, that many sessions have run without closing, and the hook says so with
dates.

**The self-exclusion is the whole check, not a detail.** Without it the predicate fires 100% of the
time, because the session running the hook writes its own transcript at startup — an alarm that
always fires is not an alarm, it is the hedging S1 exists to eliminate, wearing a date. Caught by
Frank's Intake gate, 2026-08-13.

Verification that the condition exists, using evidence NOT contaminated by the observing session:
transcript `7920ea8c-…jsonl`, mtime 2026-08-11 10:25, is newer than the head queue capture of
2026-08-10 13:20 and is not the current session. `N ≥ 1` today on clean evidence. An earlier draft
of this Intake cited a 2026-08-13 transcript as proof — that was this session's own file, i.e. the
document verified its premise with the artifact the predicate was wrong about. Recorded rather than
quietly corrected.

Two details for the spec-lite, not decided here: transcript mtimes are local-tz `stat` values and
`created_at` is tz-aware — normalize before comparing. And sub-agent dispatches also write `.jsonl`
into the same directory, inflating `N`; the spec must decide whether that is acceptable noise and
say which.

**S3 — carry git state into the close capture.** `/lore-close` records unpushed commits and dirty
tree state in the capture body, so the next session inherits it. (Step 7 already gates on unpushed
commits interactively; this records the outcome rather than only prompting.)

## 4. Explicitly out of scope

- **A SessionEnd hook. Decided against, 2026-08-13 (Danny).** It runs after the session ends: its
  output reaches nobody, it cannot make anyone run `/lore-close`, and it cannot write a capture
  because deciding what mattered is judgment. S2 covers the detection half from the reading end.
- Propagation to any other repo. This lands in agent-rig only. Slice 12 of
  `signpost-pillar-propagation` is the separate, still-pending rollout vehicle.
- Changes to `capture_memory`, the gateway, or the LORE schema. `tags` already exists.
- Re-litigating `85194cb`. Its two known non-blocking defects (output-shape validation; untagged
  outer `timeout 5`) are listed below as carry-ins, not reopened design.

## 5. Carry-ins from the prior Frank gate

Both were PASS-with-recommendation, to be fixed before propagation. Folding them here rather than
leaving them loose:

- Wrapper validates JSON parseability but not `hookSpecificOutput.hookEventName == "SessionStart"`.
- Wrapper's outer `timeout 5` is untagged and borrows a budget sourced for local git operations, not
  a Tailscale Postgres round trip.

## 6. Decisions (Danny, 2026-08-13)

1. **Tag name: `session-queue`.** Confirmed, and confirmed as a cross-project convention if this
   propagates — chosen with that in mind, not as an agent-rig-local string.
2. **`/lore-close` is edited globally.** Confirmed intended: this is a homelab-wide implementation,
   not agent-rig-local guidance. The command lives at `~/.claude/commands/lore-close.md` and is
   shared by every project, so this change alters close behaviour for every agent. Recorded here
   explicitly because it is the one part of this work with a blast radius beyond this repo.
3. **S3: structured — but inside `content`, not as a column.** Danny asked for a recommendation and
   said his gut was structured. Agreed, with one correction found by checking the write path rather
   than assuming it:

   `capture_memory` accepts `projectId`, `documentType`, `title`, `content`, `tags`, `status`,
   `supersedesId`, `epistemicType`, `author`, `confidence`, `sourceType` — **there is no metadata
   parameter.** The `metadata` jsonb column exists on `documents` but the write path does not expose
   it. `update_metadata` offers only `status`, `git_sha`, `supersedes_id`, as a separate post-hoc
   call.

   So git state goes in as a **fenced structured block inside `content`** (`branch`, `head`,
   `unpushed`, `dirty`). Rationale: needs no gateway or schema change (§4 puts those out of scope);
   the hook already reads `content`; it stays human-legible in `search_knowledge` results instead of
   hiding in a column nobody queries; and it avoids a second write call that could fail
   independently and leave the capture half-recorded.

   Rejected: `git_sha` via `update_metadata` — a genuine structured field, but it holds one SHA and
   cannot express "3 unpushed commits, tree dirty," which is the actual signal.

## 7. Done-when

- A capture written by `/lore-close` is retrievable by tag, deterministically.
- The hook distinguishes "tagged queue found" / "no queue found" / "queue found but N sessions have
  run since it was written," and says which — no hedging where a fact is available.
- Both carry-ins closed.
- **CORRECTION 2026-08-13 (Frank implementation gate, FAIL): the premise below was FALSE.**
  This document asserted "zero existing captures carry the `session-queue` tag." Live data: TWO
  agent-rig captures from 2026-07-21 already carry it (`85ce19a5`, `59c986bc`; the latter is already
  superseded, so only the former is live). The author verified tag *counts* (21/39 rows non-empty)
  but never ran `WHERE tags @> ARRAY['session-queue']` — the single query the whole design depends
  on — and every downstream artifact inherited the unchecked claim. The built implementation then
  asserted "This IS the queue, retrieved deterministically" about a three-week-stale row while the
  real 2026-08-10 close-out, being untagged, was never mentioned. That is worse than the hedging it
  replaced: confident and wrong beats uncertain and honest only when it is right.
  Recorded, not quietly fixed — the same standard this document applied to its own rev-1 error.
- **Consequence: the probe must not trust a bare tag.** A tagged hit is cross-checked against the
  newest untagged canonical capture; where a newer untagged one exists, the injection reports the
  conflict rather than crowning the tagged row. Chosen over retagging the legacy rows (Danny,
  2026-08-13) because it is correct in every repo, including those whose tag history nobody knows.
- **First-run transition.** Where no tagged queue exists at all, the hook reports that captures exist
  but predate the convention. The hook must report that honestly — "no tagged
  queue found; captures exist but predate the convention" — rather than implying the project has
  never been closed. This resolves itself at the first post-change `/lore-close`.
- Verified by a real session start, not by running the script manually. **The current hook has never
  been observed firing in a live session** — that gap applies to this work too and does not close
  until someone opens a session and sees the output.
