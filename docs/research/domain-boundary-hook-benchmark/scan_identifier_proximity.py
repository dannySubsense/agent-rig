#!/usr/bin/env python3
"""
scan_identifier_proximity.py — committed, re-runnable measurement of the REAL distance
from an `externalSourceIdentifiers` match to the nearest comment line, in both directions.

    python3 docs/research/domain-boundary-hook-benchmark/scan_identifier_proximity.py

Writes results-identifier-proximity.md and identifier-proximity.jsonl next to itself.
Deterministic: file lists sorted, no sampling, no randomness.

WHY THIS FILE EXISTS
--------------------
`scripts/domain_boundary_provenance_probe.py` carries `PROXIMITY_WINDOW = 5`, cited to
`results.md` §5. §5 measures a DIFFERENT quantity: comment-to-ASSIGNMENT distance, upward
only, over name-bound numeric-literal assignments (rule c/d), capped at 12 lines. The
probe's window is applied to `externalSourceIdentifiers` MATCH lines, in BOTH directions.
This script measures the quantity the probe actually applies its window to.

WHAT IS MEASURED
----------------
For every line in the corpus that `find_identifier_matches` would match (same matching
semantics: literal substring, or `re:`-prefixed regex, case-sensitive), the distance in
lines to the nearest Python comment line ABOVE and BELOW, searched to end of file,
uncapped. Distance 1 == comment on the immediately adjacent line. A comment ON the match
line itself (trailing or full-line) is recorded as distance 0 in a separate bucket and
excluded from the directional distributions, since it has no direction.

"Comment line" here = a line whose stripped text starts with `#`, PLUS (for the
match-line-itself bucket) a `#` appearing anywhere on the match line outside no-string
analysis. Full-line comment detection is purely `lstrip().startswith("#")` — no AST, no
string-literal awareness. Stated so the number can be read for what it is.

IDENTIFIER SOURCES — this is the load-bearing scope limit
----------------------------------------------------------
`externalSourceIdentifiers` is per-repo manifest content, authored at retrofit time. It is
not a property of the corpus. This script therefore does not invent an identifier list. It
uses only identifier lists that exist as committed files on this machine:

  SET R ("real")    — the one production manifest that exists anywhere in the corpus:
                      projects/gap-lens-dilution-filter/docs/tooling/domain-boundary-manifest.json
  SET F ("fixture") — agent-rig's self-test fixture manifest:
                      tests/fixtures/domain_boundary_manifest_fixture.json

Each set is measured twice, and both are reported separately:

  scope "manifest"  — only files under that manifest's own repo AND matching its own
                      `pipelineConfigGlobs` (fnmatch, POSIX relpath — same call the probe
                      makes). This is the population the shipped hook can actually see.
  scope "corpus"    — every `.py` file in the whole corpus, globs ignored. A larger,
                      out-of-scope population, reported only to show whether the
                      manifest-scoped N is small because the identifiers are rare or
                      because the globs are narrow.

Corpus roots, skip-dirs and the file walk are imported from scan_thresholds.py rather than
re-declared, so both benchmarks provably walk the same tree.
"""

from __future__ import annotations

import fnmatch
import json
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# Corpus + walking machinery reused verbatim from the sibling benchmark.
from scan_thresholds import (  # noqa: E402
    CORPUS_ROOTS,
    SKIP_DIRS,
    iter_py_files,
    AGENT_RIG,
    PROJECTS,
)

# Identifier matching semantics reused verbatim from the shipped probe.
sys.path.insert(0, str(AGENT_RIG / "scripts"))
from domain_boundary_provenance_probe import (  # noqa: E402
    find_identifier_matches,
    PROXIMITY_WINDOW,
)

REAL_MANIFEST = PROJECTS / "gap-lens-dilution-filter" / "docs" / "tooling" / "domain-boundary-manifest.json"
FIXTURE_MANIFEST = AGENT_RIG / "tests" / "fixtures" / "domain_boundary_manifest_fixture.json"

WINDOWS = (2, 5, 10)


@dataclass
class Match:
    identifier_set: str
    scope: str
    repo: str
    path: str
    line: int              # 1-based
    identifier: str
    comment_on_line: bool
    dist_above: int | None
    dist_below: int | None


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def measure(lines: list[str], idx: int):
    """idx is 0-based index of the match line. Returns (comment_on_line, above, below),
    distances uncapped, None when no comment exists in that direction."""
    on_line = "#" in lines[idx]
    above = None
    for j in range(idx - 1, -1, -1):
        if is_comment_line(lines[j]):
            above = idx - j
            break
    below = None
    for j in range(idx + 1, len(lines)):
        if is_comment_line(lines[j]):
            below = j - idx
            break
    return on_line, above, below


