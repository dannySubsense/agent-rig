---
name: code-implementation
description: |
  Step-by-step process for implementing code per specification.
  Use when building features according to architecture and roadmap.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Code Implementation

Procedural guide for implementing code according to specifications.

**CRITICAL:** Replace ALL bracketed placeholders (e.g., `[feature]`, `[EntityName]`) with concrete values. Never write placeholder text to disk.

## Step 1: Load the Contract

Read and extract from the contract:
- SPEC_DIR: Path to spec documents
- SLICE: Which slice from 04-ROADMAP.md
- FILES: Exact files to create/modify
- OUTPUT confirmation format

## Step 2: Load Spec Documents

```bash
# Read architecture for patterns and schemas
cat {SPEC_DIR}/02-ARCHITECTURE.md

# Read UI spec for component structure
cat {SPEC_DIR}/03-UI-SPEC.md

# Read roadmap for slice details
cat {SPEC_DIR}/04-ROADMAP.md
```

Extract:
- Schemas (exact TypeScript interfaces)
- Patterns (what to use)
- Anti-patterns (what NOT to use)
- Slice files and done criteria

## Step 3: Survey Existing Code

```bash
# Check for existing patterns
find src -name "*.ts" -o -name "*.tsx" | head -20

# Find similar components
grep -r "similar pattern" src/ --include="*.tsx" | head -5

# Check existing imports
head -30 src/components/[similar]/index.tsx
```

Match existing conventions.

## Step 4: Implement Types First

If the slice includes types:
```typescript
// src/types/{feature}.ts

// Copy EXACTLY from 02-ARCHITECTURE.md §Data Schemas
interface EntityName {
  id: string;
  // ... exact fields from spec
}
```

Verify types compile:
```bash
npx tsc --noEmit src/types/{feature}.ts
```

## Step 5: Implement Store/State

If the slice includes state management:
```typescript
// src/stores/{feature}Store.ts

// Follow pattern from 02-ARCHITECTURE.md §API Contracts
import { create } from 'zustand';

interface FeatureStore {
  // ... exact interface from spec
}

export const useFeatureStore = create<FeatureStore>((set, get) => ({
  // ... implementation matching interface
}));
```

## Step 6: Implement Components

If the slice includes components:
```typescript
// src/components/{Feature}/index.tsx

// Props interface from 02-ARCHITECTURE.md
// Structure from 03-UI-SPEC.md §Component Hierarchy

export function FeatureComponent({ props }: FeatureProps) {
  // Implementation
}
```

## Step 7: Automated QC Gates

Before reporting complete, run automated quality checks.

### Auto-detect project type and run gates:

```bash
# Detect project type
if [ -f "package.json" ]; then
  echo "Detected: TypeScript/JavaScript project"
  
  # Type check
  echo "Running type check..."
  npx tsc --noEmit
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Type errors"; exit 1; fi
  
  # Lint check
  echo "Running lint..."
  npm run lint --if-present
  if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Lint errors"; exit 1; fi
  
  # Format check (if prettier configured)
  if [ -f ".prettierrc" ] || grep -q "prettier" package.json; then
    echo "Running format check..."
    npx prettier --check "src/**/*.{ts,tsx,js,jsx}" 2>/dev/null || true
  fi
  
  echo "✅ All TypeScript/JavaScript gates passed"

elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "requirements.txt" ]; then
  echo "Detected: Python project"
  
  # Lint check (flake8)
  if command -v flake8 &> /dev/null; then
    echo "Running flake8..."
    flake8 src/ --max-line-length=100 --exclude=__pycache__
    if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Lint errors"; exit 1; fi
  fi
  
  # Format check (black)
  if command -v black &> /dev/null; then
    echo "Running black check..."
    black --check src/
    if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Format errors"; exit 1; fi
  fi
  
  # Type check (mypy)
  if command -v mypy &> /dev/null; then
    echo "Running mypy..."
    mypy src/ --ignore-missing-imports
    if [ $? -ne 0 ]; then echo "❌ GATE FAIL: Type errors"; exit 1; fi
  fi
  
  # Import check
  echo "Running import check..."
  python -c "import sys; sys.path.insert(0, '.'); import src" 2>/dev/null || echo "⚠️ Import check skipped"
  
  echo "✅ All Python gates passed"

else
  echo "⚠️ Unknown project type — skipping automated gates"
fi
```

### Gate Results:

| Gate | Status |
|------|--------|
| Type check | ✅ PASS / ❌ FAIL |
| Lint | ✅ PASS / ❌ FAIL |
| Format | ✅ PASS / ❌ FAIL / ⚠️ SKIP |

**If ANY gate fails:** Fix the issues and re-run. Do NOT proceed until all gates pass.

## Step 8: Verify Against Spec

After gates pass, verify against spec:
- [ ] All files from contract are created/modified
- [ ] Types match 02-ARCHITECTURE.md exactly
- [ ] Component structure matches 03-UI-SPEC.md
- [ ] No files outside slice scope touched

## Step 9: Report Completion

```
✅ IMPLEMENTATION COMPLETE

Files created:
- src/types/feature.ts — Entity types
- src/stores/featureStore.ts — State management

Files modified:
- [none or list]

Ready for: @test-writer

Status: COMPLETE
```

## Error Handling

If spec is ambiguous:
→ HALT, quote the ambiguous section, request clarification

If existing code conflicts with spec:
→ HALT, document the conflict, request resolution

If dependency is missing:
→ HALT, list what's needed, request installation approval
