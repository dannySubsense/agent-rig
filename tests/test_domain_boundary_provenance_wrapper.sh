#!/usr/bin/env bash
# Wrapper-level tests for .claude/hooks/domain-boundary-provenance.sh (Slice 2).
#
# Convention note: this repo's sibling wrapper (.claude/hooks/first-turn-contract.sh) has no
# dedicated wrapper-level test file — its behavior is covered by the probe's own test suite
# (tests/test_first_turn_contract_probe.py) plus a live demonstration. That same probe-suite
# coverage exists here for domain-boundary-provenance.sh's probe
# (tests/test_domain_boundary_provenance_probe.py, Slice 1, 17/17 passing).
#
# This file exists ONLY to cover wrapper-specific logic the probe's own test suite structurally
# cannot reach, because it lives in the bash wrapper itself, not the Python probe:
#   - timeout kill -> fail-open + single write_probe_error entry
#   - non-zero probe exit -> fail-open + single write_probe_error entry
#   - malformed/non-JSON probe stdout on exit 0 -> fail-open + single write_probe_error entry
#   - no double-write when the probe already wrote its own track-record line
#   - $CLAUDE_PROJECT_DIR is guaranteed set (defaulted to repo root) even when unset in env
#
# Run: bash tests/test_domain_boundary_provenance_wrapper.sh
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER="$REPO_DIR/.claude/hooks/domain-boundary-provenance.sh"
TRACK_RECORD="$REPO_DIR/docs/tooling/domain-boundary-provenance-track-record.jsonl"

PASS=0
FAIL=0

# Isolate a fake probe directory so we can swap in stub probes without touching the real one.
FAKE_PROBE_DIR="$(mktemp -d)"
trap 'rm -rf "$FAKE_PROBE_DIR"' EXIT

# Run the wrapper against a stub probe by temporarily pointing REPO_DIR's probe path at a fake
# script. We do this by copying the wrapper into the fake dir with its probe path patched, since
# the wrapper resolves REPO_DIR from its own on-disk location (BASH_SOURCE).
run_with_stub_probe() {
  local stub_script="$1"
  shift
  local fake_repo="$FAKE_PROBE_DIR/repo"
  rm -rf "$fake_repo"
  mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
  cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
  cp "$stub_script" "$fake_repo/scripts/domain_boundary_provenance_probe.py"
  chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"
  echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
    | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
  echo "$fake_repo"
}

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

# --- Test 1: timeout -> fail-open, empty stdout, exit 0, one probe_error entry -----------------
cat >"$FAKE_PROBE_DIR/timeout_probe.py" <<'EOF'
#!/usr/bin/env python3
import time
time.sleep(10)
EOF
chmod +x "$FAKE_PROBE_DIR/timeout_probe.py"

fake_repo="$FAKE_PROBE_DIR/repo"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
cp "$FAKE_PROBE_DIR/timeout_probe.py" "$fake_repo/scripts/domain_boundary_provenance_probe.py"
chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"

# Patch the wrapper's 5s timeout down to 1s so this test doesn't take 5+ seconds.
sed -i 's/timeout 5 /timeout 1 /' "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"

OUT="$(echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
  | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh")"
EXIT_CODE=$?
assert_eq "timeout: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "timeout: wrapper emits nothing on stdout" "" "$OUT"
TR_LINES="$(wc -l < "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" 2>/dev/null || echo 0)"
assert_eq "timeout: exactly one track-record entry written" "1" "$TR_LINES"
TR_CAUSE="$(cat "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["decision"])')"
assert_eq "timeout: track-record decision is probe_error" "probe_error" "$TR_CAUSE"

# --- Test 2: non-zero probe exit -> fail-open + one probe_error entry --------------------------
fake_repo="$FAKE_PROBE_DIR/repo2"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
cat >"$fake_repo/scripts/domain_boundary_provenance_probe.py" <<'EOF'
#!/usr/bin/env python3
import sys
print("boom", file=sys.stderr)
sys.exit(1)
EOF
chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"

