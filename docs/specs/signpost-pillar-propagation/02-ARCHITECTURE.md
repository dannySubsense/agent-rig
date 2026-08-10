# Architecture: Signpost→Pillar Propagation

**Status**: DRAFT — pending Frank spec-gate
**Author**: wright
**Date**: 2026-08-08

## Reference Implementation Provenance

**Source-of-record is agent-rig's own `reference/` directory** (`reference/session_probe.py`,
`reference/session-start-probe.sh`) — not a live dependency on any consumer repo's working tree or
branch state. This corrects an earlier draft of this document, which cited department-os's live
file paths directly; that citation broke when department-os's checked-out branch moved (Frank's
blind consistency review, 2026-08-08, caught the resulting dead-path defect). Per this repo's own
North Star thesis — orchestration mechanics are hardened once, centrally, not left to drift as each
consumer's own copy — the proven artifact belongs in agent-rig, not cited by reference to wherever
it happened to be piloted.

| Artifact | Piloted in (historical provenance, not a live dependency) | Now source-of-record at |
|---|---|---|
| `session_probe.py` | department-os (2026-08-07), itself generalized from market-data's `alpha`-authored, domain-coupled original | `reference/session_probe.py` (this repo) |
| `session-start-probe.sh` | department-os (2026-08-07) — includes the self-disclaimer text (US-3) and fail-loud-on-error (US-2) proven live there, ported unchanged | `reference/session-start-probe.sh` (this repo) |
| `.claude/settings.json` `SessionStart` block | department-os | Documented inline in Component 3 below (`matcher: "startup|resume|clear"`) |
| CLAUDE.md "Session Start Behaviour" (Signpost:/Pillar: convention) | department-os | Documented inline in Component 4 below |
| `assert_gate_date_coupling.py` | market-data (`alpha`) | Cited as external worked example only (Component 6) — not copied, market-data's own file remains that project's |
| `HANDOFF-2026-08-07-verify-before-assert-what-actually-works.md` | market-data (`alpha`), DRAFT | Cited as external source doctrine only (Components 5, 7, 8) — see US-9 gate, Component 10 |

market-data's own `session_probe.py` (DB-freshness-aware, project-specific) is **not** the
propagation source — it is domain-coupled (DuckDB tables, `STALE_DAYS` heuristic) and was itself
the input department-os's version was generalized from. `reference/session_probe.py` (this repo,
verified 2026-08-08 to run standalone with no department-os dependency) is the correct base because
it is already domain-neutral (git + docs only).

---

## Components

