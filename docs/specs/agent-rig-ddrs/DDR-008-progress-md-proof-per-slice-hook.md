# DDR-008 — `PROGRESS.md` Proof-Per-Slice Stop Hook

**Status**: DRAFT
**Author**: wright (recording an agreed design direction, 2026-08-21/22)
**Date**: 2026-08-22
**Scope**: agent-rig first; generalizes to any repo using the `PROGRESS.md`/sprint-slice pattern.

---

## 0. Provenance

Arose from a direct question: does `WORKPLAN.md` (proposed in DDR-005 §1 move 2) duplicate
`PROGRESS.md`, which agent-rig already has as declared sprint ground truth? Resolution, agreed
2026-08-21/22: `WORKPLAN.md` is not built as a separate artifact. Its three jobs split as follows —
**objective** is carried by the work order (DDR-005 §2, issued in conversation, no file needed);
**ordered tasks** is already `PROGRESS.md`'s job; **definition-of-done, checked not narrated** is
the one piece missing, and this DDR is that piece.

Design precedent: `github.com/Glitch-Cat-Club/prompt-router-starter`'s `gate.py` (Stop hook) —
a contract/ledger of numbered requirements, each with a proof command; on a "done" claim, every
allowlisted proof actually runs, and a failing or missing proof holds the turn open naming the
specific row. Not adopted wholesale (that repo's ledger is a separate JSON contract per work order);
the adopted piece is the mechanism — proof-per-line, run not narrated — applied to `PROGRESS.md`'s
existing slice checkboxes instead of a new file.

This directly closes the gap named in the standing feedback memory
`feedback_gate_not_substitutable_by_slice_checkboxes.md`: today a `[x] COMPLETE` mark on a
`PROGRESS.md` slice is self-asserted by the agent, cross-checked against `GATE-LOG.md` only by
convention and discipline, not by anything that fails if the check is skipped.

## 1. The mechanism

Extend `PROGRESS.md`'s slice-line format to carry a proof command per slice (or per Done-When
criterion within a slice, where a slice has several). A Stop hook, sibling to
`first-turn-contract.sh`, fires when a reply claims a slice complete: reads the proof command(s)
for that slice, runs any that are allowlisted, and refuses to let the checkbox stand as `[x]` if a
proof fails or is missing — same allowlist/manual-stamp split as DDR-006 and the `gate.py`
precedent (allowlisted commands run and are trusted; anything else is stamped `manual` and never
blocks).

## 2. Relationship to other DDRs in this family

- **DDR-005**: this is DDR-005's first concrete implementation slice, not a separate initiative —
  §1's "definition-of-done, checked not narrated" move, built.
- **`first-turn-contract-enforcement`**: shares the Stop-hook wrapper pattern (bounded timeout,
  fail-open on error, track-record log) — reuse that wrapper's shape rather than redesigning it.
- **DDR-006 / DDR-010**: same family (mechanize a check that currently depends on someone
  remembering or asserting it), different target (slice completion vs. borrowed values vs. gate
  assertion coverage).

## 3. Open questions

1. **Proof-command placement in `PROGRESS.md`'s existing format.** Needs a concrete syntax decision
   — inline per slice line, or a structured block per slice — before Intake.
2. **Allowlist scope.** Reuse `first-turn-contract-enforcement`'s allowlist conventions or define
   fresh ones for this hook; likely the former for consistency.
3. **Does this replace or run alongside `GATE-LOG.md`/Frank's own gate?** This hook checks
   mechanical slice-completion claims; Frank's gate is a judgment call on the whole sprint. Not the
   same thing — needs stating explicitly in the spec so nobody reads one as replacing the other.

## 4. Next step

Intake, per this repo's standard workflow. Sequenced second in the current build order (after
DDR-006), per Danny's 2026-08-22 approval — one hook rolled out at a time, soak period before the
next, per the standing rollout policy recorded in `00-DDR-INDEX.md`.

---

## References

- `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` — the thesis this implements
- `docs/specs/first-turn-contract-enforcement/` — the Stop-hook wrapper pattern to reuse
- `github.com/Glitch-Cat-Club/prompt-router-starter` — `gate.py`/ledger design precedent
- `feedback_gate_not_substitutable_by_slice_checkboxes.md` (memory) — the gap this closes
