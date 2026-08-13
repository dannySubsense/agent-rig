# Architecture — S2 Staleness Predicate (Round 3)

**Status**: LOCKED (Frank binding spec-gate PASS 2026-08-13, both layers; human approval Danny 2026-08-13)
**Author**: architect (dispatched by wright)
**Mode**: spec-lite
**Supersedes path**: was `docs/specs/session-queue-hardening/02-ARCHITECTURE-staleness.md` — relocated to the lite-mode source-of-record path.

**Author**: wright (architect role)
**Date**: 2026-08-13
**Scope**: fixes the S2 staleness count only. S1 (tag retrieval + cross-check) and S3 (git-state
capture) are unaffected and out of scope here.
**Status of prior rounds**: Round 1 (self-inclusion) and Round 2 (writer-transcript continuation)
both failed review on the same predicate. This document is the third attempt and is designed
against evidence gathered from the live repo, not against the two failed rounds' reasoning.

---

## 1. Evidence gathered

All of the following was verified directly against this checkout and its LORE rows, not assumed
from the INTAKE doc (whose own S2 section is the thing that has failed twice — see caller's brief).

**1a. The reviewer's specific case: transcript `0098cb1e…jsonl` as "the session that wrote it".**

```
documents row 85ce19a5-582f-4db9-8ad1-50e742245da1
  title: SESSION QUEUE 2026-07-21 → NEXT: start DDR-004 /spec-start...
  author: wright, created_at: 2026-07-21 05:14:48.789638+00
  tags: [session-queue, ddr-004, spec-start, next-session-entry-point, ...]
```

```
$ ls -la ~/.claude/projects/-home-d-tuned-agent-rig/0098cb1e-1cb7-4656-b821-69d5367a6b8e.jsonl
-rw------- 1 d-tuned d-tuned 1913954 Jul 21 05:31 0098cb1e-...jsonl
```

The transcript's mtime (05:31) is **16 minutes after** the capture's `created_at` (05:14:48) — the
same session, continuing through `/lore-close` Steps 5–7 (next-entry-point write, policy guard,
push gate) after Step 4 already wrote the capture. This is exactly Round 2's bug, reproduced on
real data: the writer's own transcript will *always* postdate its own capture by some margin, so
counting it as "a session that ran since the queue was written" is definitionally wrong — it's the
same session finishing the job that wrote the queue in the first place.

**1b. Transcript directory layout** (`~/.claude/projects/-home-d-tuned-agent-rig/`):

Top-level: one `<session-id>.jsonl` per main session (7 files observed). Sub-agent dispatches write
to `<session-id>/subagents/agent-<hash>.jsonl`, one level deeper — confirmed by directory listing;
the existing non-recursive `os.listdir()` scan in `newer_session_transcripts` already excludes
these correctly. **No change needed here** — Round 2 got this part right; it is not what failed
review.

**1c. Writer session ID is available to `/lore-close` at capture time.**

```
$ env | grep CLAUDE_CODE_SESSION_ID
CLAUDE_CODE_SESSION_ID=9c760bae-3c48-44c4-bbca-a39fd1981c68
```

This matches the current session's own transcript filename
(`9c760bae-3c48-44c4-bbca-a39fd1981c68.jsonl`, confirmed by directory listing) exactly. It is set in
the environment of every Claude Code session (main or child), not derived from stdin, so it is
readable by a slash command running mid-session — unlike `transcript_path`/`session_id`, which are
only delivered to `SessionStart` hooks via stdin and are not otherwise available to `/lore-close`.
This is the missing piece: Round 2 could self-exclude the *reading* session (stdin gives it that at
`SessionStart`) but had no way to identify the *writing* session at read time, because nothing
recorded which session wrote the capture. `$CLAUDE_CODE_SESSION_ID` closes that gap at write time.

**1d. Legacy rows exist and must be handled, not assumed away.**

Only two rows in `agent-rig` currently carry the `session-queue` tag at all (`85ce19a5…`,
`59c986bc…`, both 2026-07-21, pre-dating this hardening work entirely). The real 2026-08-09/08-10
close-outs are untagged (S1's problem, not S2's — but it means the row S2 will most often be asked
to evaluate, in this repo, right now, has no writer-session field and never will unless `/lore-close`
is re-run). Any design that only works when the field is present will silently do nothing useful for
the majority of near-term real usage in this repo.

---

## 2. Chosen signal

Keep the signal: **on-disk transcript mtimes in the project's local `~/.claude/projects/<slug>/`
directory**, compared against the queue capture's `created_at`. Rejecting this signal outright was
considered (see §5) but there is no better local proxy for "a session ran" — LORE only records
sessions that captured *something*, and the entire point of S2 is to catch sessions that captured
nothing (the un-closed case). A session that never touches LORE still touches its own transcript
file, continuously, for as long as it runs. Transcript mtime is the only observable trace of
"did a session run" independent of whether that session followed the close protocol.

What changes is **what gets excluded from the count**, and **what the mechanism is willing to
claim when it cannot know**.

### 2a. New field: `writer-session-id`, recorded at write time

`/lore-close` Step 4 records the closing session's own ID into the capture, using the value already
present in its own environment (`$CLAUDE_CODE_SESSION_ID`) — no new capability required, no new
capture parameter (still inside `content`, same rationale as S3's git-state block: no metadata
parameter exists on the write path).

### 2b. Exact rule

Given a retrieved queue capture (`created_at`, `content`, possibly containing a
`writer-session-id`), and the reading session's own `session_id` from `SessionStart` stdin:

1. Build `exclude_names` = `{ "<reading-session-id>.jsonl" }` (unchanged from Round 2 — this part
   was correct).
2. If `content` contains a `writer-session-id: <uuid>` line matching a UUID pattern, add
   `"<writer-session-id>.jsonl"` to `exclude_names`. Call this **writer-known = true**.
   If no such line is present (parse finds nothing, or the value is empty/malformed), **do not**
   add anything — but record **writer-known = false**. This is the branch that matters: it must be
   a distinguishable state, not silently treated as "writer excluded" or "writer is nobody."
3. Scan the top-level (non-recursive) `.jsonl` files in the project's transcript directory, as
   `newer_session_transcripts` already does. For each file not in `exclude_names`, with
   `mtime > created_at`, it counts as a stale session.
4. **Reporting branches on `writer-known`:**
   - `writer-known = true`, count = 0 → *"No session has run since this queue was written and
     closed, other than the writer's own close-out steps (excluded) and this reading session
     (excluded). Consistent with a clean handoff."*
   - `writer-known = true`, count = N > 0 → *"N session(s) have run since this queue was written
     and closed, excluding the writer's own close-out and this session, and produced no newer
     tagged queue. These may have ended without closing: [list, with mtimes]."*
   - `writer-known = false` (legacy row, no writer-session-id) → **do not compute or assert a
     count at all.** Emit: *"STALENESS UNKNOWN — this capture predates the writer-session-id
     field (or the field is missing/malformed), so this queue's own writer cannot be
     distinguished from a session that ran afterward and didn't close. No count is asserted;
     check `git log`, `git status`, and recent transcripts manually before trusting this queue's
     currency."* This replaces both Round 1's "always fires" and Round 2's "fires on the writer's
     own tail" — for legacy rows it fires on *nothing*, honestly, instead of computing a number it
     cannot stand behind.

This is the precise fix for the reported case: for `85ce19a5…` (2026-07-21, pre-dates this field),
`writer-known` will be `false` once this ships, and the hook will say "unknown," not assert a count
— true today, and true for any row written before this change ships, anywhere.

### 2c. Why this doesn't just move the bug (writer-session mid-run continuation)

An open question, not swept under the rug: if the writer's session keeps running *substantially*
after `/lore-close` finishes — new work, not just Steps 5–7's few remaining lines — its transcript
mtime keeps advancing indefinitely, and it stays excluded forever under this rule, because exclusion
is by identity (session ID), not by a time window. A truly open-ended continuation *would* be a
session that "ran since the queue was written" in every sense that matters, and this design would
mask it. This is a real, accepted limitation, not a solved case — see §6.

---

## 3. Exact rule, restated as pseudocode-level precision (design only, not code)

```
writer_id := extract from capture.content, pattern: line matching
             ^\s*writer-session-id:\s*([0-9a-f-]{36})\s*$   (case-insensitive hex)
             within the same fenced block convention S3 already established
             (a "session-queue-meta:" fenced block, sibling to "git-state:")

exclude := { reading_session_id }  (from SessionStart stdin, as today)
if writer_id is not None:
    exclude := exclude ∪ { writer_id }
    writer_known := true
else:
    writer_known := false

if writer_known:
    stale := [ t for t in top_level_transcripts(project_dir)
               if basename(t) not in {id + ".jsonl" for id in exclude}
               and mtime(t) > capture.created_at ]
    N := len(stale)
    report N, with list of (name, mtime) if N > 0
else:
    report UNKNOWN, no N computed, no alarm asserted
```

`created_at` and transcript mtimes are compared exactly as Round 2 already does it (UTC-aware
`datetime.fromtimestamp(mtime, tz=timezone.utc)` vs. Postgres's tz-aware column) — that
normalization was correct and is unchanged.

---

## 4. What changes, in which files

| File | Change |
|---|---|
| `~/.claude/commands/lore-close.md` (global, source of record: `commands/lore-close.md` in this repo) | Step 4: extend the existing fenced-block convention (currently only `git-state:`) with a second block `session-queue-meta:` containing `writer-session-id: <value of $CLAUDE_CODE_SESSION_ID>`. If the env var is empty/unset at capture time, omit the block entirely (do not write a placeholder like `unknown` — an absent field and an explicitly-unknown field must mean the same thing to the reader, so there is no reason to distinguish them at the writer). Document the env var's provenance (Claude Code session env, confirmed present in every session — see §1c) inline as a comment, same evidentiary standard as S3's `git-state` block. |
| `reference/session_queue_probe.py` and its deployed copy `scripts/session_queue_probe.py` (kept identical, per existing convention — confirm identical after edit, do not let the two drift) | `newer_session_transcripts` gains a `writer_known: bool` return alongside its existing list (or an equivalent signal — exact return shape is an implementation choice for whoever builds this, not fixed here). Add a small parser for the `session-queue-meta:` block (regex per §3) applied to `content` before calling `newer_session_transcripts`. Branch the staleness message text per §2b's three cases instead of the current two (stale / not-stale). The `HEADER`/`FOOTER` framing, the tag cross-check (S1), and the first-run-transition branch are all unaffected — only the staleness paragraph changes. |
| `.claude/hooks/session-queue.sh` | No change. It already passes stdin through unmodified; the reading-session self-exclusion path is untouched. |
| `docs/specs/session-queue-hardening/INTAKE.md` | Not edited by this document (out of scope for an architecture doc per the producer's own workflow — Intake corrections are the producer's or Frank's call) but its §S2 predicate text should be treated as superseded by this document once approved; flag for whoever runs the next Frank gate. |

No schema or gateway change (unchanged from INTAKE §4 — `content` is still where this lives, for
the same reason S3 chose it: no metadata parameter on the write path).

---

## 5. Failure modes considered and rejected

**Rejected: infer the writer from `documents.author` instead of a new field.**
`author` is always `wright` in this repo (single agent) — it cannot distinguish *which* session
wrote a given capture, only *which agent persona*. Multi-session, single-author is exactly this
repo's normal case, so this signal has zero discriminating power here. Rejected on direct evidence,
not by construction.

**Rejected: infer the writer as "the transcript whose mtime is closest to (but after) `created_at`".**
This looks appealing — the writer's transcript should be the *first* one to go stale after the
capture, by a small margin, versus a genuinely later unclosed session which would be further out.
But it is a heuristic with no reliable threshold: how many minutes is "the closing session finishing
Steps 5–7" versus "a different session that happened to start soon after"? Any cutoff would be an
unsourced constant (forbidden by this repo's numbers discipline) and would still be wrong whenever a
second session starts within that window — a realistic case (Danny working across two terminals).
Rejected in favor of an exact identity match, which has no threshold to get wrong.

**Rejected: drop the transcript-mtime signal entirely, use only LORE row timestamps (e.g. "N
captures written since this one").**
This answers a different, easier-to-get-right question ("has anyone captured anything since"), not
the one S2 exists to answer ("did a session run and *not* capture anything, i.e. end without
closing"). A session that ends without closing is, by definition, invisible to a LORE-only signal —
it wrote no row. Using only LORE data would silently stop detecting the exact failure mode S2 was
built for. Rejected because it deletes the mechanism's actual purpose while looking like a smaller
change.

**Rejected: have the SessionStart hook itself write a marker file/row identifying "this is a
continuation, not a fresh unclosed session."**
Considered as an alternative to recording `writer-session-id` at close time. Rejected because it
requires a write on every session start (this hook is explicitly read-only by design — see the
probe's own docstring, "Read-only. Never writes to LORE, never writes a file") and because it
doesn't solve the problem retroactively for the one concrete case in evidence (`85ce19a5…`, written
weeks before any such marker would exist). Recording at close time, in the row itself, needs no new
write surface and degrades gracefully for legacy rows (§2b's UNKNOWN branch) instead of requiring a
migration.

**Rejected: keep computing N for legacy rows using self-exclusion only (Round 2's behavior), just
document it as "may overcount by 1."**
This is what just failed review twice. An alarm that is wrong by a known, constant, always-present
offset is still an alarm that always fires in the steady state — "may overcount by exactly 1" is
indistinguishable in practice from "always fires," which is the reviewer's stated objection
verbatim. Explicitly rejected rather than re-proposed with a caveat.

**Considered: remove the staleness sub-check entirely, keep only S1's tag+cross-check.**
This is the "reduces or removes the mechanism" option the brief explicitly permits. It was not
chosen, but the reasoning against it should be recorded: S1's cross-check already catches *one*
shape of staleness — a newer **untagged** capture existing. It does not catch the shape S2 targets —
a session that ran and captured **nothing at all**, tagged or not. That is a materially different
and more dangerous case (fully silent), and it is also the concrete, evidenced case that motivated
this whole predicate (INTAKE §S2's own verification: `7920ea8c…`, 2026-08-11, ran with no capture
before or after it). Removing S2 would remove the only signal for exactly the failure mode it exists
to catch. Kept, with its claim narrowed (§2b) rather than its existence removed.

---

## 6. Open questions (not resolved here — stated, not assumed)

1. **Extended writer continuation.** If the writer's session keeps doing substantial work long after
   `/lore-close` finishes (not just Steps 5–7), its transcript stays excluded indefinitely under
   identity-based exclusion, and genuine staleness from that continuation goes undetected. No
   threshold-based fix was found that doesn't reintroduce an unsourced constant (§5). Whether this
   residual gap is acceptable, or whether `/lore-close` should be the natural end of a session by
   convention (making this moot in practice), is a product/workflow question, not an architecture
   one — flagging for Danny.

2. **Cross-machine sessions.** The transcript directory is local to the machine running the hook.
   A queue capture written by an agent session on a different machine (or a different `~/.claude`
   install) is invisible to this scan entirely — `newer_session_transcripts` would return `[]` not
   because nothing happened, but because nothing happened *here*. This produces a false "no staleness
   detected" for the "repo whose history nobody knows" case named in the brief. No design in this
   document solves this — it would require a signal outside the local filesystem (e.g. LORE-recorded
   session starts, which does not currently exist and is out of scope per INTAKE §4's "no gateway/
   schema changes"). Recording this as a known blind spot the emitted text should name, not paper
   over — suggest the UNKNOWN-branch message (§2b) and the count-provided message both gain a
   trailing note: *"This check only sees sessions run on this machine's Claude Code install."*

3. **Malformed `writer-session-id` values.** §3's regex requires a UUID-shaped value. What a
   hand-edited or corrupted capture with a non-UUID value in that field should do (treat as absent →
   UNKNOWN, per §2b's "malformed" branch) is specified above, but was not tested against a real
   malformed row because none exists yet. Flagging that the parser needs a test case for this before
   being called done, not before being designed.
