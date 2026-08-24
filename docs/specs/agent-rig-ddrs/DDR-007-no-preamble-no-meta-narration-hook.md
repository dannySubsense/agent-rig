# DDR-007 — No-Preamble / No-Meta-Narration Response Hook

**Status**: FORGE COMPLETE (2026-08-24) — implemented, tested, QC'd, Frank's binding forge-gate
PASS (attempt 1/3, both layers, no PROVISIONAL). PR #16 ready-for-review, not yet merged. Ships in
`log_only` mode — promotion to `blocking` is a separate, evidence-gated future decision per
SPEC.md §6.4's PROVISIONAL threshold (owner: Danny), not authorized by this build.
**Author**: wright
**Date**: 2026-08-22 (index entry); this record authored 2026-08-24
**Scope**: agent-rig build, cross-project reuse expected — same shape as DDR-006/DDR-008's
Stop-hook infrastructure.

---

## 1. What this DDR tracks

Detects and blocks first-person meta-narration substituting for substance in assistant responses:
intent announcements ("I'm going to..."), stall-before-substance openers, honesty/ownership
cushioning, praise padding, performative-effort narration, emotional-state narration. Mechanizes
this repo's own "Don't narrate your internal deliberation" instruction (and every sibling
project's equivalent prose) — currently an exhortation, not a check, the same failure shape
DDR-005 §1 names generally and DDR-006/DDR-008 already mechanized for their own domains.

**Detection mechanism**: a grammatical rule — subject "I"/"we" + internal/communicative verb + no
concrete noun in the same clause = flag — not a fixed phrase list (trivially bypassed by
rewording).

**Trigger surface**: two-part, per `prompt-router-starter` precedent — pre-generation
`UserPromptSubmit` style injection + post-generation `Stop`-hook pattern block, same family as
`first-turn-contract-enforcement`.

**Rollout**: starts observe/log-only, promoted to blocking once false-positive rate is measured
low (threshold not yet defined — open question, Intake §Open Questions item 2).

## 2. Relationship to DDR-005 and sibling hooks

One concrete instance of DDR-005's general thesis (mechanize conduct, don't leave it as prose),
build-order 3rd in the hook-mechanization cluster (`00-DDR-INDEX.md`), after DDR-006 (merged PR
#11) and DDR-008 (merged PR #13, live in agent-rig). Reuses `first-turn-contract-enforcement`'s
Stop-hook wrapper shape (bounded timeout, fail-open, append-only track-record log) rather than
redesigning it.

## 3. Explicitly out of scope — DDR-011

Plain-language / no-AI-slop-jargon detection was proposed as a possible addition to this hook
(Danny, 2026-08-24) and deliberately split into its own DDR (`00-DDR-INDEX.md` row 011) rather
than folded in here: the detection method differs (vocabulary/register-based vs. this hook's
grammatical-structural rule), and combining them would make this hook's own false-positive rate
unmeasurable during its observe/log-only soak. No acceptance criterion in this DDR's eventual spec
may test for jargon/plain-language violations.

## 4. Not yet decided (open, per DRAFT status)

See `docs/tooling/no-preamble-no-meta-narration-hook/INTAKE.md` §Open Questions for the full list
— summarized: the exact grammatical rule (verb set, "concrete noun" test, clause-boundary
detection), the false-positive threshold for promotion to blocking, how the rule distinguishes
legitimate first-person status updates from substance-substituting narration, whether this extends
`first-turn-contract-enforcement` or ships as a separate sibling hook, and retrofit-roster scope.

## 5. Next step

Intake approved (`docs/tooling/no-preamble-no-meta-narration-hook/INTAKE.md`, APPROVED,
2026-08-24, Danny). `spec-start --lite` proceeds to the single-document `SPEC.md` via
`@architect`.

---

## References

- `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` row 007 — original index entry, build-order 3rd
- `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` row 011 — split-out plain-language/jargon hook
- `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — the general thesis this
  is one instance of
- `docs/tooling/first-turn-contract-enforcement.md` — the Stop-hook reference implementation this
  extends
- `docs/tooling/progress-md-proof-per-slice-hook/` — most recent sibling build, current Lite Mode
  File Layout precedent
- `~/.claude/CLAUDE.md` — Research Data Integrity rules 1–3, PROMOTED DEFAULT → SHARED WELL →
  CERTIFIED GARBAGE doctrine
