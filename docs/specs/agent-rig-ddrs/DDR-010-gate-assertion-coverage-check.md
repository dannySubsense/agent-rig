# DDR-010 — Gate Assertion-Coverage Check

**Status**: DRAFT — incident verified directly against source, 2026-08-22 (alpha, in-repo, not secondhand)
**Author**: wright (recording a sidebar incident report, 2026-08-22; verified account folded in same day)
**Date**: 2026-08-22
**Scope**: cross-project — any repo that reports a "gate PASS" as evidence a specific capability is
working.

---

## 0. Provenance

Raised as a sidebar during the DDR-005/006/007 hook-pattern conversation, 2026-08-22. Danny shared
an assessment of an incident, confirmed 2026-08-22 as **alpha's `market_data` project** (repo
identified; the account below is Danny's assessment, not yet independently verified by wright
against the actual gate script — that verification is in progress via Switchboard with alpha, see
§4 Q1): a paid data-acquisition
path (an S3 flat-file feed) had silently stopped being used, with the pipeline falling back to a
REST API instead, for an unconfirmed period including at least a second paid month. The producer's
gate (`scripts/validate_massive_ingestion.py` per the report) checked data presence and provenance
tagging, and reported PASS throughout — because it had no assertion on *acquisition method*, only on
*data having arrived*. The producer reported gate-PASS as "the path is working," which the gate was
structurally incapable of verifying.

Danny's own diagnosis, quoted because it is the whole finding: *"A gate that can't fail on the
failure mode it exists to catch is not a gate."* And: *"exactly the certified-garbage pattern this
project has a standing rule against, and it happened anyway because the rule lives in my
instructions, not in the gate's code"* — i.e. this is a second, independent instance of the same
family DDR-006 already generalizes from (PROMOTED DEFAULT → SHARED WELL → CERTIFIED GARBAGE), but a
different failure shape within that family: not a borrowed *value* crossing a domain boundary
unexamined, but a claimed-verified *capability* with no assertion capable of falsifying it.

**Verified directly by alpha, 2026-08-22, against the live repo (not secondhand):**

1. `scripts/validate_massive_ingestion.py` has exactly 3 assertions —
   `assertion_1_breadth_vs_scope`, `assertion_2_provenance_non_null_since_deployment`,
   `assertion_3_rollup_spot_check`. Nothing checks acquisition method (flat-file vs. REST).
2. Root cause confirmed exactly: the pipeline's 01:00 UTC run fired 4+ hours before the vendor's
   actual publish window (~04:45–05:36 UTC, per S3 `head_object LastModified`), deterministically,
   every night — 0/26 nights the flat file was available at run time. Not stochastic; structural.
3. Fix already shipped same session (Fix 2 in the original assessment): Step 5/5a moved out of
   `daily_update.py`'s 01:00 run into `fetch_massive_intraday_bars.py`'s own `main()`, now on a
   separate 06:30 UTC cron (`run_massive_intraday_late.sh`). Test suite green (476 passed).
   **Not yet production-confirmed on a live trading night** as of this DDR — next fire is the
   normal weekday cron.
4. Incident captured to LORE, `market-data` project, documentId `9b82235c-29a8-4e80-a120-e95cc1fd1ab6`.
5. Fix 1 (the 4th assertion this DDR proposes) is **queued, not yet built** — Danny wants Fix 2
   production-confirmed first before deciding on further Massive spend.

**Alpha's correction to the proposed check itself** (important — changes §2 below): a bare
trailing-window success-rate threshold is the right shape but can pass by luck. If a *different*
structural defect later starts routing through the same fallback path, a rate staying above
threshold "by luck" would hide it. The fix: the assertion's failure (and pass) must carry *why*
the fallback fired — not-yet-published vs. genuine miss vs. something else — as part of the
assertion's output, not just a pass/fail boolean.

## 1. The pattern

A "gate PASS" is repeated as "X is confirmed working," where X is never actually in the gate's
assertion set — only some correlate of X (data arrived) is. The gate cannot fail on the specific
way X breaks, so it cannot catch it, and its PASS gets reported as broader coverage than it has.

This is distinct from DDR-006 (unsourced value crossing a domain boundary) and from DDR-007
(narration substituting for substance) — a third, separate member of the same family, not a
duplicate of either.

## 2. The check

