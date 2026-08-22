# Research Plan — Context Ratio Inversion & Work-Order Protocol (supports DDR-005)

**Status**: COMPLETE — see `FINDINGS.md` in this folder (research run 2026-08-21)
**Author**: wright
**Date**: 2026-08-21
**Feeds**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` (DRAFT) — this
research does not decide DDR-005; it supplies external, citable evidence for its open questions
before Danny reviews it further. Per this repo's Decision Discipline, every claim DDR-005 makes
about "best practice" needs a citable source or a PROVISIONAL tag — this plan is how that gets
supplied.

---

## Objective

DDR-005 claims (§1) that an agent's standing context should be inverted from ~90% conduct-rule
prose / 10% work definition toward the reverse — short `CLAUDE.md` + `WORKPLAN.md` + mechanized
(hook/script) enforcement instead of prose exhortation. That claim is currently sourced entirely
from one session's diagnosis (§0: "the four sections below are his analysis"). This research asks:
what does the wider field — Anthropic's own guidance, academic work, and practitioner community —
already know about this problem, and does it corroborate, refine, or contradict DDR-005's specific
proposal?

Not in scope: deciding DDR-005 itself, writing implementation, or resolving DDR-005 §7's open
questions by fiat. This is evidence-gathering only.

---

## Approach

Parallel fan-out across source types that don't overlap much, rather than one search thread
covering everything serially:

1. **Anthropic's own documentation/engineering blog/Claude Code docs** — context engineering,
   system-prompt design, prompt structuring guidance. Most likely place for the answer to already
   exist, per Danny's own hypothesis.
2. **Academic/technical literature** — arXiv and similar, on context-window management,
   instruction-following degradation with long system prompts, "lost in the middle" and adjacent
   findings, exhortation vs. enforced-constraint framing in LLM instruction design.
3. **Practitioner community** — GitHub issues/discussions (Claude Code and other agent tooling
   repos), Hacker News, Reddit, dev blogs, on `CLAUDE.md`/system-prompt design patterns and
   real-world experience reports.
4. **Adjacent agent frameworks** — how other publicly documented agent tooling (Cursor, Aider,
   Devin, etc.) structures standing instructions vs. task definition, where documented.
5. **Internal read** — DDR-005's own text plus agent-rig's current `CLAUDE.md`, so external
   findings get evaluated against the actual proposal on the table, not in a vacuum.

Synthesis: merge findings into a structured brief — established best practice vs. speculation,
where DDR-005's specific 90/10 ratio claim and "delete, don't supplement" instruction (§1, dissented
from in §9) are corroborated or contradicted, and concrete patterns worth citing.

## Output

A findings document in this same folder (`FINDINGS.md`, not yet written) — one section per source
type above, each claim carrying its source, plus a synthesis section explicitly addressing DDR-005
§7's open questions (which rules are mechanizable, per-repo `WORKPLAN.md` ownership, rollout order)
and §9's producer/Danny disagreement over deletion vs. replacement-per-rule.

---

## Relationship to DDR-005

- This plan lives in its own folder (`docs/research/ddr-005-context-ratio/`) rather than inside
  `docs/specs/agent-rig-ddrs/`, because it is evidence-gathering in service of a DDR, not a DDR
  section itself — keeping it separate avoids the single-source-diagnosis problem DDR-005 §9
  already flags for itself.
- DDR-005 is amended (§ "Related research", below its own §9) to point here.
- Once `FINDINGS.md` exists, DDR-005 should be revised to cite it directly wherever §1/§7/§9 make a
  best-practice claim that this research bears on — not left as two documents that happen to be
  about the same thing.
