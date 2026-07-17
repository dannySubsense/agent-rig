# Notebook Orchestration — Quick Start

## Install

```bash
cd notebook-orchestration-04182026
./install.sh
```

Installs agents, skills, commands, and templates to `~/.claude/`. Existing files backed up to `~/.claude/backup/YYYYMMDD_HHMMSS/`.

## One-time project setup

Copy the invariants template into your project and edit as needed:

```bash
mkdir -p docs/research
cp ~/.claude/templates/NOTEBOOK-INVARIANTS.md docs/research/NOTEBOOK-INVARIANTS.md
```

The invariants doc is project-specific. The global template is the starting point.

## Build a notebook

```bash
claude
> /notebook-start
```

The orchestrator will ask for:
- Which notebook in the series (number + name)
- Planning doc (e.g., `docs/research/planning/notebook-roadmap.md`)
- Dataset paths (e.g., `docs/research/data/backtest_results.parquet`)
- Where to write the notebook (e.g., `research/notebooks/`)

## What happens

```
1. @notebook-designer produces design-sheet.md
   → HUMAN APPROVAL GATE (you review the sheet)

2. @notebook-builder writes the .ipynb

3. @notebook-executor runs it, produces _executed.ipynb

4. @notebook-qc runs mechanical checks
   → If fail, back to builder with specific gaps

5. @frank runs the judgment gate
   → If fail, back to builder with specific gaps

6. Notebook Advisor STAMP: APPROVED
   → HUMAN FINAL GATE (you approve to commit)
```

At each gate, you can interrupt, revise, or continue.

## File outputs

For notebook 02 named `the_plays`:

```
research/notebooks/
├── 02_the_plays.ipynb                 # Built notebook
└── 02_the_plays_executed.ipynb        # Executed version with outputs

docs/research/planning/notebooks/
└── 02-design.md                       # Design sheet (committed)
```

## Resume

If a session is interrupted, `/notebook-start` again and point to the in-progress notebook. The orchestrator resumes from the last completed stage.

## Troubleshooting

**QC keeps failing:** Re-read the design sheet. If the sheet itself is wrong, fix it and restart from the builder stage.

**Frank rejects something that looks fine:** Read his reasoning carefully. His bar is "would a skeptical reviewer tear this apart." If he's right, tighten the prose or narrow the claims.

**Executor hits cell errors:** The builder wrote code that doesn't run against the actual data. Common causes: schema assumption mismatch, missing NULL handling, incorrect dataset path.

**Designer output is too vague:** Give more context in the initial request — what questions specifically, what the reader should walk away knowing, which sections of the planning doc apply.

## Updating the framework

Pull new version, re-run `./install.sh`. Existing files are backed up. Review the backup to see what changed.
