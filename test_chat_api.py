#!/usr/bin/env python3
"""
Quick smoke-test for the PolyAI Studio chat REST API.
Usage: python3 test_chat_api.py
Reads POLY_ADK_KEY from ~/.config/claude/secrets.env
"""
import json, os, sys
from pathlib import Path

# ── Load key from secrets.env ──────────────────────────────────────────────
secrets = Path.home() / ".config/claude/secrets.env"
for line in secrets.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

KEY = os.environ.get("POLY_ADK_KEY", "")
if not KEY:
    sys.exit("❌  POLY_ADK_KEY not set in ~/.config/claude/secrets.env")

# ── Config ─────────────────────────────────────────────────────────────────
BASE    = "https://api.eu.poly.ai"
ACCOUNT = "poly-srpski-euw"
PROJECT = "PROJECT-LEQWVUHR"
ENV     = "sandbox"      # change to "live" once deployed to live env
CHANNEL = "webchat.polyai"

HEADERS = {
    "X-API-KEY":    KEY,
    "Content-Type": "application/json",
}

# ── Helpers ────────────────────────────────────────────────────────────────
try:
    import urllib.request as req
    import urllib.error

    def post(path: str, body: dict) -> dict:
        url  = BASE + path
        data = json.dumps(body).encode()
        r    = req.urlopen(req.Request(url, data=data, headers=HEADERS, method="POST"), timeout=10)
        return json.loads(r.read())

except Exception as e:
    sys.exit(f"Import error: {e}")


def pretty(label: str, data: dict):
    print(f"\n{'─'*60}")
    print(f"  {label}")
    print('─'*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Test conversation ───────────────────────────────────────────────────────
chat_path = f"/adk/v1/accounts/{ACCOUNT}/projects/{PROJECT}/chat"

print(f"\n🔗  {BASE}{chat_path}")
print(f"    env={ENV}  channel={CHANNEL}\n")

# 1. Start session
print("1/3  Creating chat session …")
try:
    session = post(chat_path, {"client_env": ENV, "channel": CHANNEL})
except urllib.error.HTTPError as e:
    body = e.read().decode()
    sys.exit(f"❌  {e.code} {e.reason}\n{body}")

pretty("Session created", session)
conv_id = session.get("conversation_id") or session.get("id") or ""
greeting = session.get("response") or session.get("message") or session.get("text") or "(no text)"
print(f"\n✅  Agent greeting: {greeting}")
print(f"    conversation_id: {conv_id}")

if not conv_id:
    sys.exit("❌  No conversation_id in response — check the session payload above")

# 2. Send a message in Serbian
msg_path = f"{chat_path}/{conv_id}"
print(f"\n2/3  Sending message in Serbian …")
try:
    reply = post(msg_path, {
        "message":       "Kakav je status leta JU500?",
        "client_env":    ENV,
        "asr_lang_code": "sr-RS",
    })
except urllib.error.HTTPError as e:
    body = e.read().decode()
    sys.exit(f"❌  {e.code} {e.reason}\n{body}")

pretty("Agent reply", reply)
text = reply.get("response") or reply.get("message") or reply.get("text") or json.dumps(reply)
print(f"\n✅  Agent says: {text}")

# 3. End session
print(f"\n3/3  Ending session …")
try:
    end = post(f"{msg_path}/end", {"client_env": ENV})
    print(f"✅  Session ended: {end}")
except Exception as e:
    print(f"⚠️   End session failed (non-critical): {e}")

print("\n🎉  Done — API is reachable and returning responses.\n")
