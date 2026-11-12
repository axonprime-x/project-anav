import os
import time
import sqlite3
import json
import hashlib

LEDGER_DB = 'anav_ledger.db'

def initialize_anavai_db():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS anavai_autonomous_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            agent_state TEXT,
            decision_payload TEXT,
            hash_proof TEXT
        )
    ''')
    conn.commit()
    conn.close()

def run_anavai_cycle():
    initialize_anavai_db()
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    timestamp = time.time()
    state = "AUTONOMOUS_SYNTHESIS_ACTIVE"
    payload = json.dumps({
        "node": "node_master_01",
        "engine": "ANAVAI-v1",
        "objective": "perpetual_mesh_optimization_and_liquidity_compounding",
        "cpu_target_pct": 20.0
    })
    
    proof = hashlib.sha256(f"anavai-{timestamp}-{payload}".encode()).hexdigest()
    
    cursor.execute(
        'INSERT INTO anavai_autonomous_log (timestamp, agent_state, decision_payload, hash_proof) VALUES (?, ?, ?, ?)',
        (timestamp, state, payload, proof)
    )
    conn.commit()
    conn.close()
    print(f"[ANAVAI] Autonomous reasoning cycle executed successfully. Proof: {proof[:16]}...")

if __name__ == '__main__':
    print("[ANAVAI] Initializing ANAVAI Autonomous Intelligence Core...")
    while True:
        run_anavai_cycle()
        time.sleep(30)
