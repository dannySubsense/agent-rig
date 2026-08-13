#!/usr/bin/env python3
"""SessionStart queue injection — the signpost half.

Reads the tagged ('session-queue') LORE capture for this project and injects it into the
agent's context at session start, explicitly labeled as a SIGNPOST: a list of claims to
be verified, not facts to be repeated.

Why a hook and not `search_knowledge`: a tool call requires the agent to remember to make
it. A hook fires whether anyone remembers or not. Blind priming at session start is how a
narrative gets absorbed as truth; an injected, labeled worklist is how it gets checked.

Read-only. Never writes to LORE, never writes a file.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

TIMEOUT_SECONDS = 3  # PROVISIONAL — owner: wright. Deliberately shorter than the wrapper's
                      # outer `timeout 5`, so this connect timeout can actually fire (and
                      # produce a useful psycopg2 error) instead of being unreachable dead code
                      # preempted by the outer kill, per session_probe.py's stripped pattern.
MAX_CHARS = 4000  # PROVISIONAL — unvalidated, owner: wright. keep injected context bounded;
                   # truncation is marked, never silent

# The tag /lore-close writes on its Step-4 closing capture (see
# ~/.claude/commands/lore-close.md Step 4). Deterministic: a capture either carries it or
# doesn't — no more inferring "is this a close-out?" from document_type.
QUEUE_TAG = "session-queue"

# S2 Round 3 (docs/tooling/session-queue-hardening.md §3): the writing session's own ID,
# recorded by /lore-close Step 4 inside a "session-queue-meta:" fenced block (sibling to
# S3's "git-state:" block), so the reader can exclude the WRITER's transcript — not just
# the reader's own — from the staleness scan. A capture written before this field existed
# (or with a malformed value) yields no match here, which is the UNKNOWN branch, not a
# false "writer excluded" or "no writer".
WRITER_SESSION_ID_RE = re.compile(
    r"^\s*writer-session-id:\s*([0-9a-f-]{36})\s*$", re.IGNORECASE | re.MULTILINE
)


def extract_writer_session_id(content):
    """Parse the writer-session-id out of a capture's content, per §3's regex. Returns the
    UUID string, lowercased, if present and well-formed, else None (absent field and
    malformed field are treated identically — both mean "writer unknown", per the
    architecture doc's explicit call not to distinguish them).

    Lowercased here, at the single point of extraction, rather than at the point main()
    builds the exclusion filename: this is the one choke point every current and future
    caller passes through, so normalization can't be skipped by a caller that forgets to
    lowercase downstream. The regex itself stays case-insensitive (re.IGNORECASE) so a
    hand-edited or corrupted uppercase value still parses as "writer known" instead of
    silently falling through to UNKNOWN — it's normalized, not rejected. Real Claude Code
    session transcript filenames on disk are lowercase UUIDs, so the exclusion filename
    built from this value (f"{writer_id}.jsonl") must be lowercase to ever match reality."""
    if not content:
        return None
    match = WRITER_SESSION_ID_RE.search(content)
    if not match:
        return None
    return match.group(1).lower()


def load_database_url():
    """Read DATABASE_URL from agent-lore's env file. That file is the single source."""
    env_path = os.path.expanduser("~/runtime/agent-lore/.env")
    if not os.path.exists(env_path):
        return None, f"env file not found at {env_path}"
    with open(env_path) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("DATABASE_URL"):
                _, _, value = line.partition("=")
                return value.strip().strip('"').strip("'"), None
    return None, f"DATABASE_URL not present in {env_path}"


def project_id_for(repo_dir):
    """Derive projectId from the repo's CLAUDE.md, which declares it. No guessing."""
    claude_md = os.path.join(repo_dir, "CLAUDE.md")
    if not os.path.exists(claude_md):
        return None, "CLAUDE.md not found — cannot determine projectId"
    with open(claude_md, errors="replace") as fh:
        text = fh.read()
    match = re.search(r"[Pp]roject\s*ID[^\n`]*[`\"']([a-z0-9][a-z0-9._-]*)[`\"']", text)
    if not match:
        match = re.search(r"projectId[:\s]+[`\"']([a-z0-9][a-z0-9._-]*)[`\"']", text)
    if not match:
        return None, "no projectId declared in CLAUDE.md"
    return match.group(1), None


def fetch_tagged_queue(database_url, project_id):
    """The queue: tagged AND not superseded, newest-first. Tag alone is not enough — a
    tagged row can itself be superseded by a later tagged (or untagged) correction, and a
    tag-only query would return the stale one. See INTAKE §S1 for the live counterexample
    (2026-08-10 close-out superseded 22 minutes later by a push-state correction)."""
    import psycopg2

    conn = psycopg2.connect(database_url, connect_timeout=TIMEOUT_SECONDS)
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.title, d.content, d.author, d.created_at, d.id, d.document_type
                FROM documents d
                WHERE d.project_id = %s
                  AND d.tags @> ARRAY[%s]::text[]
                  AND NOT EXISTS (
                      SELECT 1 FROM documents s WHERE s.supersedes_id = d.id
                  )
                ORDER BY d.created_at DESC
                LIMIT 1
                """,
                (project_id, QUEUE_TAG),
            )
            return cur.fetchone()
    finally:
        conn.close()


def fetch_most_recent_untagged(database_url, project_id):
    """First-run transition support (INTAKE §7): if no tagged queue exists, tell the
    difference between "no captures at all" and "captures exist but predate this
    convention" by looking at the most recent capture regardless of tag."""
    import psycopg2

    conn = psycopg2.connect(database_url, connect_timeout=TIMEOUT_SECONDS)
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT d.title, d.created_at
                FROM documents d
                WHERE d.project_id = %s
                  AND NOT EXISTS (
                      SELECT 1 FROM documents s WHERE s.supersedes_id = d.id
                  )
                ORDER BY d.created_at DESC
                LIMIT 1
                """,
                (project_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def read_hook_stdin():
    """SessionStart hooks receive JSON on stdin, including session_id and transcript_path.
    Used to self-exclude the currently-running session's own transcript from the staleness
    scan (INTAKE §S2) — without this a session's own startup write makes the check fire
    100% of the time. Best-effort: absence or malformed stdin must not break the hook."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def transcripts_dir_for(repo_dir):
    """Claude Code's on-disk transcript directory naming: '/' -> '-', leading '-' kept.
    e.g. /home/d-tuned/agent-rig -> ~/.claude/projects/-home-d-tuned-agent-rig"""
    slug = "-" + repo_dir.strip("/").replace("/", "-")
    return os.path.join(os.path.expanduser("~/.claude/projects"), slug)


def newer_session_transcripts(repo_dir, since_dt, exclude_names):
    """Count + list main-session transcripts (top-level '<session-id>.jsonl' files) newer
    than `since_dt`, excluding names in `exclude_names`.

    Decision (INTAKE §S2, "second detail"): scan is NON-RECURSIVE — only the top-level
    directory, not subdirectories. Sub-agent dispatches write their transcripts into a
    nested '<session-id>/subagents/*.jsonl' path, one level below the top-level
    '<session-id>.jsonl' main-session file (verified on disk 2026-08-13: 7 top-level
    session transcripts vs 159 total files including sub-agent dispatches in
    agent-rig's own transcript dir). A non-recursive listdir() naturally excludes
    sub-agent noise without needing a separate filter — chosen over a recursive walk
    plus pattern-matching because it needs no additional convention to stay correct if
    the sub-agent directory layout changes shape, only if it changes depth.

    mtime normalization: os.stat mtimes are POSIX epoch seconds (tz-agnostic by
    construction); converting with datetime.fromtimestamp(mtime, tz=timezone.utc) yields
    an aware UTC datetime directly comparable to Postgres's tz-aware `created_at` without
    a separate local-tz lookup.
    """
    d = transcripts_dir_for(repo_dir)
    if not os.path.isdir(d):
        return []
    found = []
    for name in os.listdir(d):
        if not name.endswith(".jsonl"):
            continue
        if name in exclude_names:
            continue
        path = os.path.join(d, name)
        if not os.path.isfile(path):
            continue
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        if mtime_dt > since_dt:
            found.append((name, mtime_dt))
    found.sort(key=lambda pair: pair[1], reverse=True)
    return found


def emit(context_text):
    """SessionStart hooks communicate by printing this JSON shape on stdout."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context_text,
        }
    }))


HEADER = (
    "SESSION QUEUE — SIGNPOST, NOT PILLAR.\n\n"
    "What follows is the tagged ('session-queue') capture for this project. It is a list of "
    "CLAIMS, not facts. It was true when written and may not be true now: commits move, "
    "branches merge, other agents act, and the writer may simply have been wrong. See the "
    "PROVENANCE line below for what kind of capture this actually is.\n\n"
    "USE IT AS A WORKLIST, NOT AN ANSWER. Take each item, open the primary source it points "
    "at, and confirm it yourself before you assert it to anyone. Reading this text is not "
    "verification. Restating it is not verification.\n\n"
    "This injection also does NOT satisfy memory priming — it is one capture, not a search. "
    "Use search_knowledge deliberately, aimed by the items below, when you need more.\n"
)

FOOTER = (
    "\n\nEND QUEUE. Nothing above is verified. Your first-turn summary must label what you "
    "took from here as `Signpost:` and label separately, as `Pillar:`, only what you have "
    "independently checked this session and by what method."
)


def main():
    repo_dir = os.getcwd()

    hook_input = read_hook_stdin()
    self_transcript_path = hook_input.get("transcript_path")
    self_session_id = hook_input.get("session_id")
    exclude_names = set()
    if self_transcript_path:
        exclude_names.add(os.path.basename(self_transcript_path))
    if self_session_id:
        exclude_names.add(f"{self_session_id}.jsonl")

    project_id, err = project_id_for(repo_dir)
    if err:
        emit(f"SESSION QUEUE UNAVAILABLE — {err}. No queue was loaded; do not assume there is "
             f"nothing queued. Check LORE manually with search_knowledge.")
        return 0

    database_url, err = load_database_url()
    if err:
        emit(f"SESSION QUEUE UNAVAILABLE — {err}. No queue was loaded; do not assume there is "
             f"nothing queued. Check LORE manually with search_knowledge.")
        return 0

    try:
        row = fetch_tagged_queue(database_url, project_id)
    except Exception as exc:  # noqa: BLE001 — a hook must never break session start
        emit(f"SESSION QUEUE UNAVAILABLE — LORE query failed for project '{project_id}': "
             f"{exc.__class__.__name__}: {exc}. No queue was loaded; this is NOT evidence that "
             f"nothing is queued. Check manually with search_knowledge before proceeding.")
        return 0

    if row is None:
        # First-run transition (INTAKE §7): tell "never closed" apart from "closed, but
        # predates the tag convention" — a second, cheap query, not a guess.
        try:
            untagged_row = fetch_most_recent_untagged(database_url, project_id)
        except Exception:
            untagged_row = None

        if untagged_row is None:
            emit(f"SESSION QUEUE EMPTY — no tagged ('{QUEUE_TAG}') capture found for project "
                 f"'{project_id}', and no captures exist for this project at all. The query "
                 f"succeeded and returned nothing, so this is a real empty, not a failure.")
        else:
            untagged_title, untagged_created_at = untagged_row
            emit(f"NO TAGGED QUEUE FOUND for project '{project_id}' — but captures exist that "
                 f"predate this convention. Most recent: \"{untagged_title}\" "
                 f"({untagged_created_at}). This does NOT mean the project has never been "
                 f"closed; it means no /lore-close run since the '{QUEUE_TAG}' tag was "
                 f"introduced has captured a queue yet. Check that capture manually with "
                 f"search_knowledge or get_document if you need it.")
        return 0

    title, content, author, created_at, doc_id, document_type = row
    body = content or ""
    truncated = ""
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS]
        truncated = (f"\n\n[TRUNCATED at {MAX_CHARS} chars — this is NOT the whole capture. "
                     f"Read the rest with get_document('{doc_id}') before relying on it.]")

    # Cross-check: a bare tag hit is not trusted on its own. Compare against the newest
    # non-superseded capture regardless of tag — if something more recent exists and isn't
    # tagged, that is a discrepancy to report, not adjudicate (INTAKE gate finding
    # 2026-08-13: hand-tagged captures can predate this convention and outrank a real
    # close-out that never got tagged).
    try:
        untagged_row = fetch_most_recent_untagged(database_url, project_id)
    except Exception:
        untagged_row = None

    if untagged_row is not None and untagged_row[1] > created_at:
        untagged_title, untagged_created_at = untagged_row
        provenance = (
            f"PROVENANCE: retrieved by tag = '{QUEUE_TAG}' — newest non-superseded capture "
            f"carrying that tag, written {created_at} by '{author}'. document_type = "
            f"'{document_type}'.\n\n"
            f"DISCREPANCY: a more recent non-superseded capture exists for this project that "
            f"is NOT tagged '{QUEUE_TAG}': \"{untagged_title}\" ({untagged_created_at}). This "
            f"could mean the tag predates the convention that keeps it current, or that a "
            f"later close-out simply wasn't tagged. The code cannot tell you which — check "
            f"both with get_document before trusting either as the queue."
        )
    else:
        provenance = (
            f"PROVENANCE: retrieved by tag = '{QUEUE_TAG}' — newest non-superseded capture "
            f"carrying that tag, written {created_at} by '{author}'. document_type = "
            f"'{document_type}'. It is still a claim, not a fact — verify its contents "
            f"against primary sources before trusting it."
        )

    # Staleness check (docs/tooling/session-queue-hardening.md §2b/§3, Round 3): has anyone
    # run a session since this queue was written, without closing again? Excludes the
    # reading session's own transcript, and — when known — the WRITING session's transcript
    # too (which otherwise always postdates its own capture via /lore-close Steps 5-7, and
    # would make the count always fire; see the architecture doc's "always fires" finding).
    writer_id = extract_writer_session_id(content)
    writer_known = writer_id is not None
    if writer_known:
        exclude_names.add(f"{writer_id}.jsonl")
        stale_transcripts = newer_session_transcripts(repo_dir, created_at, exclude_names)
        if stale_transcripts:
            dates = ", ".join(
                f"{name} ({mtime_dt.isoformat()})" for name, mtime_dt in stale_transcripts
            )
            staleness = (
                f"\n\nSTALENESS: {len(stale_transcripts)} session(s) have run since this queue "
                f"was written ({created_at}) and closed, excluding the writer's own close-out "
                f"and this reading session, and produced no newer tagged queue. These may have "
                f"ended without closing: {dates}"
            )
        else:
            staleness = (
                "\n\nSTALENESS: no session has run since this queue was written and closed, "
                "other than the writer's own close-out steps (excluded) and this reading "
                "session (excluded). Consistent with a clean handoff."
            )
    else:
        staleness = (
            "\n\nSTALENESS UNKNOWN — this capture predates the writer-session-id field (or "
            "the field is missing/malformed), so this queue's own writer cannot be "
            "distinguished from a session that ran afterward and didn't close. No count is "
            "asserted; check `git log`, `git status`, and recent transcripts manually before "
            "trusting this queue's currency."
        )

    emit(
        f"{HEADER}\n"
        f"--- Tagged queue for '{project_id}' ---\n"
        f"Title:   {title}\n"
        f"Author:  {author}\n"
        f"Written: {created_at}\n"
        f"Doc ID:  {doc_id}\n"
        f"Type:    {document_type}\n\n"
        f"{provenance}\n"
        f"{staleness}\n\n"
        f"{body}{truncated}"
        f"{FOOTER}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
