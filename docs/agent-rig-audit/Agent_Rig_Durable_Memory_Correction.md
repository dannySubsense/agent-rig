# Agent Rig Durable Memory Correction

**Date:** 2026-09-18  
**Status:** Analysis and recommendation; not adopted architecture  
**Scope:** Existing Agent Rig memory records and future durable-memory admission

## Executive judgment

Agent Rig can correct its memory without deleting its history or pretending that old records were
always accurate. The safest approach is to separate **historical retention** from **active trust**:

- preserve existing LORE and related process records as historical signposts;
- stop treating them as canonical evidence or automatically injecting them into new work;
- revalidate only the small subset needed for current work;
- promote supported, reusable claims into a deliberately small active memory surface; and
- require a human decision before a claim becomes durable memory.

Correcting only future capture is insufficient. Existing records can continue to contaminate
future contexts if retrieval presents them as authoritative. Rewriting all old memory in place is
also unsafe: it destroys provenance and can convert retrospective interpretation into false
history.

The appropriate correction is therefore **demotion, selective validation, and explicit
promotion**, not wholesale rewriting.

## The governing distinction

Agent Rig should distinguish four things that are currently easy to conflate:

| Surface | Purpose | Authority |
|---|---|---|
| Working reasoning | Temporary exploration within an active task | Ephemeral; not evidence |
| Historical record | What an agent or human previously reported, attempted, or believed | A signpost to investigate |
| Durable memory | A reusable, scoped claim admitted for future context | Trusted only within its stated scope |
| Canonical artifact | Current source, specification, policy, or other governed truth surface | Authoritative for its defined subject |

Durable memory is not a substitute for canonical artifacts. It should help a future worker locate
and interpret primary sources, not supersede them. A memory can accurately report that a decision
occurred, but the governing decision record remains the authority. A memory can point to a test,
but it is not the test result.

## What should happen to the existing memory bank

Do not begin with deletion or repository-wide rewriting. First determine which records are
actually loaded, searched, summarized, or injected into active sessions. Records that are never
retrieved are archival clutter; records that enter new contexts are the contamination risk.

Classify only the retrieved or currently relevant records:

### Current and supported

The claim is still true, has a defined scope, and is supported by a current canonical artifact or
reproducible evidence.

**Treatment:** Eligible for active durable memory after human approval. Preserve a reference to
the governing source and its relevant identity, such as a commit or document revision.

### Useful signpost, not evidence

The record identifies a potentially important issue, decision, file, or historical event, but
does not independently establish that its claim is true now.

**Treatment:** Retain in history and label as a signpost. Do not automatically present it as
trusted context.

### Superseded

The record was once applicable but a later source, decision, or implementation replaced it.

**Treatment:** Preserve it unchanged as history, attach or record a concise supersession pointer,
and exclude it from normal active retrieval.

### Unsupported

The record makes a claim that cannot be established from repository reality, primary evidence,
or an accountable human decision.

**Treatment:** Keep only if it has historical or diagnostic value. Mark it unsupported and remove
it from trusted retrieval. Do not silently rewrite it into a stronger claim.

### Obsolete or duplicate

The record describes retired machinery, repeats a better-governed source, or adds no unique
information.

**Treatment:** Remove it from active retrieval. Archive or delete it only under the repository's
normal retention rules and with clear human authorization.

### Indeterminate

The record may be correct, but validating it would require evidence that is unavailable or work
that is disproportionate to current need.

**Treatment:** Exclude it from trusted retrieval. Revisit only when an actual task depends on it.

## Why history should not be corrected in place

Editing an old narrative so that it agrees with current understanding creates several problems:

- it erases what agents actually knew or believed at the time;
- it obscures when a correction occurred and who accepted it;
- it encourages later readers to treat narrative consistency as proof;
- it makes audit findings difficult to reproduce; and
- it can contaminate Git history with a second layer of retrospective narration.

When an old claim is wrong, the truthful representation is: **the old record made this claim; the
claim is now unsupported or superseded for these reasons.** The old text may remain intact while
its retrieval status and authority change.

## Minimal correction procedure

The correction should be demand-driven and bounded:

1. **Identify the retrieval path.** Determine what memory is automatically or routinely placed
   into Wright, implementer, Codex, or Frank contexts.
2. **Choose one bounded task surface.** For the first pass, use only memory that could affect the
   proposed Frank authority-path tracer.
3. **Read the primary sources.** Validate claims against current repository artifacts, Git
   identity, deterministic tests, and explicit human decisions—not against other memory records.
4. **Classify each relevant record.** Use the six classifications above.
5. **Restrict active retrieval.** Only current, supported, human-approved claims enter ordinary
   future context. Other records remain discoverable history when specifically requested.
