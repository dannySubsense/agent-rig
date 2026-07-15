# Development Cadence

Workflow phases for this project. Agents follow this cadence unless directed otherwise.

---

## Phase 1: Specification

**Command:** `/spec-start`

```
Feature Request
    │
    ├── @requirements-analyst → 01-REQUIREMENTS.md
    ├── @architect → 02-ARCHITECTURE.md
    ├── @ui-spec-writer → 03-UI-SPEC.md
    ├── @planner → 04-ROADMAP.md
    └── @spec-reviewer → 05-REVIEW.md
    │
    ▼
Human Approval Required
```

**Exit criteria:** All 5 docs approved by human.

---

## Phase 2: Implementation

**Command:** `/forge-start`

For each slice in 04-ROADMAP.md:

```
Slice Start
    │
    ├── @code-executor → Implementation
    ├── @test-writer → Tests
    ├── @test-runner → Results
    │   ├── PASS → Continue
    │   └── FAIL → Fix loop
    ├── @qc-agent → Verification
    │   ├── PASS → Continue
    │   └── FAIL → Fix loop
    └── @github-ops → Commit
    │
    ▼
Slice Complete
```

**Exit criteria:** All slices pass QC, all tests green.

---

## Phase 3: Integration

After all slices complete:

```
All Slices Complete
    │
    ├── Full test suite run
    ├── Integration verification
    ├── @doc-writer → Documentation
    └── @github-ops → PR creation
    │
    ▼
Ready for Review
```

**Exit criteria:** PR created, CI passing.

---

## Phase 4: Review

```
PR Created
    │
    ├── Human code review
    ├── Address feedback (back to Phase 2 if needed)
    └── Approval
    │
    ▼
Merge to Main
```

**Exit criteria:** PR approved and merged.

---

## Checkpoints

| Phase | Checkpoint | Human Required? |
|-------|------------|-----------------|
| Spec | After each doc | Optional |
| Spec | Final approval | **Yes** |
| Forge | After each slice | No |
| Forge | Session end | Optional |
| Integration | PR creation | **Yes** |
| Review | Merge | **Yes** |

---

## Recovery

### Stuck in Spec
- Review 05-REVIEW.md for gaps
- Address open questions
- Re-run affected agents

### Stuck in Forge
- Check test failures for root cause
- Review QC report for violations
- May need spec amendment (back to Phase 1)

### Stuck in Review
- Address feedback in Phase 2
- Re-run QC after changes
- Update PR
