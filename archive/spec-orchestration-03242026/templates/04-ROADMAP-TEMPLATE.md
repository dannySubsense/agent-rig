# Implementation Roadmap: [Feature Name]

## Overview

[Brief description of implementation approach. 2-3 sentences.]

---

## Slice Overview

| Slice | Goal | Depends On | Files |
|-------|------|------------|-------|
| 1 | [Deliverable] | — | [file count] |
| 2 | [Deliverable] | Slice 1 | [file count] |
| 3 | [Deliverable] | Slice 1, 2 | [file count] |

---

## Slice Details

### Slice 1: [Name]

**Goal:** [Single deliverable in one sentence]

**Depends On:** —

**Files:**
- `src/types/[feature].ts` — create
- `src/stores/[feature]Store.ts` — create

**Implementation Notes:**
- [Specific guidance from architecture]
- [Pattern to follow]

**Tests:**
- [ ] Unit test for [type/function]
- [ ] Store actions work correctly

**Done When:**
- [ ] Types compile without errors
- [ ] Store initializes correctly
- [ ] All tests pass

---

### Slice 2: [Name]

**Goal:** [Single deliverable in one sentence]

**Depends On:** Slice 1

**Files:**
- `src/components/[Feature]/index.tsx` — create
- `src/components/[Feature]/[Feature].tsx` — create
- `src/components/[Feature]/[Feature].test.tsx` — create

**Implementation Notes:**
- [Specific guidance]
- [Pattern to follow]

**Tests:**
- [ ] Component renders without errors
- [ ] [Specific behavior test]

**Done When:**
- [ ] Component renders with mock data
- [ ] Props interface matches architecture
- [ ] All tests pass

---

### Slice 3: [Name]

**Goal:** [Single deliverable in one sentence]

**Depends On:** Slice 1, 2

**Files:**
- `src/services/[feature]Service.ts` — create
- `src/components/[Feature]/[Feature].tsx` — modify

**Implementation Notes:**
- [Specific guidance]

**Tests:**
- [ ] Service functions return expected data
- [ ] Component integrates with real service

**Done When:**
- [ ] End-to-end flow works
- [ ] Error states handled
- [ ] All tests pass

---

## Sequence Rules

1. Complete each slice fully before starting next
2. No partial slice work
3. If blocked → HALT, do not skip ahead
4. Each slice must pass tests before proceeding
5. No new slices without human approval

---

## Deferred (Not This Roadmap)

- [Enhancement for later]
- [Nice-to-have not in requirements]
- [Optimization to consider post-MVP]
