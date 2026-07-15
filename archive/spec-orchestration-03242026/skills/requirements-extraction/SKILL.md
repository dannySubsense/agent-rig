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

## Step 1: Analyze the Intake Notes

Read the feature request / intake notes. Identify what you know and what's missing:
- Who is the user? (Known / Unknown / Assumed)
- What do they want to accomplish? (Clear / Vague / Missing)
- Why do they want it? (Stated / Implied / Unknown)
- What constraints exist? (Listed / Unknown)
- What's out of scope? (Stated / Assumed / Unknown)

## Step 2: Conduct Clarifying Interview

**MANDATORY:** Before writing user stories, interview the human to fill gaps.

Ask questions to clarify:
- Ambiguous goals ("When you say 'filter', do you mean by status, date, or both?")
- Missing user context ("Who will use this — admins, end users, or both?")
- Unstated constraints ("Any performance requirements? Mobile support?")
- Scope boundaries ("Should this include export functionality, or is that separate?")
- Success criteria ("How will you know this feature is working correctly?")

**Format:** Ask 3-5 focused questions. Wait for answers before proceeding.

**Skip interview ONLY if:** Intake notes are comprehensive AND explicitly marked as "approved" or "final."

## Step 3: Extract User Stories

Format each user story as:
```
As a [user type],
I want [goal],
so that [benefit].
```

Create one story per distinct capability.

## Step 4: Define Acceptance Criteria

For each user story, define testable criteria:
```
- [ ] Given [context], when [action], then [result]
- [ ] [Measurable condition that proves story is complete]
```

Each criterion must be:
- Binary (pass/fail)
- Independently testable
- Specific (no "should work well")

## Step 5: Identify Edge Cases

Create a table:
```markdown
| Case | Expected Behavior |
|------|-------------------|
| [unusual input] | [what should happen] |
| [boundary condition] | [what should happen] |
| [error scenario] | [what should happen] |
```

## Step 6: Define Out of Scope

Explicitly list what this feature does NOT include:
```markdown
## Out of Scope

- NOT: [feature that might be assumed but isn't included]
- NOT: [related functionality being deferred]
- Deferred: [future enhancement]
```

This prevents scope creep during implementation.

## Step 7: Document Constraints

```markdown
## Constraints

- Must: [hard requirement]
- Must not: [anti-requirement]
- Assumes: [assumption that if wrong changes everything]
```

## Step 8: Write the Document

Use this template structure:
```markdown
# Requirements: [Feature Name]

## Summary
[1-2 sentence description]

## User Stories
[from Step 3]

## Acceptance Criteria
[from Step 4]

## Edge Cases
[from Step 5]

## Out of Scope
[from Step 6]

## Constraints
[from Step 7]
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
