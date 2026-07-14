# Lobster Harness Test Log

**Project:** Lobster Harness Setup  
**Status:** In Progress  
**Document:** Test results and verification steps  

---

## 2026-03-25 Test Session

### Installation

**Lobster CLI:**
- Cloned from https://github.com/openclaw/lobster
- Location: `~/lobster/`
- Built with `npx tsc -p tsconfig.json`
- Executable: `~/lobster/bin/lobster.js`

**Test Project:**
- Location: `~/test-lobster-harness/`
- Contains: INTAKE.md, specs/, src/, tests/ directories
- Purpose: Minimal test of harness (to be deleted after verification)

### Test 1: Basic Workflow Execution

**Workflow:** `~/agent-orchestration-frameworks/workflows/test-spec-pipeline.lobster`

```yaml
steps:
  - id: hello
    run: echo "Hello from Lobster"
  - id: check_files
    run: ls -la ${project_dir}
  - id: test_approval
    approval: "This is a test approval. Approve to continue?"
  - id: complete
    run: echo "Pipeline complete"
```

**Execution:**
```bash
node ~/lobster/bin/lobster.js run \
  --mode tool \
  --file test-spec-pipeline.lobster \
  --args-json '{"project_dir":"/home/d-tuned/test-lobster-harness"}'
```

**Result:** ✅ SUCCESS

**Output:**
```json
{
  "protocolVersion": 1,
  "ok": true,
  "status": "needs_approval",
  "requiresApproval": {
    "prompt": "This is a test approval. Approve to continue?",
    "resumeToken": "eyJwcm90b2NvbFZlcnNpb24iOjEsInYiOjEsImtpbmQiOiJ3b3JrZmxvdy1maWxlIiwic3RhdGVLZXkiOiJ3b3JrZmxvdy9yZXN1bWVfMTViNDkxZmMtNDQxZC00ZjJlLTk2ODItZTA5ZDFjN2YyODA0In0"
  }
}
```

### Test 2: Resume with Approval

**Command:**
```bash
node ~/lobster/bin/lobster.js resume \
  --token <token> \
  --approve yes
```

**Result:** ✅ SUCCESS

**Output:**
```json
{
  "protocolVersion": 1,
  "ok": true,
  "status": "ok",
  "output": ["Pipeline complete"]
}
```

### Verified Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| Shell command execution | ✅ | `run:` steps work |
| Variable expansion | ✅ | `${project_dir}` resolved correctly |
| Approval gates | ✅ | Halts with resume token |
| Resume flow | ✅ | Completes after approval |
| JSON output mode | ✅ | `--mode tool` produces valid JSON |
| Args passing | ✅ | `--args-json` works |

### Open Questions

1. **llm.invoke syntax** — Need to verify exact command structure
2. **stdin piping** — Test `$step.stdout` reference
3. **Sub-workflow loops** — Verify PR #20 syntax is available
4. **JSON output capture** — Test structured output from llm.invoke

### Next Steps

- [ ] Test llm.invoke with actual model call
- [ ] Create spec-pipeline.lobster with real agent prompts
- [ ] Test sub-workflow with loop
- [ ] Document final harness syntax

---

**END OF TEST LOG**
