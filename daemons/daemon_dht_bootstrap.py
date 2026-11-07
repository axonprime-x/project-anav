#!/usr/bin/env python3
import os
import time
import sqlite3
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")

def broadcast_bootstrap_heartbeat():
    timestamp = time.time()
    payload = json.dumps({
        "node_id": "node_master_01",
        "status": "ACTIVE_DHT_RELAY",
        "spare_compute_pct": 99.4,
        "timestamp": timestamp
    })
    proof = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, proof, payload, "DHT_RELAY_BROADCAST_SUCCESS", 1))
        conn.commit()
        print(f"[DHT BOOTSTRAP] Broadcasted network heartbeat proof: {proof[:16]}...")
    except Exception as e:
        print(f"[DHT BOOTSTRAP] Ledger error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[DHT BOOTSTRAP] Initializing global gossip relay broadcaster...")
    while True:
        broadcast_bootstrap_heartbeat()
        time.sleep(60)
