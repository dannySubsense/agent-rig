# Hook Telemetry Schema + Aggregator — Tooling Doc

**Status**: LIVE in agent-rig (branch `feature/hook-telemetry-schema`, 2026-09-07). Frank binding
forge-gate PASS, attempt 1/3, 211/211 tests passing (`docs/tooling/hook-telemetry-schema/PROGRESS.md`).
**Spec of record**: `docs/tooling/hook-telemetry-schema/SPEC.md` (LOCKED) — this doc does not
restate its rationale, only what shipped and how to use it.

No behavior change to any hook's actual block/allow/deny decision logic in this sprint — only what
gets logged changed.

---

## 1. What this is

A normalized telemetry envelope (`TelemetryEvent`) and one shared writer
(`write_telemetry_event()`, `scripts/hook_telemetry.py`), replacing six previously-bespoke ad hoc
dict-builders:

- Three probes' own `write_track_record` / `build_track_record_entry` functions:
  `scripts/signpost_checklist_probe.py`, `scripts/no_preamble_probe.py`,
  `scripts/progress_proof_per_slice_probe.py`.
- Three wrapper `write_probe_error()` failure-path fallbacks (fire only when the wrapper's probe
  never ran far enough to write its own line — timeout, non-zero exit, malformed stdout):
  `.claude/hooks/signpost-checklist.sh`, `.claude/hooks/no-preamble-no-meta-narration.sh`,
  `.claude/hooks/progress-proof-per-slice.sh`.

All six now construct one `TelemetryEvent` via `write_telemetry_event()` instead of inventing their
own field sets.

## 2. The schema

```python
# scripts/hook_telemetry.py
@dataclass(frozen=True)
class TelemetryEvent:
    hook_name: str             # "signpost-checklist" | "no-preamble-no-meta-narration" |
                                # "progress-proof-per-slice"
    timestamp: str              # datetime.now(timezone.utc).isoformat()
    session_id: Optional[str]
    decision: str                # e.g. "allow" | "block" | "deny" | "flagged" | "probe_error" —
                                  # not a closed enum; written exactly as the caller passes it,
                                  # never remapped writer-side
    reason: Optional[str]
    probe_error: Optional[str]
    payload: dict[str, Any] = field(default_factory=dict)   # hook-specific fields
```

`write_telemetry_event(*, hook_name, jsonl_path, session_id, decision, reason, probe_error,
payload)` builds the envelope, appends one JSON line to `jsonl_path`, then calls
`write_telemetry_pg()`. Best-effort throughout — never raises into the caller, matching every prior
`write_track_record`'s contract (the track record is an audit trail, not a gate).

**Backward compatibility**: existing flat-shape lines already on disk are never rewritten or
migrated. Only new lines written after this migration use the envelope shape (hook-specific fields
nested under `payload`). `hook_telemetry_aggregate.py` reads both shapes from the same file —
legacy flat lines (hook-specific fields at top level) and new envelope lines — since both carry
`decision` / `probe_error` at the top level, which is all `summarize()` needs.

## 3. Using the aggregator

```bash
python3 scripts/hook_telemetry_aggregate.py
```

Reads all three known hook logs (`signpost-checklist`, `no-preamble-no-meta-narration`,
`progress-proof-per-slice`) via `HOOK_LOG_PATHS`, and prints, per hook and once combined:

- fire count (`total`)
- decision breakdown with percentages (raw tally of whatever string is in `decision` — no
  vocabulary mapping, so `"deny"` and `"block"` stay separate keys)
- `block-side (block+deny)` count — the one normalization the aggregator applies, read-side only,
  on top of the raw tally
- error rate (`probe_error is not None` count / total — not a `decision == "probe_error"` string
  match)
- first/last timestamp seen

`progress-proof-per-slice`'s log path is project-dir-relative (per-invocation, not a fixed
repo-root path). Use `--project-dir <path>` to point the aggregator at that hook's log under a
different project directory; it defaults to this repo's own root.

## 4. Postgres write path — stub, not implemented

`write_telemetry_pg(event: TelemetryEvent) -> None` is a **no-op stub** in this sprint: no
connection, no write, never raises. Target (decided, per Danny 2026-09-07): a new, separate
`homelab_telemetry` database on the same Postgres host that hosts `lore` — not a table inside
`lore` itself, to avoid coupling disposable/high-frequency telemetry to LORE's curated/embedded
knowledge store. `homelab_telemetry` is a proposed name only. Table/column schema and provisioning
are explicitly **not done this sprint** — a future sprint provisions the database, defines its
schema, and fills in this function's body; only this function's body changes when that happens,
every probe call site stays the same.

## 5. Open item carried from Frank's forge-gate (not resolved this sprint)

`reference/no_preamble_probe.py` is a byte-parity mirror of `scripts/no_preamble_probe.py` (that
hook's own drift-guard discipline — correct as a mirror). Post-migration, it imports
`hook_telemetry`, which has **no `reference/` counterpart** — so the mirror is **not
standalone-executable** as of this sprint. This is non-blocking for the forge-gate PASS because the
mirror is never independently invoked (the live hook path is `scripts/no_preamble_probe.py`), but it
is a real, open item, not merely a QC note. It is flagged as a follow-up decision for a future
sprint — either add a `reference/hook_telemetry.py` mirror or make an explicit documented decision
that the mirror is byte-parity-only and no longer standalone-executable. See
`docs/tooling/hook-telemetry-schema/PROGRESS.md` (Slice 1 notes and Forge Gate attempt 1) for the
full finding text.

## 6. Retired

`scripts/signpost_checklist_summary.py` is superseded by `hook_telemetry_aggregate.py` and deleted
(it was untracked in git, no history to retire).

## 7. Dependencies

Standard library only (`json`, `os`, `datetime`, `dataclasses`, `collections.Counter`) — no new
third-party dependency.
