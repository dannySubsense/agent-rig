# UI Spec: first-turn-contract-c3-signpost-sourcing

## No UI Surface

This sprint has **no screens, no user flows, and no interaction surface**. It is a pure internal
enforcement-logic change confined to `scripts/first_turn_contract_probe.py`:

- The change modifies `check_c3_violation`'s subject-sourcing logic (adding Signpost-sourced
  subjects alongside existing Pillar-sourced subjects), extracts a new internal helper,
  `_extract_section_text`, adds two new extraction patterns (`_BARE_SHA_RE`/`_looks_like_sha`,
  `_DECISION_ID_RE`/`_looks_like_decision_id`) to `_extract_claim_subjects`, and mirrors every
  edit into `reference/first_turn_contract_probe.py` (see 02-ARCHITECTURE.md's Reference Mirror
  section).
- Per 01-REQUIREMENTS.md's Out of Scope section, this is explicitly not a new hook or script
  file — it is a change within existing functions in an already-existing probe script.
- The probe runs as a Stop-hook check against transcript data (stdin/JSON records) and produces
  a pass/violation decision consumed by the hook wrapper, not by any human-facing screen, form,
  dashboard, or CLI prompt introduced by this sprint.
- No new data schema, API endpoint, CLI flag, or output format is introduced (02-ARCHITECTURE.md
  confirms no new persistent data structures, no new files, no new libraries).
- Consumers of the probe's output (the existing Stop-hook mechanism and any existing
  track-record logging) are unchanged by this sprint — only the internal subject-sourcing
  computation that feeds the existing violation decision is modified.

## Why No UI Spec Is Applicable

The `ui-specification` skill's steps (screens, flows, layout, interactions, component hierarchy,
state visibility) all presuppose a human-facing interface. Nothing in 01-REQUIREMENTS.md's User
Stories or Acceptance Criteria describes a screen, form, view, or user-observable output beyond
the existing (unchanged) Stop-hook pass/fail behavior. 02-ARCHITECTURE.md confirms the change is
scoped entirely to internal functions (`_extract_section_text`, `_extract_claim_subjects` reuse,
`check_c3_violation`, `run`'s call site) with no new integration point outside the probe script
itself.

There is therefore no content to populate under Screens, User Flows, Layout Structure,
Interactions, Component Hierarchy, or State Visibility — inventing any of these would fabricate
UI structure that does not exist for this sprint, which this document deliberately avoids.

## Disposition

No screens defined. No user flows mapped. No HALT — this is not an ambiguity, it is a confirmed
absence of UI surface consistent with both prior spec documents.
