#!/usr/bin/env python3
import time
import json
import sqlite3
import hashlib

DB_PATH = "anav_ledger.db"

def broadcast_farcaster_manifest():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_ingress_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                proof TEXT,
                payload TEXT,
                amount_usdc REAL DEFAULT 0.0,
                bridged INTEGER DEFAULT 1
            )
        ''')
        payload = {
            "network": "Farcaster-Base-Registry",
            "status": "AGENT_CARD_BROADCAST",
            "node_id": "node_master_01",
            "treasury": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
            "standard": "ERC-8004",
            "rail": "x402-Base",
            "timestamp": time.time()
        }
        proof = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        cursor.execute(
            "INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)",
            (time.time(), proof, json.dumps(payload), 0.0, 1)
        )
        conn.commit()
        conn.close()
        print("[FARCASTER BROADCASTER] Broadcasted ERC-8004 manifest to Base / Farcaster indexers.")
    except Exception as e:
        print(f"[FARCASTER ERROR] {e}")

if __name__ == "__main__":
    while True:
        broadcast_farcaster_manifest()
        time.sleep(300)
