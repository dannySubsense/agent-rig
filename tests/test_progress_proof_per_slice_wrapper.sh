#!/usr/bin/env bash
# Wrapper-level tests for .claude/hooks/progress-proof-per-slice.sh (Slice 2).
#
# Convention note: this repo's established pattern (tests/test_domain_boundary_provenance_wrapper.sh)
# covers wrapper-specific logic the probe's own test suite structurally cannot reach, because it
# lives in the bash wrapper itself, not the Python probe. This file follows that same pattern for
# progress-proof-per-slice.sh (spec §6):
#   - outer timeout kill (30s, spec §6) -> fail-open + single write_probe_error entry
#   - non-zero probe exit -> fail-open + single write_probe_error entry
#   - malformed/non-JSON probe stdout on exit 0 -> fail-open + single write_probe_error entry
#   - no double-write when the probe already wrote its own track-record line
#   - $CLAUDE_PROJECT_DIR is guaranteed set (defaulted to repo root) even when unset in env
#   - a valid deny path relays correctly with exactly one track-record entry
#
# Run: bash tests/test_progress_proof_per_slice_wrapper.sh
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="$REPO_DIR/.claude/hooks/progress-proof-per-slice.sh"
TRACK_RECORD_NAME="progress-proof-per-slice-track-record.jsonl"

PASS=0
FAIL=0

FAKE_PROBE_DIR="$(mktemp -d)"
trap 'rm -rf "$FAKE_PROBE_DIR"' EXIT

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  if [ "$expected" = "$actual" ]; then
    echo "PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $desc (expected [$expected] got [$actual])"
    FAIL=$((FAIL + 1))
  fi
}

STDIN_PAYLOAD='{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"PROGRESS.md","old_string":"- [ ] Slice 1: X","new_string":"- [x] Slice 1: X"},"cwd":"REPLACE_ME"}'

# --- Test 1: timeout -> fail-open, empty stdout, exit 0, one probe_error entry -----------------
fake_repo="$FAKE_PROBE_DIR/repo1"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"
cat >"$fake_repo/scripts/progress_proof_per_slice_probe.py" <<'EOF'
#!/usr/bin/env python3
import time
time.sleep(10)
EOF
chmod +x "$fake_repo/scripts/progress_proof_per_slice_probe.py"

# Patch the wrapper's 30s outer timeout down to 1s so this test doesn't take 30+ seconds.
sed -i 's/timeout 30 /timeout 1 /' "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"

PAYLOAD="${STDIN_PAYLOAD/REPLACE_ME/$fake_repo}"
OUT="$(echo "$PAYLOAD" | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/progress-proof-per-slice.sh")"
EXIT_CODE=$?
assert_eq "timeout: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "timeout: wrapper emits nothing on stdout" "" "$OUT"
TR_FILE="$fake_repo/docs/tooling/$TRACK_RECORD_NAME"
TR_LINES="$(wc -l < "$TR_FILE" 2>/dev/null || echo 0)"
assert_eq "timeout: exactly one track-record entry written" "1" "$TR_LINES"
TR_CAUSE="$(cat "$TR_FILE" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["decision"])')"
assert_eq "timeout: track-record decision is probe_error" "probe_error" "$TR_CAUSE"

# --- Test 2: non-zero probe exit -> fail-open + one probe_error entry --------------------------
fake_repo="$FAKE_PROBE_DIR/repo2"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"
cat >"$fake_repo/scripts/progress_proof_per_slice_probe.py" <<'EOF'
#!/usr/bin/env python3
import sys
print("boom", file=sys.stderr)
sys.exit(1)
EOF
chmod +x "$fake_repo/scripts/progress_proof_per_slice_probe.py"

PAYLOAD="${STDIN_PAYLOAD/REPLACE_ME/$fake_repo}"
OUT="$(echo "$PAYLOAD" | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/progress-proof-per-slice.sh")"
EXIT_CODE=$?
assert_eq "non-zero exit: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "non-zero exit: wrapper emits nothing on stdout" "" "$OUT"
TR_FILE="$fake_repo/docs/tooling/$TRACK_RECORD_NAME"
TR_LINES="$(wc -l < "$TR_FILE" 2>/dev/null || echo 0)"
assert_eq "non-zero exit: exactly one track-record entry written" "1" "$TR_LINES"

# --- Test 3: malformed/non-JSON stdout on exit 0 -> fail-open + one probe_error entry ----------
fake_repo="$FAKE_PROBE_DIR/repo3"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"
cat >"$fake_repo/scripts/progress_proof_per_slice_probe.py" <<'EOF'
#!/usr/bin/env python3
print("not json at all")
EOF
chmod +x "$fake_repo/scripts/progress_proof_per_slice_probe.py"

