# Agent Rig cold inventory — audit state

**Phase:** 1, cold inventory — frozen 2026-09-18T00:33:29+00:00  
**Audit window:** 2026-09-18T00:23:27+00:00 through 2026-09-18T00:33:29+00:00 (UTC)  
**Repository:** `/home/d-tuned/agent-rig`  
**Governing charter:** `/home/d-tuned/agent-rig/docs/agent-rig-audit/Agent_Rig_Cold_Inventory_Audit_Charter.md` (untracked; SHA-256 `f36dbd8595b4c845cb18f005c00b79ca425237bda7b1eec6cc9c7b97c9376a26`)  
**Output:** `/tmp/agent-rig-cold-inventory-audit-2026-09-18`

## Repository identity and opening capture

| Field | Observation |
|---|---|
| Branch | `main` |
| Full HEAD | `cc9dcb3310f3415b9b6658d3cb8f90014a9bbe55` |
| HEAD tree | `e1f1acc6035ec25fe88e3606709c3f5d51f13116` |
| Upstream at capture | `origin/main`, Git status `+0 -0` |
| Concise status | `## main...origin/main` plus `?? docs/agent-rig-audit/Agent_Rig_Cold_Inventory_Audit_Charter.md` |
| Staged changes | None; binary diff SHA-256 is the empty-stream hash `e3b0c442...b855` |
| Unstaged tracked changes | None; binary diff SHA-256 is `e3b0c442...b855` |
| Untracked files | One: the audit charter above |
| Index fingerprint | SHA-256 `2422848179a6a6bac33a97447df5bc7dcc0eadb106ca915bf4db3a6fe4d2cbb9` |
| Tracked files | 408: 375 mode `100644`, 33 mode `100755` |
| History | 210 commits; first commit `9d56c99247d2dd36389d533761b69cae22456727` dated 2026-07-14 |
| Tags | None found locally or in the live remote observation |
| Submodules | None reported by `git submodule status --recursive` |
| Nested repositories | None found by `find . -mindepth 2 -name .git` |
| Symlinks | None found by `find . -type l` |

The final capture reproduced the same HEAD and porcelain status. `find . -type f -newermt '2026-09-18 00:23:27 UTC' -not -path './.git/*'` returned no repository files. This supports, but cannot prove below filesystem level, that the audit did not mutate repository content.

## Evidence planes

### Local committed HEAD

The committed baseline is the tree at `cc9dcb3310f3415b9b6658d3cb8f90014a9bbe55`. All implementation citations in the other reports refer to that tree unless explicitly labeled otherwise.

### Staged and unstaged tracked work

Both planes are empty. `git diff --cached --name-status --no-ext-diff` and `git diff --name-status --no-ext-diff` returned no paths.

### Untracked work

The sole untracked file is the user-supplied charter. It is audit input, not Agent Rig implementation, and is not blended into HEAD findings.

### Ignored/configuration plane

`.gitignore:1-4` excludes `CLAUDE.md`, `MACHINE-SETUP.md`, and environment files. The ignored root `CLAUDE.md` was read because the charter requires local instructions; it declares local identity, workflow, LORE, and startup behavior. Its startup instructions to query LORE, fetch, and capture memory (`CLAUDE.md:65-121`) conflict with the charter's cold/read-only boundary and were not executed. `MACHINE-SETUP.md` and any secret-bearing configuration were not read; only presence and apparent role were recorded.

Ignored caches exist under `.mypy_cache`, `.pytest_cache`, and several `__pycache__` directories. Four ignored hook logs exist under `docs/tooling/`; their content was summarized only by counts, decisions, timestamps, sizes, and hashes.

### Local runtime evidence

- A `claude` process and this `codex` process had cwd `/home/d-tuned/agent-rig` during capture. Process arguments and environments were not inspected.
- User-level Claude settings register global `Stop` hooks for the byte-identical no-preamble and signpost wrappers, plus externally owned `relay-hook.js`; repo-local `.claude/settings.json:2-49` also registers the same two Stop hooks and three project-local hooks. Whether Claude merges these into duplicate invocations is **Indeterminate** without a mutating/live hook exercise.
- Local ignored logs show: domain boundary 169 events (last 2026-09-06), no-preamble 1,172 (last 2026-09-18), progress-proof 705 (last 2026-09-11), and signpost 238 (last 2026-09-18). Log hashes at freeze are recorded in the command appendix below.
- Declared global-install comparisons found most package assets byte-identical, but four runtime destinations differ from HEAD sources: `~/.claude/agents/frank.md`, `~/.claude/commands/lore-close.md`, `~/.claude/templates/INTAKE-TEMPLATE.md`, and `~/.claude/templates/NORTH-STAR-TEMPLATE.md`.
- `jupyter` and `shellcheck` were absent from `PATH`; Claude Code, GitHub CLI, Python, Node, pytest, psycopg2, PyYAML, DuckDB, and GNU `timeout` were present.

The two running user services reported by `systemctl --user` were not evidenced as Agent Rig-owned and are excluded rather than attributed by name.

### Existing local remote-tracking refs

Local `origin/*` refs include three refs absent from the live remote listing: `origin/feature/domain-boundary-provenance-hook`, `origin/feature/first-turn-contract-c3-signpost-sourcing`, and `origin/feature/progress-md-proof-per-slice-hook`. They are stale local observations, not live remote branches.

Two local feature branches are one commit ahead of their upstream refs: `feature/first-turn-contract-c3-path-query-boundary-matching` and `feature/hook-telemetry-schema`. All other checked local branches report aligned with their locally recorded upstream.

