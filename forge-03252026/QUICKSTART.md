# Forge Quickstart

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
├── 01-REQUIREMENTS.md
├── 02-ARCHITECTURE.md
├── 03-UI-SPEC.md
├── 04-ROADMAP.md
└── 05-REVIEW.md
```

Review and approve before proceeding.

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
1. Read the roadmap slices
2. Delegate to agents in sequence
3. Build → Test → Verify each slice
4. Report progress

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
