---
description: Bootstrap a new homelab project: agent identity, CLAUDE.md, git, GitHub, LORE capture.
---

## Preamble

This command encodes the canonical 13-step homelab bootstrap sequence. The executing producer agent reads this document and follows it procedurally — gathering inputs from Danny, conducting a vision quest to name and register a new agent identity, registering with Cairn via the Switchboard relay, generating CLAUDE.md and MACHINE-SETUP.md from templates, creating the .gitignore, initializing git, creating the GitHub repo, configuring the SSH remote, bootstrapping the DDR directory, making the initial commit and push, and capturing the bootstrap record to LORE. The result is a fully bootstrapped project with a consistent repo shape ready for the first sprint.

---

## Fixed Decision Table

These values are locked. Never ask Danny about them.

| Decision | Fixed value |
|---|---|
| GitHub account | `dannySubsense` |
| Git email | `danny@subsense.art` |
| Git name | `dannySubsense` |
| Branch name | `main` |
| SSH remote alias | `github.com-danny` |
| git config scope | per-repo (global and system flags prohibited) |
| LORE DB | `<lore-db-host>:5432/lore` |
| Template source dir | `~/.claude/templates/` (runtime read location; source-of-record is the agent-rig repo, deployed here — DDR-014) |
| HOMELAB-CLAUDE.md template filename | `HOMELAB-CLAUDE.md.template` |
| MACHINE-SETUP.md template filename | `MACHINE-SETUP.md.template` |
| Bootstrap commit message | `chore: project bootstrap` |
| Bootstrap staged files | `.gitignore`, `HOMELAB-CLAUDE.md.template`, `.claude/commands/relay.md`, `docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md`, `docs/NORTHSTAR.md` (path is variable — `<InputBundle.projectId>` is resolved at runtime) |
| LORE documentType (bootstrap) | `decision` |
| LORE epistemicType (bootstrap) | `FACT` |
| LORE status (bootstrap) | `locked` |
| Cairn relay handle | `cairn` |
| Cairn thread | `registration` |
| relay.md send identity | `from: AgentIdentity.slug` |
| Cairn registration host | `vm101` |
| Cairn registration status | `active` |
| Cairn registration role | `producer` |

---

## Variable Inputs

Danny must supply the following fields before any action proceeds. All fields must be confirmed before Step 1 completes.

| Field | Format constraint |
|---|---|
| `projectName` | Human-readable display name, e.g. `"Agent Dashboard"` |
| `projectId` | Kebab-case; must match `/^[a-z][a-z0-9-]+[a-z0-9]$/`; becomes LORE `projectId` and DDR path prefix |
| `repoDescription` | One sentence; passed verbatim to `gh repo create --description` |
| `visibility` | Exactly `public` or `private` — no other values accepted |
| `projectContext` | One paragraph: what does this project own, build, or solve? Passed verbatim into the HOMELAB-CLAUDE.md.template project context placeholder. |
| `repoName` | Derived: equals `projectId` — the GitHub repository name under `dannySubsense/`. Not collected from Danny. |
| `agentName` | Declared by the executing agent during Step 2 (vision quest) — NOT collected from Danny upfront; agent proposes, Danny confirms |

---

## Pre-flight Already-Bootstrapped Detection — Early Pass

**Editorial note — polarity inversion:** These four checks use the same four-field bullet format as the existing Pre-flight Validation Checks 1-5 below (`- **Command:**` / `- **Pass condition:**` / `- **Severity:**` / `- **Failure message:**`), but the polarity is inverted: Checks 1-5 HALT on *failure* (a required tool/service absent or misconfigured); these checks HALT on *detection* (a prior bootstrap artifact present). So "Pass condition" below means "this sign of prior bootstrap is absent," and "Failure message" is the HALT message shown when the sign IS detected.

This early pass runs before Substep 1.1 (prompting) and before the existing Pre-flight Validation checks below — these four checks require no `InputBundle` field and are therefore the earliest-runnable signs of a prior `/new-project` bootstrap in the sequence. All four checks run unconditionally (no short-circuit on the first sign found) before the HALT message is constructed, so a combination of signs is never under-reported (see Combined-signs message below). Any sign detected HALTs immediately — no file is written, no command is run, and no step proceeds.

### Sign (a) — CLAUDE.md exists at project root

