# Spec — Hook Telemetry: Normalized Schema + Aggregator

**Status**: LOCKED

Cites: `docs/tooling/hook-telemetry-schema/INTAKE.md` (APPROVED). This spec covers Intake items
1–4. No behavior change to any hook's block/allow decision logic — only to what gets logged.

---

## 1. Problem Recap

Three live probes each build their own ad hoc track-record dict and write it independently:

- `scripts/signpost_checklist_probe.py::write_track_record` — fields: `timestamp`,
  `session_id`, `stop_hook_active`, `queue_injected`, `first_turn`, `decision`, `violations`,
  `reason`, `probe_error`. Writes to `TRACK_RECORD_PATH` (repo-root-relative,
  `docs/tooling/signpost-checklist-track-record.jsonl`, env-overridable via
  `SIGNPOST_TRACK_RECORD_PATH`).
- `scripts/no_preamble_probe.py::write_track_record` — fields: `timestamp`, `session_id`,
  `stop_hook_active`, `mode`, `decision`, `flagged_clauses`, `reason`, `probe_error`. Writes to
  `docs/tooling/no-preamble-no-meta-narration-track-record.jsonl`.
- `scripts/progress_proof_per_slice_probe.py::write_track_record` — takes a pre-built `entry`
  dict from `build_track_record_entry`: `timestamp`, `session_id`, `file_path`,
  `file_in_scope`, `transitions_found`, `transitions_verified`, `matched_by`, `proof_status`,
  `decision`, `reason`, `probe_error`. Path is **project-dir-relative** (per-invocation
  `project_dir`, not a fixed repo path), at `TRACK_RECORD_RELATIVE_PATH`
  (`docs/tooling/progress-proof-per-slice-track-record.jsonl` under that project dir).

Three more writers exist alongside these three probes — one `write_probe_error()` shell
function per wrapper, all three wired in `.claude/settings.json`: `.claude/hooks/
signpost-checklist.sh::write_probe_error`, `.claude/hooks/no-preamble-no-meta-narration.sh::
write_probe_error`, and `.claude/hooks/progress-proof-per-slice.sh::write_probe_error`. Each
shells out to an embedded Python heredoc to build its own flat dict (fields: `timestamp`,
`session_id`, `stop_hook_active` (signpost/no-preamble only), `queue_injected`/`first_turn`
(signpost, hardcoded `False`), `mode` (no-preamble, read from the probe module where importable),
`decision` (hardcoded `"probe_error"`), `reason`, `probe_error`), appended to the same jsonl path
the corresponding probe itself writes to. All three fire only on their wrapper's own failure paths
(timeout, non-zero probe exit, malformed stdout) — cases where the probe itself never ran far
enough to write its own line. (`.claude/hooks/domain-boundary-provenance.sh` has the same
`write_probe_error` pattern too, but that hook is sunset and out of scope for this spec — not
touched, not inventoried further here.)

Shared across all six writers today (three probes, three wrapper fallbacks): `timestamp`,
`session_id`, `decision`, `reason`, `probe_error`. Everything else is hook-specific and was
invented independently. `scripts/signpost_checklist_summary.py` reads only the signpost log and
hardcodes its field names.

## 2. Components

