# Architecture — first-turn-contract-enforcement

**Status**: DRAFT
**Author**: architect (dispatched by wright)
**Date**: 2026-08-14 (revised same day — see §0)
**Intake**: `docs/specs/first-turn-contract-enforcement/INTAKE.md` (APPROVED 2026-08-14, Danny)
**Mode**: spec-lite — single document, no UI, bounded internal tooling.

---

## 0. Revision note

The original draft flagged two assumptions for forge-stage verification rather than resolving
them (§12 of that draft): the exact Stop-hook field names/decision protocol, and the transcript
JSONL shape. Both were verified before forge, against primary sources, on this machine:

- `strings` against the installed binary, `/home/d-tuned/.npm-global/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe` (Claude Code 2.1.232) — confirms the literal string *"For
  Stop/SubagentStop hooks, check stop_hook_active in the input and return success while it's true.
  Set CLAUDE_CODE_STOP_HOOK_BLOCK_CAP to raise this limit,"* independently re-run and matched
  verbatim.
- A real transcript, `~/.claude/projects/-home-d-tuned-agent-rig/cb179922-….jsonl`, and a real
  fixture extracted from it, `tests/fixtures/first_turn_contract_corpus.json`, both read directly.

Both checks changed the design: §3–§5 below are rewritten, not merely annotated. Where a prior
decision is being reversed rather than confirmed, this section says so explicitly rather than
letting the rewrite pass silently.

**Second addendum, same day**: the block-cap finding above was corroborated by a second,
independent method (a byte-level scan locating the exact source fragment, not just a `strings`
grep) and is a real citable constant, not PROVISIONAL. But its enforcement is conditional
(`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` disables it) and it is external to this hook, so §4 orders it
last, as a backstop, not first, as the guarantee — the guarantee is this hook's own unconditional
logic (`stop_hook_active` + wrapper fail-open). Presenting an environment-dependent control as the
primary safety claim was flagged as the promoted-default pattern from this project's founding
postmortem and corrected before this draft was reported complete.

---

## 1. Purpose and non-goals

**Purpose.** A `Stop` hook that inspects the first assistant turn of a session in which the
session-queue (`scripts/session_queue_probe.py`) was injected, and blocks that turn from
completing if it violates the FOOTER contract — order (C1), forbidden third section (C2), or
absence of a verifying tool-call trace (C3) — returning the specific violation as feedback so the
agent redoes the turn.

**Non-goals** (binding, per Intake §4/§5 — no acceptance criterion below may imply otherwise):

- Does **not** judge whether a Pillar claim is *true*. That is Frank's lane and the human's.
- Does **not** act on any turn other than the first of a queue-injected session.
- Does **not** retrofit other repos. Deployment is agent-rig-only (Intake §7); the artifact is
  built portable (`reference/` source-of-record shape) but not installed elsewhere.
- Does **not** modify the `SessionStart` hook, the probe, or the FOOTER text. This tool reads that
  contract; it does not author it.
- Does **not** catch a Pillar section whose *form* is correct but whose *content* is fabricated —
  C3 proves tool calls occurred, not that they targeted the claims being made. This limit is
  structural (§8 below), not a v2 gap.

---

## 2. Components

| Component | Responsibility | Location |
|---|---|---|
| `first_turn_contract_probe.py` | Reads Stop-hook stdin JSON + the session transcript, applies C1/C2/C3, emits the block/allow decision. Pure function of stdin (+ transcript, for C3 only); no LORE access, no network. | `scripts/first_turn_contract_probe.py`, mirrored source-of-record copy at `reference/first_turn_contract_probe.py` (same duplication discipline as `session_queue_probe.py`) |
| `.claude/hooks/first-turn-contract.sh` | Wrapper: captures stdin, replays to the probe under a timeout, validates output shape, fails open on any probe error. Structurally identical to `.claude/hooks/session-queue.sh`. | `.claude/hooks/first-turn-contract.sh` |
| Track-record log | Append-only record of every invocation's verdict, written by the hook itself. The evidence base §7's propagation standard is measured against. | `docs/tooling/first-turn-contract-track-record.jsonl` (repo-local, git-tracked) |
| `.claude/settings.json` `Stop` hook entry | Wires the wrapper into the `Stop` event, alongside the existing global `switchboard/relay-hook.js` entry (repo-local settings, additive — does not replace the global entry). | `.claude/settings.json` |

