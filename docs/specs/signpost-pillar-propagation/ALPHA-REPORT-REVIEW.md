# Independent Review — alpha's "Verify Before Assert" Handoff Report

- **Artifact:** `/home/d-tuned/market_data/docs/reports/HANDOFF-2026-08-07-verify-before-assert-what-actually-works.md`
- **Reviewer:** Frank (independent, map-not-route briefing — no access to Wright's or alpha's checklists)
- **Date:** 2026-08-08
- **Purpose:** source-credibility gate required by the `signpost-pillar-propagation` sprint AC before this report's mechanisms are cited as settled.

═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — HANDOFF-2026-08-07-verify-before-assert
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise [pass — the report's central numbers (17 days, four incidents, 32400/1800 timeout) are cited to named artifacts, and the ones I could reach check out]. Input [pass — I opened the raw sources myself: DDR-0009 header, `.git/hooks/`, `settings.local.json`, both scripts, the 06-29 postmortem, the live systemd unit]. Evidence independence [pass for this review — I did not read alpha's verification method, only the claims; my checks ran against the filesystem, not the report's own Provenance section].

Claims verified directly (all held):
1. **DDR-0009 status** — header reads exactly `**Status:** PROPOSED / QUEUED (not started)`. Confirmed. The report's warning that DDR-0009 is a plan, not a mechanism, is correct and is itself the report's most valuable caveat.
2. **No non-sample git hooks** — `/home/d-tuned/market_data/.git/hooks/` contains only `*.sample` files. Confirmed.
3. **`settings.local.json`** — exactly one top-level key, `permissions`. No `hooks` key. Confirmed via JSON parse, not eyeballing.
4. **Single root `CLAUDE.md`**, no scoped split. Confirmed.
5. **`assert_gate_date_coupling.py` fails closed** — verified adversarially myself: wrong date (`--target-date 1999-01-01`) exits 1 with a specific mismatch message; unknown unit exits 1 refusing to silently pass; retired unit name (`cron-yield-collision-gate.timer`) exits 1 (LoadState=not-found path). No-args also exits 1. The fail-closed claim is real, not asserted.
6. **`session_probe.py`** — exists, self-declares read-only (no write statements found in source), and ran end-to-end in **0.7s** against the live DB. Report says "~3s" — conservative, if anything.
7. **Incident 2026-06-29** — spot-checked against `docs/reports/POSTMORTEM-2026-06-29-v1-dead-code-and-false-alarm.md`. The report's one-row summary (confident inference from two true facts, caught by 2-minute verification, rule written into CLAUDE.md) matches the postmortem's own account precisely, including the dead-code detail.
8. **F1 (repo vs live unit)** — repo `systemd/cron-yield-gate.service` and live `~/.config/systemd/user/cron-yield-gate.service` both now read `TimeoutStartSec=32400`, i.e. consistent with the divergence having existed and been fixed. The historical "live was 1800" state is no longer observable — see below.

Claims I could NOT verify directly:
- The **historical** value of the live unit (1800) before the 2026-08-07 fix — the evidence was overwritten by the fix itself. Consistent with the record, unfalsifiable now. Low risk: the mechanism lesson (deployment step missing from verification plans) does not depend on the exact number.
- The 2026-07-07 incidents (Danny's verbal corrections) and the 17-day misdiagnosis timeline — these rest on PROGRESS.md, a LORE capture, and lived session history. The pattern is consistent with the artifacts cited, but two of the four table rows are ultimately testimony, not filesystem state. That is acceptable for a lessons doc; it would not be acceptable as quantitative evidence.
- Section 2.1's account of *how* Frank's 2026-08-07 review was briefed (map withheld, route withheld) — this is alpha's characterization of alpha's own briefing. Plausible, self-serving in shape, unverifiable from here.

Inference-presented-as-fact check:
- The report is unusually honest about its own epistemics — it opens by correcting its own success narrative, flags itself DRAFT/unreviewed, and its strongest claim ("prose rules demonstrably insufficient") is backed by the checkable incident record. One soft spot: Section 2.5's "repetition as a diagnostic instrument" generalizes from N=1 accidental discovery, and the report says so itself ("stumbled into, not designed"). Cite it as a heuristic, not a proven pattern.

Why:
The report's load-bearing structure is: (a) documented controls that don't exist on disk are the trap; (b) what works is executable fail-closed asserts, map-not-route briefing, ordering (probe before memory), and success/failure producing different bytes. Every filesystem-checkable claim underneath (a) and (b) verified clean, including the adversarial exit-code behavior — which I re-ran myself rather than trusting the report's "verified adversarially" line. The unverifiable residue is historical testimony that the report itself flags as such. The Provenance section's claims sample-checked at roughly 8-for-8.

Verdict: **SAFE TO CITE**, with two mandatory caveats when propagating:

1. **Do not propagate DDR-0009 / hook enforcement (retrofit item 6)** — the report itself says this, and I confirmed the mechanism does not exist. Any agent-rig artifact citing this report must carry that status forward, not just the recommendation list.
2. **Cite Section 2.5 (repetition-as-instrument) as a heuristic, not an established mechanism** — N=1, accidental, self-acknowledged.

The four mechanisms agent-rig is actually propagating — map-not-route briefing, `assert_*.py` fail-closed convention, `Verification:`/`Re-verify with:` capture lines, sentinel/observability — all rest on claims I verified directly or on incident history consistent with its cited postmortems. Good source. The DRAFT flag can be considered discharged by this review for citation purposes; the doc's own Status line remains alpha's to update.

═══════════════════════════════════════════════════════════════════
