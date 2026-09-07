#!/usr/bin/env python3
import json, re, subprocess, sys

SECRET_PATTERNS = [
    r"(?i)(api[_-]?key|secret[_-]?key|password)\s*=\s*['\"][^'\"\s]{6,}['\"]",
    r"ghp_[A-Za-z0-9]{20,}",
    r"gho_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"sk_live_[A-Za-z0-9]{10,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]

def scan(text):
    for pat in SECRET_PATTERNS:
        m = re.search(pat, text or "")
        if m:
            return m.group(0)[:40]
    return None

def block(reason):
    print(f"BLOCKED by block-secrets hook: {reason}", file=sys.stderr)
    sys.exit(2)

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
ti = data.get("tool_input", {})

if tool == "Bash":
    cmd = ti.get("command", "")
    if re.search(r"\bgit\s+(add|commit)\b", cmd) and re.search(r"(^|[\s/])\.env(\.[a-zA-Z]+)?(\s|$)", cmd) and ".env.example" not in cmd:
        block(f"command references a .env file: {cmd}")
    if re.search(r"\bgit\s+commit\b", cmd):
        try:
            staged = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, timeout=10).stdout
        except Exception:
            staged = ""
        hit = scan(staged)
        if hit:
            block(f"staged diff contains what looks like a secret: {hit}...")

elif tool in ("Write", "Edit"):
    path = ti.get("file_path", "") or ""
    if re.search(r"(^|[\\/])\.env(\.[a-zA-Z]+)?$", path) and not path.endswith(".env.example"):
        block(f"writing directly to {path} is not allowed")
    content = ti.get("content") or ti.get("new_str") or ""
    hit = scan(content)
    if hit:
        block(f"content contains what looks like a secret: {hit}...")

sys.exit(0)
