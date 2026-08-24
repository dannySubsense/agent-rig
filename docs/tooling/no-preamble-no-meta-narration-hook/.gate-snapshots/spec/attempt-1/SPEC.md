# no-preamble-no-meta-narration-hook — Tooling Spec (spec-lite)

**Status**: DRAFT
**Mode**: spec-lite (per `docs/tooling/no-preamble-no-meta-narration-hook/INTAKE.md` — no
Requirements/UI/Roadmap layering; this single document carries purpose, contract, and acceptance
criteria)
**Author**: architect (dispatched by wright)
**Date**: 2026-08-24

**Spec of record**: `docs/specs/agent-rig-ddrs/DDR-007-no-preamble-no-meta-narration-hook.md`.
**Governing thesis**: `docs/specs/agent-rig-ddrs/DDR-005-context-ratio-and-work-orders.md` §1 —
"rules that live as exhortations get performed; rules that live as failing checks get satisfied."
Third build in the hook-mechanization cluster, after DDR-006 (merged PR #11) and DDR-008 (merged
PR #13, live in agent-rig). **Intake**:
`docs/tooling/no-preamble-no-meta-narration-hook/INTAKE.md` (APPROVED 2026-08-24, Danny).
**Wrapper-shape precedent, reused verbatim, not redesigned**:
`docs/tooling/first-turn-contract-enforcement.md` §3.4/§4 and `.claude/hooks/first-turn-
contract.sh` — bounded timeout, fail-open on any internal error, append-only track-record log.
**File-layout precedent**: `docs/tooling/progress-md-proof-per-slice-hook/SPEC.md`.

---

## 1. Purpose

Mechanize this repo's own (and every sibling project's) already-stated, never-enforced prose
instruction — "don't narrate your internal deliberation" — by detecting, structurally, the pattern
of first-person meta-narration substituting for substance in an assistant turn: intent
announcements, stall-before-substance openers, honesty/ownership cushioning, praise padding,
performative-effort narration, emotional-state narration. Not a phrase-list filter (trivially
bypassed by rewording, per DDR-007 §3/Intake constraints) — a grammatical rule: subject "I"/"we" +
an internal/communicative verb, with no concrete noun in the same clause.

## 2. Non-Goals

- **Not a plain-language/jargon/"AI slop" vocabulary check.** That is DDR-011's separate hook,
  separate detection method (vocabulary/register-based, not grammatical-structural). No acceptance
  criterion below tests for jargon, verbosity, or register — per DDR-007 §3, mixing the two would
  make this hook's own false-positive rate unmeasurable during its soak.
- **Not a judge of whether a claim is true.** Structural pattern match only, same posture as
  `first-turn-contract-enforcement` C1–C3 (form, not truth).
- **Not a redesign of `first-turn-contract-enforcement`'s wrapper.** The bounded-timeout/fail-open/
  append-only-log shape is reused verbatim (§7 below); only the detection logic and trigger points
  specific to meta-narration are new.
- **Not an extension of `first-turn-contract-enforcement`'s existing `Stop` hook.** Ships as a
  fully separate sibling hook (§4 justifies this).
- **Not scoped to the first turn.** Unlike `first-turn-contract-enforcement`, this hook has no
  "first turn of a queue-injected session" gate — it applies (in whichever mode is active, §6) to
  every assistant turn, because meta-narration is not a first-turn-specific failure.
