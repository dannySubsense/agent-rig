# INTAKE — first-turn-contract-enforcement

**Status**: APPROVED (2026-08-14, Danny) — §7 resolved: agent-rig-only, propagate on evidence
**Author**: wright
**Date**: 2026-08-14
**Mode**: full (not spec-lite — this ships a blocking hook to every repo)
**DDR**: none

---

## 1. What exists now, and why it is not enough

`feature/session-queue-injection` (head `23bf07d`, Frank forge-gate PASS) installs a `SessionStart`
hook that injects the LORE session queue labelled SIGNPOST, with a FOOTER instructing the reading
agent to work Signpost → Pillar, verify before reporting, and emit no third "not yet verified"
section.

**On its first live fire, 2026-08-14, the reading agent violated that contract three ways** —
reported Pillar before Signpost, closed with a "not yet verified this session" list, and did it
again after correction. The FOOTER was then rewritten to state the contract far more explicitly.

That rewrite is not a fix, and the sprint's own record says so: the three tests covering it pin the
*string*, not the *behaviour*, and it has N=0 live fires (`session-queue-hardening-PROGRESS.md`,
"Residual unknown"; Frank's gate: "this gate does not certify that the new FOOTER works").

**The deeper problem is that the rewrite repeats Slice 11, inside the sprint that dropped Slice 11.**
Slice 11 of `signpost-pillar-propagation` was DROPPED by Danny on exactly this reasoning: prose is a
*description* of a mechanism, not the mechanism — text has to be remembered to work, a hook fires
whether anyone remembers or not; "zero engineering cost" was the tell that there was zero mechanism.
Answering a behavioural failure with a longer paragraph in the same injected text is that rejected
move, one layer down. A better-worded request for compliance is still a request for compliance.

## 2. The problem, stated as a mechanism gap

There is a mechanism that *delivers* the contract (`SessionStart`). There is no mechanism that
*checks* it. The check currently lives entirely in the agent's willingness to comply with a
paragraph it read thousands of tokens ago — which is the failure mode the whole signpost/pillar
doctrine exists to name.

The two observed violations are both **textually detectable** in the turn that commits them:
ordering (a `Pillar:` section preceding a `Signpost:` section) and the forbidden third section (a
"not yet verified" / "not verified this session" tail). Neither requires judgment to spot.

## 3. What is proposed

A `Stop` hook, repo-local and portable, that inspects the **first assistant turn of a session in
which the queue was injected** and blocks the turn from completing if it violates the contract,
returning the specific violation so the agent redoes it — not a warning, not a log line.

Precedent that the surface works on this host: `~/.claude/settings.json` already runs a global
`Stop` hook (`switchboard/relay-hook.js`). The event fires and is wired today.

Three checks, in ascending order of what they can actually prove:

- **C1 — order.** A `Pillar` heading must not precede a `Signpost` heading. Pure text.
- **C2 — no third section.** A "not yet verified"-class tail is a violation. Pure text.
- **C3 — verification actually happened.** The hook receives `transcript_path`. Where the turn
  asserts a Pillar section, the session must contain real tool calls before it. This is the
  department-os lesson applied mechanically: verify by **tool-call trace, not response-text
  plausibility** (LORE `312c594f`, 2026-08-07 — a fix was confirmed only by grepping
  `--output-format stream-json` for the literal tool-call event, after response phrasing had
  looked plausible while the call was in fact missing).

## 4. The limit, stated up front rather than discovered at a gate

**C1 and C2 check the shape of a report. C3 checks that tools ran, not that they ran on the right
things.** None of them can catch a Pillar section whose claims are fabricated but whose form is
correct. This mechanism raises the floor; it does not certify truth, and no wording in the spec
should later imply it does.

That limit is acceptable because it is matched to the observed failures: both real violations this
session were violations of *form*, committed while every underlying fact was correct. But the limit
must be written into the artifact, because the failure mode of this sprint's ancestor was precisely
a control that defended one axis and was cited as if it defended another.

## 5. Explicitly out of scope

- Judging whether a Pillar claim is *true*. Frank's lane and the human's, not a hook's.
- Any turn other than the first of a queue-injected session.
- Retrofitting the seven repos. That is `signpost-pillar-propagation` Slice 12's lane; this sprint
  produces the artifact in the same `reference/`-source-of-record shape Slice 12 already propagates
  (`commands/new-project.md:494`) so it can be carried by that slice without redesign. Per §7,
  propagation is gated on an evidence record from agent-rig, not on this design being approved.
- Changing the `SessionStart` queue hook or the FOOTER again.

## 6. Decisions already made (producer, not open questions)

- **Portable from the start**, not repo-local-then-generalised. agent-rig exists to build things
  that propagate; a repo-local hook needing redesign for seven repos is the same work twice.
- **Blocking, not advisory.** An advisory check is a paragraph with extra steps. The one thing that
  distinguishes this from the dropped Slice 11 is that it fires and stops the turn.
- **Must never deadlock a session.** The hook fails open on its own error (same discipline as
  `session-queue.sh`: always exit cleanly, report its own failure in-context) and must not be able
  to block the same turn indefinitely. Exact escape is an architecture decision.
- **The FOOTER stays.** Delivery and enforcement are different jobs; this does not replace it.

## 7. Resolved by Danny, 2026-08-14 — blast radius

**Decision: block in agent-rig only. Propagate on evidence, not on design.**

The hook is installed and blocking in agent-rig alone. No other repo receives it in this sprint,
and no propagation is scheduled against a design review — the trigger for extending it is an
accumulated track record of it blocking real violations and not blocking compliant turns, in live
sessions, in this repo.

Two consequences that bind this sprint:

1. **Blast radius is one repo, and the fail-open discipline (§6) is still required inside it.**
   Scoping down is not a substitute for the hook being unable to deadlock a session; both hold.
2. **The artifact is still built in the `reference/` source-of-record shape (§5).** Building it
   portable costs nothing now and avoids a redesign later; what is withheld is *deployment*, not
   *portability*. The design is ready to travel; it does not travel until the evidence says so.

This is the same standard the sprint applies to itself elsewhere: `session-queue-hardening` refused
to label the queue hook LIVE on the strength of manual invocation, and its FOOTER repair is recorded
as unproven at N=0 live fires. A mechanism that enforces "verify before you assert" does not get
deployed fleet-wide on the assertion that it works.

**What counts as the track record is not defined here** — it is a spec-stage question (how many
sessions, what mix of blocked and passed turns, recorded where). It must be written down before the
hook goes live, not decided retrospectively when someone wants to propagate.

## 8. Done-when

- [ ] A first turn that reports Pillar before Signpost is blocked, with the violation named.
- [ ] A first turn carrying a "not yet verified" tail is blocked, with the violation named.
- [ ] A first turn asserting Pillar with no tool calls in the transcript is blocked.
- [ ] A compliant first turn passes untouched, and is demonstrated on a real session, not a harness.
- [ ] The hook's own failure never blocks a session — proven by fault injection, not by inspection.
- [ ] Artifact exists in the `reference/` source-of-record shape Slice 12 propagates, and is
      installed in agent-rig ONLY (§7) — no other repo touched by this sprint.
- [ ] The track-record standard that would justify propagation is written down before the hook goes
      live, not decided retrospectively.
- [ ] Every one of the above is demonstrated by an executed check attached to the claim.
