# Roster `.gitignore` audit — Components 4/7 durability

**Date:** 2026-08-12 · **Author:** wright · **Sprint:** `signpost-pillar-propagation` (Slice 11)

**Trigger:** `alpha` reported (Switchboard, thread `signpost-pillar-propagation`, 2026-08-12) that
`market_data` gitignores `CLAUDE.md` at `.gitignore:36`, so Components 4/7 exist on disk there but
outside version control. Their point: the Slice 10 pilot is unrepresentative on exactly the two
practice-only components Slice 11 rolls out, and per-repo state should be checked before Slice 11
is called done anywhere.

**Method:** for each of the 8 roster repos named at `02-ARCHITECTURE.md:321-322`, checked (a) the
ignore rule via `git check-ignore -v CLAUDE.md`, (b) whether the file is *actually tracked* via
`git ls-files --error-unmatch` — these can disagree, and the tracked state is the one that governs
what survives a clone — and (c) whether Component 4/7 content and the probe artifacts are present.

## Results

| Repo | `CLAUDE.md` tracked? | Ignore rule | C4 present | C7 present | Probe + hook |
|---|---|---|---|---|---|
| `market_data` | **no** | `.gitignore:36` | yes | yes | **yes** |
| `electric-blue` | **no** | `.gitignore:2` | no | no | no |
| `gap-lens-dilution` | **no** | `.gitignore:15` | no | no | no |
| `gap-lens-dilution-filter` | **no** | `.gitignore:42` | no | no | no |
| `ask-edgar-repo` | **yes** | none | no | no | no |
| `sonic-store` | **yes** | none | no | no | no |
| `quant-foundry` | **no** | `.gitignore:1` | no | no | no |
| `runtime/agent-lore` | **no** | `.gitignore:31` | no | no | no |

All 8 repos have a `CLAUDE.md` on disk. Every one of the 6 ignored cases is a real, explicit
`.gitignore` entry — not an incidental glob match.

## Findings

**F1 — The roster is split 6/2, and the majority case is untracked.** Six of eight repos gitignore
`CLAUDE.md`; two track it. `agent-rig` itself also gitignores its own (stated in that file). So the
untracked case is the house norm, not an outlier — `market_data` was representative after all, just
not in the direction that helps.

**F2 — "Slice 11 done" is not a durable claim in 6 of 8 repos.** Components 4 and 7 are delivered
*as CLAUDE.md prose*. Where that file is untracked, applying them changes one working copy on one
machine: the change does not survive a fresh clone, is invisible to every other agent and to code
review, and cannot be verified by anyone who is not sitting on that filesystem. The rollout would
report 8/8 complete while 6 of those 8 are machine-local state.

**F3 — Verification method for Slice 11 must not be file-content inspection alone.** Reading
`CLAUDE.md` on disk returns *present* in exactly the case that is least durable. The check has to
include tracked-status, or it certifies the failure mode. This is the same shape as the exec-bit
defect (`docs/reports/retrofit-procedure-verification-2026-08-12/`): the naive observation returns
"fine" precisely when it isn't.

**F4 — Only `market_data` is retrofitted at all.** The other 7 have no probe, no hook, and no C4/C7
content. Three (`ask-edgar-repo`, `sonic-store`, `runtime/agent-lore`) lack even a Session Start
Behaviour section. Slice 12's blast radius is therefore 7 greenfield installs, not 7 cutovers —
the step-3 "remove the prior variant" step will be a no-op in most of them, and the procedure should
say so rather than leaving each resident agent to discover it.

## Open question for the composer — not decided here

Components 4/7 were specified as CLAUDE.md edits on the assumption that CLAUDE.md is a durable,
reviewable project artifact. In 6 of 8 roster repos it is explicitly not. This is a **premise defect
in the architecture**, not an execution gap, and it is not agent-rig's call to resolve unilaterally
across other agents' repos. Three candidate directions, for Danny:

1. **Untrack-and-accept** — treat C4/C7 as deliberately machine-local practice, and drop the claim
   that Slice 11 propagates anything durable. Cheapest; weakest.
2. **Move C4/C7 into a tracked file** — e.g. a committed `docs/SESSION-START.md` that CLAUDE.md
   references. Durable and reviewable; costs a per-repo edit and a spec amendment.
3. **Per-repo resident-agent decision** — each agent decides whether to track their own CLAUDE.md.
   Consistent with the sprint's "resident-agent-owned retrofit" principle; yields a split roster
   permanently.

**Recommendation: (2).** It is the only option under which "Slice 11 complete" means the same thing
in all 8 repos, and it preserves the sprint's own thesis — orchestration mechanics hardened once,
centrally, not left to drift per consumer. It requires amending the architecture's Component 4/7
definitions, so it needs the composer's decision before any Slice 11 work proceeds.

**Slice 11 remains HELD pending that decision.** Slice 12 is unaffected by this finding — its
components (1-3) are tracked script and settings files in every case.
