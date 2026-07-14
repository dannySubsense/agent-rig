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

## Step 7: Verify Against Spec

Before reporting complete:
- [ ] All files from contract are created/modified
- [ ] Types match 02-ARCHITECTURE.md exactly
- [ ] Component structure matches 03-UI-SPEC.md
- [ ] No files outside slice scope touched
- [ ] Code compiles without errors
- [ ] Lint passes (if configured)

```bash
# Type check
npx tsc --noEmit

# Lint check (if available)
npm run lint --if-present 2>/dev/null || echo "No lint configured"
```

## Step 8: Report Completion

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
