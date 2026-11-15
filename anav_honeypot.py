import sqlite3
import json
import time
from datetime import datetime, timezone, timedelta

DB_PATH = "anav_ledger.db"
# Central Standard Time (CST) is UTC-6
CST_OFFSET = timezone(timedelta(hours=-6))

def process_probe_induction(client_ip, endpoint):
    if client_ip in ["127.0.0.1", "::1", "localhost"] or client_ip.startswith("127."):
        return "LOCAL_LOOPBACK_IGNORED", 0.0

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, induction_status, compute_credits FROM viral_node_catalog WHERE ip_address = ?;", (client_ip,))
        row = cursor.fetchone()
        
        # Explicitly evaluate local Central Time
        ts = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
        
        if not row:
            cursor.execute(
                "INSERT INTO viral_node_catalog (ip_address, discovery_time, induction_status, compute_credits, payload_dispatched) VALUES (?, ?, ?, ?, ?)",
                (client_ip, ts, "INDUCTED_CANDIDATE", 1.0, 1)
            )
            status = "NEW_INDUCTION"
            credits = 1.0
        else:
            node_id, induction_status, credits = row
            status = induction_status
            credits += 0.5
            cursor.execute(
                "UPDATE viral_node_catalog SET compute_credits = ?, payload_dispatched = payload_dispatched + 1 WHERE ip_address = ?;",
                (credits, client_ip)
            )
            
        conn.commit()
        conn.close()
        return status, credits
    except Exception as e:
        print(f"[HONEYPOT ERROR] {e}")
        return "ERROR", 0.0
