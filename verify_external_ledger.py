#!/usr/init/env python3
import sqlite3
import json
import os

DB_PATH = "anav_ledger.db"
EXTERNAL_LEDGER_PATH = "anav_external_isolated.db"

def isolate_external_ledger():
    if not os.path.exists(DB_PATH):
        print("[ERROR] Primary anav_ledger.db not found.")
        return

    # Remove stale isolated copy if it exists
    if os.path.exists(EXTERNAL_LEDGER_PATH):
        os.remove(EXTERNAL_LEDGER_PATH)

    # 1. Safely backup/clone the locked database online
    try:
        src_conn = sqlite3.connect(DB_PATH)
        dest_conn = sqlite3.connect(EXTERNAL_LEDGER_PATH)
        with dest_conn:
            src_conn.backup(dest_conn)
        src_conn.close()
        dest_conn.close()
        print(f"[ISOLATION] Safely cloned live ledger to {EXTERNAL_LEDGER_PATH}")
    except Exception as e:
        print(f"[ERROR] Safe database backup failed: {e}")
        return

    # 2. Open the isolated copy and purge internal telemetry
    conn = sqlite3.connect(EXTERNAL_LEDGER_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, payload FROM global_ingress_log;")
        rows = cursor.fetchall()
        
        purged_count = 0
        retained_count = 0

        for row in rows:
            try:
                data = json.loads(row['payload'])
            except:
                data = {"raw": row['payload']}

            # Heuristics for internal system events
            is_internal = False
            if "failed_module" in data or "action" in data and data["action"] in ["synthetic_proof_ping", "MIGRATION_LEDGER_BACKUP", "ROLLING_CLOUD_BACKUP", "CLOUD_LEDGER_BACKUP"]:
                is_internal = True
            elif "node_id" in data and data["node_id"] == "node_master_01":
                is_internal = True
            elif "agent" in data and "sub_twin" in data["agent"]:
                is_internal = True

            if is_internal:
                cursor.execute("DELETE FROM global_ingress_log WHERE id = ?;", (row['id'],))
                purged_count += 1
            else:
                retained_count += 1

        conn.commit()
        print(f"[ISOLATION COMPLETE] Purged {purged_count} internal telemetry records. Retained {retained_count} true external entries in {EXTERNAL_LEDGER_PATH}.")

    except Exception as e:
        print(f"[ERROR] Ledger filtering failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    isolate_external_ledger()
