#!/usr/bin/env python3
"""SessionStart queue injection — the signpost half.

Reads the most recent canonical LORE capture for this project and injects it into the
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

TIMEOUT_SECONDS = 3  # PROVISIONAL — owner: wright. Deliberately shorter than the wrapper's
                      # outer `timeout 5`, so this connect timeout can actually fire (and
                      # produce a useful psycopg2 error) instead of being unreachable dead code
                      # preempted by the outer kill, per session_probe.py's stripped pattern.
MAX_CHARS = 4000  # PROVISIONAL — unvalidated, owner: wright. keep injected context bounded;
                   # truncation is marked, never silent

# documentTypes that /lore-close writes on a proper session close-out (see
# ~/.claude/commands/lore-close.md Step 4). Any other type on the top row means this project
# captures mid-session too, and the row is NOT a closing account.
CLOSE_OUT_TYPES = ("decision", "review")


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


def fetch_queue(database_url, project_id):
    import psycopg2

    conn = psycopg2.connect(database_url, connect_timeout=TIMEOUT_SECONDS)
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute(
                """
                -- Canonical = not superseded by any later capture. The schema records the
                -- relationship one way only (documents.supersedes_id -> the doc it replaces),
                -- so "superseded" is expressed as: some other row points at me.
                SELECT d.title, d.content, d.author, d.created_at, d.id, d.document_type
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
    "What follows is the most recent canonical capture for this project. It is a list of "
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
        row = fetch_queue(database_url, project_id)
    except Exception as exc:  # noqa: BLE001 — a hook must never break session start
        emit(f"SESSION QUEUE UNAVAILABLE — LORE query failed for project '{project_id}': "
             f"{exc.__class__.__name__}: {exc}. No queue was loaded; this is NOT evidence that "
             f"nothing is queued. Check manually with search_knowledge before proceeding.")
        return 0

    if row is None:
        emit(f"SESSION QUEUE EMPTY — no canonical capture found for project '{project_id}'. "
             f"The query succeeded and returned nothing, so this is a real empty, not a failure.")
        return 0

    title, content, author, created_at, doc_id, document_type = row
    body = content or ""
    truncated = ""
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS]
        truncated = (f"\n\n[TRUNCATED at {MAX_CHARS} chars — this is NOT the whole capture. "
                     f"Read the rest with get_document('{doc_id}') before relying on it.]")

    if document_type in CLOSE_OUT_TYPES:
        provenance = (
            f"PROVENANCE: document_type = '{document_type}'. This is consistent with a proper "
            f"session close-out (see /lore-close), so it MAY be the last session's own account "
            f"of where it left off — but the type alone doesn't prove the session actually "
            f"closed cleanly. Verify against primary sources before trusting it as a close."
        )
    else:
        provenance = (
            f"PROVENANCE: document_type = '{document_type}'. This is NOT a session close-out "
            f"type — it is a mid-session capture. That means the last session most likely ended "
            f"WITHOUT a proper close (crash, compaction, abandoned terminal), and there is no "
            f"closing account to rely on. Treat this as a partial, in-flight snapshot, not a "
            f"summary of where things landed."
        )

    emit(
        f"{HEADER}\n"
        f"--- Most recent capture for '{project_id}' ---\n"
        f"Title:   {title}\n"
        f"Author:  {author}\n"
        f"Written: {created_at}\n"
        f"Doc ID:  {doc_id}\n"
        f"Type:    {document_type}\n\n"
        f"{provenance}\n\n"
        f"{body}{truncated}"
        f"{FOOTER}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
