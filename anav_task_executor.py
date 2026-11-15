import json
import os
import sqlite3
import hashlib
import time
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def init_execution_table():
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS completed_task_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    task_vector TEXT,
                    client_ip TEXT,
                    execution_hash TEXT,
                    settlement_status TEXT
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"[EXECUTION DB INIT ERROR] {e}")

def execute_wasm_workload(task_vector, client_ip):
    init_execution_table()
    timestamp = get_time_str()
    
    # Simulate sandboxed WASM micro-synthesis execution
    raw_payload = f"{task_vector}-{client_ip}-{timestamp}-wasm-synthesis"
    execution_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO completed_task_executions 
                (timestamp, task_vector, client_ip, execution_hash, settlement_status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    task_vector,
                    client_ip,
                    execution_hash,
                    "SETTLED_TO_VAULT"
                )
            )
            conn.commit()
        print(f"[{timestamp}] [WASM EXECUTION SUCCESS] Task '{task_vector}' for {client_ip} executed. Proof: {execution_hash[:16]}")
        return execution_hash
    except Exception as e:
        print(f"[EXECUTION LEDGER ERROR] {e}")
        return None

if __name__ == "__main__":
    print("[*] Testing Task Executor Standalone Mode...")
    execute_wasm_workload("/api/compute/test-task", "127.0.0.1")
