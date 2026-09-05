# 05-REVIEW — Verification Pass (editorial loop iteration 2 of 2)

**Status**: VERIFIED — clean to proceed to Frank's spec-gate
**Date**: 2026-09-05
**Reviewer**: spec-review (independent)
**Scope**: targeted re-verification of G-3, G-4, G-5, G-7 only, plus a new-contradiction check.
Objectives 1/2/4/5/6 from the prior pass are not re-reviewed (already passed, not expected to
regress). All findings below are from direct reads of current file content on 2026-09-05, not from
either correction agent's self-report.

---

## Verification Results

| ID | Finding (prior pass) | Verdict | Evidence (current files) |
|---|---|---|---|
| **G-3** | Constant name mismatch / collision risk | **RESOLVED** | Architecture names the new constant `PROXIMITY_WINDOW_THRESHOLD` in §4 (L203), §7 (L391), §8 (L443), §13 (L519). Roadmap uses the identical name in the Dependency Map (L34), Slice 4 (L47, L181, L213), Slice 9 (L34, L416, L438, L445), and Deferred (L576). No third spelling anywhere in either doc. Live probe (`scripts/domain_boundary_provenance_probe.py`) defines only `PROXIMITY_WINDOW = 5` at L51; a full read of the file shows no `PROXIMITY_WINDOW_THRESHOLD` and no other module-level name it could shadow. **No collision.** |
| **G-4** | No exact required comment text; incumbent's L50/L51 disposition unclear | **RESOLVED** | Architecture §7 L386–390 gives the literal comment block, starting `# THRESHOLD-PROVENANCE: PROVISIONAL — owner: wright, unmeasured.`, immediately above `PROXIMITY_WINDOW_THRESHOLD = 3` (L391), and L392–401 states it is "the exact text to land in" the probe file, with the explicit reason a bare `PROVISIONAL —` line would fail `has_threshold_provenance_marker`. §8's G-9/G-4 row (L443) gives two distinct per-constant answers: incumbent's `PROXIMITY_WINDOW = 5` (probe L51) has no name-gate word, context 2 never fires, its existing L50 comment **needs no change** — confirmed against the live file (L50 reads `# §5 — PROVISIONAL, owner: wright. …`, name contains none of `limit/cap/threshold/cutoff/retry/retries/budget/timeout/max/min`). Roadmap Slice 4 mirrors this: Implementation Note L193–200 and Done-When L215–217 require the adjacent comment to start with the literal `THRESHOLD-PROVENANCE:`, verbatim per §7, verified by direct read rather than test inference. Slice 9 (L409–423, Done-When L445–447) requires **two separately named** fixture cases — `PROXIMITY_WINDOW` unflagged (name gate never fires) vs. `PROXIMITY_WINDOW_THRESHOLD` cited (gate fires, marker satisfies) — explicitly "not merged into one case or one assertion." Distinguishable and correct. |
| **G-5** | `mode` nullable / wrapper writes `null` | **RESOLVED** | Architecture §6 schema L313 declares `mode: "log_only" \| "blocking";` with no `\| null`, and L338–362 states the rationale plus the concrete new wrapper responsibility: `.claude/hooks/domain-boundary-provenance.sh` reads `docs/tooling/domain-boundary-mode.json` itself when constructing any `probe_error` entry, with the same fail-safe default (`absent/unreadable/invalid → "log_only"`). Roadmap Slice 8 matches exactly — Goal L344–346 ("`mode` is never `null`"), Implementation Note L357–364 (shell-native read, `jq`→`grep`/`sed`→`log_only` fallback; only `cross_domain`/`local_threshold` detail fields may stay null), Tests L376–381, Done-When L387. No occurrence of writing `null` for `mode` remains in the Roadmap. |
| **G-7** | LOCKED spec §3's explicit rejection of unscoped blocking `PreToolUse` not engaged | **RESOLVED** | Architecture §3 L142–161 is a dedicated reconciliation paragraph. It (a) names the rejection and its stated grounds ("required to keep this both correct and low-noise"), (b) concedes the new pass is *by shape* exactly the rejected surface, (c) does not claim the rejection is settled by silence, (d) argues `log_only` (§5) withholds the one property — blocking — that made the rejection apply, so noise surfaces as track-record entries not disrupted edits, and (e) states what evidence would justify promotion (per-repo track-record false-positive data, matching the DDR-0014 amendment's per-repo promotion rule), while explicitly making no promotion decision here. This is genuine engagement, not restatement. |

**Blocking items remaining: 0.**

---

## New-Contradiction Check (Architecture ↔ Roadmap)

Checked: slice numbering and cross-references, dependency ordering, every constant/function/type
name, file paths, and Done-When criteria touched by the four fixes.

