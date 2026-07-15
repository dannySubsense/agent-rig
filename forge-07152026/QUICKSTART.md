# Forge Quickstart

**Version:** 07152026

Get up and running in 5 minutes.

---

## 1. Install

```bash
./install.sh
```

This copies agents, skills, and commands to `~/.claude/`.

---

## 2. Set Up Your Project

```bash
cd your-project

# Copy governance templates
cp ~/.claude/templates/CLAUDE.md ./CLAUDE.md
cp ~/.claude/templates/INVARIANTS.md ./docs/INVARIANTS.md
cp ~/.claude/templates/CADENCE.md ./docs/CADENCE.md

# Edit for your project
```

`docs/INVARIANTS.md` and `docs/CADENCE.md` are **mandatory** — `/forge-start` HALTs before any
agent delegation if either is missing. There is no "if exists" fallback.

---

## 3. Create Specs First

Forge needs approved spec documents. Use Spec Orchestration to create them:

```bash
claude
> /spec-start
```

This produces:
```
docs/specs/{feature}/
├── NORTH-STAR.md
├── 01-REQUIREMENTS.md
├── 02-ARCHITECTURE.md
├── 03-UI-SPEC.md
├── 04-ROADMAP.md
└── 05-REVIEW.md
```

Review and approve before proceeding. `docs/specs/{feature}/NORTH-STAR.md` is also **mandatory**
for Forge — it's the artifact Frank's binding forge-gate reads to judge sprint North Star
fidelity, and `/forge-start` HALTs before any delegation if it's missing.

---

## 4. Start Forging

```bash
claude
> /forge-start
```

Point to your specs:
```
> Build from docs/specs/model-viewer/
```

Forge will:
1. Load governance — HALT if `docs/INVARIANTS.md`, `docs/CADENCE.md`, or the sprint
   `NORTH-STAR.md` is missing
2. Read the roadmap slices
3. Delegate to agents in sequence
4. Build → Test → Verify each slice
5. Report progress

---

## 5. The Cycle

For each slice:

```
@code-executor  →  Implements code
        ↓
@test-writer    →  Writes tests
        ↓
@test-runner    →  Runs tests
        ↓           ↓
      PASS        FAIL → fix loop
        ↓
@qc-agent       →  Verifies compliance
        ↓           ↓
      PASS        FAIL → fix loop
        ↓
    COMPLETE
```

---

## 6. Checkpoints

Forge runs autonomously but reports at:
- Slice completion
- Test failures (with diagnosis)
- QC violations (with specifics)
- Session end (with summary)

You can interrupt anytime.

---

## 7. Feature Completion — Frank's Binding Forge-Gate

Once every slice reaches STAMP: APPROVED, Forge invokes Frank once, as a binding gate
(`LANE: forge-gate`), before docs and the PR. PASS/FAIL/HALT with no manual override — a
FAIL/HALT blocks `@doc-writer` and `@github-ops` the same way a missing approved spec blocks
implementation. See `README.md` for the full gate procedure.

---

## Example Session

```
> /forge-start
> Build from docs/specs/filter-panel/

Starting Forge for: docs/specs/filter-panel/

Slices to implement:
1. [ ] Types and Store (2 files)
2. [ ] Filter Component (3 files)
3. [ ] Integration (2 files)

Beginning Slice 1...

═══════════════════════════════════════════════════════════════════
DELEGATING TO @code-executor
═══════════════════════════════════════════════════════════════════
...

✅ Slice 1 complete. Tests: 4/4 passing. QC: PASS.

Beginning Slice 2...
```

---

## Troubleshooting

### "Spec documents not found"
Ensure specs are in `docs/specs/{feature}/` with correct filenames.

### "HALTED — missing governance artifact"
`docs/INVARIANTS.md`, `docs/CADENCE.md`, or `docs/specs/{feature}/NORTH-STAR.md` is missing.
This blocks the whole session before any delegation — copy the missing template or produce the
missing spec artifact, then restart.

### "Agent HALTED"
Read the HALT message. Usually means:
- Spec is ambiguous
- Something is missing
- Decision needed

### "Tests keep failing"
Check if it's implementation bug or test bug. Forge Advisor will diagnose and re-delegate.

### "QC keeps failing"
Review the QC report. Common issues:
- Acceptance criteria not implemented
- Architecture pattern violation
- Invariant breach

---

## Next Steps

- Read the full [README.md](./README.md)
- Review agent definitions in `agents/`
- Customize templates for your project
