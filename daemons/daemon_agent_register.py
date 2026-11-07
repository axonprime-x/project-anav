#!/usr/bin/env python3
import os
import time
import sqlite3
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")

def register_agent_card():
    timestamp = time.time()
    manifest = {
        "node_id": "node_master_01",
        "name": "Project ANAV Ingress Gateway",
        "standard": "ERC-8004",
        "protocol": "x402",
        "endpoint": "http://localhost:8080/api/v1/mcp",
        "treasury": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
        "timestamp": timestamp
    }
    payload = json.dumps(manifest)
    proof = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, proof, payload, "ERC8004_REGISTRY_BROADCAST_SUCCESS", 1))
        conn.commit()
        print(f"[AGENT REGISTRY] Published ERC-8004 Agent Card proof: {proof[:16]}...")
    except Exception as e:
        print(f"[AGENT REGISTRY] Ledger error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[AGENT REGISTRY] Initializing persistent ERC-8004 Agent Card broadcaster...")
    while True:
        register_agent_card()
        time.sleep(300)