| Area | Result |
|---|---|
| Slice numbering | Consistent. 12 slices in the overview table, 12 detail sections, no gaps/duplicates. All internal references resolve (Slice 4 → 5, Slices 1/2/5 → 6, 6 → 7, 7 → 8, 1–8 → 9, 1–9 → 10, 10 → 11, 1–11 → 12). Architecture's forward references to "Slice 4", "Slice 9", "Slice 10", "Slice 12" (§4 L210, §8 L443, §6 L338, §3 L151) all point at the slice that actually owns that work. |
| Constant/type/function names | Consistent across both docs: `load_mode_config`, `detect_threshold_literals`, `FlaggedLiteral`, `has_threshold_provenance_marker`, `PROXIMITY_WINDOW_THRESHOLD`, `run_cross_domain_pass`, `run_local_threshold_pass`, `PassResult`, `combine`, `CombinedResult`, `TrackRecordEntry`. No drift introduced by the fixes. |
| Values | `PROXIMITY_WINDOW_THRESHOLD = 3` (both docs); incumbent `PROXIMITY_WINDOW = 5` (both docs + live file L51); mode file initial value `{"schemaVersion": 1, "mode": "log_only"}` (Arch §5 L283, Roadmap Slice 2 L97/L103). |
| Paths | `docs/tooling/domain-boundary-mode.json`, `.claude/hooks/domain-boundary-provenance.sh`, `scripts/domain_boundary_provenance_probe.py`, `.claude/settings.json`, `HOOK-DEPLOYMENT-ROSTER.md` — identical in both docs, all real or precisely named-new. |
| Fix-induced contradictions | **None found.** The G-5 fix (wrapper reads mode) is reflected in the Roadmap's Dependency Map row (L30) as well as Slice 8, so the dependency graph did not go stale. The G-3/G-4 fix is reflected in the Dependency Map's corpus row (L34) as well as Slices 4 and 9. |

### Minor (non-blocking) — label collision, pre-existing, carried forward

Architecture §8's table reuses the labels **G-4** and **G-7** for review findings *different from*
the ones this pass verified: §8's `G-7` row is the "`run()` takes `mode` as param AND reads config"
item, and §8's `G-4` row is the "US-4 AC2 has no verification path / no soundness-implying language"
item. The Roadmap inherits both readings — Slice 4 L193 cites "Architecture §7/§8 G-4/G-9" meaning
the self-scan comment, while the HALT Check L598 cites "§8's G-4 finding (no soundness-implying
language)". Both citations are individually correct against §8's own numbering, but the same label
denotes two different things within one document. This is a documentation-navigability nit, not a
design contradiction — the underlying obligations (Slice 4's comment text, Slice 9's grep test) are
both present and unambiguous in prose. Recommend a one-line renumbering or disambiguating note in
§8's header on the next edit; not worth blocking the gate.

---

## Risks (unchanged from prior pass, no new ones introduced)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Unscoped `.py` scan produces high false-positive volume | H | M | `log_only` initial mode (Arch §5); Slice 12 collects the data; promotion is a separate per-repo decision |
| `PROXIMITY_WINDOW_THRESHOLD = 3` and the §2 exclusion/name-word lists are unmeasured | H | L | Both carry `PROVISIONAL — owner: wright`; Slice 12 surfaces revision data |
| Wrapper's shell-native mode read mis-parses a hand-edited mode file | L | L | Fail-safe default to `log_only` on any non-zero exit/empty result (Arch §6, Slice 8) |
| Schema migration breaks the incumbent's existing tests | M | M | Slice 1 is a pure extraction gated on the unmodified pre-existing suite passing; Slice 7 Done-When requires diff review |

## Assumptions

| Assumption | Impact if wrong |
|---|---|
| §7's "exact comment text" means the comment block at L386–390, not the trailing `# ^ This comment…` annotation at L392–401 | Forge lands explanatory meta-commentary in the probe source; cosmetic, and the Done-When's "starts with `THRESHOLD-PROVENANCE:`" still holds |
| The live probe file will not gain a `PROXIMITY_WINDOW_THRESHOLD`-named symbol from another sprint before forge runs | Name collision reappears; low risk, single-owner file |

## Open Questions

| Question | Status |
|---|---|
| Should Architecture §8's duplicate G-4/G-7 labels be renumbered? | Open — editorial, non-blocking |

None require human input before the gate.

---

## Approval Checklist

### Requirements (01)
- [ ] Reviewed by human — note Architecture §12 lists five corrections owed to this doc (Stop-vs-PreToolUse, US-1 AC1, US-3 reuse lineage, Out of Scope, North Star) which are **not** fixed by this pass

### Architecture (02)
- [x] G-3 constant name unique and consistent, verified against live source
- [x] G-4 exact comment text specified; incumbent's `PROXIMITY_WINDOW` correctly requires no change
- [x] G-5 `mode` non-nullable, wrapper reads mode config
- [x] G-7 LOCKED §3 rejection engaged explicitly
- [ ] Reviewed by human

### Roadmap (04)
- [x] Slice 4 and Slice 9 reflect G-3/G-4 exactly, with two distinguishable self-scan fixture cases
- [x] Slice 8 reflects G-5 exactly, no `null` mode path
- [x] No slice-numbering, naming, path, or Done-When contradiction introduced
- [ ] Reviewed by human

### Overall
- [x] All four flagged gaps resolved
- [x] No new Architecture↔Roadmap contradiction
- [x] All risks have mitigations
- [ ] Human approval + Frank's binding spec-gate

---

**Verdict: CLEAN TO PROCEED.** G-3, G-4, G-5 and G-7 are genuinely resolved in current file
content, and the fixes introduced no new inconsistency between Architecture and Roadmap. One
non-blocking editorial nit (§8's duplicated G-4/G-7 labels) and the five outstanding
`01-REQUIREMENTS.md`/`NORTH-STAR.md` corrections Architecture §12 already flags remain open for the
human/gate to dispose of.
