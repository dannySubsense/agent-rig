#!/usr/bin/env python3
"""Shared hook-telemetry envelope schema + writer.

See docs/tooling/hook-telemetry-schema/SPEC.md §3/§4. Every probe (and wrapper
`write_probe_error()` fallback) migrated to this schema constructs a normalized
event via `write_telemetry_event()` instead of building its own ad hoc dict.

New lines written after migration use this envelope shape (hook-specific fields
nested under `payload`); existing flat legacy lines already on disk are left
exactly as they are, never rewritten.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass(frozen=True)
class TelemetryEvent:
    """Normalized hook-telemetry envelope. `payload` carries every field that is
    specific to one hook and not shared across the probes today."""

    hook_name: str
    timestamp: str
    session_id: Optional[str]
    decision: str
    reason: Optional[str]
    probe_error: Optional[str]
    payload: dict[str, Any] = field(default_factory=dict)


def to_jsonl_line(event: TelemetryEvent) -> str:
    """Serializes a TelemetryEvent to one JSON line, flat top-level fields plus a
    nested 'payload' dict for hook-specific fields."""
    entry = {
        "hook_name": event.hook_name,
        "timestamp": event.timestamp,
        "session_id": event.session_id,
        "decision": event.decision,
        "reason": event.reason,
        "probe_error": event.probe_error,
        "payload": event.payload,
    }
    return json.dumps(entry)


def write_telemetry_pg(event: TelemetryEvent) -> None:
    """PROVISIONAL — targets a new, separate `homelab_telemetry` database (see
    SPEC.md §7). v1 body is a no-op: no connection, no write, never raises."""
    pass


def write_telemetry_event(
    *,
    hook_name: str,
    jsonl_path: str,
    session_id: Optional[str],
    decision: str,
    reason: Optional[str],
    probe_error: Optional[str],
    payload: dict,
) -> None:
    """Builds a TelemetryEvent, appends it as one JSON line to `jsonl_path`, then
    calls write_telemetry_pg() with the same event. Best-effort: never raises
    into the caller. No decision normalization happens here — `decision` is
    written exactly as the caller passes it."""
    event = TelemetryEvent(
        hook_name=hook_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
        session_id=session_id,
        decision=decision,
        reason=reason,
        probe_error=probe_error,
        payload=dict(payload) if payload else {},
    )
    try:
        os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
        with open(jsonl_path, "a") as fh:
            fh.write(to_jsonl_line(event) + "\n")
    except Exception:
        # The track record is an audit trail, not a gate — a write failure here
        # must not change or block the probe's decision to Claude Code.
        pass

    try:
        write_telemetry_pg(event)
    except Exception:
        pass