- **Not a blocking mechanism at v1 ship.** Starts observe/log-only (§6); promotion to blocking is a
  separate, evidence-gated future decision, not authorized by this document (mirrors
  `first-turn-contract-enforcement` §7's own posture toward propagation-beyond-agent-rig).
- **Not a retrofit-roster document.** Scope is agent-rig build only, this sprint (§9 confirms
  explicitly). Retrofit to sibling projects, if it happens, is tracked separately later, per the
  precedent `first-turn-contract-enforcement` and `progress-md-proof-per-slice-hook` both already
  set (agent-rig-first, propagation evidence-gated).
- **Not a general grammar/NLP engine.** Detection is regex/heuristic-based on the same class of
  structural text matching `first-turn-contract-enforcement` C1–C3 already use (heading-line regex,
  not a parser or ML model) — no new dependency (§10).

## 3. The Grammatical Rule, Concretely (resolves Intake Open Question 1)

### 3.1 Clause boundary

A **clause**, for this rule, is the run of text between two clause-boundary tokens. Clause
boundaries are: sentence-ending punctuation (`.`, `!`, `?`), a semicolon (`;`), a colon (`:`) that
is not part of a markdown heading label (see §3.4 for the heading-label exemption, reused from
`first-turn-contract-enforcement` §5.2's heading-line predicate shape), a coordinating conjunction
preceded by a comma (`, and`, `, but`, `, so`), or a line break. This mirrors the same "structural
text matching over substring matching" pattern already validated empirically in
`first-turn-contract-enforcement` §5.2/§5.3/§10 — clause-level, not full-message-level or
sentence-level-only, because a single sentence commonly mixes one narrating clause with one
substantive clause ("Let me check the config — `config.yaml` sets the timeout to 30s." has a
flaggable first clause and a clean second clause; message-level scanning would wrongly clear the
whole sentence on the second clause's concrete noun, clause-level scanning correctly isolates the
first).

### 3.2 Trigger pattern: subject + internal/communicative verb

A clause **matches the subject+verb pattern** iff, after stripping leading markdown emphasis
markers (`*`, `_`, `#`) and whitespace, it begins with one of the following case-insensitive
subject+verb sequences (the closed v1 verb set — enumerated, not open-ended, per Intake Open
Question 1's requirement for "a defensible enumeration ... not an ad hoc list masquerading as
one"):

```
I'll | I will | I'm going to | I am going to | I'm about to | I plan to | I intend to
I need to | I have to | I should | I want to | I'd like to | I would like to
I think | I believe | I feel | I realize | I recognize | I understand
Let me | Let's | Let us
I'm | I am        (only when immediately followed by one of: "going", "trying", "working on",
                    "doing", "starting", "looking")
To be honest | Honestly | Frankly
I apologize | I'm sorry | My apologies | I should have | I made a mistake
We'll | We will | We're going to | We are going to | We need to | We should
```

Each entry is matched as a whole-token sequence at clause start (word-boundary anchored), case-
insensitive, allowing one optional adverb between subject and verb ("I'll now check...", "I
should probably..."). This is the same class of enumeration `first-turn-contract-enforcement` §5.2
uses for heading labels (`Signpost|Pillar`) — closed, explicit, revisable by amendment (§11) if the
observe/log-only period (§6) surfaces a real pattern this list misses, not silently extended at
implementation time.

**Explicitly excluded from the verb set** (would over-match): "I found," "I ran," "I read," "I
wrote," "I changed," "I fixed," "I confirmed," "I verified" — these are past-tense report-of-
completed-action verbs, not internal-state/communicative-intent verbs; a sentence built on one of
these ("I confirmed the timeout is 30s in `config.yaml`") is exactly the substance-bearing
first-person statement §5 (Intake Open Question 3) requires this rule not to flag, and past-tense
completed-action verbs are structurally distinct from the future-intent/internal-state verbs
above — this exclusion is load-bearing for §5, not an oversight.

### 3.3 Neutralizing test: concrete noun in the same clause

A clause that matches §3.2 is **neutralized** (does not flag) iff the same clause (the same span
between the two clause boundaries identified in §3.1) also contains at least one of:

1. **A backtick-delimited code span** — `` `...` `` (matches `first-turn-contract-enforcement`'s
   own convention of quoting exact text spans, and code spans are definitionally concrete: a file
   path, identifier, or command).
2. **A file-path-shaped token** — a token containing at least one `/` or matching
   `\b[\w-]+\.(md|py|ts|tsx|js|json|yaml|yml|sh|txt|log)\b` (case-insensitive extension list).
3. **A capitalized multi-word or proper-noun token that is not the clause's first word** — a
   token beginning with an uppercase letter, appearing at position 2+ in the clause (excludes the
   trivial case of the sentence's own capitalized first word, e.g. "I" itself or a sentence-initial
   "Let"), and not one of the closed function-word list `{The, This, That, These, Those, It, A,
   An}`. Catches named entities: "the `DDR-007` spec," "Frank's gate," "the Stop hook."
4. **A digit sequence** — `\d+` anywhere in the clause (line numbers, version numbers, counts,
   thresholds — concrete by construction).
5. **A double- or single-quoted literal string** — `"..."` or `'...'` (a quoted term, error
   message, or literal value).

**Rationale for this five-way test, not a single rule**: Intake Open Question 3 names this as the
sprint's hardest design problem. A single concrete-noun test (e.g. "any capitalized word") would
both under-match (misses `config.yaml`, lowercase) and over-match (catches "I think Frank should
review this," where "Frank" is present but the clause is still pure narration with no
substance — see §5's worked counter-case below, resolved by clause-scoping in §3.1: "Frank should
review this" is itself a substantive imperative clause once boundary-split from "I think," so §3.1
already isolates the flaggable half correctly without needing the noun test to do that job alone).
Five independent concrete-signal classes, any one sufficient, mirrors defense-in-depth reasoning
already used in this repo (`first-turn-contract-enforcement` §4's layered, not single-point,
guarantees) applied to a detection question instead of a safety question.

### 3.4 Heading-label exemption

Reused verbatim from `first-turn-contract-enforcement` §5.2/§5.3: a colon that closes a markdown
heading label (a line, after markup-stripping, that begins with a capitalized word/phrase followed
immediately by `:`) is not treated as a clause boundary for the purposes of scanning *into* that
heading — headings like `**Signpost:**`, `**HALT:**`, `**BLOCKER:**` are structural markers, not
narrating clauses, and are excluded from §3.2 matching entirely (a heading label never begins with
one of the §3.2 verb sequences in practice, but this is stated explicitly so a future heading
convention starting with, e.g., "I" cannot accidentally match).

### 3.5 Flag condition

A clause **flags** iff it matches §3.2 (subject + internal/communicative verb) and is not
neutralized by §3.3, and is not exempted by §3.4 or §5 (legitimate-narration exemptions, below).

## 4. Sibling Hook, Not an Extension of `first-turn-contract-enforcement` (resolves Intake Open Question 4)

**Decision: ships as a fully separate hook** —
`.claude/hooks/no-preamble-no-meta-narration.sh` wrapping a new
`scripts/no_preamble_probe.py`, its own track-record log, its own `.claude/settings.json` entries.

**Rejected: extend `first-turn-contract-enforcement`'s existing `Stop` hook to also run this
check.**

- **Scope mismatch is structural, not incidental.** `first-turn-contract-enforcement` fires only on
  the first turn of a queue-injected session (its §5.1 predicate) and allows unconditionally
  outside that narrow window — that gate is load-bearing for *its* purpose (C1–C3 are FOOTER-
  contract checks meaningful only on the queue-injected first turn) but is exactly wrong for this
  hook, which must evaluate **every** assistant turn regardless of queue injection or turn number
  (per §2's non-goal statement and Intake's problem framing — meta-narration is not a first-turn-
  only failure). Bolting this check onto the existing probe would require either (a) running it
  inside the existing first-turn/queue-injection gate, silently narrowing this hook's real scope to
  match a different hook's scope for no reason connected to this hook's own purpose, or (b) adding
  a second, independent gate-bypass path inside the same probe file, which is strictly more complex
  than two probes each with one gate.
- **Independent rollout life-cycles.** `first-turn-contract-enforcement` is already past its own
  soak/propagation-evidence gate (§7 of that document) and blocking in agent-rig. This hook starts
  observe/log-only (§6) and is promoted independently, on its own evidence (§6.3). Coupling the two
  probes would couple their block/allow decisions and their track-record schemas, making it
  impossible to reason about or promote one without touching the other — directly against the
  "ship one hook at a time" cluster rollout policy already governing this cluster (Intake, Context
  §"Cluster rollout policy").
- **Two-part trigger doesn't fit inside a `Stop`-only hook anyway.** Per DDR-007 and Intake, this
  hook's design has a `UserPromptSubmit`-side component (§6.1) that `first-turn-contract-
  enforcement` has no equivalent of at all — extending a `Stop`-only hook cannot host that half
  regardless of the scope-mismatch argument above.
- **Precedent for separate-but-sibling, not merged, hooks already exists in this repo.**
  `progress-md-proof-per-slice-hook` and `domain-boundary-provenance-hook` are two separate
  `PreToolUse` hooks in the same cluster, sharing a *pattern* (allowlist/manual-stamp split,
  PROVISIONAL-constant discipline) without sharing a *probe file* — this decision follows that same
  precedent, not a novel one.

Cost of this decision, stated plainly: two probes both read `last_assistant_message` off `Stop`-
hook stdin, in two separate files, and both maintain a track-record log with a similar (but not
identical, §6.3) schema — a small amount of structural duplication, judged acceptable against the
scope-mismatch and independent-rollout arguments above, matching the same duplication already
accepted between `progress-md-proof-per-slice-hook` and `domain-boundary-provenance-hook`'s
independent PreToolUse probes.

## 5. Distinguishing Legitimate Narration From Substance-Substituting Narration (resolves Intake Open Question 3)

This is the sprint's hardest design problem (Intake, explicit framing) and gets three independent
mechanisms, not one:

### 5.1 Mechanism 1 — the concrete-noun test itself (§3.3) is the primary filter

Most legitimate first-person statements — a genuine status update ("I'm now running the test
suite against `tests/fixtures/first_turn_contract_corpus.json`"), a direct answer to "what are you
doing" ("I'm reading `SPEC.md` to check the acceptance criteria"), a HALT/BLOCKER report ("I
cannot proceed because `config.yaml` is missing the `timeout` key") — all name a concrete thing in
the same breath, because genuine narration is *about* something specific. Substance-substituting
narration is definitionally the case where no concrete thing is named ("Let me dig into this,"
"I'll take a look," "I think I should be honest about something"). §3.3's five-way test is doing
most of the real work here, and this is deliberate: the grammatical shape (verb-without-object) is
itself the signal, not a separate "is this legitimate" classifier layered on top.

### 5.2 Mechanism 2 — structural exemption for HALT/BLOCKER/status-report headings

A clause is exempted regardless of §3.2/§3.3 if it is, or is the first clause immediately following
(same line or next line), one of the following heading markers (using the same heading-line
predicate shape as `first-turn-contract-enforcement` §5.2/§5.3 — case-insensitive, markup-stripped,
first word of the line followed by an optional parenthetical and a colon):

```
^HALT\b | ^BLOCKER\b | ^STATUS\b | ^PROGRESS UPDATE\b | ^WAITING ON\b
```

**Rationale**: these are exactly the legitimate-narration cases the Intake names — a HALT message
is definitionally first-person ("I cannot proceed until X") and definitionally substantive (it
names the blocking condition), but the blocking condition may sometimes fall outside the five-way
concrete-noun test (e.g. "I need your decision on which of the two options to take" — no code
span, file path, digit, or proper noun, yet this is a legitimate report a human genuinely needs).
Rather than widen §3.3's noun test to cover this case and risk under-flagging elsewhere, the
heading-marker exemption is scoped narrowly to the four report types this repo already has a
structural convention for (`HALT`/`BLOCKER` are this repo's own established Frank-gate vocabulary;
`STATUS`/`PROGRESS UPDATE`/`WAITING ON` are added as the general "legitimate first-person report"
shapes the Intake names for mid-task updates).

### 5.3 Mechanism 3 — direct-answer exemption is explicitly NOT implemented in v1

The Intake also names "a direct answer to 'what are you doing'" as a legitimate case requiring
cross-referencing the preceding user turn's text (was the immediately-prior user message a
question about current activity?). **This mechanism is deliberately deferred, not silently
dropped**: implementing it requires the probe to read the transcript for the immediately-preceding
`user` record and classify it as a question-about-activity, which is a second, independent
detection problem (question classification) layered on top of this hook's own grammatical rule,
and risks exactly the "one detector, two unrelated jobs" complexity the DDR-011 split was designed
to avoid for this cluster generally (§2's non-goal: DDR-011 stays separate because mixing detection
methods makes false-positive rate unmeasurable). **v1 disposition**: a direct-answer turn typically
also satisfies §5.1 (an answer to "what are you doing" that doesn't name what you're doing isn't
actually answering the question, so the concrete-noun test still clears it in practice) — if the
observe/log-only period (§6) surfaces real false positives of this specific shape that §5.1/§5.2
don't already cover, that becomes evidence for a v2 amendment (§11), not a gap this document should
paper over with an unbuilt mechanism.

## 6. Two-Part Trigger, Concretely (resolves Intake Open Question 3 of the DDR index entry / Capability Gap 3)

### 6.1 Part 1 — `UserPromptSubmit`: pre-generation reminder injection

Event: `UserPromptSubmit`. Fires once per user turn, before the model generates its response.
Emits `hookSpecificOutput.additionalContext` (the same field `session_queue_probe.py` already uses
for its own `SessionStart` injection, per `session-queue-hardening.md` §2a — a confirmed, already-
live mechanism in this repo, not a new claim needing fresh verification) containing a fixed,
literal reminder string:

```
NO-PREAMBLE REMINDER — do not open with intent-announcement, stall, or self-narration ("I'll...",
"Let me...", "I think I should...", "To be honest..."). Start with the substantive action or
the concrete answer. A Stop-hook check inspects this turn for exactly this pattern
(docs/tooling/no-preamble-no-meta-narration-hook/SPEC.md).
```

This is advisory injection, not a check — it cannot block anything (`UserPromptSubmit`'s
`additionalContext` has no block/deny semantics; it only adds text to context, same posture
`session_queue_probe.py` already establishes for its own injected content). Its purpose is
identical to `session_queue_probe.py`'s FOOTER-contract injection: give the model the rule as
context immediately before generation, on the theory (already validated by this cluster's DDR-005
thesis, and by `first-turn-contract-enforcement`'s own FOOTER precedent) that a check paired with a
fresh reminder produces better compliance than either alone.

### 6.2 Part 2 — `Stop`: post-generation pattern check

Event: `Stop`. Wrapper (`.claude/hooks/no-preamble-no-meta-narration.sh`) captures stdin, replays
to `scripts/no_preamble_probe.py` under the same 5s bounded timeout as `first-turn-contract.sh`
(§7 below — same class of operation: no network, single-message regex scan, cheaper than
`first-turn-contract-enforcement`'s C3 transcript read since this probe never reads
`transcript_path` at all, only `last_assistant_message`).

Unlike `first-turn-contract-enforcement`, this probe:

- Does **not** gate on queue injection or first-turn status (§2 non-goal — applies to every turn).
- Does **not** consult the transcript at all — `last_assistant_message` is the only input needed
  (no C3-equivalent check exists in this hook's design).
- **Does** still check `stop_hook_active` first and allow unconditionally if true — same
  unconditional-restraint guarantee as `first-turn-contract-enforcement` §4.1, for the same reason
  (bounds this hook's own contribution to a stop cycle to at most one decision).

**Decision protocol**: identical shape to `first-turn-contract-enforcement` §3.2 —
`{"decision": "block", "reason": "..."}` on block, `{}`/empty stdout on allow — reusing the same
confirmed-correct binary contract (§3.2 of that document, evidence class 2, already verified on
this host's installed Claude Code version; not re-verified independently here because it is the
same binary, same `Stop` event, same field, no reason to expect drift since that verification).

### 6.3 Rollout mode: log-only at v1, blocking gated on §6.4's evidence bar

The probe runs in one of two modes, controlled by a single module-level constant in
`scripts/no_preamble_probe.py`:

```python
MODE = "log_only"  # "log_only" | "blocking" — flipped only per §6.4's evidence bar, by a
                    # deliberate code change + commit, never by runtime env var (unlike
                    # CLAUDE_CODE_STOP_HOOK_BLOCK_CAP's env-var toggle, which this design
                    # deliberately does not mirror — see first-turn-contract-enforcement §4.3's
                    # own critique of environment-toggled safety-relevant behavior; the same
                    # reasoning applies here to a toggle that changes user-facing behavior).
```

- **`log_only` (v1 default)**: on a flagged turn, the probe writes a `flagged` track-record entry
  (§8) but always emits `{}` (allow) to Claude Code — the turn is never blocked, only recorded.
- **`blocking`** (future, evidence-gated): on a flagged turn, emits
  `{"decision": "block", "reason": "..."}` with `reason` naming the flagged clause verbatim (quoted,
  not paraphrased, matching `first-turn-contract-enforcement`'s own `reason` convention) and
  instructing the agent to restate the turn leading with the substantive content.

### 6.4 False-positive threshold for promotion to `blocking` (resolves Intake Open Question 2)

**No prior instance of this specific hook exists to cite a measured number from** (same situation
`first-turn-contract-enforcement` §7 was in for its own propagation-beyond-agent-rig bar). The
closest citable precedent in this repo is that document's own evidence standard, reused here in
shape (not copied as an unexamined default — DDR-005/CLAUDE.md's "promoted default" caution applies
directly to reusing a number without re-justifying it for the new context, so this is stated as its
own decision, not an inheritance):

**PROVISIONAL — owner: Danny, no citable precedent exists for this hook specifically (judgment
call, not a measurement, per this repo's Decision Discipline)**:

- At least **20** track-record entries with `decision: flagged` (log-only mode), spanning at least
  **3** distinct calendar days of real usage (raised from `first-turn-contract-enforcement`'s
  10-entries/2-days bar because this hook fires on every turn, not gated to one turn per session —
  the same entry count there represents far fewer distinct sessions/turns of real signal than here,
  so a larger sample is needed to reach comparable coverage), AND
- **Zero** entries where a flagged clause, on human review, was judged legitimate narration (a
  false positive per §5's own framing), AND
- **At least five** entries where a flagged clause, on human review, was judged a genuine
  substance-substituting narration instance the hook correctly caught (mirrors
  `first-turn-contract-enforcement` §7's "a hook with zero true positives has not yet been observed
  doing its job" reasoning, raised from 1 to 5 because this hook's pattern — unlike a rare FOOTER-
  contract violation — is expected to be common if the underlying problem is real, per the Intake's
  own problem statement; five occurrences is a low bar against that expectation, not a high one).

If 20 log-only entries pass with zero flags at all, this bar is not met (no true positives to
count) — the correct read of that outcome is either the rule is too narrow (§3's verb set misses
real cases) or the underlying problem is smaller in agent-rig specifically than the Intake's
ecosystem-wide framing suggests; either way, that is itself a finding to report to Danny, not a
silent trigger for loosening the bar.

**This threshold is revisitable by Danny at any time — it is PROVISIONAL, not locked — but must not
be silently loosened by a future session that wants to promote to blocking and finds it
inconvenient**, same standing rule `first-turn-contract-enforcement` §7 states for its own bar.

## 7. Components

| Component | Responsibility | Location |
|---|---|---|
| `no_preamble_probe.py` | Reads `Stop`-hook stdin JSON, applies §3's clause-level detection rule to `last_assistant_message`, applies §5's exemptions, emits allow/flag(-only)/block per §6.3's mode, writes its own track-record entry. Pure function of stdin; no transcript read, no LORE access, no network. | `scripts/no_preamble_probe.py`, mirrored source-of-record copy at `reference/no_preamble_probe.py` (same drift-guarded duplication discipline as `first_turn_contract_probe.py`) |
| `.claude/hooks/no-preamble-no-meta-narration.sh` | Wrapper: captures stdin, replays to the probe under a 5s bounded timeout, validates output shape, fails open on any probe error. Structurally identical to `.claude/hooks/first-turn-contract.sh` (§4's decision: same shape, separate file). | `.claude/hooks/no-preamble-no-meta-narration.sh` |
| `no_preamble_reminder.py` (or inline in the wrapper, forge-stage call) | `UserPromptSubmit` handler emitting the fixed reminder string (§6.1) as `hookSpecificOutput.additionalContext`. No detection logic — pure static injection, same shape as `session_queue_probe.py`'s own injection call. | `scripts/no_preamble_reminder.py` (or equivalent — exact split between a dedicated script vs. inline wrapper logic is a forge-stage implementation choice, not architecturally load-bearing either way, since the injected string is fixed and requires no runtime computation) |
| Track-record log | Append-only record of every `Stop`-hook invocation's verdict (§8 schema). | `docs/tooling/no-preamble-no-meta-narration-track-record.jsonl` (repo-local, `.gitignore`d working-copy file — same durability tradeoff and rationale as `first-turn-contract-enforcement` §6: a git-tracked file every `Stop` event appends to would permanently corrupt `dirty:` semantics that `session-queue-hardening`'s close-capture machinery depends on) |
| `.claude/settings.json` entries | Wires `UserPromptSubmit` → the reminder handler and `Stop` → the wrapper, alongside the existing `first-turn-contract.sh` and `progress-proof-per-slice.sh` entries (repo-local settings, additive). | `.claude/settings.json` |

Four components (one more than `first-turn-contract-enforcement`'s three, because this hook has a
`UserPromptSubmit`-side component that hook does not), two wiring changes.

## 8. Track-Record Schema

```typescript
interface NoPreambleTrackRecordEntry {
  timestamp: string;        // ISO 8601 UTC, wall-clock of the Stop event
  session_id: string;
  stop_hook_active: boolean;
  mode: "log_only" | "blocking";  // §6.3's active MODE at the time of this invocation
  decision: "allow" | "flagged" | "block" | "probe_error";
  // "flagged": log_only mode, a clause matched §3.5 but no block was emitted (§6.3)
  // "block": blocking mode, a clause matched §3.5 and a block WAS emitted
  flagged_clauses: Array<{ text: string; verb_matched: string }>; // empty on allow/probe_error
  reason: string | null;    // the exact reason string sent on block; null otherwise (including
                             // on "flagged", since log_only mode never sends a reason to Claude
                             // Code — this field only ever populates in blocking mode)
  probe_error: string | null;
}
```

Deliberately not identical to `first-turn-contract-enforcement`'s `TrackRecordEntry` (§6 of that
document) — no `queue_injected`/`first_turn`/`violations: C1|C2|C3` fields, since this hook has no
queue-injection gate and no C1/C2/C3-shaped violation taxonomy; `mode` and `flagged_clauses` are
new fields this hook's own design requires. Same *shape* of discipline (every invocation gets a
line, gitignored not tracked, drives §6.4's evidence bar the same way `first-turn-contract-
enforcement` §7's schema drives its own bar), not a copy-pasted schema.

## 9. Scope Confirmation (resolves Intake Open Question 5)

**This sprint builds and wires the hook in agent-rig only.** No retrofit roster is defined by this
document. This follows the precedent already set twice in this cluster —
`first-turn-contract-enforcement` §1 non-goals ("Does not retrofit other repos... built portable
but not installed elsewhere") and `first-turn-contract-enforcement` §7/§8 (propagation is a future,
evidence-gated decision) — rather than the `signpost-pillar-propagation` retrofit-roster pattern the
Intake flagged as the alternative. Retrofit to sibling projects, if warranted, is tracked as a
separate future DDR/sprint once §6.4's evidence bar is met and Danny decides to act on it — this
document does not pre-authorize that step.

## 10. Dependencies

| Dependency | Version | Purpose |
|---|---|---|
| Python 3 stdlib (`json`, `re`, `sys`, `os`, `datetime`) | already used by `first_turn_contract_probe.py`/`session_queue_probe.py` | stdin parsing, clause/regex matching, JSON I/O — no new dependency |
| `bash` | already used by `first-turn-contract.sh` | wrapper stdin capture, timeout, JSON validation |

No new third-party library, no network access, no LORE/Postgres dependency — same posture as
`first-turn-contract-enforcement` §9.

## 11. Patterns

| Pattern | Usage | Rationale |
|---|---|---|
| Wrapper-invokes-probe-under-timeout, wrapper-owns-fail-open | `.claude/hooks/no-preamble-no-meta-narration.sh` → `scripts/no_preamble_probe.py` | Exact precedent: `first-turn-contract.sh` → `first_turn_contract_probe.py`, reused verbatim per Intake constraint. |
| Structural (clause/heading) regex matching over substring matching | §3, §5.2 | Same class of empirically-motivated design as `first-turn-contract-enforcement` §5.2/§5.3 (heading-line predicate beats substring scan on real corpus data) — applied here by construction, since no meta-narration corpus yet exists to validate against (§12 flags this as a forge-stage need). |
| Closed, enumerated verb/heading lists, revisable by amendment | §3.2, §5.2 | Matches `first-turn-contract-enforcement`'s C1/C2 closed-label-set approach; avoids an open-ended "configurable later" deferral this document's constraints forbid. |
| Two-mode (`log_only`/`blocking`) probe behind a single module constant, no env-var toggle | §6.3 | Deliberately does NOT mirror `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`'s env-var-toggle shape — `first-turn-contract-enforcement` §4.3 already names the risk of an externally-flippable behavior toggle; this hook's mode change is a deliberate code edit + commit, not runtime-configurable. |
| Gitignored, working-copy-only track-record log | §7, §8 | Same rationale and same defect class `first-turn-contract-enforcement` §6 already found and fixed (git-tracking a per-Stop-event append corrupts `session-queue-hardening`'s `dirty:` semantics) — applied proactively here rather than re-discovered. |

### Anti-patterns (do not use)

- **Fixed banned-phrase substring list.** Explicitly rejected by DDR-007/Intake — trivially
  bypassed by rewording; this is the mechanism DDR-011 exists to keep separate, and applying it
  here would blur that boundary.
- **A single "any capitalized word" concrete-noun test.** Rejected in favor of §3.3's five-way
  test — under-matches lowercase file paths, over-matches sentence-initial capitalization and named
  mentions inside otherwise-pure-narration clauses (§3.3's worked example).
- **Extending `first-turn-contract-enforcement`'s existing `Stop` probe.** Considered and rejected;
  full reasoning in §4.
- **Env-var-toggled blocking mode.** Considered (mirroring `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) and
  rejected — §6.3, §11 pattern table above.
- **Cross-referencing the preceding user turn to classify "was this a direct answer to a
  question."** Deferred, not built, in v1 — §5.3 states why and what would trigger reconsidering it.

## 12. Integration Boundary — What This Tool Does NOT Get Authority Over

- **Truth or quality of the response.** This hook matches a grammatical shape (subject + narrating
  verb + no concrete noun). It has no opinion on whether the substantive content of a turn, once
  the narration is stripped, is correct, complete, or well-written.
- **Jargon, register, or plain-language compliance.** Explicitly DDR-011's separate hook (§2, §9).
- **Frank.** This tool runs at `UserPromptSubmit`/`Stop`, has no gate authority, and does not feed
  into or override Frank's binding spec/forge gates, same boundary `first-turn-contract-
  enforcement` §8 states for itself.
- **Human judgment.** In `blocking` mode (once/if promoted), a human can always override, ignore,
  or re-litigate a block by reading the `reason` and the flagged clause directly — advisory to the
  agent continuing the turn, not binding on the human. In `log_only` mode (v1), the hook has no
  power to affect the turn at all — it only records.
- **Any other repo.** Per §9, this document authorizes agent-rig build and wiring only.
- **The FOOTER/Signpost/Pillar contract.** That remains `first-turn-contract-enforcement`'s lane
  entirely (§4 explains why these stay separate hooks) — this document does not modify, read, or
  depend on that probe's logic or track record.

## 13. Acceptance Criteria

1. A `last_assistant_message` opening with a clause matching §3.2 and containing no §3.3 concrete-
   noun signal in that clause (e.g. `"Let me dig into this and see what's going on."`) produces a
   `flagged` track-record entry (mode `log_only`) and an allow (`{}`) to Claude Code.
2. A `last_assistant_message` opening with a clause matching §3.2 but containing a §3.3 signal in
   the same clause (e.g. `"I'll check config.yaml for the timeout value."`) produces an `allow`
   track-record entry — no flag.
3. A `last_assistant_message` using one of the §3.2-excluded past-tense verbs (e.g. `"I confirmed
   the tests pass."`) produces `allow` — verifies the exclusion in §3.2 is real, not just stated.
4. A `last_assistant_message` opening with `**HALT:**` or `**BLOCKER:**` followed by first-person
   narration with no §3.3 signal (e.g. `"**HALT:** I need your decision on which option to take."`)
   produces `allow` — verifies §5.2's structural exemption fires.
5. `stop_hook_active: true` always allows regardless of `last_assistant_message` content —
   demonstrated by feeding a flaggable message twice, second time with the flag set, second call
   allows (mirrors `first-turn-contract-enforcement` acceptance criterion 6).
6. Wrapper/probe failure (exception, timeout, malformed output) never blocks and never crashes the
   turn — demonstrated by fault injection, matching `first-turn-contract-enforcement` acceptance
   criterion 5.
7. With `MODE = "blocking"` set (test-only override, not the shipped default per §6.3), a flagged
   message produces `{"decision": "block", "reason": ...}` naming the flagged clause verbatim
   (quoted) — demonstrated even though `blocking` is not the v1 shipped mode, to prove the code
   path exists and is correct ahead of the future promotion decision (§6.4).
8. Artifact exists at `scripts/no_preamble_probe.py` and `reference/no_preamble_probe.py`
   (identical, drift-guarded) plus `.claude/hooks/no-preamble-no-meta-narration.sh` plus the
   `UserPromptSubmit` reminder component (§7); `.claude/settings.json` wires both events in
   agent-rig only; `.gitignore` gains an entry for
   `docs/tooling/no-preamble-no-meta-narration-track-record.jsonl` in the same commit.
9. `docs/tooling/no-preamble-no-meta-narration-track-record.jsonl` exists in the working copy and
   gains one entry per real invocation once the hook is live, matching §8's schema; `git status
   --porcelain` shows the file as ignored, not dirty, at every point in the demonstration.
10. This document's §6.4 evidence standard exists (it does) before any future session sets
    `MODE = "blocking"` as the shipped default — i.e. before `.claude/settings.json`'s wiring is
    paired with a non-`log_only` `MODE` value in a real commit.
11. Every criterion above is demonstrated by an executed check attached to the claim (unit test
    against a constructed fixture set, fault-injection output, or a real observed session), not
    asserted by inspection alone — matching `first-turn-contract-enforcement` acceptance criterion
    10's evidentiary standard.

## 14. Open Items for the Forge Stage (not this document's to resolve)

- **No real fixture corpus exists yet for this hook**, unlike `first-turn-contract-enforcement`
  which had a real transcript (`tests/fixtures/first_turn_contract_corpus.json`) to validate C1–C3
  against before shipping. §3's clause-boundary and five-way concrete-noun rules are reasoned from
  the Intake's own example phrases, not empirically validated against a real corpus of this
  ecosystem's actual meta-narration instances the way `first-turn-contract-enforcement` §5.2/§5.3
  were. Forge stage should assemble a real fixture set (a handful of real transcripts from
  agent-rig sessions, scanned for both true meta-narration and legitimate first-person statements)
  before or alongside implementation, and amend §3/§5 if real data contradicts the reasoned design
  here — the same "verify against real files" discipline this repo's other hooks in this family
  already applied, not skipped here just because no obvious defect prompted it yet.
- Exact split of the `UserPromptSubmit` reminder handler (dedicated script vs. inline wrapper
  logic, §7) is a forge-stage implementation choice.
- §6.4's threshold is PROVISIONAL, owner Danny — confirm with Danny before or at forge completion
  whether the 20-entries/3-days/0-false-positive/5-true-positive bar stands as stated or should be
  adjusted before this document is treated as informing any future promotion decision.