| Component | Responsibility | Location |
|---|---|---|
| `TelemetryEvent` (schema) | Defines the normalized envelope every probe emits | `scripts/hook_telemetry.py` (new) |
| `write_telemetry_event()` | Shared writer: builds envelope, appends to a hook's local `.jsonl`, calls the Postgres stub | `scripts/hook_telemetry.py` (new) |
| `write_telemetry_pg()` | Postgres write-path stub — targets a new, separate `homelab_telemetry` database on the same Postgres host documented in this repo's CLAUDE.md, PROVISIONAL, no-op until that database is provisioned | `scripts/hook_telemetry.py` (new) |
| Per-probe adapter calls | Each probe replaces its own `write_track_record`/`build_track_record_entry` with one call to `write_telemetry_event()`, passing its existing fields as `payload` | `scripts/signpost_checklist_probe.py`, `scripts/no_preamble_probe.py`, `scripts/progress_proof_per_slice_probe.py` (edited) |
| `hook_telemetry_aggregate.py` | General aggregator: reads all normalized `.jsonl` logs, reports fire counts / decision breakdown / error rate per-hook and combined | `scripts/hook_telemetry_aggregate.py` (new, replaces `scripts/signpost_checklist_summary.py`) |
| `write_probe_error()` (all three wrappers, migrated) | Each wrapper's shell-embedded fallback writer now shells out via the same `sys.path.insert(0, os.path.join(repo_dir, "scripts"))` shim already proven in `.claude/hooks/no-preamble-no-meta-narration.sh:46-50`, imports `write_telemetry_event` from `scripts/hook_telemetry.py`, and calls it with `decision="probe_error"` and the wrapper's own failure-path fields under `payload` | `.claude/hooks/signpost-checklist.sh`, `.claude/hooks/no-preamble-no-meta-narration.sh`, `.claude/hooks/progress-proof-per-slice.sh` (all three edited) |

`scripts/signpost_checklist_summary.py` is retired (deleted) once the aggregator covers its
output; see §6.

**Disposition of `write_probe_error()` (all three wrappers):** migrated to call the shared
`write_telemetry_event()`, not left as tolerated legacy. The shim this requires — a standalone
Python heredoc adding `scripts/` to `sys.path` before importing a repo module — is not new,
speculative complexity: `.claude/hooks/no-preamble-no-meta-narration.sh:46-50` already pays this
exact cost today (`sys.path.insert(0, os.path.join(repo_dir, "scripts"))` then `from
no_preamble_probe import MODE`), for the same reason (a heredoc has no package context). Reusing
that proven pattern to import `write_telemetry_event` instead of `MODE` is the same shape of call,
not a new one. Separately, live logs show zero `probe_error` lines observed across all three logs
as of spec time (2026-09-07) — a path that has never fired in production is the cheapest one to migrate, since there is
no historical data whose shape would need reconciling. Each migrated wrapper passes its existing
failure-path fields (`stop_hook_active`, `queue_injected`, `first_turn`, `mode`, etc., whichever
apply to that hook) under `payload`, exactly as its sibling probe already does per §9, so a
wrapper's own failure line and its probe's success lines share one envelope shape in the same
file going forward. §12's Intake-item-1 coverage claim ("one shared writer") now covers wrapper
failure paths too, with no remaining carve-out.

## 3. Data Schema

```python
# scripts/hook_telemetry.py

from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass(frozen=True)
class TelemetryEvent:
    """Normalized hook-telemetry envelope. Every probe migrated to this schema constructs one of
    these (directly or via write_telemetry_event's kwargs) instead of building its own ad hoc
    dict. `payload` carries every field that is specific to one hook and not shared across the
    probes today. Real contract, stated plainly: new lines written after migration use this
    envelope shape (hook-specific fields nested under `payload`); existing flat lines already on
    disk are left exactly as they are, in place, never rewritten or migrated. All six writers
    (§1, §2) — the three probes and their three wrapper `write_probe_error()` fallbacks — emit
    the new envelope shape going forward. Consequently, `hook_telemetry_aggregate.py` (§4) is
    required to read both shapes from the same file — envelope lines with a `payload` key, and
    flat legacy lines already on disk from before this migration, with hook-specific fields at
    the top level — not to assume every line in a `.jsonl` file is one shape.
    """
    hook_name: str            # e.g. "signpost-checklist", "no-preamble-no-meta-narration",
                               # "progress-proof-per-slice" — stable per-probe identifier
    timestamp: str             # datetime.now(timezone.utc).isoformat(), same as today
    session_id: Optional[str]
    decision: str               # "allow" | "block" | "deny" | "flagged" | "probe_error"
                                 # (union of values actually emitted by the six writers today,
                                 # incl. progress_proof_per_slice_probe.py's "deny" —
                                 # scripts/progress_proof_per_slice_probe.py:450; not a closed
                                 # enum — a probe introducing a new decision value is not a
                                 # schema violation, the aggregator treats unknown decisions as
                                 # pass-through, see §4 summarize()). No normalization happens
                                 # here or anywhere in the writer: the writer records `decision`
                                 # exactly as emitted by the probe, always as a single top-level
                                 # string, never remapped and never duplicated into `payload`.
                                 # "deny" stays "deny" on disk. The one deny-counts-as-block
                                 # normalization this schema needs for aggregate/rate purposes is
                                 # applied later, read-side, in hook_telemetry_aggregate.py's
                                 # summarize() — see §4 — because that is the only place that sees
                                 # both legacy flat-shape lines (which already say "deny") and new
                                 # envelope-shape lines, across all history.
    reason: Optional[str]
    probe_error: Optional[str]
    payload: dict[str, Any] = field(default_factory=dict)
```

