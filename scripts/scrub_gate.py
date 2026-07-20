#!/usr/bin/env python3
"""scrub_gate.py — block internal infra + secrets from being committed to this public repo.

Single detection engine, called by both the local pre-commit hook (.githooks/pre-commit)
and CI (.github/workflows/scrub-gate.yml) so the pattern list never forks.

  scrub_gate.py            scan STAGED content (pre-commit default)
  scrub_gate.py --all      scan all tracked files (CI / manual full sweep)

Exit 0 = clean, 1 = one or more hits (blocks the commit / fails CI).

Detects, by default (block-by-default; carve out intentional examples in the allowlist):
  - Private / tailnet IPv4: 10/8, 172.16/12, 192.168/16, 169.254/16, and 100.64/10 (CGNAT).
    Exact range membership via `ipaddress` — a public IP like 1.2.3.4 is NOT flagged.
  - Common secret shapes: sk-…, ghp_/gho_/github_pat_…, AKIA…, xox[baprs]-…,
    and postgres/mysql URLs carrying a real (non-placeholder) password.

Allowlist: scripts/scrub-gate-allow.txt — one exact token per line (# comments ok).
The CGNAT *range notation* 100.64.0.0/10 is allowlisted so docs can describe what to block.
"""
import ipaddress
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOW_FILE = ROOT / "scripts" / "scrub-gate-allow.txt"

# Files the gate must never scan (they legitimately contain patterns/examples).
SELF_SKIP = {"scripts/scrub_gate.py", "scripts/scrub-gate-allow.txt"}
SKIP_PREFIXES = (".git/", "node_modules/")

FORBIDDEN_NETS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("100.64.0.0/10"),  # Tailscale CGNAT — the leak we rewrote out
]

IP_RE = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

SECRET_RES = [
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b")),
    ("aws-akid", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]
# DB URL with a password that is NOT an obvious placeholder.
DBURL_RE = re.compile(r"\b(?:postgres(?:ql)?|mysql)://[^:@\s/]+:([^@\s/]+)@")
PLACEHOLDER_RE = re.compile(r"^(?:<.*>|\$\{?\w+\}?|\*+|password|changeme|your[_-].*)$", re.I)


def load_allow():
    allow = set()
    if ALLOW_FILE.exists():
        for line in ALLOW_FILE.read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                allow.add(line)
    return allow


def is_forbidden_ip(tok):
    try:
        ip = ipaddress.ip_address(tok)
    except ValueError:
        return False
    return any(ip in net for net in FORBIDDEN_NETS)


def scan_text(text, allow):
    """Yield (lineno, token, reason) for every hit in text."""
    for i, line in enumerate(text.splitlines(), 1):
        for tok in IP_RE.findall(line):
            if tok in allow:
                continue
            if is_forbidden_ip(tok):
                yield i, tok, "private/tailnet IP"
        for reason, rx in SECRET_RES:
            for m in rx.findall(line):
                if m not in allow:
                    yield i, m, reason
        for m in DBURL_RE.finditer(line):
            pw = m.group(1)
            if not PLACEHOLDER_RE.match(pw) and pw not in allow:
                yield i, m.group(0), "db-url with real password"


def git(*args):
    # Decode with errors="replace" so binary blobs (e.g. a staged .pyc or image)
    # degrade to replacement chars instead of crashing the gate.
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True).stdout
    return out.decode("utf-8", errors="replace")


def staged_files():
    out = git("diff", "--cached", "--name-only", "--diff-filter=ACM")
    return [f for f in out.splitlines() if f]


def all_files():
    return [f for f in git("ls-files").splitlines() if f]


def read(path, staged):
    if staged:
        return git("show", f":{path}")
    p = ROOT / path
    try:
        return p.read_text(errors="replace")
    except (OSError, UnicodeDecodeError):
        return ""


def skip(path):
    return path in SELF_SKIP or path.startswith(SKIP_PREFIXES)


def main():
    staged = "--all" not in sys.argv
    allow = load_allow()
    files = staged_files() if staged else all_files()
    hits = []
    for f in files:
        if skip(f):
            continue
        for lineno, tok, reason in scan_text(read(f, staged), allow):
            hits.append((f, lineno, tok, reason))

    if not hits:
        print(f"scrub-gate: clean ({len(files)} files, {'staged' if staged else 'all-tracked'})")
        return 0

    print("scrub-gate: BLOCKED — internal infra / secrets detected:\n", file=sys.stderr)
    for f, lineno, tok, reason in hits:
        print(f"  {f}:{lineno}: {reason}: {tok}", file=sys.stderr)
    print(
        "\nRemove the value (use a placeholder + resolve at runtime — see DDR-003), "
        "or if it is a legitimate example add the exact token to scripts/scrub-gate-allow.txt.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
