---
name: requirements-extraction
description: |
  Step-by-step process for extracting requirements from vague input.
  Use when translating feature requests into structured requirements documents.
allowed-tools: Read, Write, Glob, Grep
---

# Requirements Extraction

Procedural guide for extracting and structuring requirements.

**CRITICAL:** Replace ALL bracketed placeholders (e.g., `[Feature Name]`, `[user type]`) with concrete values. Never write placeholder text to the output document.

## Step 1: Analyze the Input

Read the feature request carefully. Identify:
- Who is the user?
- What do they want to accomplish?
- Why do they want it?
- What constraints are mentioned?

## Step 2: Extract User Stories

Format each user story as:
```
As a [user type],
I want [goal],
so that [benefit].
```

Create one story per distinct capability.

## Step 3: Define Acceptance Criteria

For each user story, define testable criteria:
```
- [ ] Given [context], when [action], then [result]
- [ ] [Measurable condition that proves story is complete]
```

Each criterion must be:
- Binary (pass/fail)
- Independently testable
- Specific (no "should work well")

## Step 4: Identify Edge Cases

Create a table:
```markdown
| Case | Expected Behavior |
|------|-------------------|
| [unusual input] | [what should happen] |
| [boundary condition] | [what should happen] |
| [error scenario] | [what should happen] |
```

## Step 5: Define Out of Scope

Explicitly list what this feature does NOT include:
```markdown
## Out of Scope

- NOT: [feature that might be assumed but isn't included]
- NOT: [related functionality being deferred]
- Deferred: [future enhancement]
```

This prevents scope creep during implementation.

## Step 6: Document Constraints

```markdown
## Constraints

- Must: [hard requirement]
- Must not: [anti-requirement]
- Assumes: [assumption that if wrong changes everything]
```

## Step 7: Write the Document

Use this template structure:
```markdown
# Requirements: [Feature Name]

## Summary
[1-2 sentence description]

## User Stories
[from Step 2]

## Acceptance Criteria
[from Step 3]

## Edge Cases
[from Step 4]

## Out of Scope
[from Step 5]

## Constraints
[from Step 6]
```

## Output Verification

Before reporting complete, verify:
- [ ] Every user story has acceptance criteria
- [ ] Out of scope section is not empty
- [ ] No implementation details leaked in
- [ ] Constraints are concrete, not vague

## Error Handling

If input is too vague to extract requirements:
→ HALT and list specific questions that need answers

If requirements conflict:
→ HALT and document the conflict for human resolution
