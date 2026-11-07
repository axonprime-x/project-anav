#!/usr/bin/env python3
import os
import time
import sqlite3
import hashlib
import urllib.request
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")
TWIN_PORT_PRIMARY = 8080
TWIN_PORT_SECONDARY = 8081

def execute_synthetic_handshake():
    timestamp = time.time()
    payload = json.dumps({
        "emitter": "node_master_twin_02",
        "receiver": "node_master_01",
        "action": "synthetic_proof_ping",
        "timestamp": timestamp
    })
    proof = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, proof, payload, "SYNTHETIC_TWIN_HANDSHAKE_SUCCESS", 1))
        conn.commit()
        print(f"[TWIN SIMULATOR] Generated synthetic micro-tx proof: {proof[:16]}...")
    except Exception as e:
        print(f"[TWIN SIMULATOR] Ledger error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[TWIN SIMULATOR] Internal proof loop online. Emulating M2M traffic...")
    while True:
        execute_synthetic_handshake()
        time.sleep(30)
