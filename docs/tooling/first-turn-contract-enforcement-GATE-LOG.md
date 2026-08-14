# GATE LOG — first-turn-contract-enforcement

Verdicts transcribed verbatim from Frank's dispatches. The orchestrator does not paraphrase,
soften, or summarize a verdict into this file.

## Spec Gate

| Attempt | Date | Verdict | Findings Summary | Fix routed to |
|---|---|---|---|---|
| 1 | 2026-08-14 | **FAIL** | Layer 1 fail, Layer 2 pass (project NORTHSTAR Established 2026-07-17, non-DRAFT → no PROVISIONAL tag). **F1 (blocking):** §3.2/§3.3 chose `hookSpecificOutput.permissionDecision: "deny"` as the block signal. The binary binds `permissionDecision` inside a `hookEventName:"PreToolUse"` literal and guards its consumption on `=== "PreToolUse"`; its own help text states `decision: "block"` is the mechanism "for PostToolUse/Stop/UserPromptSubmit hooks (deprecated for PreToolUse, use hookSpecificOutput.permissionDecision instead)". As specified the hook would emit a payload Stop silently ignores — it would never block anything, while the track-record log recorded "deny" verdicts that had no effect. The prior draft's `decision: "block"` was correct; the revision reversed a right answer into a wrong one. **F2:** §3.1's `last_assistant_message` rests on the same method (string present in bundle → field assumed live on this event) and needs live verification, not `strings`. Everything else passed, explicitly: §4's deadlock ordering, §5.2/§5.3's corpus-grounded predicates, §7's PROVISIONAL propagation bar, §1/§8's honoring of Intake §4's limit. | @architect |

| 2 | 2026-08-14 | **PASS** | Layer 1 pass, Layer 2 pass (NORTHSTAR Established, non-DRAFT → no PROVISIONAL). F1 fixed document-wide, not cosmetically — Frank grepped for surviving `permissionDecision` references and found none; wrapper malformed-output definition correctly tightened. F2 resolved at evidence class 1 (live stdin capture). The three-class evidence standard is **applied, not merely asserted** — Frank audited for residual class-3 claims and found one: that a post-block Stop fires with `stop_hook_active: true`, which the live capture never observed (nothing blocked). It sits at class 2 (binary help text), is covered by AC #6 at forge, and is backstopped by §4.3's default-8 cap. Recorded as a forge-verification item, not a gate finding. Loop classification: SHRINKING. | — (PASS) |

### Attempt 2 — orchestrator's independent post-PASS review

Per the cadence, the orchestrator's own review must be capable of producing a finding Frank did
not. It produced one. **Frank's PASS stands and was not overridden** — this was routed as a fix on
a passed document, not as a re-gate.

**Finding: §6's track-record log was specified as git-tracked, written on every invocation.**
Verified against this repo's own machinery rather than reasoned about: `commands/lore-close.md:78`
derives the session-close capture's `dirty:` field from `git status --porcelain` being non-empty.
A git-tracked file appended on every `Stop` event would pin `dirty: true` permanently in every
future capture — and that field is read back by the SessionStart queue hook's `git-state:` block.
The artifact would have corrupted the state-carrying mechanism its own sibling sprint exists to
provide, and would conflict on every cross-branch merge in a repo that works on feature branches by
policy.

**Resolution (@architect):** the log is written to the working tree but `.gitignore`d, not
committed. §7's propagation review reads the working copy. Writing is unchanged, so §7's
denominator — total qualifying invocations, required to compute a false-positive rate rather than
a violation count — stays computable. Stated cost: no durability across a fresh clone, wiped tree,
or different machine; accepted because Intake §7 already scopes the hook to one repo and one
machine for the evidence-gathering window. Three alternatives were rejected in §6 with reasons tied
to §7. §12 gained the general lesson: any artifact writing into a repo that also runs the
close/inject machinery must be checked against `git status --porcelain` / `dirty:` / `git-state:`
observability, and is not clean merely because its own gate passed on its own terms.

