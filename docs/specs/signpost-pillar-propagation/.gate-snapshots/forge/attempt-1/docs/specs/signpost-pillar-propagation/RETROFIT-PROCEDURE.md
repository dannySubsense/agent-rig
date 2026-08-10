# RETROFIT-PROCEDURE.md

**Source of record:** `docs/specs/signpost-pillar-propagation/02-ARCHITECTURE.md` — Component 9,
Retrofit Mechanism (Surface 2) and Data Schemas sections.

**This is a copyable, executable checklist.** Each resident agent copies/executes this doc in their
own repo. **It is NOT imported as a dependency** — no symlink, no submodule reference back to
agent-rig. Each project owns its own copy, matching how `/new-project`-scaffolded projects receive
templates (author≠install-location, same pattern this repo's own CLAUDE.md already states for
Frank/cross-cutting personas).

---

## Ordering Rule

Per architecture's Retrofit Mechanism section, ordering (US-10 AC, alpha §6 yield ranking):

1. **Practice-only items proceed per-project immediately.** Components 4, 5, 7 (Signpost/Pillar
   labeling, map-not-route briefing, capture schema) have zero engineering cost and apply to every
   roster project immediately once each resident agent runs its own audit.
2. **Probe-hook items wait for the retrofit pilot's Frank-gate PASS.** Components 1-3 (probe-hook
   rollout) are piloted in exactly one retrofit-roster project before broader rollout. Do not begin
   probe-hook cutover in your own repo until the pilot project's Frank gate (step 5 below) has
   returned a PASS verdict.

---

## Per-Project Cutover Procedure (Component 9)

Each resident agent, in their own repo, executes the following six steps in order:

1. **Blast-radius audit** — grep own repo for: prior probe-style variant script paths (e.g.
   Cairn's Major Tom variant, beta/gaplens-SEC's), doc references to it (CLAUDE.md, specs, READMEs),
   and all call-sites (hook wiring, manual invocation instructions). Record per the
   `RetrofitAuditRecord` schema below.

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

## RetrofitAuditRecord Schema

Not a formal database table — this is the shape of the retrofit completion note each resident
agent captures to LORE at cutover. **LORE is the single authoritative location**, not a project's
own `PROGRESS.md` — a per-project file is not centrally searchable across the 8 retrofit-target
repos, while a LORE capture is discoverable via `search_knowledge` from any project. Specified here
as a schema so every resident agent's cutover record is comparable and audit item completeness is
checkable (per US-10's five ACs).

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

Fill in this shape as the LORE capture body when recording step 6 above.
