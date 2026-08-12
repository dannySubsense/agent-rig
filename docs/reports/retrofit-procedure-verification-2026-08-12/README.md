# Retrofit-procedure step 2a verification — 2026-08-12

Verifies the exec-bit failure mode reported by `alpha` (market_data Slice 10 pilot) against
agent-rig's own `reference/` artifacts, and confirms the step-2a pass condition discriminates.

Fixture: scratch git repo, `reference/session_probe.py` -> `scripts/`,
`reference/session-start-probe.sh` -> `.claude/hooks/` (the layout the wrapper's own
`REPO_DIR="$(dirname)/../.."` derivation requires).

| Case | Wrapper exit | Probe exit | `PROBE OUTPUT INCOMPLETE` | Ground truth injected |
|---|---|---|---|---|
| A — exec bit stripped (`chmod -x`) | 0 | **126** Permission denied | present (1) | **none** |
| B — exec bit set (`chmod +x`)      | 0 | 0                         | absent (0)  | full git/docs state |

**Finding:** confirmed as reported. The wrapper degrades honestly (exit 0, no fabricated data), which
is correct behavior AND is precisely what makes the defect invisible — session start succeeds while
every session receives zero ground truth. Absence of the `INCOMPLETE` string is therefore a valid
pass condition; wrapper exit status is NOT (it is 0 in both cases).

**Harness note (recorded because it nearly produced a false result):** the first run passed
`REPO_DIR` as an env var. The wrapper derives `REPO_DIR` itself and ignored it, so both cases
resolved to a nonexistent path and returned 127 (not-found), not 126 — making a correct artifact
look broken in both arms. Re-run against the correct layout before concluding anything from this
script. Verify the fixture, then the finding.

Raw evidence: `case-a-exec-bit-stripped.json`, `case-b-exec-bit-set.json`.
