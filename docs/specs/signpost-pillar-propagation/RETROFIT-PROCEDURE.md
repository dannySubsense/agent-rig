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

   **2a. Verify the executable bit, then prove the probe actually ran.** The wrapper execs the probe
   directly (`timeout 5 "$REPO_DIR/scripts/session_probe.py"`). Installed without `+x` it dies with
   `Permission denied`, exit 126. The wrapper then degrades exactly as designed — exit 0, honest
   `PROBE OUTPUT INCOMPLETE` notice, no fabricated data — so session start is never blocked and
   **nothing looks wrong, while every session receives zero ground truth.** `/new-project`
   scaffolding sets the bit; retrofit into an existing repo is precisely the path that misses it.

   ```bash
   chmod +x "$REPO_DIR/scripts/session_probe.py"
   test -x "$REPO_DIR/scripts/session_probe.py" || { echo "FAIL: probe not executable"; exit 1; }
   ./.claude/hooks/session-start-probe.sh | tee /tmp/retrofit-probe-check.txt
   grep -q "PROBE OUTPUT INCOMPLETE" /tmp/retrofit-probe-check.txt \
     && { echo "FAIL: probe degraded — ground truth is empty"; exit 1; } \
     || echo "OK: probe returned complete output"
   ```

   Absence of the `INCOMPLETE` string is the pass condition. Do not substitute reading the wrapper
   source or observing that session start "worked" — both are true in the failure case.
   (Source: `alpha`, market_data Slice 10 pilot, 2026-08-12; Frank gate rider, same pilot.)

3. **Remove** the prior project-local variant entirely — script file(s), hook wiring, and every doc
   reference found in step 1. Full replacement, not coexistence (US-10 AC3).

4. **Trace-verify** cutover via live tool-call trace (`--output-format stream-json`, grep for the
   actual `session_probe.py`/hook invocation and, separately, for the `search_knowledge` call
   confirming priming still fires) — not response-text plausibility. This is the same bar
   department-os's own pilot was verified against.

   **Verify via the production invocation path, not a convenient equivalent.** A verification that
   does not use the same invocation shape production uses is not a verification. In the Slice 10
   pilot the implementer self-checked with `venv/bin/python scripts/session_probe.py` while the hook
   execs the probe directly — same script, same session, two invocation shapes, **opposite
   verdicts**: the interpreter path succeeded while the hook path died exit 126. A unit test would
   have mocked the hook and passed while the artifact was broken. Run what production runs.
   (Source: `alpha`, market_data Slice 10 pilot, 2026-08-12. This is the general rule; the step-2a
   exec-bit check is one instance of it.)

   **Park the trace artifact in-repo at `docs/reports/retrofit-<YYYY-MM-DD>/`** — a fixed,
   version-controlled location inside the retrofitted project, committed alongside the cutover.
   A session-scoped scratchpad path does not count: the trace must still be openable by the step-5
   Frank gate, which runs as a separate dispatch with no access to your session's scratch space.
   **A trace the gate cannot open is prose, not evidence** — the `traceVerification` field below
   demands a pointer to bytes. Include both the raw stream-json capture and the grep output.
   (Source: `alpha`, market_data Slice 10 pilot, 2026-08-12 — Frank rejected a scratchpad-resident
   trace as unverifiable at gate time; convention adopted from that pilot's own
   `docs/reports/retrofit-2026-08-12/`.)

   **If in-tree bytes are a problem for your repo, park them elsewhere and commit a pointer.** A
   raw trace runs ~100KB per capture; a repo with tighter size discipline or an established reports
   convention may not want that in-tree. Acceptable alternative: commit the **grep-evidence table
   plus a durable pointer** to where the raw bytes live, provided the step-5 gate can actually open
   them. The requirement is that the gate can reach the evidence — **not** that the bytes sit in
   this specific directory. What is never acceptable is a pointer only you can resolve.
   (Raised by `alpha`, 2026-08-12, from the pilot's own ~100KB trace.)

5. **Dispatch an independent, unbriefed Frank gate** — the resident agent supplies Frank with
   objective + architecture (this document + Components 1-4's finalized text) and explicitly
   withholds their own step-1 audit checklist and step-2/3/4 completion notes, per the map-not-route
   convention this same sprint is propagating (Component 5) — the retrofit process is its own first
   dogfooding case. Frank's verdict (PASS/FAIL/HALT) is binding per this repo's existing Decision
   Discipline; no manual override.

   **Expect your own reading of the architecture to be the thing most likely wrong.** This
   convention does not depend on you noticing your own gap — that is the entire point of it. In the
   Slice 10 pilot the coordinating agent had read the Components table and this procedure but not
   the API Contracts or Rejected Alternatives sections, then briefed an implementer with confident,
   specific, wrong instructions, and got exactly what was asked for: the anti-pattern named at
   `02-ARCHITECTURE.md:274-276`. Frank returned FAIL in round 1 **because the withheld checklist
   forced him to the architecture itself instead of inheriting that reading.** Briefed route-style
   ("here is what I did, confirm it"), he would have inherited the blind spot and stamped it.
   (Source: `alpha`, market_data Slice 10 pilot, 2026-08-12 — the convention's first validated
   catch.)

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
  probeExecutable: boolean;         // step 2a: `test -x` passed AND wrapper output carried no
                                    // "PROBE OUTPUT INCOMPLETE" — must be true
  frankGateVerdict: "PASS" | "FAIL" | "HALT";
  frankGateUnbriefed: boolean;      // must be true — map-not-route, US-10
  traceVerification: string;        // in-repo path, docs/reports/retrofit-<YYYY-MM-DD>/ — must be
                                    // committed and openable by the step-5 gate, not a scratchpad
}
```

Fill in this shape as the LORE capture body when recording step 6 above.