No new predetermined constants: `hook_name` values are the probes' own existing identifiers
(literal strings already implied by each script's filename/log-name), not invented thresholds.

## 4. API Contracts

```python
# scripts/hook_telemetry.py

def write_telemetry_event(
    *,
    hook_name: str,
    jsonl_path: str,
    session_id: str | None,
    decision: str,
    reason: str | None,
    probe_error: str | None,
    payload: dict,
) -> None:
    """Builds a TelemetryEvent, appends it as one JSON line to `jsonl_path`, then calls
    write_telemetry_pg() with the same event. Best-effort: never raises into the caller (same
    contract as every existing write_track_record — the track record is an audit trail, not a
    gate, per each probe's own existing comment). `jsonl_path` is passed by the caller, not
    computed here, because progress_proof_per_slice_probe.py's path is project-dir-relative
    (resolved per-invocation from stdin's project_dir) while the other two are repo-relative
    module constants — the writer does not assume either shape. No decision normalization
    happens here: `decision` is written to the top-level field exactly as the caller passes it
    (e.g. progress_proof_per_slice_probe.py's "deny", scripts/progress_proof_per_slice_probe.py:
    450, is written as "deny", not remapped), and `payload` never gets a conditional `decision`
    key — payload's keyset is whatever the caller passes, independent of the decision value. The
    one deny-counts-as-block normalization this schema needs is read-side, in
    hook_telemetry_aggregate.py's summarize() — see below — not writer-side."""

def write_telemetry_pg(event: TelemetryEvent) -> None:
    """PROVISIONAL — targets a new, separate `homelab_telemetry` database on
    the same Postgres host documented in this repo's CLAUDE.md (agent-rig-owned, not a table in
    the shared `lore` database — see §7). v1 body is a no-op: does not open a connection, does not write, does not raise. Exists
    now only so call sites in the three probes and the writer above do not need a second edit
    once the database is provisioned — only this function's body changes."""

def to_jsonl_line(event: TelemetryEvent) -> str:
    """Serializes a TelemetryEvent to one JSON line using the same flat-dict shape probes emit
    today, with hook-specific fields nested under 'payload' instead of top-level. Used by
    write_telemetry_event(); exposed separately so probes/tests can construct a line without
    performing the file I/O."""
```

```python
# scripts/hook_telemetry_aggregate.py

def load_events(jsonl_path: str) -> list[dict]:
    """Best-effort JSONL read: missing file -> [], malformed line -> skipped. Same contract as
    signpost_checklist_summary.py's existing load_entries()."""

def summarize(events: list[dict]) -> dict:
    """Pure function, no I/O. Returns: {"total": int, "decision_counts": dict[str, int],
    "block_side_count": int, "error_count": int, "error_rate": float, "first_ts": str | None,
    "last_ts": str | None}. error_count / error_rate is derived from `probe_error is not None`,
    not from a `decision == "probe_error"` string match, since not every probe necessarily uses
    that literal value for all error paths — counting on the dedicated field is the more general
    and already-present signal every schema carries. `decision_counts` is a raw tally keyed on
    whatever string literally appears in each event's top-level `decision` field — no vocabulary
    mapping, so "deny" and "block" remain separate keys there. The one normalization this schema
    needs (deny counts as block-side for aggregate/rate purposes) is applied here, once, on top
    of that raw tally: `block_side_count = decision_counts.get("block", 0) +
    decision_counts.get("deny", 0)`. This is the only place in the whole telemetry path that
    performs this mapping, and it is applied uniformly to both shapes of input line —
    legacy flat-shape lines written before this spec (which already say "deny" at top level) and
    new envelope-shape lines (which, per §4 write_telemetry_event, also say "deny" verbatim,
    since the writer no longer remaps) — because summarize() is the only function that sees both
    shapes across all history."""

def print_report(per_hook: dict[str, dict], combined: dict) -> None:
    """Prints fire count, decision breakdown (with percentages), and error rate for each hook
    (keyed by hook_name / its known jsonl path) and once combined across all of them. Read-only
    against all logs — never writes to them, same discipline as the summary script it
    replaces."""

# Known hook -> jsonl path table, mirroring each probe's own TRACK_RECORD_PATH /
# TRACK_RECORD_RELATIVE_PATH constants — not a magic list because every value here is a
# hook's own existing, already-defined path constant, not an invented one:
HOOK_LOG_PATHS: dict[str, str]
```

## 5. Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Shared writer, per-call `payload` dict | `write_telemetry_event()` | Matches Intake item 1 exactly: one function, hook-specific data stays a dict rather than forcing a shared dataclass to grow one field per hook. |
| Append-only JSONL, best-effort write | `write_telemetry_event()` -> local `.jsonl` | Existing convention in all three probes (`try/except: pass`, track record is audit trail not gate) — no reason to change it, and Intake item 2 explicitly says no relocation. |
| No-op stub for the Postgres path | `write_telemetry_pg()` | Intake item 3 explicitly prefers a stub over inventing a schema unilaterally; the target is a new, separate `homelab_telemetry` database on the same Postgres host documented in this repo's CLAUDE.md, owned by agent-rig, still pending provisioning/infra confirmation before the stub body can write. |
| Pure summarize / impure print split | `hook_telemetry_aggregate.py` | Matches the existing `signpost_checklist_summary.py` shape (`load_entries` / `print_summary` split) — same testability property, extended to multiple logs. |

### Anti-Patterns (Do Not Use)

- Renaming or dropping any existing top-level field (`session_id`, `decision`, `reason`,
  `probe_error`) when moving hook-specific fields into `payload` — Intake item 2 requires
  existing flat lines untouched in place and the aggregator to read both shapes (see §3), not a
  breaking change to either.
- Inventing a Postgres table/column schema in this spec and marking it "final" — Intake item 3
  is explicit that schema design waits for the new database to be provisioned; see §7.
- A single aggregator function that both reads files and prints — breaks the pure/impure split
  the existing summary script already established and this spec continues.

## 6. Retirement of `signpost_checklist_summary.py`

`hook_telemetry_aggregate.py` supersedes it. The existing script's per-hook output (gating
breakdown: `stop_hook_active` bypass / `queue_injected` / `first_turn` counts, decision
breakdown, block-reason detail) is signpost-specific — those stay inside `payload` for the
signpost hook and the aggregator's core report (fire count / decision breakdown / error rate)
covers the cross-hook case Intake item 4 asks for. `scripts/signpost_checklist_summary.py` is
untracked (`git status --porcelain` shows `??`, confirmed at spec time) — there is no repo history
to retire it from. Once `hook_telemetry_aggregate.py` is in place and covers its callers (none
found in `scripts/` or CI at spec time — confirm at forge time before deleting, per this repo's
verify-before-marking-done discipline), the correct action is deleting the file from the working
tree, not any git-history operation.

