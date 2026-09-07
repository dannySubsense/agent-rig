# Intake — Hook Telemetry: Normalized Schema + Aggregator

**Status**: APPROVED

## Problem

Agent-rig has five hooks (`signpost-checklist`, `no-preamble-no-meta-narration`,
`progress-proof-per-slice`, the unwired/sunset `domain-boundary-provenance`, and
`session-queue`), each writing its own bespoke audit-log schema — only
`timestamp`/`session_id`/`decision`/`reason`/`probe_error` are shared; everything else was
invented independently per hook, with no coordination and no cross-log aggregator. Danny asked
for telemetry (fire count, block/allow rate) without manually running a script each time, growing
toward a real dashboard view over time.

## Proposed Direction

1. A shared, normalized event schema (envelope + per-hook `payload` dict) that every probe
   constructs via one shared writer, replacing each probe's ad hoc dict-building.
2. Short-term: writer keeps emitting to local gitignored `.jsonl` per hook, same locations as
   today, just via the shared schema.
3. Write path into the shared Postgres (the same Postgres host and `lore` database `lore-gateway`
   and `agent-dashboard` already use — see this repo's CLAUDE.md) — coordinated with agent-lore, who owns that DB's schema
   lifecycle. This is the one open architectural question this Intake does not resolve; it's an
   Interview-stage question.
4. A general aggregator tool replacing the one existing single-log summary script, reading across
   all normalized logs (and later, Postgres) for fire counts, decision breakdown, error rate.

## Scope

- In scope: agent-rig's own hooks, schema, local writer, aggregator, and the Postgres
  write-path coordination question.
- Out of scope, explicitly deferred: the actual `agent-dashboard` UI panel (separate future
  Intake in that repo, its own cadence); retrofitting `domain-boundary-provenance` (sunset status
  needs re-confirming first — do not resurrect a retired hook as a side effect of this sprint);
  `session_queue_probe.py`'s SessionStart injections (no log today, not assumed in scope).

## Governing constraint carried forward

No behavior change to any hook's actual block/allow decision logic — this sprint touches only
what gets logged, not what gets decided.

## Open Questions for Danny

1. Postgres write path (Slice 3): does this need agent-lore's direct involvement now (e.g. a
   Switchboard/relay coordination step during Interview), or should agent-rig propose a schema
   and let agent-lore review it asynchronously?
2. Table/schema naming and shape for the Postgres side — deferred to Interview once agent-lore's
   preference is known, unless you already have one.
3. Sprint slug confirmed as `hook-telemetry-schema` (lite mode) — override if you want different
   naming.

## Next Step

On approval, this is a **Lite Mode** build (bounded internal tooling, no UI, no
multi-stakeholder scope beyond the one Postgres coordination question) — proceeds via
`/spec-start --lite hook-telemetry-schema`.