def load_manifest(path: Path):
    data = json.loads(path.read_text())
    return data["externalSourceIdentifiers"], data["pipelineConfigGlobs"]


def glob_match(relposix: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(relposix, g) for g in globs)


def collect(set_name: str, identifiers: list[str], globs: list[str],
            manifest_repo: str | None) -> tuple[list[Match], int]:
    """Returns (matches, files_scanned). If manifest_repo is set, scope is
    'manifest' (that repo only, glob-filtered); otherwise 'corpus' (all repos, no globs)."""
    out: list[Match] = []
    files = 0
    scope = "manifest" if manifest_repo else "corpus"
    for repo, root in CORPUS_ROOTS:
        if not root.exists():
            continue
        if manifest_repo and repo != manifest_repo:
            continue
        for p in iter_py_files(root):
            relposix = p.relative_to(root).as_posix()
            if manifest_repo and not glob_match(relposix, globs):
                continue
            files += 1
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = find_identifier_matches(src, identifiers)
            if not hits:
                continue
            lines = src.split("\n")
            for line_idx, identifier in hits:
                on_line, above, below = measure(lines, line_idx)
                out.append(Match(set_name, scope, repo, relposix, line_idx + 1,
                                 identifier, on_line, above, below))
    return out, files


def hist(values: list[int | None]) -> dict:
    return dict(sorted(Counter(v for v in values if v is not None).items()))


def coverage(values: list[int | None], total: int, w: int) -> float:
    if total == 0:
        return 0.0
    n = sum(1 for v in values if v is not None and v <= w)
    return round(100.0 * n / total, 1)


def summarize(matches: list[Match]) -> dict:
    directional = [m for m in matches]
    above = [m.dist_above for m in directional]
    below = [m.dist_below for m in directional]
    total = len(directional)
    either = [
        min([d for d in (m.dist_above, m.dist_below) if d is not None], default=None)
        for m in directional
    ]
    return {
        "total": total,
        "comment_on_match_line": sum(1 for m in directional if m.comment_on_line),
        "no_comment_above": sum(1 for v in above if v is None),
        "no_comment_below": sum(1 for v in below if v is None),
        "hist_above": hist(above),
        "hist_below": hist(below),
        "max_above": max([v for v in above if v is not None], default=None),
        "max_below": max([v for v in below if v is not None], default=None),
        "coverage": {
            w: {
                "above": coverage(above, total, w),
                "below": coverage(below, total, w),
                "either": coverage(either, total, w),
            }
            for w in WINDOWS
        },
    }