## 7. Postgres Write-Path — target decided, PROVISIONAL pending provisioning

Per Danny's direct preference (2026-09-07), the destination is now decided as the default
direction, superseding the "propose a shared-DB table" framing this section originally carried:

- **Target:** a new database, tentatively named `homelab_telemetry`, on the same Postgres server
  (documented in this repo's CLAUDE.md) that hosts `lore` — **not** a new table or schema inside the existing
  `lore` database. Danny's stated reasoning (via the orchestrator, confirmed by him): telemetry
  is high-frequency/operational/disposable, LORE is curated/embedded/semantic — different data
  shapes, different owners, different access patterns. Mixing them would put every telemetry
  field under agent-lore's sign-off on their production knowledge store, which is real
  coordination overhead for no benefit. A separate database, wholly owned by agent-rig, avoids
  that coupling entirely. `homelab_telemetry` is a proposed name only — confirm or rename it at
  provisioning time, it is not load-bearing anywhere in this spec's design.
- **What actually still needs coordination:** since this is agent-rig's own database rather than
  a schema addition to agent-lore's `lore` database, the open item shifts from "agent-lore schema
  sign-off on our fields" to a lighter infra question — can a new database be provisioned on
  that Postgres instance (see this repo's CLAUDE.md), and who holds the credentials/access to create one.
  That's still worth a quick check with agent-lore or whoever administers that Postgres instance
  (they may be the only one with CREATE DATABASE rights on that server), but it is a much smaller
  ask than review of production knowledge-store schema — this repo isn't asking to touch `lore`
  at all.
- **Why a stub instead of a proposed schema:** table/column design for `homelab_telemetry` still
  isn't defined here — Intake item 3 asks this spec to prefer a no-op interface over inventing a
  schema unilaterally, and that discipline is unchanged by deciding the destination database. A
  stub satisfies Intake items 1, 2, and 4 fully today without blocking on provisioning, and gives
  every probe a single call site (`write_telemetry_pg`) that starts writing the moment
  `homelab_telemetry` exists and its schema is defined, with no second round of edits to the
  three probes themselves.
- **v1 behavior:** `write_telemetry_pg()` takes a `TelemetryEvent`, does nothing, returns
  `None`. No connection, no environment variable read, no schema constant defined anywhere in
  this codebase — there is nothing here to source or fabricate a number for.
- **Follow-up:** a future sprint (not this one) provisions `homelab_telemetry`, defines its
  table/column schema, and fills in this function's body. That sprint's own spec is where any
  table/column constants and the connection string get defined and cited — not here.

## 8. Downstream-Consumer Context (informational only, not designed here)

`agent-dashboard` (`/home/d-tuned/projects/agent-dashboard`) is a read-only, single-user,
Tailscale-only dashboard (per its Northstar) that already has Next.js API routes reading from
the shared `lore` Postgres database (`src/app/api/{open-work,session-closes,ddr-pipeline,
activity-feed,agents,projects}/route.ts`) in a route-per-domain pattern. Telemetry per §7 lands
in a separate `homelab_telemetry` database, not `lore` — so a future `agent-dashboard` route
reading telemetry would need its own connection to that second database, not a reuse of its
existing `lore` connection. Noted here only because it confirms the normalized envelope in §3
(flat fields + one JSON payload column) is a reasonable shape for that kind of consumer, not
because this spec designs agent-dashboard's side. That work is explicitly out of scope (per
Intake) and belongs to a separate Intake in that repo.

## 9. Integration Points

- `scripts/signpost_checklist_probe.py` — its `write_track_record` call sites are replaced with
  `write_telemetry_event(hook_name="signpost-checklist", jsonl_path=TRACK_RECORD_PATH, ...,
  payload={"stop_hook_active": ..., "queue_injected": ..., "first_turn": ..., "violations":
  ...})`. `TRACK_RECORD_PATH` constant is unchanged.
- `scripts/no_preamble_probe.py` — same replacement, `hook_name="no-preamble-no-meta-narration"`,
  `payload={"stop_hook_active": ..., "mode": ..., "flagged_clauses": ...}`.
- `scripts/progress_proof_per_slice_probe.py` — same replacement; `jsonl_path` is computed
  per-invocation from `project_dir` exactly as `write_track_record(project_dir, entry)` does
  today, passed through to `write_telemetry_event`'s `jsonl_path` kwarg;
  `payload={"file_path": ..., "file_in_scope": ..., "transitions_found": ...,
  "transitions_verified": ..., "matched_by": ..., "proof_status": ...}`.
- `scripts/hook_telemetry_aggregate.py` — new entry point, no existing script calls it; replaces
  direct invocation of `scripts/signpost_checklist_summary.py`.
- `.claude/hooks/signpost-checklist.sh::write_probe_error` — migrated per §2's disposition: adds
  the `sys.path.insert(0, os.path.join(repo_dir, "scripts"))` shim, imports
  `write_telemetry_event` from `scripts/hook_telemetry.py`, calls it with
  `hook_name="signpost-checklist"`, `jsonl_path=SIGNPOST_TRACK_RECORD_PATH`,
  `decision="probe_error"`, `payload={"stop_hook_active": ..., "queue_injected": False,
  "first_turn": False}`. Writes envelope lines into the same file
  `signpost_checklist_probe.py` writes to.
- `.claude/hooks/no-preamble-no-meta-narration.sh::write_probe_error` — same shim pattern (already
  present at lines 46-50 of this file for importing `MODE`; extended here to also import
  `write_telemetry_event`); `hook_name="no-preamble-no-meta-narration"`,
  `decision="probe_error"`, `payload={"stop_hook_active": ..., "mode": probe_mode}`.
- `.claude/hooks/progress-proof-per-slice.sh::write_probe_error` — same shim pattern;
  `hook_name="progress-proof-per-slice"`, `jsonl_path` computed per-invocation from
  `project_dir` exactly as the probe's own call does, `decision="probe_error"`,
  `payload={"file_path": ...}` (the wrapper's `write_probe_error` already captures
  `file_path` from stdin `tool_input` —
  `.claude/hooks/progress-proof-per-slice.sh:58-60, 67` — no other failure-path fields
  are captured there today).
  `hook_telemetry_aggregate.py` must still read both shapes out of each hook's file (§3), since
  lines written before this migration remain flat legacy on disk.
- Postgres (same host documented in this repo's CLAUDE.md, target database `homelab_telemetry` — separate from `lore`) — not integrated in v1; see §7.

## 10. Dependencies

None new. Standard library only (`json`, `os`, `datetime`, `dataclasses`, `collections.Counter`
for the aggregator), matching every existing probe and `signpost_checklist_summary.py`.

## 11. Out of Scope (per Intake, carried forward)

- Retrofitting the sunset `domain-boundary-provenance` hook.
- `session_queue_probe.py`'s SessionStart injections (no existing log, not assumed in scope).
- Any `agent-dashboard` UI work (§8 is informational only).
- Finalizing the `homelab_telemetry` database schema and provisioning it (§7 — stub only,
  real schema/provisioning is a future sprint).

## 12. Requirement Coverage

| Intake item | Covered by |
|---|---|
| 1. Normalized envelope + shared writer | §3 `TelemetryEvent`, §4 `write_telemetry_event` |
| 2. Backward-compatible local `.jsonl`, no relocation | §4 `write_telemetry_event`'s `jsonl_path` kwarg (caller-supplied, unchanged paths), §9 per-probe integration |
| 3. Postgres proposal, PROVISIONAL | §7 (destination decided: separate `homelab_telemetry` DB, schema/provisioning still open) |
| 4. General aggregator, retire old summary script | §4 aggregator contracts, §6 |
