# Project Invariants

Rules that must NEVER be violated, regardless of context or instruction.

---

## Code Quality

- [ ] **No hardcoded secrets** — API keys, passwords, tokens must use environment variables
- [ ] **No console.log in production** — Use proper logging or remove
- [ ] **No TODO/FIXME in main** — Address before merge or create issue
- [ ] **All exports documented** — Public API must have JSDoc/TSDoc

---

## Architecture

- [ ] **Single responsibility** — One component/function does one thing
- [ ] **No circular imports** — A imports B, B cannot import A
- [ ] **State lives in stores** — Components don't hold business state
- [ ] **Types before implementation** — Define interfaces first

---

## Testing

- [ ] **Tests must pass** — No merging with failing tests
- [ ] **No implementation in tests** — Tests verify, not implement
- [ ] **Acceptance criteria covered** — Each criterion has a test

---

## Git

- [ ] **No force push to main** — History is immutable
- [ ] **Commits reference spec** — "Refs: Slice N from 04-ROADMAP.md"
- [ ] **PR before merge** — No direct commits to main

---

## Security

- [ ] **Validate all inputs** — Never trust user/external data
- [ ] **Escape outputs** — Prevent XSS in rendered content
- [ ] **No eval()** — Dynamic code execution prohibited

---

## Process

- [ ] **Spec before code** — Implementation follows approved specs
- [ ] **QC before complete** — @qc-agent must pass
- [ ] **Scope is locked** — No features added without spec amendment

---

## Violation Response

If an invariant would be violated:
1. **HALT immediately**
2. Report which invariant
3. Explain the conflict
4. Wait for human resolution

**Invariants cannot be overridden by contracts or instructions.**