6. **Record corrections by reference.** A supersession or support decision points to the primary
   source; it does not duplicate that source's full content.
7. **Stop when the bounded task is clean.** Do not turn the first correction into a complete LORE
   migration or a new memory platform.

This procedure does not require a new event system, proof ledger, dashboard, ontology, or semantic
classification hook. A small reviewed list or existing retrieval configuration is sufficient for
a pilot, provided it does not become another competing source of truth.

## Rule for future durable memory

Working reasoning should expire by default. A claim becomes durable memory only when all of the
following are true:

1. **Reusable:** It is likely to matter beyond the current task.
2. **Supported:** It cites a primary artifact, reproducible observation, or accountable human
   decision.
3. **Scoped:** It states where and when the claim applies, including important exceptions.
4. **Current:** It has not been superseded by a later canonical source.
5. **Compact:** It records the durable fact or principle, not the conversation or failed attempts
   that produced it.
6. **Owned:** A human accepts responsibility for promoting it into trusted memory.
7. **Reversible:** It can be demoted or superseded without rewriting historical records.

A suitable admission rule is:

> Working reasoning expires. Durable memory is admitted only when it states a reusable fact or
> principle, cites its primary evidence, names its scope, and receives human approval.

Human approval can cover a coherent reviewed batch; it need not become an approval ceremony for
every sentence. The important boundary is that an agent cannot promote its own narration into
trusted memory merely by writing it down.

## Retrieval rules

Admission and retrieval are separate controls. Even a valid memory should not be injected into
every role or task.

- **Implementers** receive only memory relevant to the bounded work contract and complete
  judgment surface.
- **Codex auditors** should prefer frozen source and evidence; memory may identify an area to
  inspect but must not supply the expected conclusion.
- **Cold Frank** should not receive author memory, prior reviewer conclusions, repair history, or
  confidence claims. Relevant canonical criteria should be supplied directly.
- **Wright/orchestrators** may use memory for navigation and planning but must not present it as
  repository proof.
- **Humans** should be able to inspect why a memory was admitted, what supports it, and whether it
  remains in scope.

Retrieval should favor the smallest sufficient context. “Potentially useful” is not enough to
justify automatic injection.

## Avoiding a new narration loop

Memory correction would fail if it generated a diary of every reviewed record, a new ledger that
duplicates LORE, or recurring reports whose primary subject is the correction process itself.

Avoid that outcome by applying these constraints:

- retain classifications only where they change retrieval or authority;
- cite primary artifacts instead of copying their contents;
- do not preserve reviewer discussion or chain-of-thought;
- do not create a memory record merely to say that another memory was reviewed;
- do not automatically turn every failure into a lesson;
- do not measure success by the number of records processed; and
- delete temporary working notes when the bounded review ends.

The output that matters is a smaller, better-supported active memory set—not a comprehensive
account of the cleanup.

## Smallest defensible pilot

Run the first memory correction alongside, but do not expand, the Frank authority-path tracer.

### Scope

Review only records that make claims about:

- which Frank source is authoritative;
- where Frank is installed;
- whether Notebook may own or overwrite the same destination;
- how installed-copy drift is detected; and
- what constitutes an independent Cold Frank judgment.

### Method

1. Enumerate only the memory records that retrieval would surface for those questions.
2. Validate them against the frozen repository target, relevant source/install files, governing
   documents, and the tracer's deterministic test.
3. Classify them without editing their historical wording.
4. Present the proposed active set, exclusions, and evidence references to the human owner.
5. After approval, use only the active supported set in ordinary orchestration; keep excluded
   records available only as explicitly requested history.

### Success criteria

- An implementer can complete the tracer without relying on unsupported historical narrative.
- Codex and Cold Frank can judge the frozen target without receiving conclusions from memory.
- Every active memory claim has a direct support reference and defined scope.
- Superseded and unsupported records do not enter ordinary task context.
- No new general memory framework or recursive cleanup ledger is created.
- A clean reader can distinguish current truth, historical claim, evidence, reviewer judgment,
  and human decision.

## Recommendation

Correct the existing memory bank **selectively and now where it affects active work**, while also
changing admission rules going forward. Do not attempt a universal historical rewrite, and do not
leave the existing bank fully trusted while merely promising better future capture.

The practical posture is:

> Preserve history, demote unsupported narration, validate on demand, promote sparingly, and keep
> human accountability at the admission boundary.

The first concrete action is to identify the exact LORE or memory records automatically retrieved
for the Frank authority-path tracer. That read-only inventory will reveal whether correction
requires a retrieval configuration change, a small curated active set, or simply the removal of
obsolete records from automatic context.