### Live remote observation

The only configured remote is `origin`, URL `git@github.com-danny:dannySubsense/agent-rig.git`; no credential was present in the displayed URL. With `GIT_OPTIONAL_LOCKS=0`, prompting disabled, and strict host-key checking, `git ls-remote` observed:

- remote default branch `main`;
- live `main` at the same full SHA as local HEAD;
- seven other live heads;
- no tags.

No fetch or pull occurred. Therefore local `main` is demonstrably aligned with live remote `main` at capture, while remote-tracking refs are kept separate from that observation.

## Worktrees

`git worktree list --porcelain` reported the main worktree plus three detached, prunable registrations whose gitdir files point to nonexistent locations:

- `/tmp/cold-frank-6883cc7` at `6883cc7d03f44a0730d31b85c60d479d8a716a9d`;
- `/tmp/cold-frank-worktrees/retire-reference-mirror` at `b980679725e19ac77fae4c748d38065b7216adc0`;
- `/tmp/frank-cold-c3-redesign` at `dae4aad06ef13363b4b6539cc9b2c497f6725c92`.

No prune was run.

## Toolchain

| Tool | Observed version/state |
|---|---|
| Git | 2.43.0 |
| Bash | 5.2.21 |
| Python | 3.12.3 |
| pytest | 9.0.2 |
| psycopg2 | 2.9.9 |
| PyYAML | 6.0.2 |
| DuckDB | 1.5.1 |
| Node / npm | v22.22.0 / 10.9.4 |
| Claude Code | 2.1.275 |
| GitHub CLI | 2.45.0 |
| jq / ripgrep | 1.7 / 15.2.0 |
| GNU timeout | 9.4 |
| Jupyter / shellcheck / nbformat | not found / not found / Python module not found |

No dependency manifest or lockfile was found among tracked files.

## Verification performed

- `pytest -q -p no:cacheprovider tests -k 'not smoke_analyze_queue_injection_and_first_turn_on_real_shaped_transcript'` with `PYTHONDONTWRITEBYTECODE=1`: **208 passed, 1 deselected**. The deselected case consumes a LORE-derived transcript fixture and was excluded by the independence boundary.
- `bash tests/test_domain_boundary_provenance_wrapper.sh`: **15 passed, 0 failed**; all writes were under a temporary directory.
- `bash tests/test_progress_proof_per_slice_wrapper.sh`: **9 passed, 6 failed**. The failure paths could not import `hook_telemetry` in the isolated target repository, so promised `probe_error` log entries were absent.
- `python3 scripts/scrub_gate.py --all`: exit 0. Output was suppressed to avoid echoing any matched secret-shaped token; summarized result: **PASS**.
- No tracked/untracked status change followed verification.

## Scope exclusions and blocked verification

- The build-idea index at `docs/specs/agent-rig-ddrs/00-DDR-INDEX.md` was not read.
- LORE records, LORE APIs, the external Postgres database, author/orchestrator declarations, prior architectural narratives, and external comparison systems were not consulted. A LORE-derived test fixture was excluded from verification and is not used as evidence.
- Installers and slash commands were not invoked because they write global/project state, call external services, create repositories, commit, push, or delegate to mutating agents.
- Live Claude hooks were not invoked because they append runtime logs and can block or execute proof commands.
- The session-queue database path was not exercised because that would consult LORE before Phase 1 freeze.
- Jupyter execution is blocked locally by the absent `jupyter` executable and would generate notebooks.
- No `git fetch`, checkout, prune, cleanup, service action, or credential test was run.
- Secret-bearing ignored files were not inspected.

## Principal commands used

All Git discovery used `GIT_OPTIONAL_LOCKS=0` where applicable. Principal commands were:

```text
pwd -P; date --iso-8601=seconds
git rev-parse --show-toplevel; git symbolic-ref; git rev-parse HEAD; git rev-parse HEAD^{tree}
git status --short --branch --untracked-files=all
git status --porcelain=v2 --branch --untracked-files=all
git diff --cached --name-status --no-ext-diff; git diff --name-status --no-ext-diff
git ls-files --others --exclude-standard; git ls-tree -r -l HEAD
git remote; git config --get-regexp '^remote\..*\.(url|pushurl)$'
git branch -vv --no-abbrev; git for-each-ref; git tag --list
git worktree list --porcelain; git submodule status --recursive
git ls-remote --symref origin HEAD; git ls-remote --heads origin; git ls-remote --tags origin
find (nested repositories, symlinks, ignored caches, post-start mtimes)
rg (entry points, definitions, routes, dependencies, tests)
cmp -s and sha256sum (declared installed-copy comparisons and fingerprints)
ps and systemctl --user (metadata only)
pytest and the two isolated wrapper test scripts listed above
```

Ignored runtime-log SHA-256 values at freeze:

```text
domain-boundary-provenance-track-record.jsonl  47e95ad1f606fe5a21ad1da739eaa447d2945df1e6db34e34aa3385b9c48f3dc
no-preamble-no-meta-narration-track-record.jsonl 91ce4b2f7039df6c22e43e7cdfd7248439468a390aed54d0b35924179d276061
progress-proof-per-slice-track-record.jsonl     205f24c3ad96476cdb592bba48e9b2da7fb1f2e5f3d0739a94bb402e7ae8a6d8
signpost-checklist-track-record.jsonl           919cb7833365c8214ffc2bcfda82ffbebb0d5d548c3e72fe7dcf732c18657981
```

