#!/usr/bin/env python3
import os
import time
import json
import sqlite3
import hashlib
import urllib.request

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")
NODE_PUBLIC_URL = os.getenv("ANAV_PUBLIC_URL", "http://localhost:8080")
TREASURY_ADDRESS = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"

def broadcast_discovery_manifest():
    agent_card = {
        "node_id": "node_master_01",
        "status": "ACTIVE_SPRINT_READY",
        "treasury": TREASURY_ADDRESS,
        "ingress_endpoint": f"{NODE_PUBLIC_URL}/api/v1/mcp",
        "protocols": ["x402-Base", "x402-Solana", "ERC-8004"],
        "capabilities": ["m2m-micro-synthesis", "decentralized-compute-spare", "am5-hardware-bounty"],
        "timestamp": time.time()
    }
    
    payload_json = json.dumps(agent_card)
    proof_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (time.time(), proof_hash, payload_json, "GLOBAL_DISCOVERY_MANIFEST_BROADCAST", 1))
        conn.commit()
        print(f"[DISCOVERY] Published ERC-8004 Agent Card manifest | Proof: {proof_hash[:16]}...")
    except Exception as e:
        print(f"[DISCOVERY] Ledger write error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[DISCOVERY] Global Discovery & Crawler Indexer Broadcaster online...")
    while True:
        broadcast_discovery_manifest()
        time.sleep(60)
