---
name: test-execution
description: |
  Step-by-step process for running tests and reporting results.
  Use when executing test suites after tests are written.
allowed-tools: Read, Bash, Glob
---

# Test Execution

Procedural guide for running tests and reporting results.

## Step 1: Load the Contract

Read and extract from the contract:
- TEST_FILES: Which tests to run
- TEST_COMMAND: Specific command (or use default)
- COVERAGE: Whether to report coverage

## Step 2: Verify Test Environment

```bash
# Check test framework is installed
npm list jest vitest 2>/dev/null || echo "Test framework check"

# Check test files exist
ls -la {TEST_FILES}
```

If framework missing → HALT

## Step 3: Run Tests

Execute with appropriate command:

```bash
# For Jest
npm test -- --testPathPattern="{pattern}" --verbose --coverage

# For Vitest
npx vitest run {pattern} --reporter=verbose

# For specific file
npm test -- {TEST_FILES}
```

Capture:
- Exit code
- stdout (pass/fail details)
- stderr (errors)
- Coverage report (if enabled)

## Step 4: Parse Results

Extract from output:
- Total tests
- Passed count
- Failed count
- Skipped count
- Coverage percentage (if available)

For each failure, extract:
- Test name
- Error message
- Stack trace (first 5 lines)

## Step 5: Report Results

### If All Pass:

```
✅ TEST RUN COMPLETE

Command: npm test -- --testPathPattern="Feature" --verbose

Results:
- Total: 8
- Passed: 8
- Failed: 0
- Skipped: 0

Coverage: 87%

Status: PASS

Ready for: @qc-agent
```

### If Any Fail:

```
❌ TEST RUN COMPLETE

Command: npm test -- --testPathPattern="Feature" --verbose

Results:
- Total: 8
- Passed: 6
- Failed: 2
- Skipped: 0

Failed tests:
1. "should filter items by status"
   Error: Expected 3 but received 0
   at Feature.test.tsx:24

2. "should persist filter"
   Error: localStorage is not defined
   at Feature.test.tsx:45

Status: FAIL

Returning to: Forge Advisor for diagnosis
```

## Step 6: Provide Re-run Command

Always include:
```bash
# To re-run these tests:
npm test -- --testPathPattern="{pattern}" --verbose
```

## Common Test Commands

| Framework | Run All | Run Pattern | With Coverage |
|-----------|---------|-------------|---------------|
| Jest | `npm test` | `npm test -- --testPathPattern="X"` | `--coverage` |
| Vitest | `npx vitest run` | `npx vitest run X` | `--coverage` |
| Playwright | `npx playwright test` | `npx playwright test X` | N/A |

## Error Handling

If test command fails to execute (not test failure):
→ HALT, report error, likely missing dependency

If test timeout:
→ Report as failure with "TIMEOUT" error

If no tests found:
→ HALT, report "No tests matched pattern"
