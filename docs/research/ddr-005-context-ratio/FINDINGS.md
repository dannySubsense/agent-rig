# Research Findings — Context Ratio Inversion & Work-Order Protocol (DDR-005)

**Status**: COMPLETE (research run 2026-08-21)
**Author**: wright (synthesized from a 5-agent parallel workflow — 4 source-type sweeps + 1 synthesis pass)
**Feeds**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — see that doc's §10 for
the back-reference. This document does not decide DDR-005; it supplies external evidence per
`RESEARCH-PLAN.md` in this same folder.

**Provenance note**: all claims below trace to a specific URL and a quoted/paraphrased excerpt, per
each source agent's brief. Several are flagged by the source agents themselves as snippet-level
(WebSearch summary, not independently WebFetched/verified against primary text) — those are marked
explicitly and should not be treated as more solid than stated. This is a signpost for further
reading, not a substitute for reading the cited sources directly before citing them further in a
locked decision doc.

---

## 1. Executive Summary

The evidence broadly **corroborates DDR-005's core mechanism** — large, conduct-heavy standing
context degrades an agent's adherence to instructions generally, including task performance — but
does **not corroborate the specific ~90/10 ratio framing or the "theatrics of rigor" causal story as
stated**, because no source (official, academic, or practitioner) measures a conduct-vs-task ratio
as such; that framing is original to DDR-005, not literature-derived.

The strongest, most direct support is for moves (1) short standing files and (3) mechanize-into-hooks
— official Anthropic docs state bloated CLAUDE.md files cause instructions to be ignored, and
Anthropic's own hooks system is a documented, deterministic alternative to advisory prose. Move (2),
the `WORKPLAN.md`/work-order format, is corroborated only by analogy (Anthropic's "give Claude a
checkable definition of done" guidance, Devin's Playbook/Knowledge split, and a practitioner
"definition of done" pattern) — no source uses DDR-005's exact "work order" construct.

The research also surfaces real complication for the producer's dissent in DDR-005 §9: one
controlled community test found no adherence difference between 25 and 500 lines (brevity's value
framed as cost/context-rot, not obedience), and one academic benchmark found system-prompt removal
causes universal performance degradation across turns — both cutting against a pure-deletion,
corpus-is-overhead reading, and lending some support to "the corpus is load-bearing."

**Overall: refine, not confirm or contradict.** The diagnosis (bloat hurts) is well-supported, the
specific ratio/causal narrative is unsourced, and the prescribed fix is directionally right but
under-specified relative to what's available in the literature.

---

## 2. Corroborating Evidence

