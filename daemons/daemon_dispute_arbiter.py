import os
import time
import sqlite3
import json

LEDGER_DB = 'anav_ledger.db'

def init_dispute_db():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dispute_arbitration_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            proof_reference TEXT,
            dispute_reason TEXT,
            arbitration_verdict TEXT,
            penalty_applied INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def process_pending_disputes():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_disputes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proof_ref TEXT,
            query TEXT,
            claimed_error TEXT,
            status TEXT DEFAULT 'PENDING'
        )
    ''')
    
    cursor.execute("SELECT id, proof_ref, query, claimed_error FROM client_disputes WHERE status = 'PENDING';")
    disputes = cursor.fetchall()
    
    for dispute_id, proof_ref, query, claimed_error in disputes:
        print(f"[DISPUTE ARBITER] Processing dispute for proof reference: {proof_ref}")
        
        verdict = "VALIDATED_SUCCESS"
        penalty = 0
        
        if "malformed" in claimed_error.lower() or "timeout" in claimed_error.lower():
            verdict = "REFUND_ISSUED"
            penalty = 1
            
        cursor.execute(
            "INSERT INTO dispute_arbitration_log (timestamp, proof_reference, dispute_reason, arbitration_verdict, penalty_applied) VALUES (?, ?, ?, ?, ?)",
            (time.time(), proof_ref, claimed_error, verdict, penalty)
        )
        cursor.execute("UPDATE client_disputes SET status = 'RESOLVED' WHERE id = ?;", (dispute_id,))
        conn.commit()
        print(f"[DISPUTE ARBITER] Dispute {dispute_id} resolved with verdict: {verdict}")
        
    conn.close()

def run_arbiter_daemon():
    print("[DISPUTE ARBITER] Starting ANAV Decentralized Dispute Arbitration Daemon...")
    init_dispute_db()
    while True:
        try:
            process_pending_disputes()
        except Exception as e:
            print(f"[DISPUTE ARBITER] Loop error: {e}")
        time.sleep(60)

if __name__ == '__main__':
    run_arbiter_daemon()
