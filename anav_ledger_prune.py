import sqlite3
import os

DB_PATH = "anav_ledger.db"

def prune_ledger():
    if not os.path.exists(DB_PATH):
        print("[ANAV] Ledger database not found.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Remove logs older than 48 hours to prevent database bloat
        cursor.execute("""
            DELETE FROM global_ingress_log 
            WHERE timestamp < datetime('now', '-48 hours');
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        # Reclaim unused disk space
        cursor.execute("VACUUM;")
        
    print(f"[ANAV] Pruned {deleted_count} expired ingress log entries older than 48 hours and optimized ledger storage.")

if __name__ == "__main__":
    prune_ledger()
