# Aurora Internal Document Roster

> **Purpose:** Source of truth for `internal_status` and `internal_owner` of every Aurora-internal document. Read by `@corpus-curator` during inventory; populated into per-paper `metadata.json`. Without this lookup, aurora-internal papers ship with null status/owner and pass QC silently.

> **Owner:** Human-maintained. Update before running `/lit-synthesis-run` if new internal docs land.

> **Format:** Each row matches an aurora-internal slug (after curator's slugification). Status values: `active | archived | draft | superseded`. Owner: team or named individual.

---

## Roster

| Slug | Title | Status | Owner | Notes |
|------|-------|--------|-------|-------|
| aurora-liquidity-diastasis-curve-gat | Aurora Liquidity Diastasis Curve (GAT) | active | [team] | [optional context] |
| aurora-outlook-a-case-for-american-industrial-exceptionalism | Aurora Outlook: American Industrial Exceptionalism | active | [team] | |
| aurora-inflow-smart-dca-platform-gat-tf | Aurora Inflow Smart DCA (GAT/TF) | active | [team] | |
| | | | | |

---

## Default for unknown internal docs

If curator encounters a slug that triggers `aurora-internal` variant assignment but is NOT in this roster:

- `internal_status: unknown`
- `internal_owner: unknown`
- Curator logs the slug in the "Unrostered Slugs" section below for human triage.

---

## Unrostered Slugs (require human action)

| Slug | First seen | Action |
|------|------------|--------|
| | | |

---

## Lifecycle

- `active` — currently in use; relevant for ongoing strategy
- `archived` — historical, not in active use; preserved for reference
- `draft` — work in progress; not yet finalized
- `superseded` — replaced by a newer doc (note in Notes column)
