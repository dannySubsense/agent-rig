# Gate Log: progress-md-proof-per-slice-hook

## Spec Gate
Counter: 3/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|
| 1 | 2026-08-22 | FAIL | Layer 1 FAIL: §6 step 5's transition-detection prefix rule contradicts §4's own worked example — the canonical completion edit (COMPLETE segment inserted before PROOF:) is not a prefix match and would silently go undetected, making the hook a no-op on its own happy path. Layer 2 PASS, non-PROVISIONAL. | .gate-snapshots/progress-md-proof-per-slice-hook/spec/attempt-1/ |

| cold | 2026-08-22 | PASS (unbriefed second opinion) | Danny flagged that attempts 1-3 were not map-not-route — the orchestrator's dispatches told Frank specifically what to scrutinize (e.g. named the allowlist design "the single riskiest decision" ahead of his own read), a checklist not a map. A fresh, unbriefed Frank instance (objective + file path only) reviewed the same current SPEC.md independently. Concurred: PASS, both layers, non-PROVISIONAL. Confirmed prior findings (attempt-1 prefix contradiction, attempt-2 step5/step7 contradiction) genuinely closed by tracing the worked examples by hand, not by trusting the record. Found one new non-blocking nit missed by all three prior (briefed) passes: allowlist entry "npm test" has no trailing space, so exact-prefix match would also trust "npm testxyz" — forge-time tightening, not a gate finding. | n/a |
| 3 | 2026-08-22 | PASS (final) | Layer 1 PASS: F1 resolved — §4/§6 step 5/step 7 now route all four (old-PROOF × new-PROOF) combinations to one authority (step 7 inspects new_lines[i]), no residual "allows unconditionally" claim; AC3 clarified to new_lines[i]; new AC11 fixture exercises the add-proof-on-completion case end-to-end. F2 resolved as an honestly-stated §9 gap (mutation/deletion bypass), not softened, matching the existing Write/shell=True framing. Convergence: SHRINKING (no-op-on-happy-path → documentation contradiction one layer down → both closed, no new findings). Layer 2 PASS, non-PROVISIONAL, unchanged. Orchestrator's own independent read (§4, §6 steps 5-9, §9 re-verified directly) found no further issues — concurs with PASS. | .gate-snapshots/progress-md-proof-per-slice-hook/spec/attempt-2/ (pre-fix) |
| 2 | 2026-08-22 | FAIL | Layer 1 FAIL: attempt-1's F1/F2 genuinely fixed, but new F1 found one layer down — §6 step 5's parenthetical ("no PROOF: on old line → allows unconditionally") contradicts step 7 (extracts PROOF: from the NEW line and runs it if present). For an edit that ADDS a proof while completing a slice, one section says skip-and-allow, the other says run-and-possibly-deny. Also F2 (non-blocking but must be stated): mutating/deleting the PROOF: segment during the completing edit isn't a stated gap in §9 — it's a silent bypass (edit fails equality check → not a transition → skipped → allowed, proof never runs). Layer 2 PASS, non-PROVISIONAL, unchanged. | .gate-snapshots/progress-md-proof-per-slice-hook/spec/attempt-2/ |

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]

## Post-approval revision (Danny-directed, 2026-08-23)

At human review, Danny rejected §9's originally-accepted mutation/deletion bypass (a checkbox-flip
edit that also changes the description or drops the PROOF: segment was silently allowed) — required
it be denied, not accepted. Six further Frank supplementary rounds followed, all FAIL until the
seventh PASS, each finding real and progressively deeper:

1. C2 deny mechanism added (mutation → deny). PASS on the mechanism, FAIL on residual-gap accuracy.
2. Residual statement corrected, still understated the attack surface (single-call line-count-mismatch
   variant cheaper than the stated two-call dodge). FAIL.
3. Residual statement corrected again — found a THIRD variant (line reordering breaks positional/
   index-based matching entirely). FAIL. Danny: stop patching instances, redesign the mechanism.
4. Real redesign — index-based line diffing replaced with identity-based matching (description
   segment primary key, PROOF segment fallback). Closes the whole positional family (line-count
   mismatch, reordering) at once. Surfaced one new honest residual: simultaneous description+PROOF
   mutation in one edit has no surviving content-based identity key.
5. Danny's decision: close that via a new optional `SLICE-ID:` segment (stable, author-assigned,
   forward-only — never retrofitted onto existing PROGRESS.md files). Added, with fallback to
   content-matching when absent. FAIL — over-claimed closure didn't account for the token itself
   also changing in the same edit.
6. Residual qualified precisely; Danny's decision recorded: accept the token-mutation variant as
   residual (self-honesty threat model, not adversarial security; the two-call dodge is already
   accepted and easier to exploit; a deny rule would false-positive on legitimate edits). Two
   documentation-consistency FAILs followed (a stale contradictory clause left behind across two
   sub-rounds) before all four sections (§4/§6/§9/§12) said the same thing once, with one owner.

**Final PASS (2026-08-23)**, both layers, non-PROVISIONAL. Frank's verdict used the new Carried
Condition structure (per the agents/frank.md fix shipped same session) instead of loose prose —
copied verbatim into PROGRESS.md's Fix Attempts / Notes per that same rule:

1. PROVISIONAL constants (allowlist content, 25s inner / 30s outer timeouts) → forge measures
   against real proof commands before values are treated as settled. Route: forge.
2. Edit-specific PreToolUse envelope shape has never been live-verified (only Write was captured,
   for the sibling hook) → forge runs the same throwaway-hook live-capture method scoped to Edit
   before trusting old_string/new_string presence and the deny shape. Route: forge.
3. The two-call mutate-then-flip dodge (§12 item 1) — close now vs. accept — is an explicit open
   decision point for Danny, at forge kickoff, not decided here.

Also worth noting for future sessions: this revision cycle surfaced and corrected a real process
error — Frank's dispatches in rounds 1-3 used unearned adversarial/hostile-actor framing
("attacker," "dodge," "bypass") inherited from this session's higher-stakes hooks, applied to a
self-honesty mechanism where the actual actor is an agent or human under time pressure, not a
hostile party. Recalibrated from round 4 onward — review posture should match actual stakes, not
default to whatever framing was used last.

## Forge Gate
Counter: 0/3

| Attempt | Date | Verdict | Findings Summary | Snapshot |
|---|---|---|---|---|

Convergence judgment (attempt 3 only): SHRINKING | STATIC | THRASHING
Deep-diagnosis evidence:
Orchestrator independent re-derivation: AGREES | DISAGREES — [if disagrees, both readings recorded here before escalation]
