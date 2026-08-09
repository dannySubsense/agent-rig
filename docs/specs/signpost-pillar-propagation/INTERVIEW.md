# Interview: signpost-pillar-propagation

**Status**: Complete
**Mechanism**: Inline
**Date**: 2026-08-08

## Seed Questions (gap-diff)

| # | Category | Question | Answer | Assumed? |
|---|---|---|---|---|
| 1 | testing/rollback | If a propagated hook masks priming again in a different repo, how do we catch/roll it back — per-repo manual monitoring, or something more structural before retrofit is called done? | Trace-verify each retrofit at the time it's done (live tool-call trace, same bar as department-os); no standing ongoing monitor after. A future regression is treated as its own incident if it happens, not pre-emptively monitored for. | no |
| 2 | non-functional | Any performance/security constraint (probe runtime budget, sandboxing) to lock into the Intake now, or leave to architecture? | Leave to architecture. No hard ceiling stated at Intake level; architecture sets a probe runtime budget and confirms no elevated-privilege operations. | no |
| 3 | downstream impact | Other agents already run their own probe-style scripts (Cairn's Major Tom variant, beta/gaplens-SEC). Does this sprint's canonical hook aim to eventually replace those, or coexist indefinitely? | **Full replacement is the goal**, not indefinite coexistence — but explicitly NOT a one-size-fits-all sweep. Each project's blast radius (doc references, existing script call-sites, project-specific variants) must be individually evaluated before cutover; assuming uniform propagation risks leaving stale references scattered across docs. | no |
| 4 | edge cases | What should happen if the probe hook itself errors (git command fails, LORE gateway unreachable) during a real session? | Fail loud — inject the error itself into `additionalContext` so the agent sees "probe failed: <error>" rather than silence, matching DDR-004 §6's stated bias against silent skip. | no |

## Adaptive Follow-ups

| Triggered by | Question | Answer |
|---|---|---|
| Q3 (full-replacement + per-project blast-radius audit) | Who performs the audit/sanitization for each project — that project's own resident agent, or a centralized pass by Wright/agent-rig across all repos? | Each project's own resident agent does its own audit — with an independently dispatched, unbriefed Frank gate per project as the audit's check (map-not-route: Frank gets the objective/architecture, not the resident agent's own checklist). |
| Q3 (follow-up 1) | Given blast radius varies per project and this is a full replacement, should each project's cutover go through its own Frank gate before being called done, or is agent-rig's sprint-level Frank gate sufficient? | Per-project Frank gate at cutover — confirmed as the recommended default. Each project's cutover (old variant removed, new canonical hook live, no stale references left) is independently verified, not assumed correct because the sprint-level spec passed once. |

## Stopping Rationale

6 exchanges total (4 seed + 2 adaptive follow-ups), within/just above the 5-7 soft anchor. Q1, Q2, and Q4 were each non-generative (answer confirmed the recommended default, opened no new thread). Q3 was generative — it introduced a new, unresolved thread (full replacement with per-project blast-radius audits, not indefinite coexistence or a uniform sweep) — which triggered two adaptive follow-ups, fully resolving audit ownership (per-project resident agent) and gate mechanism (per-project Frank gate, unbriefed/map-not-route). The follow-up thread's second answer was non-generative (confirmed the recommended default), and no further gap remains open across the four categories. Stopped here rather than continuing to pad toward a higher count.
