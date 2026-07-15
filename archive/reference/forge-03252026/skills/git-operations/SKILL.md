---
name: git-operations
description: |
  Step-by-step process for git operations and GitHub workflows.
  Use for commits, branches, and pull requests.
allowed-tools: Read, Bash, Glob
---

# Git Operations

Procedural guide for git operations in the development workflow.

## Operation: Status

Check current git state:

```bash
# Current branch
git branch --show-current

# Status
git status --short

# Recent commits
git log --oneline -5
```

Report:
```
Branch: feature/model-viewer
Status: 3 modified, 1 new
Last commit: abc1234 "feat(viewer): add rotation controls"
```

## Operation: Branch

Create a feature branch:

```bash
# Ensure on main/develop
git checkout main
git pull origin main

# Create branch
git checkout -b feature/{feature-name}

# Or for slice work
git checkout -b slice/{feature}/{slice-number}
```

Naming conventions:
- `feature/{name}` — New features
- `fix/{description}` — Bug fixes
- `slice/{feature}/{n}` — Per-slice branches
- `chore/{description}` — Maintenance

## Operation: Commit

After QC passes, commit the slice:

### Step 1: Stage files

```bash
# Stage specific files (preferred)
git add src/types/feature.ts
git add src/stores/featureStore.ts

# Or stage all changes (verify first)
git status
git add .
```

### Step 2: Commit with message

```bash
git commit -m "feat(feature): implement slice N

- Add FeatureType interface
- Add featureStore with actions
- Add FeatureComponent

Refs: Slice N from 04-ROADMAP.md"
```

### Commit Message Format

```
{type}({scope}): {brief description}

- {detail 1}
- {detail 2}

Refs: {reference to spec}
```

Types:
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code change without feature/fix
- `test` — Adding tests
- `docs` — Documentation
- `chore` — Maintenance

## Operation: Push

Push branch to remote:

```bash
# Push new branch
git push -u origin {branch-name}

# Push existing branch
git push
```

## Operation: Pull Request

Create PR via GitHub CLI:

```bash
# Check gh is authenticated
gh auth status

# Create PR
gh pr create \
  --title "feat(feature): {description}" \
  --body "## Summary
Implements Slice N from docs/specs/feature/04-ROADMAP.md

## Changes
- {change 1}
- {change 2}

## Testing
- [ ] Unit tests pass
- [ ] QC verification pass

## Checklist
- [ ] Code follows architecture spec
- [ ] Tests cover acceptance criteria
- [ ] No console.log or debug code"
```

## Operation: Merge

After PR approval:

```bash
# Merge via GitHub CLI
gh pr merge --squash

# Or merge locally
git checkout main
git pull origin main
git merge --no-ff {branch-name}
git push origin main
```

## Pre-Operation Checks

Before any operation, verify:

```bash
# No uncommitted changes (unless committing)
git status --short

# On correct branch
git branch --show-current

# Up to date with remote
git fetch origin
git status -uno
```

## Error Handling

### Merge Conflict

```
❌ HALT: Merge conflict detected

Conflicting files:
- src/stores/featureStore.ts

Action required: Human resolution
```

### Uncommitted Changes

```
❌ HALT: Uncommitted changes exist

Modified files:
- src/components/Feature.tsx

Action required: Commit or stash before operation
```

### Remote Ahead

```
❌ HALT: Remote has changes not in local

Behind by: 3 commits

Action required: Pull before push
```
