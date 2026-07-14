---
name: test-writing
description: |
  Step-by-step process for writing tests per specification.
  Use when creating tests for implemented features.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Test Writing

Procedural guide for writing tests according to specifications.

## Step 1: Load the Contract

Read and extract from the contract:
- SPEC_DIR: Path to spec documents
- SLICE: Which slice was implemented
- IMPLEMENTATION_FILES: Files to test
- TEST_OUTPUT: Where to write tests

## Step 2: Load Requirements

```bash
# Read acceptance criteria
cat {SPEC_DIR}/01-REQUIREMENTS.md
```

Extract acceptance criteria for this slice:
- [ ] Criterion 1: Given X, when Y, then Z
- [ ] Criterion 2: ...

Each criterion becomes a test.

## Step 3: Check Existing Test Patterns

```bash
# Find existing test files
find src -name "*.test.ts" -o -name "*.test.tsx" | head -10

# Read a similar test file
cat src/components/[similar]/*.test.tsx | head -50
```

Match:
- Import patterns
- Test structure (describe/it vs test)
- Mocking patterns
- Assertion library

## Step 4: Read Implementation

```bash
# Read the files being tested
cat {IMPLEMENTATION_FILES}
```

Understand:
- Exported functions/components
- Props/parameters
- Expected behavior

## Step 5: Write Unit Tests

For each acceptance criterion:

```typescript
// src/components/{Feature}/{Feature}.test.tsx

import { render, screen } from '@testing-library/react';
import { FeatureComponent } from './FeatureComponent';

describe('FeatureComponent', () => {
  // Test for Criterion 1
  it('should [criterion description]', () => {
    // Arrange
    const props = { /* test data */ };
    
    // Act
    render(<FeatureComponent {...props} />);
    
    // Assert
    expect(screen.getByText('expected')).toBeInTheDocument();
  });

  // Test for Criterion 2
  it('should [criterion description]', () => {
    // ...
  });
});
```

## Step 6: Write Store Tests

If testing state management:

```typescript
// src/stores/{feature}Store.test.ts

import { useFeatureStore } from './featureStore';

describe('featureStore', () => {
  beforeEach(() => {
    // Reset store between tests
    useFeatureStore.setState({ /* initial state */ });
  });

  it('should [action] when [trigger]', () => {
    const { actionName } = useFeatureStore.getState();
    actionName(/* params */);
    expect(useFeatureStore.getState().field).toBe(expected);
  });
});
```

## Step 7: Map Tests to Criteria

Create explicit mapping:

```typescript
/**
 * Acceptance Criteria Coverage:
 * - [x] AC1: "User can filter by status" → test line 15
 * - [x] AC2: "Filter persists on refresh" → test line 28
 * - [ ] AC3: "..." → not in this slice
 */
```

## Step 8: Verify Tests

Before reporting:
```bash
# Check tests compile
npx tsc --noEmit src/**/*.test.ts src/**/*.test.tsx

# Optionally run to verify they execute (but don't fix failures)
npm test -- --testPathPattern="{test file}" --passWithNoTests
```

## Step 9: Report Completion

```
✅ TESTS WRITTEN

Test files created:
- src/components/Feature/Feature.test.tsx — 4 tests

Acceptance criteria covered:
- [x] AC1: User can filter → "should filter items by status"
- [x] AC2: Filter persists → "should restore filter on mount"

Ready for: @test-runner

Status: COMPLETE
```

## Error Handling

If acceptance criteria are vague:
→ HALT, quote the criterion, explain why it's untestable

If implementation doesn't match spec:
→ HALT, document the mismatch

If testing requires implementation changes:
→ HALT, explain what would need to change
