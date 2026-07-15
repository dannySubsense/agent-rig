---
name: documentation-writing
description: |
  Step-by-step process for writing documentation.
  Use for README, API docs, and inline documentation.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Documentation Writing

Procedural guide for writing documentation that matches implementation.

## Step 1: Load the Contract

Read and extract from the contract:
- DOC_TYPE: readme | api | inline | changelog
- TARGET_FILES: Files to document
- OUTPUT_PATH: Where to write docs

## Step 2: Read Implementation

```bash
# Read the files being documented
cat {TARGET_FILES}

# Extract exports
grep -E "^export" {TARGET_FILES}

# Extract types/interfaces
grep -A 10 "interface\|type " {TARGET_FILES}
```

## Documentation Type: README

For feature/component README:

```markdown
# {Feature Name}

{One sentence description of what this does.}

## Usage

\`\`\`tsx
import { FeatureComponent } from './FeatureComponent';

function App() {
  return <FeatureComponent prop={value} />;
}
\`\`\`

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `prop1` | `string` | Yes | {description} |
| `prop2` | `number` | No | {description} |

## Examples

### Basic Usage

\`\`\`tsx
<FeatureComponent prop1="value" />
\`\`\`

### With Options

\`\`\`tsx
<FeatureComponent 
  prop1="value"
  prop2={42}
/>
\`\`\`
```

## Documentation Type: API

For service/store documentation:

```markdown
# {Service/Store Name} API

## Overview

{What this service does and when to use it.}

## Methods

### `methodName(params): ReturnType`

{Description of what it does.}

**Parameters:**
- `param1` (`Type`) — {description}

**Returns:** `Type` — {description}

**Example:**
\`\`\`typescript
const result = await methodName({ param1: 'value' });
\`\`\`

**Errors:**
- `ErrorType` — When {condition}
```

## Documentation Type: Inline (JSDoc/TSDoc)

Add to source files:

```typescript
/**
 * Brief description of the function.
 * 
 * @param param1 - Description of param1
 * @param param2 - Description of param2
 * @returns Description of return value
 * 
 * @example
 * ```ts
 * const result = functionName('value', 42);
 * ```
 */
export function functionName(param1: string, param2: number): ReturnType {
  // ...
}
```

For components:

```typescript
/**
 * Brief description of the component.
 * 
 * @example
 * ```tsx
 * <ComponentName prop="value" />
 * ```
 */
export function ComponentName({ prop }: ComponentProps) {
  // ...
}
```

## Documentation Type: Changelog

For CHANGELOG.md entries:

```markdown
## [Unreleased]

### Added
- {Feature description} ([#PR](link))

### Changed
- {Change description}

### Fixed
- {Fix description}
```

Follow [Keep a Changelog](https://keepachangelog.com/) format.

## Verification

Before reporting complete:

- [ ] All exports are documented
- [ ] Examples are copy-paste ready
- [ ] Types match implementation
- [ ] No references to unimplemented features
- [ ] Follows existing doc patterns

```bash
# Check for undocumented exports
grep "^export" {TARGET_FILES} | wc -l
# Should match number of documented items
```

## Report Completion

```
✅ DOCUMENTATION COMPLETE

Files created/updated:
- docs/api/feature.md — API documentation
- src/components/Feature/README.md — Usage guide

Documented:
- 3 components
- 5 functions
- 2 types

Status: COMPLETE
```

## Error Handling

If implementation behavior is unclear:
→ Document what IS clear, flag unclear parts

If existing docs contradict implementation:
→ HALT, report the conflict
