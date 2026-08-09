# Cadence: Agent Rig

**Status**: Confirmed by Danny, 2026-08-09 — authoritative
**Derived from**: `CLAUDE.md` "Project Workflow Pattern," `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md`, this repo's own `spec-forge-cadence-refactor` sprint history (the sprint that produced the cadence being described)

## Phases

1. **Intake** (mandatory, always) — `docs/specs/<sprint-slug>/INTAKE.md`, requires `**Status**: APPROVED` (case-insensitive exact match) before any downstream doc generation. DDR is optional; Intake is not.
2. **Interview** (mandatory, always) — inline in the live session by default, using the `interview-conduct` skill's gap-diff + loop-until-dry procedure. Always produces `INTERVIEW.md`, even on zero gaps. Subagent fallback (`interview-conductor`) only when no live channel to Danny exists.
3. **`/spec-start`** — authors the sprint `NORTH-STAR.md` once (Locked at authoring, never re-edited mid-sequence), then delegates `01-REQUIREMENTS.md` → `02-ARCHITECTURE.md` → `03-UI-SPEC.md` (Step 5 is unconditional at the command level; skipping it for no-UI features is `@ui-spec-writer`'s own judgment — `ui-spec-writer.md:54` / `ui-specification/SKILL.md:150` — not a command-level branch) → `04-ROADMAP.md` → `05-REVIEW.md`, with an editorial fix loop on reviewer-found gaps before Frank's gate.
4. **Frank's binding spec-gate** (`LANE: spec-gate`) — Layer 1 (sprint North Star fidelity) and Layer 2 (project North Star relevance) both evaluated on every attempt, independent 3-attempt counter, no manual override. PROVISIONAL Layer 2 tag if `docs/NORTHSTAR.md`'s `Status:` field reads DRAFT at gate time. **Undefined-case rule, made explicit — fail-safe, not fail-open**: if `docs/NORTHSTAR.md` has no `Status:` field, that is not automatically a full pass. It is a full, non-PROVISIONAL pass only when the document carries an explicit confirmation marker in its place — e.g. `**Established:** <date>` with a recorded human-confirmation event (as agent-rig's own currently does, confirmed by Danny per its own history). Absent both a `Status:` field and any such confirmation marker, treat it the same as DRAFT: PROVISIONAL. An absent field is not itself evidence of confirmation — the marker is what earns the full pass, not the mere absence of DRAFT.
5. **Human approval** — full artifact set plus Frank's verdict presented together, including any PROVISIONAL tag.
6. **`/forge-start`** — HALTs if `docs/INVARIANTS.md`/`docs/CADENCE.md` are missing and this project has no source material to derive them from (otherwise: derive, present for confirmation, write once); HALTs if the sprint `NORTH-STAR.md` is missing. Implements slice by slice per `04-ROADMAP.md`, each slice ending in a commit to the git-flow-determined branch. `PROGRESS.md` is ground truth for sprint state, updated slice by slice.
7. **Frank's binding forge-gate** (`LANE: forge-gate`) — same two-layer, independent-attempt-counter design as the spec-gate, run once at implementation completion.
8. **PR / commit** — per this repo's Git Workflow (`CLAUDE.md`): PR/feature-branch flow, manual-push-only. DDR status (if one was used) updates to `ACCEPTED (shipped, PR #N)`.

## Non-negotiables carried into every phase

- One Frank gate per major phase (spec, forge) — not per-slice, not per-doc.
- Danny reviews and approves in the raw artifact, not a summary, for identity-tier docs (North Star, `agents/frank.md`).
- `PROGRESS.md` is verified against live files before a slice is marked complete — a partial checklist pass is not a pass.
- DDR stays optional; Intake does not.

## Provenance note

This cadence was itself produced by agent-rig's `spec-forge-cadence-refactor` sprint (shipped commit `b161781`, verified via `git log` — corrects a stale hash `0bf8a6f` inherited from `CLAUDE.md`, which is fixed in the same pass this file was drafted) — this file documents the pattern that sprint established as agent-rig's own standing practice, it does not introduce anything new.
