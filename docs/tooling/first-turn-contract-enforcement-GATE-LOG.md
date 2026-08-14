# GATE LOG — first-turn-contract-enforcement

Verdicts transcribed verbatim from Frank's dispatches. The orchestrator does not paraphrase,
soften, or summarize a verdict into this file.

## Spec Gate

| Attempt | Date | Verdict | Findings Summary | Fix routed to |
|---|---|---|---|---|
| 1 | 2026-08-14 | **FAIL** | Layer 1 fail, Layer 2 pass (project NORTHSTAR Established 2026-07-17, non-DRAFT → no PROVISIONAL tag). **F1 (blocking):** §3.2/§3.3 chose `hookSpecificOutput.permissionDecision: "deny"` as the block signal. The binary binds `permissionDecision` inside a `hookEventName:"PreToolUse"` literal and guards its consumption on `=== "PreToolUse"`; its own help text states `decision: "block"` is the mechanism "for PostToolUse/Stop/UserPromptSubmit hooks (deprecated for PreToolUse, use hookSpecificOutput.permissionDecision instead)". As specified the hook would emit a payload Stop silently ignores — it would never block anything, while the track-record log recorded "deny" verdicts that had no effect. The prior draft's `decision: "block"` was correct; the revision reversed a right answer into a wrong one. **F2:** §3.1's `last_assistant_message` rests on the same method (string present in bundle → field assumed live on this event) and needs live verification, not `strings`. Everything else passed, explicitly: §4's deadlock ordering, §5.2/§5.3's corpus-grounded predicates, §7's PROVISIONAL propagation bar, §1/§8's honoring of Intake §4's limit. | @architect |

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
