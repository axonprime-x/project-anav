#!/usr/bin/env python3
import time
import sqlite3
import json
import hashlib

DB_PATH = "anav_ledger.db"

def pulse_bridges():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT network_name, endpoint_url FROM depin_bridge_status;")
    bridges = cursor.fetchall()
    
    for name, endpoint in bridges:
        pulse_data = {
            "node_id": "node_master_01",
            "bridge": name,
            "endpoint": endpoint,
            "status": "HEARTBEAT_ACTIVE",
            "timestamp": time.time()
        }
        proof = hashlib.sha256(json.dumps(pulse_data).encode()).hexdigest()
        cursor.execute('''
            INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged)
            VALUES (?, ?, ?, ?, ?)
        ''', (time.time(), proof, json.dumps(pulse_data), 0.0, 1))
        
    conn.commit()
    conn.close()
    print(f"[MULTI-NETWORK SYNC] Pulsed {len(bridges)} bridges successfully at {time.time()}")

if __name__ == '__main__':
    print("[MULTI-NETWORK SYNC DAEMON] Initialized and running...")
    while True:
        try:
            pulse_bridges()
        except Exception as e:
            print(f"[SYNC ERROR] {e}")
        time.sleep(300)
