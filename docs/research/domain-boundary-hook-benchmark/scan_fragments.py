#!/usr/bin/env python3
"""
scan_fragments.py -- committed, re-runnable measurement of detection recall at the
REAL scan surface: FRAGMENTS, not whole files.

    python3 docs/research/domain-boundary-hook-benchmark/scan_fragments.py

WHY THIS FILE EXISTS
--------------------
results.md sec.4 measured rule (c)'s 2/2 recall against 445 WHOLE .py FILES. The hook
does not scan whole files. `get_scan_surface` in
scripts/domain_boundary_provenance_probe.py returns only tool_input.new_string (Edit)
or tool_input.content (Write). For an Edit, that is routinely an INDENTED fragment with
no enclosing `class`/`def`/module context -- exactly I2's shape. A bare
`ast.parse(fragment)` raises IndentationError there and the incumbent's
`except SyntaxError: return []` would silently yield ZERO candidates.

02-ARCHITECTURE.md sec.2.1 specifies the fix (three parse strategies) and explicitly
records the 2/2 figure as "NOT YET VALIDATED AT THE REAL SCAN SURFACE ... it has not
been run as part of this architecture-fix pass." THIS SCRIPT IS THAT RUN.

GROUND TRUTH -- both fragments are transcribed from real source, not invented:
  I1  `_HEAD_BYTES = 65_536`
      gap-lens-dilution-filter research/gates/measure_oq5_residue.py:69 @ HEAD,
      column 0 (module level), preceded by a 3-line comment block.
  I2  `filing_text_max_bytes: int = 512_000`
      gap-lens-dilution-filter research/pipeline/config.py:47 @ git rev 7d9fdf5
      (DELETED at HEAD, tombstoned per DDR-0010). Indented FOUR SPACES inside
      `class BacktestConfig:` (line 29). Verified by `git show 7d9fdf5:...`.

Both are pulled live from those sources at runtime by build_fragments(); if a source is
unavailable the case is reported UNAVAILABLE, never fabricated.

Writes results-fragment-shaped.md next to itself. Deterministic: no sampling.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_thresholds import (  # noqa: E402
    INCIDENT_1, INCIDENT_2_PATH, INCIDENT_2_REPO, INCIDENT_2_REV,
    PARSE_DEDENT, PARSE_DIRECT, PARSE_NONE, PARSE_REGEX,
    scan_source_fragment,
)

HERE = Path(__file__).resolve().parent

I1_TARGET = "_HEAD_BYTES"
I2_TARGET = "filing_text_max_bytes"


def _lines(text: str) -> list[str]:
    return text.splitlines()


def _find(lines: list[str], needle: str) -> int:
    for i, ln in enumerate(lines):
        if needle in ln and "=" in ln:
            return i
    raise LookupError(needle)


def build_fragments():
    """Returns (cases, notes). Each case: dict(id, incident, target, shape, fragment)."""
    cases, notes = [], []

    # ---- I1: live file at HEAD ----
    if not INCIDENT_1.exists():
        notes.append(f"I1 source UNAVAILABLE: {INCIDENT_1} not found. I1 cases NOT measured.")
    else:
        src = _lines(INCIDENT_1.read_text(encoding="utf-8", errors="replace"))
        i = _find(src, I1_TARGET)
        cases += [
            dict(id="I1-a", incident="I1", target=I1_TARGET,
                 shape="changed line only (module level, column 0)",
                 fragment=src[i]),
            dict(id="I1-b", incident="I1", target=I1_TARGET,
                 shape="changed line + 2 lines of real preceding context (comment block)",
                 fragment="\n".join(src[i - 2:i + 1])),
            dict(id="I1-c", incident="I1", target=I1_TARGET,
                 shape="changed line + 3 lines before and after (real surrounding code)",
                 fragment="\n".join(src[i - 3:i + 4])),
        ]

    # ---- I2: deleted at HEAD, recovered from git ----
    try:
        raw = subprocess.run(
            ["git", "-C", str(INCIDENT_2_REPO), "show", f"{INCIDENT_2_REV}:{INCIDENT_2_PATH}"],
            capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        notes.append(f"I2 source UNAVAILABLE: could not recover from git ({e}). I2 cases NOT measured.")
        raw = None

    if raw is not None:
        src = _lines(raw)
        i = _find(src, I2_TARGET)
        cls = max(j for j in range(i) if src[j].startswith("class "))
        dangle = max(j for j in range(i) if src[j].strip() == "])")
        assert src[i].startswith("    "), "expected 4-space class-body indent"
        cases += [
            # THE WORST CASE named in sec.2.1: exact original indentation, zero enclosing structure.
            dict(id="I2-a", incident="I2", target=I2_TARGET,
                 shape="changed line only, ORIGINAL 4-space indent, NO enclosing class (worst case)",
                 fragment=src[i]),
            dict(id="I2-b", incident="I2", target=I2_TARGET,
                 shape="changed line + 2 lines of real preceding context (indented, no class line)",
                 fragment="\n".join(src[i - 2:i + 1])),
            dict(id="I2-c", incident="I2", target=I2_TARGET,
                 shape="changed line + enclosing `class ...:` line + other body lines",
                 fragment="\n".join([src[cls]] + src[i - 2:i + 4])),
            dict(id="I2-d", incident="I2", target=I2_TARGET,
                 shape="changed line + 3 real body lines after (indented, no class line)",
                 fragment="\n".join(src[i:i + 4])),
            # Realistic Edit that starts mid-block: the fragment OPENS with the dangling
            # `])` that closes a list literal begun above the fragment window. Unbalanced
            # bracket -> plain SyntaxError, not IndentationError, so sec.2.1 skips strategy 2
            # and only strategy 3 can recover it. Sliced from the real `])` line.
            dict(id="I2-e", incident="I2", target=I2_TARGET,
                 shape="fragment OPENS with a dangling `])` closing a list begun above the window (unbalanced)",
                 fragment="\n".join(src[dangle:i + 1])),
            # Mixed indentation: the changed line at original indent preceded by a
            # column-0 line, so textwrap.dedent finds NO common prefix to strip.
            dict(id="I2-f", incident="I2", target=I2_TARGET,
                 shape="changed line at 4-space indent preceded by a column-0 line (dedent finds no common prefix)",
                 fragment="# Pipeline settings\n" + src[i]),
            # HONEST GAP PROBE, not a ground-truth incident: a real FLOAT threshold from the
            # same dataclass, forced onto the regex path. sec.2.1's regex matches
            # (-?\d[\d_]*|True|False) -- integers and bools only -- so a float is expected to MISS.
            # Recorded as a measured case so the limitation is a number, not a caveat in prose.
            dict(id="F1", incident="F1 (float probe, not ground truth)", target="dilution_pct_min",
                 shape="FLOAT threshold `dilution_pct_min: float = 0.10`, forced onto regex path (col-0 line first)",
                 fragment="# Filter thresholds\n" + src[_find(src, "dilution_pct_min")]),
        ]
    return cases, notes


def run_case(case) -> dict:
    cands, strategy = scan_source_fragment("fragment-sim", "research/pipeline/config.py", case["fragment"])
    hits = [c for c in cands if c.target_name == case["target"]]
    net = [c for c in hits if c.net_flagged()]
    return {
        **case,
        "strategy": strategy if hits else (strategy if cands else PARSE_NONE),
        "n_candidates": len(cands),
        "hit": bool(net),
        "detail": "; ".join(f"line {c.line} ctx={c.context} value={c.value_repr} "
                            f"net_flagged={c.net_flagged()}" for c in hits) or "target not detected",
    }


STRAT_LABEL = {
    PARSE_DIRECT: "1 direct ast.parse",
    PARSE_DEDENT: "2 dedent-retry",
    PARSE_REGEX: "3 regex fallback",
    PARSE_NONE: "none (no candidates)",
}


def main() -> int:
    cases, notes = build_fragments()
    rows = [run_case(c) for c in cases]

    L, A = [], None
    A = L.append
    A("# Fragment-Shaped Recall — Committed Results")
    A("")
    A("**Generated by**: `docs/research/domain-boundary-hook-benchmark/scan_fragments.py`  ")
    A("**Regenerate**: `python3 docs/research/domain-boundary-hook-benchmark/scan_fragments.py`  ")
    A(f"**Python**: {sys.version.split()[0]}  ")
    A("**Detector under test**: `scan_source_fragment` in `scan_thresholds.py` — the three-strategy")
    A("chain specified by `02-ARCHITECTURE.md` §2.1 (ast.parse → dedent-retry on IndentationError →")
    A("regex fallback for the assignment context only).")
    A("")
    A("This file is machine-generated. Do not hand-edit — rerun the script.")
    A("")
    A("## 1. Why this run exists")
    A("")
    A("`results.md` §4's 2/2 recall was measured against **whole `.py` files**. The hook's real scan")
    A("surface is `tool_input.new_string` / `tool_input.content` — a **fragment**. `02-ARCHITECTURE.md`")
    A("§2.1 records the whole-file figure as *\"NOT YET VALIDATED AT THE REAL SCAN SURFACE\"* and")
    A("specifies this exact re-run as its required follow-up. This is that run.")
    A("")
    if notes:
        A("**Source availability problems (reported, not fabricated):**")
        A("")
        for n in notes:
            A(f"- {n}")
        A("")
    A("## 2. Fragment test matrix")
    A("")
    A("Every fragment below is sliced live from real source at runtime (I1 from the working tree,")
    A("I2 from `git show 7d9fdf5:research/pipeline/config.py`) — none is hand-typed.")
    A("")
    A("| Case | Incident | Fragment shape | Strategy that ran | Result |")
    A("|---|---|---|---|---|")
    for r in rows:
        A(f"| `{r['id']}` | {r['incident']} | {r['shape']} | {STRAT_LABEL.get(r['strategy'], r['strategy'])} | "
          f"**{'PASS' if r['hit'] else 'MISS'}** |")
    A("")
    A("### Per-case detail")
    A("")
    for r in rows:
        A(f"**`{r['id']}` — {'PASS' if r['hit'] else 'MISS'}** ({r['shape']})")
        A("")
        A("```python")
        for ln in r["fragment"].splitlines():
            A(ln)
        A("```")
        A("")
        A(f"- Strategy: `{STRAT_LABEL.get(r['strategy'], r['strategy'])}`")
        A(f"- Total candidates from fragment: {r['n_candidates']}")
        A(f"- Target hits: {r['detail']}")
        A("")
    A("## 3. Recall by incident")
    A("")
    A("| Incident | Cases | PASS | MISS | Recall |")
    A("|---|---|---|---|---|")
    for inc in sorted({r["incident"] for r in rows}):
        sel = [r for r in rows if r["incident"] == inc]
        if not sel:
            A(f"| {inc} | 0 | — | — | **NOT MEASURED (source unavailable)** |")
            continue
        p = sum(1 for r in sel if r["hit"])
        A(f"| {inc} | {len(sel)} | {p} | {len(sel) - p} | {p}/{len(sel)} |")
    gt = [r for r in rows if r["incident"] in ("I1", "I2")]
    gt_p = sum(1 for r in gt if r["hit"])
    A(f"| **GROUND TRUTH (I1+I2 only)** | {len(gt)} | {gt_p} | {len(gt) - gt_p} | **{gt_p}/{len(gt)}** |")
    A("")
    A("`F1` is a deliberate limitation probe, not a historical incident — it is excluded from the")
    A("ground-truth recall figure and reported separately in §5.")
    tot_p = gt_p
    A("")
    A("## 4. Strategy attribution")
    A("")
    A("| Strategy | Cases where it was the one that ran |")
    A("|---|---|")
    for s in (PARSE_DIRECT, PARSE_DEDENT, PARSE_REGEX, PARSE_NONE):
        ids = [r["id"] for r in rows if r["strategy"] == s]
        A(f"| {STRAT_LABEL[s]} | {', '.join(f'`{i}`' for i in ids) if ids else '—'} |")
    A("")
    A("## 5. What this run does NOT establish")
    A("")
    A("- **Contexts 1 and 2 (comparison operand, slice/truncation) are not measured here.** §2.1")
    A("  gives them no regex fallback by design; an unparsable fragment yields zero candidates from")
    A("  them. This run measures context 3 only, because both ground-truth incidents are context 3.")
    A("- **The regex fallback matches integers and booleans only** —")
    A("  `(-?\\d[\\d_]*|True|False)` per §2.1. A float threshold (e.g. `dilution_pct_min: float = 0.10`,")
    A("  a real line four rows above I2 in the same dataclass) does **not** match it, so a float")
    A("  threshold in an unparsable fragment is a known MISS. Neither ground-truth incident is a")
    A("  float, so this does not affect the recall figures above — it is recorded, not hidden.")
    A("- **Precision is not measured.** No false-positive labeling was done on the regex fallback.")
    A("- The `{0, 1, -1, 2}` exclusion set is applied identically to the ast and regex paths and")
    A("  remains unvalidated (`results.md` §6).")
    A("")

    (HERE / "results-fragment-shaped.md").write_text("\n".join(L) + "\n")

    for r in rows:
        print(f"  {r['id']:6s} {'PASS' if r['hit'] else 'MISS'}  strategy={STRAT_LABEL.get(r['strategy'])}  {r['shape'][:60]}")
    print(f"total {tot_p}/{len(rows)}")
    print(f"wrote {HERE/'results-fragment-shaped.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
