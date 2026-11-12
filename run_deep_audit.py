import sqlite3
import json
import os

print("========================================================")
print("       PROJECT ANAV SYSTEM & INGRESS DEEP AUDIT         ")
print("========================================================")

# 1. Inspect Database & Ingress Log State
db_path = "anav_ledger.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
    total_logs = cursor.fetchone()[0]
    print(f"[LEDGER] Total entries in global_ingress_log: {total_logs}")
    
    cursor.execute("SELECT id, timestamp, proof, amount_usdc FROM global_ingress_log ORDER BY id DESC LIMIT 3;")
    print("[LEDGER] Last 3 entries:")
    for row in cursor.fetchall():
        print(f"  -> ID: {row[0]}, Time: {row[1]}, Proof: {row[2][:16]}..., USDC: {row[3]}")
    conn.close()
else:
    print("[WARNING] anav_ledger.db not found in working directory.")

# 2. Check ERC-8004 Agent Card Manifest file
manifest_path = ".well-known/agent-card.json"
if os.path.exists(manifest_path):
    with open(manifest_path, "r", encoding="utf-8") as f:
        card = json.load(f)
    print(f"[MANIFEST] ERC-8004 card loaded successfully for agentId: {card.get('agentId')}")
    print(f"           Endpoints: {card.get('endpoints')}")
    print(f"           Treasury: {card.get('treasury')}")
else:
    print("[WARNING] .well-known/agent-card.json manifest not found.")

# 3. Check Gateway Ingress x402 payment validation logic
gateway_path = "gateway_ingress.py"
if os.path.exists(gateway_path):
    with open(gateway_path, "r", encoding="utf-8") as f:
        gw_code = f.read()
    has_402 = "status_code=402" in gw_code
    has_header = "X-PAYMENT-PROOF" in gw_code
    print(f"[GATEWAY] x402 402-Enforcement Logic Present: {has_402}")
    print(f"[GATEWAY] X-PAYMENT-PROOF Header Binding Present: {has_header}")
else:
    print("[WARNING] gateway_ingress.py not found.")

print("========================================================")
print("                 AUDIT COMPLETE                         ")
print("========================================================")
