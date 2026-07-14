---
name: ui-specification
description: |
  Step-by-step process for specifying user interfaces.
  Use when defining screens, user flows, and interaction patterns.
allowed-tools: Read, Write, Glob, Grep
---

# UI Specification

Procedural guide for specifying user interfaces that bridge requirements and architecture.

## Step 1: Load Context

Read prior spec documents:
```bash
cat docs/specs/{feature}/01-REQUIREMENTS.md
cat docs/specs/{feature}/02-ARCHITECTURE.md
```

Extract:
- User stories (what users need to do)
- Components (what's available to build with)
- Data schemas (what data is displayed)

## Step 2: Identify Screens

List every distinct screen/view:
```markdown
## Screens

| Screen | Purpose | Entry Point |
|--------|---------|-------------|
| [ScreenName] | [what user accomplishes here] | [how user gets here] |
```

A screen is a distinct UI state, not a component.

## Step 3: Map User Flows

For each user story, define the flow:
```markdown
## User Flows

### Flow: [User Story Summary]

1. User starts at: [Screen]
2. User sees: [what's visible]
3. User action: [click/input/etc]
4. System response: [what happens]
5. User sees: [updated state]
6. End state: [where user ends up]

**Success path:** [brief description]
**Error path:** [what happens on failure]
```

## Step 4: Define Layout Structure

For each screen, define the layout:
```markdown
## Screen: [ScreenName]

### Layout Structure

\`\`\`
┌─────────────────────────────────────┐
│ Header: [what's here]                │
├─────────────┬───────────────────────┤
│ Sidebar     │ Main Content          │
│ [purpose]   │ [purpose]             │
│             │                       │
├─────────────┴───────────────────────┤
│ Footer: [what's here]                │
└─────────────────────────────────────┘
\`\`\`

### Sections

| Section | Content | Data Source |
|---------|---------|-------------|
| [area] | [what appears] | [which schema/store] |
```

## Step 5: Define Interaction Patterns

```markdown
## Interactions

### [Interaction Name]

**Trigger:** [user action]
**Component:** [which component handles this]
**Behavior:**
1. [immediate feedback]
2. [state change]
3. [side effects]

**Loading state:** [what user sees during async]
**Error state:** [what user sees on failure]
**Success state:** [what user sees on completion]
```

## Step 6: Specify Component Hierarchy

```markdown
## Component Hierarchy

\`\`\`
ScreenName
├── HeaderComponent
│   ├── Logo
│   └── Navigation
├── MainContent
│   ├── FilterPanel
│   │   └── FilterCheckbox (×n)
│   └── DataList
│       └── DataItem (×n)
└── FooterComponent
\`\`\`
```

Map to architecture components where possible.

## Step 7: Document State Visibility

```markdown
## State Visibility

| State | Visible In | Updated By |
|-------|------------|------------|
| [store.field] | [which screens/components] | [which actions] |
```

## Step 8: Write the Document

Assemble all sections into `03-UI-SPEC.md`.

## Output Verification

Before reporting complete, verify:
- [ ] Every user story has a flow
- [ ] Every flow has a screen
- [ ] Every screen has a layout
- [ ] Interactions cover success, loading, and error states
- [ ] Component hierarchy matches architecture components

## Error Handling

If requirements don't specify user-facing features:
→ HALT and clarify (is this a backend-only feature?)

If architecture doesn't support needed UI pattern:
→ HALT and document the gap for @architect to address