For any claim of the form "gate PASS confirms capability X," verify the gate's own assertion list
actually contains a check capable of failing specifically because of X's failure mode — not merely
a check whose output correlates with X when X is healthy. Concretely, per the sidebar report's own
proposed Fix: an ingestion gate asserting "data present, correctly tagged" is not evidence the paid
acquisition path was used; a gate asserting "flat-file success rate over a trailing window > 0%" is.

**Presence/absence, not judgment**: this is checking whether an assertion exists for a claimed
capability, not judging whether an existing assertion is well-written (that stays `benchmark`'s and
Frank's job, consistent with DDR-006 §1's same carve-out).

**Amended per alpha's correction above**: an assertion that exists but is a bare boolean/rate
threshold with no reason-coded failure output does not fully close this pattern — it can still go
green "by luck" if a different defect later shares the same symptom. The check should verify not
just that an assertion exists for capability X, but that a failing assertion for X would tell a
reader *why*, not merely *that*.

## 1a. Alpha's proposed extension — gate-design-time review, not just postmortem/runtime check

Alpha, asked by Danny to weigh in directly (2026-08-22): the deeper fix isn't only a runtime/lint
check on existing gates — it's a **design-time question**. This gate shipped with a documented
3-assertion contract and nobody asked what was outside that contract until the cost surfaced.
Proposed: any gate protecting a paid or architecturally load-bearing capability should have to
answer "what does this assertion set fail to see?" explicitly before it ships — e.g. as a
checklist item in whatever spec/gate-design step agent-rig owns (`notebook-design` or equivalent),
not only as a hook that audits gates already in production.

**Scope flag for Danny**: this cluster's rollout policy (00-DDR-INDEX.md, hook-mechanization
cluster header) was scoped hook-only (D7, 2026-08-22). Alpha's extension is partly that (a runtime
check) and partly a **spec-process addition** (a design-time checklist question), which is a
different kind of artifact than the other four items in this cluster. Recommend keeping DDR-010
itself scoped to the runtime/lint check (in-cluster, hook-only, consistent with D7), and tracking
alpha's design-time-checklist proposal as a separate, related backlog item — not silently folded
into DDR-010's scope. Danny's call.

## 3. Relationship to DDR-006

Same family, different member. DDR-006 catches: *a value used here was never re-justified for this
use.* DDR-010 catches: *a claim made here was never actually checkable by the thing being cited as
proof.* Both are instances of the founding postmortem's PROMOTED DEFAULT / CERTIFIED GARBAGE
shape — DDR-006 on the value side, DDR-010 on the verification-claim side. Worth building on shared
tooling where practical (both are static analysis over a pipeline's own docs/config/gate-script
triplet), but they are not the same check and should not be merged into one DDR.

## 4. Open questions

1. **Source repo and verification — RESOLVED.** Repo: alpha's `market_data`,
   `scripts/validate_massive_ingestion.py`. Verified directly by alpha against the live repo,
   2026-08-22 (see §0) — meets the same standard DDR-006 met before its Accept. Remaining before
   Accept: Danny's ruling on where DDR-010 sequences in the build order (currently outside the
   ranked cluster, per 00-DDR-INDEX.md), and on §1a's scope question (design-time checklist —
   in/out of this DDR).
2. **How "capability X" gets named/scoped for the check to key on.** DDR-006 has a clean trigger
   (a value read from outside the pipeline's own config). This check's trigger is fuzzier: it needs
   some declared list of capabilities a gate is supposed to cover, checked against its actual
   assertions — that declared list doesn't exist yet anywhere and would need designing.
3. **Whether this generalizes to a static lint (compare a gate's assertions against its own
   docstring/spec claims) or needs a runtime component** (e.g. trailing-window success-rate
   assertions, per the sidebar's own proposed Fix 1) — likely both, but which is core to this DDR
   and which is a downstream implementation detail of the specific gate being fixed needs deciding
   at spec time.

## 5. Next step

Intake, per this repo's standard workflow — including resolving Q1 (source/verification) before
Intake is written, not after.

---

## References

- `docs/specs/agent-rig-ddrs/DDR-006-domain-boundary-provenance-hook.md` — sibling pattern, same family
- `~/.claude/CLAUDE.md` — Research Data Integrity rules 1–3, PROMOTED DEFAULT → SHARED WELL → CERTIFIED GARBAGE doctrine
- `market_data` LORE, documentId `9b82235c-29a8-4e80-a120-e95cc1fd1ab6` — the verified incident capture
- Switchboard thread `ddr-010-gate-assertion-coverage`, 2026-08-22, wright ↔ alpha
