# Progress: first-turn-contract-c3-claim-matching

**Status**: FORGE COMPLETE — PR #20 ready for review, DDR-004 status-line update still open (see below)

---

## Slices

- [x] Slice 1: rewrite `check_c3_violation` for claim-subject matching, per `SPEC.md` — COMPLETE
      (2026-08-27). @code-executor implemented, 2 fix rounds during forge (target-side then
      claim-side gh-command PR-number extraction bugs, both found by @test-runner/@qc-agent, not
      self-reported), @test-writer added 10 new tests (26 total, 16 pre-existing unmodified),
      @test-runner confirmed 26/26 independently twice, @qc-agent PASS on full spec-compliance
      re-review. reference/first_turn_contract_probe.py kept byte-identical throughout.
- [x] **Frank binding forge-gate** — PASS, attempt 1/3, both layers, no carried conditions
      (2026-08-27). Layer 2 no PROVISIONAL (NORTHSTAR.md Established). Orchestrator's own
      independent post-PASS review agreed (re-ran 26/26, confirmed diff scope, no fabricated
      thresholds) — no additional finding this round. Verdict in `GATE-LOG.md`'s `## Forge Gate`
      section.

## Post-forge tasks (not blocking forge, must close before this sprint is called complete)

- [ ] Update DDR-004's status line in `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` (row 004) to
      reflect the C3 claim-matching gap is closed, once this fix's PR merges. (SPEC.md §7 OQ3.)

## Deferred (tracked outside this sprint, not blocking)

- #17 — multiple Pillar sections in one turn
- #19 — word-boundary matching for file-path/quoted-query subjects (narrowed; identifier half
  resolved in this sprint)

## Closed during this sprint

- #18 — require-all-subjects vs require-any-subject (resolved: require-all adopted)
