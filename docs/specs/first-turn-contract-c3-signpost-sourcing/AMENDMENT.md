# Amendment: first-turn-contract-c3-signpost-sourcing

Replaces INTAKE/INTERVIEW/NORTH-STAR/01-REQUIREMENTS/02-ARCHITECTURE/04-ROADMAP/05-REVIEW, all of
which describe a design that was abandoned before shipping. This is the record of what happened
and what shipped.

## Problem (issue #27)

C3 is a check inside `scripts/first_turn_contract_probe.py` that's supposed to block a session
when its "Pillar" section (an agent's claim of what it verified) isn't backed by real work. A
Pillar that plainly admits it verified nothing — "Pillar: none yet — nothing independently checked
this session" — was passing anyway, because the check only fires when it can find something
specific to disagree with, and plain-English admission text has nothing to disagree with.

## Abandoned approach

Original plan: also pull claim-worthy details (file names, branch names, IDs) out of the
"Signpost" section — background context injected into the agent's prompt — and require the
Pillar to address anything the Signpost raised.

Rejected for two reasons:
1. Signpost text isn't something the current agent wrote or controls — it's handed to them.
   Blocking a session over content it didn't author isn't verification.
2. Tested against 18 real Signpost sections pulled from this repo's own session history: ~40% of
   what it would have flagged was false — ordinary phrases like "2/3" or "pushed/clean" misread as
   file/branch references. Confirmed with real data, not assumed.

## What shipped

`check_c3_violation` now also fires when the Pillar section's own text admits it verified
nothing ("none yet," "nothing checked," etc.) — checked only against the Pillar heading's own
immediate text, nothing else. This holds an agent to its own words, not to background noise.

Verified: catches the literal issue #27 text; does not false-fire on a real verified Pillar;
tested against 22 real Pillar sections from this repo's history — 0 false positives, all 4 real
evasions caught. 34/34 tests pass (2 new). `scripts/` and `reference/` copies are identical.

## Status

Code: done, committed (`dae4aad`, branch `feature/first-turn-contract-c3-signpost-sourcing`).
Not yet through a passing Frank gate or a PR.
