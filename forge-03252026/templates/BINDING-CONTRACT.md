# Binding Contract Template

Use this template for all agent delegations. Contracts must be concrete — no placeholders.

---

## Standard Contract Format

```
═══════════════════════════════════════════════════════════════════
TASK: [PHASE] — [AGENT TASK DESCRIPTION]
═══════════════════════════════════════════════════════════════════

ROLE
Agent: @[agent-name]
Constraints: Follow your preloaded skill exactly. HALT on ambiguity.

GOVERNANCE (LOCKED)
- INVARIANTS: docs/INVARIANTS.md
- SPEC_DIR: docs/specs/[feature-name]/

INPUTS
- [INPUT_NAME]: [concrete value, not placeholder]
- [INPUT_NAME]: [concrete value]
- FILES: [actual file paths]

OBJECTIVE
[Single sentence describing what this delegation achieves]

SCOPE
IN:
- [Specific thing to do]
- [Specific thing to do]

OUT:
- [Explicit exclusion]
- [Explicit exclusion]

SPECIFICATION
[Detailed requirements — reference spec docs by section]
- Per 02-ARCHITECTURE.md §Data Schemas: [specific guidance]
- Per 04-ROADMAP.md Slice 2: [specific files]

HALT IF
- [Condition that should stop work]
- [Condition that should stop work]
- Any ambiguity in specification

OUTPUT
- Files: [expected output files with paths]
- Report: Status + summary under 30 lines

═══════════════════════════════════════════════════════════════════
```

---

## Example: Code Implementation Contract

```
═══════════════════════════════════════════════════════════════════
TASK: FORGE — Implement Filter Store
═══════════════════════════════════════════════════════════════════

ROLE
Agent: @code-executor
Constraints: Follow code-implementation skill. HALT on ambiguity.

GOVERNANCE (LOCKED)
- INVARIANTS: docs/INVARIANTS.md
- SPEC_DIR: docs/specs/filter-panel/

INPUTS
- SLICE: 1 — Types and Store
- ARCHITECTURE: docs/specs/filter-panel/02-ARCHITECTURE.md
- UI_SPEC: docs/specs/filter-panel/03-UI-SPEC.md

OBJECTIVE
Implement FilterState type and useFilterStore with all actions.

SCOPE
IN:
- src/types/filter.ts — create
- src/stores/filterStore.ts — create

OUT:
- No components (Slice 2)
- No tests (that's @test-writer)
- No modifications to existing files

SPECIFICATION
Per 02-ARCHITECTURE.md §Data Schemas:
- FilterState interface with: status, dateRange, searchQuery
- All fields optional except status (required, default 'all')

Per 02-ARCHITECTURE.md §API Contracts:
- useFilterStore with: setStatus, setDateRange, setSearchQuery, reset

HALT IF
- Schema in spec is incomplete
- Existing store pattern conflicts with spec
- Dependency not installed (e.g., zustand)

OUTPUT
- Files: src/types/filter.ts, src/stores/filterStore.ts
- Report: Status + files created

═══════════════════════════════════════════════════════════════════
```

---

## Contract Rules

1. **Concrete values only** — Never `[placeholder]`, always actual paths and names
2. **Reference spec sections** — "Per 02-ARCHITECTURE.md §Patterns"
3. **Explicit scope** — IN and OUT sections prevent drift
4. **Clear HALT conditions** — Agent knows when to stop
5. **Verifiable output** — Advisor can check files exist

---

## Common Mistakes

❌ `FILES: src/[feature]/[component].tsx`
✅ `FILES: src/components/FilterPanel/FilterPanel.tsx`

❌ `Implement the feature`
✅ `Implement FilterState type and useFilterStore per 02-ARCHITECTURE.md §Data Schemas`

❌ `HALT IF: something goes wrong`
✅ `HALT IF: zustand not in package.json dependencies`