PAYLOAD="${STDIN_PAYLOAD/REPLACE_ME/$fake_repo}"
OUT="$(echo "$PAYLOAD" | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/progress-proof-per-slice.sh")"
EXIT_CODE=$?
assert_eq "malformed stdout: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "malformed stdout: wrapper emits nothing on stdout" "" "$OUT"
TR_FILE="$fake_repo/docs/tooling/$TRACK_RECORD_NAME"
TR_LINES="$(wc -l < "$TR_FILE" 2>/dev/null || echo 0)"
assert_eq "malformed stdout: exactly one track-record entry written" "1" "$TR_LINES"

# --- Test 4: no double-write when probe already wrote its own valid entry ----------------------
# A clean exit-0 with a valid block decision means the probe already wrote its own line; the
# wrapper's write_probe_error must not fire on this path at all.
fake_repo="$FAKE_PROBE_DIR/repo4"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"
cat >"$fake_repo/scripts/progress_proof_per_slice_probe.py" <<EOF
#!/usr/bin/env python3
import json
import os

track_record_path = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", "."), "docs", "tooling",
    "$TRACK_RECORD_NAME",
)
os.makedirs(os.path.dirname(track_record_path), exist_ok=True)
with open(track_record_path, "a") as fh:
    fh.write(json.dumps({"decision": "deny", "reason": "stub deny"}) + "\n")
print(json.dumps({"decision": "block", "reason": "stub deny"}))
EOF
chmod +x "$fake_repo/scripts/progress_proof_per_slice_probe.py"

PAYLOAD="${STDIN_PAYLOAD/REPLACE_ME/$fake_repo}"
OUT="$(echo "$PAYLOAD" | env CLAUDE_PROJECT_DIR="$fake_repo" bash "$fake_repo/.claude/hooks/progress-proof-per-slice.sh")"
EXIT_CODE=$?
assert_eq "valid deny: wrapper exits 0" "0" "$EXIT_CODE"
assert_eq "valid deny: wrapper relays the block JSON" '{"decision": "block", "reason": "stub deny"}' "$OUT"
TR_FILE="$fake_repo/docs/tooling/$TRACK_RECORD_NAME"
TR_LINES="$(wc -l < "$TR_FILE" 2>/dev/null || echo 0)"
assert_eq "valid deny: exactly one track-record entry (no wrapper double-write)" "1" "$TR_LINES"

# --- Test 5: $CLAUDE_PROJECT_DIR is guaranteed set even when unset in env ----------------------
fake_repo="$FAKE_PROBE_DIR/repo5"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/progress-proof-per-slice.sh"
cat >"$fake_repo/scripts/progress_proof_per_slice_probe.py" <<'EOF'
#!/usr/bin/env python3
import os
import sys
val = os.environ.get("CLAUDE_PROJECT_DIR")
if val:
    print("SET:" + val, file=sys.stderr)
else:
    print("UNSET", file=sys.stderr)
sys.exit(1)
EOF
chmod +x "$fake_repo/scripts/progress_proof_per_slice_probe.py"

PAYLOAD="${STDIN_PAYLOAD/REPLACE_ME/$fake_repo}"
echo "$PAYLOAD" \
  | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/progress-proof-per-slice.sh" >/dev/null 2>"$FAKE_PROBE_DIR/stderr5.log"
# The wrapper captures the probe's stderr into its own internal temp file and never re-emits it
# to the wrapper's own stderr -- it only threads it through into the track-record entry's
# "probe_error" field (via write_probe_error's "${ERR}" interpolation). So the probe's
# SET:/UNSET message must be read from the track-record entry, not from the wrapper's stderr.
TR_FILE="$fake_repo/docs/tooling/$TRACK_RECORD_NAME"
STDERR_CONTENT="$(cat "$TR_FILE" \
  | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["probe_error"])')"
case "$STDERR_CONTENT" in
  *SET:*) RESULT="SET" ;;
  *) RESULT="UNSET" ;;
esac
assert_eq "\$CLAUDE_PROJECT_DIR defaulted to a non-empty value when unset in env" "SET" "$RESULT"
# The wrapper resolves REPO_DIR from its own on-disk location; since we copied the wrapper into
# $fake_repo, the default must resolve to $fake_repo (symlink-resolved).
EXPECTED_REPO="$(cd "$fake_repo" && pwd -P)"
ACTUAL_VAL="${STDERR_CONTENT#*SET:}"
assert_eq "\$CLAUDE_PROJECT_DIR defaults to the wrapper's own resolved repo root" "$EXPECTED_REPO" "$ACTUAL_VAL"

echo
echo "----------------------------------------"
echo "PASS: $PASS  FAIL: $FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
