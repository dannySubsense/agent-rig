# DDR-006 — Unsourced-Threshold Provenance Hook (implementation-side record, renamed 2026-09-05, was "Domain-Boundary Provenance Hook")

**Status**: **Corrected 2026-09-05 — v1 already SHIPPED, currently unwired; extension in
spec-gate.** v1 (domain-crossing-only scope) was specced (Frank spec-gate PASS attempt 3/3 +
supplementary), forged (Frank forge-gate PASS attempt 1/3, binding), and merged — PR #11, `.claude/hooks/domain-boundary-provenance.sh` +
`scripts/domain_boundary_provenance_probe.py`, LOCKED spec at
`docs/tooling/domain-boundary-provenance-hook.md`. **It is built but not currently wired into
`.claude/settings.json`** — confirmed by direct read, no live entry. A 2026-09-05 scope-broadening
amendment (see DDR-0014 §"Amendment, 2026-09-05") extends this hook with a new same-file/local
threshold detection pass; that extension sprint (`docs/specs/domain-boundary-provenance-hook/`) is
currently in Frank's binding spec-gate loop (attempt 1/3 FAIL, in remediation) as of this
correction. This file previously described v1 as "not yet spec'd/forged" — that was stale from
before the original build shipped and is corrected here.
**Author**: wright
**Date**: 2026-08-22 (v1), corrected 2026-09-05
**Scope**: cross-project — implemented and stewarded in agent-rig, run against any homelab
pipeline that has an unsourced threshold-shaped literal (own-pipeline or cross-domain).

---

## 0. Relationship to gap-lens-dilution-filter DDR-0014

**This is a short, implementation-side record, not a restatement.** The spec, both source
incidents, the rationale, and the ownership split are all recorded once, in
`gap-lens-dilution-filter/docs/DDR/DDR-0014-DOMAIN-BOUNDARY-PROVENANCE-CHECK.md` (originally
`docs/decisions/`, renamed to `docs/DDR/` same session; commit `eca45d2`, authored by
beta/gaplens-SEC, **Status: Accepted, Danny, 2026-08-22**). Do not duplicate that content here —
per DDR-0014's own §"Decision", two copies of the same decision is the cross-project shape of the
exact defect its `universe_membership.py` precedent exists to prevent (one rule, drifting across
multiple restatements). Read DDR-0014 directly for: the WHO byte-cap incident (2026-07-13
postmortem), the OQ-5 borrowed market-cap-floor incident (2026-08-20/22), the proposed check's
exact shape, and what the check explicitly does *not* do (judge whether a cited rationale is
sound — that stays `benchmark`'s and Frank's job).

**Ownership split** (agreed over Switchboard thread `hook-patterns-vs-prose-conduct`,
2026-08-22, wright ↔ beta, confirmed by Danny): DDR-0014 is the spec of record. Agent-rig owns
the build — this DDR tracks that build, since the mechanism is cross-project by design and
agent-rig already stewards the Stop-hook / first-turn-contract reference implementation this
extends.

## 1. What this DDR tracks

The implementation of DDR-0014's check: a hook-shaped presence/absence + citation verification —
for any numeric constant, cap, threshold, or boolean flag a pipeline reads from outside its own
config/spec (a shared DB column, an imported module's constant, an inherited default), the
consuming pipeline's own docs/spec must cite *why that value is correct for this use*. Absence of
that citation is a flagged finding.

Per DDR-0014 §"Consequences" and §"Alternatives considered": this is complementary to, not a
replacement for, the `benchmark` agent (which judges whether an *existing* citation is actually
good) — this hook only closes the "no citation at all" gap, unattended, without needing an agent
dispatch to be remembered.

## 2. Resolved in v1 (shipped, PR #11)

- **Hook event and trigger surface: PreToolUse**, on Edit/Write, gated by an explicit per-repo
  manifest (`docs/tooling/domain-boundary-manifest.json`) — not pre-commit, not scheduled. See
  `docs/tooling/domain-boundary-provenance-hook.md` §3 for full rationale.
- **Detection rule: explicit manifest** (`pipelineConfigGlobs` + `externalSourceIdentifiers`), not
  static import/reference analysis. See that spec's §4.
- **Citation convention: `DOMAIN-BOUNDARY:` marker**, 5-line proximity window, PROVISIONAL owner
  wright. PROVISIONAL-tag reuse was explicitly considered and rejected (semantically wrong claim).
  See that spec's §5.
- **Rollout scope**: agent-rig build only (Intake OQ-4). Retrofit into gap-lens-dilution-filter or
  elsewhere is separate, later work — not yet started as of this correction.

## 3. Not yet decided (open, per the 2026-09-05 extension sprint currently in progress)

- **Wiring v1 live**: `.claude/settings.json` has no entry for this hook. Getting it live (under
  `log_only`, per the extension sprint's Architecture §11/§3) is in scope for the current
  extension sprint, not a separate future task.
- **Extension detection rule** for same-file/local threshold-shaped literals (the 2026-09-05
  amendment's scope) — being resolved in `docs/specs/domain-boundary-provenance-hook/02-ARCHITECTURE.md`
  (currently in Frank spec-gate remediation, attempt 1/3 FAIL, fixes in progress).
- **Sequencing against DDR-005.** Unchanged from v1 — still one concrete instance of DDR-005's
  general thesis.

## 4. Next step

Frank's binding spec-gate for the extension sprint, attempt 2/3 (attempt 1 FAILed on two blocking
findings, both routed for correction as of this update). See
`docs/specs/domain-boundary-provenance-hook/GATE-LOG.md` for current state — read that file
directly rather than trusting this DDR's account of it, since this DDR was itself found stale in
this same correction pass.

---

## References

- `gap-lens-dilution-filter/docs/DDR/DDR-0014-DOMAIN-BOUNDARY-PROVENANCE-CHECK.md` (Accepted, commit `eca45d2`) — the spec of record
- `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — the general thesis this is one instance of
- `docs/specs/first-turn-contract-enforcement/` — the Stop-hook reference implementation this extends
- `~/.claude/CLAUDE.md` — Research Data Integrity rules 1–3, PROMOTED DEFAULT → SHARED WELL → CERTIFIED GARBAGE doctrine
- Switchboard thread `hook-patterns-vs-prose-conduct`, 2026-08-22
