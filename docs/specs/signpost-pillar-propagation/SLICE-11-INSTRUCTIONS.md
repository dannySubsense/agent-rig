# Slice 11 — Resident Agent Instructions (Components 4, 5, 7)

**Audience:** the resident agent of each roster repo. **You execute this in your own repo.**
**Authority:** Danny (composer), 2026-08-12 — resident agents receive full instructions and update
their own `CLAUDE.md` files.

**Source of record:** `agent-rig/HOMELAB-CLAUDE.md.template` (Components 4/7 text),
`agent-rig/MAP-NOT-ROUTE-BRIEFING.md.template` (Component 5).
**Sprint:** `signpost-pillar-propagation`. **Architecture:** `02-ARCHITECTURE.md`.

This is a **full instruction packet, not a map.** Map-not-route governs briefing a *verifier* — it
does not apply here. You are the doer; you get everything. (This slice has no Frank gate; see
step 6.)

---

## What this slice is, and what it is not

Components 4, 5, and 7 are **practice-only**: prose in your `CLAUDE.md` plus two template docs.
Zero engineering. No scripts, no hooks, no settings changes.

**This is not Slice 12.** Slice 12 (probe + hook, Components 1-3) is separate, tracked separately,
and released to agents independently. Do not bundle them — Slice 12 *does* carry a binding Frank
gate, and mixing a prose edit into that change makes the gate unable to tell what it is certifying.

---

## Step 0 — Decide and record: is your `CLAUDE.md` tracked?

**Do this first. It determines whether anything else in this slice is durable.**

```bash
git ls-files --error-unmatch CLAUDE.md >/dev/null 2>&1 && echo TRACKED || echo untracked
git check-ignore -v CLAUDE.md   # shows the ignoring rule, if any
```

Audited 2026-08-12 (`docs/reports/roster-gitignore-audit-2026-08-12.md`): **6 of 8 roster repos
gitignore `CLAUDE.md`; 2 track it.** `agent-rig` ignores its own. Untracked is the house norm.

**Why you are being asked:** Components 4/7 ship *as `CLAUDE.md` prose*. If that file is
gitignored, your edit changes one working copy on one machine — it does not survive a fresh clone,
is invisible to every other agent and to code review, and cannot be verified by anyone not sitting
on your filesystem. The change is real but **local**. That is not a reason to skip the slice; it is
a reason to know which of the two you are doing.

**The text goes in `CLAUDE.md` either way — that is not optional.** Being auto-loaded into context is the entire mechanism. Tracked-vs-untracked only decides whether it also survives a clone. You own your repo's blast radius; agent-rig does not decide
this for you. Pick one and state it in your step-7 capture (see step 6 — this slice has no Frank gate):

- **(a) Keep it untracked** — accept the edit as deliberately machine-local practice. Record
  `claudeMdTracked: false` and do not claim the change is propagated beyond this machine.
- **(b) Track it** — `git rm --cached` the ignore, drop the `.gitignore` line, commit. Do this only
  if your `CLAUDE.md` holds no secrets or machine-specific paths. **Check before you commit** —
  several of these files carry local absolute paths, and one carries connection strings.
- **(c) Split it — WITHDRAWN 2026-08-12. Do not do this.** The earlier version of this packet
  offered moving C4/C7 into a tracked `docs/SESSION-START.md` referenced from `CLAUDE.md`, and
  recommended it. That was wrong and it broke the mechanism: **`CLAUDE.md` is loaded into context
  automatically at session start; a referenced doc is not.** The convention only works because the
  text is in front of you before your first reply. Moving it to a file an agent must choose to open
  turns a forcing function into documentation. Durable-and-never-loaded is worse than
  local-and-always-loaded. If you already did this, fold it back into `CLAUDE.md`.

If your `CLAUDE.md` is already tracked (`ask-edgar-repo`, `sonic-store`), take (a) trivially — you
are already durable — and record `claudeMdTracked: true`.

---

## Step 1 — Pre-existing content: already established, don't re-derive

**Cancelled — do not run a blast-radius grep.** `docs/reports/roster-gitignore-audit-2026-08-12.md`
already established this centrally, with its method stated: C4/C7 content exists nowhere on the
roster except `market_data`, and three repos (`ask-edgar-repo`, `sonic-store`, `runtime/agent-lore`)
have no Session Start Behaviour section at all — for those, step 2 is an insert, not an edit.

Read your own row in that audit. Seven agents re-deriving a known-empty result is cost with no
information yield.

---

## Step 2 — Component 4: Session Start Behaviour + Signpost:/Pillar: labeling

Copy the `## Session Start Behaviour` section verbatim from
`agent-rig/HOMELAB-CLAUDE.md.template` (lines 91-158), substituting `<PROJECT-ID>` and
`<AGENT-NAME>` with your own. It contains:

1. The three cold-start checks (LORE `search_knowledge`, Switchboard `read_messages`, `git fetch` +
   `git status -uno` — **fetch and report only, never auto-merge/pull/push**).
2. The **Signpost: / Pillar:** first-turn labeling convention.

**The labeling convention is the substance of this slice.** Your first-turn state summary must
separate:

- **Signpost:** what `search_knowledge` (and a SessionStart probe, if your repo runs one) returned —
  prior-session claims and narrative, **not yet independently checked this session**.
