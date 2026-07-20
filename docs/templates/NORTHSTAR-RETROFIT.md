# Northstar Retrofit Procedure

Source schema: `docs/NORTHSTAR.md`'s canonical four-section shape is owned by DDR-012 §3.1
(`agent-dashboard` repo). This procedure does not restate or redefine that shape — it points to it.
Source contract: `RetrofitCompletionCapture` (architecture §2, `project-bootstrap-v2` sprint,
`agent-dashboard` repo).

---

## 1. Preamble

This document is a **procedure**, not code — a fixed sequence of steps for retroactively producing
`docs/NORTHSTAR.md` in a project that predates DDR-012 (the Northstar model). It is handed to (or
picked up by) **that project's own agent** — the agent already working in that project's repo, under
that project's own identity — not run by `agent-dashboard`/Lumen on another project's behalf. Lumen
may draft a candidate as a starting point for a project (see the ecosystem-rollout candidate, if one
exists at `docs/specs/project-bootstrap-v2/candidates/<projectId>-NORTHSTAR-DRAFT.md` in
`agent-dashboard`), but it is always that project's own agent who runs this procedure to actually
produce, confirm, write, and commit the final `docs/NORTHSTAR.md` in that project's own repo.

**Explicit non-goal:** this is a procedure doc, not a slash command and not a skill. Per DDR-012 §3.3
and `project-bootstrap-v2`'s requirements ("Out of Scope"), promoting this doc to a slash command or
skill is explicitly deferred as a v2 candidate contingent on usage data — it is not built here and
should not be treated as a `/`-invocable command by any agent reading this.

**Tooling requirement:** this procedure requires no tool beyond **Read**, **Write**, `git` (via
Bash), and `capture_memory` (the system-wide `lore-gateway` MCP tool). No new MCP tool, no new slash
command, and no new skill file are needed to run it — every agent in every project already has all
four.

---

## 2. Read order (fixed)

Gather source materials in this exact order. Each substep below states its own fallback if the
source is absent — never halt on a missing source; a thin or absent input degrades the eventual
draft's quality, it does not block drafting.

### 2.1 Read that project's own `CLAUDE.md` project-context paragraph

Read the project-context paragraph from that project's own root `CLAUDE.md`.

- **If the paragraph is missing** (file absent, or present but carries no identifiable
  project-context paragraph): note `claudeMdProjectContext` as `null`, and continue to step 2.2.

### 2.2 Read that project's own DDRs

Read every DDR file found under that project's own `docs/specs/*-ddrs/*.md` (all matching files, all
of them — not a sample).

- **If no DDRs directory exists** (no path matches `docs/specs/*-ddrs/`): note `ddrDocuments` as
  `empty`, and continue to step 2.3.

### 2.3 Read that project's own `README.md`

Read that project's own root `README.md` last, after CLAUDE.md and the DDRs.

- **If no README exists**: note `readmeContent` as `null`, and proceed to Synthesis (§3).

---

## 3. Synthesis

Expand the gathered materials (§2) into the canonical four-section shape — **Purpose, Thesis,
Non-goals, Drift check** — owned by DDR-012 §3.1 and reused unchanged as the same shape
`project-bootstrap-v2` architecture §2.0 calls `NorthstarDocument`. This document does not
independently redefine that shape; DDR-012 §3.1 is the sole source of truth for the section list, the
header line format, and the Drift-check tripwire count (2-4). If that shape ever changes, DDR-012
§3.1 is the only place to edit — this retrofit doc must then be updated to match, never the reverse.

**Derive, don't interview.** Expand what the gathered materials already state — a project's own
decided purpose, thesis, and boundaries are usually already implicit in its CLAUDE.md project-context
paragraph, its DDRs' stated rationale, and its README's description. Do not start from a blank
interview or invent purpose/thesis/non-goals/tripwires from nothing; synthesize them from what
already exists in the materials read in §2.

**Thinness flag.** If any one (or more) of the three sources in §2 was absent or thin (per the
fallback notes recorded in §2.1–2.3, or present but sparse enough to yield weak synthesis material),
set `thinSourceFlag: true` and write a one-line `thinSourceReason` (e.g. `"CLAUDE.md project-context
paragraph absent; DDRs and README only"`). Carry both forward into the Confirmation gate (§4) so the
human reviewing the draft sees the caveat alongside the draft itself, not just the draft in
isolation.

---

## 4. Confirmation gate

Present the full rendered draft — including `thinSourceFlag`/`thinSourceReason` called out explicitly
if `thinSourceFlag` is `true` — to that project's human/Composer.

Same loop semantics as `project-bootstrap-v2`'s new-project Substep 4.5.2:

- Await explicit confirmation or an edit request.
- If changes are requested, revise the draft per the feedback and re-present.
- Repeat until the human gives explicit confirmation.
- **No write occurs on any outcome other than explicit confirmation.** Do not proceed to §5 (Write
  and commit) on a partial, implied, or silent confirmation.

---

## 5. Write and commit

Once (and only once) §4's confirmation gate returns a confirmed outcome:

1. Write the confirmed content to `docs/NORTHSTAR.md` at that project's own root, using the Write
   tool.
2. Stage and commit it using that project's own established git workflow and identity — this
   procedure does not prescribe a commit message convention; use whatever convention that project's
   own repo already follows.

`docs/NORTHSTAR.md` is never gitignored and is always committed and tracked — it carries no secrets,
unlike that project's own `CLAUDE.md`.

---

## 6. LORE capture

Immediately after the commit in §5 completes, call `capture_memory` with the following shape (the
`RetrofitCompletionCapture` contract, `project-bootstrap-v2` architecture §2):

```typescript
interface RetrofitCompletionCapture {
  projectId: string;
  author: string;               // that project's own agent slug — never "lumen"
  documentType: 'decision';
  epistemicType: 'FACT';
  content: string;               // must state: retrofit ran, date, source materials used, thinSourceFlag value
}
```

- `projectId` — that project's own LORE `projectId` (never `agent-dashboard`, unless
  `agent-dashboard` itself is the project being retrofitted).
- `author` — that project's own agent slug. **Never `lumen`** — Lumen may have drafted an earlier
  candidate as a starting point, but the retrofit's completion is recorded by the project's own agent
  who ran §§4-5, under that agent's own identity.
- `documentType` — always `"decision"`.
- `epistemicType` — always `"FACT"`.
- `content` — a string that states all four of the following elements, explicitly, so a future
  session can find durable evidence the retrofit already ran without needing to re-derive it:
  1. **that the retrofit ran** — i.e. this procedure was executed and completed for this project;
  2. **the date** it ran;
  3. **which sources were used** — i.e. which of CLAUDE.md project-context paragraph / DDRs / README
     were actually present and read (per §2's `null`/`empty`/`null` fallbacks, note which were
     absent too, not only which were present);
  4. **the `thinSourceFlag` value** (`true` or `false`) determined in §3, so a future session knows
     whether the confirmed Northstar was drafted from thin material.

This capture is the durable, LORE-queryable record that prevents this retrofit from being silently
re-run or silently skipped in a later session on this project.