Three components, one wiring change. No new library dependency (§9).

---

## 3. The contract, mechanically

### 3.1 Hook event and stdin shape

Event: `Stop`. Verified against the installed binary (Claude Code 2.1.232), not documentation
alone. The JSON payload on stdin includes:

```typescript
interface StopHookInput {
  session_id: string;
  transcript_path: string;
  stop_hook_active: boolean;      // true iff this Stop cycle is already a continuation forced
                                   // by a prior block (this or another Stop hook) — confirmed
                                   // string in the binary, cited in §0
  last_assistant_message: string; // the full text of the assistant's most recent message —
                                   // i.e. exactly the turn text C1/C2 need to inspect. Confirmed
                                   // present on Stop-hook stdin; supersedes the prior draft's
                                   // "recover the turn text from the transcript" design (§5.1).
  // additional fields (cwd, hook_event_name, etc.) may be present; unused fields are ignored.
}
```

**Revision from the prior draft**: C1 and C2 operate on `last_assistant_message` directly. The
transcript (`transcript_path`) is no longer needed to find "the first turn's text" — it is needed
only for C3 (tool-call trace, §5.4), which `last_assistant_message` cannot provide. This is a
simplification the prior draft's own §12 anticipated verifying, and it removes an entire predicate
(§5.1's "first assistant record" logic) that turned out to be wrong on real data (§5.1 below).

### 3.2 Decision protocol (how "block" is communicated)

**Revision from the prior draft**: the prior draft offered `decision: "block"` as the mechanism
and separately noted exit-code-2 as a documented alternative, without picking one. Both
`permissionDecisionReason` and the wrapped `hookSpecificOutput` shape are confirmed present in the
installed binary. This document picks the wrapped shape — it is the same shape
`session_queue_probe.py` already uses for `SessionStart`, so both hooks in this repo share one
output convention, and it is unambiguous (no reliance on exit-code side-channels for the payload).
Exit-code-2 is not used.

```typescript
interface FirstTurnHookOutput {
  hookSpecificOutput: {
    hookEventName: "Stop";
    permissionDecision: "allow" | "deny";      // "deny" is this hook's block
    permissionDecisionReason: string;           // required when permissionDecision === "deny";
                                                 // names the check, quotes the exact triggering
                                                 // text, and states what to do
  };
}
```

On allow, the probe still emits this shape with `permissionDecision: "allow"` and a short
`permissionDecisionReason` (e.g. `"no queue-injection marker in this session"` or `"C1/C2/C3 all
pass"`) — an explicit allow, not silence, so the track-record log (§6) always has a real verdict
to write, and so "the probe ran and had no opinion" is distinguishable from "the probe crashed"
(handled entirely at the wrapper layer, §3.4).

`permissionDecisionReason` on deny must contain: which check fired (C1/C2/C3), the exact text span
that triggered it (quoted, not paraphrased), and one line telling the agent what to do ("re-emit
the turn with Signpost before Pillar" / "remove the third section; if a claim is genuinely
unverifiable, report it as a BLOCKER, not a to-do" / "run the verifying tool call(s) for the Pillar
claims before reporting them").

### 3.3 What "block" means mechanically

On `permissionDecision: "deny"`, Claude Code does not end the turn — it feeds
`permissionDecisionReason` back to the model as an instruction and lets it continue generating in
the same stop cycle. The next time the model tries to stop, the `Stop` hook fires again with
`stop_hook_active: true` on that pass (§4.1) — this hook allows unconditionally at that point, so
in the normal case there is no "keeps triggering denies" scenario to speak of. If some other Stop
hook (not this one) kept denying regardless, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` (default **8**,
confirmed in the binary, §4.3) is the runtime's own backstop ceiling — but that is a fact about the
platform's general safety valve, not a guarantee this design leans on (§4.3 explains why).

### 3.4 Wrapper responsibilities (`.claude/hooks/first-turn-contract.sh`)

Structurally identical to `session-queue.sh`:

1. Capture stdin to a temp file, replay it to the probe (the probe needs `transcript_path`,
   `session_id`, `stop_hook_active`, `last_assistant_message`).
2. Run the probe under a bounded timeout. **PROVISIONAL — owner: wright — 5s**, matching
   `session-queue.sh`'s existing outer timeout exactly (same class of operation: no network round
   trip — `last_assistant_message` needs no parsing beyond what's already on stdin, and the
   transcript read for C3 is one local file — so if anything this budget is generous relative to
   its precedent, not newly invented).
3. Validate stdout is either empty, or valid JSON matching `FirstTurnHookOutput`'s shape
   (`hookSpecificOutput.hookEventName === "Stop"` and `permissionDecision` ∈
   `{"allow","deny"}`). Anything else (non-JSON, wrong shape, non-zero probe exit, timeout) is
   treated as **probe failure**.
4. On probe failure: emit nothing (empty stdout, exit 0) — i.e. **fail open, silently allow the
   turn to stop**. `SessionStart`'s `additionalContext` is inert if wrong, but a `Stop` hook that
   emits a malformed `permissionDecision` risks corrupting the block/allow contract itself.
   Silence is the safe failure for a hook whose only power is to block. The wrapper still logs the
   failure to the track-record log (§6) so silent failures are visible in aggregate, just not
   injected into the transcript.

---

## 4. Deadlock safety (resolved, not deferred)

A blocking `Stop` hook that misfires can, in principle, prevent a session from ever finishing its
first turn. Three controls, ordered by **what we control and can vouch for unconditionally**, not
by which is numerically largest — an environment-dependent backstop is not the guarantee, per the
project's own promoted-default lesson (a value correct where it was born, load-bearing somewhere
it was never re-justified). The runtime cap is real and cited, but it is last, not first.

### 4.1 `stop_hook_active` — this hook's own restraint (primary guarantee, holds unconditionally)

If `stop_hook_active` is `true` on invocation, the probe **always allows** (`permissionDecision:
"allow"`) — it does not run C1/C2/C3 at all, regardless of `last_assistant_message`'s content.
Checked first in the probe's own logic, before any check runs. This bounds *this hook's*
contribution to a stop cycle to **at most one deny**, full stop — no environment variable, no
runtime configuration, and no external actor can change this behavior, because it is logic inside
our own probe, not a setting we depend on being left alone. This is the guarantee that holds
regardless of configuration.

### 4.2 Wrapper fail-open on any probe error (ours, holds unconditionally)

Independently of §4.1, any exception, timeout, or malformed-output condition inside the probe
results in the wrapper emitting nothing (§3.4 step 4). A probe bug that throws, hangs past the
timeout, or emits garbage cannot deny a turn — it can only fail to check one. Also entirely inside
code we own; nothing external can disable it either, short of editing the wrapper itself.

### 4.3 `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` — the runtime's backstop (not ours, environment-dependent)

Confirmed in the installed binary (Claude Code 2.1.232, §0), corroborated by two independent
reads — a `strings` grep and a separate byte-level scan locating the exact source fragment
`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8;if(_o>0&&ms>_o)return N("tengu_stop_hook_block_count",{...)` —
Claude Code stops honouring `deny` from Stop/SubagentStop hooks after a running count exceeds this
cap, default **8**, enforced behaviour (the surrounding code compares a live counter and emits
telemetry on trip), not a documentation claim.

**This is a backstop, not the guarantee this design leans on, for one specific reason found in the
same source**: the guard is `if (_o > 0 && ms > _o)` — the cap is enforced only when the configured
value is greater than zero. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=0` disables the engine's own deadlock
protection entirely, and any process in this environment can set that variable without touching
this hook, this repo, or even knowing this mechanism exists. A design that named this cap as *the*
guarantee would be exactly the promoted-default failure this project's CLAUDE.md names by name: a
value correct in the context it was built for (a general runtime safety valve, on by default) and
silently load-bearing somewhere its own disable condition was never re-examined.

**What this section is entitled to claim, precisely:** if §4.1 and §4.2 are both correct — and
they are ours to verify, not the environment's — this hook denies at most once per stop cycle and a
broken probe denies zero times, and §4.3 is never reached at all in the normal case. §4.3 matters
only as insurance against a bug in §4.1/§4.2 that this design does not currently believe exists,
and even then only in the default (non-zero) configuration. **The deadlock guarantee this document
makes is §4.1 + §4.2, full stop; §4.3 is additional insurance whose presence should not be relied
upon or cited as sufficient on its own.**

---

## 5. Detection predicates (complete v1 — no deferrals)

### 5.1 Identifying "the first turn of a queue-injected session"

**Revision from the prior draft**, on two points verified against real data (§0):

1. **Turn text comes from stdin, not the transcript.** The prior draft recovered "the first
   turn's text" by scanning the transcript for the first assistant record containing a text
   block. This was verified wrong on a real transcript
   (`~/.claude/projects/-home-d-tuned-agent-rig/cb179922-….jsonl`, 121 assistant records): **11
   assistant records precede the first text block** in that session — thinking and `tool_use`
   records come first, with no text content. Any predicate keyed to "the first assistant record"
   matches a thinking block, not the turn's prose. `last_assistant_message` on Stop-hook stdin
   (§3.1) is the turn's actual rendered text and needs no such reconstruction — this is not a
   heuristic, it is what the field already is.

2. **Queue-injection detection still requires the transcript**, because the injection happens at
   `SessionStart`, before any `Stop` event, and `last_assistant_message` covers only the current
   turn's text, not session-start context. The predicate: the transcript at `transcript_path`
   contains, at or before the first assistant record, an entry whose text contains the literal
   substring `"SESSION QUEUE — SIGNPOST, NOT PILLAR."` — the first line of `HEADER` in
   `scripts/session_queue_probe.py`. This string is emitted **only** on the success path (a tagged
   queue row was found and injected); the UNAVAILABLE/EMPTY/NO-TAGGED-QUEUE branches emit
   different text that never contains this substring.

   When scanning the transcript for this marker (and, for C3, for tool calls), filter to
   `isSidechain: false` records. Confirmed on the real transcript: `isSidechain` is a real field,
   `False` for all 121 records in that session (subagent dispatches live in a separate
   `<session-id>/subagents/` directory and would not normally appear at the top level regardless —
   filtering on `isSidechain` is a defensive, explicit check rather than relying solely on
   directory layout, per the same "verify against real files" discipline `session-queue-hardening`
   already applies to its own transcript-directory assumptions).

If the `HEADER` substring is absent anywhere in the (sidechain-filtered) transcript: **not
queue-injected**, probe allows unconditionally, no further checks run.

**"First turn"**, for the purpose of this hook: the turn currently ending, as given directly by
`last_assistant_message`. This hook fires on every `Stop` event; it only applies C1/C2/C3 when
(a) `stop_hook_active` is false (§4.1) and (b) the session is queue-injected (above) and (c) this
is the *first* `Stop` event of the session (i.e., the first turn) — tracked by checking whether any
assistant record with real text content precedes the current one in the transcript, filtered to
`isSidechain: false`. If an earlier non-thinking, non-tool-only assistant text record already
exists before the one `last_assistant_message` corresponds to, this is turn 2+ and the hook allows
unconditionally (per Intake §5, out of scope).

### 5.2 C1 — order

**Revision from the prior draft**: the heading predicate was designed around `#`-style markdown
headings. Verified wrong against the real corpus (`tests/fixtures/first_turn_contract_corpus.json`,
extracted from the session that produced the actual live violations): real headings are
bold-markdown, e.g. `**Pillar (verified this session, by method):**`, never `#`. A predicate
anchored on `#` would silently never fire. Rewritten below.

Within `last_assistant_message`, locate the first line (after stripping leading whitespace and
markdown emphasis markers — `#`, `*`) that, case-insensitively, begins with the word `Signpost` or
`Pillar` as the first word of the line, optionally followed by parenthesized qualifiers, and then
a colon — matching the real observed shapes `**Signpost:**`, `**Signpost (from the queue, not
re-checked):**`, `**Pillar (verified this session, by method):**`, and the plain `Signpost:` /
`Pillar:` case. Formally: the stripped line matches
`^(Signpost|Pillar)\b[^:\n]*:\s*\**\s*$|^(Signpost|Pillar)\b[^:\n]*:\s*\**\s*\S`
— i.e., the word starts the line (after markup-stripping) and is followed, before end of line, by
a colon that closes the heading label (trailing prose after the colon on the same line is
permitted, matching how the real corpus's headings run directly into their first bullet or
sentence).

- `S` = position of the first such Signpost heading, or `None`.
- `P` = position of the first such Pillar heading, or `None`.
- **C1 violates** iff `P` is not `None` and (`S` is `None` or `P < S`).

Validated against the corpus: `true_positive_c1_and_c2` opens directly with
`**Pillar (verified this session, by method):**` and contains no Signpost heading at all — `P` is
set, `S` is `None`, C1 correctly violates.

### 5.3 C2 — forbidden third section

Using the same heading-line predicate shape as §5.2 (line starts, after markup-stripping, with the
label text, followed by a colon), scan `last_assistant_message` for any heading line whose label
text, case-insensitively, matches:

```
^not\s+(yet\s+)?verified(\s+this\s+session)?\s*$
```

- **C2 violates** iff any such heading line exists.

**Empirically validated, not just reasoned about** (§0): every occurrence of the phrase "not (yet)
verified (this session)" was extracted across all 30 turns of the real session that produced the
defect (`tests/fixtures/first_turn_contract_corpus.json`). **Exactly one occurrence is in heading
form** — `**Not yet verified this session:**` in `true_positive_c2_heading`, the real violation —
**and six are inline prose** discussing the phrase (e.g. `"You're right. \"Not yet verified\" is
me reporting an unfinished job as a finding."`, and commit-message-style text about this very
spec, captured in `must_not_block_prose_mentions`). A substring scan would have flagged all seven;
the heading-line predicate flags exactly the one that is a real violation. This is the concrete
dataset behind the design brief's item 2 concern, not a hypothetical defense of it.

### 5.4 C3 — verification actually happened

Applies **only if C1's `P` is not `None`** (a Pillar section was asserted at all).

Parse the transcript (JSONL, `transcript_path`, filtered to `isSidechain: false`, per §5.1) for all
records **preceding** the current turn's assistant record (the one `last_assistant_message`
corresponds to), in this same session. Build the set of `tool_use` content blocks that have a
corresponding `tool_result` record (the call completed and produced a result — success or failure
of the underlying tool does not matter, only that it ran and returned).

**Excluded tool names**: `{"TodoWrite"}`. Todo-list bookkeeping is not verification of anything;
excluding it prevents C3 being satisfiable by a tool call that touches nothing external. No other
tool is excluded — a `Read`, `Bash`, `Grep`, `WebFetch`, or `mcp__*` call all count, because C3's
job (per Intake §3) is to prove tools ran, not to judge which tools are appropriate.

- **C3 violates** iff `P` is not `None` and the qualifying tool-call set (above) is empty.

**Why this cannot be satisfied by "any tool call whatsoever"**: it is in fact satisfiable by any
non-`TodoWrite` tool call — that is a deliberate, stated limit (§1, §8), not a hidden gap. What C3
rules out is the shape of the observed live failure: a turn that asserts a Pillar section while
the transcript shows zero tool invocations of any kind before it. It does not, and per Intake §4
cannot, verify that the tool calls that did run are the ones the Pillar claims describe.

---

## 6. Track-record log

`docs/tooling/first-turn-contract-track-record.jsonl`, one line per hook invocation (both the
wrapper's own failures and the probe's real decisions), append-only, git-tracked.

```typescript
interface TrackRecordEntry {
  timestamp: string;       // ISO 8601 UTC, wall-clock of the Stop event
  session_id: string;
  stop_hook_active: boolean;
  queue_injected: boolean; // §5.1 result; false short-circuits everything below
  first_turn: boolean;     // §5.1 result; false (turn 2+) also short-circuits
  decision: "allow" | "deny" | "probe_error";
  violations: Array<"C1" | "C2" | "C3">; // empty on allow
  reason: string | null;   // the exact permissionDecisionReason sent; null on probe_error
  probe_error: string | null; // exception class + message, only on probe_error
}
```

Written by the probe itself on every real invocation (including plain allows, per §3.2's explicit-
allow decision); the wrapper appends a `probe_error` line if it cannot even invoke the probe (e.g.
timeout killed it before it could write its own entry). This is a deliberate divergence from
`session_queue_probe.py`'s read-only discipline: that probe writes nothing because its job is
injection; this probe's job is judgment, and a judgment with no record of its own track is
unauditable and cannot support §7's propagation decision.

---

## 7. Propagation evidence standard (written down now, per Intake §7)

This binds *this* sprint's exit condition, not a future one. It must exist before the hook goes
live in agent-rig; it is written here, not left to a future reader.

**What is recorded**: every invocation, in `docs/tooling/first-turn-contract-track-record.jsonl`
(§6), for as long as the hook runs in agent-rig.

**What would constitute evidence for propagating beyond agent-rig** (per Intake §7, this sprint
does not decide to propagate — it defines what the evidence bar is):

**PROVISIONAL — owner: wright, no citable precedent exists (this mechanism has no prior instance
to benchmark against; the number is a judgment call, not a measurement).**

- At least **10** track-record entries with `queue_injected: true` and `first_turn: true`,
  spanning at least **2** distinct calendar days of real usage (not a single burst of manufactured
  test sessions), AND
- **Zero** entries where a `deny` decision's `reason` was later determined (by human review of the
  blocked turn) to have been a false positive — i.e., the blocked turn was in fact compliant with
  the FOOTER contract, AND
- **At least one** entry where a `deny` decision correctly caught a real violation (a turn that,
  absent the block, would have shipped Pillar-before-Signpost, a forbidden third section, or an
  unverified Pillar claim) — a hook with zero true positives has not yet been observed doing its
  job, only observed not misfiring, which is a weaker claim.

If 10 sessions pass with zero real violations to catch, the second bullet is trivially satisfied
and the third is not — propagation should wait for a true positive, not be inferred from an absence
of opportunity to fail. This mirrors this sprint's own stated standard for the FOOTER rewrite
(`session-queue-hardening-PROGRESS.md`, "Residual unknown": N=0 live fires is not evidence of
correctness).

This standard itself is revisitable by Danny at any time — it is PROVISIONAL, not locked — but it
must not be silently loosened by a future session that wants to propagate and finds the bar
inconvenient.

---

## 8. Integration boundary — what this tool does NOT get authority over

- **Truth of claims.** C1–C3 check form (order, section presence, tool-call existence). None of
  them evaluate whether a Pillar claim is factually correct, or whether the tool calls found by C3
  actually verify the specific claims in the Pillar section. That judgment remains with the human
  reading the turn, and with Frank's binding gates at the spec/forge level — this hook has no gate
  authority and is not a substitute for either.
- **Frank.** This tool runs at `Stop`, inside a session, on the first turn of a queue-injected
  session. Frank's binding spec/forge gates are a separate, human-facing judgment layer that this
  tool does not participate in, feed into automatically, or override.
- **Human judgment.** A human can always override, ignore, or re-litigate a block by reading the
  `permissionDecisionReason` and the transcript directly — that text is advisory to the *agent*
  continuing the turn, not a verdict binding on the human.
- **Any turn after the first.** Per Intake §5, this tool has no opinion on turn 2 onward in the
  same session, or on any turn in a session where the queue was not injected.
- **Other repos.** Per Intake §7, this design and its artifact are portable in shape but this
  sprint installs and enables blocking in agent-rig only; propagation is a future, evidence-gated
  decision (§7), not authorized by this document.

---

## 9. Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib (`json`, `re`, `sys`, `os`, `datetime`) | already used by `session_queue_probe.py` | stdin parsing, transcript parsing (C3 only), regex matching, JSON I/O — no new dependency |
| `bash` | already used by `session-queue.sh` | wrapper stdin capture, timeout, JSON validation |

No new third-party library. No network access, no LORE/Postgres dependency — this tool reads only
stdin and (for C3) the local transcript file.

---

## 10. Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Wrapper-invokes-probe-under-timeout, wrapper-owns-fail-open | `.claude/hooks/first-turn-contract.sh` → `scripts/first_turn_contract_probe.py` | Exact precedent: `session-queue.sh` → `session_queue_probe.py`. |
| Structural (heading-line) text matching over substring matching | C1, C2 (§5.2, §5.3) | Empirically validated (§5.3): 1 real heading-form violation vs. 6 inline-prose mentions in the actual defect session. Substring matching would have flagged all 7. |
| Hook-owned unconditional controls (`stop_hook_active` allow + wrapper fail-open) as the primary deadlock guarantee, runtime cap as backstop only | §4 | Our own logic holds regardless of environment configuration; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` is real and sourced but is disableable (`=0`) by an actor outside this hook's control, so it cannot be the guarantee — only insurance. No redundant counter is built on top of either. |
| `reference/` + deployed-copy duplication with a drift guard | `first_turn_contract_probe.py` | Matches the Slice-12 propagation shape (`commands/new-project.md:494`) already used by `session_queue_probe.py`. A drift test (mirroring `test_reference_copy_matches_executed_copy`) is required at forge time. |

### Anti-patterns (do not use)

- **Regex substring scan for "not yet verified" anywhere in the text.** Rejected — empirically
  shown wrong (§5.3: 6 of 7 real occurrences are non-violations).
- **`#`-style markdown heading detection.** Rejected — empirically shown to match nothing against
  real turn output, which uses bold-markdown headings (§5.2).
- **Reconstructing turn text from the transcript's assistant records.** Rejected — empirically
  shown wrong (§5.1: 11 non-text assistant records precede the first text block in a real
  session); `last_assistant_message` on Stop-hook stdin is the correct, direct source.
- **A stateful "have I already blocked this session" marker file as the deadlock escape.**
  Rejected — `stop_hook_active` (§4.1) already provides an unconditional, environment-independent
  guarantee that this hook denies at most once per stop cycle; a file-based counter on top of it
  would be a fabricated constant duplicating a mechanism Claude Code already gives us, and would
  introduce a new failure mode (a stale marker from a crashed prior run silently disabling the
  check forever).
- **Citing `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` as the deadlock guarantee.** Considered and rejected
  as the *primary* claim — it is real and sourced (§0/§4.3) but conditional on
  `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` being left at its non-zero default, an environment fact outside
  this hook's control. Kept as a documented backstop (§4.3), not cited as sufficient on its own.
- **Treating "any tool call ran this session" as satisfying C3.** Considered and narrowed to
  "before the current turn's assistant record, excluding TodoWrite."

---

## 11. Acceptance criteria

Mapped 1:1 to Intake §8's done-when list; none exceed the limit stated in §1/§8. Each references
the real corpus (`tests/fixtures/first_turn_contract_corpus.json`) where a fixture exists, per the
coordinator's requirement that this be tested against the actual failure that caused it.

1. Feeding `true_positive_c1_and_c2` as `last_assistant_message` produces `permissionDecision:
   "deny"` naming C1, quoting the Pillar heading and noting no Signpost heading precedes it.
2. Feeding `true_positive_c2_heading` as `last_assistant_message` produces `deny` naming C2,
   quoting `**Not yet verified this session:**`.
3. A `last_assistant_message` asserting a `Pillar` heading with zero qualifying (non-`TodoWrite`,
   completed) tool calls before it in the transcript produces `deny` naming C3.
4. Each of the four `must_not_block_prose_mentions` fixtures, and a compliant Signpost-then-Pillar
   turn with a qualifying tool call, produce `permissionDecision: "allow"` — demonstrated against
   the fixture corpus AND on a real live session, not the fixture alone.
5. Wrapper/probe failure (exception, timeout, malformed output) never denies — demonstrated by
   fault injection (a deliberately broken probe swapped in under test) producing an allow, not by
   code inspection alone.
6. `stop_hook_active: true` always allows regardless of `last_assistant_message` content —
   demonstrated by feeding a violating fixture twice, second time with the flag set, second call
   allows.
7. Artifact exists at `scripts/first_turn_contract_probe.py` and
   `reference/first_turn_contract_probe.py` (identical, drift-guarded) plus
   `.claude/hooks/first-turn-contract.sh`; `.claude/settings.json` wires `Stop` → the wrapper in
   agent-rig only.
8. `docs/tooling/first-turn-contract-track-record.jsonl` exists and gains one entry per real
   invocation once the hook is live, matching the schema in §6.
9. This document's §7 evidence standard exists (it does) before the hook is flipped live — i.e.
   before `.claude/settings.json` is edited to wire it in.
10. Every criterion above is demonstrated by an executed check attached to the claim (test run
    against `tests/fixtures/first_turn_contract_corpus.json`, fault-injection output, or a real
    observed session), not asserted by inspection.

---

## 12. Open items for the forge stage (not this document's to resolve)

- §0's verification covered `stop_hook_active`, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`,
  `last_assistant_message`, and the `hookSpecificOutput`/`permissionDecisionReason` output shape
  against the installed binary (2.1.232) directly. Re-verify against whatever Claude Code version
  is installed at forge/build time if it differs, the same way `CLAUDE_CODE_SESSION_ID` had to be
  flagged as induction-from-one-install in the sibling spec.
- The exact JSONL record shape used for C3's tool-call scan (which fields distinguish a `tool_use`
  block from its matching `tool_result`, and how `isSidechain` interacts with nested sub-agent
  transcript paths beyond the single session already inspected) should get one more direct check
  against a transcript containing a real Pillar-with-tool-calls turn during forge, since the corpus
  used here documents violations and prose-mentions but was not exhaustively checked for every C3
  edge case (e.g. a tool call that started before the turn but whose `tool_result` lands mid-turn).