**Empirically verified by the orchestrator, not accepted on report:** created the log file, marked
it ignored, ran `git status --porcelain` — the file did not appear; the only entry was the spec doc
under edit. The `dirty:` derivation is preserved.

**Carried to human approval per Frank's instruction:** this document's decision protocol reversed
twice in one day — `decision:"block"` → `permissionDecision` (producer error) → `decision:"block"`.
That churn is presented alongside the PASS rather than filed quietly here.

### Attempt 1 — root cause, recorded because it is not the architect's error

F1 originates with the **producer**, not `@architect`. The architect's own draft specified
`decision: "block"`. The producer verified that the strings `permissionDecision` and
`hookSpecificOutput` were present in the installed binary and instructed the architect to switch to
the wrapped form. The architect complied.

Frank's classification: *"the promoted-string cousin of the promoted default: a verification method
(grep the binary) valid for proving a constant exists was silently promoted to proving an event
honors a field."* The "second independent method" the producer cited as corroboration — a
byte-level scan after a shell grep — read the same bytes with a different tool. **That is one read,
not two, on the semantics question.**

The distinction that makes §4.3 sound and §3.2 unsound, both in the same document:

- `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8` was verified with surrounding **code context** — the guard
  `if(_o>0&&ms>_o)`, the comparison, the telemetry call. It holds.
- `permissionDecision` was verified by **string presence alone**. It failed.