- **Command:** `ls CLAUDE.md`
- **Pass condition:** Exit code non-zero (file not found — no prior bootstrap sign)
- **Severity:** HALT
- **Failure message:** `CLAUDE.md already exists at <path>.` (`<path>` = the absolute path checked)

### Sign (b) — .git exists with at least one commit

- **Command:** `test -d .git && git log -1 --oneline`
- **Pass condition:** Exit code non-zero for the compound command. `.git` absent short-circuits `test -d .git` to non-zero (sign absent). `.git` present but zero commits makes `git log -1` itself exit non-zero (`git log` on a commit-less repo errors — this is the deliberate carve-out: a commit-less `.git`, e.g. from a manual `git init` with no bootstrap commit yet, does NOT HALT). Only both conjuncts true (`.git` exists AND has at least one commit) fails this pass condition.
- **Severity:** HALT
- **Failure message:** `.git already has <N> commit(s).` (`<N>` = the result of `git rev-list --count HEAD`, run only once this sign is confirmed present, to avoid a second failing `git` invocation on a commit-less repo)

### Sign (c) — DDR directory already exists (name-independent glob match)

- **Command:** `ls -d docs/specs/*-ddrs/ 2>/dev/null`
- **Pass condition:** Exit code non-zero, or zero matched paths (no DDR directory found under any project name)
- **Severity:** HALT
- **Failure message:** `A DDR directory already exists: <matched-path>.` (`<matched-path>` = the first matched path; if the glob matches more than one directory, each is listed per the Combined-signs message below). This is a name-independent glob match — NOT keyed to the current run's derived `InputBundle.projectId` — so it detects a DDR directory left by a prior bootstrap under ANY project name, not only the current run's.

### Sign (e) — docs/NORTHSTAR.md already exists

- **Command:** `ls docs/NORTHSTAR.md`
- **Pass condition:** Exit code non-zero (file not found — no prior bootstrap sign)
- **Severity:** HALT
- **Failure message:** `docs/NORTHSTAR.md already exists at <path>.` (`<path>` = the absolute path checked). Unlike `CLAUDE.md`, `docs/NORTHSTAR.md` is not gitignored, so this sign survives a target directory populated from a prior bootstrap's artifacts without git history (e.g. a GitHub tarball, `rsync --exclude=.git`) under a different project name than the current run.

### Combined-signs message

Within this pass, if more than one of signs (a), (b), (c), (e) is detected, surface a combined message listing every sign found — not only the first:

```
Bootstrap already detected — multiple signs found:
- CLAUDE.md already exists at <path>.
- .git already has <N> commit(s).
- A DDR directory already exists: <matched-path>.
- docs/NORTHSTAR.md already exists at <path>.
Resolve the existing state, or target a different directory, before re-invoking /new-project.
```

