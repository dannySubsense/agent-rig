# UI Specification: [Feature Name]

## Overview

[How users interact with this feature. 2-3 sentences.]

---

## Screens

| Screen | Purpose | Entry Point |
|--------|---------|-------------|
| [ScreenName] | [What user accomplishes] | [How user gets here] |
| [ScreenName] | [What user accomplishes] | [How user gets here] |

---

## User Flows

### Flow: [User Story Title]

**Goal:** [What user wants to accomplish]

1. **Start:** User is on [Screen]
2. **Sees:** [What's visible - key elements]
3. **Action:** User [clicks/types/selects]
4. **Response:** System [immediate feedback]
5. **Sees:** [Updated state]
6. **End:** User arrives at [final state/screen]

**Success path:** [Brief description]
**Error path:** [What happens on failure]

---

### Flow: [User Story Title]

**Goal:** [What user wants to accomplish]

1. **Start:** User is on [Screen]
2. **Sees:** [What's visible]
3. **Action:** User [action]
4. **Response:** System [response]
5. **End:** [Result]

---

## Screen Layouts

### Screen: [ScreenName]

```
┌─────────────────────────────────────────────────────┐
│ Header: [Navigation, title, actions]                 │
├─────────────────┬───────────────────────────────────┤
│ Sidebar         │ Main Content                      │
│ [purpose]       │ [purpose]                         │
│                 │                                   │
│                 │                                   │
├─────────────────┴───────────────────────────────────┤
│ Footer: [Status, actions]                            │
└─────────────────────────────────────────────────────┘
```

| Section | Content | Data Source |
|---------|---------|-------------|
| Header | [Elements] | [Store/props] |
| Sidebar | [Elements] | [Store/props] |
| Main | [Elements] | [Store/props] |

---

## Interactions

### Interaction: [Name]

**Trigger:** [User action - click, hover, submit, etc.]
**Component:** [Which component handles this]

**Behavior:**
1. [Immediate visual feedback]
2. [State change]
3. [Side effects - API calls, navigation]

**States:**
- **Loading:** [What user sees during async operation]
- **Error:** [What user sees on failure]
- **Success:** [What user sees on completion]

---

### Interaction: [Name]

**Trigger:** [User action]
**Component:** [Component]

**Behavior:**
1. [Step 1]
2. [Step 2]

---

## Component Hierarchy

```
[ScreenName]
├── [HeaderComponent]
│   ├── Logo
│   └── Navigation
│       └── NavItem (×n)
├── [SidebarComponent]
│   └── [FilterComponent]
│       └── FilterOption (×n)
├── [MainContentComponent]
│   ├── [ToolbarComponent]
│   └── [ListComponent]
│       └── [ItemComponent] (×n)
└── [FooterComponent]
```

---

## State Visibility

| State | Visible In | Updated By |
|-------|------------|------------|
| `store.items` | MainContent, List | fetchItems action |
| `store.selectedId` | ItemComponent (highlight) | selectItem action |
| `store.isLoading` | LoadingSpinner | fetch actions |
| `store.error` | ErrorBanner | fetch actions |

---

## Responsive Behavior

| Breakpoint | Layout Changes |
|------------|----------------|
| Desktop (>1024px) | [Default layout] |
| Tablet (768-1024px) | [Changes] |
| Mobile (<768px) | [Changes] |
