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

## Step 8: Automated QC Gates

Before reporting complete, verify tests compile and run.

### Auto-detect project type and run gates:

```bash
if [ -f "package.json" ]; then
  echo "Detected: TypeScript/JavaScript project"
  
  # Type check test files
  echo "Type checking test files..."
  npx tsc --noEmit
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Test files have type errors"; exit 1; fi
  
  # Verify tests run (quick smoke test)
  echo "Running test smoke check..."
  npm test -- --testPathPattern="{TEST_FILES}" --passWithNoTests --maxWorkers=1 2>&1 | head -50
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Tests fail to run"; exit 1; fi
  
  echo "✅ All TypeScript/JavaScript test gates passed"

elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  echo "Detected: Python project"
  
  # Syntax check test files
  echo "Checking test file syntax..."
  python -m py_compile tests/*.py 2>/dev/null || python -m py_compile test_*.py 2>/dev/null
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Test files have syntax errors"; exit 1; fi
  
  # Verify tests run (quick smoke test)
  echo "Running test smoke check..."
  pytest {TEST_FILES} --collect-only 2>&1 | head -30
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Tests fail to collect"; exit 1; fi
  
  echo "✅ All Python test gates passed"

else
  echo "⚠️ Unknown project type — skipping automated gates"
fi
```

### Gate Results:

| Gate | Status |
|------|--------|
| Test files compile | ✅ PASS / ❌ FAIL |
| Tests collect/run | ✅ PASS / ❌ FAIL |

**If ANY gate fails:** Fix the issues and re-run. Do NOT proceed until all gates pass.

## Step 9: Verify Coverage Mapping

Confirm all acceptance criteria have tests:

| Acceptance Criterion | Test | Status |
|---------------------|------|--------|
| AC1: [criterion] | [test name] | ✅ |
| AC2: [criterion] | [test name] | ✅ |

If any criterion is untested → Add test or document why (out of slice scope).

## Step 10: Report Completion

```
✅ TESTS WRITTEN

Automated QC Gates:
- Test compilation: ✅ PASS
- Test smoke check: ✅ PASS

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
