name: test-spec-pipeline
version: 1.0
description: Minimal test of spec pipeline

args:
  - name: project_dir
    type: string
    required: true

steps:
  - id: hello
    name: Hello Step
    run: echo "Hello from Lobster"
    
  - id: check_files
    name: Check Project Files
    run: ls -la ${project_dir}
    
  - id: test_approval
    name: Test Approval Gate
    depends_on: [check_files]
    approval: "This is a test approval. Approve to continue?"
    
  - id: complete
    name: Complete
    depends_on: [test_approval]
    run: echo "Pipeline complete"