| Claim | Strength | Source |
|---|---|---|
| Over-long CLAUDE.md causes Claude to ignore instructions — "important rules get lost in the noise" | **Strong, primary-source, direct** | [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices) |
| Context window fills fast; performance degrades as it fills ("context rot") — non-uniform accuracy decay as tokens grow, even on trivial tasks | **Strong consensus** — Anthropic + independent 18-model study | [anthropic.com/engineering/effective-context-engineering-for-ai-agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [trychroma.com/research/context-rot](https://www.trychroma.com/research/context-rot) |
| Compositional instruction-following collapses combinatorially as simultaneous rule count grows — probe success falls below 50% at ~7 constraints for the strongest model tested, 3 or fewer for 12/15 models | **Strong — two independent quantitative studies** | arXiv:2608.12426; arXiv:2507.11538 |
| Hooks are deterministic and guarantee the action happens; CLAUDE.md instructions are advisory only — exactly DDR-005 move (3)'s claim | **Strong, primary-source, direct, same host environment agent-rig runs on** | [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices); [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) |
| Five-plus independent practitioner blogs converge on "bloat degrades all-rule adherence" and "hooks/CI beat prose" | **Strong convergence**, not confirmed via primary discussion threads (no HN/Reddit found) | dev.to/minatoplanb; tianpan.co; dev.to/nishilbhave; evilmartians.com; strandsagents.com |
| Devin's Knowledge (always-on, short) vs. Playbook (task procedure) split maps closely onto DDR-005's CLAUDE.md/WORKPLAN.md distinction | **Single source**, closest structural analogue found | fast.io/resources/devin-ai-playbook-guide, devin-knowledge-guide |
| Anthropic's "give Claude a checkable definition of done" guidance, and a practitioner "definition of done" pattern, support the work-order concept's core idea | **Corroborates concept, not the exact format** | [code.claude.com/docs/en/best-practices](https://code.claude.com/docs/en/best-practices); digitalapplied.com/blog |
| Cursor is deprecating a single always-loaded rules file in favor of scoped, glob-activated rule files, explicitly citing cost | **Single source, framework precedent** — corroborates diagnosis, not DDR-005's specific remedy | cursor.com/docs/rules |
| Adjacent ML literature (RLVR, VerIF, RECAST, Rule-Based Rewards) independently prefers deterministic checks over natural-language instructions | **Adjacent-but-relevant** — training-time reward design, an analogy, not a direct test | arXiv:2506.09942 et al. |

---

## 3. Contradicting or Complicating Evidence

- **No adherence difference from 25 to 500 lines**, in one reported controlled test — brevity's
  value framed as a cost/context-rot argument, not an obedience argument. Directly complicates
  DDR-005's implicit causal claim that length itself degrades compliance. **Single, unverified
  secondary source — flag as suggestive only.** ([dev.to/nishilbhave](https://dev.to/nishilbhave/claudemd-best-practices-the-complete-2026-guide-435j))
- **ETH Zurich finding**: added context files don't improve task success rates, but do raise
  inference cost >20% on average — supports a cost-minimization argument, not the "degrades success"
  mechanism DDR-005 asserts.
- **System-prompt removal causes universal multi-turn performance degradation**, and top models can
  be *more* sensitive to its removal than weaker ones (arXiv:2511.03508) — real pushback against
  pure deletion; some support for the producer's DDR-005 §9 dissent that "the corpus is load-bearing."
- **AGENTS.md and Aider's CONVENTIONS.md both keep standing content as unenforced prose** — no
  evidence of hook-level mechanization anywhere in the wider field outside Claude Code itself,
  suggesting DDR-005 move (3) is more aspirational than field-standard.
- **Cline's Memory Bank is a documented case of exactly the "theatrics of rigor" failure** —
  compliance is self-reported by the model via a status flag (`[MEMORY BANK: ACTIVE]`), not
  externally verified. Confirms the failure mode is real and unsolved elsewhere; not evidence
  DDR-005's fix is validated at scale.
- **No source validates the ~90/10 ratio number itself** — it is a diagnostic metaphor from
  DDR-005's own case study, not a measured or externally corroborated figure.

---

## 4. DDR-005 §7 Open Questions — What the Research Bears On

1. **Which conduct is mechanizable vs. must stay prose?** Partial: Claude Code hooks demonstrably
   mechanize action/file-level constraints; nothing found addresses judgment-dependent conduct
   (deference, hedging, verification-against-live-files) — the kind DDR-005's own CLAUDE.md is
   mostly made of. One paper (arXiv:2604.20911, **title-only, unverified**) hints omission
   constraints ("don't do X") decay faster than commission constraints ("do X") in long-context
   agent settings — directly relevant to DDR-005's mostly-omission rule style if true, but cannot be
   cited as settled without reading the actual paper. **Genuinely open.**
2. **`WORKPLAN.md` ownership/cadence?** No evidence found anywhere in any of the four sweeps.
   **Unaddressed gap.**
3. **Rollout order?** No source sequences these moves. Indirect signal: all three patterns exist and
   succeed independently elsewhere (Cursor scoping without hooks, Claude Code hooks without a
   WORKPLAN-equivalent, Devin's split without hook enforcement), implying no strict dependency — but
   this is inference from absence, not a finding. **Unaddressed by direct evidence.**
4. **Delete-on-replacement vs. all-at-once?** Explicitly checked for in every sweep and explicitly
   not found anywhere. **Confirmed unaddressed** — this remains a judgment call DDR-005 has to make
   without external precedent.

---

## 5. Notable gaps in this research pass (stated, not papered over)

- **No HN or Reddit thread was surfaced**, despite being explicitly searched for — the community
  sweep found only dev-blog-style sources. "Community convergence" above means convergence across
  independent blogs, not confirmed large-scale practitioner consensus.
- **Academic findings are WebSearch-snippet-level only** — no full-text WebFetch was performed on
  any arXiv paper. The single most DDR-005-relevant paper found (arXiv:2604.20911, omission vs.
  commission constraint decay) is title-only and unverified; treat as a lead to chase, not a citation
  to use as-is.
- **Not searched**: Windsurf, GitHub Copilot Workspace, OpenAI's own agent tooling (Codex CLI),
  AutoGPT-style frameworks — no finding either way.
- **No Anthropic source quantifies a conduct-vs-task token ratio** — DDR-005's central ~90/10 number
  has no external anchor of any kind.

---

## 6. Sources (flat list)

- https://code.claude.com/docs/en/best-practices
- https://code.claude.com/docs/en/hooks-guide
- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://arxiv.org/abs/2307.03172 ("Lost in the Middle")
- https://www.trychroma.com/research/context-rot
- https://arxiv.org/html/2608.12426 (compositional constraint satisfaction phase transitions)
- https://arxiv.org/pdf/2507.11538 ("How Many Instructions Can LLMs Follow At Once?")
- https://arxiv.org/html/2604.20911v1 (omission vs. commission constraint decay — title-only, unverified)
- https://arxiv.org/html/2506.09942 (VerIF)
- https://arxiv.org/html/2511.03508v1 (multi-turn instruction following benchmark)
- snippet-only, unverified: arXiv:2505.19030 (RECAST), arXiv:2411.01111 (Rule-Based Rewards), arXiv:2601.04770 (SciIF)
- https://dev.to/minatoplanb/i-wrote-200-lines-of-rules-for-claude-code-it-ignored-them-all-4639
- https://tianpan.co/blog/2026-02-14-writing-effective-agent-instruction-files
- https://dev.to/nishilbhave/claudemd-best-practices-the-complete-2026-guide-435j
- https://evilmartians.com/chronicles/stop-writing-rules-in-agents-md-use-agent-hooks-and-nano-staged-instead
- https://strandsagents.com/blog/steering-accuracy-beats-prompts-workflows/
- https://www.digitalapplied.com/blog/define-done-acceptance-criteria-agent-prompts-2026
- https://agents.md/ ; https://codersera.com/blog/agents-md-complete-guide-2026/
- https://cursor.com/docs/rules ; https://www.romanticode.com/blog/cursor-rules-vs-agents-md/
- https://aider.chat/docs/usage/conventions.html
- https://docs.cline.bot/best-practices/memory-bank
- https://fast.io/resources/devin-ai-playbook-guide/ ; https://fast.io/resources/devin-knowledge-guide/
- https://agentbuilderacademy.com/blog/claude-code-hooks-rules-nobody-builds
- https://www.dryrun.security/blog/top-ai-sast-tools-2026
- https://tweag.github.io/agentic-coding-handbook/examples-scripts/pre-commitator/

---

## 7. Raw per-sweep findings

Full structured findings from each of the four parallel research agents (Anthropic docs, academic
literature, practitioner community, adjacent frameworks) — including each sweep's own stated gaps —
are preserved in the workflow journal at:

`/home/d-tuned/.claude/projects/-home-d-tuned-agent-rig/56815b92-88fd-47d5-bf11-f599b2355192/subagents/workflows/wf_670c8f61-7d3/journal.jsonl`

(run ID `wf_670c8f61-7d3`). Retained there rather than duplicated in full here to keep this document
readable; consult the journal for the complete quote/evidence text behind any row above.