OUT="$(echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
  | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh")"
EXIT_CODE=$?
assert_eq "non-zero exit: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "non-zero exit: wrapper emits nothing on stdout" "" "$OUT"
TR_LINES="$(wc -l < "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" 2>/dev/null || echo 0)"
assert_eq "non-zero exit: exactly one track-record entry written" "1" "$TR_LINES"

# --- Test 3: malformed/non-JSON stdout on exit 0 -> fail-open + one probe_error entry ----------
fake_repo="$FAKE_PROBE_DIR/repo3"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
cat >"$fake_repo/scripts/domain_boundary_provenance_probe.py" <<'EOF'
#!/usr/bin/env python3
print("not json at all")
EOF
chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"

OUT="$(echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
  | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh")"
EXIT_CODE=$?
assert_eq "malformed stdout: wrapper exits 0 (fail-open)" "0" "$EXIT_CODE"
assert_eq "malformed stdout: wrapper emits nothing on stdout" "" "$OUT"
TR_LINES="$(wc -l < "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" 2>/dev/null || echo 0)"
assert_eq "malformed stdout: exactly one track-record entry written" "1" "$TR_LINES"

# --- Test 4: no double-write when probe already wrote its own valid entry ----------------------
# A clean exit-0 with a valid block decision means the probe already wrote its own line; the
# wrapper's write_probe_error must not fire on this path at all.
fake_repo="$FAKE_PROBE_DIR/repo4"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
cat >"$fake_repo/scripts/domain_boundary_provenance_probe.py" <<'EOF'
#!/usr/bin/env python3
import json
import os

track_record_path = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", "."), "docs", "tooling",
    "domain-boundary-provenance-track-record.jsonl",
)
os.makedirs(os.path.dirname(track_record_path), exist_ok=True)
with open(track_record_path, "a") as fh:
    fh.write(json.dumps({"decision": "deny", "reason": "stub deny"}) + "\n")
print(json.dumps({"decision": "block", "reason": "stub deny"}))
EOF
chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"

OUT="$(echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
  | env CLAUDE_PROJECT_DIR="$fake_repo" bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh")"
EXIT_CODE=$?
assert_eq "valid deny: wrapper exits 0" "0" "$EXIT_CODE"
assert_eq "valid deny: wrapper relays the block JSON" '{"decision": "block", "reason": "stub deny"}' "$OUT"
TR_LINES="$(wc -l < "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" 2>/dev/null || echo 0)"
assert_eq "valid deny: exactly one track-record entry (no wrapper double-write)" "1" "$TR_LINES"

# --- Test 5: $CLAUDE_PROJECT_DIR is guaranteed set even when unset in env ----------------------
fake_repo="$FAKE_PROBE_DIR/repo5"
rm -rf "$fake_repo"
mkdir -p "$fake_repo/.claude/hooks" "$fake_repo/scripts" "$fake_repo/docs/tooling"
cp "$WRAPPER" "$fake_repo/.claude/hooks/domain-boundary-provenance.sh"
cat >"$fake_repo/scripts/domain_boundary_provenance_probe.py" <<'EOF'
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
chmod +x "$fake_repo/scripts/domain_boundary_provenance_probe.py"

echo '{"session_id":"s1","tool_name":"Edit","tool_input":{"file_path":"x.py"},"cwd":"'"$fake_repo"'"}' \
  | env -u CLAUDE_PROJECT_DIR bash "$fake_repo/.claude/hooks/domain-boundary-provenance.sh" >/dev/null 2>"$FAKE_PROBE_DIR/stderr5.log"
# The wrapper captures the probe's stderr into its own internal temp file and never re-emits it
# to the wrapper's own stderr -- it only threads it through into the track-record entry's
# "probe_error" field (via write_probe_error's "${ERR}" interpolation). So the probe's
# SET:/UNSET message must be read from the track-record entry, not from the wrapper's stderr.
STDERR_CONTENT="$(cat "$fake_repo/docs/tooling/domain-boundary-provenance-track-record.jsonl" \
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
