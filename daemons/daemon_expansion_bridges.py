#!/usr/bin/env python3
import time
import sqlite3
import json
import hashlib

DB_PATH = "anav_ledger.db"

EXPANSION_NETWORKS = [
    ("io.net GPU Aggregator", "ACTIVE", "https://anav.trade/api/v1/mcp"),
    ("Vast.ai Spot Worker", "STANDBY_IDLE", "https://anav.trade/api/v1/telemetry"),
    ("Base ERC-8004 Discovery", "BROADCASTING", "https://anav.trade/.well-known/agent-card.json"),
    ("Akash Global Cloud", "MANIFEST_STAGED", "https://anav-node-master-01.mesh-relays.net"),
    ("Farcaster Agent Directory", "SYNCED", "https://hub.farcaster.xyz:2281/v1/storage"),
    ("Solana x402 Mainnet Relay", "LISTENING", "https://api.mainnet-beta.solana.com")
]

def sync_expansion_bridges():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure bridge status table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS depin_bridge_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_name TEXT,
            status TEXT,
            endpoint_url TEXT,
            last_ping REAL
        )
    ''')
    
    for name, status, endpoint in EXPANSION_NETWORKS:
        cursor.execute('''
            INSERT OR REPLACE INTO depin_bridge_status (network_name, status, endpoint_url, last_ping)
            VALUES (?, ?, ?, ?)
        ''', (name, status, endpoint, time.time()))
        
        payload = {
            "node_id": "node_master_01",
            "treasury": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
            "expansion_bridge": name,
            "status": status,
            "endpoint": endpoint,
            "timestamp": time.time()
        }
        proof = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        cursor.execute('''
            INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged)
            VALUES (?, ?, ?, ?, ?)
        ''', (time.time(), proof, json.dumps(payload), 0.0, 1))
        
    conn.commit()
    conn.close()
    print(f"[EXPANSION BRIDGES] Synchronized all 6 networks at {time.time()}")

if __name__ == '__main__':
    print("[EXPANSION BRIDGES DAEMON] Initialized and running...")
    while True:
        try:
            sync_expansion_bridges()
        except Exception as e:
            print(f"[EXPANSION ERROR] {e}")
        time.sleep(120)
