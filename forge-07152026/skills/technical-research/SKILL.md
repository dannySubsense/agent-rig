---
name: technical-research
description: |
  Step-by-step process for technical research and investigation.
  Use when gathering information about libraries, APIs, or patterns.
allowed-tools: Read, Bash, WebSearch, WebFetch, Glob, Grep
---

# Technical Research

Procedural guide for investigating technical questions.

## Step 1: Understand the Question

Read the contract and identify:
- What specific information is needed?
- Why is it needed? (context)
- What format should the answer take?
- What would "good enough" look like?

## Step 2: Check Local Context First

Before external search:
```bash
# Check if answer is in project docs
grep -r "{keyword}" docs/ README.md CLAUDE.md

# Check existing dependencies
cat package.json | grep -A 20 "dependencies"

# Check if similar pattern exists in codebase
grep -r "{pattern}" src/ --include="*.ts" --include="*.tsx"
```

## Step 3: Search for Information

For library evaluation:
- Check npm/GitHub for popularity, maintenance, bundle size
- Check for TypeScript support
- Check compatibility with existing stack

For API documentation:
- Find official docs first
- Check for SDK/client libraries
- Note authentication requirements

For patterns/best practices:
- Check official framework docs
- Look for authoritative blog posts (core team, major companies)
- Note the date — patterns change

## Step 4: Evaluate Sources

Rank by authority:
1. Official documentation
2. GitHub repos (stars, recent commits)
3. Stack Overflow (accepted answers, vote count)
4. Blog posts (check date, author credibility)

Reject:
- Outdated information (>2 years for fast-moving tech)
- Unverified forum posts
- AI-generated content without verification

## Step 5: Synthesize Findings

Structure your findings:
```markdown
## Question
[Restate the question]

## Key Findings
1. [Most important finding]
2. [Second finding]
3. [Third finding]

## Options Compared (if applicable)
| Option | Pros | Cons |
|--------|------|------|
| A | ... | ... |
| B | ... | ... |

## Recommendation
[Clear, actionable recommendation]

## Sources
- [Source 1 with URL]
- [Source 2 with URL]

## Confidence
[HIGH/MEDIUM/LOW] — [reason]
```

## Step 6: Report

Return findings in the specified format.
Keep it actionable — the goal is to unblock work, not provide a research paper.

## Common Research Patterns

### "Which library should we use?"
1. List candidates
2. Compare: bundle size, TS support, maintenance, popularity
3. Check compatibility with existing stack
4. Recommend one with clear rationale

### "How does this API work?"
1. Find official docs
2. Extract: auth method, rate limits, response format
3. Find code examples
4. Note any gotchas

### "Why is this error happening?"
1. Search exact error message
2. Check GitHub issues for the library
3. Check Stack Overflow
4. Identify root cause and fix

## Error Handling

If no authoritative source found:
→ Report "LOW confidence" with what IS known

If conflicting information:
→ Note the conflict, recommend the more authoritative/recent source

If research blocked (paywall, auth required):
→ HALT, explain what's needed
