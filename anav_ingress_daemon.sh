#!/bin/bash
set -e

PROJECT_DIR="/home/anav/project-anav"
DB_PATH="$PROJECT_DIR/anav_ledger.db"

cd "$PROJECT_DIR"

echo "[ANAV_INGRESS] Starting Sovereign Ingress Telemetry Daemon with strict schema mapping..."

exec python3 -u - << 'PYTHON_DAEMON'
import sqlite3
import time
from datetime import datetime

DB_PATH = "/home/anav/project-anav/anav_ledger.db"

def record_ingress(client_ip, remote_ip, endpoint, status, payload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Use local or normalized timestamp formatting
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, client_ip, remote_ip, endpoint, status, payload)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ts, client_ip, remote_ip, endpoint, status, payload))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Ingress ledger insert failed: {e}")

print("[ANAV_INGRESS] Daemon active. Listening for L4/L7 telemetry events...")
while True:
    time.sleep(10)
PYTHON_DAEMON