| Component | Responsibility | Location (propagation target) |
|---|---|---|
| 1. `scripts/session_probe.py` (generalized) | Read-only script; prints git branch/HEAD/dirty/ahead-behind, recent commits, `docs/*.md` listing. No project-specific DB/table logic. | `{new-project-scaffold}/scripts/session_probe.py`, templated into every new project's repo root |
| 2. `.claude/hooks/session-start-probe.sh` | Shell wrapper: runs the probe, wraps stdout+stderr into a self-disclaiming `additionalContext` JSON payload, always exits 0 (never blocks session start) | `{new-project-scaffold}/.claude/hooks/session-start-probe.sh` |
| 3. `.claude/settings.json` SessionStart wiring | Registers the hook against `matcher: "startup\|resume\|clear"` so it fires before the first assistant turn, ahead of the manual `search_knowledge` step | `/new-project` writes/merges this block during scaffold (Step 4-equivalent, alongside existing CLAUDE.md generation) |
| 4. Session Start Behaviour template block (Signpost:/Pillar:) | Documents the labeling convention and the 3-check pattern (LORE / Switchboard / git) as one merged block | `HOMELAB-CLAUDE.md.template` `## Session Start Behaviour` section |
| 5. Map-not-route briefing convention doc | Documents the checker-briefing template (objective + architecture + what's-claimed, structurally omitting method). **Documentation-only convention — does not claim any hook, lint rule, or CI gate enforces it (see Citation Constraints below).** | New template file: agent-rig repo root, `MAP-NOT-ROUTE-BRIEFING.md.template` (beside `HOMELAB-CLAUDE.md.template`), referenced from `HOMELAB-CLAUDE.md.template`. Deploys to `~/.claude/templates/` per Component 11 (Deploy Mechanism). |
| 6. `assert_*.py` convention doc | Documents the fail-closed exit-code convention, scoped to "when a coupling is known," with `assert_gate_date_coupling.py` as the worked example. **Documentation-only convention — no shared enforcement mechanism (e.g. no DDR-0009-style hook) exists or is claimed to exist; see Citation Constraints below.** | New doc: agent-rig repo root, `ASSERT-CONVENTION.md.template` (beside `HOMELAB-CLAUDE.md.template`; or a subsection inside `HOMELAB-CLAUDE.md.template` — see Open Decision D1). Deploys to `~/.claude/templates/` per Component 11. |
| 7. Capture schema addition (`Verification:`/`Re-verify with:`) | Adds two required lines to the Capture Behaviour section's guidance | `HOMELAB-CLAUDE.md.template` `## Capture Behaviour` section (edit existing) |
| 8. Sentinel/observability pattern doc | Documents "success and failure must produce different bytes" + alpha's F3 lesson. **Documentation-only convention, not an enforced mechanism; see Citation Constraints below.** | Same target file as Component 6 (bundled — see Rationale below) |
| 9. Retrofit audit procedure (per-project) | Per-project resident-agent-run blast-radius audit + cutover checklist template | New doc: `docs/specs/signpost-pillar-propagation/RETROFIT-PROCEDURE.md` (agent-rig-local; each resident agent copies/executes it in their own repo, does not import it as a dependency) |
| 10. Alpha's-report review record | Frank's independent review verdict on the handoff report (reviewer is Frank only, not Wright — doer=checker avoidance, since Wright authored this propagation architecture), gating which of its recommendations may be cited as settled | `docs/specs/signpost-pillar-propagation/ALPHA-REPORT-REVIEW.md` (distinct artifact from `05-REVIEW.md`, which is this sprint's own spec-gate review record) — **must exist and be referenced before Components 5/6/8 cite the handoff report as settled** (US-9) |
| 11. Deploy mechanism (source → `~/.claude/`) | Copies agent-rig's edited/new commands and templates (this sprint: Components 5/6's new template files, Component 4/7's edits to `HOMELAB-CLAUDE.md.template`) from their repo-root source-of-record to `~/.claude/templates/` (and `~/.claude/commands/` for any command edits), and verifies the copy landed correctly | Manual `cp` + diff verification, per the existing `commands/README.md` precedent ("Edit here, then redeploy — don't edit the installed copy directly") — no new tooling introduced; see Deploy Mechanism section below |

### Rationale: Components 6 and 8 bundled into one doc

The assert-convention and sentinel/observability doc are two closely related but distinct
disciplines (fail-closed pre-flight check vs. runtime distinguishable-artifact pattern). alpha's
report treats them as sibling sections (§2.2, §4) of one document. Bundling avoids a fourth
near-empty template file for two items with no independent scaffolding logic (pure documentation,
no hook/script to wire). If a future sprint needs to version them independently, split then —
YAGNI against speculative granularity now.

---

## Citation Constraints (per Component 10 / US-9 Gate)

Frank's review (`ALPHA-REPORT-REVIEW.md`) is a **conditional PASS**, not an unconditional one. Both
conditions are binding on every artifact this sprint produces or propagates (Components 4, 5, 6, 7,
8, and any downstream template/doc text derived from them — matching 01-REQUIREMENTS.md's
Cross-cutting AC/Constraint scope of US-4 through US-8 exactly):

1. **No DDR-0009 / hook-enforcement claims.** DDR-0009 (market-data) is `PROPOSED / QUEUED (not
   started)` — Frank confirmed no non-sample git hooks exist and `settings.local.json` carries no
   `hooks` key. The report itself flags this as its most valuable caveat: documented controls that
   don't exist on disk are the trap this sprint exists to avoid repeating. Accordingly:
   - Components 4 (Signpost/Pillar labeling), 5 (map-not-route briefing), 6 (`assert_*.py`
     convention), 7 (capture schema addition), and 8 (sentinel pattern) ship as **practice-only /
     documentation-only conventions** — text describing what an agent does
     by judgment at the point of use, never text implying a hook, lint rule, CI gate, or other
     automated mechanism enforces compliance. This is already this document's Pattern choice
     ("Documentation-as-convention (no enforcing code) for Components 4, 5, 6, 7, 8" — Patterns table
     above); this constraint makes explicit *why* it is non-negotiable, not merely a design
     preference.
   - No propagated template text may cite DDR-0009 or "hook enforcement" as an existing or
     retrofit-item-6 mechanism. Retrofit ordering (Retrofit Mechanism section, item 2) already
     excludes DDR-0009-style enforcement from this sprint's scope; this constraint additionally
     forbids *describing* it as present anywhere it might be cited.

2. **Section 2.5 ("repetition as diagnostic instrument") is a heuristic, not an established
   pattern.** Frank's review: "N=1, accidental, self-acknowledged" — the report itself says the
   discovery was "stumbled into, not designed." No component in this sprint currently cites Section
   2.5 (Components 5/6/8/9 draw on the report's §2.2, §4, §6, and Provenance section, not §2.5). If
   any future template edit, roadmap task, or retrofit artifact under this sprint does cite it, it
   must be labeled explicitly as "heuristic, not established pattern" in the citing text itself —
   never presented as a proven or recommended technique.

Both constraints trace to `docs/specs/signpost-pillar-propagation/ALPHA-REPORT-REVIEW.md` as their
source; that file is the source of record for these conditions, not this document. This section
exists so the conditions are architecturally enforced (checked against Components 5/6/8's actual
shipped text at roadmap/forge time) rather than living only as a note in a review doc that later
work could silently drift past.

---

## Probe Runtime Budget (Open Decision, resolved)

Requirements explicitly deferred a hard ceiling to architecture (Out of Scope: "NOT: Setting a
hard numeric probe-runtime-budget ceiling at the requirements stage — left to architecture per
Interview Q2, informed by alpha's ~3s precedent").

**Decision: 5s soft budget, PROVISIONAL, owner wright.**

- Basis: alpha's market-data `session_probe.py` measured ~3s in production use (cited in
  `HANDOFF-2026-08-07-*.md` §2.3 and Intake). Department-os's generalized version does strictly
  less work (no DuckDB queries, no pytest optional path) — git + doc-listing only — so 3s is
  already a conservative ceiling for the propagated version, not a floor to hit.
- 5s (not 3s exactly) is chosen as the enforced budget with headroom for slower disks/first-run
  git operations on retrofit targets, since those repos are unmeasured. This is a PROVISIONAL
  buffer multiplier, not itself sourced — **flagged as such**, owner wright, to be replaced with a
  measured number after the first `/new-project` scaffold run and the first retrofit are
  trace-verified (Component 3's hook always exits 0 regardless, so a budget miss degrades to a
  clearly-marked partial result — the hook captures the probe's actual exit status and injects an
  explicit "PROBE OUTPUT INCOMPLETE" marker into `additionalContext` on timeout or error, rather
  than silently presenting truncated output as a complete ground-truth snapshot — not a blocking
  failure, which is what makes a PROVISIONAL tag acceptable here rather than a hard requirement).
- Enforcement mechanism: a single `timeout 5 python3 scripts/session_probe.py` wrap at the
  hook-script level (Component 2) is sufficient and matches the existing exit-status-capture,
  fail-loud-but-non-blocking pattern in the department-os reference hook. The department-os
  reference's inner `_run()` helper also carries a per-subprocess `timeout=15` argument; that value
  can never fire (the outer 5s wrap always kills the process first) and is dropped in the
  generalized version — `subprocess.run(cmd, ...)` with no `timeout` kwarg, since the outer wrap is
  the sole enforcement point. Carrying a constant that can never trigger reads as a live guarantee
  it isn't; simpler to remove it than to document it as vestigial.

**Security/sandboxing constraint (Interview Q2, second half):** the probe performs read-only git
and filesystem operations only (`git rev-parse`, `git status`, `git log`, `Path.rglob`) — no
network calls, no writes, no elevated privileges. This matches the department-os reference exactly
and is preserved unchanged in generalization. No new sandboxing mechanism is introduced.

---

## Data Schemas

### Hook output contract (`additionalContext` JSON payload)

```typescript
interface SessionStartHookOutput {
  hookSpecificOutput: {
    hookEventName: "SessionStart";
    additionalContext: string; // see composition rules below
  };
}
```

`additionalContext` composition (all four elements required, in this order — matches the
department-os reference verbatim, generalized only in the wording that references project name):

1. Self-disclaimer preamble — states this is NOT LORE/memory priming and does not satisfy the
   Session Start Behaviour's `search_knowledge` step (US-3).
2. Probe output (raw stdout+stderr from `session_probe.py`, or the literal string
   `"probe failed: <error>"` if the script errored/timed out — US-2).
3. A trailing blank-line-separated block.
4. Action-required directive naming `search_knowledge` explicitly as the still-pending step (US-3).

### Capture schema addition

```typescript
interface DurableCapture {
  // ...existing fields per this repo's Capture Behaviour section (documentType, epistemicType, status, supersedesId)...
  verification: string;   // "Verification:" line — what was checked, by what method, when
  reverifyWith: string;   // "Re-verify with:" line — exact command/query a future session runs
}
```

Both fields are **required** on every durable capture per US-6; guidance change only (LORE's
capture API/schema itself is owned by `agent-lore`, out of this repo's lane per this repo's own
CLAUDE.md — this sprint changes the *documented convention* agents follow when calling
`capture_memory`, not the underlying MCP schema).

### Retrofit audit record (per project, Component 9's output)

```typescript
interface RetrofitAuditRecord {
  project: string;                  // e.g. "market_data"
  residentAgent: string;            // e.g. "alpha"
  blastRadius: {
    docReferences: string[];        // files referencing the old variant
    scriptCallSites: string[];      // files invoking the old variant
    priorVariantPaths: string[];    // e.g. "scripts/major_tom_probe.py" (Cairn's variant)
  };
  cutoverComplete: boolean;
  priorVariantRemoved: boolean;     // must be true, not "coexisting" — US-10
  frankGateVerdict: "PASS" | "FAIL" | "HALT";
  frankGateUnbriefed: boolean;      // must be true — map-not-route, US-10
  traceVerification: string;        // pointer to the stream-json trace / grep evidence, not prose
}
```

Not a formal database table — this is the shape of the retrofit completion note each resident
agent captures to LORE at cutover. **LORE is the single authoritative location**, not a project's
own `PROGRESS.md` — a per-project file is not centrally searchable across the 8 retrofit-target
repos, while a LORE capture is discoverable via `search_knowledge` from any project. Specified here
as a schema so every resident agent's cutover record is comparable and audit item completeness is
checkable (per US-10's five ACs).

---

## API Contracts

### `session_probe.py` (generalized)

```python
def _run(cmd: list[str]) -> str:
    """Run a subprocess with cwd=REPO, no inner timeout kwarg; return stdout or
    '<error: ...>' string. Timeout enforcement is the hook wrapper's job (outer `timeout 5`,
    Component 2) — an inner per-subprocess timeout would be strictly redundant and unreachable."""

def section(title: str) -> str:
    """Format a section header line."""

def main() -> None:
    """Print git state (branch, HEAD, dirty count, ahead/behind), recent commits (-8),
    full git status, and docs/*.md listing, to stdout. No return value, no exit code
    signaling (errors are embedded as '<error: ...>' strings, matching the department-os
    reference — the hook wrapper, not the probe script, owns fail-loud injection into
    additionalContext)."""
```

No project-specific parameters. Projects needing domain-specific freshness checks (DB tables,
cron logs — like market-data's original) add those as a *separate*, project-owned probe extension
invoked after this generalized one, not by parameterizing this script. This preserves "generalized
(not market-data-specific)" per US-1's AC while not forbidding projects from layering their own
richer checks on top.

### `.claude/hooks/session-start-probe.sh`

```bash
# No arguments. Reads $BASH_SOURCE to locate REPO_DIR two levels up.
# Contract:
#   1. Runs scripts/session_probe.py with a 5s timeout (see Probe Runtime Budget above),
#      capturing stdout+stderr, "|| true" so a probe failure never aborts the hook.
#   2. Emits ONE line of JSON on stdout matching SessionStartHookOutput.
#   3. Always exits 0 — a broken probe is reported via the injected error text
#      (US-2), never via hook failure/silence.
```

### `assert_*.py` convention (documented contract, not a shared library)

```python
# Naming: assert_<coupling-name>.py, one file per known load-bearing coupling.
# Contract (per assert_gate_date_coupling.py, the worked reference):
#   - Exit 0 only on a confirmed, determinate match.
#   - Exit non-zero (via sys.exit(<message>)) on: mismatch, missing input,
#     ambiguous/indeterminate state, or any error resolving either side of
#     the comparison. NEVER default to a passing exit code when uncertain.
#   - No shared base class/framework — each script is self-contained and
#     reads its own sources of truth directly (matches the market-data
#     reference; introducing an abstraction here would be premature for a
#     convention with exactly one worked example so far).
```

---

## Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Hook always exits 0, errors surfaced via injected context text | Component 2 | Matches US-2's AC and department-os's live-verified reference exactly; a hook that can fail the session start is a worse failure mode than a hook that reports its own failure |
| Self-disclaiming injected context (explicit "NOT priming" + named next step) | Component 2 | Directly fixes the department-os incident (LORE capture `312c594f`) where undisclaimed context caused priming to be skipped twice — this is not a hypothetical design choice, it is a proven regression fix |
| Documentation-as-convention (no enforcing code) for Components 4, 5, 6, 7, 8 | Signpost/Pillar labeling, map-not-route, assert-convention, capture schema addition, sentinel pattern | These are practices applied by an agent's judgment at the point of use (labeling a doc, briefing a checker, spotting a load-bearing coupling, adding capture-schema guidance, designing a control) — not events with a fixed trigger a hook could intercept. Alpha's own §6 ranks these as "practice-only, zero engineering cost," and forcing a mechanical enforcement layer around them now would be exactly the DDR-0009 trap (a plan/wrapper with no proven need) this sprint exists to avoid |
| Resident-agent-owned retrofit, not centralized sweep | Component 9 | Per Interview Q3 follow-ups and Requirements US-10 — binding, not a preference; each project's blast radius is unknown to agent-rig and must be independently assessed by the agent who actually knows that repo |
| Independent unbriefed Frank gate per retrofit | Component 9/10 | Directly reuses the map-not-route pattern (Component 5) as the verification mechanism for Component 9 itself — the retrofit process eats its own dog food rather than inventing a second review pattern |
| PROVISIONAL tag with named owner for the one architecture-invented number (5s budget) | Probe Runtime Budget section | Per this repo's Decision Discipline — no fabricated constants; the 3s figure is alpha's citable precedent, the 5s enforcement wrapper is new and is tagged accordingly |

### Anti-Patterns (Do Not Use)

- **Parameterizing `session_probe.py` with project-specific flags** (e.g., a `--tables` flag like
  market-data's original): reintroduces domain coupling into the generalized artifact. Project
  -specific checks are a separate, layered script (see API Contracts above).
- **A shared Python base class/framework for `assert_*.py` scripts**: only one worked example
  exists; premature abstraction. Revisit only once 3+ independent `assert_*.py` scripts exist
  across the homelab and a real duplicated-logic pain point shows up.
- **A uniform retrofit propagation script run centrally by agent-rig**: explicitly excluded by
  Requirements Constraints ("Must not: Apply a uniform, one-size-fits-all propagation script") and
  Out of Scope.
- **Enforcing the map-not-route / assert / sentinel conventions via a lint rule or CI gate in this
  sprint**: not requested, not scoped (Requirements defines these as documented conventions);
  would be scope creep beyond what US-5/US-7/US-8's ACs ask for.

---

## Backlog Reconciliation (per Constraint: "must reconcile with, not duplicate")

### DDR-INDEX "Template tier: promote the 3-check session-start block" (2026-07-20)

**Folded in.** This backlog item's scope (LORE prime + Switchboard `read_messages` + git
fetch/status, promoted from agent-rig's own CLAUDE.md into `HOMELAB-CLAUDE.md.template`) is a
strict subset of Component 4's target section. Component 4 ships the Signpost:/Pillar: labeling
convention *and* carries this pre-existing backfill item into the same template edit, per Intake
open question 2's recommendation (Danny-approved: "Recommend absorbing the 3-check promotion").
Key property preserved per the backlog note: the Switchboard inbox check fires once at cold start,
not on compaction/mid-session — Component 4's template text keeps this framing unchanged from
agent-rig's own CLAUDE.md source.

### DDR-INDEX "Prevention layer: gap-lens pre-checks at doer + dispatcher" (2026-07-21, thread `gaplens-prevention`)

**Kept separate, not folded in.** Per Intake open question 2's recommendation (Danny-approved:
"keeping the prevention-layer item separate — it's framed as doer-layer prevention, a different
architectural surface than propagation/detection tooling covered here"): this sprint's Component 5
(map-not-route briefing) is a **detection** mechanism — it catches a bad assumption after it has
already been made, via an independent checker. The backlog item's scope is **prevention** —
stopping the bad assumption from being seeded at the doer/dispatcher layer in the first place, a
different point in the pipeline. Overlapping subject matter (both trace to the `gaplens-prevention`
thread and alpha's report), non-overlapping architecture. No component in this document addresses
doer/dispatcher-layer prevention; that remains a distinct future DDR.

---

## Retrofit Mechanism (Surface 2)

### Roster (reused as-is, per Constraint: "Assumes... reused as-is from DDR-INDEX's existing
backfill list")

`market_data`, `electric-blue`, `gap-lens-dilution`, `gap-lens-dilution-filter`, `ask-edgar-repo`,
`sonic-store`, `quant-foundry`, `runtime/agent-lore`. (`api-doc-scraper` excluded — separate
stale-reference fix, Out of Scope.)

### Ordering (US-10 AC, alpha §6 yield ranking)

1. **Practice-only items first** (Components 4, 5, 7 — Signpost/Pillar labeling, map-not-route
   briefing, capture schema): zero engineering cost, apply to every roster project immediately
   once each resident agent runs its own audit.
2. **Probe-hook rollout** (Components 1-3): piloted in exactly one retrofit-roster project before
   broader rollout, per alpha §6 ranking item 2 and Requirements Out of Scope's deferral of "items
   4-6 of the Intake's What Is Missing list." Candidate first pilot project: `market_data` — it
   already has alpha's own `session_probe.py` as a live-comparison baseline and alpha (as resident
   agent) already possesses the deepest context on this mechanism of any roster agent. This is a
   recommendation for the roadmap phase to sequence, not a binding assignment made here.
3. **Components 6, 8** (assert-convention, sentinel pattern): documentation-only propagation to all
   roster projects can proceed alongside step 1 (no engineering dependency), but *application* —
   writing an actual `assert_*.py` for a project's own known coupling — happens per-project, on
   that project's own timeline, "when a coupling is known" (per US-7's AC), not as a sprint
   deliverable to force couplings into existence.

### Per-Project Cutover Procedure (Component 9, `RETROFIT-PROCEDURE.md`)

Each resident agent, in their own repo, executes:

1. **Blast-radius audit** — grep own repo for: prior probe-style variant script paths (e.g.
   Cairn's Major Tom variant, beta/gaplens-SEC's), doc references to it (CLAUDE.md, specs, READMEs),
   and all call-sites (hook wiring, manual invocation instructions). Record per the
   `RetrofitAuditRecord` schema above.
2. **Install** the canonical Components 1-3 (or, for practice-only items, edit the project's own
   CLAUDE.md per Components 4/5/6/7/8's finalized template text) into the project's own repo — not
   a symlink or submodule reference back to agent-rig; each project owns its own copy, matching how
   `/new-project`-scaffolded projects receive it (author≠install-location, same pattern this repo's
   own CLAUDE.md already states for Frank/cross-cutting personas).
3. **Remove** the prior project-local variant entirely — script file(s), hook wiring, and every doc
   reference found in step 1. Full replacement, not coexistence (US-10 AC3).
4. **Trace-verify** cutover via live tool-call trace (`--output-format stream-json`, grep for the
   actual `session_probe.py`/hook invocation and, separately, for the `search_knowledge` call
   confirming priming still fires) — not response-text plausibility. This is the same bar
   department-os's own pilot was verified against.
5. **Dispatch an independent, unbriefed Frank gate** — the resident agent supplies Frank with
   objective + architecture (this document + Components 1-4's finalized text) and explicitly
   withholds their own step-1 audit checklist and step-2/3/4 completion notes, per the map-not-route
   convention this same sprint is propagating (Component 5) — the retrofit process is its own first
   dogfooding case. Frank's verdict (PASS/FAIL/HALT) is binding per this repo's existing Decision
   Discipline; no manual override.
6. **Record** the completed `RetrofitAuditRecord` (LORE capture, `documentType: "decision"`,
   `epistemicType: "FACT"`, with `Verification:`/`Re-verify with:` lines per Component 7 — this
   sprint's own capture-schema addition applies to its own retrofit records) before declaring that
   project's cutover done.

**Who invokes the Frank gate mechanically:** the resident agent dispatches Frank via
`subagent_type: frank` (this repo's existing pattern for spec/forge gates) from within their own
project's session, briefing per step 5 above. There is no new dispatch mechanism to build — this
reuses the existing Frank-dispatch capability already available in every homelab project's Claude
Code environment; the only new discipline is the map-not-route briefing content and the "not
sprint-substitutable" rule (US-10 AC4), both already fully specified.

---

## Deploy Mechanism (Component 11)

Every command/template this sprint edits or creates has its source-of-record at the agent-rig repo
root (`HOMELAB-CLAUDE.md.template`, new `MAP-NOT-ROUTE-BRIEFING.md.template`,
`ASSERT-CONVENTION.md.template`) — none of it is live until copied to `~/.claude/templates/`. This
follows the existing precedent already documented in `commands/README.md` for `/new-project`'s own
propagation under DDR-014: "Edit here, then redeploy — don't edit the installed copy directly."
No deploy script exists in this repo today (confirmed by listing `scripts/` this session — only
`scrub_gate.py`/`scrub-gate-allow.txt`, unrelated); the mechanism is a manual copy, same as
DDR-014's own rollout.

**Mechanism:**

1. `cp HOMELAB-CLAUDE.md.template ~/.claude/templates/HOMELAB-CLAUDE.md.template` (overwrite —
   this file already exists at the deploy target from prior sprints).
2. `cp MAP-NOT-ROUTE-BRIEFING.md.template ~/.claude/templates/MAP-NOT-ROUTE-BRIEFING.md.template`
   (new file at the deploy target).
3. `cp ASSERT-CONVENTION.md.template ~/.claude/templates/ASSERT-CONVENTION.md.template` (new file;
   or omitted if Open Decision D1 resolves to bundling into `HOMELAB-CLAUDE.md.template` instead).

**Verification (not asserted, diffed):** after each copy, `diff <source> <deploy-target>` must
report no differences. A deploy step that isn't diff-verified reproduces exactly the "documented
but not installed" failure mode (DDR-0009) this sprint exists to close — matching this repo's own
Decision Discipline (`PROGRESS.md` ground-truth verification requirement) applied to the deploy
artifact, not just the source edit. This diff check is the roadmap-phase deploy slice's Done-When
criterion, not a suggestion.

---

## Rollback: `/new-project` Scaffolding (distinct from Retrofit Rollback)

Interview Q1 answered rollback for **retrofits** to existing projects (roster of 8, prior-state
preservation matters there). This is the separate case: a **newly bootstrapped** project (via
`/new-project`, Components 1-3 scaffolded fresh) where the installed hook misbehaves post-bootstrap.

**Rollback:** remove `.claude/hooks/session-start-probe.sh` and delete the `SessionStart` block
from `.claude/settings.json`. This fully reverts the scaffold — no data migration is needed because
a freshly bootstrapped project has no prior probe/hook state to preserve or restore; the scaffold is
purely additive (new files, one new settings block), so removing what was added is complete
rollback by construction. `scripts/session_probe.py` may be left in place (inert with no hook
invoking it) or deleted alongside; either is a complete rollback, since the hook removal is what
stops it from running.

---

## US-9 Gate: Alpha's Report Review

Per Requirements Constraint ("Must not: Cite alpha's report's recommendations as settled guidance
in shipped artifacts before its independent review (US-9) completes") — **this architecture
document itself cites the report extensively** (Components 5, 6, 8, 9's ordering, the Probe Runtime
Budget's 3s precedent). This is permitted under Intake open question 3's approved resolution
("recommend in parallel — the report's core claims... were already filesystem-verified by alpha per
their Provenance section, and this Intake's own scope doesn't depend on unverified parts of the
report") — architecture may **design against** the report's claims, but the finalized templates
(Components 4-8's actual shipped text) must not go out as "settled" until Component 10's review
record exists. Review is performed by **Frank alone** (not Wright — Wright authored this
propagation architecture and is not an independent checker of it; doer=checker avoidance). This is
a **roadmap-phase gate**, not an architecture-phase blocker: the roadmap document must place
"Frank's review of alpha's report" before the "finalize and ship Components 5/6/8 templates" task,
and must not schedule template-ship before it.

**Status:** Component 10's review record now exists at
`docs/specs/signpost-pillar-propagation/ALPHA-REPORT-REVIEW.md` — Frank's verdict is **conditional
PASS ("SAFE TO CITE")** with two mandatory caveats. The gate is satisfied for citation purposes, but
the two caveats are binding constraints on how Components 5, 6, and 8 may cite the report — see
"Citation Constraints (per Component 10 / US-9 Gate)" below. This document's other citations of the
report (Component 9's ordering, the Probe Runtime Budget's 3s precedent) are unaffected — both rest
on claims Frank verified directly (session_probe.py timing, Provenance section spot-checks), not on
the two caveated items.

---

## Dependencies

No new library dependencies. All components are shell/Python (stdlib only, matching the
department-os and market-data references — `subprocess`, `pathlib`, `json`, `argparse`, `re`,
`datetime` — no new PyPI packages introduced). No changes to `~/.claude/commands/new-project.md`'s
existing dependency surface (git, gh CLI, LORE gateway, SSH — already-established pre-flight
checks) beyond adding two file-write steps (probe script + hook script) alongside the existing
CLAUDE.md/MACHINE-SETUP.md generation steps.

---

## Integration Points

- **`~/.claude/commands/new-project.md`**: gains two new scaffold steps, sequenced alongside the
  existing "Step 4 — CLAUDE.md Generation" / "Step 6 — MACHINE-SETUP.md Generation" steps — write
  `scripts/session_probe.py` and `.claude/hooks/session-start-probe.sh`, and merge the
  `SessionStart` hook block into the generated `.claude/settings.json` (a new artifact for
  `/new-project` — verify in roadmap phase whether `/new-project` currently writes any
  `.claude/settings.json` at all; if not, this is a new write step, not a merge). **Flagged for
  roadmap-phase verification**, not resolved here — architecture does not have confirmed knowledge
  of `/new-project`'s current `.claude/settings.json` handling and must not assume it exists.
- **`HOMELAB-CLAUDE.md.template`** (agent-rig repo root, source-of-record): `## Session Start
  Behaviour` section extended with Signpost:/Pillar: convention + 3-check block (Component 4);
  `## Capture Behaviour` section extended with `Verification:`/`Re-verify with:` requirement
  (Component 7); new cross-references to Components 5/6's standalone template docs
  (`MAP-NOT-ROUTE-BRIEFING.md.template`, `ASSERT-CONVENTION.md.template`, both also agent-rig
  repo root). All edits land at repo-root source; deploy to `~/.claude/templates/` is Component 11
  (see Deploy Mechanism below) — not part of this integration point.
- **Existing retrofit-roster projects' local CLAUDE.md files**: each is gitignored/local per this
  repo's own precedent (see DDR-INDEX's Decision Discipline backfill item) — retrofit is a
  per-project local-file edit, not a committed change pushed from agent-rig.
- **agent-lore's `capture_memory` MCP tool**: unchanged at the schema/API level (out of this repo's
  lane, per this repo's CLAUDE.md "Schema lifecycle is owned by agent-lore. Do not run migrations
  from this repo") — only the *documented convention* for what agents pass into the free-text
  fields changes.
- **Frank (`subagent_type: frank`)**: existing dispatch mechanism reused unchanged for both the
  sprint-level spec/forge gates and, per Component 9, each retrofit's independent per-project gate.

---

## Coverage Check

| Requirement | Component(s) |
|---|---|
| US-1 | 1, 2, 3 |
| US-2 | 2 |
| US-3 | 2 |
| US-4 | 4 |
| US-5 | 5 |
| US-6 | 7 |
| US-7 | 6 |
| US-8 | 8 |
| US-9 | 10, US-9 Gate section |
| US-10 | 9, Retrofit Mechanism section |
| Cross-cutting (no DDR-0009 state) | Every component ships as either fully working (1-4, 7) or explicitly documentation-only with a stated scope boundary (5, 6, 8) — none is a "planned hook, not installed"; Component 11 (Deploy Mechanism) closes the remaining gap between "edited in agent-rig" and "live at `~/.claude/`" with a diff-verified copy step |
| Cross-cutting (sourced numbers) | Probe Runtime Budget section (3s sourced + 5s PROVISIONAL/wright) |

---

## Open Items for Roadmap Phase

- **D1**: Whether Components 6/8 ship as one combined template file or two — left as an
  implementation-sequencing choice, not an architectural one (see Rationale note above).
- **D2**: Confirm `/new-project`'s current `.claude/settings.json` write behavior before Component 3
  is implemented as "merge" vs. "create new."
- **D3**: First pilot project for probe-hook retrofit (Component 1-3) — `market_data` recommended,
  not binding; roadmap/human approval confirms.
