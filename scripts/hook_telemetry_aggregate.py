#!/usr/bin/env python3
"""General hook-telemetry aggregator — reads all normalized `.jsonl` logs and
reports fire counts / decision breakdown / error rate per-hook and combined.

Replaces `scripts/signpost_checklist_summary.py` (retired, single-log only).
See docs/tooling/hook-telemetry-schema/SPEC.md §4/§6.

Reads both event shapes from the same file: envelope lines with a `payload`
key (written by hook_telemetry.py going forward) and flat legacy lines
already on disk from before this migration (hook-specific fields at the top
level). Both shapes carry `decision`/`probe_error` at the top level, which is
all `summarize()` needs.
"""

import argparse
import json
import os
import sys
from collections import Counter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Known hook -> jsonl path table, mirroring each probe's own TRACK_RECORD_PATH /
# TRACK_RECORD_RELATIVE_PATH constants — every value here is a hook's own
# existing, already-defined path constant, not an invented one.
#
# "progress-proof-per-slice" is project-dir-relative (resolved per-invocation
# from stdin's project_dir, not a fixed repo-root path) — its own probe/wrapper
# never hardcode an absolute path. This table documents that relative suffix
# so the aggregator can resolve it against a project_dir (default: this
# repo's own root, since that is the only repo this hook is installed in per
# this sprint's scope — see --project-dir to override).
HOOK_LOG_PATHS: dict[str, str] = {
    "signpost-checklist": os.environ.get(
        "SIGNPOST_TRACK_RECORD_PATH",
        os.path.join(REPO_ROOT, "docs", "tooling", "signpost-checklist-track-record.jsonl"),
    ),
    "no-preamble-no-meta-narration": os.path.join(
        REPO_ROOT, "docs", "tooling", "no-preamble-no-meta-narration-track-record.jsonl"
    ),
    "progress-proof-per-slice": os.path.join(
        REPO_ROOT, "docs", "tooling", "progress-proof-per-slice-track-record.jsonl"
    ),
}


def load_events(jsonl_path: str) -> list:
    """Best-effort JSONL read: missing file -> [], malformed line -> skipped."""
    events = []
    try:
        with open(jsonl_path) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    events.append(obj)
    except Exception:
        return []
    return events


def summarize(events: list) -> dict:
    """Pure function, no I/O. decision_counts is a raw tally of the literal
    top-level `decision` string — no vocabulary mapping. error_count/rate is
    derived from `probe_error is not None`, not a decision string match."""
    total = len(events)
    decision_counts: Counter = Counter()
    error_count = 0
    first_ts = None
    last_ts = None

    for event in events:
        decision = event.get("decision")
        if decision is not None:
            decision_counts[decision] += 1
        if event.get("probe_error") is not None:
            error_count += 1
        ts = event.get("timestamp")
        if isinstance(ts, str):
            if first_ts is None or ts < first_ts:
                first_ts = ts
            if last_ts is None or ts > last_ts:
                last_ts = ts

    block_side_count = decision_counts.get("block", 0) + decision_counts.get("deny", 0)
    error_rate = (error_count / total) if total else 0.0

    return {
        "total": total,
        "decision_counts": dict(decision_counts),
        "block_side_count": block_side_count,
        "error_count": error_count,
        "error_rate": error_rate,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def _print_hook_summary(name: str, summary: dict) -> None:
    print(f"--- {name} ---")
    print(f"  fires: {summary['total']}")
    total = summary["total"]
    if total:
        for decision, count in sorted(summary["decision_counts"].items()):
            pct = (count / total) * 100
            print(f"    {decision}: {count} ({pct:.1f}%)")
        print(f"  block-side (block+deny): {summary['block_side_count']}")
        print(f"  error rate: {summary['error_count']}/{total} ({summary['error_rate'] * 100:.1f}%)")
        print(f"  first: {summary['first_ts']}  last: {summary['last_ts']}")
    else:
        print("  no events recorded")
    print()


def print_report(per_hook: dict, combined: dict) -> None:
    """Prints fire count, decision breakdown (with percentages), and error rate
    for each hook and once combined across all of them. Read-only against all
    logs."""
    for name, summary in per_hook.items():
        _print_hook_summary(name, summary)
    _print_hook_summary("combined", combined)


def _combine(per_hook_events: dict) -> dict:
    all_events = []
    for events in per_hook_events.values():
        all_events.extend(events)
    return summarize(all_events)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        default=REPO_ROOT,
        help="Project dir to resolve progress-proof-per-slice's relative log path against "
        "(defaults to this repo's own root).",
    )
    args = parser.parse_args()

    hook_paths = dict(HOOK_LOG_PATHS)
    hook_paths["progress-proof-per-slice"] = os.path.join(
        args.project_dir, "docs", "tooling", "progress-proof-per-slice-track-record.jsonl"
    )

    per_hook_events = {name: load_events(path) for name, path in hook_paths.items()}
    per_hook_summary = {name: summarize(events) for name, events in per_hook_events.items()}
    combined = _combine(per_hook_events)

    print_report(per_hook_summary, combined)
    return 0


if __name__ == "__main__":
    sys.exit(main())
