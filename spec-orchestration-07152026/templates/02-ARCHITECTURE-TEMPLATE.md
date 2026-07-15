# Architecture: [Feature Name]

## Overview

[How this feature fits into the existing system. 2-3 sentences.]

---

## Components

| Component | Responsibility | Location |
|-----------|----------------|----------|
| [ComponentName] | [Single responsibility] | `src/components/[path]` |
| [StoreName] | [What state it manages] | `src/stores/[path]` |
| [ServiceName] | [What it does] | `src/services/[path]` |

---

## Data Schemas

```typescript
interface [EntityName] {
  id: string;
  field: Type;
  nested: {
    subfield: Type;
  };
  createdAt: Date;
  updatedAt: Date;
}

type [StatusType] = 'pending' | 'active' | 'complete';

interface [QueryParams] {
  filter?: Partial<[EntityName]>;
  sort?: keyof [EntityName];
  limit?: number;
}
```

---

## API Contracts

```typescript
// Component Props
interface [Component]Props {
  data: [EntityName];
  onAction: (id: string) => void;
  isLoading?: boolean;
}

// Store Interface
interface [Feature]Store {
  // State
  items: [EntityName][];
  selectedId: string | null;
  isLoading: boolean;
  error: Error | null;
  
  // Actions
  fetchItems: (params?: [QueryParams]) => Promise<void>;
  selectItem: (id: string) => void;
  updateItem: (id: string, changes: Partial<[EntityName]>) => void;
  reset: () => void;
}

// Service Functions
function fetch[Entity](params: [QueryParams]): Promise<[EntityName][]>
function update[Entity](id: string, data: Partial<[EntityName]>): Promise<[EntityName]>
```

---

## Patterns

| Pattern | Usage | Rationale |
|---------|-------|-----------|
| [Pattern name] | [Where/how used] | [Why this pattern] |
| [Pattern name] | [Where/how used] | [Why this pattern] |

### Anti-Patterns (Do Not Use)

- **[Pattern]:** [Why not for this feature]
- **[Pattern]:** [Why not for this feature]

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| [library] | ^X.Y.Z | [Why needed] |

*Only list NEW dependencies not already in package.json*

---

## Integration Points

- **[Existing Component]:** [How this feature integrates]
- **[Existing Service]:** [How this feature uses it]
- **[External API]:** [How we connect, authentication, rate limits]
