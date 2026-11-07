import sqlite3
import json
import os

print("========================================================")
print("     PROJECT ANAV EXISTENTIAL CODE & ROUTING AUDIT      ")
print("========================================================")

# 1. Inspect Ingress Route Handlers & x402 Header Enforcement
gw_path = "gateway_ingress.py"
if os.path.exists(gw_path):
    with open(gw_path, "r", encoding="utf-8") as f:
        code = f.read()
    has_mcp = "@app.post(\"/api/v1/mcp\")" in code or "def mcp" in code
    has_x402_header = "X-PAYMENT-PROOF" in code
    has_402_status = "402" in code
    print(f"[INGRESS GATEWAY] /api/v1/mcp route present: {has_mcp}")
    print(f"[INGRESS GATEWAY] X-PAYMENT-PROOF header check: {has_x402_header}")
    print(f"[INGRESS GATEWAY] HTTP 402 challenge enforcement: {has_402_status}")
else:
    print("[ERROR] gateway_ingress.py not found.")

# 2. Inspect ERC-8004 Manifest Schema & Public Endpoints
manifest_path = ".well-known/agent-card.json"
if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"[AGENT MANIFEST] Loaded agentId: {manifest.get('agentId')}")
    print(f"[AGENT MANIFEST] Endpoints advertised: {manifest.get('endpoints')}")
    print(f"[AGENT MANIFEST] Accepted rails: {manifest.get('accepted_rails')}")
else:
    print("[ERROR] .well-known/agent-card.json missing.")

# 3. Inspect Ledger Ingress & Error Logs
db_path = "anav_ledger.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
    print(f"[LEDGER STATE] Total global ingress log records: {cursor.fetchone()[0]}")
    conn.close()

print("========================================================")
print("               AUDIT MAP CHECK COMPLETE                 ")
print("========================================================")
