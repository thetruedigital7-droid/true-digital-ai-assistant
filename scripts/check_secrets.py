#!/usr/bin/env python3
"""Pre-push check: fail if anything private made it into the repo.

Usage:  python3 scripts/check_secrets.py
Exit code 1 if a finding is reported. Run it before every push, and
again after re-exporting a workflow from n8n.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKIP = {".git", "screenshots"}

PATTERNS = {
    "n8n cloud host": r"[a-z0-9-]+\.app\.n8n\.cloud",
    "webhook path that looks like a UUID": r"webhook(?:-test)?/[0-9a-f]{8}-[0-9a-f]{4}-",
    "ElevenLabs agent id": r"agent_[0-9a-z]{20,}",
    "ElevenLabs API key": r"sk_[0-9a-f]{40,}",
    "OpenAI/Groq/Anthropic-style key": r"\b(sk-[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|sk-ant-[A-Za-z0-9_-]{20,})",
    "Google API key": r"AIza[0-9A-Za-z_-]{35}",
    "Supabase project URL": r"[a-z0-9]{20}\.supabase\.co",
    "JWT (Supabase service key etc.)": r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.",
    "HubSpot private app token": r"pat-[a-z]{2,3}\d?-[0-9a-f-]{20,}",
    "Slack token": r"xox[abpr]-[A-Za-z0-9-]{10,}",
    "Indian mobile number": r"(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b",
    "email address": r"[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9.-]+\.[a-z]{2,}",
}

findings = []

for path in ROOT.rglob("*"):
    if path.is_dir() or any(p in SKIP for p in path.parts) or path.name == "check_secrets.py":
        continue
    try:
        text = path.read_text()
    except UnicodeDecodeError:
        continue
    rel = path.relative_to(ROOT)
    for label, pat in PATTERNS.items():
        for m in re.finditer(pat, text):
            findings.append(f"{rel}: {label}: {m.group(0)[:60]}")

    if path.suffix == ".json" and path.parent.name == "workflows":
        wf = json.loads(text)
        for n in wf.get("nodes", []):
            for ctype, c in (n.get("credentials") or {}).items():
                if "id" in c:
                    findings.append(f"{rel}: credential id left on node '{n['name']}' ({ctype})")
            if "webhookId" in n:
                findings.append(f"{rel}: webhookId left on node '{n['name']}'")
        for key in ("id", "versionId", "meta", "shared", "activeVersion"):
            if key in wf:
                findings.append(f"{rel}: instance field '{key}' present at top level")

if findings:
    print("Private data found — fix before pushing:\n")
    print("\n".join(sorted(set(findings))))
    sys.exit(1)
print("Clean: no keys, webhook URLs, agent ids, credential ids, emails or phone numbers found.")
