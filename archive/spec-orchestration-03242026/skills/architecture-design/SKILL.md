---
name: architecture-design
description: |
  Step-by-step process for designing technical architecture.
  Use when creating architecture documents from requirements.
allowed-tools: Read, Write, Glob, Grep, Bash
---

# Architecture Design

Procedural guide for designing technical architecture that satisfies requirements.

## Step 1: Load Context

Read the requirements document:
```bash
cat docs/specs/{feature}/01-REQUIREMENTS.md
```

Extract:
- User stories (what capabilities are needed)
- Constraints (what limits the design)
- Out of scope (what NOT to design)

## Step 2: Survey Existing Codebase

Check for existing patterns:
```bash
# Find existing components
find src -name "*.tsx" -o -name "*.ts" | head -20

# Check for existing stores/state
grep -r "create.*Store\|useState\|useContext" src/ --include="*.ts" --include="*.tsx" | head -10

# Check for existing API patterns
grep -r "fetch\|axios\|api" src/ --include="*.ts" | head -10
```

Note patterns to follow for consistency.

## Step 3: Define Components

Create a components table:
```markdown
## Components

| Component | Responsibility | Location |
|-----------|----------------|----------|
| [ComponentName] | [single responsibility] | `src/components/[path]` |
| [StoreName] | [what state it manages] | `src/stores/[path]` |
| [ServiceName] | [what it does] | `src/services/[path]` |
```

Each component has ONE responsibility.

## Step 4: Define Data Schemas

Write exact TypeScript interfaces:
```markdown
## Data Schemas

\`\`\`typescript
interface FeatureName {
  id: string;
  field: Type;
  nested: {
    subfield: Type;
  };
}

type Status = 'pending' | 'active' | 'complete';
\`\`\`
```

Be precise — these become the contract.

## Step 5: Define API Contracts

Write exact function signatures:
```markdown
## API Contracts

\`\`\`typescript
// Component props
interface ComponentNameProps {
  data: FeatureName;
  onAction: (id: string) => void;
}

// Store actions
interface FeatureStore {
  items: FeatureName[];
  fetchItems: () => Promise<void>;
  updateItem: (id: string, changes: Partial<FeatureName>) => void;
}

// Service functions
function fetchFeatureData(params: QueryParams): Promise<FeatureName[]>
\`\`\`
```

## Step 6: Choose Patterns

Document patterns with rationale:
```markdown
## Patterns

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| [pattern name] | [where used] | [why this pattern] |

## Anti-Patterns (Do Not Use)

- [pattern]: [why not for this feature]
```

## Step 7: Specify Dependencies

```markdown
## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| [library] | ^X.Y.Z | [why needed] |
```

Only add dependencies that don't already exist in package.json.

## Step 8: Document Integration Points

```markdown
## Integration Points

- [Existing Component]: [how this feature integrates]
- [Existing Service]: [how this feature uses it]
- [External API]: [how we connect]
```

## Step 9: Write the Document

Assemble all sections into `02-ARCHITECTURE.md`.

## Output Verification

Before reporting complete, verify:
- [ ] Every requirement has architecture coverage
- [ ] Schemas are complete TypeScript (not pseudocode)
- [ ] No implementation details (that's for code)
- [ ] Patterns are justified
- [ ] Integration points are identified

## Error Handling

If a requirement cannot be satisfied:
→ HALT and explain the technical blocker

If a major design decision is needed:
→ HALT and present options with tradeoffs