def main() -> int:
    runs = []
    if REAL_MANIFEST.exists():
        ids_r, globs_r = load_manifest(REAL_MANIFEST)
        runs.append(("R-manifest", ids_r, globs_r, "gap-lens-dilution-filter", str(REAL_MANIFEST)))
        runs.append(("R-corpus", ids_r, globs_r, None, str(REAL_MANIFEST)))
    else:
        runs.append(("R-MISSING", [], [], None, f"MISSING {REAL_MANIFEST}"))
    if FIXTURE_MANIFEST.exists():
        ids_f, globs_f = load_manifest(FIXTURE_MANIFEST)
        runs.append(("F-manifest", ids_f, globs_f, "agent-rig", str(FIXTURE_MANIFEST)))
        runs.append(("F-corpus", ids_f, globs_f, None, str(FIXTURE_MANIFEST)))

    all_matches: list[Match] = []
    results = []
    for name, ids, globs, repo, src in runs:
        if not ids:
            results.append((name, src, ids, globs, repo, 0, {"total": 0}))
            continue
        ms, nfiles = collect(name, ids, globs, repo)
        all_matches.extend(ms)
        results.append((name, src, ids, globs, repo, nfiles, summarize(ms)))

    with open(HERE / "identifier-proximity.jsonl", "w") as fh:
        for m in sorted(all_matches, key=lambda x: (x.identifier_set, x.repo, x.path, x.line)):
            fh.write(json.dumps(asdict(m)) + "\n")

    L: list[str] = []
    A = L.append
    A("# Identifier-to-Comment Proximity — Committed Results")
    A("")
    A("**Generated by**: `docs/research/domain-boundary-hook-benchmark/scan_identifier_proximity.py`  ")
    A("**Regenerate**: `python3 docs/research/domain-boundary-hook-benchmark/scan_identifier_proximity.py`  ")
    A(f"**Python**: {sys.version.split()[0]}  ")
    A("**Raw rows**: `identifier-proximity.jsonl` (one line per (line, identifier) match)")
    A("")
    A("Machine-generated. Do not hand-edit — rerun the script.")
    A("")
    A("## 1. What is measured")
    A("")
    A("Distance in lines from an `externalSourceIdentifiers` match line to the nearest")
    A("Python comment line ABOVE and BELOW, searched to end of file, **uncapped**.")
    A("Distance 1 = adjacent line. A `#` present on the match line itself is counted")
    A("separately (`comment on match line`) and is not a direction.")
    A("")
    A("Matching uses `find_identifier_matches` imported from the shipped probe, so")
    A("literal/`re:` semantics are identical. Corpus roots, skip-dirs and the file walk are")
    A("imported from `scan_thresholds.py`.")
    A("")
    A(f"For reference, the probe's current `PROXIMITY_WINDOW` is **{PROXIMITY_WINDOW}**. This")
    A("document reports the measured distribution only; it selects no window.")
    A("")
    A("## 2. Identifier sources (scope limit)")
    A("")
    A("`externalSourceIdentifiers` is per-repo manifest content, not a property of the corpus.")
    A("Only identifier lists that exist as committed files on this machine are used — none are")
    A("invented. Exactly one production manifest exists anywhere in the corpus.")
    A("")
    A("| Set | Source file | Identifiers | Globs |")
    A("|---|---|---|---|")
    for name, src, ids, globs, repo, nfiles, s in results:
        if repo is not None or name.endswith("-corpus"):
            pass
        A(f"| `{name}` | `{src}` | {', '.join('`'+i+'`' for i in ids) or '—'} | "
          f"{', '.join('`'+g+'`' for g in globs) or '(ignored)'} |")
    A("")
    A("Scope `manifest` = that manifest's own repo, glob-filtered (what the shipped hook can")
    A("see). Scope `corpus` = every `.py` in all corpus repos, globs ignored (out of the hook's")
    A("reach; reported to separate 'identifiers are rare' from 'globs are narrow').")
    A("")
    for name, src, ids, globs, repo, nfiles, s in results:
        A(f"## Set `{name}` — files scanned: {nfiles}")
        A("")
        if s["total"] == 0:
            A("**Total identifier-match candidates: 0.** No distance distribution exists.")
            A("")
            continue
        A(f"- **Total identifier-match candidates: {s['total']}**")
        A(f"- Comment on the match line itself: {s['comment_on_match_line']}")
        A(f"- No comment anywhere above: {s['no_comment_above']} | "
          f"no comment anywhere below: {s['no_comment_below']}")
        A(f"- **Max observed distance above: {s['max_above']}** | "
          f"**below: {s['max_below']}**")
        A("")
        A("| Distance | Count above | Count below |")
        A("|---|---|---|")
        keys = sorted(set(s["hist_above"]) | set(s["hist_below"]))
        for d in keys:
            A(f"| {d} | {s['hist_above'].get(d, 0)} | {s['hist_below'].get(d, 0)} |")
        A("")
        A("Cumulative coverage of ALL candidates (denominator = total candidates, including")
        A("those with no comment in that direction) at window W:")
        A("")
        A("| W | Above | Below | Either direction |")
        A("|---|---|---|---|")
        for w in WINDOWS:
            c = s["coverage"][w]
            A(f"| {w} | {c['above']}% | {c['below']}% | {c['either']}% |")
        A("")
    A("## 3. What this does NOT decide")
    A("")
    A("No window size is recommended, no disposition proposed. This is the raw measured")
    A("distribution of the quantity the probe's window is applied to. The choice of value is")
    A("a human decision made after reading this file.")
    A("")
    (HERE / "results-identifier-proximity.md").write_text("\n".join(L) + "\n")

    for name, src, ids, globs, repo, nfiles, s in results:
        print(f"{name}: files={nfiles} matches={s['total']}")
    print(f"wrote {HERE/'results-identifier-proximity.md'} and {HERE/'identifier-proximity.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
