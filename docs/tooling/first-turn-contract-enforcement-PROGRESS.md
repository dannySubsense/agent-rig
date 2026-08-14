# Progress: first-turn-contract-enforcement

## Status: IN_PROGRESS

Spec: `docs/tooling/first-turn-contract-enforcement.md` (LOCKED, Danny 2026-08-14)
Gate log: `docs/tooling/first-turn-contract-enforcement-GATE-LOG.md` (Spec Gate PASS attempt 2/3)
Mode: forge-lite. No `04-ROADMAP.md` — slices derived from the spec's §11 acceptance criteria.

## Slices

- [ ] **Slice 1: Probe core** — `scripts/first_turn_contract_probe.py`. Stdin parsing; §5.1 gating
      (queue-injection detection via the `HEADER` marker, first-turn determination,
      `stop_hook_active` unconditional allow); C1, C2, C3 predicates; track-record entry write (§6).
      Covers AC 1, 2, 3, 6, 8 (schema half).
- [ ] **Slice 2: Wrapper, wiring, drift guard** — `.claude/hooks/first-turn-contract.sh`;
      fail-open on every probe failure mode; output-shape validation; `reference/` mirror + drift
      test; `.gitignore` entry; `.claude/settings.json` `Stop` wiring **last**, per AC 9 (the §7
      evidence standard must exist before the hook is flipped live — it does).
      Covers AC 5, 7, 8 (ignored-not-dirty half), 9.
- [ ] **Slice 3: Live demonstration** — the part no harness can do. AC 4 requires a compliant turn
      to pass *on a real live session, not the fixture alone*, and AC 10 requires every criterion
      be demonstrated by an executed check. This is its own slice because the sibling sprint's
      entire lesson is that running the script is not the same as the harness running it.
      Covers AC 4 (live half), 10.

## Current

Slice: 1 — awaiting branch consent before dispatch
Step: Session Start (governance loaded, git flow determined, slices derived)
Last updated: 2026-08-14

## Fix Attempts

| Test/File | Attempts | Last Error |
|-----------|----------|------------|
| — | — | — |

## Notes

- **Branch decision:** this work is being cut from `feature/session-queue-injection`, not from
  `main`. The spec's §5.1 queue-injection predicate keys on the literal `HEADER` string in
  `scripts/session_queue_probe.py`, and both that probe and the rewritten `FOOTER` this hook
  enforces exist **only on that unmerged branch**. A branch cut from `main` would carry a spec
  referencing code that isn't there.
- **Deferred, tracked here so it is not lost:** `session-queue-hardening`'s FOOTER repair is still
  open at N=0 live fires. Slice 3's live session is the natural point to close it — one real
  SessionStart fire with the first-turn output checked against the contract satisfies both that
  sprint's standing instruction and this sprint's AC 4.
