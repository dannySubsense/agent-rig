# Lobster Harness — Spec + Forge Pipeline

**Purpose:** Deterministic multi-agent orchestration for software specification and implementation  
**Status:** Design phase — pending Lobster installation  
**Created:** 2026-03-25  
**Location:** `~/agent-orchestration-frameworks/LOBSTER-HARNESS.md`

---

## Overview

This harness uses OpenClaw's Lobster workflow engine to run deterministic agent pipelines. Unlike `sessions_spawn` (which gives LLMs control over spawning), Lobster uses YAML-defined workflows with explicit steps, approval gates, and resumable state.

**Key Benefits:**
- Deterministic flow control (YAML defines the sequence, not the LLM)
- Approval checkpoints between phases
- Resumable workflows (halt and resume with tokens)
- One tool call instead of many back-and-forth spawns

**Community References:**
- [DEV Community: Deterministic Multi-Agent Pipeline](https://dev.to/ggondim/how-i-built-a-deterministic-multi-agent-dev-pipeline-inside-openclaw-and-contributed-a-missing-4ool) — Rejected `sessions_spawn` for deterministic control
- [ClawFlows Blog](https://openclaws.io/blog/clawflows-workflow-automation/) — Skills as composable building blocks
- [Lobster PR #20](https://github.com/openclaw/lobster/pull/20) — Sub-workflow loops with conditions
- [Lobster README](https://github.com/openclaw/lobster) — Typed JSON pipelines, local-first execution

---

## Prerequisites

```bash
# Install Lobster globally
npm install -g @openclaw/lobster

# Verify installation
lobster --version
```

---

## Community Consensus: Key Patterns

| Aspect | Pattern | Source |
|--------|---------|--------|
| **Orchestration** | YAML-defined, not LLM-controlled | DEV, Lobster docs |
| **Steps** | Sequential with `depends_on` | Lobster README |
| **Agent invocation** | `llm.invoke` or shell commands | Lobster PR #20 |
| **Data flow** | JSON piping via `stdin:` between steps | Lobster README |
| **Retries** | Built-in retry logic with max iterations | Lobster PR #20 |
| **Approvals** | `approval:` field in step definition | Lobster docs |
| **Loops** | Sub-workflows with `loop:` conditions | Lobster PR #20 |
| **Resume** | Compact tokens, state stored under Lobster state dir | Lobster docs |

**Critical Insight from DEV Community:**
> "A YAML file with condition, loop, and stdin piping is infinitely more reliable than telling an LLM 'if the review is negative, go back to step 2, but only up to 3 times.'"

---

## Harness Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOBSTER HARNESS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   SPEC      │ →  │  APPROVAL   │ →  │   FORGE     │ →  │  APPROVAL   │  │
│  │  PIPELINE   │    │    GATE     │    │  PIPELINE   │    │    GATE     │  │
│  │             │    │             │    │             │    │             │  │
│  │ 5 agents    │    │ Danny       │    │ 4 agents    │    │ Danny       │  │
│  │ sequential  │    │ reviews     │    │ per slice   │    │ reviews     │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        │                   │                  │                  │         │
│        ▼                   ▼                  ▼                  ▼         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                      LOBSTER WORKFLOW ENGINE                        │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│   │  │   Parse     │  │   Execute   │  │   Approve   │  │   Resume    │ │   │
│   │  │   YAML      │  │   Steps     │  │   Halt      │  │   Token     │ │   │
│   │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Correct Lobster Syntax (Community-Verified)

**Step Types:**

```yaml
# Shell command step
- id: fetch
  run: weather --json ${location}

# Pipeline step with llm.invoke
- id: summarize
  pipeline:
    - llm.invoke --prompt 'Summarize this diff'

# Sub-workflow step (PR #20)
- id: review_loop
  lobster: ./review.lobster
  args:
    file: "${src_file}"
  loop:
    max: 3
    condition: "exit_code != 0"

# Approval gate
- id: confirm
  approval: "Want jacket advice from the LLM?"
```

**Data Flow via stdin:**

```yaml
- id: collect
  run: inbox list --json
  
- id: categorize
  run: inbox categorize --json
  stdin: $collect.stdout
  
- id: apply
  run: inbox apply --json
  stdin: $categorize.stdout
```

**Loop Environment Variables (PR #20):**
- `LOBSTER_LOOP_STDOUT` — stdout from last iteration
- `LOBSTER_LOOP_JSON` — parsed JSON output
- `LOBSTER_LOOP_ITERATION` — current iteration number

---

## Spec Pipeline Workflow

**File:** `~/agent-orchestration-frameworks/workflows/spec-pipeline.lobster`

```yaml
name: spec-pipeline
version: 1.0
description: Generate software specification documents (01-05)

args:
  - name: project_dir
    type: string
    required: true
    description: Project directory containing INTAKE.md
  - name: feature_name
    type: string
    required: true
    description: Feature name in kebab-case

env:
  SPEC_DIR: "${project_dir}/specs"
  INTAKE_DOC: "${project_dir}/INTAKE.md"
  AGENTS_DIR: "${HOME}/.claude/agents"

steps:
  # Step 1: Requirements Analyst
  - id: requirements
    name: Extract Requirements
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model moonshotai/kimi-k2.5 \
        --system "$(cat ${AGENTS_DIR}/requirements-analyst.md)" \
        --prompt "Read ${INTAKE_DOC} and create ${SPEC_DIR}/01-REQUIREMENTS.md with functional requirements, non-functional requirements, acceptance criteria, constraints, and assumptions. Reply DONE when file is written."
    timeout: 300
    
  # Step 2: Architect
  - id: architecture
    name: Design Architecture
    depends_on: [requirements]
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model nvidia/nemotron-3-super-120b-a12b \
        --system "$(cat ${AGENTS_DIR}/architect.md)" \
        --prompt "Read ${SPEC_DIR}/01-REQUIREMENTS.md and create ${SPEC_DIR}/02-ARCHITECTURE.md. Design system architecture, APIs, data models, component structure. Reply DONE when file is written."
    timeout: 600
    
  # Step 3: UI Spec Writer
  - id: ui_spec
    name: Write UI Specification
    depends_on: [architecture]
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model moonshotai/kimi-k2.5 \
        --system "$(cat ${AGENTS_DIR}/ui-spec-writer.md)" \
        --prompt "Read ${SPEC_DIR}/02-ARCHITECTURE.md and create ${SPEC_DIR}/03-UI-SPEC.md. Specify UI components, interactions, design system. Reply DONE when file is written."
    timeout: 300
    
  # Step 4: Planner
  - id: planner
    name: Create Roadmap
    depends_on: [ui_spec]
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model moonshotai/kimi-k2.5 \
        --system "$(cat ${AGENTS_DIR}/planner.md)" \
        --prompt "Read ${SPEC_DIR}/03-UI-SPEC.md and create ${SPEC_DIR}/04-ROADMAP.md with implementation slices, dependencies, estimates. Reply DONE when file is written."
    timeout: 300
    
  # Step 5: Spec Reviewer
  - id: reviewer
    name: Review Specifications
    depends_on: [planner]
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model nvidia/nemotron-3-super-120b-a12b \
        --system "$(cat ${AGENTS_DIR}/spec-reviewer.md)" \
        --prompt "Read all docs in ${SPEC_DIR}/ and create ${SPEC_DIR}/05-REVIEW.md. Review quality, identify gaps, rate each document, provide recommendations. Reply DONE when file is written."
    timeout: 600
    
  # Approval Gate
  - id: approval
    name: Await Approval
    depends_on: [reviewer]
    approval: |
      Spec pipeline complete. Review ${SPEC_DIR}/05-REVIEW.md and approve to continue.
      
      Project: ${feature_name}
      Location: ${SPEC_DIR}/
      
      Approve to proceed to Forge pipeline?
```

---

## Forge Pipeline Workflow

**File:** `~/agent-orchestration-frameworks/workflows/forge-pipeline.lobster`

```yaml
name: forge-pipeline
version: 1.0
description: Implement approved spec through code → test → review cycles

args:
  - name: project_dir
    type: string
    required: true
  - name: feature_name
    type: string
    required: true
  - name: slice_id
    type: string
    required: true
    description: Implementation slice from 04-ROADMAP.md

env:
  SPEC_DIR: "${project_dir}/specs"
  SRC_DIR: "${project_dir}/src"
  TEST_DIR: "${project_dir}/tests"
  AGENTS_DIR: "${HOME}/.claude/agents"

steps:
  # Step 1: Code Executor
  - id: code
    name: Implement Slice
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model qwen/qwen3-coder-480b-a35b-instruct \
        --system "$(cat ${AGENTS_DIR}/code-executor.md)" \
        --prompt "Read ${SPEC_DIR}/04-ROADMAP.md slice ${slice_id} and ${SPEC_DIR}/02-ARCHITECTURE.md. Implement in ${SRC_DIR}/. Reply DONE when complete."
    timeout: 900
    
  # Step 2: Test Writer
  - id: tests
    name: Write Tests
    depends_on: [code]
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model qwen/qwen3-coder-480b-a35b-instruct \
        --system "$(cat ${AGENTS_DIR}/test-writer.md)" \
        --prompt "Read implementation in ${SRC_DIR}/. Write tests in ${TEST_DIR}/. Reply DONE when complete."
    timeout: 600
    
  # Step 3: Test Runner
  - id: test_run
    name: Run Tests
    depends_on: [tests]
    run: cd ${project_dir} && pytest ${TEST_DIR} -v --tb=short
    timeout: 300
    on_failure:
      action: retry
      max_retries: 3
      
  # Step 4: QC Agent (with retry loop)
  - id: qc
    name: Quality Check
    depends_on: [test_run]
    lobster: ./qc-sub.lobster
    args:
      project_dir: "${project_dir}"
      slice_id: "${slice_id}"
    loop:
      max: 2
      condition: "$LOBSTER_LOOP_JSON.approved != true"
    
  # Approval Gate
  - id: approval
    name: Await Approval
    depends_on: [qc]
    approval: |
      Slice ${slice_id} complete. QC report: ${project_dir}/QC_REPORT_${slice_id}.md
      Approve to mark slice complete and proceed?
```

**QC Sub-workflow** (`qc-sub.lobster`):

```yaml
name: qc-sub
version: 1.0

args:
  - name: project_dir
    type: string
    required: true
  - name: slice_id
    type: string
    required: true

steps:
  - id: qc_check
    run: |
      llm.invoke \
        --provider nvidia-nim \
        --model nvidia/nemotron-3-super-120b-a12b \
        --system "$(cat ${HOME}/.claude/agents/qc-agent.md)" \
        --prompt "Review ${project_dir}/src/ and ${project_dir}/tests/. Create ${project_dir}/QC_REPORT_${slice_id}.md. Output JSON: {\"approved\": true/false, \"issues\": [...]}"
    output:
      format: json
```

---

## Master Orchestrator Workflow

**File:** `~/agent-orchestration-frameworks/workflows/master.lobster`

```yaml
name: spec-forge-master
version: 1.0
description: Master orchestrator for full spec + forge pipeline

args:
  - name: project_dir
    type: string
    required: true
  - name: feature_name
    type: string
    required: true

steps:
  # Run Spec Pipeline
  - id: spec_phase
    name: Run Spec Pipeline
    lobster: ./spec-pipeline.lobster
    args:
      project_dir: "${project_dir}"
      feature_name: "${feature_name}"
    
  # Danny approves specs
  - id: spec_approval
    name: Spec Approval Gate
    depends_on: [spec_phase]
    approval: |
      ✅ SPEC PHASE COMPLETE
      
      Project: ${feature_name}
      Location: ${project_dir}/specs/
      
      Review 05-REVIEW.md and approve to proceed to Forge phase.
      
  # Parse roadmap for slices
  - id: parse_roadmap
    name: Parse Roadmap
    depends_on: [spec_approval]
    run: |
      grep -E "^## Slice [0-9]+:" ${project_dir}/specs/04-ROADMAP.md | \
        sed 's/## Slice \([0-9]*\):.*/\1/' > /tmp/slices.txt
    output:
      file: "/tmp/slices.txt"
      
  # Loop through slices
  - id: forge_loop
    name: Forge All Slices
    depends_on: [parse_roadmap]
    lobster: ./forge-pipeline.lobster
    args:
      project_dir: "${project_dir}"
      feature_name: "${feature_name}"
      slice_id: "$item"
    loop:
      over: "/tmp/slices.txt"
```

---

## Model Assignments

| Agent | Model | Rationale |
|-------|-------|-----------|
| requirements-analyst | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient for extraction |
| architect | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Planning/reasoning strength |
| ui-spec-writer | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| planner | `nvidia-nim/moonshotai/kimi-k2.5` | Free, sufficient |
| spec-reviewer | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Strongest NIM reasoning |
| code-executor | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding specialist |
| test-writer | `nvidia-nim/qwen/qwen3-coder-480b-a35b-instruct` | Coding specialist |
| test-runner | `nvidia-nim/moonshotai/kimi-k2.5` | Just runs bash |
| qc-agent | `nvidia-nim/nvidia/nemotron-3-super-120b-a12b` | Strongest NIM reasoning |

---

## Usage

### Run Spec Pipeline

```bash
lobster run \
  --file ~/agent-orchestration-frameworks/workflows/spec-pipeline.lobster \
  --args-json '{"project_dir":"/home/d-tuned/projects/gap-lens-dilution-filter","feature_name":"gap-lens-dilution-filter"}'
```

### Run Forge Pipeline (single slice)

```bash
lobster run \
  --file ~/agent-orchestration-frameworks/workflows/forge-pipeline.lobster \
  --args-json '{"project_dir":"/home/d-tuned/projects/gap-lens-dilution-filter","feature_name":"gap-lens-dilution-filter","slice_id":"1"}'
```

### Run Full Master Pipeline

```bash
lobster run \
  --file ~/agent-orchestration-frameworks/workflows/master.lobster \
  --args-json '{"project_dir":"/home/d-tuned/projects/gap-lens-dilution-filter","feature_name":"gap-lens-dilution-filter"}'
```

---

## Resuming Halted Workflows

If a workflow halts for approval:

```bash
# List halted workflows
lobster list --status halted

# Resume with token
lobster resume --token <resume-token>
```

**Compact Resume Tokens:** Lobster stores workflow resume state under its state dir and hands back a small token key (not the full state).

---

## Error Handling & Retries

| Failure | Action |
|---------|--------|
| Agent timeout | Retry once, then escalate |
| Test failure | Retry code-executor (max 3), then HALT |
| QC CHANGES_REQUESTED | Loop with max 2 iterations, then HALT |
| Approval timeout | Send reminder, keep halted |
| Tool error | Log and HALT |

---

## File Structure

```
~/agent-orchestration-frameworks/
├── LOBSTER-HARNESS.md              # This document
├── workflows/                       # Lobster workflow files
│   ├── spec-pipeline.lobster
│   ├── forge-pipeline.lobster
│   ├── master.lobster
│   └── qc-sub.lobster
└── MERGER_DECISION_RECORD.md       # Existing framework docs

~/projects/{feature}/
├── INTAKE.md                        # Project anchor
├── specs/                           # Generated by spec pipeline
│   ├── 01-REQUIREMENTS.md
│   ├── 02-ARCHITECTURE.md
│   ├── 03-UI-SPEC.md
│   ├── 04-ROADMAP.md
│   └── 05-REVIEW.md
├── src/                             # Generated by forge pipeline
└── tests/                           # Generated by forge pipeline
```

---

## Open Questions / Verification Needed

1. **llm.invoke syntax:** Verify exact CLI syntax for `llm.invoke` with `--system` and `--prompt`
2. **Sub-workflow loops:** Confirm PR #20 loop syntax is merged and available
3. **JSON output:** Verify `output.format: json` syntax for structured responses
4. **Resume tokens:** Test approval/resume flow end-to-end
5. **Environment variables:** Confirm `$HOME` and variable expansion in `run:` commands

---

## Next Steps

1. [ ] Install Lobster: `npm install -g @openclaw/lobster`
2. [ ] Create workflow directory: `mkdir -p ~/agent-orchestration-frameworks/workflows`
3. [ ] Verify `llm.invoke` CLI syntax
4. [ ] Write minimal test workflow (hello-world)
5. [ ] Test approval/resume flow
6. [ ] Implement spec-pipeline.lobster
7. [ ] Test with real project

---

**END OF HARNESS SPEC**
