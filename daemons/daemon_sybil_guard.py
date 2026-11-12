import os
import time
import sqlite3

LEDGER_DB = 'anav_ledger.db'

def run_sybil_guard():
    print("[SYBIL GUARD] Running Sybil Resistance & Reputation Guard...")
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS node_reputation_registry (
            node_id TEXT PRIMARY KEY,
            reputation_score REAL,
            handshake_failures INTEGER,
            status TEXT,
            last_seen REAL
        )
    ''')
    conn.commit()
    conn.close()
    
    while True:
        try:
            conn = sqlite3.connect(LEDGER_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM node_reputation_registry;")
            conn.close()
        except Exception as e:
            print(f"[SYBIL GUARD] Loop error: {e}")
        time.sleep(60)

if __name__ == '__main__':
    run_sybil_guard()