- **Pillar:** what you personally verified this session against a primary source — read the actual
  file, ran the query, checked live state — stated *with its verification method*. If nothing has
  been verified yet, say so explicitly: `Pillar: none yet — nothing independently checked this
  session`. Do not omit the label.

Never state a status claim as settled fact without it falling under one of these two labels.

**Note if you also run the probe hook (Slice 12):** the hook's raw output is still a **Signpost** —
mechanically gathered, not independently verified. It is not a Pillar, and its presence is not
evidence that priming happened. Neither the hook nor this convention is an automatic gate; both
depend on you actually doing them.

---

## Step 3 — Component 5: map-not-route briefing convention

Copy `agent-rig/MAP-NOT-ROUTE-BRIEFING.md.template` into your repo and reference it from
`CLAUDE.md`.

When briefing a verifier (Frank, an auditor, a reviewer): give the **map** — objective,
architecture, where things live, what is claimed. Never the **route** — your method, your checklist,
your completion notes. **A method handed over is a lens handed over; it caps their ceiling at
yours.**

State it as a consequence, not a courtesy: the point is not briefing hygiene, it is that **you lose
the verifier's independent ceiling the moment you hand them your route.** They stop checking the
thing and start checking your account of it. (`beta`, 2026-08-12.)

This is not theoretical. On 2026-08-12, `alpha` specified a cutover shape wrongly — merging project
logic into the canonical probe, the anti-pattern named at `02-ARCHITECTURE.md:274-276`. Frank caught
it *because he was briefed objective+architecture only and went to the source*. Had he received
alpha's checklist, he would have inherited the blind spot and the anti-pattern would have propagated
to seven repos with a Frank stamp on it.

---

## Step 4 — Component 7: capture schema

Copy the `Verification:` / `Re-verify with:` convention from the template's `## Capture Behaviour`
section. Every durable capture's free-text body must include both lines:

- **`Verification:`** — what was checked and by what method ("read the live file at `path` and
  confirmed the section exists"; "ran `git log --oneline -5`, commit present"). A capture that
  restates a claim without saying how it was checked **does not satisfy this line**.
- **`Re-verify with:`** — the exact command or query a future session can run to re-confirm.
  Concrete and runnable, not a vague pointer.

Practice convention, not an automated gate. Nothing validates these; include them by discipline.

---

## Step 5 — Verify your own edit

In Claude Code, `grep` routes to ugrep with `--ignore-files` and is **blind to gitignored files**
when used recursively — use `command grep`, or grep the path directly as below. (`alpha`, 2026-08-12.)

```bash
command grep -c -i "signpost" CLAUDE.md  # expect >0
command grep -c "Pillar:" CLAUDE.md      # expect >0
command grep -c "Re-verify with" CLAUDE.md  # expect >0
git ls-files --error-unmatch CLAUDE.md >/dev/null 2>&1 && echo "durable" || echo "LOCAL ONLY"
```

**Reading the file back is not sufficient on its own.** Content-presence returns "present" in
exactly the least durable case — the untracked one. Pair it with the tracked-status check, and
report both. (Same trap as the Slice 12 exec-bit defect: the naive observation says fine precisely
when it isn't.)

---

## Step 6 — No Frank gate for this slice

**Cancelled.** Do not dispatch a Frank gate for Slice 11. The step-5 self-check is the whole
verification.

Why, since the sprint mandates a gate elsewhere: **a gate cannot verify a habit.** C4/C5/C7 are
practice conventions — they are followed, or not, in *future sessions*, not at install time. All a
gate could check here is that text is present and whether the file is tracked, which is a two-line
grep you run yourself in step 5. And in the 6 of 8 repos where `CLAUDE.md` is untracked, a binding
PASS would stamp a machine-local, unversioned, unreviewable working-copy edit — a seal on state
nobody else can inspect.

The per-repo unbriefed gate was written for the **cutover** case (Slice 10/12): replacing live
executable code with unknown call-sites. It was inherited by a slice whose risk profile it was never
sized for. Correct where it was born, ceremony where it landed.

**The Frank gate remains mandatory for Slice 12** — that installs a probe script and a SessionStart
hook, and it has already caught two real defects.

---

## Step 7 — Record to LORE

`documentType: "decision"`, `epistemicType: "FACT"`, with `Verification:` / `Re-verify with:` lines
(this slice's own convention applies to its own completion record). Keep it short:

```typescript
{
  project: string;
  residentAgent: string;
  componentsApplied: ["4", "5", "7"];
  claudeMdTracked: boolean;        // step 0 — false means this edit is machine-local
  trackingDecision: "keep-untracked" | "tracked-it" | "split-to-docs";
}
```

---

## Reporting back

One message to `wright` on Switchboard, thread `signpost-pillar-propagation`, three fields:
your step-5 self-check result, `claudeMdTracked`, and `trackingDecision`. Without those three,
"Slice 11 complete" means different things in different repos.

**If you chose option (b), track it** — add one line: that you checked for secrets and machine-local
absolute paths before committing. That is the one place this slice can do real damage, and a
self-attestation is the right-sized control for it.

A short reply is the expected output here. Don't write a report.

If you hit something this packet does not cover, or something in it is wrong for your repo, **say so
rather than improvising silently** — a defect found in one repo gets fixed centrally before it
reaches the other seven. That is exactly how the Slice 12 exec-bit and trace-location defects were
caught.
