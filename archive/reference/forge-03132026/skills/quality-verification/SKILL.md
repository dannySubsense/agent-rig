---
name: quality-verification
description: |
  Step-by-step process for verifying implementation against specs.
  Use for quality checks after tests pass.
allowed-tools: Read, Glob, Grep
---

# Quality Verification

Procedural guide for verifying implementations against specifications and invariants.

## Step 1: Load the Contract

Read and extract from the contract:
- SPEC_DIR: Path to spec documents
- SLICE: Which slice to verify
- IMPLEMENTATION_FILES: Files to check
- TEST_FILES: Test files to review

## Step 2: Load All Specs

```bash
cat {SPEC_DIR}/01-REQUIREMENTS.md
cat {SPEC_DIR}/02-ARCHITECTURE.md
cat {SPEC_DIR}/03-UI-SPEC.md
cat {SPEC_DIR}/04-ROADMAP.md
cat docs/INVARIANTS.md
```

## Step 3: Verify Requirements Coverage

For each acceptance criterion in 01-REQUIREMENTS.md:

| Criterion | Implementation | Test | Status |
|-----------|----------------|------|--------|
| [AC text] | [file:line or "missing"] | [test name] | ✅/❌ |

Check:
- Is the criterion implemented?
- Is there a test for it?
- Does the test actually verify it?

## Step 4: Verify Architecture Compliance

### Schema Check

Compare implementation types to 02-ARCHITECTURE.md:

```bash
# Extract interfaces from implementation
grep -A 20 "interface\|type " {IMPLEMENTATION_FILES}
```

- [ ] Field names match exactly
- [ ] Field types match exactly
- [ ] No extra fields added
- [ ] No fields missing

### Pattern Check

For each pattern in 02-ARCHITECTURE.md §Patterns:
- [ ] Pattern is used where specified
- [ ] No anti-patterns used

### File Location Check

- [ ] Files are in locations specified in architecture
- [ ] No files created outside spec

## Step 5: Verify UI Spec Compliance

Compare to 03-UI-SPEC.md:

### Component Hierarchy
- [ ] Components match specified hierarchy
- [ ] Parent-child relationships correct

### Interactions
- [ ] All specified interactions implemented
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Success states handled

### State Visibility
- [ ] Data appears in specified locations
- [ ] State updates from specified actions

## Step 6: Verify Roadmap Compliance

Compare to 04-ROADMAP.md Slice N:

- [ ] Only files in slice are touched
- [ ] All files in slice are touched
- [ ] Done criteria are met
- [ ] No scope creep

```bash
# Check which files were modified (if git available)
git diff --name-only HEAD~1 2>/dev/null || echo "Git not available"
```

## Step 7: Verify Invariants

For each rule in INVARIANTS.md:
- [ ] Invariant is not violated
- [ ] No exceptions introduced

Common invariants to check:
- No hardcoded secrets
- Error handling present
- No console.log in production code
- Imports are sorted (if required)
- No TODO/FIXME (if required)

```bash
# Check for common violations
grep -r "console.log\|TODO\|FIXME\|HACK" {IMPLEMENTATION_FILES}
```

## Step 8: Generate Report

```
═══════════════════════════════════════════════════════════════════
QC VERIFICATION REPORT
═══════════════════════════════════════════════════════════════════

Slice: [N] - [Slice Name]
Files Verified: [list]

REQUIREMENTS CHECK (01-REQUIREMENTS.md)
✅ AC1: User can filter by status
   Evidence: FilterPanel.tsx implements status filter
✅ AC2: Filter persists across sessions
   Evidence: useFilterStore persists to localStorage
❌ AC3: Filter shows count of matching items
   Violation: Count not displayed in UI

ARCHITECTURE CHECK (02-ARCHITECTURE.md)
✅ FilterState interface matches schema exactly
✅ Zustand pattern used as specified
❌ Anti-pattern: Direct DOM manipulation in line 45

UI SPEC CHECK (03-UI-SPEC.md)
✅ Component hierarchy matches
✅ Loading state implemented
⚠️ Error state shows generic message, spec says specific

ROADMAP CHECK (04-ROADMAP.md)
✅ Only slice files modified
✅ Done criteria met

INVARIANTS CHECK
✅ No hardcoded secrets
❌ console.log found in filterStore.ts:23

═══════════════════════════════════════════════════════════════════
VERDICT: FAIL

Issues requiring fix:
1. AC3 not implemented (count display)
2. Direct DOM manipulation violates architecture
3. console.log must be removed

═══════════════════════════════════════════════════════════════════
```

## Verdict Rules

**PASS** only if:
- ALL acceptance criteria verified
- ALL architecture patterns followed
- ALL invariants respected
- NO scope creep

**FAIL** if ANY violation found.

No partial credit. No "mostly good."
