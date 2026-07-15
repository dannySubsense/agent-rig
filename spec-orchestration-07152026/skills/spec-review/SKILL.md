---
name: spec-review
description: |
  Step-by-step process for reviewing spec documents for completeness.
  Use after all specs are drafted, before human approval.
allowed-tools: Read, Write, Glob, Grep
---

# Spec Review

Procedural guide for reviewing all spec documents for completeness and consistency.

## Step 1: Load All Documents

```bash
cat docs/specs/{feature}/01-REQUIREMENTS.md
cat docs/specs/{feature}/02-ARCHITECTURE.md
cat docs/specs/{feature}/03-UI-SPEC.md
cat docs/specs/{feature}/04-ROADMAP.md
```

## Step 2: Check Requirements Completeness

Verify:
- [ ] Summary is present and clear
- [ ] User stories follow "As a... I want... so that..." format
- [ ] Every user story has acceptance criteria
- [ ] Edge cases table is populated
- [ ] Out of scope section is not empty
- [ ] Constraints are concrete

Document gaps:
```markdown
### Requirements Gaps

| Gap | Impact |
|-----|--------|
| [what's missing] | [why it matters] |
```

## Step 3: Check Architecture Completeness

Verify:
- [ ] Every requirement has architecture coverage
- [ ] Schemas are valid TypeScript (not pseudocode)
- [ ] API contracts are complete
- [ ] Patterns are justified
- [ ] Integration points documented

Cross-reference:
```markdown
### Requirements → Architecture Coverage

| Requirement | Architecture Coverage | Status |
|-------------|----------------------|--------|
| [user story] | [component/schema] | ✅/⚠️/❌ |
```

## Step 4: Check UI Spec Completeness

Verify:
- [ ] Every user story has a flow
- [ ] Every screen has a layout
- [ ] Interactions cover all states (loading, error, success)
- [ ] Component hierarchy maps to architecture

Cross-reference:
```markdown
### Requirements → UI Coverage

| User Story | Screen/Flow | Status |
|------------|-------------|--------|
| [story] | [screen + flow] | ✅/⚠️/❌ |
```

## Step 5: Check Roadmap Completeness

Verify:
- [ ] Every architecture component is in a slice
- [ ] Every UI component is in a slice
- [ ] No circular dependencies
- [ ] Each slice has "done" criteria
- [ ] File paths are concrete

Cross-reference:
```markdown
### Architecture → Roadmap Coverage

| Component | Slice | Status |
|-----------|-------|--------|
| [component] | Slice N | ✅/⚠️/❌ |
```

## Step 6: Identify Risks

```markdown
## Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [risk] | H/M/L | H/M/L | [how to address] |
```

## Step 7: Document Assumptions

```markdown
## Assumptions

| Assumption | Impact if Wrong |
|------------|-----------------|
| [assumption] | [consequence] |
```

## Step 8: List Open Questions

```markdown
## Open Questions

| Question | Status | Resolution |
|----------|--------|------------|
| [question] | Open | [needs human input] |
```

## Step 9: Prepare Approval Checklist

```markdown
## Approval Checklist

### Requirements (01)
- [ ] Reviewed by human
- [ ] Acceptance criteria are testable
- [ ] Out of scope is acceptable

### Architecture (02)
- [ ] Reviewed by human
- [ ] Patterns are appropriate
- [ ] Schemas are correct

### UI Spec (03)
- [ ] Reviewed by human
- [ ] Flows are complete
- [ ] Layouts are appropriate

### Roadmap (04)
- [ ] Reviewed by human
- [ ] Sequence is correct
- [ ] Slices are appropriately sized

### Overall
- [ ] All open questions resolved
- [ ] All risks have mitigations
- [ ] Ready for implementation
```

## Step 10: Write the Document

Assemble into `05-REVIEW.md`.

## Output Verification

Before reporting complete, verify:
- [ ] All cross-reference tables completed
- [ ] All gaps documented
- [ ] All risks have mitigations
- [ ] Approval checklist is complete

## Error Handling

If critical gap found:
→ Document in review but don't HALT (human decides)

If documents are fundamentally inconsistent:
→ HALT and explain the conflict
