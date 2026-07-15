---
name: implementation-planning
description: |
  Step-by-step process for breaking specs into implementation slices.
  Use when creating ordered, testable implementation roadmaps.
allowed-tools: Read, Write, Glob, Grep
---

# Implementation Planning

Procedural guide for breaking architecture and UI specs into ordered implementation slices.

## Step 1: Load All Specs

Read all prior spec documents:
```bash
cat docs/specs/{feature}/01-REQUIREMENTS.md
cat docs/specs/{feature}/02-ARCHITECTURE.md
cat docs/specs/{feature}/03-UI-SPEC.md
```

Extract:
- Components from architecture
- Screens from UI spec
- Data schemas
- Dependencies between pieces

## Step 2: Identify Atomic Units

List every piece that could be implemented:
- Each schema/type
- Each store/state
- Each component
- Each service function
- Each screen

## Step 3: Map Dependencies

Create a dependency graph:
```markdown
## Dependency Map

| Unit | Depends On |
|------|------------|
| DataList component | DataItem component, dataStore |
| dataStore | DataSchema types |
| DataItem component | DataSchema types |
| FilterPanel | filterStore |
```

## Step 4: Define Slices

Group units into slices where:
- Each slice is independently testable
- Each slice has clear "done" criteria
- Slices don't have circular dependencies

```markdown
## Slice Overview

| Slice | Goal | Depends On | Files |
|-------|------|------------|-------|
| 1 | [deliverable] | — | [files] |
| 2 | [deliverable] | Slice 1 | [files] |
| 3 | [deliverable] | Slice 1, 2 | [files] |
```

## Step 5: Detail Each Slice

For each slice:
```markdown
### Slice N: [Name]

**Goal:** [Single deliverable in one sentence]

**Depends On:** [Previous slices or "—" if none]

**Files:**
- `src/types/feature.ts` — create
- `src/stores/featureStore.ts` — create
- `src/components/Feature/index.tsx` — create

**Implementation Notes:**
- [Specific guidance from architecture]
- [Pattern to follow]

**Tests:**
- [ ] Unit test for [function/component]
- [ ] [Specific behavior to test]

**Done When:**
- [ ] [Specific criterion]
- [ ] [Specific criterion]
- [ ] All tests pass
```

## Step 6: Define Sequence Rules

```markdown
## Sequence Rules

1. Complete each slice fully before starting next
2. No partial slice work
3. If blocked → HALT, do not skip ahead
4. Each slice must pass tests before proceeding
5. No new slices without human approval
```

## Step 7: Document Deferred Work

```markdown
## Deferred (Not This Roadmap)

- [Enhancement for later]
- [Nice-to-have not in requirements]
- [Optimization to consider post-MVP]
```

## Step 8: Write the Document

Assemble into `04-ROADMAP.md`.

## Output Verification

Before reporting complete, verify:
- [ ] Every architecture component is in a slice
- [ ] Every UI component is in a slice
- [ ] No circular dependencies between slices
- [ ] Each slice has testable "done" criteria
- [ ] File paths are concrete (not placeholders)

## Error Handling

If architecture is incomplete:
→ HALT and list missing components

If circular dependency detected:
→ HALT and document the cycle for restructuring

If a slice can't be made independently testable:
→ HALT and explain why splitting isn't possible
