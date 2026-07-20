# DDR-003 — Public Surface & Contribution Model

- **Status:** DRAFT — pending Danny's review and a spec
- **Author:** wright
- **Date:** 2026-07-20
- **Sprint (on approval):** TBD — candidate slug `public-surface-and-contribution-model`
- **Supersedes:** —
- **GitHub issue:** —

---

## §1 Context

`agent-rig` is a **public** GitHub repo (`dannySubsense/agent-rig`, confirmed `PUBLIC` 2026-07-20). Its charter is composing/refining orchestration frameworks and releasing finished ones "into the world" — i.e. it is *meant* to face the community. But the same tree carries a **homelab surface** that must not: real internal hosts, `~/runtime/agent-lore` paths, the agent roster (wright/cairn/alpha/beta/lumen), LORE/Switchboard specifics, and internal DDRs that narrate private decisions.

This surfaced concretely during the DDR-014 template migration (2026-07-20): the tracked, public `HOMELAB-CLAUDE.md.template` hardcoded the LORE DB Tailscale host (the literal `<LORE_DB_HOST>` value, twice), and an archived report carried a second tailnet host — even though the authoritative, non-public copy of those values already lives in `~/runtime/agent-lore/.env` (gitignored), which the gateway actually loads from, and which the template's own line 62 says is the source ("Do not duplicate those credentials in this repo"). The hardcode was a promoted-default/shared-well duplication: one fact in two places, one of them public, free to drift. Precedent: agent-dashboard already ran a scrub commit (`5960a8f`) to remove this exact IP from its tracked docs; agent-rig never got that sweep.

**Immediate scrub already done (2026-07-20, this session), ahead of this DDR:** the two hosts were replaced with placeholders (`<LORE_DB_HOST>`, `<tailnet-host>`) plus pointers to `.env`. Verified zero internal IPs remain in tracked files. That closes the leak; this DDR is about the *system* so it doesn't recur and so the public/private boundary is deliberate rather than accidental.

## §2 Principle

Two different things share one tree and must be told apart:

1. **Community-valuable, already near-generic** — the orchestration packages (spec / forge / notebook / lit-synthesis), Frank, the Intake→spec→forge cadence, the DDR discipline. These are the contribution; the notebook package was already assessed as domain-agnostic by construction.
2. **Homelab surface** — real infra values, private paths, the agent roster, internal decision narratives. These are the reference implementation of *one* private homelab, not the product.

A homelab value is not lost by being scrubbed from the public tree — it is **relocated to its single non-public source of truth and resolved at use time**. The reason values were persisted in the template (zero-friction redeploy) is preserved by resolution-at-bootstrap, not by hardcoding-in-public. A secret (password, API key) belongs in `.env`/a vault; a non-secret infra *fact* (a host address) belongs in a single untracked config the bootstrap reads — neither belongs hardcoded in a tracked public file.

## §3 Decision (to build; details deferred to spec)

Commit to a **public-surface model with three mechanisms**, spec'd rather than decided offhand:

### 3.1 Placeholder + bootstrap-time resolution (preserves zero-friction redeploy)
- Tracked public templates carry placeholders (`<LORE_DB_HOST>`, etc.), never literals.
- `/new-project` **resolves** placeholders at bootstrap from the untracked source of truth — parse from `~/runtime/agent-lore/.env` (`DATABASE_URL`) for values that already live there, or a small non-secret `~/.homelab/infra.conf` for infra facts we want separate from secrets — and writes the real value into the *generated* per-project `CLAUDE.md`, which is gitignored. New projects get working values automatically; the tracked template never holds them.
- Single source of truth per value (anti-shared-well): a value lives in exactly one non-public place; the template references it, the bootstrap resolves it. No third copy.

### 3.2 Scrub gate (prevents recurrence)
- A pre-commit / CI check that blocks tracked files containing internal tailnet hosts (`100.64.0.0/10`), RFC-1918 addresses, known private paths, or roster names in template placeholders. Named owner: Wright. This is the enforcement surface that makes §3.1 hold under pressure rather than by discipline alone.

### 3.3 README + public/private demarcation
- The README frames the repo as **the frameworks** (what a visitor is here for), with the homelab specifics clearly demarcated as "reference implementation for one private homelab," not the product.
- Decide, at spec time, what stays in-tree-but-demarcated vs. what should be gitignored or moved private (candidate: internal DDRs that narrate private decisions, the live agent roster). Bias: keep the frameworks public and generic; quarantine the narrative/infra specifics.

### 3.4 Growth path (YAGNI-gated)
- The frameworks are already packaged directories — the natural unit to publish externally *if/when* there is a real community consumer (a separate public repo, or a marketplace, the way `ponytail` ships). Do **not** build a publish/sanitization pipeline until that consumer exists. §3.1–§3.3 are the now; this is the later.

## §4 Risks

| Risk | Mitigation |
|---|---|
| Scrub gate (§3.2) has false negatives — a new secret shape slips through | Gate is defense-in-depth over the §3.1 convention, not the only line; pattern list is owned and extended as new shapes appear |
| Bootstrap resolution (§3.1) reads a source that isn't present on some machine | `/new-project` already HALTs on a missing template; extend the same HALT posture to a missing resolution source rather than writing a broken placeholder into a real `CLAUDE.md` |
| Over-engineering the split before there's a community consumer | §3.4 is explicitly YAGNI-gated; the now is placeholder + gate + README, not a publish pipeline |
| Git history still contains the scrubbed IPs | Tailscale CGNAT hosts (not publicly routable) — low real exposure; history rewrite is a separate, heavier decision, flagged not assumed |

## §5 Open Questions

- Source of truth for non-secret infra facts: reuse `.env`, or a dedicated `~/.homelab/infra.conf`? — spec's call.
- Scrub-gate mechanism: local `PreToolUse`/pre-commit hook vs. CI check vs. both — spec's call, composes with the DDR-002 §3.4 hook work.
- What moves private vs. stays demarcated in-tree (internal DDRs, roster) — spec's call; needs Danny's steer since it touches how much of the decision trail is public.
- Whether to rewrite git history for the already-committed IPs, or accept the low CGNAT exposure and only prevent forward — Danny's call.