(Shown above with all four signs present — only the signs actually detected are listed, in fewer-than-four cases. If exactly one sign is found, surface that sign's Failure message verbatim instead of this combined form.)

---

## Pre-flight Validation

Pre-flight runs after Step 1 input confirmation and before Step 2 (vision quest). All five checks must complete before any write or system operation begins.

**HALT checks are blocking.** If any HALT check fails, execution stops immediately. No file is written, no command is run, and no step proceeds. Resolve the reported issue and re-invoke `/new-project`.

**WARN and NOTE checks are non-blocking.** Bootstrap may continue with the issue acknowledged.

---

### Check 1 — git installed

- **Command:** `git --version`
- **Pass condition:** Exit code 0
- **Severity:** HALT
- **Failure message:** `` `git --version` returned non-zero. Install git before running /new-project. ``

---

### Check 2 — gh CLI authenticated as dannySubsense

- **Command:** `gh auth status`
- **Pass condition:** Output contains `dannySubsense`
- **Severity:** HALT
- **Failure message:** `` `gh auth status` failed or shows account other than dannySubsense. Run `gh auth login` as dannySubsense. ``

---

### Check 3 — LORE gateway reachable

- **Tool:** `mcp__lore-gateway__check_health`
- **Pass condition:** Returns healthy status
- **Severity:** HALT
- **Failure message:** `` `check_health` failed. Verify lore-gateway MCP is registered and LORE DB is reachable over Tailscale. ``

---

### Check 4 — SSH alias configured

- **Command:** `grep -c "github.com-danny" ~/.ssh/config`
- **Pass condition:** Result ≥ 1
- **Severity:** WARN (non-blocking)
- **Failure message:** `SSH alias github.com-danny not found in ~/.ssh/config. Step 12 git push will fail. See MACHINE-SETUP.md SSH section to configure the alias before proceeding.`

---

### Check 5 — Switchboard available

- **Tool:** `relay_status` or `send_message` dry-run
- **Pass condition:** Responds without error
- **Severity:** NOTE (non-blocking)
- **Failure message:** `Switchboard unavailable. Step 3 Cairn registration will be surfaced as a pending action.`

---

## Step 1 — Input Gathering

Prompt Danny for the five InputBundle fields, validate each, confirm the bundle, and run a LORE collision check. No files are written and no commands run during this step.

### Substep 1.1 — Prompt for fields

Ask Danny to provide:

- `projectName` — human-readable display name (e.g. `"Agent Dashboard"`)
- `projectId` — kebab-case identifier (e.g. `"agent-dashboard"`); becomes the LORE `projectId` and DDR path prefix
- `repoDescription` — one sentence; passed verbatim to `gh repo create --description`
- `visibility` — exactly `public` or `private`
- `projectContext` — one paragraph describing what this project owns, builds, or solves; passed verbatim into the HOMELAB-CLAUDE.md.template project context placeholder

If Danny provides an empty string or whitespace-only value for `projectContext`, re-prompt for `projectContext` only. All other previously collected fields are retained. Repeat until a non-empty value is provided.

### Substep 1.2 — Validate projectId

Validate `projectId` against the regex `/^[a-z][a-z0-9-]+[a-z0-9]$/`. If the value does not match, re-prompt Danny for `projectId` only. Repeat until the value passes.

### Substep 1.3 — Validate visibility

Validate that `visibility` is exactly `public` or `private`. Any other value is invalid. Re-prompt Danny for `visibility` only. Repeat until a valid value is provided.

### Substep 1.4 — Confirmation gate

Present the complete InputBundle to Danny:

```
projectName:     <value>
projectId:       <value>
repoName:        <value>  (derived from projectId)
repoDescription: <value>
visibility:      <value>
projectContext:  <value>
```

Await Danny's explicit confirmation before proceeding. **No irreversible action proceeds until Danny confirms the full InputBundle.**

### Substep 1.5 — LORE projectId collision check

Call:

```
search_knowledge({
  query: InputBundle.projectId,
  projectId: "lore-personal",
  minSimilarity: 0.1
})
```

If any returned result references the same `projectId` in an existing project record, warn Danny and require explicit confirmation or an alternate `projectId` before proceeding.

### Substep 1.6 — Derive repoName

Set `InputBundle.repoName = InputBundle.projectId`. This is the GitHub repository name. No additional input from Danny is required.

---

## Pre-flight Already-Bootstrapped Detection — Post-1.6 Pass

**Editorial note — polarity inversion:** Same four-field bullet format and inverted polarity as the Early Pass above (HALT on detection, not on failure) — see that section's editorial note for the full explanation.

This check runs immediately after Substep 1.6 (repoName derivation) and strictly before the existing Pre-flight Validation Checks 1-5 execute and before Step 2 begins. It is the sole sign requiring a derived `InputBundle` field (`repoName`) and therefore cannot run any earlier than this point.

### Sign (d) — GitHub repo already exists

- **Command:** `gh repo view dannySubsense/<InputBundle.repoName>`
- **Pass condition:** Exit code non-zero (no existing GitHub repo found under this name — no prior bootstrap sign)
- **Severity:** HALT
- **Failure message:** `GitHub repo dannySubsense/<InputBundle.repoName> already exists.`

This is the sole remaining name-keyed sign — it is expected to be name-keyed since it checks specifically for a collision on the current run's derived repo name, unlike signs (a), (b), (c), (e) above, which are all name-independent and run in the Early Pass. This pass carries a single sign only and therefore never produces a combined-signs message.

---

## Step 2 — Vision Quest + Agent Name Confirmation

Propose and confirm the agent identity for this project. **No agent name may appear in any file, command, or payload until `AgentIdentity.confirmed = true`.**

### Substep 2.1 — Query the Agent Registry

Call:

```
search_knowledge({
  query: "Agent Registry registered agents",
  projectId: "lore-personal",
  minSimilarity: 0.1
})
```

If results are sparse, retry with `minSimilarity: 0.05`.

### Substep 2.2 — Extract existing names

Review all returned documents. Extract every existing agent name and slug.

### Substep 2.3 — Propose a name

Propose a short, lowercase agent name with full etymology explaining the name's meaning and rationale. The proposed name must not match any entry found in substep 2.2 (case-insensitive comparison).

### Substep 2.4 — Collision check loop

If the proposed name matches any existing registry entry: discard it, choose an alternative with a distinct etymology, and return to substep 2.3. Repeat until a collision-free name is found.

### Substep 2.5 — Present to Danny

Present the proposed name and etymology to Danny. Include a summary of the registry search results demonstrating uniqueness.

### Substep 2.6 — Await approval

Await Danny's explicit approval. Do not proceed until approval is given.

### Substep 2.7 — Handle rejection

If Danny rejects the proposed name, return to substep 2.3 and propose a new name with a distinct etymology.

### Substep 2.8 — Confirm identity

On Danny's approval, set `AgentIdentity.confirmed = true` and record:

```
AgentIdentity.name:        <approved name>
AgentIdentity.slug:        <same lowercase value — permanent author identifier>
AgentIdentity.relayHandle: <same as slug — case-sensitive on Switchboard>
AgentIdentity.etymology:   <approved etymology text>
AgentIdentity.confirmed:   true
```

**No agent name may appear in any file, command, or payload until `AgentIdentity.confirmed = true`.**

---

## Step 3 — Cairn Registration

Register the new agent with Cairn via the Switchboard relay. Registration is **non-blocking** — the bootstrap sequence continues regardless of outcome.

### Construct CairnRegistrationPayload

Build from `AgentIdentity` and `InputBundle`:

```
name:        AgentIdentity.name
authorSlug:  AgentIdentity.slug
relayHandle: AgentIdentity.relayHandle
projectId:   InputBundle.projectId
repo:        "dannySubsense/" + InputBundle.repoName
host:        "vm101"
status:      "active"
role:        "producer"
etymology:   AgentIdentity.etymology
```

### Send registration message

Call:

```
send_message({
  from:    AgentIdentity.slug,
  to:      "cairn",
  thread:  "registration",
  message: <structured text — see format below>
})
```

**Message format** (substitute CairnRegistrationPayload values for each `<field>` token):

```
New agent registration request:

Name: <name>
Author slug: <authorSlug>
Relay handle: <relayHandle>
Project ID: <projectId>
Repo: <repo>
Host: <host>
Status: <status>
Role: <role>
Etymology: <etymology>
```

### On success

Log: "Cairn registration sent."

### On failure (non-blocking)

If `send_message` fails for any reason, do not halt. Surface to Danny:

> SURFACE: Cairn registration pending — Switchboard unavailable. Send registration manually at next relay session.

Record this as a pending action in the session summary.

---

## Step 4 — CLAUDE.md Generation

Read the HOMELAB-CLAUDE.md.template, resolve placeholders, and write CLAUDE.md to the project root.

### Substep 4.1 — Read template

Read `~/.claude/templates/HOMELAB-CLAUDE.md.template` using the Read tool.

- **HALT if not found:** `Template not found at ~/.claude/templates/HOMELAB-CLAUDE.md.template. Verify the template deploy at ~/.claude/templates/ (source-of-record: agent-rig repo).`

### Substep 4.2 — Resolve placeholders

Substitute all placeholders using the following map:

| Placeholder | Resolved value |
|---|---|
| `<PROJECT-NAME>` | `InputBundle.projectName` |
| `<AGENT-NAME>` | `AgentIdentity.slug` |
| `<REPO-NAME>` | `InputBundle.repoName` |
| `<PROJECT-ID>` | `InputBundle.projectId` |
| `<One paragraph: what does this project own, what stack layer is it, how does it relate to the broader system.>` | `InputBundle.projectContext` |

**Implementation note — projectContext placeholder safety gate:** The token in the row above is a prose string, not `<ALL-CAPS-WITH-HYPHENS>`. Substep 4.3's zero-placeholder check does not match it. Apply these two checks explicitly:

1. Before substitution: verify the exact token string `<One paragraph: what does this project own, what stack layer is it, how does it relate to the broader system.>` occurs at least once in the template content read in Substep 4.1. If zero occurrences are found, the template has changed — **HALT:** `projectContext placeholder token not found in HOMELAB-CLAUDE.md.template. Template may have changed. Verify token and update Substep 4.2 before proceeding.`
2. After substitution: verify the exact token string no longer appears in the resolved content. If it still appears, the substitution failed — do not proceed to Substep 4.3 or Substep 4.4.

### Substep 4.3 — Zero-placeholder verification

Before writing, verify that zero placeholder strings of the form `<ALL-CAPS-WITH-HYPHENS>` remain in the resolved content. If any remain, the substitution is incomplete — do not write the file.

### Substep 4.4 — Write CLAUDE.md

Write the resolved content to `CLAUDE.md` in the project root using the Write tool.

### Substep 4.5 — Copy reference template

Copy `~/.claude/templates/HOMELAB-CLAUDE.md.template` to `HOMELAB-CLAUDE.md.template` in the project root. This reference copy is staged and committed in Step 12. Note: `CLAUDE.md` is gitignored by Step 7 and excluded from all commits.

---

## Step 4.5 — Northstar

**Editorial note:** Step 4 already ends with its own `Substep 4.5` (Copy reference template, above). This new top-level section is `## Step 4.5 — Northstar` — a different heading level and namespace (`Step` vs `Substep`), so there is no literal collision, but the coincidence is worth flagging so a future reader does not confuse "Substep 4.5" (Step 4's last substep) with "Step 4.5" (this new step).

Draft `docs/NORTHSTAR.md` from `InputBundle.projectContext` (collected in Step 1) and gate it on Danny's explicit confirmation before writing — thesis and drift-tripwires are judgment calls, not something to silently invent and commit. This step must complete before Step 5 begins.

### Substep 4.5.1 — Draft

Expand `InputBundle.projectContext`, `InputBundle.projectName`, and `InputBundle.repoDescription` into the four fixed sections owned by DDR-012 §3.1 (canonical schema — do not restate or redefine the section list here). Set `established` and `lastReviewed` to today's bootstrap date (same date value used in Step 13). Populate 2-4 concrete, project-specific Drift check tripwires — not generic placeholders. Do not paste `projectContext` unedited into every section.

### Substep 4.5.2 — Confirmation gate

Present the full rendered Markdown to Danny. Await explicit confirmation or edit — same posture as Substep 1.4. If Danny requests changes, revise and re-present; repeat until confirmed. Do not proceed to Substep 4.5.3 without confirmation.

### Substep 4.5.3 — Write

Write the confirmed content to `docs/NORTHSTAR.md` in the project root using the Write tool.

### Verify

Confirm `docs/NORTHSTAR.md` exists on disk before proceeding to Step 5.

---

## Step 5 — Relay Skill

**Precondition:** verify `docs/NORTHSTAR.md` exists before proceeding.

```bash
ls docs/NORTHSTAR.md
```

**HALT if the file does not exist:** `docs/NORTHSTAR.md not found. Step 4.5 did not complete successfully. Resolve Step 4.5 before proceeding.`

Create the `/relay` slash command for the new project using the inline template below. This file is staged and committed in Step 12.

### Inline relay.md template

Construct the content of `.claude/commands/relay.md` by substituting `AgentIdentity.slug` for every instance of `<AGENT-SLUG>` in this template:

```
Check the Switchboard relay for messages.

1. Call `read_messages({ agent_id: "<AGENT-SLUG>" })` — primary handle
2. If messages are waiting, read them and respond via `send_message({ from: "<AGENT-SLUG>", to: "<sender>", message: "..." })`
3. If inbox is empty, report: "No messages."

Keep responses concise and on-topic.
```

### Write

1. Create `.claude/commands/` directory in the project root if it does not exist.
2. Write the resolved content to `.claude/commands/relay.md` using the Write tool.

### Verify

Confirm no `<AGENT-SLUG>` placeholder remains in the written file. If any placeholder remains, the substitution failed — do not proceed.

---

## Step 6 — MACHINE-SETUP.md Generation

Read the MACHINE-SETUP.md.template, resolve placeholders, and write MACHINE-SETUP.md to the project root.

### Substep 6.1 — Read template

Read `~/.claude/templates/MACHINE-SETUP.md.template` using the Read tool.

- **HALT if not found:** `Template not found at ~/.claude/templates/MACHINE-SETUP.md.template. Verify the template deploy at ~/.claude/templates/ (source-of-record: agent-rig repo).`

### Substep 6.2 — Resolve placeholders

Substitute all placeholders using the following map:

| Placeholder | Resolved value |
|---|---|
| `<REPO-NAME>` | `InputBundle.repoName` |

### Substep 6.3 — Zero-placeholder verification

Before writing, verify that zero placeholder strings of the form `<ALL-CAPS-WITH-HYPHENS>` remain in the resolved content. If any remain, the substitution is incomplete — do not write the file.

### Substep 6.4 — Write MACHINE-SETUP.md

Write the resolved content to `MACHINE-SETUP.md` in the project root using the Write tool.

Note: `MACHINE-SETUP.md` is gitignored by Step 7 and must never appear in any commit.

---

## Step 7 — .gitignore Creation

Write `.gitignore` to the project root with exactly these 7 entries in this order, one per line:

```
CLAUDE.md
MACHINE-SETUP.md
.env
.env*.local
node_modules/
.next/
dist/
```

No entries may be omitted. Additional project-specific entries may follow but the seven above must appear first.

---

## Step 8 — Git Initialization

Execute the following 4 commands in sequence:

```bash
git init
git branch -m main
git config user.email "danny@subsense.art"
git config user.name "dannySubsense"
```

The `--global` and `--system` flags are prohibited in this step and in all git config calls throughout this command. git config must always be scoped per-repo.

Verification: run `git config --list | grep user` — output must show `danny@subsense.art` and `dannySubsense`.

---

## Step 9 — GitHub Repo Creation

Run:

```bash
gh repo create dannySubsense/<InputBundle.repoName> \
  --<InputBundle.visibility> \
  --description "<InputBundle.repoDescription>"
```

Error handling:

- HALT on any non-zero exit code — surface the exact gh CLI error to Danny.
- Name conflict special case: if the error indicates the repo name is already taken, present the error to Danny, accept an alternate repo name, update `InputBundle.repoName`, and retry this step once. All other errors: HALT without retry.
- On success: confirm the repo URL returned by gh CLI to Danny.

---

## Step 10 — SSH Remote Configuration

Run:

```bash
git remote add origin "git@github.com-danny:dannySubsense/<InputBundle.repoName>.git"
```

Verification: run `git remote -v` — output must show `origin` using the `github.com-danny` SSH alias.

If the remote add fails for any reason, HALT and surface the exact error to Danny.

---

## Step 11 — DDR Directory Bootstrap

Run:

```bash
mkdir -p docs/specs/<InputBundle.projectId>-ddrs/
```

Write `docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md` with this exact stub content (resolving `InputBundle.projectId` and `InputBundle.projectName` from the values confirmed in Step 1):

```markdown
# DDR Index — <InputBundle.projectName>

| # | Title | Status |
|---|-------|--------|
```

---

## Step 12 — Initial Commit and Push

Before staging, verify that the DDR index file created in Step 11 exists and that `docs/NORTHSTAR.md` exists:

```bash
ls docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md
ls docs/NORTHSTAR.md
```

**HALT if the file does not exist:** `DDR index file not found at docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md. Step 11 did not complete successfully. Resolve Step 11 before proceeding.`

**HALT if `docs/NORTHSTAR.md` does not exist:** `docs/NORTHSTAR.md not found at project root. Step 4.5 did not complete successfully. Resolve Step 4.5 before proceeding.`

`<InputBundle.projectId>` in the command above is a documentation placeholder — the executing agent substitutes the confirmed `projectId` value before running this command.

Stage exactly these five items — no others:

```bash
git add .gitignore HOMELAB-CLAUDE.md.template .claude/commands/relay.md docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md docs/NORTHSTAR.md
```

Run `git status` and verify that `CLAUDE.md` and `MACHINE-SETUP.md` appear as excluded (listed under gitignore-excluded files, not in the staged set). If either file appears in the staged set, do not commit — investigate and resolve before proceeding.

Commit with this exact message — no variation:

```bash
git commit -m "chore: project bootstrap"
```

Push:

```bash
git push origin main
```

Error handling:

- HALT on push failure. Do not retry silently. Report the exact error to Danny.
- If push fails with an SSH error, direct Danny to `MACHINE-SETUP.md` SSH alias setup section.
- The repo is left in a valid local-only state.

---

## Step 13 — LORE Bootstrap Capture

Construct and call:

```
capture_memory({
  projectId:     InputBundle.projectId,
  author:        AgentIdentity.slug,
  documentType:  "decision",
  epistemicType: "FACT",
  status:        "locked",
  content:       <narrative>
})
```

The content narrative must include at minimum: agent name, author slug, relay handle, etymology, workflow pattern (DDR → spec → forge), project roles (Composer: Danny, Producer: AgentIdentity.name, Frank: dispatched agent, `subagent_type: frank`), and bootstrap date.

If `capture_memory` fails, do not halt. Surface to Danny:

> LORE bootstrap capture failed. Re-run capture_memory manually before closing this session.

Record the pending action.

---

## Error Reference

### Halt Conditions

| Step | Condition | HALT message |
|------|-----------|--------------|
| Pre-flight | git not found | `git --version` returned non-zero. Install git before running /new-project. |
| Pre-flight | gh CLI not authenticated or wrong account | `gh auth status` failed or shows account other than dannySubsense. Run `gh auth login` as dannySubsense. |
| Pre-flight | LORE gateway unreachable | `check_health` failed. Verify lore-gateway MCP is registered and LORE DB is reachable over Tailscale. |
| Step 4 | HOMELAB-CLAUDE.md.template missing | Template not found at `~/.claude/templates/HOMELAB-CLAUDE.md.template`. Verify the template deploy at ~/.claude/templates/ (source-of-record: agent-rig repo). |
| Step 5 | `docs/NORTHSTAR.md` not found before Step 5 begins | `docs/NORTHSTAR.md not found. Step 4.5 did not complete successfully. Resolve Step 4.5 before proceeding.` |
| Step 6 | MACHINE-SETUP.md.template missing | Template not found at `~/.claude/templates/MACHINE-SETUP.md.template`. Verify the template deploy at ~/.claude/templates/ (source-of-record: agent-rig repo). |
| Step 9 | gh repo create fails | Exact gh CLI error surfaced. If name conflict: accept alternate name from Danny and retry. All other errors: HALT. |
| Step 10 | git remote add fails | Exact git error surfaced. |
| Step 12 | DDR index file not found before git add | `DDR index file not found at docs/specs/<InputBundle.projectId>-ddrs/00-DDR-INDEX.md. Step 11 did not complete successfully. Resolve Step 11 before proceeding.` |
| Step 12 | `docs/NORTHSTAR.md` not found before git add | `docs/NORTHSTAR.md not found at project root. Step 4.5 did not complete successfully. Resolve Step 4.5 before proceeding.` |
| Step 12 | git push fails | Exact error surfaced. If SSH error: direct Danny to MACHINE-SETUP.md. Repo left in local-only valid state. No retry. |
| Pre-flight (early pass, before Substep 1.1) | `CLAUDE.md` exists at project root | `CLAUDE.md already exists at <path>.` |
| Pre-flight (early pass, before Substep 1.1) | `.git` exists with ≥1 commit | `.git already has <N> commit(s).` |
| Pre-flight (early pass, before Substep 1.1) | Any dir matching glob `docs/specs/*-ddrs/` exists (name-independent) | `A DDR directory already exists: <matched-path>.` |
| Pre-flight (early pass, before Substep 1.1) | `docs/NORTHSTAR.md` exists at project root | `docs/NORTHSTAR.md already exists at <path>.` |
| Pre-flight (post-1.6 pass, before Checks 1-5 / Step 2) | GitHub repo `dannySubsense/<repoName>` already exists | `GitHub repo dannySubsense/<InputBundle.repoName> already exists.` |
| Pre-flight (early pass only — the post-1.6 pass has a single sign and cannot combine) | More than one sign detected within the same pass | Combined message listing every sign found in that pass — never only the first (see Early Pass Combined-signs message) |

### Non-blocking Failures

| Step | Condition | Surface message |
|------|-----------|-----------------|
| Step 3 | Cairn send_message fails | Cairn registration pending — Switchboard unavailable. Send registration manually at next relay session. |
| Step 13 | capture_memory fails | LORE bootstrap capture failed. Re-run capture_memory manually before closing this session. |

### Validation Loops

| Step | Condition | Action |
|------|-----------|--------|
| Step 1 | projectId is not kebab-case | Re-prompt for projectId only. |
| Step 1 | visibility is not `public` or `private` | Re-prompt for visibility only. |
| Step 1 | `projectContext` is empty or whitespace-only | Re-prompt for `projectContext` only. All previously collected fields retained. |
| Step 2 | Proposed name collides with registry entry | Discard name; propose new name with distinct etymology; repeat registry check. |
| Step 2 | Danny rejects proposed name | Propose new name with distinct etymology; repeat from Step 2.3. |
| Step 4.5 | Danny requests edits to the drafted Northstar | Revise draft per feedback; re-present; repeat until confirmed. No write until confirmed. |
