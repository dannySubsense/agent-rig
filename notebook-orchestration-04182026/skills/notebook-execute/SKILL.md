---
name: notebook-execute
description: |
  Step-by-step process for executing a Jupyter notebook and producing the _executed version.
  Pure execution — no judgment, no modification.
allowed-tools: Read, Bash, Glob
---

# Notebook Execute

Procedural guide for executing a notebook end-to-end and capturing the result.

## Goal

Run the notebook in a clean kernel, produce a `_executed.ipynb` with all outputs embedded, and report whether every cell ran cleanly.

You are a mechanical executor. You do not fix errors. You do not judge outputs. You run and report.

---

## Step 1: Load the Contract

Read and extract:
- `INPUT_PATH` — the .ipynb to execute
- `OUTPUT_PATH` — where to write the _executed.ipynb (default: alongside input with `_executed` suffix before `.ipynb`)
- `TIMEOUT_PER_CELL` — seconds, default 600
- `KERNEL_NAME` — default `python3`

## Step 2: Verify Inputs

```bash
# Input exists
test -f "$INPUT_PATH" || HALT "Input notebook not found"

# Valid JSON
python3 -c "import json; json.load(open('$INPUT_PATH'))" || HALT "Input is not valid JSON"

# jupyter / nbconvert installed
which jupyter >/dev/null || HALT "jupyter not installed"
```

## Step 3: Execute

Use nbconvert with `--to notebook --execute` and `--allow-errors=false` so failures halt execution and surface the error cell:

```bash
jupyter nbconvert \
  --to notebook \
  --execute \
  --ExecutePreprocessor.timeout="$TIMEOUT_PER_CELL" \
  --ExecutePreprocessor.kernel_name="$KERNEL_NAME" \
  --output "$OUTPUT_PATH" \
  "$INPUT_PATH" 2>&1 | tee /tmp/notebook_exec.log
```

## Step 4: Analyze the Result

Two cases:

### Clean run

If `nbconvert` exits 0:
- `OUTPUT_PATH` exists and is valid JSON
- All cells have outputs
- No cell has an `error` output type

Verify:
```bash
python3 <<EOF
import json
nb = json.load(open("$OUTPUT_PATH"))
cells = nb["cells"]
code = [c for c in cells if c["cell_type"] == "code"]
errors = [
    (i, c) for i, c in enumerate(code)
    if any(o.get("output_type") == "error" for o in c.get("outputs", []))
]
print(f"code_cells={len(code)} errors={len(errors)}")
EOF
```

Collect:
- Total cells executed
- Duration (from log)
- Warnings count (grep the log for `UserWarning`, `DeprecationWarning`, etc.)

### Cell error

If `nbconvert` exits non-zero:
- `OUTPUT_PATH` still exists (nbconvert writes partial output)
- At least one cell has an error output
- The first cell with an error is the failure point

Extract:
- Failing cell index
- Exception type and message
- Last 5 lines of traceback

```bash
python3 <<EOF
import json
nb = json.load(open("$OUTPUT_PATH"))
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code": continue
    for o in c.get("outputs", []):
        if o.get("output_type") == "error":
            print(f"FAILED_CELL={i}")
            print(f"ENAME={o.get('ename')}")
            print(f"EVALUE={o.get('evalue')}")
            print("TRACEBACK:")
            for line in o.get("traceback", [])[-5:]:
                print(line)
            exit()
EOF
```

## Step 5: Return Report

### On clean run

```
✅ EXECUTION CLEAN

Input: [INPUT_PATH]
Output: [OUTPUT_PATH]
Cells executed: [N]
Duration: [MM:SS]
Warnings: [count — brief list if any]

Ready for: @notebook-qc

Status: COMPLETE
```

### On cell error

```
❌ EXECUTION FAILED

Input: [INPUT_PATH]
Output: [OUTPUT_PATH] (partial — contains error cell)
Cells executed: [N of M]
Failed cell: [index]
Error: [ENAME: EVALUE]

Traceback (last 5 lines):
[snippet]

Needs: @notebook-builder to fix cell [index]
Likely cause: [brief diagnosis — schema mismatch, NULL handling, dependency?]

Status: FAILED
```

---

## Step 6: Clean Up

Remove `/tmp/notebook_exec.log` if present. Do not leave artifacts outside the expected output path.

---

## HALT Conditions

HALT if:
- Input notebook missing
- Input is not valid JSON
- jupyter/nbconvert not installed
- Kernel `$KERNEL_NAME` not available
- Output path parent directory doesn't exist and cannot be created
- A cell exceeds `$TIMEOUT_PER_CELL` — report which cell, do not retry

---

## What you do NOT do

- Modify cells to make them run
- Re-execute after failure
- Install missing packages
- Change the kernel
- Skip cells
- Judge whether the output "looks right" — that's @notebook-qc and @frank