The document diagnoses this exact failure mode correctly in §4.3 and commits it in §3.2. The
standard adopted going forward (Frank's fix #3): a binary-sourced claim requires surrounding code
context showing the field is *consumed on this event* — presence in the bundle is not evidence.

**Producer's independent re-derivation of F1:** confirmed. Located the binary's help text directly
(`decision` — "block" for PostToolUse/Stop/UserPromptSubmit hooks, deprecated for PreToolUse) and
agree with Frank without reservation. No independent FAIL beyond his two findings.

**Gate independence note, disclosed to Frank in the briefing:** several of this document's
strongest sections originate with the producer rather than `@architect` — the transcript-shape
findings, the binary-sourced hook fields, the corpus result, the block-cap demotion. Frank recorded
evidence independence as "degraded, disclosed" and re-derived the binary claims himself rather than
trusting either party.

## Forge Gate

| Attempt | Date | Verdict |
|---|---|---|
| 1 | 2026-08-14 | **PASS** — see verbatim dispatch below |

Verdict transcribed verbatim from Frank's dispatch, session `04a0945a-52f3-4af6-ac11-e57fb147a731`:

```
═══════════════════════════════════════════════════════════════════
FRANK'S VERDICT — first-turn-contract-enforcement (forge-gate, forge-lite)
═══════════════════════════════════════════════════════════════════

Findings:
- Pre-checks: Premise pass — the two load-bearing constants are handled correctly: the 5s timeout is PROVISIONAL-tagged with owner (wright) AND re-justified by direct measurement on this probe (167ms on 5.4 MB / 3203 records, ~30x headroom), not inherited from `session-queue.sh`'s non-transferring rationale; §7's 10-entry/2-day bar is PROVISIONAL with named owner, as the spec requires. Input pass — I opened the raw artifacts myself: the track-record JSONL (11 lines, schema key-set matches §6 exactly, QC injections attributable by `sid=qc2`, harness fires attributable by real session ids), and the live-demo transcript itself (365 KB, marker present exactly once, first assistant text record opens "**Signpost** (claims from the queue capture, unverified until checked below):" — a genuinely compliant turn, independently confirmed against the probe's heading regex). Evidence independence pass — Slice 1's defect was caught by QC reading the real transcript, not the synthetic fixtures the doer wrote; the mutation test (kill `_extract_attachment_texts` → 8 failures) proves the suite detects the regression rather than sharing the doer's blind spot; and I re-derived the Slice 3 claim from the transcript, not from PROGRESS.md's narrative.
- Mirror: `diff scripts/first_turn_contract_probe.py reference/first_turn_contract_probe.py` — identical, drift-guarded. Wiring: `.claude/settings.json:19` Stop → wrapper, additive. `.gitignore:14` covers the log; `git check-ignore` confirms; porcelain shows only PROGRESS.md, not the log — `lore-close`'s `dirty:` semantics intact.
- Tests: 35 passed, executed by me, 0.12s. Wrapper fail-open validated by fault injection (AC 5) with the positive control PROGRESS names — a real C1 block passes through the wrapper unchanged, so fail-open is not fail-always.
- §11 AC 1–10: all satisfied. AC 4's live half is real: entry `2026-08-14T13:52:26Z`, session `04a0945a-…`, `queue_injected: true`, `first_turn: true`, `decision: allow`, and the transcript confirms C1/C2/C3 ran against an actual Signpost-then-Pillar turn with prior tool calls.
- Residuals, adjudicated individually: (1) probe_error lines writing `queue_injected:false`/`first_turn:false` as facts — acceptable; §6's schema mandates booleans, the direction is safe (errors accrue zero propagation credit), and the reviewer instruction is written down. Note for the §7 reviewer: an error rate cannot be computed as errors/qualifying-invocations — the denominator structurally excludes errors. (2) malformed-shape double-write — unreachable in the shipped probe (one stdout write, valid by construction), assumption stated at the exact code site (`first-turn-contract.sh:135–147`) with bounded consequence. Acceptable. (3) unreadable `transcript_path` ≡ not-injected — this is §5.1's own specified fail-toward-not-injected behavior; changing it would be a spec amendment, not a fix. Carrying it is correct. None of the three should have blocked.
- One gap worth a line, not a FAIL: an `allow` entry records no "Pillar was present" field, so the log alone cannot distinguish a compliant Signpost-then-Pillar turn from a headingless turn — AC 4's live half is only verifiable by opening the transcript, which I did and a §7 propagation reviewer must also do for the true-positive bullet. The log already can't satisfy §7's third bullet without transcript review anyway, so this changes reviewer workload, not the evidence bar.
- Layer 1: pass — every §11 criterion demonstrated by executed check, F1's restored `{"decision":"block","reason":...}` protocol implemented verbatim, §4.1 stop_hook_active checked first in `run()`, §4.2 fail-open at both probe and wrapper layers.
- Layer 2: pass, no PROVISIONAL — `docs/NORTHSTAR.md` exists, Established 2026-07-17, not DRAFT. This hook hardens the shared session-queue/FOOTER mechanism in the workshop repo, agent-rig-only deployment, propagation evidence-gated per §7 — squarely inside the "harden shared orchestration mechanics here before relying on them elsewhere" thesis, and its drift-check item 3 (propagation defined, not skipped) is explicitly satisfied by §7.

Why:
The failure mode this sprint kept flirting with — a hook that is inert in production while every test passes — surfaced twice (Slice 1's attachment-record miss, Slice 2's silent no-log error paths) and was both times caught by verification against real harness data rather than fixtures, then locked in with a negative control and a mutation test. That is the correct antidote to the shared-well pattern, executed, not narrated. The live demonstration is genuine: the qualifying entry comes from a fresh session, the transcript confirms the checks actually ran on a real first turn, and the QC injections are cleanly attributable and excluded. The residuals were named with their exact safe direction and bounded consequence, and each one is either spec-mandated behavior or unreachable-with-stated-assumption — none voids the work. The one thing the artifact has not yet demonstrated is a true-positive block under the live harness — but §7 already says exactly that: zero live true positives means propagation waits. The spec's own risk tolerance anticipated this state and gated on it; the sprint is not claiming otherwise.

Verdict: PASS

═══════════════════════════════════════════════════════════════════

Key files verified: `/home/d-tuned/agent-rig/scripts/first_turn_contract_probe.py`, `/home/d-tuned/agent-rig/.claude/hooks/first-turn-contract.sh`, `/home/d-tuned/agent-rig/reference/first_turn_contract_probe.py`, `/home/d-tuned/agent-rig/docs/tooling/first-turn-contract-track-record.jsonl`, `/home/d-tuned/agent-rig/tests/test_first_turn_contract_probe.py`.
```
